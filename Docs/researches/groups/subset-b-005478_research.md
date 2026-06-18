# subset-b-005478 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/usbtmc.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/class/usbtmc.c

Purpose: implements the Linux USB Test and Measurement Class character driver for USBTMC and USBTMC-USB488 instruments. It binds application-specific USB interfaces with subclass 3 and protocols 0 or 1, exposes them as `/dev/usbtmc%d`, and provides synchronous read/write, asynchronous ioctl-based transfers, USB488 status/SRQ handling, clear/abort/control requests, poll, fasync, suspend/resume, reset, and disconnect handling.

Important types and APIs: `struct usbtmc_device_data` is the per-interface object containing the `usb_device`, endpoint addresses, device/interface capabilities, shared USBTMC tags, interrupt-in state, `kref`, `io_mutex`, wait queue, async notification state, and the list of open file handles. `struct usbtmc_file_data` is per-open state with timeout, term char config, EOM and auto-abort flags, SRQ byte/assertion, error lock, submitted and read anchors, write semaphore, and transfer status counters. The file operations are `usbtmc_open`, `usbtmc_release`, `usbtmc_flush`, `usbtmc_read`, `usbtmc_write`, `usbtmc_ioctl`, `usbtmc_poll`, and `usbtmc_fasync`. USB driver callbacks include `usbtmc_probe`, `usbtmc_disconnect`, `usbtmc_suspend`, `usbtmc_resume`, `usbtmc_pre_reset`, and `usbtmc_post_reset`.

Control flow: probe allocates device state, finds bulk IN/OUT endpoints with `usb_find_common_endpoints`, optionally finds interrupt IN, reads capabilities via `GET_CAPABILITIES`, submits the interrupt URB if present, and registers the USB class device. `open` allocates file state, initializes anchors and defaults, gets a `kref`, and links the file into `file_list`. Normal `write` builds a DEV_DEP_MSG_OUT USBTMC header, sends the first URB, advances `bTag`, then delegates the remaining payload to `usbtmc_generic_write`. Normal `read` sends REQUEST_DEV_DEP_MSG_IN, validates the returned bulk-in header, checks the returned tag, copies the first packet payload, then delegates additional packets to `usbtmc_generic_read`. The generic paths use anchored URBs, callbacks, wait queues, and a max of `MAX_URBS_IN_FLIGHT`.

State and persistence: no on-disk persistence exists. Runtime state is in the USB interface object, per-open state, anchors, wait queues, and atomics. `bTag`, `bTag_last_write`, and `bTag_last_read` are shared per device and protected by `io_mutex` around I/O. Per-file options such as timeout, EOM, term char, and auto-abort are reset on each open. Disconnect marks `zombie`, wakes waiters, kills/scuttles anchored URBs, deregisters the minor, and drops references. The interrupt URB holds an additional `kref` while active.

Dependencies and integration points: depends on usbcore, `linux/usb/tmc.h` ioctl definitions, USB class registration, URB anchors, bulk/control/interrupt pipe helpers, kref, fasync, poll, wait queues, and sysfs attribute groups. It integrates with USB PM and reset callbacks, class-device minor allocation at base 176, and USB488 SRQ through interrupt notifications, `SIGIO`, `EPOLLPRI`, and per-file SRQ flags.

Risks: the driver exposes a broad userspace ioctl surface and must validate copy sizes, status bytes, tags, endpoint presence, and timeout values. Shared `data->fasync` is per-device while SRQ assertion is per-open, so multi-open behavior should be tested. Generic async reads return `-EAGAIN` when no read URB has completed and kill all submitted URBs on exit/error, which can surprise callers mixing async and sync operations. Clear/abort loops rely on bounded read/status retries; devices that never short-packet or report pending can cause long waits. Probe error unwinding around interrupt URB allocation/submission is reference-sensitive. `usbtmc_ioctl_request` permits class/vendor control requests up to `USBTMC_BUFSIZE` and must stay constrained.

Test signals: use USBTMC device or dummy_hcd/gadget tests for probe, missing endpoint rejection, capability sysfs values, read header/tag validation, EOM and term-char options, large writes split across URBs, async write/read ioctls, timeout behavior, auto-abort on transfer failure, SRQ delivery through poll/fasync and `WAIT_SRQ`, disconnect while blocked in read/SRQ wait, suspend/resume resubmission of interrupt URB, and pre/post reset cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/class/usbtmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/common/Kconfig

Purpose: declares Kconfig symbols for USB common support and small common USB facilities. `USB_COMMON` is the shared tristate selected by host/gadget/common helpers. `USB_LED_TRIG` enables USB activity LED triggers. `USB_ULPI_BUS` enables the ULPI PHY bus implementation. `USB_CONN_GPIO` enables GPIO-based USB role/connection detection.

Important symbols: `USB_COMMON` is a bare tristate used as a build target. `USB_LED_TRIG` is a bool depending on `LEDS_CLASS`, `USB_COMMON`, and `LEDS_TRIGGERS`. `USB_ULPI_BUS` is tristate, selects `USB_COMMON`, and builds module `ulpi`. `USB_CONN_GPIO` is tristate, depends on `GPIOLIB`, selects `USB_ROLE_SWITCH` and `POWER_SUPPLY`, and builds `usb-conn-gpio.ko`.

Control flow and state: Kconfig has no runtime control flow. The important behavior is dependency propagation into the Makefile: enabled symbols decide whether `common.o`, `debug.o`, `led.o`, `ulpi.o`, `usb-conn-gpio.o`, and `usb-otg-fsm.o` are compiled.

Dependencies and integration points: integrates with LED triggers, PHY/ULPI controller drivers, GPIO descriptor APIs, USB role switch, and power-supply class. `USB_OTG_FSM` is not declared here but is consumed by the common Makefile, with the actual option declared in the USB core Kconfig.

Risks: dependency changes can alter module boundaries and link availability for exported helpers. `USB_LED_TRIG` is bool rather than tristate, so its code is folded into `usb-common` rather than becoming a standalone module. `USB_CONN_GPIO` selecting role switch and power supply can pull extra subsystems into embedded builds.

Test signals: verify `allyesconfig`, `allmodconfig`, minimal host-only, gadget-only, `USB_ULPI_BUS=m`, and `USB_CONN_GPIO=m` builds. Confirm resulting modules and selected dependencies match the help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/common/Makefile

Purpose: maps common USB Kconfig symbols to kernel objects. It builds `usb-common.o` from `common.o` plus optional `debug.o` and `led.o`, and builds separate objects for GPIO connector detection, OTG FSM, and ULPI bus.

Important build rules: `obj-$(CONFIG_USB_COMMON) += usb-common.o`; `usb-common-y += common.o`; `usb-common-$(CONFIG_TRACING) += debug.o`; `usb-common-$(CONFIG_USB_LED_TRIG) += led.o`; `obj-$(CONFIG_USB_CONN_GPIO) += usb-conn-gpio.o`; `obj-$(CONFIG_USB_OTG_FSM) += usb-otg-fsm.o`; `obj-$(CONFIG_USB_ULPI_BUS) += ulpi.o`.

Control flow and state: build-only file. The main state is the object composition of `usb-common.o`: tracing controls whether `usb_decode_ctrl` is linked, and LED trigger support controls whether `ledtrig_usb_init/exit` do real registration.

Dependencies and integration points: ties Kconfig to objects consumed by host, gadget, PHY, and OTG code. `debug.o` is compiled into usb-common for trace formatting, not as an independent module. `usb-otg-fsm.o` is built from a core Kconfig symbol even though the source lives in common.

Risks: moving objects between `usb-common-y` and separate `obj-*` lines changes symbol export/module loading behavior. Missing `debug.o` under tracing would break tracepoints that call `usb_decode_ctrl`. Missing `led.o` when `USB_LED_TRIG` is enabled would leave declared hooks unresolved.

Test signals: run kernel builds with `CONFIG_TRACING=y/n`, `CONFIG_USB_LED_TRIG=y`, `CONFIG_USB_COMMON=m/y`, and module builds for `ulpi`, `usb-conn-gpio`, and `usb-otg-fsm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/common.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/common/common.c

Purpose: provides exported USB helper functions shared by host and gadget stacks. It formats endpoint, OTG, speed, and device states; parses firmware properties for maximum speed, SuperSpeedPlus rate, dual-role mode, and default role-switch mode; decodes endpoint intervals; supplies OF helpers for OTG/PHY relationships; and initializes shared USB debugfs and optional LED triggers.

Important APIs: exported helpers include `usb_ep_type_string`, `usb_otg_state_string`, `usb_speed_string`, `usb_get_maximum_speed`, `usb_get_maximum_ssp_rate`, `usb_state_string`, `usb_get_dr_mode`, `usb_get_role_switch_default_mode`, `usb_decode_interval`, `of_usb_get_dr_mode_by_phy`, `of_usb_host_tpl_support`, `of_usb_update_otg_caps`, and `usb_of_get_companion_dev`. It exports globals `usb_debug_root` and `usb_dynids_lock`.

Control flow: most functions are bounded table lookups or property readers. `usb_decode_interval` converts endpoint `bInterval` to microseconds based on endpoint type and speed. OF helper `of_usb_get_dr_mode_by_phy` scans available controller nodes with `phys`, matches the requested PHY node and argument, then reads that controller's `dr_mode`. `of_usb_update_otg_caps` validates `otg-rev` and applies `hnp-disable`, `srp-disable`, and `adp-disable` properties. `usb_common_init` creates `/sys/kernel/debug/usb` and registers LED triggers; exit reverses this.

State and persistence: no persistent state. Runtime globals are the debugfs root dentry and the dynamic ID mutex. Property-derived values are returned to callers and not cached here.

Dependencies and integration points: depends on generic device properties, OF, platform-device lookup, debugfs, USB chapter 9 definitions, OTG data structures, and optional LED trigger hooks declared in `common.h`. It is foundational for other USB core files such as `devices.c`, tracepoints, host controller drivers, gadget drivers, and DT/ACPI described controllers.

Risks: property string matching is strict, so firmware spelling errors fall back to unknown modes. `of_usb_get_dr_mode_by_phy` assumes it finds a controller before the `finish` path reads properties; changes here need careful null handling. Interval decoding must remain aligned with USB spec rules or user-visible diagnostics and scheduler decisions become misleading. `usb_debug_root` lifetime matters for child debugfs users.

Test signals: unit-style tests can exercise table fallbacks, invalid speeds/states, interval decoding for control/bulk/int/isoc endpoints at low/full/high/super speeds, DT fixtures for `maximum-speed`, SSP rate, `dr_mode`, `role-switch-default-mode`, and OTG capability properties, plus debugfs/LED trigger init-exit smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/common.h -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/common/common.h

Purpose: local header for common USB code that abstracts optional LED trigger support behind two functions, `ledtrig_usb_init` and `ledtrig_usb_exit`.

Important APIs: when `CONFIG_USB_LED_TRIG` is enabled, the functions are declared and implemented by `led.c`. Otherwise, static inline no-op definitions are supplied, allowing `common.c` to call them unconditionally.

Control flow and state: no runtime state in the header. Compile-time selection either binds calls to real trigger registration/unregistration or eliminates them through no-op inlines.

Dependencies and integration points: included by `common.c` and `led.c`. It is intentionally narrow, avoiding exposure of the LED trigger objects themselves to the rest of usb-common.

Risks: signatures must match `led.c`; changing init/exit annotations or return types can break `common.c` builds in one configuration but not another. Since disabled support silently no-ops, tests should cover both enabled and disabled configs.

Test signals: compile with `CONFIG_USB_LED_TRIG=y` and `n`, including `W=1` builds, to ensure declarations and inlines match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/debug.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/common/debug.c

Purpose: provides `usb_decode_ctrl`, an exported helper that formats USB control requests into human-readable strings for tracing and diagnostics.

Important functions: internal decoders cover GET_STATUS, SET/CLEAR_FEATURE, SET_ADDRESS, GET/SET_DESCRIPTOR, GET/SET_CONFIGURATION, GET/SET_INTERFACE, SYNCH_FRAME, SET_SEL, and SET_ISOCH_DELAY. `usb_decode_ctrl_generic` formats type, recipient, direction, request, value, index, and length for vendor, class, unknown, or unrecognized standard requests. `usb_decode_device_feature` and `usb_decode_test_mode` name feature selectors and test modes.

Control flow: `usb_decode_ctrl` dispatches by request type. Standard requests are further dispatched by `bRequest`; unsupported requests fall back to generic formatting. Output is written into the caller-provided buffer with `snprintf` and the same pointer is returned, which lets tracepoint print formatters call it inline.

State and persistence: stateless. The only state is the caller's output buffer. The function expects `wValue`, `wIndex`, and `wLength` already converted to CPU byte order.

Dependencies and integration points: depends on USB chapter 9 constants and is built into `usb-common.o` only under `CONFIG_TRACING`. Tracepoints and debug code can use it to keep control-message output consistent.

Risks: buffer size is caller-managed; comments suggest about 200 bytes. Adding longer strings can truncate output. Missing new standard requests or descriptor types reduces diagnostic quality but should not affect USB behavior. Incorrect recipient handling can mislead debugging of interface/endpoint requests.

Test signals: trace or KUnit-style checks for representative standard, class, vendor, unknown, endpoint-direction, test-mode, and descriptor-type requests. Build with tracing enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/led.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/common/led.c

Purpose: registers two LED triggers, `usb-gadget` and `usb-host`, and exposes `usb_led_activity` so USB code can blink activity indicators for gadget or host events.

Important APIs: `DEFINE_LED_TRIGGER` creates `ledtrig_usb_gadget` and `ledtrig_usb_host`. `usb_led_activity(enum usb_led_event ev)` maps the event to a trigger and calls `led_trigger_blink_oneshot` with 30 ms on/off delays. `ledtrig_usb_init` registers the triggers, and `ledtrig_usb_exit` unregisters them.

Control flow and state: initialization registers simple triggers under the LED subsystem. Runtime events are one-shot blink requests; `led_trigger_blink_oneshot` tolerates a NULL trigger, so unsupported/unknown paths do not crash. Exit unregisters both triggers.

Dependencies and integration points: depends on LED class/trigger APIs and USB event enum definitions. Called from `usb_common_init/exit` through `common.h` only when `USB_LED_TRIG` is enabled. Exported `usb_led_activity` is available to host/gadget code.

Risks: trigger registration return values are ignored, so failures are silent. The trigger globals are shared and must be unregistered only after users stop generating events during usb-common teardown. Event enum additions require updating the switch.

Test signals: build with LED trigger support, verify `/sys/class/leds/*/trigger` lists `usb-gadget` and `usb-host`, generate host/gadget activity, and test unload/reload without dangling triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/ulpi.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/common/ulpi.c

Purpose: implements the ULPI PHY bus. USB controller drivers register a ULPI interface with register read/write operations; this code creates a `ulpi` device, reads vendor/product IDs, matches and probes ULPI PHY drivers, emits modaliases for module autoloading, and exposes debugfs register dumps.

Important APIs and types: exported `ulpi_read` and `ulpi_write` call controller-provided ops. `__ulpi_register_driver` and `ulpi_unregister_driver` manage ULPI PHY drivers. `ulpi_register_interface` allocates and registers a `struct ulpi`; `ulpi_unregister_interface` removes debugfs and unregisters the device. The static `ulpi_bus` provides match, uevent, probe, and remove callbacks.

Control flow: registration sets parent, bus, device type, name, and ACPI companion, optionally attaches an OF child named `ulpi`, probes scratch-register access, reads vendor/product registers, requests a matching module by ULPI modalias or OF modalias, then registers the device and creates `debugfs/ulpi/<dev>/regs`. Driver matching prefers OF when no vendor ID or no ID table exists, otherwise matches vendor/product pairs.

State and persistence: runtime state is in `struct ulpi`, its parent ops pointer, device ID fields, optional OF node reference, and the debugfs root. No persistent state. Device release drops the OF node and frees the ULPI object.

Dependencies and integration points: uses Linux device/bus core, module autoloading, OF and ACPI matching, clock defaults via `of_clk_set_defaults`, debugfs, seq_file, and ULPI register definitions. USB controller drivers are producers of ULPI interfaces; PHY drivers are consumers on the ULPI bus.

Risks: controller ops must be valid for all register reads used by debugfs; failed reads abort the register dump. `ulpi_read_id` returns success even when scratch or ID probing fails, relying on OF module request, so probe failures can be deferred to driver matching. `ulpi_register_interface` leaks no registered device on failure, but error paths around device registration and OF references are sensitive. Debugfs register reads can touch live PHY hardware.

Test signals: register a fake or controller-backed ULPI interface, verify modalias content, OF child matching, module autoload request, driver probe/remove, debugfs `regs` output, scratch mismatch fallback, and unregister cleanup under module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/ulpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/usb-conn-gpio.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/common/usb-conn-gpio.c

Purpose: platform driver for GPIO-based USB connector detection. It reads optional ID and VBUS GPIOs, derives the current USB role, drives a USB role switch, optionally controls a VBUS regulator in host mode, and exposes charger online state through the power-supply class.

Important types and functions: `struct usb_conn_info` holds device state, IDA allocated charger ID, role switch, last role, optional regulator, delayed detection work, debounce, GPIO descriptors/IRQs, power-supply descriptor, and initial-detection flag. Key functions are `usb_conn_detect_cable`, `usb_conn_isr`, `usb_charger_get_property`, `usb_conn_psy_register`, `usb_conn_probe`, `usb_conn_remove`, `usb_conn_suspend`, and `usb_conn_resume`.

Control flow: probe gets optional `id` and `vbus` GPIOs and requires at least one. It configures hardware debounce where possible or falls back to delayed work, gets optional VBUS regulator, gets the role switch, registers a USB power supply, requests threaded IRQs on both GPIOs, marks wakeup capable, and queues initial detection. Detection maps GPIO levels to `USB_ROLE_HOST`, `USB_ROLE_DEVICE`, or `USB_ROLE_NONE`; host mode has priority over VBUS. It disables the regulator when leaving host, sets the role switch, enables VBUS regulator when entering host, updates `last_role`, and notifies power supply.

State and persistence: no persistence. Runtime state is kept in `usb_conn_info`; charger ID is allocated from a global IDA and freed on remove. Delayed work coalesces GPIO IRQ changes. Suspend either enables IRQ wake or disables IRQs and selects sleep pinctrl; resume reverses that and queues detection.

Dependencies and integration points: depends on GPIOLIB, IRQ, pinctrl PM, regulator, USB role switch, power supply, OF compatible `gpio-usb-b-connector`, IDA, and system power-efficient workqueue.

Risks: role derivation relies on board GPIO polarity being described correctly. If only one GPIO is present, the code synthesizes the missing signal (`ID=1` for VBUS-only, `VBUS=ID` for ID-only), which must match hardware intent. Regulator enable/disable errors are logged but `last_role` still changes. Repeated role warnings are suppressed only during initial detection. Remove must cancel work before freeing ID/regulator state.

Test signals: DT probe with ID-only, VBUS-only, and both GPIOs; IRQ edge role changes; debounce fallback path; regulator enable/disable in host transitions; power-supply `ONLINE`; suspend/resume with and without wakeup; remove during pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/usb-conn-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/usb-otg-fsm.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/common/usb-otg-fsm.c

Purpose: implements the USB 2.0 OTG finite state machine used by controller drivers that provide an `otg_fsm`. It transitions between A-device and B-device OTG states, starts/stops host or gadget protocols, manages OTG timers, drives VBUS/connect/SOF callbacks, and supports HNP polling.

Important functions: `otg_statemachine` is exported and performs transition decisions under `fsm->lock`. `otg_set_state` executes entry actions for each new state. `otg_leave_state` cleans up timers and flags from the old state. `otg_set_protocol` stops the old host/gadget role and starts the new one. `otg_hnp_polling_work` polls the connected device's OTG status selector and triggers HNP by clearing bus request flags.

Control flow: callers update inputs in `struct otg_fsm` and call `otg_statemachine`. The state machine tests current state plus inputs such as `id`, session valid, bus requests, VBUS valid, connect/suspend/resume flags, ADP/SRP flags, and timer timeout flags. Entry actions call controller-provided OTG helpers such as `otg_drv_vbus`, `otg_chrg_vbus`, `otg_loc_conn`, `otg_loc_sof`, `otg_start_host`, `otg_start_gadget`, `otg_add_timer`, and `otg_del_timer`.

State and persistence: all state is in `struct otg_fsm` and `fsm->otg->state`; no persistence. HNP polling uses delayed work and an optional controller-allocated `host_req_flag` buffer. `fsm->state_changed` reports whether a transition occurred.

Dependencies and integration points: depends on usbcore host/gadget/OTG APIs, hub child lookup, control messages to read/set OTG feature flags, workqueues, timers implemented by controller drivers, and `usb_otg_state_string` from common code.

Risks: transition correctness is highly stateful and tied to OTG spec timing. Missing timer cleanup can cause stale timeout flags. HNP polling assumes port 1 child on root hub and a valid `host_req_flag` buffer. Protocol start/stop failures abort state entry before `fsm->otg->state` is updated. Controllers must serialize input updates with `fsm->lock` discipline.

Test signals: controller or simulated FSM tests for every transition, timeout handling, ID changes, SRP/ADP paths, A/B host/peripheral handoff, HNP polling success/failure, protocol start/stop errors, and suspend/resume interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/common/usb-otg-fsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/Kconfig -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/core/Kconfig

Purpose: declares miscellaneous USB core policy and feature options. These options influence enumeration logging, persist defaults, initialization retry behavior, minor allocation, OTG support, OTG product restrictions, external hub policy, OTG FSM build, USB port LED trigger, autosuspend delay, and default authorization mode.

Important symbols: `USB_ANNOUNCE_NEW_DEVICES`, `USB_DEFAULT_PERSIST`, `USB_FEW_INIT_RETRIES`, `USB_DYNAMIC_MINORS`, `USB_OTG`, `USB_OTG_PRODUCTLIST`, `USB_OTG_DISABLE_EXTERNAL_HUB`, `USB_OTG_FSM`, `USB_LEDS_TRIGGER_USBPORT`, `USB_AUTOSUSPEND_DELAY`, and `USB_DEFAULT_AUTHORIZATION_MODE`. `USB_OTG_FSM` depends on `USB && USB_OTG` and selects `USB_PHY`.

Control flow and state: no runtime control flow here, but defaults become compiled policy or module parameters in usbcore. `USB_DEFAULT_AUTHORIZATION_MODE` is range-limited 0..2 and controls initial authorization behavior for new devices unless overridden by module parameter or command line.

Dependencies and integration points: integrated by `drivers/usb/core/Makefile` and other USB core source files. OTG options affect hub enumeration and OTG FSM build. LED trigger option builds `ledtrig-usbport.o`. Autosuspend and authorization defaults feed core device power/security behavior.

Risks: defaults have user-visible system behavior. Disabling persist can disrupt mounted USB storage across suspend power loss. Authorization mode 2 relies on ACPI internal/external classification. OTG product list and external hub restrictions can intentionally reject devices and should be enabled only for constrained hosts.

Test signals: config matrix builds for USB=y/m, OTG on/off, LED trigger module, dynamic minors, and authorization modes. Runtime tests should inspect sysfs defaults and enumeration behavior under selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/Makefile -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/core/Makefile

Purpose: defines the `usbcore.o` aggregate and optional USB core objects. It is the build map for core enumeration, hub, HCD, URB, message, driver binding, configuration parsing, file/minor handling, buffers, sysfs, endpoints, usbfs devio, notifications, quirks, PHY, ports, tracing, and optional platform integrations.

Important build rules: `usbcore-y` includes `usb.o hub.o hcd.o urb.o message.o driver.o config.o file.o buffer.o sysfs.o endpoint.o devio.o notify.o generic.o quirks.o devices.o phy.o port.o trace.o`. Optional objects include `of.o`, `offload.o`, `hcd-pci.o`, `usb-acpi.o`, and onboard USB platform-device data. `obj-$(CONFIG_USB) += usbcore.o`; `obj-$(CONFIG_USB_LEDS_TRIGGER_USBPORT) += ledtrig-usbport.o`. `CFLAGS_trace.o := -I$(src)` supports trace header inclusion.

Control flow and state: build-only. The object list determines which internal symbols are always present when USB is enabled and which are conditional on OF, XHCI sideband, PCI, ACPI, onboard devices, and port LED triggers.

Dependencies and integration points: ties Kconfig and source files into the kernel module or built-in `usbcore`. `devio.o` exposes `/dev/bus/usb` char operations; `devices.o` exposes topology debug/proc-style output; `config.o` parses descriptors; `buffer.o` serves HCD DMA allocation.

Risks: object ordering can matter for init/exit dependencies. Removing objects from `usbcore-y` can break internal references. `trace.o` include path must remain correct for generated trace definitions.

Test signals: full build matrix for `CONFIG_USB=y/m`, OF/ACPI/PCI variants, XHCI sideband, onboard device support, and USB port LED trigger module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/buffer.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/core/buffer.c

Purpose: provides DMA-coherent buffer allocation helpers for host controller drivers and usbfs mmap. It creates small DMA pools per HCD and routes allocations through local memory pools, DMA pools, coherent DMA allocation, or ordinary pages/kmalloc for PIO-only controllers.

Important APIs: `usb_init_pool_max` adjusts pool sizes for `ARCH_DMA_MINALIGN`. `hcd_buffer_create` and `hcd_buffer_destroy` manage per-HCD DMA pools. `hcd_buffer_alloc`/`hcd_buffer_free` allocate/free arbitrary transfer buffers. `hcd_buffer_alloc_pages`/`hcd_buffer_free_pages` allocate page-sized coherent regions for mmap-capable usbfs buffers.

Control flow: pool creation skips if local memory pool exists or HCD does not use DMA. Allocation first handles zero size, then local memory pool, then PIO-only fallback, then the smallest configured DMA pool that can hold the size, and finally `dma_alloc_coherent`. Free mirrors the same decision tree based on HCD state and size.

State and persistence: per-HCD DMA pools live in `hcd->pool[]`; optional local memory pool is external in `hcd->localmem_pool`. No persistent state. `pool_max[]` is initialized at boot and adjusted for architecture alignment.

Dependencies and integration points: depends on DMA mapping, DMA pools, genalloc local memory pools, HCD helpers, USB bus/HCD conversion, and memory allocation APIs. Used by HCD core and by `devio.c` for mmap'd usbfs transfer buffers.

Risks: size passed to free must match the allocation path; otherwise the wrong pool may be used. Alignment must satisfy architecture DMA requirements. Localmem allocations require correct DMA address handling. PIO fallback uses sentinel DMA values, which callers must treat appropriately.

Test signals: HCD init/destroy with DMA and PIO controllers, allocations at 0, pool thresholds, above-pool sizes, page allocations, localmem pool path, allocation failure unwind, and DMA debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/config.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/core/config.c

Purpose: retrieves, validates, normalizes, stores, and frees USB configuration and BOS descriptors. It turns raw descriptors into `usb_host_config`, `usb_interface_cache`, `usb_host_interface`, and `usb_host_endpoint` structures used by driver binding, endpoint lookup, sysfs, usbfs, and HCD scheduling.

Important APIs and functions: public functions are `usb_get_configuration`, `usb_destroy_configuration`, `usb_release_interface_cache`, `usb_get_bos_descriptor`, and `usb_release_bos_descriptor`. Internal parsers include `usb_parse_configuration`, `usb_parse_interface`, `usb_parse_endpoint`, `usb_parse_ss_endpoint_companion`, `usb_parse_ssp_isoc_endpoint_companion`, `usb_parse_eusb2_isoc_endpoint_companion`, duplicate endpoint checks, and descriptor scanning helpers.

Control flow: `usb_get_configuration` bounds the device's configuration count, allocates config/raw descriptor arrays, reads each config header to learn `wTotalLength`, reads the full descriptor, and calls `usb_parse_configuration`. The parser validates descriptor lengths, counts interfaces/altsettings, stores IADs, allocates interface caches, then parses interfaces and endpoints. Endpoint parsing fixes invalid address bits, filters duplicate or ignored endpoints, adjusts `bInterval`, coerces low-speed bulk endpoints to interrupt, validates maxpacket sizes, handles high-speed and SuperSpeed companion descriptors, and stores class/vendor extra descriptors. BOS parsing reads the BOS header and complete set, validates each device capability length, and stores pointers to recognized capabilities.

State and persistence: descriptor state is cached in `dev->config`, `dev->rawdescriptors`, and `dev->bos`; no disk persistence. Interface caches use krefs because interfaces share altsetting cache data. Raw descriptor buffers remain for usbfs reads.

Dependencies and integration points: depends on USB descriptor definitions, HCD/device helpers, quirk flags, endian conversion, allocation helpers, and device logging. It is called during enumeration and reset/reinit paths and feeds the rest of usbcore.

Risks: descriptor parsing is an attack surface because devices control descriptor bytes. Length checks, hard limits (`USB_MAXCONFIG`, `USB_MAXALTSETTING`, `USB_MAXINTERFACES`, `USB_MAXENDPOINTS`, `USB_MAXIADS`), and quirk handling are critical. Error unwinding must free partially allocated caches. Normalizing descriptors changes what drivers see, so compatibility quirks need regression coverage. BOS capability pointers reference the allocated BOS buffer and become invalid after release.

Test signals: fuzz malformed descriptors, short descriptors, zero configs, too many configs/interfaces/altsettings/endpoints/IADs, duplicate endpoints, invalid intervals/maxpacket values, SuperSpeed and SSP companions, eUSB2 isoc companions, quirk flags, BOS truncation/unknown caps, and destroy/reparse paths under kmemleak/KASAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/devices.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/core/devices.c

Purpose: implements the read operation for the USB devices listing, producing a text snapshot of USB topology, device descriptors, strings, configurations, interfaces, IADs, endpoints, drivers, speeds, and root-hub bandwidth usage.

Important APIs and functions: exported file operations are `usbfs_devices_fops` with `.read = usb_device_read` and `.llseek = no_seek_end_llseek`. Formatting helpers include `class_decode`, `usb_dump_endpoint_descriptor`, `usb_dump_interface_descriptor`, `usb_dump_interface`, `usb_dump_iad_descriptor`, `usb_dump_config_descriptor`, `usb_dump_config`, `usb_dump_device_descriptor`, `usb_dump_device_strings`, `usb_dump_desc`, and recursive `usb_device_dump`.

Control flow: `usb_device_read` locks `usb_bus_idr_lock`, iterates registered USB buses, skips unregistered root hubs, locks the root hub, and recursively dumps each device tree. `usb_device_dump` allocates an 8 KiB scratch buffer per device, formats topology and optional root-hub bandwidth, appends descriptor/config/interface/endpoint lines, handles skip/count for file offsets, copies the requested slice to userspace, frees the buffer, then recurses over child devices while locking each child.

State and persistence: no persistent state. Output is generated live from USB bus/device structures. File position drives skip behavior across reads; no private iterator is stored.

Dependencies and integration points: depends on USB bus IDR, hub child iteration, device locks, descriptor caches from `config.c`, `usb_decode_interval`, HCD bandwidth accounting, and uaccess. It provides the classic `/sys/kernel/debug/usb/devices` or usbfs devices-style text view.

Risks: generated output can be truncated per device if descriptor text exceeds the scratch buffer. Holding `usb_bus_idr_lock` while traversing and locking devices makes lock ordering important. Serial numbers are included when `ALLOW_SERIAL_NUMBER` is defined, which has privacy implications. The recursive traversal must obey `MAX_TOPO_LEVEL`.

Test signals: read with multiple buses, nested hubs, devices disconnecting during read, many configurations/altsettings/endpoints, long strings, root hub bandwidth values, offset/partial reads, and topology depth limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/devio.c -->
# Research: sources/distributed-fs/ceph-client/drivers/usb/core/devio.c

Purpose: implements usbfs character-device access to USB devices under `/dev/bus/usb`. It allows userspace drivers to read descriptors, submit control/bulk/interrupt/isochronous URBs, mmap transfer buffers, claim/release interfaces and ports, disconnect/reconnect kernel drivers, manage streams, control suspend behavior, drop privileges, receive disconnect signals, and reap async completions.

Important types and APIs: `struct usb_dev_state` is per-open state with device/file pointers, async lists, mmap memory list, wait queues, disconnect signal info, credentials, claimed-interface bitmap, disabled bulk endpoints, allowed-interface mask, resume/suspend flags, and privilege-drop state. `struct usb_memory` tracks mmap'd transfer memory with VMA/URB refcounts. `struct async` wraps submitted URBs, owner credentials, userspace pointers, mmap association, memory accounting, status, and bulk-continuation state. Public file operations are `usbdev_file_operations`; lifecycle APIs are `usb_devio_init` and `usb_devio_cleanup`; usbfs interface driver callbacks are grouped in `usbfs_driver`.

Control flow: open looks up the `usb_device` by device number, autoresumes it, initializes per-file lists/waits/credentials, and links into `dev->filelist`. read copies the device descriptor and raw config descriptors. ioctl dispatch locks the device, permits reap operations after disconnect, rejects most commands after disconnect, then routes to control/bulk sync transfers, endpoint reset/clear halt, device reset, interface/config changes, async submit/discard/reap, driver ioctls, claim/release, stream allocation, privilege drop, speed/capability queries, suspend controls, and variable-size connection-info. Async URB submission validates flags, endpoint/interface ownership, control recipients, transfer size, mmap ranges, SG layout, isochronous packet descriptors, and URB flags; completion moves the async object to completed list, records status, copies IN data on reap, wakes waiters, and optionally signals the submitter.

State and persistence: no disk persistence. Global state includes `usbfs_memory_mb`, `usbfs_memory_usage`, `usbfs_mutex`, registered cdev range, and USB notifier. Per-open state persists until release or device removal. Memory usage is globally capped and adjusted for mmap and transfer allocations. Release unclaims interfaces/ports, kills pending async URBs, autosuspends if appropriate, frees completed asyncs, and drops credentials/PIDs. Device removal destroys all async work, wakes waiters, marks lists detached, and sends disconnect signals.

Dependencies and integration points: depends on usbcore, HCD buffer allocation, USB security/credentials/signal helpers, scatterlist, DMA mapping, notifier chain, cdev, poll, compat ioctl support, runtime PM, interface driver claiming, hub port claiming, streams APIs, and uaccess. It is the kernel side of the stable `usbdevfs` UAPI.

Risks: this is a major security boundary because untrusted userspace controls ioctl arguments and USB devices control transfer completion. Critical risks include integer overflow in lengths, stale userspace pointers, mmap lifetime/refcount mistakes, async completion races, disconnect/release/resume races, privilege drop bypass, interface-claim conflicts, bulk continuation endpoint disabling semantics, signal credential handling, and compat struct translation. The code mitigates with caps (`USBFS_XFER_MAX`, `usbfs_memory_mb`, iso packet limits), device locks, spinlocks, refcounts, interface checks, memory accounting, and post-disconnect reap allowances.

Test signals: syzkaller-style usbfs fuzzing; KASAN/KCSAN/lockdep runs; mmap submit/release races; disconnect during blocking reap, wait-for-resume, sync transfers, and async completion; compat ioctls; privilege drop masks; claimed interface/config reset conflicts; bulk continuation failures; SG transfers over/under bus `sg_tablesize`; isochronous packet limit and completion copying; memory limit exhaustion; runtime suspend allow/forbid/wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/core/devio.c -->
