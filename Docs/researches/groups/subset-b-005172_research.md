# subset-b-005172 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-vt8500.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-vt8500.c

Purpose: implements a Linux PWM provider for VIA/WonderMedia VT8500-compatible PWM hardware. The controller exposes register blocks for four logical channels, but this driver registers only `VT8500_NR_PWMS` equal to two implemented channels. It binds through the platform bus and device tree compatible `via,vt8500-pwm`.

Important APIs, types, and functions: `struct vt8500_chip` carries the MMIO base and prepared clock. `vt8500_pwm_apply()` is the only `pwm_ops` entry and orchestrates polarity, configuration, enable, and disable. `vt8500_pwm_config()` converts nanosecond period and duty into hardware prescaler, period, and duty registers. `vt8500_pwm_enable()`, `vt8500_pwm_disable()`, and `vt8500_pwm_set_polarity()` update the control register. `vt8500_pwm_busy_wait()` polls `REG_STATUS` update bits after every register write. `vt8500_pwm_probe()` allocates the chip with devres, gets a prepared clock, maps the IO resource, and registers the PWM chip.

Control flow: probe validates an OF node, allocates a two-channel chip, records private data, prepares the clock, maps registers, and calls `devm_pwmchip_add()`. Runtime requests enter `apply`: polarity changes on an enabled channel first disable output, disabled target state exits after optionally disabling, and enabled state always calls config before enabling. Config enables the clock temporarily, computes `period_cycles = clk_rate * period_ns / 1e9`, derives a 10-bit prescaler and 12-bit period value, writes scalar/period/duty/autoload in order, waits for each update bit to clear, and disables the clock. Enabling leaves the clock enabled until disable.

State and persistence: persistent state is hardware register state plus the clock enable count. No software cache is kept beyond PWM core state. Busy-wait timeout only logs a warning and does not abort, so hardware that fails to clear update bits can leave partially programmed state.

Dependencies and integration: depends on Linux platform, clock, MMIO, OF matching, and PWM core APIs. It uses `devm_` lifetime for allocation and mapping. The driver relies on the PWM core to serialize consumer state transitions.

Risks: `msecs_to_loops(10)` is a crude polling budget and can be CPU-frequency sensitive. Duty calculation uses the reduced period register value, so rounding can be visible. If `state->period` is zero, the division path in duty computation would be invalid unless the PWM core prevents it. Polarity writes do not enable the clock explicitly, unlike config and enable.

Test signals: boot with a matching device tree node, verify `pwmchip` registration, exercise both channels through sysfs/debug consumers, check period/duty rounding at minimum and maximum rates, test polarity changes while active, and watch for status timeout warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-vt8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-xilinx.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-xilinx.c

Purpose: exposes the Xilinx LogiCORE AXI Timer as a single PWM output when the device tree node declares PWM cells. It reuses timer register definitions from `clocksource/timer-xilinx.h` and models the two timer counters as period and duty generators.

Important APIs, types, and functions: `xilinx_timer_tlr_cycles()` maps a cycle count into the timer load register based on up/down counting. `xilinx_timer_get_period()` converts a hardware load register back to nanoseconds. `xilinx_timer_pwm_enabled()` validates the two timer control registers against the supported PWM mode. `xilinx_pwm_apply()` implements PWM configuration and enable/disable. `xilinx_pwm_get_state()` reconstructs PWM state from hardware. `xilinx_pwm_probe()` initializes regmap, clock, counter width, and the PWM chip.

Control flow: probe rejects nodes lacking `#pwm-cells` so timer-only bindings can be handled elsewhere, allocates a one-channel PWM chip, maps the register resource, creates a little-endian 32-bit regmap, requires `xlnx,one-timer-only` to be false, accepts counter widths 8/16/32, gets and locks `s_axi_aclk`, then registers the chip. Apply rejects inverted polarity, converts requested period and duty to cycles with overflow guards, clamps period to the representable `priv->max + 2`, rejects periods below two cycles, clamps duty, adjusts 100 percent duty down by one cycle, and maps sub-two-cycle duty to constant low behavior. It writes TLR0/TLR1 and either lets a running PWM reload naturally or initializes the counters with LOAD followed by ENALL. Disabled state clears both TCSR registers.

State and persistence: persistent state is entirely in timer registers and the exclusive clock rate. `get_state` reads TLR and TCSR registers and treats a configuration matching `TCSR_PWM_SET` as enabled. It maps equal period and duty back to zero duty because this hardware produces low output in that case.

Dependencies and integration: integrates with PWM core, platform/OF, regmap MMIO, clock framework, and the Xilinx timer register contract. It takes an exclusive clock-rate reference so timing math remains stable while registered.

Risks: documented limitations include possible one-cycle glitch when changing period and duty together, no true 100 percent duty, normal polarity only, and disabled output always low. The driver assumes active-high Generate Out signals but cannot validate that from device tree. Existing bootloader state is only considered supported if the TCSR bits exactly match this driver's PWM mode.

Test signals: verify probe rejects one-timer-only nodes, exercise min/max counter widths, compare requested and observed period/duty with clock-rate changes blocked, inspect `get_state` after bootloader-preconfigured PWM, and test disable always drives low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-xilinx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm_th1520.rs -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm_th1520.rs

Purpose: Rust PWM driver for the T-HEAD TH1520 controller. It registers up to six channels and implements the newer PWM waveform API, including conversion between abstract waveform fields and hardware period, duty, control, and enable state.

Important APIs, types, and functions: `Th1520WfHw` is the hardware waveform representation with `period_cycles`, `duty_cycles`, `ctrl_val`, and `enabled`. `Th1520PwmDriverData` owns devres-managed MMIO and the clock. `ns_to_cycles()` and `cycles_to_ns()` perform saturating time/rate conversion. The `pwm::PwmOps` implementation provides `round_waveform_tohw`, `round_waveform_fromhw`, `read_waveform`, and `write_waveform`. `Th1520PwmPlatformDriver::probe()` maps resources and registers the chip. A pinned drop disables and unprepares the clock.

Control flow: probe obtains IO resource 0, gets and enables the unnamed clock, rejects zero or greater-than-1 GHz rates, maps a fixed `0xB0` register region, and registers six PWM channels with `pwm::Chip::new`. Waveform rounding treats period zero as disabled, converts period and duty to 32-bit cycle values, rounds a too-small nonzero period up to one cycle with nonzero status, and encodes inversion by using `FPOUT` absence plus `period - duty` when the requested duty offset indicates an inverted signal. Reads fetch control, period, and duty registers for the selected channel and report enabled as `duty_cycles != 0`. Writes disable by writing the requested control, zero duty, and `CFG_UPDATE` when previously enabled; enable/configure writes control, period, duty, then `CFG_UPDATE`, and writes `START` as a separate final transaction only when transitioning from disabled.

State and persistence: hardware registers are the source of truth. The driver deliberately disables by forcing duty to zero rather than clearing `START` because hardware does not reliably force inactive output through `INACTOUT`. Clock state persists for the driver lifetime and is released in `PinnedDrop`. No software state is cached between operations.

Dependencies and integration: depends on Rust-for-Linux `kernel::pwm`, `platform`, `of`, `clk`, devres, and typed IO memory APIs. It binds `thead,th1520-pwm` and uses the Rust module PWM platform-driver macro.

Risks: clock-rate exclusivity is noted as missing because the Rust wrapper lacks an equivalent to `clk_rate_exclusive_get()`, so later rate changes can skew conversions. `cycles_to_ns()` assumes nonzero rate; probe enforces this. Inversion inference from duty offset is intentionally limited and does not support arbitrary phase offsets. The enabled heuristic treats any zero-duty programmed state as disabled.

Test signals: probe with valid and invalid clock rates, read back default hardware state, apply normal and inverted waveforms, verify glitch-free latch on next period, check disable produces static low, test all six channels, and compare rounded waveform status for sub-cycle periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm_th1520.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/rapidio/Kconfig

Purpose: defines top-level RapidIO kernel configuration, including core subsystem enablement, optional enumeration, debug, DMA engine integration, channelized messaging, user-space mport character device access, and switch/device submenus.

Important options: `HAVE_RAPIDIO` is an architecture/platform capability boolean. `RAPIDIO` is the main tristate and depends on `HAVE_RAPIDIO || PCI`. `RAPIDIO_DISC_TIMEOUT` controls host discovery wait time. `RAPIDIO_ENABLE_RX_TX_PORTS` opts into enabling input/output ports for non-maintenance traffic. `RAPIDIO_DMA_ENGINE` depends on `DMADEVICES` and selects `DMA_ENGINE`. `RAPIDIO_DEBUG` adds debug messages through `subdir-ccflags`. `RAPIDIO_ENUM_BASIC`, `RAPIDIO_CHMAN`, and `RAPIDIO_MPORT_CDEV` enable fabric enumeration, channelized messaging, and `/dev` mport access. It sources device and switch Kconfig files.

Control flow and integration: this file drives which objects in the RapidIO Makefile are compiled. Because `RAPIDIO` is tristate, core code can be built in or as a module, and child drivers follow the selected symbols. `RAPIDIO_DMA_ENGINE` changes both generic mport cdev behavior and the Tsi721 device build by enabling DMA code paths.

State and persistence: no runtime state; Kconfig choices persist in the kernel build configuration and shape available ABI, modules, and debug output.

Dependencies: relies on Linux Kconfig, PCI, DMADEVICES, and RapidIO source layout. It includes `drivers/rapidio/devices/Kconfig` before later generic options, so device options are visible under the RapidIO menu.

Risks: enabling `RAPIDIO_MPORT_CDEV` exposes a broad user-space control surface for maintenance, mapping, DMA, and device add/remove operations. `RAPIDIO_ENABLE_RX_TX_PORTS` can change link behavior beyond maintenance traffic. The help text for DMA contains a typo but no functional effect.

Test signals: run `make menuconfig` or `scripts/kconfig/conf` combinations with `RAPIDIO=y/m`, `PCI=n`, and `DMADEVICES` toggles; verify object inclusion matches the Makefiles and that `RAPIDIO_DEBUG` adds `-DDEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/rapidio/Makefile

Purpose: builds the RapidIO core and optional RapidIO modules according to Kconfig symbols.

Important entries: `obj-$(CONFIG_RAPIDIO) += rapidio.o` builds the aggregate core object. `rapidio-y := rio.o rio-access.o rio-driver.o rio-sysfs.o` supplies base subsystem, config access, bus/driver model, and sysfs pieces. Optional objects include `rio-scan.o` for basic enumeration and `rio_cm.o` for channelized messaging. It always descends into `switches/` and `devices/` when `CONFIG_RAPIDIO` is enabled. `subdir-ccflags-$(CONFIG_RAPIDIO_DEBUG) := -DDEBUG` enables debug macros throughout the subtree.

Control flow and integration: the build system links `rio-access.c` and `rio-driver.c` into the core `rapidio` object, making exported symbols available to device drivers such as `tsi721` and user-facing drivers such as `rio_mport_cdev`. Subdirectories compile additional drivers based on their own Makefiles and config symbols.

State and persistence: no runtime state; build products persist as kernel objects/modules depending on tristate choices.

Dependencies: Linux kbuild, top-level RapidIO Kconfig symbols, and source files in this directory plus child directories.

Risks: because debug flags are applied as subdir ccflags, enabling `RAPIDIO_DEBUG` can significantly increase log volume across multiple drivers. If `CONFIG_RAPIDIO=m`, child built-in assumptions must still be module-safe.

Test signals: inspect `make V=1 drivers/rapidio/` output for expected object lists under `RAPIDIO=y/m`, `RAPIDIO_ENUM_BASIC`, `RAPIDIO_CHMAN`, and `RAPIDIO_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/rapidio/devices/Kconfig

Purpose: declares RapidIO master-port device driver options. In this subset it exposes only the IDT Tsi721 PCI Express Serial RapidIO controller driver.

Important option: `RAPIDIO_TSI721` is a tristate labeled `IDT Tsi721 PCI Express SRIO Controller support`. It depends on `RAPIDIO && PCIEPORTBUS` and defaults to `n`.

Control flow and integration: enabling this symbol causes `drivers/rapidio/devices/Makefile` to build the Tsi721 mport object. When `RAPIDIO_DMA_ENGINE` is also enabled, the Tsi721 DMA support object is linked into the same module.

State and persistence: no runtime state; the selected symbol persists in `.config` and controls whether PCI probing for vendor/device ID Tsi721 is present.

Dependencies: Kconfig symbol `RAPIDIO`, PCIe port bus support, and the Tsi721 PCI hardware.

Risks: the dependency on `PCIEPORTBUS` ensures PCIe services are present but does not by itself guarantee MSI/MSI-X availability or BAR layout compatibility; those are handled at probe time. Default `n` avoids pulling in hardware-specific code unexpectedly.

Test signals: Kconfig dependency tests should verify the option is hidden without `RAPIDIO` or `PCIEPORTBUS`, and module builds should include `tsi721_mport` only when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/Makefile -->
# sources/distributed-fs/ceph-client/drivers/rapidio/devices/Makefile

Purpose: builds RapidIO device-level drivers, specifically the Tsi721 master-port driver and the generic mport character device.

Important entries: `obj-$(CONFIG_RAPIDIO_TSI721) += tsi721_mport.o` creates the Tsi721 module. `tsi721_mport-y := tsi721.o` always includes the PCI/mport driver body. `tsi721_mport-$(CONFIG_RAPIDIO_DMA_ENGINE) += tsi721_dma.o` conditionally links DMAengine support into the same module. `obj-$(CONFIG_RAPIDIO_MPORT_CDEV) += rio_mport_cdev.o` builds the user-space mport character device.

Control flow and integration: this file ties the Kconfig topology to concrete build artifacts. It keeps the Tsi721 DMA code in the Tsi721 module rather than as a separate object, which lets `tsi721.c` call `tsi721_register_dma()`, `tsi721_unregister_dma()`, and `tsi721_dma_stop_all()` when DMA support is compiled in.

State and persistence: no runtime state; output object composition depends on `.config`.

Dependencies: Linux kbuild, `RAPIDIO_TSI721`, `RAPIDIO_DMA_ENGINE`, and `RAPIDIO_MPORT_CDEV`.

Risks: conditional linking means code paths guarded by `CONFIG_RAPIDIO_DMA_ENGINE` must remain synchronized with stubs in `tsi721.h`; otherwise non-DMA builds can break. The cdev builds independently of Tsi721 and can attach to any registered RapidIO mport.

Test signals: build with all four combinations of Tsi721 and DMA enabled/disabled; run `nm` or module link checks to ensure DMA symbols are present only in DMA builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/rio_mport_cdev.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/devices/rio_mport_cdev.c

Purpose: provides a generic `/dev/rio_mportN` character device for each registered RapidIO master port. It exposes maintenance reads/writes, device add/remove, inbound and outbound window mapping, optional DMA transfers, doorbell send/receive, port-write event delivery, mmap, poll, and async notification to user space.

Important APIs, types, and functions: `struct mport_dev` represents each mport cdev and owns the `cdev`, device node, mapping list, doorbell/port-write filter lists, open file list, and optional default DMA channel. `struct mport_cdev_priv` is per-open-file state with event FIFO, filters, async queue, and optional per-file DMA channel/request list. `struct rio_mport_mapping` tracks inbound, outbound, and coherent DMA mappings with a `kref` shared by file ownership and VMAs. Main file operations are `mport_cdev_open`, `mport_cdev_release`, `mport_cdev_ioctl`, `mport_cdev_mmap`, `mport_read`, `mport_write`, and `mport_cdev_poll`. DMA paths include `rio_dma_transfer`, `do_dma_request`, `rio_mport_wait_for_async_dma`, `rio_mport_alloc_dma`, and `rio_mport_free_dma`.

Control flow: module init registers a private class, allocates a character-device range, and registers a `class_interface` against `rio_mport_class`. When the RapidIO core adds an mport device, `mport_cdev_add()` creates `/dev/rio_mportN`, snapshots query properties, and puts the instance on `mport_devs`. Open allocates per-file state and FIFO. IOCTL dispatch validates active state and fans out to maintenance config access, host ID/component tag setters, properties, event masks, doorbell/port-write filters, inbound/outbound mapping, DMA allocation/free/transfer, async wait, and dynamic RIO device add/delete. Reads drain fixed-size `struct rio_event` records; writes send doorbells. Mmap resolves a DMA or outbound mapping by physical handle and maps it with `dma_mmap_coherent()` or `vm_iomap_memory()`, adding a VMA reference.

State and persistence: persistent runtime state is per-mport mapping/filter/open-file lists and per-file event FIFOs. Mapping lifetime is reference-counted and may outlive explicit unmap while VMAs are open. DMA requests pin user pages or hold coherent-buffer mapping references until completion/free. Removal marks the mport inactive, terminates DMA, unregisters cdev, notifies async users, releases mappings, and drops the device reference.

Dependencies and integration: integrates with RapidIO core exports (`rio_map_outb_region`, `rio_map_inb_region`, config accessors, doorbell and port-write registration, `rio_add_device`/`rio_del_device`), Linux cdev/device model, kfifo, poll/fasync, DMA coherent allocation, and optional DMAengine via RapidIO DMA prep helpers.

Risks: this is a broad privileged ABI and depends heavily on correct user input validation. Mapping overlap checks are manual and must avoid aliasing windows. DMA async release has races to manage between callbacks, file close, and wait timeouts. Some operations return success even when a requested filter or mapping was not found, making user-space diagnostics less strict. Dynamic device creation trusts config-space reads and caller-supplied names/component tags.

Test signals: create/remove mports and verify device nodes, run local/remote maintenance IO including alignment failures, map/unmap inbound/outbound windows and mmap them, exercise VMA close after file close, send and receive doorbells with filters, add/remove port-write filters, perform DMA read/write sync/async with user pages and coherent handles, test mport removal while descriptors are open, and check lockdep/KASAN under concurrent open/close/ioctl.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/rio_mport_cdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/tsi721.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/devices/tsi721.c

Purpose: implements the IDT Tsi721 PCIe-to-Serial RapidIO bridge as a Linux RapidIO master port. It handles PCI probe/remove, BAR validation and mapping, RapidIO maintenance transactions, inbound/outbound memory windows, doorbells, port-write capture, inbound/outbound messaging, interrupts, and optional DMAengine registration.

Important APIs, types, and functions: the central object is `struct tsi721_device` from `tsi721.h`. `tsi721_rio_ops` publishes RapidIO mport operations such as local/remote config access, doorbell send, mailbox open/close, message add/get, inbound/outbound map/unmap, port-write enable, and query. `tsi721_probe()` performs PCI setup. `tsi721_setup_mport()` initializes and registers `struct rio_mport`. Maintenance uses `tsi721_maint_dma()` through `tsi721_cread_dma()` and `tsi721_cwrite_dma()`. Mapping paths are `tsi721_map_outb_win()`, `tsi721_unmap_outb_win()`, `tsi721_rio_map_inb_mem()`, and `tsi721_rio_unmap_inb_mem()`. Messaging paths are `tsi721_open_outb_mbox()`, `tsi721_add_outb_message()`, `tsi721_omsg_handler()`, `tsi721_open_inb_mbox()`, `tsi721_add_inb_buffer()`, `tsi721_get_inb_message()`, and `tsi721_imsg_handler()`.

Control flow: PCI probe allocates private data, enables the PCI function, validates BAR0 registers and BAR1 doorbells, records usable 64-bit outbound BAR2/BAR4 regions, requests regions, maps BAR0/BAR1, sets DMA masks, configures PCIe ordering and completion timeout, fixes MSI-X table offsets, disables interrupts, initializes outbound and inbound translation bookkeeping, initializes the maintenance BDMA channel, doorbell queue, port-write FIFO, and messaging block, then registers the RapidIO mport and enables interrupts. Interrupt setup tries MSI-X, falls back to MSI, then INTx. The shared IRQ path decodes device and channel interrupt registers, dispatching to doorbell work, port-write work, messaging handlers, and BDMA handlers; MSI-X has dedicated handlers for several sources.

State and persistence: the driver maintains hardware-backed rings for inbound doorbells, port writes, messaging descriptors, outbound message buffers, inbound message buffers/free queues, inbound windows, outbound windows, and a reserved maintenance DMA channel. Software counters track available inbound/outbound windows and initialized mailbox state. Removal disables interrupts, frees IRQs, flushes work, unregisters the mport, unregisters DMA, frees coherent rings, closes windows, unmaps BARs, disables MSI/MSI-X, releases PCI regions, and frees private data.

Dependencies and integration: depends on PCI, RapidIO core, DMA coherent APIs, kfifo/workqueue, interrupt APIs, optional PCI MSI, and optional Tsi721 DMAengine support. `rio_mport_cdev` and RapidIO subsystem clients consume the mport operations registered here.

Risks: maintenance transactions busy-wait up to a large fixed loop and serialize globally with `tsi721_maint_lock`. Window allocation and direct inbound mapping coalescing are complex and sensitive to overlap and power-of-two alignment. MSI-X setup requires exact vector allocation and uses hardware-specific table offset fixups. Some init steps, such as port-write init, are not fully checked for errors by probe. Messaging ring handling must preserve descriptor ownership and interrupt re-enable ordering to avoid lost completions.

Test signals: PCI probe with valid/invalid BAR layouts, MSI-X/MSI/INTx fallback, RapidIO config-space reads/writes, outbound and inbound window alignment/overlap tests, doorbell send/receive, port-write delivery under FIFO overflow, mailbox open/send/receive/close for all enabled mailboxes, mport unregister while traffic is active, suspend/shutdown DMA stop, and error-injection for BDMA abort and messaging interrupt errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/tsi721.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/tsi721.h -->
# sources/distributed-fs/ceph-client/drivers/rapidio/devices/tsi721.h

Purpose: shared hardware definition and private data header for the Tsi721 PCIe-to-SRIO bridge driver and its optional DMAengine companion. It centralizes debug masks, PCI IDs, BAR constants, register offsets, bit masks, descriptor formats, ring sizes, state structures, and cross-file prototypes/stubs.

Important APIs, types, and definitions: `DRV_NAME`, `PCI_DEVICE_ID_TSI721`, BAR constants, `TSI721_REG_SPACE_SIZE`, `TSI721_DB_WIN_SIZE`, and RapidIO transaction type constants define the hardware identity. Register groups cover event management, port-write capture, inbound doorbells, inbound windows, outbound windows/zones, device interrupts, block DMA, outbound messaging, inbound messaging, and messaging ECC/retry counters. Descriptor structs `tsi721_dma_desc`, `tsi721_imsg_desc`, `tsi721_omsg_desc`, and `tsi721_dma_sts` encode the DMA/messaging ABI with alignment requirements. Enums `dma_dtype`, `dma_rtype`, `tsi721_smsg_int_flag`, `tsi721_flags`, and `tsi721_msix_vect` classify descriptor and interrupt state. Runtime structures include `tsi721_bdma_maint`, optional `tsi721_tx_desc` and `tsi721_bdma_chan`, `tsi721_imsg_ring`, `tsi721_omsg_ring`, `tsi721_ib_win`, `tsi721_obw_bar`, `tsi721_ob_win`, and the aggregate `tsi721_device`.

Control flow: the header itself has no execution path, but it controls how `tsi721.c` programs hardware and how `tsi721_dma.c` shares private channel state. Conditional declarations expose `tsi721_bdma_handler`, `tsi721_register_dma`, `tsi721_unregister_dma`, and `tsi721_dma_stop_all` only when `CONFIG_RAPIDIO_DMA_ENGINE` is enabled; otherwise no-op stubs keep the main driver buildable.

State and persistence: every persistent Tsi721 software state field is defined here: PCI device pointer, RapidIO mport, flags, MMIO pointers, MSI-X vector table, doorbell queue, work items, port-write FIFO, maintenance DMA resources, optional DMA channels, inbound/outbound messaging rings, and translation-window accounting.

Dependencies and integration: consumed by both Tsi721 source files and relies on Linux types from PCI, RapidIO, DMAengine, kfifo, workqueue, spinlock, and list APIs included by those C files.

Risks: register constants and bit masks are hardware-contract critical; any wrong offset or mask can corrupt unrelated device state. Structure alignment annotations must match hardware descriptor fetch requirements. The same DMA descriptor structure is reused for multiple descriptor types through unions, requiring careful fill logic. Conditional stubs must stay synchronized with call sites.

Test signals: compile both DMA and non-DMA configurations, validate descriptor sizes/alignment with build assertions if added, compare register offsets against the Tsi721 datasheet, and exercise MSI-X vector mapping for all enabled mailbox and DMA channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/tsi721.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/tsi721_dma.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/devices/tsi721_dma.c

Purpose: provides DMAengine support for Tsi721 block DMA channels used for RapidIO NREAD/NWRITE transfers. It registers private DMA channels on the RapidIO mport, translates RapidIO DMA prep requests into hardware descriptors, drives descriptor rings, handles completion/error interrupts, and tears channels down.

Important APIs, types, and functions: `tsi721_register_dma()` and `tsi721_unregister_dma()` are called by `tsi721.c`. `tsi721_bdma_handler()` is the top-half entry from the main interrupt path. Channel resource management uses `tsi721_alloc_chan_resources()` and `tsi721_free_chan_resources()`. DMAengine operations include `tsi721_prep_rio_sg()`, `tsi721_tx_submit()`, `tsi721_issue_pending()`, `tsi721_tx_status()`, and `tsi721_terminate_all()`. Hardware programming helpers include `tsi721_bdma_ch_init()`, `tsi721_bdma_ch_free()`, `tsi721_submit_sg()`, `tsi721_start_dma()`, `tsi721_dma_tasklet()`, and `tsi721_clr_stat()`.

Control flow: registration iterates hardware DMA channels, skips the reserved maintenance channel and disabled `dma_sel` bits, initializes `struct dma_chan` objects, tasklets, and queues, sets DMA_PRIVATE/DMA_SLAVE caps, and registers the DMA device. A client allocates resources, which allocates coherent descriptor and status rings, optional MSI-X IRQs, software transaction descriptors, initializes cookies, marks the channel active, and enables interrupts. Prep validates SG input and direction, maps write type to RapidIO request type, removes a descriptor from the free list, and fills RapidIO address/destid metadata. Submit assigns a cookie, queues the descriptor, and calls `tsi721_advance_work()`. Submission to hardware requires an idle channel, fills buffer descriptors from the SG list, merges contiguous SG segments when possible, handles ring wrap through the link descriptor, updates write counts, and starts DMA. Interrupts disable channel interrupts and schedule a high-priority tasklet, which clears status, handles errors by reinitializing aborted channels and completing the active descriptor with `DMA_ERROR`, or handles DONE/IOFDONE by completing cookies, invoking callbacks, and advancing queued work.

State and persistence: each `tsi721_bdma_chan` owns coherent descriptor/status memory, ring pointers, `wr_count` values, active descriptor, pending queue, free descriptor list, tasklet, and active flag. Descriptors retain SG cursor state so a large SG list can resume after partial ring submission. Unregister stops all channels, unregisters DMAengine, kills tasklets, frees descriptors/status memory, and removes channel list nodes.

Dependencies and integration: depends on Tsi721 register definitions, Linux DMAengine internals, RapidIO DMA extension metadata, PCI/MSI support, tasklets, spinlocks, and DMA coherent allocation. It is linked only when `CONFIG_RAPIDIO_DMA_ENGINE` is enabled.

Risks: `tsi721_terminate_all()` waits in a busy loop for idle without an explicit timeout in the active code path. Error handling assumes `active_tx` is present when DMA error interrupts occur. Descriptor-ring fullness and SG cursor mutation are subtle; wrong accounting can lose SG segments or overwrite hardware-owned descriptors. Callbacks may run during error paths while locks and list ownership are changing.

Test signals: DMAengine self-tests with read/write directions and all write types, SG lists with contiguous and non-contiguous entries, entries larger than `TSI721_BDMA_MAX_BCOUNT`, ring wrap and full-ring partial submission, async callbacks, terminate during active transfer, MSI-X and shared IRQ modes, DMA abort injection, and module unload with allocated channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/devices/tsi721_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio-access.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/rio-access.c

Purpose: provides exported RapidIO configuration-space access wrappers for local and remote devices plus a doorbell send wrapper. It is the common alignment and dispatch layer between RapidIO core/clients and mport-specific operations.

Important APIs, types, and functions: macro families `RIO_LOP_READ`, `RIO_LOP_WRITE`, `RIO_OP_READ`, and `RIO_OP_WRITE` generate `__rio_local_read_config_{8,16,32}`, `__rio_local_write_config_{8,16,32}`, `rio_mport_read_config_{8,16,32}`, and `rio_mport_write_config_{8,16,32}`. `rio_mport_send_doorbell()` invokes the mport `dsend` operation. All generated accessors are exported GPL symbols.

Control flow: each generated accessor first checks access alignment (`RIO_16_BAD`, `RIO_32_BAD`; 8-bit always allowed), then calls the appropriate `struct rio_ops` method on the mport: local `lcread`/`lcwrite` or remote `cread`/`cwrite`. Read wrappers receive a 32-bit temporary from the low-level op and truncate it to the requested type. Write wrappers pass the typed value and access length through. The doorbell helper passes `mport->id`, destination ID, and payload to `mport->ops->dsend`.

State and persistence: no local state. The only persistent effects are hardware/configuration changes made by lower-level mport operations.

Dependencies and integration: depends on `struct rio_mport` and `struct rio_ops` from RapidIO headers. Tsi721 supplies the low-level ops; `rio_mport_cdev` uses these wrappers for user-space maintenance IO; enumeration and drivers can use them for config-space access.

Risks: the wrappers do not validate operation pointers or mport lifetime; callers must use registered, live mports. They enforce alignment but not offset range, except where lower-level drivers do. Type truncation for 8/16-bit reads depends on low-level ops returning data in the expected lower bits.

Test signals: alignment error checks for 16/32-bit offsets, successful local and remote config accesses through a mock or real mport, 8/16/32-bit truncation behavior, error propagation from low-level ops, and doorbell dispatch with expected destination and payload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio-access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio-driver.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/rio-driver.c

Purpose: implements RapidIO bus driver-model glue: device/driver matching, probe/remove/shutdown dispatch, driver registration helpers, mport class registration, bus registration, uevent modalias generation, and reference helpers for `struct rio_dev`.

Important APIs, types, and functions: `rio_match_device()` compares `struct rio_device_id` tables with `struct rio_dev` IDs. `rio_dev_get()` and `rio_dev_put()` wrap device references and are exported. `rio_device_probe()`, `rio_device_remove()`, and `rio_device_shutdown()` are bus callbacks. `rio_register_driver()` and `rio_unregister_driver()` wrap `driver_register()`/`driver_unregister()` for `struct rio_driver`. `rio_attach_device()` assigns `rio_bus_type` to a `rio_dev`. Exported globals include `rio_mport_class` and `rio_bus_type`.

Control flow: at `postcore_initcall`, `rio_bus_init()` registers the `rapidio_port` class and the `rapidio` bus, unwinding the class if bus registration fails. When a driver is registered, its embedded `device_driver` name and bus are initialized. Bus matching uses the ID table, accepting wildcard vendor/device/assembly IDs. Probe obtains a device reference before invoking the driver probe and stores `rdev->driver` only on success; failure drops the reference. Remove invokes the bound driver's remove callback, clears the driver pointer, and drops the reference acquired at probe. Shutdown delegates to the driver if present. Uevents emit `MODALIAS=rapidio:v...` for module autoloading.

State and persistence: persistent state is held in the Linux device model: registered class, registered bus type, bound driver pointer on each `rio_dev`, and device reference counts. The file itself keeps no mutable global list beyond the class/bus objects.

Dependencies and integration: depends on Linux device model, RapidIO sysfs groups (`rio_mport_groups`, `rio_dev_groups`, `rio_bus_groups`), and RapidIO headers. Device creation code, including `rio_mport_cdev` dynamic add/remove, calls `rio_attach_device()` and `rio_add_device()` elsewhere to put devices onto this bus.

Risks: probe assumes `rdrv->id_table` is present; drivers without ID tables will not bind. Reference handling is simple but must be paired with device creation/removal paths outside this file. `rio_match_bus()` has compact formatting around the `out` label but functional behavior is straightforward.

Test signals: register a test RapidIO driver with exact and wildcard IDs, verify probe/remove reference transitions, check shutdown callback dispatch, inspect uevent modalias strings, test bus/class registration failure unwinding, and ensure `rio_mport_class` consumers see add/remove callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio-driver.c -->
