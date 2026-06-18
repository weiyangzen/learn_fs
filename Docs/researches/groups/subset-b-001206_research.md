# subset-b-001206

Grouped research for Linux counter and cpufreq source files under `sources/distributed-fs/ceph-client/drivers`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-chrdev.c -->
# sources/distributed-fs/ceph-client/drivers/counter/counter-chrdev.c

Purpose: implements the Generic Counter character-device event interface. It backs `/dev/counterN` style reads, polling, and ioctls for installing event watches, enabling/disabling event delivery, resizing the event FIFO, and pushing interrupt-time events from hardware drivers to userspace.

Important APIs/types/functions: defines private `struct counter_comp_node` to bind a watched userspace component descriptor to a `struct counter_comp` callback and parent object. `counter_chrdev_add()` initializes event lists, locks, waitqueue, `struct cdev`, and a default 64-byte kfifo; `counter_chrdev_remove()` frees the FIFO. File operations include `counter_chrdev_read()`, `counter_chrdev_poll()`, `counter_chrdev_ioctl()`, `counter_chrdev_open()`, and `counter_chrdev_release()`. Watch machinery is in `counter_add_watch()`, `counter_get_ext()`, `counter_set_event_node()`, `counter_enable_events()`, and `counter_disable_events()`. `counter_push_event()` is exported in the `COUNTER` namespace for drivers.

Control flow: userspace opens the cdev and the inode cdev is mapped back to `struct counter_device`. `COUNTER_ADD_WATCH_IOCTL` copies a `struct counter_watch` from userspace, validates scope/type/channel, resolves built-in count/signal/function/synapse/extension callbacks, runs optional driver `watch_validate()`, and stages the watch in `next_events_list`. `COUNTER_ENABLE_EVENTS_IOCTL` swaps `next_events_list` into the active `events_list` under the list locks and calls optional `events_configure()` so the driver can program IRQ masks. `COUNTER_DISABLE_EVENTS_IOCTL` frees active and staged watches and reconfigures the driver. Hardware drivers call `counter_push_event()`, which looks up matching active watches, reads watched component data through the resolved callback, records negative errno in `event.status`, queues `struct counter_event` entries into the kfifo, and wakes readers/pollers.

State and persistence: state is entirely in the live `counter_device`: active and staged watch lists, kfifo contents, waitqueue, and locks. Watch configuration and queued events are volatile and disappear on release/unregister. `events_queue_size` is resized by sysfs code through the same kfifo while holding input/output locks.

Dependencies and integration: depends on Linux cdev/fs/poll/uaccess/kfifo/list/mutex/spinlock/wait primitives and the public `linux/counter.h` ABI. Integrates with `counter-core.c` for lifetime and with hardware drivers through `counter_push_event()`, `watch_validate()`, and `events_configure()`.

Risks: event list operations run under mixed mutex/spinlock rules because push can occur in interrupt context; adding driver callbacks that sleep in push-path component reads would be unsafe. Duplicate watches are rejected by callback/parent equality, so extensions with shared callbacks need careful component IDs. `kfifo_alloc(&counter->events, 64, ...)` is byte-sized for `struct counter_event` elements, so queue-depth assumptions should be verified against kfifo semantics. Unregister clears `counter->ops` and wakes readers, so missing `ops_exist_lock` coverage in new paths would create use-after-unregister risk.

Test signals: exercise `open/read/poll` with empty and non-empty FIFOs, nonblocking `EAGAIN`, blocking wakeup, add-watch validation failures for invalid scope/id/channel, duplicate-watch rejection, enable/disable calls reaching driver `events_configure()`, unregister waking readers with `-ENODEV`, and interrupt-driven push from drivers such as `interrupt-cnt`, `stm32-timer-cnt`, `ti-eqep`, and `microchip-tcb-capture`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-chrdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-chrdev.h -->
# sources/distributed-fs/ceph-client/drivers/counter/counter-chrdev.h

Purpose: internal header for the Generic Counter character-device layer.

Important APIs/types/functions: declares `counter_chrdev_add(struct counter_device *counter)` and `counter_chrdev_remove(struct counter_device *counter)`. It includes `linux/counter.h` for `struct counter_device`.

Control flow: `counter-core.c` calls `counter_chrdev_add()` during `counter_alloc()` before `device_initialize()` and calls `counter_chrdev_remove()` from the device release path and allocation error cleanup.

State and persistence: the header has no state; it exposes lifecycle hooks for initializing and freeing cdev/kfifo/list state embedded in `struct counter_device`.

Dependencies and integration: private to `drivers/counter`; it couples the core registration layer to `counter-chrdev.c` without exposing implementation details to hardware drivers.

Risks: any signature changes require coordinated updates to `counter-core.c`; the header intentionally does not expose `counter_push_event()` because that is declared by the public counter API.

Test signals: successful allocation/registration of any counter device proves `counter_chrdev_add()` is callable; unregister/free paths and allocation-error injection prove `counter_chrdev_remove()` cleanup is balanced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-chrdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-core.c -->
# sources/distributed-fs/ceph-client/drivers/counter/counter-core.c

Purpose: provides the Generic Counter bus, device allocation, registration, managed helpers, and module initialization. It is the central lifetime owner for `struct counter_device` and the bridge between hardware drivers, sysfs, and the character-device event interface.

Important APIs/types/functions: defines `counter_device_allochelper` to co-allocate `struct counter_device` with aligned driver private data. Exports `counter_priv()`, `counter_alloc()`, `counter_put()`, `counter_add()`, `counter_unregister()`, `devm_counter_alloc()`, and `devm_counter_add()` in namespace `COUNTER`. Internal objects include `counter_ida`, `counter_bus_type`, `counter_device_type`, and `counter_devt`.

Control flow: `counter_init()` registers the `counter` bus and reserves 256 character-device minors. `counter_alloc()` allocates storage, assigns an ID with IDA, initializes lifetime locks and dev fields, initializes the character device with `counter_chrdev_add()`, initializes the embedded device, and names it `counter%d`. Hardware drivers then fill in name, parent, ops, counts, signals, and extensions before calling `counter_add()`. `counter_add()` mirrors the parent/of_node, builds sysfs groups with `counter_sysfs_add()`, and publishes both cdev and device through `cdev_device_add()`. `counter_unregister()` removes the cdev/device pair, clears `ops` under `ops_exist_lock`, and wakes event readers.

State and persistence: persists only kernel objects and ID allocations for registered devices. Per-device private data lives adjacent to the counter object and is freed by `counter_device_release()`. The IDA ID and cdev FIFO are released when the final device reference drops.

Dependencies and integration: uses Linux bus/device/cdev/IDA/devres APIs. Integrates with `counter-sysfs.c` for attribute construction and `counter-chrdev.c` for event cdev lifetime. Hardware drivers use managed helpers heavily, with `ti-eqep.c` being a non-devm registration example that calls `counter_add()`/`counter_unregister()` directly.

Risks: `counter_alloc()` performs `counter_chrdev_add()` before `device_initialize()`, so all error paths must remain balanced. Clearing `ops` is the unregister sentinel used by cdev reads/ioctls, so hardware drivers must not free callback backing state before unregister completes. The fixed `COUNTER_DEV_MAX` of 256 bounds minors. `counter_priv()` depends on the co-allocation layout.

Test signals: register/unregister a simple counter driver, devm unwind on probe failure, ID reuse after release, sysfs and cdev presence after `counter_add()`, readers receiving `-ENODEV` after unregister, and module init/exit bus and chrdev region cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/counter/counter-sysfs.c

Purpose: synthesizes the Generic Counter sysfs ABI from `struct counter_device` metadata and callback tables. It creates device, signal, count, synapse, extension, array, available-value, name, and component-id attributes before the device is registered.

Important APIs/types/functions: private `struct counter_attribute` wraps `struct device_attribute` plus `struct counter_comp`, scope, and parent pointer; `struct counter_attribute_group` tracks generated attributes per sysfs group. Type-specific show/store handlers include `counter_comp_u8_*`, `counter_comp_u32_*`, `counter_comp_u64_*`, `counter_comp_array_u32_*`, and `counter_comp_array_u64_*`. Attribute builders include `counter_attr_create()`, `counter_avail_attr_create()`, `counter_ext_attrs_create()`, `counter_array_attrs_create()`, `counter_sysfs_exts_add()`, `counter_signal_attrs_create()`, `counter_sysfs_signals_add()`, `counter_sysfs_synapses_add()`, `counter_count_attrs_create()`, `counter_sysfs_counts_add()`, and public `counter_sysfs_add()`.

Control flow: `counter_sysfs_add()` allocates one group for every signal, every count, and the root device group, initializes temporary attribute lists, asks `counter_sysfs_attr_add()` to fill them, then converts list nodes to `struct attribute_group` arrays assigned to `dev->groups`. Show/store handlers dispatch by component type and scope to the correct callback in `struct counter_comp` or `counter_ops`; enum-like values are converted through fixed string tables or per-component availability tables. Array extensions are expanded into one sysfs attribute per element with stable component IDs.

State and persistence: generated attributes are devm-managed against `counter->dev`; they live until device release/unregister devres cleanup. Attributes expose live driver state rather than storing values themselves, except for fixed metadata such as component IDs, names, and availability strings. `events_queue_size` resizes the character-device kfifo under cdev locks.

Dependencies and integration: depends on the public counter component macros/types, sysfs helpers, devm allocation, kstrto parsing, kfifo resizing, and the cdev event queue. It is called only from `counter_add()` before `cdev_device_add()`.

Risks: callback selection in `counter_attr_create()` keys off device-scope callbacks first; component macros must populate the matching callback fields consistently for signal/count scopes. Enum string tables are indexed by driver-returned values, so invalid enum values can read past expected semantic bounds. Array expansion relies on `counter_array.length` and ID accounting matching chrdev `counter_get_ext()`. `events_queue_size_write()` replaces the FIFO and drops queued events, which should be documented for userspace.

Test signals: inspect sysfs layout for representative drivers with device extensions, signal extensions, count extensions, arrays, and synapses; verify readable/writable modes match callbacks; write numeric, bool, enum, count-mode, polarity, and function attributes; verify `*_available` and `*_component_id`; resize event FIFO while producers/readers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/counter/counter-sysfs.h

Purpose: internal header for adding sysfs attributes to a Generic Counter device.

Important APIs/types/functions: declares `counter_sysfs_add(struct counter_device *counter)` and includes `linux/counter.h`.

Control flow: called from `counter_add()` after the hardware driver has filled `counter->ops`, signals, counts, and extensions, but before `cdev_device_add()` publishes the device.

State and persistence: the header has no state; the implementation allocates devm-managed attribute groups on the counter device.

Dependencies and integration: private glue between `counter-core.c` and `counter-sysfs.c`.

Risks: minimal; adding new sysfs lifecycle operations would require keeping this header private or moving declarations to a public counter header if hardware drivers ever need them.

Test signals: any successful `counter_add()` path with visible `/sys/bus/counter/devices/counterN` attributes verifies this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/counter-sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/ftm-quaddec.c -->
# sources/distributed-fs/ceph-client/drivers/counter/ftm-quaddec.c

Purpose: platform driver for the NXP/Freescale FlexTimer Module quadrature decoder, exposing one X4 quadrature count with two phase signals through the Generic Counter subsystem.

Important APIs/types/functions: private `struct ftm_quaddec` stores platform device, MMIO base, endian mode, and mutex. Register helpers `ftm_read()`, `ftm_write()`, and `FTM_FIELD_UPDATE()` abstract endian-aware MMIO. Hardware setup/cleanup is in `ftm_quaddec_init()` and `ftm_quaddec_disable()`. Counter callbacks include count read/write, fixed function/action reads, and prescaler enum read/write.

Control flow: probe allocates a managed counter, maps the memory resource, reads optional `big-endian`, fills one `counter_count`, two `counter_signal`s, two both-edge synapses, and a `prescaler` enum extension, initializes the hardware, registers a devm cleanup action to disable it, and calls `devm_counter_add()`. Writes to `count` only accept zero and reset CNT; prescaler writes unlock write protection, update `FTM_SC`, re-lock, and reset the counter.

State and persistence: hardware registers hold count, prescaler, modulo, and quadrature enable state. Driver state is only endian flag and mutex. Configuration is volatile and reset at probe; devm cleanup disables FTM mode and QDCTRL.

Dependencies and integration: uses `linux/fsl/ftm.h` register definitions, platform/MMIO APIs, OF matching compatible `fsl,ftm-quaddec`, and the Generic Counter API.

Risks: write-protection transitions must stay mutex-protected. Count write rejecting nonzero values may surprise generic tools. The driver uses `devm_ioremap()` rather than `devm_platform_ioremap_resource()`, so resource request semantics are limited. Endianness must match DT.

Test signals: boot/probe on compatible hardware, sysfs count/function/action/prescaler reads, writing prescaler values resets the count, writing count `0` resets, writing nonzero count returns `-EINVAL`, and removal disables quadrature mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/ftm-quaddec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/i8254.c -->
# sources/distributed-fs/ceph-client/drivers/counter/i8254.c

Purpose: reusable Generic Counter wrapper for Intel 8254-compatible programmable interval timers accessed through regmap.

Important APIs/types/functions: `struct i8254` stores a mutex, cached `preset[]`, cached output modes, and regmap. Exported `devm_i8254_regmap_register()` registers a three-counter device for users of `struct i8254_regmap_config`. Counter callbacks implement latched count reads, fixed decrease function, clock/gate action interpretation, ceiling/floor derived from mode and preset, count-mode read/write, and preset read/write.

Control flow: registration validates parent and regmap, allocates a managed counter, initializes three hardware counters to mode 0, fills six signals and three counts, and registers via `devm_counter_add()`. Reads latch the selected counter before no-increment two-byte reads. Mode writes program the control register and clear cached preset. Preset writes validate 16-bit range and reject invalid `1` reloads for rate-generator and square-wave modes, then write the counter low/high bytes.

State and persistence: hardware stores live counters and modes; driver caches preset and mode because not all programmed values can be reconstructed from hardware reads. State is volatile and initialized on register. Mutex serializes regmap command/data sequences.

Dependencies and integration: exports namespace `I8254`, imports `COUNTER`, uses `linux/i8254.h`, `regmap_noinc_read/write`, unaligned little-endian helpers, and Generic Counter extension macros. It is designed for parent bus drivers to instantiate.

Risks: shared static `i8254_counts`, signals, synapses, and extension arrays are read-only after initialization but shared across instances. The count read command/read sequence must not be interleaved, hence the mutex is critical. Cached mode/preset can diverge if another driver or firmware writes the same device.

Test signals: instantiate through a regmap-backed parent, confirm three counts and six signals, verify mode/preset sysfs writes produce expected regmap transactions, floor/ceiling edge cases for preset 0/1 and square-wave/rate-generator modes, and concurrent count reads/writes under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/i8254.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/intel-qep.c -->
# sources/distributed-fs/ceph-client/drivers/counter/intel-qep.c

Purpose: PCI driver for Intel Quadrature Encoder Peripheral devices, exposing a single X4 quadrature count with phase A/B/index signals and several configuration extensions.

Important APIs/types/functions: `struct intel_qep` stores MMIO base, device, mutex, enabled flag, and suspend context registers. Hardware helpers are `intel_qep_readl()`, `intel_qep_writel()`, and `intel_qep_init()`. Counter callbacks include count read, fixed function/action reads, ceiling, enable, spike filter length in nanoseconds, and preset-enable.

Control flow: PCI probe enables the device, maps BAR0, initializes registers with the peripheral disabled, fills Generic Counter structures, sets up runtime PM, and registers with `devm_counter_add()`. Configuration writes that alter `QEPCON`, `QEPFLT`, or `QEPMAX` take the mutex and reject changes while enabled. Enable writes manage `QEPCON_EN` and an extra runtime-PM reference to keep hardware powered while counting. Suspend saves key registers; resume restores them with enable cleared first, then restores the previous enable state.

State and persistence: live state is in MMIO registers plus cached `enabled`; suspend context caches `qepcon`, `qepflt`, and `qepmax`. Configuration is volatile across driver reload but restored across PM suspend/resume.

Dependencies and integration: uses PCI managed resource helpers, runtime PM, Generic Counter API, and PCI IDs for Intel EHL devices. No event interrupts are exposed; it is primarily polling/sysfs configuration.

Risks: several `pm_runtime_get_sync()` return values are ignored, so runtime-PM failures may produce stale MMIO access. Configuration is disabled while counting, so userspace must order enable off before setting ceiling/filter/preset behavior. Spike-filter conversion has clock-period assumptions fixed at 10 ns.

Test signals: PCI probe/remove, sysfs count and ceiling reads, attempts to change ceiling/filter/preset-enable while enabled return `-EBUSY`, 32-bit ceiling range validation, enable toggling balances runtime PM, and suspend/resume preserves filter/max/control state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/intel-qep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/interrupt-cnt.c -->
# sources/distributed-fs/ceph-client/drivers/counter/interrupt-cnt.c

Purpose: simple platform driver that counts rising-edge interrupts, optionally reads a GPIO level as the signal, and pushes Generic Counter change-of-state events.

Important APIs/types/functions: `struct interrupt_cnt_priv` stores `atomic_long_t count`, optional GPIO, IRQ number, enable flag, mutex, and per-instance signal/synapse/count descriptors. `interrupt_cnt_isr()` increments the count and calls `counter_push_event()`. Counter callbacks cover enable, action, count read/write, fixed increase function, optional signal level, and watch validation.

Control flow: probe obtains an optional IRQ and optional GPIO, derives an IRQ from GPIO if needed, builds per-instance Generic Counter descriptors, requests the IRQ with `IRQ_NOAUTOEN` and rising-edge trigger, initializes mutex, and registers with `devm_counter_add()`. Userspace enables counting through the `enable` extension, which calls `enable_irq()` or `disable_irq()`. Watch validation only accepts channel 0 `COUNTER_EVENT_CHANGE_OF_STATE`.

State and persistence: count is an atomic in memory and is reset on probe. Enable state is driver memory plus IRQ enabled state. GPIO is read live when requested. No persistent hardware configuration exists.

Dependencies and integration: uses platform/OF compatible `interrupt-counter`, GPIO consumer APIs, IRQ APIs, Generic Counter, and exported `counter_push_event()`.

Risks: `interrupt_cnt_write()` uses the atomic counter type for range validation, so portability depends on `atomic_long_t` width. Disabling an IRQ from sysfs can sleep/block depending on IRQ state. If only an IRQ is provided, signal level reads return `-EINVAL` because no GPIO exists.

Test signals: probe with IRQ-only, GPIO-only, and both sources; enable/disable toggles IRQ delivery; interrupt increments count and wakes cdev watch readers; count write range checks; signal read behavior with and without GPIO; invalid watch events rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/interrupt-cnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/microchip-tcb-capture.c -->
# sources/distributed-fs/ceph-client/drivers/counter/microchip-tcb-capture.c

Purpose: platform driver for Microchip/Atmel Timer Counter Block capture and optional quadrature decoder modes, exposing count, capture, compare, signal, and event functionality.

Important APIs/types/functions: `struct mchp_tc_data` stores SoC TCB capabilities, syscon regmap, qdec mode, number of channels, and selected channel IDs. Counter callbacks handle function read/write, signal level, action read/write, count read, capture array RA/RB read/write, compare RC read/write, and watch validation. IRQ path includes `mchp_tc_isr()`, `mchp_tc_irq_enable()`, and cleanup actions for IRQ mask and clocks.

Control flow: probe matches the parent TCB node to capability data, obtains parent syscon regmap, reads `reg` channel list, enables per-channel clocks, disables qdec, configures capture mode on channel 0, starts the counter, fills Generic Counter metadata, optionally wires the parent IRQ, and registers. Function writes switch between period capture/increase and quadrature X4; quadrature requires SoC support and channels 0 and 1. ISR reads status and interrupt mask, pushes change-of-state, capture RA/RB, threshold RC, and overflow events on UAPI-defined channels.

State and persistence: hardware registers hold mode, capture/compare values, counter value, and IRQ masks. Driver caches qdec mode and channel selection. Clocks and IRQ enables are devm cleaned up. Configuration is volatile.

Dependencies and integration: depends on AT91 TCB MFD/syscon/regmap, clocks, OF IRQ, `uapi/linux/counter/microchip-tcb-capture.h` event channel constants, and Generic Counter event cdev.

Risks: function/action writes do not use a mutex, so concurrent sysfs access could interleave regmap updates. QDEC mode requires an exact two-channel layout; invalid DT gives runtime `-EINVAL` on function write. Parent match lookup assumes `np->parent` matches a known TCB compatible. Shared TCB channels can conflict with other consumers if DT/resource ownership is wrong.

Test signals: DT with supported TCB parent and channel list, mode switches between increase and quadrature, signal reads reflect TIOA/TIOB, action writes change CMR edge bits, capture/compare sysfs reads/writes hit RA/RB/RC, IRQ events reach userspace for ETRGS/LDRAS/LDRBS/CPCS/COVFS, and invalid QDEC channel layouts fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/microchip-tcb-capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/rz-mtu3-cnt.c -->
# sources/distributed-fs/ceph-client/drivers/counter/rz-mtu3-cnt.c

Purpose: platform driver for Renesas RZ/G2L MTU3a phase-counting counters, exposing two 16-bit counters and one mutually exclusive 32-bit cascaded counter.

Important APIs/types/functions: `struct rz_mtu3_cnt` holds module clock, mutex, MTU channel array, per-logical-count enable flags, and cached 16/32-bit ceilings. Helper functions map logical count IDs to hardware channels, validate shared mode, initialize/terminate 16-bit or cascaded 32-bit counting, and read/write shared register fields. Counter callbacks cover count, function, direction, ceiling, enable, action, and device extensions `cascade_counts_enable` and `external_input_phase_clock_select`.

Control flow: probe obtains parent `struct rz_mtu3`, points at channels 1 and 2, seeds ceilings, sets channel devices, enables runtime PM, fills three counts/four signals/device extensions, and registers. Enable writes request channels, configure TMDR/TCR/TIOR and enable hardware; disabling releases channels and PM references. Count and ceiling operations verify that the logical counter matches the current `TMDR3.LWA` cascade mode. Action reads combine selected function, selected external phase clock pair, and signal ID to report rising/both/none behavior.

State and persistence: hardware state includes TMDR1 mode, TMDR3 shared cascade/clock-select bits, TCNT/TGRA registers, and channel busy/enabled flags managed by the MFD layer. Driver caches ceilings and enable state. Runtime PM gates the shared module clock.

Dependencies and integration: depends on `linux/mfd/rz-mtu3.h`, parent MFD channel ownership helpers, runtime PM, clocks, and Generic Counter. It registers as `rz-mtu3-counter` platform child.

Risks: 16-bit and 32-bit views share hardware; wrong `cascade_counts_enable` changes can invalidate active logical counters and return `-EBUSY`. Some phase-counting modes are TODO/unimplemented. Several `pm_runtime_get_sync()` results are ignored. Channel ownership/busy checks are essential to avoid conflicting with other MTU3 users.

Test signals: enable/disable each logical count, verify channel request/release behavior, switch cascade mode and confirm invalid counters return `-EBUSY`, read/write 16-bit and 32-bit ceilings with range checks, function and action reports for all supported modes and clock-select values, runtime suspend/resume clock behavior, and coexistence with other MTU3 clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/rz-mtu3-cnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/stm32-lptimer-cnt.c -->
# sources/distributed-fs/ceph-client/drivers/counter/stm32-lptimer-cnt.c

Purpose: STM32 low-power timer counter/encoder driver, supporting simple external counting and optional quadrature X4 mode through the Generic Counter subsystem.

Important APIs/types/functions: `struct stm32_lptim_cnt` stores device, regmap, clock, ceiling, polarity, quadrature flag, and enabled state. Helpers `stm32_lptim_is_enabled()`, `stm32_lptim_setup()`, and `stm32_lptim_set_enable_state()` configure CFGR/CR/ARR/CMP and clock state. Counter callbacks implement count read, function read/write, enable read/write, ceiling read/write, and action read/write.

Control flow: probe uses the parent STM32 LPTIMER MFD data, allocates a counter, selects one-count metadata with either one signal or encoder two-signal support based on `has_encoder`, and registers. Function/action/ceiling writes reject changes while hardware is enabled. Enabling configures counter or encoder mode, writes ARR/CMP after enabling the LP timer, waits for CMPOK/ARROK, clears flags, and starts continuous mode. Suspend disables only if this child had enabled the timer, records desired enabled state, selects sleep pinctrl, and resume restores pinctrl and re-enables if needed.

State and persistence: driver caches ceiling, polarity, quadrature mode, and whether it enabled the timer. Hardware counter/configuration is volatile and restored on resume only for enabled instances.

Dependencies and integration: depends on STM32 LPTIMER MFD regmap/clock definitions, pinctrl PM helpers, platform/OF compatible `st,stm32-lptimer-counter`, and Generic Counter.

Risks: no explicit mutex protects cached configuration fields against concurrent sysfs writes. `stm32_lptim_is_enabled()` is used as a guard but return values in boolean contexts need care because negative errors are true in C. Only quadrature X4 is accepted for encoder mode; other quadrature combinations are not exposed.

Test signals: probe with `has_encoder` true and false, sysfs signal/count layout differences, enable sequence writes ARR/CMP and waits for flags, busy errors for function/action/ceiling writes while enabled, action behavior for rising/falling/both in simple count mode, suspend/resume preserving enabled operation, and clock enable/disable balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/stm32-lptimer-cnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/stm32-timer-cnt.c -->
# sources/distributed-fs/ceph-client/drivers/counter/stm32-timer-cnt.c

Purpose: STM32 general-purpose timer counter/encoder driver with count, quadrature modes, capture events, overflow accounting, clock frequency reporting, and PM context restore.

Important APIs/types/functions: `struct stm32_timer_cnt` stores regmap, clock, ARR limit, enabled flag, suspend register backup, encoder capability, channel/IRQ counts, spinlock, and overflow count. Counter callbacks cover count read/write, function read/write, direction, ceiling, enable, prescaler, capture array, overflow count, action, events configuration, watch validation, and clock frequency signal extension. IRQ handler is `stm32_timer_cnt_isr()`.

Control flow: probe reads parent MFD data, detects encoder support by locating the timer-trigger child and checking its index, detects capture channels by probing CCER bits, requests global or update/capture IRQs when present, resets input selection, fills one count and five abstract signals, and registers. Function writes temporarily disable CEN, update slave-mode SMS, generate an update event, and restore CEN. Enable toggles TIM_CR1_CEN and the clock. Watch enable reconfigures DIER from the active counter event list and configures capture channels in input-capture mode; disabled captures are torn down. ISR filters SR by DIER, increments `nb_ovf`, pushes overflow/underflow and capture events, and clears handled flags.

State and persistence: hardware registers hold live count, mode, ARR, PSC, DIER/CCER/capture state. Driver caches enabled state, overflow count, detected topology, and suspend backup of CR1/CNT/SMCR/ARR. Overflow count is protected by spinlock. Enabled timers are restored after system sleep.

Dependencies and integration: depends on STM32 timers MFD definitions, regmap, clocks, pinctrl PM, OF child lookup, IRQs, and Generic Counter char-device events.

Risks: static signal layout intentionally exposes unused signals, so userspace must rely on action `none` rather than signal count for physical availability. Capture channel detection writes CCER temporarily and must not disturb active users. Event configuration writes all DIER bits from the watch list, so other timer consumers must not share the same hardware instance. Function writes restore full CR1 bits through `regmap_update_bits(..., TIM_CR1_CEN, cr1)`, relying on mask semantics.

Test signals: probe across timer instances with and without encoder support, channel detection counts, count write rejected above ARR, function mode transitions, prescaler and ceiling range checks, enable clock balancing, capture and overflow watch delivery through `/dev/counterN`, `num_overflows` synchronization, and suspend/resume preserving enabled registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/stm32-timer-cnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/ti-ecap-capture.c -->
# sources/distributed-fs/ceph-client/drivers/counter/ti-ecap-capture.c

Purpose: TI eCAP capture driver for AM62-class hardware, exposing a timestamp counter, four capture registers, overflow count, signal polarity array, clock frequency, enable control, and capture/overflow events.

Important APIs/types/functions: `struct ecap_cnt_dev` stores enabled flag, mutex, clock, regmap, atomic overflow count, and PM context. Helpers get/set event mode, enable/disable capture, and read/write count registers. Counter callbacks implement count read/write, fixed increase function/action, watch validation, clock frequency, polarity array, capture array, overflow count, ceiling, and enable.

Control flow: probe allocates a counter, enables the functional clock, verifies clock rate, maps MMIO, initializes regmap, requests IRQ, enables runtime PM, and registers. Enabling capture takes a runtime PM reference, enables event interrupts, and starts the timebase/capture loading. Disabling stops the counter, disables interrupts, and drops runtime PM. ISR reads event flags, pushes capture events for each capture slot, increments overflow count on CNTOVF, fans overflow events to all capture channels, and clears interrupt flags.

State and persistence: hardware stores time counter, capture registers, polarity/event mode, interrupt flags, and enable bits. Driver caches enabled and overflow count; PM suspend stores event mode and counter value when enabled, disables clock, and resume restores mode/counter and restarts capture if needed.

Dependencies and integration: uses platform MMIO, regmap, clocks, runtime PM, IRQs, OF compatible `ti,am62-ecap-capture`, and Generic Counter event/watch APIs.

Risks: `ecap_cnt_watch_validate()` allows overflow only for channels 0..3 even though overflow is a global event that the ISR fans to all capture channels. PM suspend calls helper functions that themselves use runtime PM, so ordering with system/runtime PM should be tested. Polarity writes are allowed while enabled and may affect capture semantics immediately.

Test signals: probe and clock-rate validation, sysfs reads/writes for count/capture/polarity/overflow/enable, enable toggling balances runtime PM, capture IRQ delivers per-channel capture events, overflow increments `num_overflows` and emits overflow events, suspend/resume restores event mode and running capture, and invalid watch channels/events are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/ti-ecap-capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/ti-eqep.c -->
# sources/distributed-fs/ceph-client/drivers/counter/ti-eqep.c

Purpose: TI Enhanced Quadrature Encoder Pulse counter driver, exposing one position counter with quadrature, pulse-direction, increase, and decrease modes plus overflow/underflow/direction-change events.

Important APIs/types/functions: `struct ti_eqep_cnt` holds separate 32-bit and 16-bit regmaps because the hardware register file changes width. Counter callbacks implement count read/write, function read/write, action read, event mask configuration, watch validation, ceiling, enable, and direction. IRQ handler `ti_eqep_irq_handler()` maps QFLG bits to Generic Counter events.

Control flow: probe maps MMIO, initializes 32-bit regmap at the base and 16-bit regmap at base + 0x24, requests a threaded IRQ, fills counter metadata, enables runtime PM and the clock, and registers with plain `counter_add()`. Function writes update QDECCTL.QSRC. Action reads derive counted edges from QSRC, signal ID, and XCR. `events_configure()` builds QEINT from active watches; ISR reads QFLG, pushes overflow/underflow/direction-change on channel 0, and writes QCLR.

State and persistence: hardware registers hold position, max, control, interrupt enable/flags, and direction. Driver holds only regmap pointers. Runtime PM is enabled at probe and disabled in remove; no suspend context is implemented here.

Dependencies and integration: uses platform MMIO, regmap, runtime PM, clock framework, OF compatibles `ti,am3352-eqep` and `ti,am62-eqep`, Generic Counter, and char-device event infrastructure.

Risks: probe uses non-devm `counter_add()` and manual remove; errors after `pm_runtime_get_sync()` and clock enable must unwind correctly. Runtime PM get result is ignored. No mutex serializes multi-register operations, though most writes are single regmap operations. Events are global channel 0 only.

Test signals: probe/remove balance runtime PM and counter unregister, count write rejected above `QPOSMAX`, all four function modes map to QDECCTL.QSRC, action reports for XCR and signal combinations, enable toggles QEPCTL.PHEN, ceiling range checks, QEINT mask changes from watches, and IRQ flags produce userspace events then clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/counter/ti-eqep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/Kconfig

Purpose: top-level Kconfig menu for Linux CPU frequency scaling support, governors, generic DT/virtual drivers, and architecture-specific cpufreq driver inclusion.

Important APIs/types/functions: defines `CPU_FREQ`, governor infrastructure options (`CPU_FREQ_GOV_ATTR_SET`, `CPU_FREQ_GOV_COMMON`), stats option, default-governor choice, individual governor configs, generic DT/Rust/virtual platform driver configs, `CPUFREQ_DT_PLATDEV`, and selected platform driver symbols such as `QORIQ_CPUFREQ`, `ACPI_CPPC_CPUFREQ`, and `ACPI_CPPC_CPUFREQ_FIE`. Sources architecture-specific Kconfig files for x86, ARM, PowerPC, MIPS, LoongArch, SPARC, and SuperH.

Control flow: configuration is gated by `if CPU_FREQ`. The default governor choice selects the corresponding governor and often performance as fallback. Generic and architecture blocks expose driver symbols based on architecture and dependency predicates. `source` directives pull deeper driver menus into this top-level menu.

State and persistence: Kconfig state persists in the kernel `.config`; it controls which objects are compiled, which governor is default at boot, and whether sysfs stats and FIE support exist. It has no runtime state.

Dependencies and integration: integrates with the cpufreq core build, scheduler utilization through schedutil, OPP/clock/DT subsystems for DT drivers, ACPI processor/CPPC support, and architecture-specific Kconfig fragments.

Risks: dependency expressions influence build coverage and runtime availability; selecting a default governor implicitly pulls modules into the build. New driver options must be matched with `Makefile` object lines. Architecture `source` paths must stay synchronized with the tree layout.

Test signals: `olddefconfig`/`allyesconfig`/`allmodconfig` across architectures, Kconfig linting, verifying default governor symbols select expected modules, and ensuring every enabled driver symbol has a Makefile object and required dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/Makefile -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/Makefile

Purpose: cpufreq build manifest mapping Kconfig symbols to core, governor, trace, x86, ARM, PowerPC, and miscellaneous platform driver objects.

Important APIs/types/functions: builds `cpufreq.o` and `freq_table.o` for `CONFIG_CPU_FREQ`, stats and governor objects for their symbols, generic DT/virtual objects, `amd_pstate-y := amd-pstate.o amd-pstate-trace.o`, x86 object ordering, ARM SoC driver mappings including `airoha-cpufreq.o`, and other architecture driver objects.

Control flow: Kbuild expands `obj-$(CONFIG_...)` entries based on `.config`; composite `amd_pstate-y` links the trace object into the AMD pstate module. Per-object `CFLAGS_amd-pstate-trace.o := -I$(src)` and `CFLAGS_powernv-cpufreq.o := -I$(src)` make local trace headers visible.

State and persistence: no runtime state; controls build outputs and module composition. Link order comments document precedence among x86 drivers.

Dependencies and integration: depends on Kbuild, Kconfig symbols from `drivers/cpufreq/Kconfig*`, and source files in the cpufreq directory. It integrates tracepoint generation by compiling `amd-pstate-trace.c`.

Risks: missing object entries make Kconfig options unbuildable. Link order matters for legacy x86 driver preference. Composite module definitions must include trace object exactly once to avoid missing or duplicate tracepoint definitions.

Test signals: `make drivers/cpufreq/` for representative configs, `modpost` for composite modules, verifying enabled Kconfig symbols produce expected `.o` or modules, and x86 build tests for ACPI/AMD pstate interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/acpi-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/acpi-cpufreq.c

Purpose: x86 ACPI Processor P-states cpufreq driver. It translates ACPI `_PSS/_PCT/_PSD` performance data into cpufreq policies and changes CPU frequency via MSRs or system I/O, with optional boost control and fast-switch support.

Important APIs/types/functions: `struct acpi_cpufreq_data` stores resume flag, access type, ACPI performance CPU, frequency-domain mask, and read/write function pointers. Key helpers include boost MSR state/set functions, frequency extraction from MSR/I/O status, `drv_read()`/`drv_write()` CPU-affine access, `get_cur_freq_on_cpu()`, `acpi_cpufreq_target()`, `acpi_cpufreq_fast_switch()`, `acpi_cpufreq_cpu_init()`, `acpi_cpufreq_cpu_exit()`, and platform probe/remove. The cpufreq driver object provides verify, target_index, fast_switch, bios_limit, init, exit, resume, name, and attrs.

Control flow: late init registers a platform driver probe. Probe refuses when ACPI is disabled or another cpufreq driver is active, allocates per-CPU ACPI performance storage, initializes boost support, and registers the cpufreq driver. Per-policy init registers ACPI performance data, handles shared-policy masks and BIOS quirks, validates P-state access method, builds a descending frequency table from ACPI states, resolves boost/max frequency through CPPC/DMI when available, initializes current frequency access, notifies SMM, marks resume, and enables fast switch when safe. Frequency transitions write the requested ACPI control value to one CPU or all CPUs in the policy mask, optionally verify the resulting frequency in strict mode, and update cached state.

State and persistence: per-CPU `acpi_perf_data` stores ACPI performance tables and current ACPI state; per-policy `acpi_cpufreq_data` stores masks and callbacks; module parameter `acpi_pstate_strict` affects verification and boost ratio use; boost enabled state is tracked in `cpufreq_driver`. State is runtime only, rebuilt on driver load and per-policy hotplug.

Dependencies and integration: depends on ACPI processor performance library, CPPC optional helpers, x86 CPU feature/vendor detection, MSR access, SMP call functions, cpufreq core, DMI quirks, CPU hotplug, and platform driver registration. Exposes `freqdomain_cpus` and optional legacy AMD `cpb` sysfs attributes.

Risks: CPU-affine MSR/I/O access must match policy shared-type semantics. BIOS quirks and incorrect `_PSD` data require overrides; wrong masks can leave CPUs at unintended frequencies. Strict mode adds transition latency and can return `-EAGAIN`. Fast switch bypasses cross-CPU writes and is disabled for unsafe shared policies. Boost control touches global/vendor MSRs and must be kept coherent across CPU offline/resume.

Test signals: boot on Intel EST, AMD/Hygon HW P-state, and I/O-port ACPI platforms; CPU hotplug; shared policy masks and `freqdomain_cpus`; target frequency changes with/without strict verification; fast-switch path; suspend/resume first target rewrite; boost/CPB sysfs behavior; DMI blacklist and AMD `_PSD` override paths; module unload frees per-CPU data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/acpi-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/airoha-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/airoha-cpufreq.c

Purpose: Airoha SoC cpufreq glue driver that configures CPU OPP/power-domain handling and then instantiates the generic `cpufreq-dt` platform driver.

Important APIs/types/functions: `struct airoha_cpufreq_priv` stores OPP config token, attached PM domain list, and child `cpufreq-dt` platform device. Global `cpufreq_pdev` holds the synthetic parent platform device. `airoha_cpufreq_config_clks_nop()` disables OPP clock setting by returning success without changing clocks. Probe/remove handle OPP config, PM domain attach/detach, and child device registration. Module init matches machine compatibles and registers the platform driver/device pair.

Control flow: module init checks `of_machine_get_match()` for `airoha,an7583` or `airoha,en7581`, registers the driver, and creates an `airoha-cpufreq` platform device carrying the match. Probe obtains CPU0 device, installs an OPP config with CPU clock name and no-op clock setter, attaches required `perf` power domain with OPP device links, registers `cpufreq-dt`, and stores private data. Remove unregisters the child, detaches PM domains, and clears OPP config.

State and persistence: runtime state is the OPP config token, PM domain attachment list, and child platform device. No frequency table is stored here; the generic cpufreq-dt driver owns actual cpufreq policy state.

Dependencies and integration: uses OPP core, PM domain list attach, platform devices, OF machine matching, and `cpufreq-dt.h`. It is built for `CONFIG_ARM_AIROHA_SOC_CPUFREQ`.

Risks: assumes CPU0 represents all CPUs and that CPUs share the same OPP table. Cleanup ordering must reverse probe exactly to avoid lingering OPP config or PM links. The no-op clock config means frequency changes rely on the PM domain/OPP machinery rather than direct clock changes.

Test signals: boot on matching Airoha DT, verify `cpufreq-dt` child appears, OPP table and required `perf` domain are attached, cpufreq policies scale through generic dt path, remove/unload unregisters child and detaches domains, and non-matching machines return `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/airoha-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-trace.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-trace.c

Purpose: tracepoint definition translation unit for the AMD pstate driver.

Important APIs/types/functions: defines `CREATE_TRACE_POINTS` and includes `amd-pstate-trace.h`, causing the trace events declared in the header to emit their storage and registration code in this object.

Control flow: no runtime logic is written directly in this file. Kbuild compiles it into the `amd_pstate` composite object so the tracepoints are defined exactly once while other AMD pstate code can include the header for declarations.

State and persistence: tracepoint state is generated by the tracepoint macros at build time and managed by the kernel tracing subsystem at runtime.

Dependencies and integration: depends on `amd-pstate-trace.h`, tracepoint infrastructure, and the Makefile `amd_pstate-y` composition plus `CFLAGS_amd-pstate-trace.o := -I$(src)`.

Risks: if included in more than one object with `CREATE_TRACE_POINTS`, duplicate symbol errors occur; if omitted from the composite module, references from AMD pstate code lack definitions.

Test signals: build `CONFIG_X86_AMD_PSTATE`, inspect available trace events under the AMD CPU trace system, and enable/disable events while exercising AMD pstate transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-trace.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-trace.h

Purpose: declares Linux trace events used by the AMD pstate cpufreq driver for performance requests, EPP state, and CPPC request diagnostics.

Important APIs/types/functions: sets `TRACE_SYSTEM amd_cpu` and `TRACE_INCLUDE_FILE amd-pstate-trace`. Declares `TRACE_EVENT(amd_pstate_perf)` with min/target/capacity/frequency/MPERF/APERF/TSC/cpu/fast-switch fields; `TRACE_EVENT(amd_pstate_epp_perf)` with CPU, highest/min/max perf, EPP, boost, and changed fields; and `TRACE_EVENT(amd_pstate_cppc_req2)` with CPU, floor perf, changed, and error code. Ends by including `<trace/define_trace.h>` outside the guard.

Control flow: AMD pstate code includes this header to get tracepoint prototypes and uses generated `trace_amd_pstate_*()` calls. `amd-pstate-trace.c` includes it with `CREATE_TRACE_POINTS` to instantiate definitions. Each event maps input arguments into trace entry fields and formats them with `TP_printk`.

State and persistence: no driver state; trace event metadata is compiled into the kernel/module and tracing buffers store runtime samples when enabled.

Dependencies and integration: depends on `linux/cpufreq.h`, `linux/tracepoint.h`, `linux/trace_events.h`, and trace include-path conventions. Integrated into the AMD pstate module through the cpufreq Makefile.

Risks: tracepoint ABI names and field meanings are consumed by tracing tools, so renames or format changes can break scripts. Field widths use `u8` for performance values and must match AMD pstate data ranges. The include guard plus `TRACE_HEADER_MULTI_READ` pattern must remain correct for trace generation.

Test signals: build with AMD pstate enabled, confirm events appear in tracing (`amd_cpu:amd_pstate_perf`, `amd_cpu:amd_pstate_epp_perf`, `amd_cpu:amd_pstate_cppc_req2`), run frequency/EPP changes, and verify field values and format strings match driver inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-trace.h -->
