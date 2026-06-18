# subset-b-003975 research

Grouped research for Linux input/serio files under `sources/distributed-fs/ceph-client/drivers/input/serio`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hil_mlc.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/hil_mlc.c

## Purpose
`hil_mlc.c` is the generic HP-HIL Master Link Controller state-machine layer. It sits between an access-method driver such as `hp_sdc_mlc.c` and HIL protocol device drivers by discovering devices on an HIL loop, polling the loop, maintaining discovered-device metadata, and exposing each discovered slot as a virtual `SERIO_HIL_MLC` serio port.

## Important APIs, types, and functions
- The public API is `hil_mlc_register()` and `hil_mlc_unregister()`, exported for hardware-specific MLC backends.
- Runtime state is stored in the `hil_mlc` object supplied by the backend: callback methods `in`, `out`, and `cts`; locks and semaphores; current state-engine index; input/output packets; discovered-device tables `di`, `di_map`, `serio_map`; and the virtual serio ports.
- `hil_mlc_se[]` is the central state-machine table. It describes controller reset/test, device hard reset, interface clear, auto-configure, discovery, metadata collection, polling, and reprobe behavior through `HILSE_FUNC`, `HILSE_OUT`, `HILSE_IN`, `HILSE_EXPECT*`, and `HILSE_CTS` nodes.
- Helpers such as `hilse_take_idd()`, `hilse_take_rsc()`, `hilse_take_exd()`, and `hilse_take_rnm()` parse HIL device description packets into `di_scratch`.
- `hilse_match()` matches the discovered scratch record to an unused remembered device slot or allocates a new slot, updates reverse maps, and triggers `serio_rescan()`.
- `hil_mlc_send_polls()` converts HIL poll response packets into byte streams delivered through the bound serio driver interrupt callback.
- `hil_mlc_serio_write()` emulates cached IDD/RSC/EXD/RNM responses for upper-layer HIL drivers and rejects unsupported non-command writes.

## Control flow
Module init sets up a one-second kicker timer and enables a global tasklet. A hardware backend calls `hil_mlc_register()`, which initializes synchronization primitives and discovery state, allocates `HIL_MLC_DEVMEM` virtual serio ports, adds the MLC to the global list, and schedules the tasklet.

The tasklet walks every registered MLC and repeatedly executes `hilse_donode()` until the current node requests a break. Output nodes prepare expected input, acquire the output semaphore, call the backend `out()` callback, and then wait for the backend ISR to release input state. Input/expect nodes call the backend `in()` callback and transition according to success, protocol mismatch, or timeout. The timer periodically sets `hil_mlcs_probe` and schedules the tasklet so the loop is re-polled and hung transactions are advanced.

During normal operation the state machine reaches `HILSEN_OPERATE`, sends `HIL_CMD_POL`, forwards poll data to the matching virtual serio port, and returns to operate unless the global probe flag asks it to re-enter discovery. Unregister removes the MLC from the list, unregisters all virtual serio ports, and schedules the tasklet to drain any pending state.

## State and persistence
The file maintains global runtime state only: the registered MLC list, tasklet, kicker timer, probe flag, and stop flag. Each MLC keeps the persistent-in-RAM mapping between physical HIL device order and remembered device information slots so devices can be rescanned without losing cached identity data. No state is written to disk or firmware.

Synchronization is split across the global `hil_mlcs_lock`, per-MLC `lock`, semaphores for input/output/clear-to-send, and tasklet/timer scheduling. Device discovery data survives while the MLC is registered but is lost when the backend unregisters.

## Dependencies and integration points
This layer depends on `<linux/hil_mlc.h>` data structures, HIL packet constants from the HIL subsystem, the serio bus, timer/tasklet infrastructure, semaphores, and a backend that implements the physical MLC callbacks and schedules `mlc->tasklet` from its ISR. `hp_sdc_mlc.c` is the paired backend in this source set.

## Risks
- The state engine is table-driven and index-sensitive; changing node order or transition constants can silently alter discovery and recovery behavior.
- `hil_mlc_send_polls()` calls the bound serio driver's `interrupt` method directly after looking at `serio->drv`; lifetime and binding state must remain stable under serio core expectations.
- Backend callbacks must obey the semaphore protocol. Missed `up()` calls or stale `istarted`/`ostarted` state can stall the global tasklet.
- `hil_mlc_serio_write()` returns `-EIO` for unsupported command sequences and only emulates selected metadata commands, so upper drivers expecting more HIL command coverage may fail.
- The global `hil_mlc_stop` disables future timer rescheduling after an output error, affecting every registered MLC.

## Test signals
- Build with HIL/HP SDC configurations to catch API drift in `hil_mlc`, `serio`, timer, and tasklet interfaces.
- Exercise backend registration/unregistration and verify every virtual serio port is registered, rescanned on new device identity, and unregistered cleanly.
- HIL hardware or simulator tests should cover empty loop, multiple devices, IDD-only devices, RSC/EXD/RNM-capable devices, timeout recovery, repoll, and forced reprobe.
- Inject backend `in()` timeout and `out()` failure paths to verify tasklet rescheduling and stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hil_mlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc.c

## Purpose
`hp_sdc.c` is the HP System Device Controller driver for PA-RISC and HP300-style systems. It owns the i8042-like SDC hardware registers, services SDC interrupts, provides callback hooks for timer/HIL/cooked events, and exports a queued transaction engine used by higher-level drivers such as `hp_sdc_mlc.c`.

## Important APIs, types, and functions
- Exported transaction APIs are `__hp_sdc_enqueue_transaction()`, `hp_sdc_enqueue_transaction()`, and `hp_sdc_dequeue_transaction()`.
- Exported hook APIs are `hp_sdc_request_timer_irq()`, `hp_sdc_request_hil_irq()`, `hp_sdc_request_cooked_irq()` and matching release functions.
- The single global `hp_i8042_sdc hp_sdc` holds all device state: I/O addresses, IRQs, interrupt mask, tasklet/timer, hook callbacks, read/write queue indices, transaction array, register cache `r7[]`, input-buffer-full tracking, and locks.
- `hp_sdc_status_in8()`, `hp_sdc_data_in8()`, `hp_sdc_status_out8()`, `hp_sdc_data_out8()`, and `hp_sdc_spin_ibf()` are the low-level SDC register access primitives.
- `hp_sdc_isr()` demultiplexes hardware interrupt status into timer, register-transaction, HIL, PUP, and cooked paths.
- `hp_sdc_take()` appends register-read status/data pairs to the current transaction and completes its semaphore or callback when enough data has arrived.
- `hp_sdc_put()` is the transaction scheduler. It serializes output to slow SDC hardware, advances actions, starts reads, updates the interrupt mask, and interleaves queued transactions.
- `hp_sdc_tasklet()` handles read timeouts and invokes `hp_sdc_put()`.

## Control flow
Module init registers the platform-specific discovery path. On PA-RISC the parisc bus probe fills the SDC I/O and IRQ fields, calls `hp_sdc_init()`, and schedules delayed loading of `hp_sdc_mlc`. On HP300 the module probes fixed I/O addresses.

`hp_sdc_init()` initializes locks and queue state, claims I/O/IRQ resources, installs the normal and NMI interrupt handlers, drains the controller, initializes the tasklet, synchronizes the cached output buffer registers through a semaphore-backed transaction, and starts the keepalive timer. `hp_sdc_register()` then reads the keyboard controller config byte, detects old/new SDC style, optionally reads extended config, and writes the self-test register for new-style SDCs.

At runtime clients enqueue `hp_sdc_transaction` objects. The tasklet calls `hp_sdc_put()`, which skips work while IBF is set, finds an eligible transaction, executes action bytes in the transaction sequence, writes precommands/data/data-register updates/postcommands, starts reads by setting `rcurr` and `rqty`, and completes semaphore or callback actions. IRQ context calls `hp_sdc_take()` for register reads and hook callbacks for asynchronous SDC/HIL events.

Exit masks SDC sub-function interrupts, waits for IBF to clear, frees IRQs, deletes the timer, kills the tasklet, cancels delayed module loading, and unregisters the parisc driver where applicable.

## State and persistence
The driver has one global controller instance. Transaction state is in RAM and protected by `hp_sdc.lock` and `hp_sdc.rtq_lock`; callback hooks are protected by `hp_sdc.hook_lock`; IBF tracking is protected by `hp_sdc.ibf_lock`. The cached write-index register and data-register bytes reduce I/O but are not persistent. Hardware configuration changes, interrupt masks, and self-test register writes persist in the SDC until firmware or hardware reset.

## Dependencies and integration points
The file depends on HP SDC protocol definitions from `<linux/hp_sdc.h>`, HIL constants, parisc or m68k I/O accessors, platform-specific discovery, Linux IRQs, tasklets, timers, semaphores, and exported symbols consumed by `hp_sdc_mlc` and other HP SDC clients.

## Risks
- The transaction sequence format is compact and stateful; malformed `seq`, `idx`, `actidx`, or `endidx` values can desynchronize the scheduler or complete the wrong action.
- `hp_sdc_dequeue_transaction()` has a TODO noting it may remove a transaction before completion.
- Timeout handling marks actions dead and may invoke callbacks from tasklet context, which differs from normal IRQ hook context.
- Busy-waiting in `hp_sdc_spin_ibf()` and IBF polling paths is hardware-sensitive and can waste CPU if the SDC wedges.
- The driver assumes a single SDC. Duplicate device discovery is rejected only by the global `hp_sdc.dev` state.
- Error cleanup on some init paths releases fixed regions conditionally; platform-specific resource paths need hardware coverage.

## Test signals
- Build on HPPA/HP300-capable configurations and verify exported symbols match `hp_sdc_mlc`.
- Hardware tests should cover old-style and new-style SDC detection, config-byte read timeout, extended-config read, interrupt-mask updates, delayed `hp_sdc_mlc` autoload, and module unload.
- Transaction tests should cover data-register writes with cached `r7[]`, precommand/dataout/postcommand/datain combinations, queue-full behavior, duplicate transaction rejection, read timeouts, and semaphore/callback completions.
- IRQ tests should inject timer, HIL command/data, PUP, cooked, register, and unknown status classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc_mlc.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc_mlc.c

## Purpose
`hp_sdc_mlc.c` is the hardware-access backend that connects the generic HIL MLC state machine in `hil_mlc.c` to HP System Device Controller raw HIL services from `hp_sdc.c`. It translates SDC HIL interrupts into HIL packets and translates MLC output/CTS requests into SDC transactions.

## Important APIs, types, and functions
- The module owns one static `hil_mlc hp_sdc_mlc`.
- `struct hp_sdc_mlc_priv_s` stores emulated test mode, a reusable `hp_sdc_transaction`, transaction sequence storage, and state for pairing SDC 5X status bytes with data bytes.
- `hp_sdc_mlc_isr()` is registered through `hp_sdc_request_hil_irq()` and fills `mlc->ipacket[]`, handles SDC HIL errors, releases `mlc->isem`, and schedules the MLC tasklet when a match, record termination, or error occurs.
- `hp_sdc_mlc_in()` implements the MLC input callback, returning success, timeout, or still-waiting state based on `isem`, timeout values, and emulated controller-test mode.
- `hp_sdc_mlc_cts()` implements clear-to-send by reading `HP_SDC_CMD_READ_USE` and checking `HP_SDC_USE_LOOP` through a semaphore-backed SDC transaction.
- `hp_sdc_mlc_out()` implements HIL output by building SDC transactions for `HP_SDC_CMD_DO_HIL` data commands or `HP_SDC_CMD_SET_LPC` loop-control commands.

## Control flow
Module init initializes the private reusable transaction and assigns `cts`, `in`, `out`, and `priv` in the static MLC object. It registers the MLC with `hil_mlc_register()`, then requests the raw HIL IRQ hook from `hp_sdc`. If the hook request fails, it unregisters the MLC.

When `hil_mlc` asks to send a packet, `hp_sdc_mlc_out()` takes `osem`, handles test-mode control packets locally when possible, validates unsupported APE/IPF combinations, fills the reusable SDC transaction sequence, and enqueues it. The SDC transaction completion releases `osem` or `csem`, allowing the MLC state machine to advance.

Incoming raw HIL SDC interrupts enter `hp_sdc_mlc_isr()`. Status/data events are packed into HIL packet words, address bits are normalized across related bytes, error statuses are converted into HIL error bits, and the generic MLC tasklet is scheduled once the expected packet or an error/termination condition is reached. Exit releases the HIL IRQ hook and unregisters the MLC.

## State and persistence
All state is runtime-only. The static MLC and private transaction are reused for the single onboard SDC-backed loop. Semaphores in the MLC coordinate input, output, and loop-use polling. `emtestmode` emulates HIL controller test responses instead of sending real SDC HIL data. No persistent settings are saved by this module.

## Dependencies and integration points
This file depends directly on `hil_mlc_register()`/`hil_mlc_unregister()` and the HP SDC exported transaction and HIL hook APIs. It also depends on HIL packet constants and SDC status/error definitions. It is the glue loaded after `hp_sdc` discovers and initializes the controller.

## Risks
- The reusable transaction object must not be enqueued concurrently for two actions; semaphore and state-machine assumptions are critical.
- Several invalid protocol situations use `BUG_ON()`, so unexpected control packets or loop-busy states can crash the kernel rather than returning an error.
- ISR packet assembly depends on SDC-specific 5X status/data ordering and address correction; subtle protocol changes can break discovery.
- `hp_sdc_mlc_in()` uses timeout state prepared by `hil_mlc`; incorrect `instart`/`intimeout` handling can cause false timeouts or hangs.

## Test signals
- Build with HP SDC and HIL MLC enabled to catch exported-symbol and structure drift.
- Exercise module load/unload after `hp_sdc` initialization, including denial of the raw HIL hook.
- Hardware or simulated SDC tests should cover normal HIL data, command status, SDC error statuses, loop reconfiguration notifications, input timeout, controller test mode, and loop-use busy handling.
- Verify `hil_mlc` device discovery works through this backend and that semaphores are released on all SDC completion and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hp_sdc_mlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hyperv-keyboard.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/hyperv-keyboard.c

## Purpose
`hyperv-keyboard.c` exposes the Microsoft Hyper-V synthetic keyboard device as a Linux serio port. It negotiates the Hyper-V keyboard protocol over VMBus, receives host keystroke messages, converts them into XT keyboard scancode bytes, and feeds them to upper-layer keyboard drivers through serio.

## Important APIs, types, and functions
- Synthetic protocol types include `enum synth_kbd_msg_type`, `struct synth_kbd_protocol_request`, `struct synth_kbd_protocol_response`, and `struct synth_kbd_keystroke`.
- `struct hv_kbd_dev` stores the Hyper-V device, serio port, protocol request/response buffers, negotiation completion, and a spinlock-protected `started` flag.
- `hv_kbd_connect_to_vsp()` sends a protocol version request and waits up to 10 seconds for an accepted response.
- `hv_kbd_on_channel_callback()` iterates VMBus packets and dispatches them through `hv_kbd_handle_received_packet()`.
- `hv_kbd_on_receive()` validates message lengths, completes protocol negotiation responses, converts `IS_E0`, `IS_E1`, and `IS_BREAK` keystroke flags to XT prefixes/release bits, and calls `serio_interrupt()`.
- `hv_kbd_start()` and `hv_kbd_stop()` toggle whether incoming events are delivered to the serio port.
- `hv_kbd_probe()`, `hv_kbd_remove()`, `hv_kbd_suspend()`, and `hv_kbd_resume()` manage VMBus channel and serio lifetimes.

## Control flow
Probe allocates `hv_kbd_dev` and a `SERIO_8042_XL` serio port, stores driver data on the Hyper-V device, opens the VMBus channel with keyboard ring sizes, negotiates protocol version 1.0, registers the serio port, and enables device wakeup.

The VMBus callback receives packet descriptors. In-band packets with valid payload size are interpreted as synthetic keyboard messages. Protocol responses are copied and complete the negotiation wait. Keyboard events are delivered only while the serio port is started; the driver emits optional E0/E1 prefix bytes, then the make code with the release bit set for break events. Key-down events trigger a hard wakeup event so the keyboard can wake the guest.

Suspend closes the VMBus channel. Resume reopens the channel and renegotiates the protocol. Remove unregisters the serio port, closes the channel, frees driver state, and clears Hyper-V driver data.

## State and persistence
The only persistent runtime state is the negotiated VMBus channel, protocol response buffer, and `started` delivery flag. No key state is cached. The host is the source of keyboard events, and settings are not persisted by the driver.

## Dependencies and integration points
The driver integrates with the Hyper-V VMBus driver model using `HV_KBD_GUID`, VMBus ring buffers, completion waits, Linux power-management wakeup helpers, and the serio keyboard stack. It intentionally presents the device as an 8042-compatible translated keyboard stream.

## Risks
- The host controls message contents. The driver validates minimal lengths but otherwise trusts message semantics.
- Events arriving before `hv_kbd_start()` or after `hv_kbd_stop()` are dropped under the spinlock.
- VMBus close on suspend discards pending packets; resume depends on successful re-negotiation.
- The conversion handles E0/E1 prefixes and the release bit but does not support Unicode event payloads despite the protocol flag existing.
- Probe failure cleanup must free both allocated objects and close the channel in the right order.

## Test signals
- Build with Hyper-V input support and verify the VMBus device ID table exports `HV_KBD_GUID`.
- Guest tests should cover protocol acceptance, protocol rejection, negotiation timeout, malformed short packets, normal make/break keys, E0/E1-prefixed keys, wakeup on key-down only, suspend/resume, and remove during active input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/hyperv-keyboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-acpipnpio.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042-acpipnpio.h

## Purpose
`i8042-acpipnpio.h` is the x86/IA64/LoongArch ACPI/PNP low-level platform layer included by `i8042.h`. It supplies I/O port accessors, default IRQ/register values, large DMI quirk handling, optional PNP resource discovery, firmware IDs, and platform init/exit hooks for the generic `i8042.c` controller driver.

## Important APIs, types, and functions
- It defines the physical path strings, `I8042_KBD_IRQ`, `I8042_AUX_IRQ`, `I8042_COMMAND_REG`, `I8042_STATUS_REG`, and `I8042_DATA_REG` used by `i8042.c`.
- Inline accessors `i8042_read_data()`, `i8042_read_status()`, `i8042_write_data()`, and `i8042_write_command()` wrap `inb()`/`outb()`.
- X86 quirk bits `SERIO_QUIRK_*` mirror i8042 module parameters such as `nokbd`, `noaux`, `nomux`, `unlock`, `probe_defer`, reset policy, direct mode, dumb keyboard, no loop, no timeout, keyboard reset, Dritek, no PNP, and no restore.
- `i8042_dmi_quirk_table[]` is a first-match DMI table for system-specific i8042 behavior overrides.
- `i8042_pnp_kbd_probe()` and `i8042_pnp_aux_probe()` collect PNP port, IRQ, name, firmware ID, and keyboard fwnode information.
- `i8042_pnp_init()` registers synchronous PNP keyboard/AUX drivers, validates or falls back to default resources, handles laptop AUX IRQ-test bypass, and updates the global register/IRQ variables.
- `i8042_check_quirks()` applies the matched DMI quirk to `i8042.c` globals.
- `i8042_platform_init()` sets defaults, checks platform absence, applies quirks, invokes PNP detection, and sends x86 A20/null commands for firmware compatibility.

## Control flow
When the generic driver calls `i8042_platform_init()`, this header first rejects platforms known not to have an i8042. It assigns default ISA IRQs, applies IA64 reset policy, processes DMI quirks, logs the active quirk set, then attempts PNP detection unless disabled. PNP probes run synchronously and may provide alternate I/O ports, IRQs, firmware names, and fwnodes.

If PNP finds no devices, the code either returns `-ENODEV` on platforms that require firmware enumeration or falls back to direct probing when legacy i8042 is expected. If PNP resources are malformed, it warns and substitutes defaults. On x86 it also sets `i8042_bypass_aux_irq_test` for laptop DMI matches when PNP data looks reliable. Platform exit unregisters PNP drivers.

## State and persistence
This header mutates global driver configuration variables before `i8042.c` creates the platform device. It persists no state outside the running kernel. PNP driver registration state and discovered device counts are kept in static booleans/counters until platform exit.

## Dependencies and integration points
It depends on ACPI, PNP, DMI, architecture IRQ mapping, x86 legacy platform flags, I/O port access, and globals declared in `i8042.c` before including `i8042.h`. It supplies firmware IDs and the keyboard fwnode used later when the serio ports are created.

## Risks
- The DMI quirk table is order-dependent; a broad vendor entry before a specific model entry can change behavior for many machines.
- PNP resource validation intentionally falls back to defaults for common firmware bugs, which can mask real resource conflicts.
- `i8042_bypass_aux_irq_test` trusts PNP and laptop DMI data, so bad firmware can cause false AUX presence.
- The header writes `i8042_*` globals defined in the including C file, making include order and configuration guards important.
- x86 A20 and null-command firmware workarounds touch legacy controller state even before full probe.

## Test signals
- Build with combinations of `CONFIG_X86`, `CONFIG_IA64`, `CONFIG_LOONGARCH`, and `CONFIG_PNP`.
- DMI tests should confirm first-match quirk behavior and module-parameter override of default reset policy.
- PNP tests should cover no devices, keyboard-only, AUX-only, invalid ports, missing IRQs, laptop AUX IRQ-test bypass, firmware ID propagation, and fwnode assignment.
- Boot tests should verify direct-probe fallback only occurs on platforms where legacy i8042 is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-acpipnpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-io.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042-io.h

## Purpose
`i8042-io.h` is the generic legacy I/O-port platform backend for `i8042.c` when no more specific architecture header is selected. It defines ISA-style register addresses, IRQs, physical names, and simple `inb()`/`outb()` accessors.

## Important APIs, types, and functions
- Defines `I8042_KBD_PHYS_DESC`, `I8042_AUX_PHYS_DESC`, and `I8042_MUX_PHYS_DESC` as `isa0060` paths.
- Defines keyboard/AUX IRQs as architecture-provided ARM values, Open Firmware PPC values, or the legacy defaults 1 and 12.
- Defines command/status/data port constants `0x64`, `0x64`, and `0x60`.
- Provides inline `i8042_read_data()`, `i8042_read_status()`, `i8042_write_data()`, and `i8042_write_command()`.
- `i8042_platform_init()` optionally checks PPC legacy I/O safety, requests the 16-byte I/O region except on SH/Alpha, and sets `i8042_reset` to always reset.
- `i8042_platform_exit()` releases the requested region where applicable.

## Control flow
The generic i8042 module includes this header through `i8042.h` on unsupported-special-case architectures. Platform init runs before controller probing, claims the fixed legacy port range when appropriate, and configures reset policy. Platform exit releases the port range after the controller driver unregisters.

## State and persistence
No private runtime state is stored here. It mutates the including file's `i8042_reset` global and claims/releases I/O port ownership for the current boot only.

## Dependencies and integration points
This header depends on legacy I/O port accessors, optional PPC `check_legacy_ioport()`, and IRQ definitions from architecture headers. It is tightly coupled to `i8042.c` globals through inclusion.

## Risks
- Fixed legacy port probing can be unsafe on systems where firmware reserves or virtualizes the i8042 range; PPC has an explicit guard but other architectures rely on config selection.
- Region claiming is skipped on SH and Alpha, so conflicts must be handled elsewhere.
- Forced reset policy may be too aggressive for unusual hardware.

## Test signals
- Build-test on ARM, PPC, SH, Alpha, and generic non-special architectures.
- Boot/probe tests should cover missing region, PPC legacy I/O rejection, successful region claim, and cleanup release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-ip22io.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042-ip22io.h

## Purpose
`i8042-ip22io.h` is the SGI IP22/HPC3 low-level backend for the generic i8042 driver. It maps i8042 data and command access onto SGI IOC keyboard/mouse registers and uses the SGI keyboard IRQ for both keyboard and AUX paths.

## Important APIs, types, and functions
- Defines physical names with the `hpc3ps2` prefix.
- Maps `I8042_KBD_IRQ` and `I8042_AUX_IRQ` to `SGI_KEYBD_IRQ`.
- Defines register macros as addresses of `sgioc->kbdmouse.command` and `sgioc->kbdmouse.data`.
- Provides inline byte accessors that read/write the `sgioc->kbdmouse` fields directly.
- `i8042_platform_init()` sets `i8042_reset` to always reset; request/release memory-region code is disabled with `#if 0`.

## Control flow
When selected by `CONFIG_SGI_HAS_I8042`, this header supplies direct HPC3 register operations to `i8042.c`. The generic driver performs all controller probing, IRQ registration, and serio port management using these macros and accessors.

## State and persistence
The header stores no private state. It mutates only the generic driver's reset policy. Hardware register effects are transient controller state.

## Dependencies and integration points
It depends on SGI IOC/IP22 architecture headers and the global `sgioc` mapping. It integrates the generic i8042 logic with SGI's memory-mapped keyboard/mouse controller layout.

## Risks
- Both KBD and AUX use the same IRQ, so generic shared IRQ handling must correctly classify data by status bits.
- The resource request/release paths are disabled because the addresses are virtual, leaving ownership enforcement to platform setup.
- Direct struct-field I/O assumes `sgioc` is valid before i8042 init.

## Test signals
- Build with `CONFIG_SGI_HAS_I8042`.
- SGI IP22 hardware tests should verify keyboard and mouse input, shared IRQ dispatch, reset behavior, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-ip22io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-jazzio.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042-jazzio.h

## Purpose
`i8042-jazzio.h` is the MIPS Jazz low-level backend for `i8042.c`. It adapts the generic driver to the R4030/Jazz keyboard controller registers and IRQ assignments.

## Important APIs, types, and functions
- Defines physical names with the `R4030` prefix.
- Maps keyboard and AUX IRQs to `JAZZ_KEYBOARD_IRQ` and `JAZZ_MOUSE_IRQ`.
- Defines data and command/status registers as fields of `jazz_kh`.
- Provides inline read/write accessors for `jazz_kh->data` and `jazz_kh->command`.
- Platform init/exit contain disabled memory-region request/release stubs.

## Control flow
With `CONFIG_MACH_JAZZ`, the generic i8042 driver uses these macros and accessors for all hardware operations. The generic code handles controller checks, port setup, IRQ registration, and serio registration.

## State and persistence
No header-local state is stored. Controller register changes are transient. Unlike several other backends, this header does not alter the generic reset mode.

## Dependencies and integration points
It depends on `<asm/jazz.h>` and the architecture-provided `jazz_kh` mapping. It integrates the generic i8042 state machine with Jazz memory-mapped keyboard hardware.

## Risks
- The resource management code is disabled because the address is virtual, so conflict prevention is external.
- Correct operation depends on `jazz_kh` being mapped and valid before i8042 initialization.
- Separate keyboard and mouse IRQs must match platform firmware definitions.

## Test signals
- Build with `CONFIG_MACH_JAZZ`.
- Platform tests should verify keyboard and mouse IRQ delivery, data/status register access, and clean unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-jazzio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-snirm.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042-snirm.h

## Purpose
`i8042-snirm.h` is the SNI RM low-level backend for `i8042.c`. It maps the controller through an MMIO base chosen by SNI board type and supplies board-specific IRQ numbers.

## Important APIs, types, and functions
- Static globals `i8042_kbd_irq`, `i8042_aux_irq`, and `kbd_iobase` back the generic IRQ and register macros.
- Register macros use offsets `0x60` and `0x64` from `kbd_iobase`.
- Inline accessors use `readb()`/`writeb()` for MMIO access.
- `i8042_platform_init()` checks `sni_brd_type`: RM200 maps `0x16000000` and uses IRQs 33/44; other boards map `0x14000000` and use IRQs 1/12.
- `i8042_platform_exit()` is empty.

## Control flow
With `CONFIG_SNI_RM`, platform init maps the controller base and sets IRQs before generic i8042 probing. Generic `i8042.c` then uses the MMIO accessors for command/data operations and the selected IRQs for serio ports.

## State and persistence
The mapped `kbd_iobase` and IRQ globals persist for the driver lifetime. No persistent hardware configuration is saved. The exit path does not unmap `kbd_iobase`.

## Dependencies and integration points
It depends on `<asm/sni.h>`, SNI board-type detection, MMIO mapping, and generic i8042 globals. It integrates non-ISA SNI hardware into the generic i8042 driver.

## Risks
- `i8042_platform_exit()` does not call `iounmap()`, so mapping cleanup relies on process lifetime or historical platform expectations.
- Only two hardcoded physical bases are supported.
- Incorrect board-type detection yields wrong IRQs and I/O base.

## Test signals
- Build with `CONFIG_SNI_RM`.
- Hardware tests should cover RM200 and non-RM200 boards, mapping failure, keyboard/AUX IRQ delivery, and unload/reload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-snirm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-sparcio.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042-sparcio.h

## Purpose
`i8042-sparcio.h` is the SPARC low-level backend for `i8042.c`. It discovers Open Firmware 8042 keyboard/mouse nodes, maps the keyboard register resource, obtains IRQs, and handles a special hardcoded JavaStation "MrCoffee" path.

## Important APIs, types, and functions
- Static globals `i8042_kbd_irq`, `i8042_aux_irq`, `kbd_iobase`, and `kbd_res` back generic register and IRQ macros.
- Inline accessors use `readb()`/`writeb()` at offsets `0x60` and `0x64`.
- `sparc_i8042_probe()` walks child OF nodes, recognizes keyboard names `kb_ps2`/`keyboard` and mouse names `kdmouse`/`mouse`, maps the keyboard resource with `of_ioremap()`, and records IRQs.
- `sparc_i8042_remove()` unmaps the keyboard resource.
- `i8042_is_mr_coffee()` detects the JavaStation-1 root node.
- `i8042_platform_init()` either uses hardcoded JavaStation register/IRQ values or registers the OF platform driver, validates discovered IRQs, sets reset policy, and returns readiness to generic i8042.

## Control flow
On PCI-capable SPARC builds, the generic i8042 init calls this platform init. JavaStation systems bypass OF child probing and map a fixed register range. Other systems register a small platform driver that probes OF `8042` nodes. If either keyboard or AUX IRQ is missing after probe, init unmaps any partial mapping and fails with `-ENODEV`. Platform exit unregisters the platform driver except on JavaStation.

## State and persistence
The header keeps mapped MMIO and IRQs in static globals for the lifetime of the generic driver. It does not persist settings. JavaStation mappings are not explicitly unmapped in the exit path.

## Dependencies and integration points
It depends on OF/platform-device APIs, SPARC prom/oplib headers, MMIO helpers, and generic i8042 globals. It bridges Open Firmware device nodes into the generic i8042 controller driver.

## Risks
- `of_find_device_by_node()` return values are assumed usable; malformed OF/platform-device state can lead to invalid resource or IRQ access.
- Partial discovery cleanup handles `kbd_iobase` but can be fragile if child resources are unusual.
- JavaStation hardcoded values are platform-specific and bypass normal resource management.
- Without `CONFIG_PCI`, platform init always returns `-ENODEV`.

## Test signals
- Build with SPARC `CONFIG_PCI` enabled and disabled.
- OF tests should cover keyboard/mouse child names, child IRQ fallback to parent IRQ, missing IRQs, mapping failure, and driver unregister cleanup.
- JavaStation tests should verify hardcoded IRQ/base operation and reset policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042-sparcio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042.c

## Purpose
`i8042.c` is the generic Linux i8042 keyboard/mouse controller driver. It probes the controller, configures keyboard and AUX/multiplexed ports, dispatches controller bytes to serio ports, exports low-level command/filter helpers, handles platform quirks, and restores controller state across power management and shutdown.

## Important APIs, types, and functions
- Exported helpers are `i8042_command()`, `i8042_lock_chip()`, `i8042_unlock_chip()`, `i8042_install_filter()`, and `i8042_remove_filter()`.
- Module parameters control probing and quirks: `nokbd`, `noaux`, `nomux`, `unlock`, `probe_defer`, `reset`, `direct`, `dumbkbd`, `noloop`, `notimeout`, `kbdreset`, x86 `dritek`, PNP `nopnp`, `forcenorestore`, and debug options.
- `struct i8042_port` stores each serio port pointer, IRQ, existence flag, driver-bound flag, and mux index. The global port array covers KBD, legacy AUX, and four mux ports.
- `__i8042_command()` implements serialized controller command I/O with encoded send/receive counts.
- `i8042_handle_data()` is the IRQ data path: read status/data, determine KBD/AUX/MUX port, apply error flags and platform filter, then call `serio_interrupt()`.
- Probe helpers include `i8042_check_aux()`, `i8042_check_mux()`, `i8042_set_mux_mode()`, `i8042_controller_check()`, `i8042_controller_selftest()`, `i8042_controller_init()`, `i8042_setup_aux()`, and `i8042_setup_kbd()`.
- PM helpers reset or restore CTR state, MUX mode, wake IRQs, and active ports across suspend, resume, hibernate, poweroff, and restore.

## Control flow
Module init calls `i8042_platform_init()` from the selected platform header, checks the controller by flushing it, marks the controller present, registers a platform driver, creates the `i8042` platform device, registers a serio bus notifier, and installs panic LED blinking.

Probe optionally self-tests the controller, initializes the control register by disabling ports and choosing translated/direct keyboard mode, applies x86 Dritek setup, probes AUX unless disabled, probes keyboard unless disabled, requests shared IRQs, enables ports, and registers all created serio ports. AUX probing uses loopback/external tests, AUX disable/enable bit tests, optional keyboard reset, and an IRQ-delivery test unless bypassed. MUX probing uses the active multiplexing loopback sequence and creates four AUX ports when supported.

At runtime keyboard writes go directly to the data register under `i8042_lock`, while AUX writes use controller commands. IRQs call `i8042_interrupt()` and `i8042_handle_data()`. Port start/stop toggles whether the IRQ path may deliver to the serio object; stop also synchronizes both IRQs before returning. Remove unregisters ports, frees IRQs, and restores the original controller control register. Shutdown and PM paths reset/restore hardware state to avoid confusing firmware.

## State and persistence
State is entirely runtime and hardware-controller state. The driver saves `i8042_initial_ctr`, maintains current `i8042_ctr`, tracks MUX presence, IRQ registration, port existence, installed filter, and keyboard ACK suppression for panic blinking. It restores the original CTR on reset/shutdown where configured but does not persist settings beyond the current boot.

## Dependencies and integration points
The file depends on the selected `i8042.h` backend for register access and platform discovery, the serio bus, platform bus, IRQ subsystem, Linux PM helpers, notifier infrastructure, and PS/2 users through `serio->ps2_cmd_mutex`. Architecture/platform quirks come from the included backend header.

## Risks
- i8042 hardware and firmware are notoriously inconsistent; AUX loop, IRQ delivery, MUX error semantics, keylock, and reset policy all have quirk-heavy behavior.
- `i8042_command()` and port writes must be serialized correctly or one port can abort another port's command.
- The IRQ path drops bytes when a port no longer exists or a platform filter consumes data; incorrect filtering can break devices.
- MUX error recovery guesses the last transmit port for some malformed statuses, which can misroute bytes on broken controllers.
- PM restore choices depend on firmware involvement and `forcenorestore`; wrong policy can lose keyboard/mouse input after resume.
- Panic blinking writes keyboard LED commands outside normal command flow and suppresses ACKs later.

## Test signals
- Build across all platform backends and with/without PNP, PM, debug, and x86 options.
- Boot tests should cover no controller, KBD-only, AUX-only, MUX, no-MUX, no-loop, no-timeout, direct mode, dumb keyboard, and DMI/PNP quirks.
- Runtime tests should cover command serialization, keyboard/AUX writes, shared IRQ handling, parity/timeout flags, platform filters, port unregister races, and panic blink ACK suppression.
- PM tests should cover suspend-to-RAM, suspend-to-idle, hibernate thaw/restore, wake IRQ enable/disable, and shutdown reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042.h -->
# sources/distributed-fs/ceph-client/drivers/input/serio/i8042.h

## Purpose
`i8042.h` is the shared private header for `i8042.c`. It selects the correct architecture/platform low-level backend and defines common controller constants and debug macros.

## Important APIs, types, and functions
- Backend selection includes Jazz, SGI IP22, SNI RM, SPARC, x86/LoongArch ACPI/PNP, or generic I/O.
- Defines `I8042_CTL_TIMEOUT`, `I8042_RET_CTL_TEST`, `I8042_BUFFER_SIZE`, and `I8042_NUM_MUX_PORTS`.
- Provides `dbg_init()`, `dbg()`, and `filter_dbg()` macros. In debug builds they include elapsed jiffies and optionally mask keyboard data unless `i8042_unmask_kbd_data` is set; otherwise they compile away.

## Control flow
The header is included once by `i8042.c` after module parameters and global variables are declared. The selected backend supplies platform init/exit and register/IRQ macros, while the common constants are used by the generic controller logic.

## State and persistence
In debug builds it declares `i8042_start_time` for relative log timestamps. It stores no persistent state.

## Dependencies and integration points
This header is tightly coupled to `i8042.c` because the backend headers reference globals such as `i8042_reset`, `i8042_debug`, and `i8042_unmask_kbd_data`. It also depends on build-time architecture configuration to choose exactly one backend path.

## Risks
- Backend include selection controls all hardware access; wrong Kconfig selection can route generic i8042 code to invalid registers.
- Debug filtering protects keyboard data by default, but enabling unmasked debug can expose sensitive keystrokes in logs.
- Backend headers depend on symbols declared by the including C file, so moving include order can break builds.

## Test signals
- Compile all supported backend configurations.
- Debug builds should verify masked and unmasked keyboard traffic logging and zero overhead in non-debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/i8042.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ioc3kbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/ioc3kbd.c

## Purpose
`ioc3kbd.c` is the SGI IOC3 PS/2 serio driver. It exposes separate keyboard and auxiliary serio ports backed by IOC3 keyboard/mouse registers and dispatches packed receive data from a shared interrupt.

## Important APIs, types, and functions
- `struct ioc3kbd_data` stores the mapped IOC3 serio registers, keyboard/AUX serio objects, active flags, and IRQ.
- `ioc3kbd_wait()` polls IOC3 CSR write-pending bits with a bounded 50 us delay loop.
- `ioc3kbd_write()` and `ioc3aux_write()` wait for keyboard or mouse write-pending bits to clear before writing `k_wd` or `m_wd`.
- `ioc3kbd_start()`/`ioc3kbd_stop()` and AUX equivalents toggle whether IRQ data is delivered.
- `ioc3kbd_process_data()` extracts up to three valid bytes from an IOC3 receive word and calls `serio_interrupt()`.
- `ioc3kbd_intr()` reads keyboard and mouse receive registers and dispatches data to active ports.
- `ioc3kbd_probe()` maps resources, allocates two serio ports, registers them, requests the shared IRQ, and enables the ports by writing `km_csr`.

## Control flow
The platform driver matches `"ioc3-kbd"`. Probe maps register resource 0, gets IRQ 0, allocates driver data and two serio objects, fills type/write/start/stop/name/phys fields, stores driver data, registers both serio ports, requests the shared IRQ, and enables keyboard/mouse clamps. Remove frees the IRQ and unregisters both ports.

## State and persistence
The driver tracks only runtime port-active booleans and the mapped register pointer. It does not persist configuration. The hardware CSR is changed on probe to enable ports.

## Dependencies and integration points
It depends on platform device resources, SGI IOC3 register definitions from `<asm/sn/ioc3.h>`, MMIO accessors, IRQs, and the serio core.

## Risks
- Serio ports are registered before IRQ request; IRQ request failure unregisters both, but transient users may have seen the ports.
- The interrupt handler always returns handled after reading registers, relying on shared IRQ tolerance.
- `ioc3kbd_process_data()` does not attach parity/frame flags; hardware error details are not surfaced.
- Active booleans are not explicitly locked; they rely on serio start/stop and IRQ ordering.

## Test signals
- Build with SGI IOC3 platform support.
- Hardware tests should verify keyboard and mouse writes, three-byte receive packing, shared IRQ behavior, IRQ request failure cleanup, and removal while ports are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ioc3kbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/libps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/libps2.c

## Purpose
`libps2.c` is the shared PS/2 protocol helper library used by keyboard, mouse, and touchpad drivers. It serializes commands, sends bytes with ACK/NAK handling and retries, collects command responses, handles common protocol quirks, and provides a common interrupt helper for PS/2 device drivers.

## Important APIs, types, and functions
- Exported APIs include `ps2_sendbyte()`, `ps2_begin_command()`, `ps2_end_command()`, `ps2_drain()`, `ps2_is_keyboard_id()`, `__ps2_command()`, `ps2_command()`, `ps2_sliced_command()`, `ps2_init()`, and `ps2_interrupt()`.
- Internal flags `PS2_FLAG_ACK`, `PS2_FLAG_CMD`, `PS2_FLAG_CMD1`, `PS2_FLAG_WAITID`, `PS2_FLAG_NAK`, and `PS2_FLAG_PASS_NOACK` track command and ACK state.
- `ps2_do_sendbyte()` writes one byte, waits for ACK/NAK/ERR, and retries NAKs up to a caller-supplied attempt count.
- `__ps2_command()` decodes the command word's send/receive counts, prepares response buffers, sends command and parameters, waits for response bytes, handles reset and GETID timeouts, and copies results back to `param`.
- `ps2_handle_ack()` processes ACK/NAK/ERR and GETID mouse-ID workarounds.
- `ps2_handle_response()` stores response bytes in reverse order and wakes waiters after first and final response bytes.
- `ps2_interrupt()` runs the caller's pre-receive handler and routes bytes to ACK handling, command response collection, or the caller's receive handler.

## Control flow
Drivers initialize a `ps2dev` with `ps2_init()`, providing pre-receive and receive callbacks. Process-context command callers use `ps2_command()` or the begin/end pair for compound commands. The library pauses serio RX while mutating command state, resumes RX while waiting for interrupts, and uses a waitqueue to sleep until ACK or response completion.

Incoming bytes from the serio interrupt path enter `ps2_interrupt()`. If the pre-receive handler reports an error, `ps2_cleanup()` clears command state and wakes waiters. If the byte is processable, the library consumes it as an ACK while waiting for ACK, as a command response while a command is active, or passes it to the driver's normal receive handler.

## State and persistence
State lives in the caller-owned `struct ps2dev`: command mutex, waitqueue, flags, `nak`, response count, response buffer, serio pointer, and callbacks. Nothing is persisted beyond the device lifetime. Command serialization may use the serio port's shared `ps2_cmd_mutex` when the underlying controller requires cross-port serialization.

## Dependencies and integration points
The library depends on the serio core, waitqueues, mutexes, KMSAN unpoisoning for response buffers, PS/2 command conventions, and optional i8042 shared command mutexes. It is consumed by higher-level PS/2 protocol drivers such as keyboard, mouse, and touchpad modules.

## Risks
- RX pause/continue windows are subtle; missed state transitions can lose ACKs or pass command responses to normal input handlers.
- GETID and reset commands have special timeout/response rules; regressions can break device detection.
- `PS2_FLAG_PASS_NOACK` intentionally passes unexpected bytes to receive handlers for some commands, which can interleave normal traffic with command handling.
- `ps2dev->cmdbuf` is size-limited; receive counts are checked, but callers must provide valid `param` buffers for send/receive commands.
- Interrupt handlers and process-context command waiters share flags and waitqueues, so lock ordering with serio locks and controller mutexes is important.

## Test signals
- Build all PS/2 keyboard/mouse/touchpad users with lockdep and KMSAN-enabled configurations.
- Unit-style protocol tests should cover ACK, NAK retry, ERR after NAK, command timeout, reset BAT one-byte/two-byte responses, GETID keyboard and mouse IDs, sliced commands, drain, and pre-receive error cleanup.
- Integration tests should verify shared i8042 command serialization across keyboard and AUX ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/libps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/maceps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/maceps2.c

## Purpose
`maceps2.c` is the SGI O2 MACE PS/2 controller driver. It creates two serio ports, one for the MACE keyboard PS/2 register block and one for the mouse block.

## Important APIs, types, and functions
- `struct maceps2_data` stores a pointer to a MACE PS/2 port register block and its IRQ.
- `maceps2_write()` waits up to `MACE_PS2_TIMEOUT` 50 us units for `PS2_STATUS_TX_EMPTY`, then writes the transmit register.
- `maceps2_interrupt()` reads one received byte when `PS2_STATUS_RX_FULL` is set and delivers it through `serio_interrupt()`.
- `maceps2_open()` requests the port IRQ, resets the hardware, and enables RX clock, TX, and RX interrupts.
- `maceps2_close()` resets the port and frees the IRQ.
- `maceps2_allocate_port()` allocates and initializes a `SERIO_8042` port for the selected index.
- `maceps2_init()` registers a platform driver, allocates a synthetic platform device, and binds static MACE register/IRQ data.

## Control flow
Module init registers the platform driver, allocates and adds a `"maceps2"` platform device, and initializes the two static `port_data` entries from the global `mace` register mapping. Probe allocates both serio ports and registers them. Each serio open requests its own IRQ and enables the hardware. Remove unregisters both ports. Module exit unregisters the synthetic device and driver.

## State and persistence
The driver uses static arrays for two port data objects and serio pointers plus one synthetic platform device pointer. Hardware control registers are reset/enabled on open and reset on close. No persistent settings are saved.

## Dependencies and integration points
It depends on SGI IP32 MACE architecture headers, platform device infrastructure, IRQ handling, MMIO-like MACE register access, and the serio core.

## Risks
- `maceps2_write()` returns `-1` instead of a standard errno on timeout.
- Interrupt handling ignores parity/framing status bits and forwards only the byte.
- The driver creates its own platform device rather than relying on firmware enumeration.
- Probe registers both ports even though IRQs are only requested later at open time, so IRQ failures are user-visible at open.

## Test signals
- Build on SGI O2/IP32 configurations.
- Hardware tests should cover keyboard and mouse open/close, IRQ request failure, write timeout, RX delivery, unload/reload, and parity/framing error behavior expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/maceps2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/olpc_apsp.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/olpc_apsp.c

## Purpose
`olpc_apsp.c` is the OLPC AP-SP serio driver for XO systems where firmware on a Marvell security processor bit-bangs PS/2 devices. It exposes separate keyboard and touchpad serio ports and demultiplexes bytes from WTM registers.

## Important APIs, types, and functions
- `struct olpc_apsp` stores the device, keyboard and touchpad serio ports, mapped WTM register base, open count, and IRQ.
- `olpc_apsp_write()` waits for command FIFO space and writes a port-tagged byte to `SECURE_PROCESSOR_COMMAND`.
- `olpc_apsp_rx()` acknowledges SP command-complete interrupts, reads `COMMAND_RETURN_STATUS`, selects keyboard or touchpad serio by the upper byte, delivers the lower byte, clears the interrupt, and reports a wakeup event.
- `olpc_apsp_open()` increments a shared open count, verifies the SP command status on first open, and unmasks interrupt 0.
- `olpc_apsp_close()` decrements open count and masks interrupt 0 when the last port closes.
- `olpc_apsp_probe()` maps resources, creates keyboard `SERIO_8042_XL` and touchpad `SERIO_8042` ports, requests the IRQ, enables wakeup, and stores driver data.

## Control flow
The OF platform driver matches `olpc,ap-sp`. Probe maps WTM registers and IRQ, registers the keyboard port first, then the touchpad port, requests the shared IRQ, and enables device wakeup. Runtime writes are tagged with keyboard or touchpad port ID. Runtime interrupts read a tagged return word and forward it to the corresponding serio port. Remove frees the IRQ and unregisters both ports.

## State and persistence
Open count and port pointers are runtime-only. The driver changes the WTM interrupt mask based on whether either serio port is open. It does not persist SP configuration.

## Dependencies and integration points
It depends on OF platform matching, MMIO resource mapping, OLPC/Marvell WTM register semantics, IRQ handling, PM wakeup helpers, and the serio input stack.

## Risks
- `olpc_apsp_open()` increments `open_count` before checking command readiness; if the first open fails, the count is not rolled back in this function.
- FIFO-full handling uses up to 50 ms of `mdelay()`, which blocks in write paths.
- Unknown port tags default to touchpad because the IRQ path uses keyboard only for exact `KEYBOARD_PORT`.
- Keyboard port is registered before touchpad allocation and IRQ request; cleanup handles failures but transient registration ordering matters.

## Test signals
- Device-tree match and resource mapping tests for `olpc,ap-sp`.
- Hardware tests should cover keyboard/touchpad RX demux, command FIFO full timeout, first-open SP-not-ready failure, interrupt masking across two open ports, wakeup events, and remove while ports are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/olpc_apsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/parkbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/parkbd.c

## Purpose
`parkbd.c` is a parallel-port adapter driver for connecting AT or XT keyboards through a simple passive adapter. It bit-bangs keyboard clock/data lines via parport control/status bits and exposes the result as one serio port.

## Important APIs, types, and functions
- Module parameters select `port` and `mode` (`SERIO_8042` AT by default, XT when zero).
- Global state tracks the current bit buffer, bit counter, last interrupt jiffies, write mode, start time, claimed parport device, and serio port.
- `parkbd_readlines()` reads keyboard clock/data from parport status bits; `parkbd_writelines()` drives output through parport control bits.
- `parkbd_write()` builds an AT keyboard host-to-device frame with parity and starts write mode; XT mode rejects writes.
- `parkbd_interrupt()` advances either transmit bits or receive bits on parport IRQ callbacks, handles timeouts, and delivers completed bytes through `serio_interrupt()`.
- `parkbd_getport()` registers and exclusively claims the selected parport.
- `parkbd_attach()` claims the configured parport, allocates the serio port, initializes line state, and registers the port. `parkbd_detach()` releases resources.

## Control flow
The parport driver calls `parkbd_attach()` for each discovered parallel port. Only the configured parport number is used. After exclusive claim, the driver creates a serio port whose type is the selected AT/XT mode and uses the parport IRQ callback for bit timing. Detach releases the parport, unregisters the serio port, unregisters the parport device, and clears the global port pointer.

## State and persistence
All state is global because the driver supports one selected adapter. It stores transient bit-level receive/transmit state and timing in jiffies. No persistent settings are saved beyond module parameters for the current load.

## Dependencies and integration points
The file depends on the parport subsystem, IRQ callbacks from parport, serio core, jiffies timing, and a specific external passive wiring adapter.

## Risks
- Bit-banging depends on interrupt timing and adapter wiring; missed IRQs reset the frame after `HZ/100`.
- Global state means only one adapter is supported and concurrency assumptions are simple.
- AT write mode is minimal and has no explicit ACK handling in this driver.
- Incorrect `mode` can decode the wrong frame length or shift.
- The driver exclusively claims the parallel port, which can conflict with printer or other parport users.

## Test signals
- Build with parport and serio support.
- Hardware tests should cover selected vs non-selected parports, AT and XT receive frame decoding, AT writes, timeout/reset behavior, detach cleanup, and parallel-port claim failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/parkbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/pcips2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/pcips2.c

## Purpose
`pcips2.c` is a PCI PS/2 keyboard/mouse serio driver, originally for Mobility Electronics docking hardware. It maps a PCI I/O BAR with simple control/status/data registers and exposes a single PS/2 serio port per PCI function.

## Important APIs, types, and functions
- `struct pcips2_data` stores the serio port, I/O base, and PCI device.
- `pcips2_write()` busy-waits until `PS2_STAT_TXEMPTY` and writes a byte to the data register.
- `pcips2_interrupt()` drains all available RX bytes, handles all-ones disconnect/status sentinel, computes parity flags, and calls `serio_interrupt()`.
- `pcips2_flush_input()` drains pending input before enabling IRQs.
- `pcips2_open()` enables the controller, flushes input, requests the shared PCI IRQ, and enables RX interrupts.
- `pcips2_close()` disables the controller and frees the IRQ.
- PCI probe enables the device, requests regions, allocates driver/serio state, fills serio fields, records BAR 0 base, and registers the port.

## Control flow
The PCI driver matches Mobility device IDs `0x0123` keyboard and `0x0124` mouse with input class constraints. Probe performs PCI enable and region claim, creates the serio port, stores driver data, and registers the port. Open enables hardware and IRQ delivery. Interrupt drains bytes until RX empty. Remove unregisters the serio port, frees state, releases PCI regions, and disables the device.

## State and persistence
State is per PCI function and stored in `pcips2_data`. Hardware control bits are enabled on open and cleared on close. No persistent settings are saved.

## Dependencies and integration points
It depends on the PCI subsystem, legacy I/O port access through `inb()`/`outb()`, shared IRQs, hweight parity computation, and serio core.

## Risks
- `pcips2_write()` has no timeout while waiting for TX empty, so wedged hardware can spin indefinitely.
- Open writes control state before IRQ request; failure leaves the controller disabled through the final control write.
- Parity interpretation depends on both hardware parity status and computed byte parity.
- The driver assumes BAR 0 is an I/O port resource with the expected register layout.

## Test signals
- Build with PCI and serio support.
- Hardware or emulation tests should cover both PCI IDs/classes, PCI enable/request failure, open IRQ failure, RX drain, parity flag reporting, all-ones sentinel handling, write under TX-busy conditions, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/pcips2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ps2-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/ps2-gpio.c

## Purpose
`ps2-gpio.c` is a GPIO bit-banged PS/2 serio bus driver. It samples PS/2 clock falling-edge interrupts and the data GPIO to receive bytes, optionally drives open-drain clock/data GPIOs to transmit bytes, and exposes a platform/DT-backed serio port.

## Important APIs, types, and functions
- `struct ps2_gpio_data` stores the device, serio port, RX/TX mode, open-drain GPIOs, write-enable flag, IRQ, IRQ timestamps, RX bit state, TX bit state, completion, mutex, and delayed work.
- `ps2_gpio_open()`/`ps2_gpio_close()` enable and disable the IRQ and flush pending TX work.
- `ps2_gpio_write()` serializes process-context writes with a mutex, starts TX, and waits for a completion; atomic-context writes start TX without waiting.
- `__ps2_gpio_write()` disables IRQs, pulls clock low, switches to TX mode, stores the byte, and schedules delayed work to begin the host request-to-send sequence.
- `ps2_gpio_irq_rx()` validates PS/2 timing, samples start/data/parity/stop bits, reports parity, filters ACK/NACK when write support is disabled, and requests resend on errors.
- `ps2_gpio_irq_tx()` advances host-to-device bits, releases the data line for stop, samples ACK, completes writes, or retries on timeout/NACK.
- `ps2_gpio_get_props()` obtains open-drain `data` and `clk` GPIOs and optional `write-enable`.
- `ps2_gpio_probe()` validates fast GPIOs, requests a non-threaded no-auto-enable IRQ, initializes TX work/completion/mutex, and registers the serio port.

## Control flow
Probe creates driver and serio state, reads platform properties, rejects GPIOs that can sleep, gets the IRQ, installs `ps2_gpio_irq()` with `IRQF_NO_THREAD | IRQF_NO_AUTOEN`, initializes RX mode and TX state, then registers the port. Open enables the IRQ. In RX mode, each IRQ samples one bit and completes a byte after the stop bit. In TX mode, the delayed work releases the clock after the host inhibit interval, then each IRQ drives the next bit until the ACK bit completes the transfer. Remove unregisters the serio port.

## State and persistence
The driver stores transient bit counters, current byte, timestamps, mode, and TX completion state. It does not persist settings. GPIO direction and IRQ enable state change dynamically during open, close, RX, and TX.

## Dependencies and integration points
It depends on gpiolib consumer APIs, platform/OF properties, hard IRQ timing, delayed work, completions, mutexes, ktime, and the serio core. The external GPIO wiring must support open-drain PS/2 signaling and low-latency GPIO reads/writes.

## Risks
- Timing is tight: GPIOs connected via sleeping controllers are rejected, but interrupt latency can still cause missed bits.
- RX error handling sends `RESEND` even when errors are caused by local timing, which may loop if write support or wiring is faulty.
- TX retry is recursive through `__ps2_gpio_write()` from IRQ context, requiring careful state consistency.
- Process-context writes can wait up to 10 seconds.
- Parity errors are tolerated and forwarded when write support is enabled but cause resend when write support is disabled.

## Test signals
- Build with GPIO, OF, and serio support.
- DT/property tests should cover missing GPIOs, sleeping GPIO rejection, missing IRQ, write-enable false/true, and remove cleanup.
- Hardware tests should cover RX timing limits, parity and stop-bit errors, ACK/NACK TX completion, resend behavior, IRQ disabled on close, and concurrent write serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ps2-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ps2mult.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/ps2mult.c

## Purpose
`ps2mult.c` is a serio driver for the TQC PS/2 multiplexer protocol. It attaches to a parent RS232/PS2MULT serio link and creates two child PS/2 serio ports for keyboard and mouse traffic.

## Important APIs, types, and functions
- Protocol control bytes include keyboard selector, mouse selector, escape, byte-sync, session start, and session end.
- `struct ps2mult_port` stores each child serio, selector byte, and registration state.
- `struct ps2mult` stores the parent serio, two child ports, spinlock, current input/output port, and escape state.
- `ps2mult_select_port()` writes a selector to the parent and records the selected output port.
- `ps2mult_serio_write()` switches output port if needed, escapes protocol control bytes in payload, and writes to the parent.
- Child `start`/`stop` callbacks mark the child as registered for interrupt delivery.
- `ps2mult_reset()` sends session end/start and selects the keyboard port.
- `ps2mult_connect()` opens the parent serio, creates and registers child ports, and resets the session.
- `ps2mult_interrupt()` parses incoming control bytes, updates input port and escape state, and forwards payload to the selected registered child.

## Control flow
The driver binds to parent serio devices of type `SERIO_RS232` and protocol `SERIO_PS2MULT`. Connect requires a parent write method, allocates state, creates keyboard and mouse child ports, opens the parent, resets the multiplexer session, and registers the children. Outbound writes from a child select that child and escape control bytes. Inbound bytes from the parent either control session/input selection or are forwarded to the current child. Disconnect sends session end, closes the parent, frees state, and clears driver data; serio core handles children.

## State and persistence
State is runtime-only: selected input/output port, escape latch, and child registration flags. Reset reinitializes the external multiplexer session but no settings are persisted.

## Dependencies and integration points
It depends on the serio core both as a serio driver for the parent and as a creator of child serio ports. It integrates a simple byte-stuffed multiplexer protocol with standard PS/2 child drivers.

## Risks
- Parent write failures are ignored in selector and payload writes.
- Input routing depends on protocol synchronization; lost selector or escape bytes can misroute data until BSYNC or reset.
- Disconnect relies on serio core child cleanup and only frees the parent `ps2mult` state.
- `registered` flags avoid delivery to stopped children but do not buffer data.

## Test signals
- Bind tests should cover parent without write support, allocation failure, parent open failure, and reconnect reset.
- Protocol tests should cover escaped control bytes in payload, BSYNC behavior, selector switching, session start/end bytes, child start/stop delivery suppression, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/ps2mult.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/q40kbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/q40kbd.c

## Purpose
`q40kbd.c` is the Q40 m68k PS/2 keyboard controller driver. It exposes the Q40 keyboard registers as a single `SERIO_8042` port and handles the Q40 keyboard IRQ.

## Important APIs, types, and functions
- `struct q40kbd` stores the serio port and a spinlock protecting register access.
- `q40kbd_interrupt()` checks the keyboard interrupt bit, reads `KEYCODE_REG`, delivers the byte, and unlocks the keyboard interrupt latch.
- `q40kbd_flush()` drains up to 100 pending keycodes while the interrupt bit is set.
- `q40kbd_stop()` disables keyboard IRQ generation and unlocks the keyboard.
- `q40kbd_open()` flushes stale data, unlocks the keyboard, and enables keyboard IRQs.
- `q40kbd_close()` stops IRQ generation and flushes stale data.
- `q40kbd_probe()` allocates state and serio, requests `Q40_IRQ_KEYBOARD`, registers the port, and stores driver data.

## Control flow
The platform probe allocates driver objects, initializes the spinlock and serio fields, stops the keyboard hardware, requests the fixed Q40 keyboard IRQ, registers the serio port, and records driver data. Open enables hardware IRQs; interrupts deliver bytes; close disables hardware IRQs. Remove unregisters the port first so close disables hardware, then frees the IRQ and state.

## State and persistence
Only the port pointer and spinlock are stored. Hardware IRQ enable/latch state changes on open, close, interrupt, and probe. No persistent settings are saved.

## Dependencies and integration points
It depends on Q40 architecture register helpers/constants, platform driver infrastructure, IRQ handling, spinlocks, and serio.

## Risks
- The driver requests the IRQ at probe, not open, so the interrupt handler exists even while the serio port is closed; hardware IRQs are disabled by `q40kbd_stop()`.
- Remove frees only `q40kbd`; the serio object is freed by serio unregister semantics.
- Flush has a fixed 100-byte cap.

## Test signals
- Build on Q40/m68k configurations.
- Hardware tests should cover probe IRQ failure, open/close IRQ enable, interrupt byte delivery, flush of stale data, and remove while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/q40kbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/rpckbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/rpckbd.c

## Purpose
`rpckbd.c` is the Acorn RiscPC IOMD keyboard controller driver. It presents the IOMD KART keyboard interface as a single PS/2-style serio port.

## Important APIs, types, and functions
- `struct rpckbd_data` stores separate transmit and receive IRQ numbers.
- `rpckbd_write()` waits until the transmit-ready bit is set in `IOMD_KCTRL`, then writes `IOMD_KARTTX`.
- `rpckbd_rx()` drains all available receive bytes from `IOMD_KARTRX` while the RX-ready bit is set and delivers them through `serio_interrupt()`.
- `rpckbd_tx()` is a placeholder TX IRQ handler that returns handled.
- `rpckbd_open()` resets the keyboard state machine, clears one RX byte, requests RX and TX IRQs, and rolls back RX IRQ if TX IRQ request fails.
- `rpckbd_close()` frees both IRQs.
- Probe gets two platform IRQs, allocates data and serio, fills port fields, stores driver data, and registers the port.

## Control flow
The platform driver named `"kart"` probes resources, creates one serio port, and registers it. Open resets hardware and requests IRQs. RX interrupts drain and forward bytes. Close frees IRQs. Remove unregisters the serio port and frees `rpckbd_data`.

## State and persistence
Per-port state is only the two IRQ numbers. Hardware state is reset at open. No persistent settings are saved.

## Dependencies and integration points
It depends on Acorn ARM machine headers, IOMD register accessors, platform IRQ resources, and the serio core.

## Risks
- `rpckbd_write()` busy-waits indefinitely for TX ready.
- The TX IRQ handler does not manage transmit state; it only acknowledges the IRQ.
- Remove frees `rpckbd_data` after unregister but relies on serio core to free the serio object.
- Open requests IRQs each time; failures leave the port unusable until retried.

## Test signals
- Build on RiscPC/IOMD configurations.
- Hardware tests should cover platform IRQ discovery, open reset sequence, RX drain loop, TX-ready wait, IRQ request rollback, close, and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/rpckbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/sa1111ps2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/sa1111ps2.c

## Purpose
`sa1111ps2.c` is the SA1111 companion-chip PS/2 controller driver. It exposes each SA1111 PS/2 device as a serio port, performs line self-tests, manages RX/TX IRQs, and handles a small transmit queue.

## Important APIs, types, and functions
- `struct ps2if` stores the serio port, SA1111 device, mapped base, RX/TX IRQs, open flag, spinlock, ring-buffer indices, and a four-byte TX buffer.
- `ps2_rxint()` drains RX bytes, clears stop/framing errors, computes `SERIO_FRAME` and `SERIO_PARITY` flags, and calls `serio_interrupt()`.
- `ps2_txint()` writes queued bytes when TX is empty and disables the TX IRQ when the queue is empty.
- `ps2_write()` writes immediately if TX empty or queues into the small ring buffer and enables TX IRQ.
- `ps2_open()` enables the SA1111 device, requests RX and TX IRQs, enables RX wake, and enables the controller.
- `ps2_close()` disables the controller, wake, IRQs, and device.
- `ps2_clear_input()`, `ps2_test_one()`, and `ps2_test()` flush and validate PS/2 clock/data line control during probe.
- `ps2_probe()` allocates state, gets IRQs, claims the memory resource, initializes clock divisors, tests the interface, disables the device, and registers the serio port.

## Control flow
The SA1111 bus driver matches `SA1111_DEVID_PS2`. Probe allocates objects, records IRQs, claims the device memory resource, uses the parent-provided mapping, enables the device temporarily, sets timing registers, clears input, tests line control, disables the device, and registers the port. Open re-enables the device and IRQs for active use. Remove unregisters the port, releases the memory resource, clears driver data, and frees state.

## State and persistence
Runtime state is per SA1111 PS/2 interface. The TX ring buffer is in RAM and protected by a spinlock. Hardware control and timing registers are programmed on probe/open and disabled on close. No persistent settings are stored.

## Dependencies and integration points
It depends on the SA1111 bus/device APIs, SA1111 IRQ lookup, MMIO register access, wake IRQ helpers, resource management, spinlocks, and the serio core.

## Risks
- The TX buffer is only four bytes and silently drops a byte if the ring is full because `ps2_write()` returns success even when no space is available.
- `ps2_clear_input()` reads the data register until `0xff`, assuming that sentinel means empty.
- Probe self-test manipulates clock/data force bits and may fail on boards with unusual wiring.
- RX parity is computed from both hardware status and byte hweight; mistakes affect upper PS/2 protocol error handling.

## Test signals
- Build with SA1111 support.
- Hardware tests should cover IRQ lookup failure, memory-region conflict, line self-test failure, RX parity/frame error reporting, TX immediate and queued paths, TX buffer-full behavior, wake IRQ enable/disable, and remove while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/sa1111ps2.c -->
