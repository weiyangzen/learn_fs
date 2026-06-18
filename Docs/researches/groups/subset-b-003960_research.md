# Research: subset-b-003960

Grouped research report for Linux input subsystem files under `sources/distributed-fs/ceph-client/drivers/input`. Each section preserves its source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/evdev.c -->
# sources/distributed-fs/ceph-client/drivers/input/evdev.c

`evdev.c` implements the generic `/dev/input/event*` character-device interface for every input device that emits `EV_SYN`. Its main types are `struct evdev`, the per-input-device handler/cdev wrapper, and `struct evdev_client`, the per-open file state with a power-of-two ring buffer, wait queue, async notification state, clock selection, revocation flag, and optional per-event-type masks.

Control flow starts when `evdev_handler` is registered by `evdev_init()`. `evdev_connect()` allocates an input minor with `input_get_new_minor()`, initializes `struct device` and `struct cdev`, registers an `input_handle`, and publishes `eventN`. On open, `evdev_open()` allocates a client buffer sized from `hint_events_per_packet`, attaches the client under RCU, and opens the underlying input device. Events arrive through `evdev_events()`, which uses `input_get_timestamp()`, optional exclusive grab routing, and `evdev_pass_values()` to filter and enqueue events. `SYN_REPORT` advances `packet_head`, wakes poll/read waiters, and sends `SIGIO`; overflow injects `SYN_DROPPED`.

The ioctl path (`evdev_do_ioctl()`) exposes identity, capability bitmaps, keymaps, current key/LED/sound/switch state, abs parameters, MT slots, force-feedback upload/erase, grabs, revocation, event masks, and clock selection. State is in memory only: open counts, grabs, client queues, masks, and clock choice vanish on close; device lifetime is controlled by input-core disconnect. Dependencies include input core, `input-compat`, force-feedback helpers, cdev/device core, RCU, spinlocks, wait queues, and user-copy APIs.

Risks center on ABI compatibility, compat bitmap layout, queue overflow semantics, lock ordering between `event_lock` and `buffer_lock`, and stale-state duplication when state-query ioctls race queued events. Test signals include opening/closing `eventN`, blocking and nonblocking reads, `poll()`, `EVIOCG*`/`EVIOCS*` ioctls, 32-bit compat tests, `EVIOCGRAB` exclusivity, `EVIOCREVOKE`, event-mask filtering, `SYN_DROPPED` on overflow, and hot-unplug returning `-ENODEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/evdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/ff-core.c -->
# sources/distributed-fs/ceph-client/drivers/input/ff-core.c

`ff-core.c` is the common force-feedback effect manager for input devices. It owns `struct ff_device` allocation and exported operations for uploading, erasing, flushing, playing, and destroying effects. The important APIs are `input_ff_create()`, `input_ff_upload()`, `input_ff_erase()`, `input_ff_flush()`, `input_ff_event()`, and `input_ff_destroy()`.

`input_ff_create()` validates `max_effects`, allocates the flexible `ff_device` owner array plus the parallel `ff_effect` array, initializes the mutex, sets `dev->event` and `dev->flush`, copies supported `ffbit` capabilities, marks `EV_FF`, and exposes rumble emulation when periodic effects exist. Upload flow validates effect and waveform support, optionally converts unsupported `FF_RUMBLE` to `FF_PERIODIC`, allocates or reuses an effect id, checks file ownership, verifies compatible replacement type, calls the device `upload()` callback, then updates effects and owner pointers under `dev->event_lock`. Erase and flush stop playback and clear ownership, with optional hardware `erase()` rollback on failure.

State is per input device and in memory: effect slots, owners, supported bits, and driver callback pointers. It integrates with evdev through `EVIOCSFF`, `EVIOCRMFF`, and `EVIOCGEFFECTS`, and with normal event injection through `EV_FF`, `FF_GAIN`, `FF_AUTOCENTER`, and effect-id playback codes. Risks include file-owner enforcement, replacement compatibility, callback locking expectations, partial flush failures being ignored, and ensuring drivers set upload/playback callbacks before registration. Test signals include effect upload limits, owner mismatch returning `-EACCES`, invalid types returning `-EINVAL`, flush-on-close via evdev, gain/autocenter callbacks, and device unregister freeing FF memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/ff-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/ff-memless.c -->
# sources/distributed-fs/ceph-client/drivers/input/ff-memless.c

`ff-memless.c` implements force-feedback support for devices that cannot store independent hardware effects. It presents the normal FF core interface while combining up to `FF_MEMLESS_EFFECTS` software slots into one or more synthesized effects passed to a driver `play_effect()` callback. Key state lives in `struct ml_device` and `struct ml_effect_state`: per-slot started/playing/aborting flags, loop count, scheduled start/stop times, envelope adjustment timestamp, global gain, and a timer.

`input_ff_create_memless()` allocates `ml_device`, enables `FF_GAIN`, creates a 16-slot FF core device, installs callbacks (`ml_ff_upload`, `ml_ff_playback`, `ml_ff_set_gain`, `ml_ff_destroy`), maps periodic support onto rumble-capable devices, and points each software state at its `ff->effects` slot. Playback starts/stops update flags and jiffies deadlines under `dev->event_lock`, then `ml_play_effects()` repeatedly asks `ml_get_combo_effect()` to group started effects by compatible output type. `ml_combine_effects()` applies gain, attack/fade envelopes, direction averaging, and saturation before calling the hardware-specific player. A timer reschedules at the next attack/fade/stop boundary.

State is volatile and timer-driven. Dependencies include FF core, input event locking, jiffies/timers, fixed-point trig helpers, and a device callback supplied by the concrete driver. Risks include envelope math overflow or truncation, stale timers during teardown, combining effects of different types, and CPU churn from short intervals. Test signals include starting finite and infinite effects, repeated replay counts, gain changes while effects play, upload while active, stop/abort behavior, unregister timer deletion, and devices supporting only rumble but accepting periodic sine/triangle/square through emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/ff-memless.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/gameport/Kconfig

This Kconfig file defines the legacy PC gameport subsystem and hardware-specific gameport providers. `GAMEPORT` is a tristate root option disabled on UML, with help text explaining the 15-pin PC gameport and sound-card gameport use cases. Under `if GAMEPORT`, it offers `GAMEPORT_NS558`, `GAMEPORT_L4`, `GAMEPORT_EMU10K1`, and `GAMEPORT_FM801`.

The dependency graph is the important behavior. ISA-only drivers (`NS558`, `L4`) depend on `ISA`; PCI drivers depend on `PCI`, and `FM801` additionally requires `HAS_IOPORT`. These symbols drive the gameport Makefile and determine whether the generic `gameport.o` core and specific bridge drivers are built in or as modules. There is no runtime state here, but the file is a persistence point for kernel configuration and controls module names documented in the help text.

Integration points are joystick drivers that `select GAMEPORT`, platform bus availability, PCI/ISA probing, and distro kernel configuration. Risks are stale help text, dependencies that allow building a driver without required I/O primitives, or missing `select GAMEPORT` from consumers. Test signals are Kconfig resolution across `allyesconfig`, `allmodconfig`, `UML`, PCI-disabled, ISA-disabled, and no-IOPORT configurations, plus ensuring selected module names match Makefile objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/gameport/Makefile

This Makefile maps gameport Kconfig symbols to kernel objects. `CONFIG_GAMEPORT` builds the generic bus/core object `gameport.o`; `CONFIG_GAMEPORT_EMU10K1`, `CONFIG_GAMEPORT_FM801`, `CONFIG_GAMEPORT_L4`, and `CONFIG_GAMEPORT_NS558` build their corresponding hardware provider modules.

There are no functions or runtime state, but the file is an integration point between Kconfig and kbuild. It preserves the expected module names from help text: `gameport`, `emu10k1-gp`, `fm801-gp`, `lightning`, and `ns558`. The object list also defines link inclusion for built-in configurations, so core availability must line up with consumers that select or depend on `GAMEPORT`.

Risks are simple but high-impact: symbol/object mismatches cause missing modules, stale objects fail builds, and ordering mistakes could omit the generic core when only provider symbols are enabled. Test signals include `make drivers/input/gameport/`, `allmodconfig`, `allyesconfig`, and checking generated modules under `drivers/input/gameport`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/emu10k1-gp.c -->
# sources/distributed-fs/ceph-client/drivers/input/gameport/emu10k1-gp.c

`emu10k1-gp.c` is a PCI gameport provider for Creative SB Live/Audigy gameport functions. It matches four Creative PCI device ids, allocates `struct emu` plus a `struct gameport`, enables the PCI device, records BAR0 start/length, requests the I/O region, initializes gameport name/physical path/parent/io, stores driver data, and registers the port with the generic gameport layer.

The control path is conventional PCI probe/remove. `emu_probe()` handles allocation, `pci_enable_device()`, resource ownership, `gameport_register_port()`, and unwind through region release, `pci_disable_device()`, `gameport_free_port()`, and `kfree()`. `emu_remove()` unregisters the gameport, releases the BAR region, frees memory, and disables PCI. The gameport uses default raw I/O handlers supplied by `gameport.c` because this file only sets `port->io`.

State is limited to PCI drvdata and the live gameport object. Dependencies include PCI core, I/O port resource management, and the gameport bus. Risks include invalid BAR assumptions, region conflicts, use on systems without real I/O port access, and ensuring unregister happens before releasing the region. Test signals are PCI modalias binding, successful `/sys/bus/gameport` device creation, resource conflict failure returning `-EBUSY`, remove/unbind cleanup, and raw gameport reads through consumers such as analog joystick drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/emu10k1-gp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/fm801-gp.c -->
# sources/distributed-fs/ceph-client/drivers/input/gameport/fm801-gp.c

`fm801-gp.c` provides gameport support for ForteMedia FM801 PCI audio controllers. Its private `struct fm801_gp` stores the registered `gameport` and requested resource. Unlike the minimal EMU10K1 provider, this driver supplies `fm801_gp_open()` and a cooked-read callback when `HAVE_COOKED` is defined.

`fm801_gp_probe()` allocates private data and a gameport, enables PCI, fills `open`, `cooked_read`, name, physical path, parent, and I/O base from BAR0, requests a 0x10-byte region, stores PCI drvdata, writes `0x60` to `io + 0x0d` to enable joystick ports, and registers the port. `fm801_gp_cooked_read()` reads four 16-bit axis/status registers, extracts buttons from high bits, converts 13-bit axis values by shifting, returns `-1` for disconnected `0xffff`, and resets the hardware with `outw(0xff, io)`. Remove unregisters the gameport, releases the resource, frees memory, and disables PCI.

State is hardware register state plus PCI drvdata; no persistence exists. Dependencies include PCI, I/O port access, gameport core, and resource management. Risks include hard-coded register layout, cooked-read availability guarded by a local define, missing managed resource cleanup, and returning success from `open()` only for raw/cooked modes. Test signals include PCI bind, cooked mode reads from analog joystick consumers, raw open acceptance, region conflict, unbind cleanup, and verifying axes/buttons under hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/fm801-gp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/gameport.c -->
# sources/distributed-fs/ceph-client/drivers/input/gameport/gameport.c

`gameport.c` is the generic legacy gameport bus. It registers a `bus_type`, manages `struct gameport` devices and `struct gameport_driver` drivers, supplies default raw I/O handlers, measures port speed, owns asynchronous registration/driver-attach work, and offers exported APIs such as `__gameport_register_port()`, `gameport_unregister_port()`, `__gameport_register_driver()`, `gameport_unregister_driver()`, `gameport_open()`, `gameport_close()`, `gameport_start_polling()`, and `gameport_stop_polling()`.

Control flow is intentionally asynchronous for slow probing. Port providers call `gameport_register_port()`, which initializes a device and queues a `GAMEPORT_REGISTER_PORT` event. `gameport_handle_events()` processes one event at a time under `gameport_mutex`, adds ports, measures speed with `ktime` or older PIT/TSC/jiffies methods, then lets driver core attach. Driver registration temporarily sets `ignore` to avoid synchronous probing, registers the driver, clears `ignore`, and queues attach work. Open/close set `gameport->drv`, validate requested mode, manage optional hardware callbacks, and tear down polling timers.

State includes the global port list, event list with module references, parent/child port relationships, per-port driver pointer, timer state, speed, sysfs `description` and `drvctl`, and module parameter `use_ktime`. Dependencies include driver core, bus sysfs, workqueues, timers, I/O port helpers, module refs, mutexes, and architecture timing. Risks include event ordering, duplicate suppression, child destruction while registration is pending, polling timer lifetime, driver callbacks that sleep during bus operations, and I/O timing accuracy. Test signals include registering/unregistering ports and drivers, sysfs `drvctl` commands (`none`, `reconnect`, `rescan`, named driver), child port cleanup, polling start/stop balance, module unload with pending work, and speed measurement paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/gameport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/lightning.c -->
# sources/distributed-fs/ceph-client/drivers/input/gameport/lightning.c

`lightning.c` supports the ISA PDPI Lightning 4 gamecard, which multiplexes up to two cards and four logical gameports per card through I/O port `0x201`. It stores eight static `struct l4` entries, each pointing to a `gameport` and logical port number.

Initialization requests the single I/O byte, probes primary and secondary cards with `l4_add_card()`, verifies command echo/id/revision through busy-waited register handshakes, creates four `gameport` objects per detected card, optionally programs calibration defaults, and registers each port. Each gameport exposes `open`, `cooked_read`, and `calibrate`. `l4_cooked_read()` selects analog/digital banks, chooses the logical port, reads an axis-present status byte, then reads up to four 8-bit axes and four buttons. `l4_calibrate()` reads existing calibration, rescales axis maxima into the 1..255 range, updates returned axes, and writes new calibration.

State is global card/port state plus hardware calibration registers, reset on module exit to conservative values. Dependencies include ISA I/O port access, gameport core, and busy-wait timing. Risks include global shared I/O with no explicit lock around cooked reads, fragile busy polling with an 80-iteration timeout, calibration side effects, and fixed legacy port address. Test signals include module load with no card returning `-ENODEV`, region conflict, detection of card revisions, cooked reads across all logical ports, calibration changes, and exit unregistering all live gameports and releasing `0x201`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/lightning.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/ns558.c -->
# sources/distributed-fs/ceph-client/drivers/input/gameport/ns558.c

`ns558.c` detects and registers classic NS558-compatible ISA and PnP gameports. `struct ns558` records type-like metadata, I/O base, region size, optional PnP device, registered gameport, and list node. All live ports are tracked in `ns558_list`.

The PnP path registers a `pnp_driver` with many legacy audio/gameport ids. `ns558_pnp_probe()` validates a port resource, requests it, allocates state and gameport, sets name/phys/parent/io, registers the port, and adds it to the list. The ISA path scans `ns558_isa_portlist` after PnP, probes each address with electrical heuristics: request region, reject writable lower axis bits, trigger/read for changing axis bits, wait for stabilization, estimate mirrored port size, then allocate/register a gameport. Exit unregisters every gameport, releases the aligned region, frees state, and unregisters the PnP driver.

State is volatile list membership and resource ownership. Dependencies include PnP core, ISA I/O ports, `msleep()`, and gameport core default raw handlers. Risks include false positives/negatives requiring a joystick attached, probing legacy addresses that may disturb hardware, mirror-size resource math, cleanup leak in a PnP allocation failure after successful `request_region()`, and mixed PnP/ISA detection ordering. Test signals include PnP modalias binding, ISA scan on enabled hardware, no-device load returning `-ENODEV`, resource conflicts, module unload releasing regions, and analog joystick consumers attaching to registered ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/gameport/ns558.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-compat.c -->
# sources/distributed-fs/ceph-client/drivers/input/input-compat.c

`input-compat.c` centralizes user ABI conversion helpers shared by evdev and proc/sysfs-style formatting. It exports `input_event_from_user()`, `input_event_to_user()`, `input_ff_effect_from_user()`, and `input_bits_to_string()`.

With `CONFIG_COMPAT`, event conversion detects 32-bit compat syscalls that do not use 64-bit time and translates between `struct input_event_compat` and native `struct input_event`. Force-feedback conversion accepts `struct ff_effect_compat`, copies it into the native storage layout, and rewrites the custom-data pointer with `compat_ptr()` for custom periodic effects. Bitmap formatting prints a native word as one hex field for native callers or as two 32-bit words for compat callers, preserving userspace-visible `/proc/bus/input/devices` formatting. Without compat, the helpers reduce to direct size validation and `copy_{to,from}_user()`.

State is absent; all operations are per-call. Dependencies include `uaccess`, compat syscall detection, FF structures from input headers, and exported GPL symbols. Risks are ABI regressions for 32-bit userspace, time64 boundary behavior, assuming the compat custom pointer remains the final relevant field, and truncation/formatting mismatches for bitmaps. Test signals include native and 32-bit evdev reads/writes, `EVIOCSFF` with custom periodic data, proc bitmap output under compat tasks, invalid FF sizes returning `-EINVAL`, and user-copy fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-compat.h -->
# sources/distributed-fs/ceph-client/drivers/input/input-compat.h

`input-compat.h` declares the input subsystem's internal compat ABI helpers and, under `CONFIG_COMPAT`, the 32-bit layout structures they use. `struct input_event_compat` stores 32-bit seconds/useconds plus event type/code/value. `struct ff_periodic_effect_compat` and `struct ff_effect_compat` mirror force-feedback ABI layout with a `compat_uptr_t` custom data pointer.

The header also defines `input_event_size()`, returning `sizeof(struct input_event_compat)` for 32-bit non-time64 compat syscalls and native `sizeof(struct input_event)` otherwise. Evdev uses this to validate read/write chunk sizes and to step through user buffers consistently with conversion helpers. The prototypes expose conversion functions implemented in `input-compat.c`.

There is no runtime state, but this file is a contract boundary for userspace ABI. Dependencies include `linux/compat.h`, `linux/input.h`, and syscall-mode helpers. Risks include structure packing drift, mismatched size decisions relative to conversion functions, and ABI breakage if force-feedback structs evolve without updating compat mirrors. Test signals are compile coverage with and without `CONFIG_COMPAT`, 32-bit evdev event I/O on non-time64 and time64 ABIs, and `EVIOCSFF` struct-size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-core-private.h -->
# sources/distributed-fs/ceph-client/drivers/input/input-core-private.h

`input-core-private.h` is a small internal header shared by input core support files. It forward-declares `struct input_dev` and declares `input_mt_release_slots()` plus `input_handle_event()`.

Its purpose is to avoid exposing internal core entry points through public input headers. `input.c` defines `input_handle_event()` as the lock-held event disposition/batching function, while `input-mt.c` defines `input_mt_release_slots()` to release active multitouch slots during inhibit/reset/disconnect paths. Both functions have locking assumptions that are meaningful only inside the input core: callers must hold `dev->event_lock` where required.

There is no state or persistence. Dependencies are minimal include guards and the internal build relationship between `input.c` and `input-mt.c`. Risks are accidental external use, stale prototypes after signature changes, and misuse without required locks. Test signals are normal input subsystem compilation and lockdep coverage during device inhibit/unregister paths that call `input_mt_release_slots()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-core-private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-leds.c -->
# sources/distributed-fs/ceph-client/drivers/input/input-leds.c

`input-leds.c` bridges input devices with `EV_LED` capabilities into LED class devices. It maps input LED codes to names and optional default triggers (`kbd-numlock`, `kbd-capslock`, audio mute, etc.), then registers one LED class device per supported LED bit.

`input_leds_handler` matches devices with `EV_LED`. `input_leds_connect()` counts named LED bits, allocates `struct input_leds` with a flexible LED array, registers and opens an input handle, then creates LED class devices named `<input-dev>::<led-name>`. Brightness reads inspect `input->led`; brightness writes inject `EV_LED` events through `input_inject_event()`, so the input core updates state and calls the hardware `event()` callback if present. The handler's input event callback is intentionally empty because state changes are obtained on demand through `brightness_get`.

State is per connected device: input handle, LED classdev registrations, and generated names. Kernel LED state itself remains in `input_dev->led`. Dependencies include input handler APIs, LED class, optional VT/audio LED triggers, and input event injection. Risks include partial registration unwind, LED name allocation failure, recursive behavior if LED class writes race device disconnect, and relying on input state rather than caching. Test signals include devices with NumLock/CapsLock exposing LED class nodes, brightness writes toggling hardware, disconnect unregistering LED classdevs, trigger assignment with and without VT/SND configs, and no registration when no named LED bits exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-mt.c -->
# sources/distributed-fs/ceph-client/drivers/input/input-mt.c

`input-mt.c` is the multitouch helper library for input drivers. It allocates MT slot state, reports tracking IDs/tool state, emulates legacy pointer events, drops unused contacts, assigns slots to new positions, and offers key-based slot lookup. Main APIs include `input_mt_init_slots()`, `input_mt_destroy_slots()`, `input_mt_report_slot_state()`, `input_mt_report_pointer_emulation()`, `input_mt_drop_unused()`, `input_mt_sync_frame()`, `input_mt_assign_slots()`, and `input_mt_get_slot_by_key()`.

Initialization allocates `struct input_mt` with flexible slots, configures `ABS_MT_SLOT` and `ABS_MT_TRACKING_ID`, copies direct/pointer ABS axes, sets BTN_TOUCH/finger-count keys and input properties, and optionally allocates a reduced-cost matrix for tracking assignment. Reporting updates the active slot, assigns monotonically wrapped tracking ids, emits MT fields through `input_event()`, and optionally emits legacy `ABS_X/Y`, pressure, BTN_TOUCH, and BTN_TOOL_* events. Frame sync can drop slots not marked in the current frame and increments `mt->frame`. Slot assignment builds a squared-distance matrix and performs a reduction pass to match positions to existing active slots within `dmax`.

State lives inside `dev->mt`: slots, flags, current slot, frame counter, tracking id, key fields, and optional matrix. Dependencies include input core internals, ABS capability state, exported MT inline helpers, and `dev->event_lock` for release paths. Risks include slot count limits, frame counter wrap assumptions, assignment quality for dense contacts, pressure emulation semantics, and callers forgetting `input_mt_sync_frame()`. Test signals include type-B MT devices, pointer/direct/semi-MT flags, contact lift on inhibit/disconnect, slot assignment with crossing contacts, hover pressure behavior, and repeated init with matching or mismatched slot counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-mt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-poller.c -->
# sources/distributed-fs/ceph-client/drivers/input/input-poller.c

`input-poller.c` provides reusable polling support for input drivers that cannot rely on interrupts. `struct input_dev_poller` stores the driver poll callback, interval/min/max milliseconds, owning `input_dev`, and a `delayed_work` item on `system_freezable_wq`.

Drivers call `input_setup_polling()` before registration, then optionally set interval bounds. `input_register_device()` finalizes defaults through `input_dev_poller_finalize()`. When the input device opens, input core calls `input_dev_poller_start()`, which runs one immediate poll and queues future work if interval is nonzero. Work calls the driver's poll function and requeues itself. Close, inhibit, or interval changes stop/reschedule with `cancel_delayed_work_sync()`. The sysfs attribute group exposes `poll`, `min`, and `max` only when a poller exists; writes validate bounds and, if the device is enabled, reschedule work under `input->mutex`.

State is per input device and freed by `input_dev_release()`. Dependencies include workqueues, sysfs attribute groups, input device enable state, mutexes, jiffies rounding, and exported setter/getter APIs. Risks include poll callbacks sleeping too long, interval zero semantics, reschedule races with close/inhibit, failing to call setup before setters, and sysfs writes while device unregisters. Test signals include polled drivers such as Seesaw, sysfs interval reads/writes including bounds failures, open/close starting and stopping work, suspend/freezable behavior, and device removal cancelling work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-poller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-poller.h -->
# sources/distributed-fs/ceph-client/drivers/input/input-poller.h

`input-poller.h` is the internal header for input polling support. It forward-declares `struct input_dev_poller`, declares lifecycle helpers `input_dev_poller_finalize()`, `input_dev_poller_start()`, and `input_dev_poller_stop()`, and exposes `input_poller_attribute_group` for inclusion in the input device's sysfs groups.

The public-facing driver APIs (`input_setup_polling()` and interval setters) live in public input headers; this private header is for `input.c` and `input-poller.c` coordination. There is no state in the header. Its integration point is `input_dev_attr_groups` in `input.c`, which includes the attribute group unconditionally but relies on the group's visibility callback to hide attributes for non-polled devices.

Risks are prototype drift and accidental exposure of internals. Test signals are compile coverage and sysfs visibility: non-polled devices must not show polling attributes, while polled devices should show `poll`, `min`, and `max`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input-poller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input.c -->
# sources/distributed-fs/ceph-client/drivers/input/input.c

`input.c` is the input subsystem core. It owns input device and handler registration, event normalization and dispatch, char-device minor allocation, sysfs/proc metadata, uevents/modalias generation, soft autorepeat, device open/close/inhibit, keymap helpers, timestamp handling, and matching handlers to devices.

Event flow is central. Drivers call `input_event()`, which validates the event type and takes `dev->event_lock`. `input_get_disposition()` updates in-kernel state for keys, switches, abs axes, LEDs, sound, repeat, and FF while filtering duplicates and inhibited devices. `input_event_dispose()` batches events in `dev->vals`, flushes on `SYN_REPORT` or buffer pressure, and `input_pass_values()` delivers through a grab handle or all open handles under RCU, with filter handlers first. It also starts/stops software autorepeat timers. `input_inject_event()` follows the same path but respects active grabs.

Registration flow allocates devices (`input_allocate_device()`, `devm_input_allocate_device()`), configures defaults, validates ABS state, sets `EV_SYN`, cleans unused bitmaps, sizes event buffers, enables softrepeat, finalizes pollers, adds the device, then attaches all matching handlers under `input_mutex`. Handler registration validates that only one of `filter`, `events`, or `event` is used, adds the handler, and connects it to existing devices. Handles link devices to handlers and select the proper dispatch adapter.

State includes global device/handler lists, input minor IDA, per-device bitmaps/current state, absinfo, timestamps, users/open counts, inhibit flag, grab pointer, poller, FF/MT allocations, and procfs state. Dependencies include device core, procfs, sysfs, PM, RCU, IDA, timers, random input, compat helpers, FF/MT/poller helpers, and the input major. Risks include lock ordering (`input_mutex`, `dev->mutex`, `event_lock`, RCU), ABI modalias formatting/truncation, unregister races, inhibited device semantics, keymap updates causing synthetic key-up events, and managed device two-stage teardown. Test signals include handler/device hotplug, `/proc/bus/input/devices`, sysfs capabilities/modalias/inhibited, uevent modalias matching, grab behavior, softrepeat, MT release on inhibit, poller start/stop, minor allocation exhaustion, and lockdep during concurrent open/close/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joydev.c -->
# sources/distributed-fs/ceph-client/drivers/input/joydev.c

`joydev.c` implements the legacy `/dev/input/js*` joystick ABI on top of input core events. `struct joydev` wraps an input handle, cdev/device, wait queue, client list, calibration/correction data, axis/button maps, current corrected axis state, and open/exist flags. `struct joydev_client` owns a fixed 64-event ring buffer plus startup-event cursor and async notification.

`joydev_handler` matches devices with joystick-like ABS or button capabilities and rejects touchpads/tablets, known accelerometer subdevices, and absolute mice. `joydev_connect()` allocates a minor, builds axis and key maps, initializes default correction from ABS min/max/flat/fuzz, registers the input handle, and publishes `jsN`. Open attaches a client and opens the underlying input device. Input events are converted in `joydev_event()`: EV_KEY above `BTN_MISC` becomes `JS_EVENT_BUTTON`, EV_ABS becomes corrected `JS_EVENT_AXIS`, duplicate axis values are suppressed, events are queued to every client, and readers are woken.

Read supports both the old `JS_DATA_TYPE` snapshot ABI and modern `struct js_event` streaming. New clients first receive startup `JS_EVENT_INIT` events for all buttons and axes. Ioctls expose calibration, timeout glue state, axis/button counts, correction arrays, axis/button maps, name, and 32-bit compat glue layouts. State is in memory and per device/client; user mapping/correction changes do not persist after disconnect/module unload. Dependencies include input core matching, cdev/input major, user-copy, compat, wait queues, RCU, and fasync.

Risks include ABI quirks, correction arithmetic, blacklisting accuracy, ring overflow dropping startup behavior, map validation, compat layout drift, and disconnect while blocked in read/ioctl. Test signals include js device creation for gamepads and absence for touch devices/absolute mice, startup event ordering, old ABI reads, mapping/correction ioctls, nonblocking poll/read, fasync, compat ioctls, hot-unplug `-ENODEV`, and axis calibration edge cases where min equals max.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joydev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/Kconfig

This Kconfig file defines the joystick/gamepad driver menu. `INPUT_JOYSTICK` is a bool menu gate that depends on `!UML`; it only controls visibility of individual driver options. The contained symbols cover gameport devices, serial/serio controllers, parport adapters, USB/SPI/I2C gamepads, platform-specific devices, and optional force-feedback/LED features.

The important behavior is dependency and selection wiring. Several legacy digital/analog options `select GAMEPORT`; serial devices `select SERIO`; parport devices depend on `PARPORT`; I2C devices depend on `I2C`; some FF options `select INPUT_FF_MEMLESS`; Seesaw selects `INPUT_SPARSEKMAP`; Sense HAT selects `MFD_SIMPLE_MFD_I2C`. Options such as `JOYSTICK_XPAD_FF`, `JOYSTICK_XPAD_LEDS`, and `JOYSTICK_PSXPAD_SPI_FF` are feature toggles layered on base drivers.

There is no runtime state, but the file is a persistent configuration contract that controls Makefile object inclusion and available module builds. Integration points include input core, gameport, serio, parport, USB, SPI, I2C, LED class, MFD, and documentation references. Risks include stale dependencies that allow impossible builds, missing `select` for shared helper libraries, module name conflicts, and menu options visible on unsupported platforms. Test signals include `allyesconfig`, `allmodconfig`, platform-specific configs, dependency solver output for helper selections, and matching every symbol to a Makefile object or subdirectory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/Makefile

This Makefile maps joystick Kconfig symbols to driver objects and subdirectories. It builds legacy gameport protocol drivers (`a3d.o`, `analog.o`, etc.), serial/serio drivers, parport drivers, USB/SPI/I2C drivers, and nested force-feedback support under `iforce/`.

There is no runtime control flow or state. The file is a build integration table: each `obj-$(CONFIG_...)` entry must correspond to a Kconfig symbol and source object. In this subset, `CONFIG_JOYSTICK_A3D` maps to `a3d.o` and `CONFIG_JOYSTICK_SEESAW` maps to `adafruit-seesaw.o`.

Risks are mismatched symbol names, missing objects, stale source names, and accidental omission of helper subdirectories. Test signals are kbuild coverage with joystick options as built-in and module, especially `allmodconfig`, plus verifying generated module names match Kconfig help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/a3d.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/a3d.c

`a3d.c` is a gameport driver for FP-Gaming Assassin 3D and MadCatz Panther devices using the A3D protocol. `struct a3d` tracks the parent gameport, optional child ADC gameport, input device, cached analog axes/buttons, detected mode, packet length, read/error counters, and physical path.

`a3d_connect()` opens the raw gameport, reads a packet, validates checksum, determines mode, sets a 20 ms poll handler, configures an input device, and either registers a full Panther XL input device or a relative mouse-like input plus optional child cooked ADC gameport for analog joystick data. `a3d_read_packet()` disables interrupts, triggers the gameport, samples falling strobes on bit 0x10, and extracts 3-bit data chunks. `a3d_poll()` reads fixed-length packets and calls `a3d_read()` to report relative axes, buttons, absolute axes, hats, and joystick buttons depending on mode. The child ADC port serves cached analog data via `a3d_adc_cooked_read()` and starts/stops parent polling when opened.

State is volatile and poll-driven: cached ADC values, packet counters, and input current state. Dependencies include gameport core polling/raw mode, input core, jiffies timing conversion, and optional child gameport registration. Risks include tight IRQ-disabled polling loops, checksum/packet-length assumptions, unknown mode rejection, child port lifecycle, and a driver name of `"adc"` that may be confusing. Test signals include device detection per mode, poll start/stop on input open/close and ADC open/close, packet checksum failure counters, full PXL axis/button reports, child gameport cooked reads, and disconnect unregistering both input and child gameport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/a3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/adafruit-seesaw.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/adafruit-seesaw.c

`adafruit-seesaw.c` is an I2C input driver for the Adafruit Mini I2C Gamepad using the Seesaw firmware register protocol. `struct seesaw_gamepad` holds the managed input device, I2C client, and last button bitmask; `struct seesaw_data` carries one poll sample of X/Y ADC values and button state.

Probe resets the Seesaw device, waits for registers to settle, reads hardware id for debug, configures button GPIO pins as inputs with pull-ups, allocates a managed input device, sets BUS_I2C identity, defines ABS_X/ABS_Y ranges, installs a sparse keymap mapping six GPIO bits to gamepad buttons, sets up input polling, configures a 16 ms default interval with 8..32 ms bounds, and registers the input device. `seesaw_poll()` reads GPIO bulk state and two ADC registers, inverts active-low button bits, reverses X axis orientation, reports ABS axes, emits only changed sparse-keymap button events, and calls `input_sync()`.

State is per device and managed by devres; button state is reset on input open and updated per poll. Dependencies include I2C transfers, unaligned big-endian register encoding, sparse keymap, input poller, and DT/I2C device id matching. Risks include no interrupt support, `i2c_transfer()` not verifying the exact message count, active-low mask assumptions, ADC orientation/range assumptions, poll interval CPU cost, and rate-limited read errors causing stale state. Test signals include OF and I2C modalias binding, reset/configuration I2C writes, sysfs poll interval bounds, button press/release events, axis end-to-end values, I2C fault handling, and device removal via devres.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/adafruit-seesaw.c -->
