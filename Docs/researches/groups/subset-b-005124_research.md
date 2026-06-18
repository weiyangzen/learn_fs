# Research: subset-b-005124 platform Chrome, CZ.NIC, Goldfish, LoongArch, and Mellanox files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_uart.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_uart.c

## Purpose

This file implements the serdev UART transport for a ChromeOS Embedded Controller. It turns an ACPI-described or OF-described UART-attached EC into a `struct cros_ec_device`, provides packet transfer with the Chrome EC host packet format, and wires suspend/resume into the common EC core.

## Important APIs, Types, And Functions

The main private types are `struct response_info`, which tracks a pending EC response buffer, expected length, status, and wait queue, and `struct cros_ec_uart`, which stores the serdev device, baud rate, flow control, IRQ, and response state. `cros_ec_uart_rx_bytes()` is the serdev receive callback. `cros_ec_uart_pkt_xfer()` is the `ec_dev->pkt_xfer` implementation. `cros_ec_uart_acpi_probe()` extracts UART serial-bus settings and a GPIO IRQ from ACPI resources. Probe allocates `cros_ec_device`, installs serdev callbacks, opens the UART, applies baud/flow settings, and calls `cros_ec_register()`.

## Control Flow

Probe initializes response synchronization, reads ACPI transport details, binds the Chrome EC device to the serdev, and registers it with the common Chrome EC stack. During command transfer, `cros_ec_prepare_tx()` formats `ec_dev->dout`; the UART driver writes it with `serdev_device_write_buf()` and waits up to `EC_MSG_DEADLINE_MS`. Receive callbacks append bytes into `ec_dev->din`, learn the expected packet length from `struct ec_host_response`, and wake the waiter once header plus payload has arrived. The transfer path then checks EC result, input size, checksum, copies payload into `ec_msg->data`, and handles reboot delay for `EC_CMD_REBOOT_EC`.

## State And Persistence

Runtime state is per-device and volatile: the response buffer pointer is set only while a command is outstanding and cleared afterward to drop out-of-band bytes. The wait queue coordinates the transfer thread with receive callbacks. Persistent state is in the EC firmware and UART hardware, not in this driver. PM state is delegated to `cros_ec_suspend()` and `cros_ec_resume()`.

## Dependencies And Integration Points

The driver depends on serdev, ACPI serial-bus resources, optional OF compatible `google,cros-ec-uart`, Chrome EC protocol helpers, and the common `cros_ec_register()` device model. It publishes ACPI ID `GOOG0019` and an OF match table.

## Risks

Only one outstanding command is represented by `response_info`; concurrent transfers would corrupt shared response state if the common EC layer did not serialize access. The expected length is trusted from the EC response header before checksum validation, so oversize protection depends on `din_size`. ACPI probing is unconditional in probe, so OF-only systems without ACPI resources may fail despite an OF match. Short UART writes become `-EIO`, and fragmented responses rely on the fixed 500 ms deadline.

## Test Signals

Useful tests include probe with `GOOG0019`, correct baud/flow-control selection, IRQ delivery to the Chrome EC core, successful EC command exchange, checksum failure injection, oversize response handling, fragmented receive callbacks, reboot command timing, and suspend/resume over a UART-connected EC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_vbc.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_vbc.c

## Purpose

This platform driver exposes the Chrome EC verified-boot NVRAM context to userspace through a binary sysfs attribute under the Chrome EC class device. It is a small bridge from sysfs reads/writes to `EC_CMD_VBNV_CONTEXT`.

## Important APIs, Types, And Functions

`vboot_context_read()` sends `EC_VBNV_CONTEXT_OP_READ` and returns the 16-byte `struct ec_response_vbnvcontext` block. `vboot_context_write()` accepts exactly the full context block and sends `EC_VBNV_CONTEXT_OP_WRITE`. `BIN_ATTR_RW(vboot_context, 16)` defines the binary attribute, and `cros_ec_vbc_probe()` creates the `vbc` sysfs group on the parent `struct cros_ec_dev` class device.

## Control Flow

The platform child named `cros-ec-vbc` probes after the Chrome EC MFD/device layer has a `cros_ec_dev` parent. Reads allocate a command buffer sized for the larger request/response payload, send the read operation through `cros_ec_cmd_xfer_status()`, copy the response block, and return its size. Writes validate that the supplied count is the full block size, populate `struct ec_params_vbnvcontext`, and send a no-response write command.

## State And Persistence

The driver keeps no cached vboot state. The persistent data is the EC-managed VBNV context. Every read fetches current EC contents; every write overwrites the entire block. Sysfs group lifetime is tied to platform-device probe/remove.

## Dependencies And Integration Points

It depends on the Chrome EC command ABI, `struct cros_ec_dev` parent data, and sysfs binary attributes. It is selected by the platform device ID `cros-ec-vbc`.

## Risks

The code ignores `pos` and `count` for reads and always returns the whole block, so partial sysfs binary reads rely on sysfs core behavior. Writes require exact full-size input and reject partial updates. Since VBNV affects verified boot, command failures or unintended writes can affect boot policy.

## Test Signals

Validate sysfs group creation/removal, 16-byte read size, exact-size write enforcement, EC command errors, and persistence of a written VBNV block across EC reads or reboot scenarios where firmware preserves VBNV.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_vbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_hps_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_hps_i2c.c

## Purpose

This I2C driver exposes a ChromeOS Human Presence Sensor as `/dev/cros-hps` and controls sensor power with an enable GPIO. It intentionally does not implement data read/write; opening the misc device powers the sensor through runtime PM, and closing it releases power.

## Important APIs, Types, And Functions

`struct hps_drvdata` holds the I2C client, miscdevice, and enable GPIO. `hps_open()` calls `pm_runtime_resume_and_get()`, and `hps_release()` calls `pm_runtime_put()`. `hps_suspend()` and `hps_resume()` drive the GPIO low/high. Probe obtains the `enable` GPIO, registers a misc device, powers the sensor off, and enables runtime PM.

## Control Flow

Firmware leaves HPS powered before Linux probe, so the driver requests the GPIO as output-high to preserve state while binding. After misc registration it powers HPS down and enables runtime PM. An open file descriptor resumes the device and sets the GPIO high; release drops the runtime PM reference. Driver removal disables PM, deregisters the misc device, and restores the default powered-on state.

## State And Persistence

State is volatile and consists of the GPIO output and runtime PM usage count. No sensor configuration or user data is persisted. Removal deliberately powers HPS on to return control to firmware/default behavior.

## Dependencies And Integration Points

The driver depends on I2C enumeration, ACPI ID `GOOG0020`, gpiolib consumer API, miscdevice registration, and runtime PM. It also has an I2C modalias `cros-hps`.

## Risks

There is no per-open serialization beyond runtime PM counting, so multiple opens keep the device powered until the last close. `hps_resume()` always powers on, including system resume paths, so platform expectations must match. Missing or misdescribed `enable` GPIO fails probe.

## Test Signals

Check ACPI/I2C probe, `/dev/cros-hps` creation, GPIO transitions on open/close, runtime PM reference balancing with multiple opens, suspend/resume GPIO behavior, and removal restoring the enable line high.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_hps_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_kbd_led_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_kbd_led_backlight.c

## Purpose

This driver registers a ChromeOS keyboard-backlight LED class device. It supports two transport models: ACPI methods for legacy devices and Chrome EC PWM commands when instantiated as a Chrome EC MFD child.

## Important APIs, Types, And Functions

`struct keyboard_led` wraps `struct led_classdev` plus optional `struct cros_ec_device`. `struct keyboard_led_drvdata` selects init, get, set, blocking-set, and maximum brightness operations. The ACPI backend uses `\_SB.KBLT.KBQC` and `\_SB.KBLT.KBCM`; the EC backend uses `EC_CMD_PWM_GET_KEYBOARD_BACKLIGHT` and `EC_CMD_PWM_SET_KEYBOARD_BACKLIGHT`. `keyboard_led_probe()` chooses backend data and registers `chromeos::kbd_backlight`.

## Control Flow

When the platform device is an MFD cell, probe uses the EC PWM backend and stores the parent Chrome EC pointer. Otherwise it obtains match data from ACPI ID `GOOG0002`. Probe initializes the backend, populates LED callbacks and flags, then registers the LED. ACPI brightness set is nonblocking and calls ACPI directly; EC brightness set is blocking and sends a host command.

## State And Persistence

The driver keeps only the LED classdev and EC pointer. Actual brightness state is stored by ACPI firmware or EC PWM state. The LED core handles suspend/resume because the classdev sets `LED_CORE_SUSPENDRESUME`.

## Dependencies And Integration Points

It integrates with the LED subsystem, ACPI, Chrome EC MFD devices, and Chrome EC PWM commands. The device ID is `cros-keyboard-leds`, with ACPI match data for `GOOG0002`.

## Risks

The EC PWM backend is compiled to an empty drvdata when `CONFIG_MFD_CROS_EC_DEV` is disabled; an MFD-instantiated device would then lack callbacks and useful max brightness. Duplicate LED registration returns `-ENODEV` on `-EEXIST`, assuming another mechanism already bound the same LED. ACPI method paths are hard-coded.

## Test Signals

Test LED registration name, ACPI get/set calls, EC PWM get/set commands, max brightness clamping through LED core, duplicate registration handling, suspend/resume brightness restore, and behavior with/without `CONFIG_MFD_CROS_EC_DEV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_kbd_led_backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.c

## Purpose

This file implements Chrome EC-backed USB Type-C alternate-mode operations for DisplayPort and Thunderbolt. It registers Type-C altmodes, translates Type-C altmode enter/exit/VDM callbacks into Chrome EC Type-C control commands, and asynchronously feeds ACK VDMs back to the Type-C altmode framework.

## Important APIs, Types, And Functions

`struct cros_typec_altmode_data` stores the Type-C altmode, owning port, SVID/mode, AP-driven mode-entry capability, VDM header/data, mutex, and work item. `struct cros_typec_dp_data` extends it with DisplayPort status/configuration state. `cros_typec_altmode_enter()` and `_exit()` issue `EC_CMD_TYPEC_CONTROL` requests. `cros_typec_displayport_vdm()` and `cros_typec_thunderbolt_vdm()` handle incoming structured VDMs. `cros_typec_displayport_status_update()` sends pending DP status ACKs after mux updates. Registration functions create Type-C altmodes and attach `cros_typec_altmode_ops`.

## Control Flow

Altmode VDM callbacks run under a mutex and stage response header/data into private state, then schedule `cros_typec_altmode_work()`. The work item calls `typec_altmode_vdm()` outside the immediate callback flow, then clears the staged packet. Enter/exit first ask the EC to enter or exit the physical mode, then synthesize an ACK VDM toward the altmode framework. DisplayPort status update is delayed until an external DP status path reports the actual mux/configuration state.

## State And Persistence

State is per-altmode and volatile: pending VDM header/data, DP configuration, `configured`, and `pending_status_update`. There is no persistence beyond EC/partner Type-C state. The mutex serializes staged VDM state with work execution.

## Dependencies And Integration Points

The file depends on `cros_ec_typec.h`, Chrome EC `EC_CMD_TYPEC_CONTROL`, the USB Type-C altmode core, DisplayPort altmode support, Thunderbolt altmode support, and USB PD VDO helpers. Build-time stubs in the header preserve basic registration when DP/TBT altmode support is disabled.

## Risks

The work item stores raw pointers to VDO data; for DP status it points into `dp_data`, but future changes must avoid stack-backed VDO pointers. Staging has only one slot, so multiple VDMs before work executes can overwrite pending data. AP-driven mode entry must be correctly advertised, or callbacks return `-EOPNOTSUPP`. Thunderbolt enter-mode handling intentionally does not ACK in this layer.

## Test Signals

Validate DP and TBT altmode registration, EC enter/exit commands, SVDM version downgrades, DP configure and status-update sequencing, mux-driven DP status ACK, concurrent VDM callback behavior, and disabled `CONFIG_TYPEC_DP_ALTMODE` or `CONFIG_TYPEC_TBT_ALTMODE` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.h -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.h

## Purpose

This header declares the Chrome EC Type-C altmode registration helpers and provides build-time fallbacks when DisplayPort or Thunderbolt altmode support is disabled.

## Important APIs, Types, And Functions

It forward-declares `struct cros_typec_port`, `struct typec_altmode`, `struct typec_altmode_desc`, and `struct typec_displayport_data`. With `CONFIG_TYPEC_DP_ALTMODE`, it declares `cros_typec_register_displayport()` and `cros_typec_displayport_status_update()`. Without that config, the registration helper falls back to `typec_port_register_altmode()` and status updates become no-ops. The Thunderbolt section similarly declares or stubs `cros_typec_register_thunderbolt()`.

## Control Flow

Including code calls these helpers without needing local `#ifdef` blocks. The compiled configuration either routes to Chrome EC-specific altmode operations or to plain Type-C altmode registration.

## State And Persistence

The header owns no state. It controls whether per-altmode private state from `cros_typec_altmode.c` exists in the build.

## Dependencies And Integration Points

It depends on `linux/kconfig.h` for `IS_ENABLED()` and `linux/usb/typec.h` for Type-C core declarations. It is consumed by Chrome EC Type-C code that wants optional DP/TBT support.

## Risks

The fallback functions register plain altmodes without Chrome EC VDM/enter/exit handling, so runtime behavior differs substantially in reduced configs. The inline fallback references `port->port`, requiring callers to include a complete `struct cros_typec_port` definition before use.

## Test Signals

Compile with DP/TBT enabled and disabled, ensure callers build in all combinations, and verify reduced configurations still register altmodes without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_altmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_switch.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_switch.c

## Purpose

This platform driver registers Type-C mode-switch and retimer devices whose actual hardware is controlled by the Chrome EC. It translates Type-C mux/retimer set requests into `EC_CMD_TYPEC_CONTROL` mux commands and waits for EC completion events.

## Important APIs, Types, And Functions

`struct cros_typec_port` stores a port number plus registered `typec_mux_dev` and `typec_retimer`. `struct cros_typec_switch_data` stores the parent EC and per-port table. `cros_typec_get_mux_state()` maps Type-C core modes and DP pin assignments to EC USB PD mux flags. `cros_typec_configure_mux()` clears the relevant event, sends `TYPEC_CONTROL_COMMAND_USB_MUX_SET`, and polls `EC_CMD_TYPEC_STATUS` for `PD_STATUS_EVENT_MUX_*_SET_DONE`. Probe walks firmware child nodes and registers mode-switch and/or retimer objects.

## Control Flow

Probe gets the Chrome EC pointer from the parent device and enumerates child fwnodes. Each child `_ADR` selects the EC Type-C port index. Presence of `retimer-switch` registers a retimer with mux index 1; presence of `mode-switch` registers a mode switch with mux index 0. Runtime `set` callbacks call the shared configure helper, which clears stale completion events, sends a new state to the EC, and polls for up to one second.

## State And Persistence

State is per platform device and tracks registered switch objects by EC port number. The mux state itself persists in EC-controlled hardware until changed, disconnect, reset, or power transition. No state is cached after each command completes.

## Dependencies And Integration Points

It depends on ACPI child fwnodes, local address `_ADR`, Chrome EC Type-C host commands, USB Type-C mux and retimer frameworks, and DisplayPort altmode constants. ACPI ID is `GOOG001A`.

## Risks

Polling with sleeps can delay mux operations up to one second. If EC event clearing or status reporting is racy, the driver can time out after a successful physical switch. Only DP altmodes are recognized for modal state mapping; unsupported modes return `-EOPNOTSUPP`. Firmware child-node properties must match Type-C connector graph expectations.

## Test Signals

Exercise child-node discovery, invalid `_ADR`, mode-switch and retimer registration, USB safe/USB/DP pin assignment state mapping, EC mux command failure, event timeout, unplug/replug sequences, and concurrent set callbacks for different ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.c

## Purpose

This file provides Chrome EC USB Power Delivery Vendor Defined Message support for Type-C ports. It fetches pending EC VDM responses/attention messages, forwards them to the matching Type-C altmode, and implements partner altmode operations that send VDM requests through the EC.

## Important APIs, Types, And Functions

`cros_typec_handle_vdm_attention()` repeatedly reads `EC_CMD_TYPEC_VDM_RESPONSE` while attentions remain and calls `typec_altmode_attention()`. `cros_typec_handle_vdm_response()` forwards a fetched VDM to `typec_altmode_vdm()`. `cros_typec_port_amode_enter()` and `cros_typec_port_amode_vdm()` build `TYPEC_CONTROL_COMMAND_SEND_VDM_REQ` payloads. The exported `port_amode_ops` supplies `.enter` and `.vdm` callbacks for port altmodes.

## Control Flow

When the higher-level EC Type-C driver observes VDM-related events, it calls the handler for the affected port. The handler reads the EC response, extracts SVID and object position from the header, finds the registered port altmode with `typec_match_altmode()`, and forwards the event. For AP-originated VDMs, the Type-C core calls `port_amode_ops`, which fills `struct typec_vdm_req` and sends it to the EC.

## State And Persistence

No persistent local state is held. All state lives in the EC pending VDM queue, registered Type-C altmode objects, and partner/port mode state managed elsewhere.

## Dependencies And Integration Points

It depends on `cros_ec_typec.h`, Chrome EC Type-C VDM response/control commands, USB PD VDO helpers, and the Type-C altmode core. The companion header exports the operations and handlers.

## Risks

The attention handler reads `resp.vdm_response[0]` for the header but calls `typec_altmode_attention()` with `resp.vdm_attention[1]`; this relies on the EC response union layout and should be kept aligned with the command ABI. `cros_typec_port_amode_vdm()` sets `vdm_data_objects = cnt` and copies `cnt - 1` payload objects, so callers must pass counts consistent with the header plus payload convention. Unregistered altmodes drop the event.

## Test Signals

Test VDM response forwarding by SVID/OPOS, attention loops with `vdm_attention_left`, EC command errors, unregistered altmode diagnostics, EnterMode request formation, arbitrary VDM payload copying, and SVDM version expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.h -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.h

## Purpose

This header exposes the Chrome EC Type-C VDM helpers to the rest of the Chrome EC Type-C driver.

## Important APIs, Types, And Functions

It declares `extern const struct typec_altmode_ops port_amode_ops`, `cros_typec_handle_vdm_attention()`, and `cros_typec_handle_vdm_response()`. The functions operate on `struct cros_typec_data` and a port number, while the altmode ops are attached to Type-C port altmodes.

## Control Flow

Event-handling code includes this header to dispatch EC VDM events into the VDM implementation. Altmode registration code uses `port_amode_ops` so Type-C core callbacks can send VDMs through the EC.

## State And Persistence

The header has no state. It provides only declarations and include guards.

## Dependencies And Integration Points

It includes `linux/usb/typec_altmode.h` and expects `struct cros_typec_data` to be visible to including translation units through `cros_ec_typec.h` or equivalent local context.

## Risks

There is no forward declaration for `struct cros_typec_data` in the header, so include ordering matters. If used outside the existing Chrome EC Type-C source pattern, compilation may fail.

## Test Signals

Compile all Chrome EC Type-C files that include this header and verify unresolved-symbol coverage when the VDM implementation is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_vdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_logger.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_logger.c

## Purpose

This platform driver periodically drains Chrome EC USB Power Delivery log entries and prints formatted kernel log messages describing charger, fault, DisplayPort, and video-codec events.

## Important APIs, Types, And Functions

`struct logger_data` stores the platform device, parent `cros_ec_dev`, command buffer, delayed work, and ordered workqueue. `ec_get_log_entry()` sends `EC_CMD_PD_GET_LOG_ENTRY`. `cros_usbpd_print_log_entry()` converts `struct ec_response_pd_log` into `PDLOG` text. `cros_usbpd_log_check()` drains up to `CROS_USBPD_MAX_LOG_ENTRIES` and requeues itself every minute. PM callbacks cancel and restart the delayed work.

## Control Flow

Probe allocates logger state, creates an ordered workqueue, initializes autocanceled delayed work, and schedules the first check. Each work run fetches entries until an error, `PD_EVENT_NO_ENTRY`, or a 30-entry cap, computes wall-clock event time from the EC timestamp delta, prints a formatted line, and schedules the next run.

## State And Persistence

The driver keeps only the reusable EC command buffer and delayed-work schedule. EC PD logs are consumed from EC firmware; printed logs persist only in the kernel log. Suspend cancels pending work and resume schedules a new delayed check.

## Dependencies And Integration Points

It depends on Chrome EC dev parent data, Chrome EC PD log command definitions, `rtc_ktime_to_tm()`, ordered workqueues, and platform device ID `cros-usbpd-logger`.

## Risks

Kernel log output may be noisy on active PD systems. The formatting code uses a fixed 80-byte buffer with append lengths accumulated from `vsnprintf()` return values; truncation is tolerated by the bounded buffer but can make messages incomplete. The reusable command buffer assumes only the ordered workqueue accesses it.

## Test Signals

Test probe scheduling, log draining limits, formatting of all known PD event types, no-entry stop behavior, EC command errors, suspend cancellation, resume requeue, and timestamp conversion correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_logger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_notify.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_notify.c

## Purpose

This module is a central notifier source for ChromeOS USB Power Delivery events. It supports both ACPI notify delivery and Chrome EC platform-event delivery, fetches PD host-event status when possible, and broadcasts events through an exported blocking notifier chain.

## Important APIs, Types, And Functions

`cros_usbpd_register_notify()` and `cros_usbpd_unregister_notify()` are exported registration APIs. `struct cros_usbpd_notify_data` stores device, EC pointer, and optional EC notifier block. `cros_usbpd_get_event_and_notify()` sends `EC_CMD_PD_HOST_EVENT_STATUS` and calls the blocking notifier chain. ACPI probe installs an ACPI notify handler for `GOOG0003`; platform probe registers with `ecdev->ec_dev->event_notifier`.

## Control Flow

Module init registers the platform child driver and, under ACPI, a separate ACPI platform driver. ACPI notifies directly call the common fetch-and-broadcast helper. Platform EC notifications filter host events for PD MCU and USB mux bits before fetching PD status and broadcasting it. Removal unregisters the ACPI handler or EC notifier.

## State And Persistence

The notifier chain is static process-wide state. Per-device state holds the EC pointer and notifier block. There is no persistent event cache; events are broadcast when received, and late subscribers see only future events.

## Dependencies And Integration Points

The module integrates with Chrome EC event notifiers, ACPI notifications, Chrome EC PD host-event commands, and external consumers through `linux/platform_data/cros_usbpd_notify.h`. It recognizes ACPI IDs `GOOG0003` and parent `GOOG0004`.

## Risks

Older ACPI device hierarchies may lack an EC pointer; the driver intentionally broadcasts event 0 in that case, which consumers must handle. Probe deferral depends on detecting a `GOOG0004` parent. Blocking notifier callbacks run synchronously and can delay event handling.

## Test Signals

Test ACPI notify registration/removal, platform EC notifier registration/removal, event filtering, PD status command failures, parent EC probe deferral, exported notifier registration, and multiple subscriber behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_usbpd_notify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Kconfig

## Purpose

This Kconfig file defines build options for the Wilco Embedded Controller core and optional debugfs, event, and telemetry interfaces.

## Important APIs, Types, And Functions

The symbols are `WILCO_EC`, `WILCO_EC_DEBUGFS`, `WILCO_EC_EVENTS`, and `WILCO_EC_TELEMETRY`. The core is tristate and depends on X86 or compile testing, ACPI, `CROS_EC_LPC`, `LEDS_CLASS`, and `HAS_IOPORT`. Optional drivers depend on the core.

## Control Flow

Selecting `WILCO_EC` enables the base eSPI/MEC mailbox driver. Enabling optional symbols builds separate modules that bind to platform children or ACPI devices and expose raw debug access, event forwarding, or telemetry.

## State And Persistence

The file contributes no runtime state; it controls which runtime modules can exist.

## Dependencies And Integration Points

It integrates Wilco EC support into the Chrome platform driver menu and expresses required subsystem dependencies for IO ports, ACPI, Chrome EC LPC MEC access, LEDs, debugfs, character devices, and telemetry paths.

## Risks

The core requires `LEDS_CLASS` because keyboard backlight support is built into the base object, so systems wanting only mailbox/sysfs still inherit the LED dependency. Optional debugfs exposes raw EC command access and should not be enabled on production builds.

## Test Signals

Check allmodconfig and minimal configs, dependency pruning when ACPI or HAS_IOPORT is absent, module names in help text, and successful builds for each optional symbol combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Makefile

## Purpose

This Makefile maps Wilco EC Kconfig symbols to kernel objects and groups core source files into the `wilco_ec` module.

## Important APIs, Types, And Functions

`wilco_ec-objs` includes `core.o`, `keyboard_leds.o`, `mailbox.o`, `properties.o`, and `sysfs.o`. Optional modules are `wilco_ec_debugfs.o`, `wilco_ec_events.o`, and `wilco_ec_telem.o`, each built from its corresponding source file.

## Control Flow

Kbuild links the core object when `CONFIG_WILCO_EC` is enabled and links optional modules according to their symbols. Optional modules remain separate so they can be omitted or loaded independently.

## State And Persistence

No runtime state is defined here. It controls which translation units are linked into each module.

## Dependencies And Integration Points

The file integrates with Kbuild and the Kconfig symbols from the same directory. The object split mirrors the platform devices created by `core.c`.

## Risks

Moving a helper between core and optional modules must preserve exported symbols and module dependencies. The built-in keyboard LED helper means LED code is always part of the core module.

## Test Signals

Build each symbol combination and verify resulting module names and unresolved-symbol checks, especially optional modules using `wilco_ec_mailbox()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/core.c

## Purpose

This is the Wilco EC core platform driver. It binds ACPI ID `GOOG000C`, claims IO resources, initializes the MEC mailbox transport, registers core sysfs and keyboard LED support, and creates platform children for RTC, charger, debugfs, and telemetry.

## Important APIs, Types, And Functions

`wilco_get_resource()` requests IO resources from the ACPI platform device. `wilco_ec_probe()` allocates `struct wilco_ec_device`, initializes `mailbox_lock`, allocates the shared data buffer, claims host data/command/MEC IO regions, calls `cros_ec_lpc_mec_init()`, and registers child platform devices. `wilco_ec_remove()` unwinds those children and sysfs.

## Control Flow

Probe requires three IO resources: host data, host command, and MEC EMI. After transport initialization it creates the debugfs child opportunistically, then RTC, keyboard LEDs, sysfs, charger, and telemetry in order. Errors unwind already-created children. Remove unregisters children in reverse logical order and removes sysfs.

## State And Persistence

The core `wilco_ec_device` contains shared mailbox state, a mutex, IO resource pointers, and child platform-device pointers. EC settings manipulated through child drivers persist in EC firmware/hardware according to their command semantics. Kernel state is devm-managed or explicitly unregistered on remove.

## Dependencies And Integration Points

The driver depends on ACPI, platform IO resources, Chrome EC LPC MEC low-level routines, Wilco platform data definitions, the Wilco mailbox module, Wilco sysfs/properties code, LED class support, and optional child drivers.

## Risks

The debugfs child registration failure is ignored, so remove must handle a null or error-like child carefully; the code only unregisters when the pointer is non-null, and `platform_device_register_data()` returns error pointers on failure. Child device ordering is important because optional modules expect parent data and mailbox transport to be ready.

## Test Signals

Test ACPI probe with all three IO resources, resource-request failures, child platform-device creation/unwind, sysfs creation, keyboard LED absence/presence, telemetry child platform data, module unload, and mailbox command use from children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/debugfs.c

## Purpose

This optional module exposes Wilco EC debugfs controls. It provides raw mailbox command access plus convenience nodes for H1 GPIO status and generating a test EC event.

## Important APIs, Types, And Functions

`struct wilco_ec_debugfs` stores the EC pointer, debugfs directory, latest raw response, and formatting buffers. `parse_hex_sentence()` converts space-separated hex tokens to bytes. `raw_write()` parses a two-byte message type plus request bytes and calls `wilco_ec_mailbox()`. `raw_read()` returns the latest response as a hex dump once. `send_ec_cmd()`, `h1_gpio_get()`, and `test_event_set()` implement the simple debug attributes.

## Control Flow

The platform child `wilco-ec-debugfs` probes with the Wilco EC parent data, creates `/sys/kernel/debug/wilco_ec`, and adds `raw`, `h1_gpio`, and `test_event`. A write to `raw` immediately sends the mailbox transaction and stores the response for the next read. Remove recursively deletes the debugfs directory.

## State And Persistence

The module has a single global `debug_info` pointer and stores only the most recent raw response until read. It does not persist data. EC state may be changed by arbitrary raw commands.

## Dependencies And Integration Points

It depends on debugfs, the Wilco mailbox export, and the core-created platform child. The documented ABI is under `debugfs-wilco-ec`.

## Risks

The global `debug_info` means multiple Wilco EC instances would collide. Raw command access is intentionally unsafe and can send arbitrary EC mailbox messages. `raw_write()` and `raw_read()` share buffers without explicit locking, so concurrent debugfs users can race.

## Test Signals

Test debugfs directory creation/removal, valid and invalid hex parsing, short raw command rejection, raw response one-shot reads, H1 GPIO command status, test event generation, and concurrent access behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/event.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/event.c

## Purpose

This optional Wilco EC ACPI event driver exposes EC events to userspace through `/dev/wilco_eventN`. It installs an ACPI notify handler, fetches event buffers via the `QSET` ACPI method, queues parsed events, and supports blocking reads and polling.

## Important APIs, Types, And Functions

`struct ec_event` models variable-length EC events. `struct ec_event_queue` is a bounded circular queue. `struct event_device_data` owns the queue, spinlock, wait queue, cdev, embedded device, existence flag, and single-open guard. `enqueue_events()` validates and copies packed events. `event_device_notify()` handles ACPI Notify `0x90`. `event_open()`, `event_poll()`, `event_read()`, and `event_release()` implement the character device.

## Control Flow

Module init creates a class, allocates a major range, and registers the ACPI platform driver for `GOOG000D`. Probe allocates a minor, creates the cdev/device, and installs the ACPI notify handler. On notify, the driver evaluates `QSET`, validates an ACPI buffer, parses one or more events, pushes them to the circular queue, and wakes readers. Reads return one complete event at a time, blocking unless opened nonblocking. Remove uninstalls ACPI notify, deletes the cdev, frees the minor, marks the device nonexistent, and wakes waiters.

## State And Persistence

Runtime state is per ACPI device. The queue is bounded by module parameter `queue_size` and overwrites oldest events when full. Events are volatile and removed when read or during device teardown. Device lifetime is reference-counted so open files can close safely after remove.

## Dependencies And Integration Points

The file depends on ACPI notifications/method evaluation, cdev/device core, IDA minor allocation, wait queues, spinlocks, and userspace poll/read consumers.

## Risks

The queue capacity parameter is not clamped against zero in the local code; invalid module parameters could stress queue indexing. Event parsing trusts packed EC event size fields after bounds checks. Only one reader may open the device, which is intentional but can surprise diagnostic tools. Dropping oldest events on overflow can hide bursts.

## Test Signals

Test class/major allocation, probe/remove with open readers, ACPI notify values other than `0x90`, malformed `QSET` returns, oversized event word counts, queue overflow behavior, blocking and nonblocking reads, poll wakeups, and single-open enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/keyboard_leds.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/keyboard_leds.c

## Purpose

This file implements the Wilco EC keyboard-backlight LED support used by the core Wilco driver. It detects EC keyboard-backlight capability, initializes PWM brightness mode, and registers a LED class device.

## Important APIs, Types, And Functions

`struct wilco_keyboard_leds` stores the EC pointer and LED classdev. `struct wilco_keyboard_leds_msg` is the packed legacy EC command payload for command `0x75`. `send_kbbl_msg()` sends a Wilco legacy mailbox command. `kbbl_exist()` probes support, `kbbl_init()` reads current state and forces PWM mode if needed, `set_kbbl()` sets brightness, and `wilco_keyboard_leds_init()` registers `platform::kbd_backlight`.

## Control Flow

Core probe calls `wilco_keyboard_leds_init()`. The helper first sends `GET_FEATURES`; status `0xff` means no keyboard LED support and probe continues without an LED. If present, it allocates LED state, initializes brightness from EC state or sets default brightness zero if EC is not in PWM mode, and registers a blocking brightness setter.

## State And Persistence

Kernel state is devm-managed LED classdev data. Brightness and mode live in EC firmware; the driver updates brightness on set and initializes PWM state during probe if needed. LED core handles suspend/resume flag behavior.

## Dependencies And Integration Points

It depends on Wilco mailbox commands, LED class support, and the core Wilco EC device. It is linked into the core `wilco_ec` module.

## Risks

Brightness values are passed as percentages 0-100 and rely on LED core bounds. Support detection treats any status other than `0xff` as present. If BIOS left the EC in a non-PWM mode, probe changes brightness to zero.

## Test Signals

Test feature-present and feature-absent EC responses, PWM-mode initialization, non-PWM fallback to zero, brightness set command failures, LED registration and removal through devm, and suspend/resume LED behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/keyboard_leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/mailbox.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/mailbox.c

## Purpose

This file implements the Wilco EC mailbox transport over the MEC LPC interface. It provides the exported `wilco_ec_mailbox()` API used by Wilco sysfs, debugfs, telemetry, properties, keyboard LED, and other child drivers.

## Important APIs, Types, And Functions

`wilco_ec_response_timed_out()` polls host command flags until the EC is not pending/busy. `wilco_ec_checksum()` computes the 8-bit request checksum. `wilco_ec_prepare()` fills `struct wilco_ec_request`. `wilco_ec_transfer()` writes request header/data to MEC, starts the command with `EC_MAILBOX_START_COMMAND`, waits, validates flag/result/checksum/size, and copies response data. `wilco_ec_mailbox()` locks `ec->mailbox_lock`, prepares the request in the shared buffer, calls transfer, and exports the symbol.

## Control Flow

Callers fill `struct wilco_ec_message` with type, request data, response data, sizes, and optional no-response flag. The mailbox layer serializes the operation, writes request bytes to MEC offsets 0 and header-size, starts the EC command via the command IO port, optionally returns immediately for no-response commands, then reads a full response packet into `ec->data_buffer` and validates it.

## State And Persistence

The shared `ec->data_buffer` and mailbox registers are protected by `mailbox_lock`. There is no persisted kernel state. EC-side settings changed by commands persist according to EC firmware behavior. Timeout is bounded by `HZ`.

## Dependencies And Integration Points

It depends on Wilco platform data structs, `cros_ec_lpc_io_bytes_mec()`, IO port accessors, jiffies, and child drivers using the exported mailbox API.

## Risks

Response validation requires `rs->data_size == EC_MAILBOX_DATA_SIZE`, so protocol variants with shorter valid replies would fail. The checksum validation depends on `cros_ec_lpc_io_bytes_mec()` returning the checksum status convention used here. No-response commands bypass response validation entirely. Polling latency and timeout affect all Wilco EC clients.

## Test Signals

Test serialized concurrent mailbox clients, checksum failure, EC result failure, bad data size, short response, no-response command, busy timeout, IO read/write errors, and representative legacy/property/telemetry callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/mailbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/properties.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/properties.c

## Purpose

This file provides exported helpers for getting and setting Wilco EC properties through the mailbox property command.

## Important APIs, Types, And Functions

`struct ec_property_request` and `struct ec_property_response` encode operation, little-endian property ID, length, and data. `send_property_msg()` wraps a `WILCO_EC_MSG_PROPERTY` mailbox transaction and validates echoed operation and property ID. Exported helpers are `wilco_ec_get_property()`, `wilco_ec_set_property()`, `wilco_ec_get_byte_property()`, and `wilco_ec_set_byte_property()`.

## Control Flow

Get requests set operation `EC_OP_GET` and a property ID, then copy response length/data into the caller message. Set requests include length/data and require the response length to match. Byte helpers enforce one-byte property values.

## State And Persistence

The file keeps no local state. Property values live in the EC and may persist depending on firmware. Request and response buffers are stack local.

## Dependencies And Integration Points

It depends on the Wilco mailbox export, Wilco platform data property limits, unaligned little-endian helpers, and external Wilco feature drivers that use property APIs.

## Risks

There is no explicit bounds check on `rs.length` before copying into `prop_msg->data`; safety depends on EC protocol and `WILCO_EC_PROPERTY_MAX_SIZE`. Set copies `prop_msg->length` bytes into the fixed request data buffer, so callers must respect the maximum.

## Test Signals

Test valid get/set, mismatched echoed operation, mismatched property ID, byte helper length validation, maximum-size properties, EC errors, and caller-side length bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/properties.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/sysfs.c

## Purpose

This file exposes Wilco EC platform settings and information through sysfs attributes on the core Wilco EC device.

## Important APIs, Types, And Functions

Attributes include write-only `boot_on_ac`, read-only `version`, `build_revision`, `build_date`, `model_number`, and read/write `usb_charge`. `get_info()` sends command `0x38` for EC strings. `boot_on_ac_store()` sends legacy CMOS auto-on command `0x7c/0x03`. `send_usb_charge()`, `usb_charge_show()`, and `usb_charge_store()` implement command `0x39`. `wilco_ec_add_sysfs()` and `wilco_ec_remove_sysfs()` manage the group.

## Control Flow

Core probe calls `wilco_ec_add_sysfs()`. Show/store methods parse or format values, build packed legacy request/response structs, and call `wilco_ec_mailbox()`. Stores accept boolean-like numeric values 0 or 1. Remove deletes the attribute group.

## State And Persistence

No values are cached. Reads fetch current EC data; writes update EC-controlled behavior. `boot_on_ac` and USB charge settings may persist in EC/firmware storage depending on platform implementation.

## Dependencies And Integration Points

It depends on the Wilco mailbox API, sysfs, and the documented Wilco EC ABI. It is linked into the core module.

## Risks

EC info strings may be non-NUL-terminated and are printed with a fixed width, which is correct but can include padding. Store methods accept only decimal 0/1. Any EC status byte for USB charge is collapsed to `-EIO`.

## Test Signals

Test sysfs group presence, each info attribute, valid and invalid store values, EC command failure paths, USB charge status failure, and teardown after open sysfs files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/telemetry.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/telemetry.c

## Purpose

This optional module exposes a constrained Wilco EC telemetry character device `/dev/wilco_telemN`. Userspace writes an allowlisted telemetry request and then reads the raw EC response from the same open file.

## Important APIs, Types, And Functions

`struct wilco_ec_telem_request` describes command and arguments. `check_telem_request()` allowlists command codes and validates argument size and reserved fields. `struct telem_device_data` owns the cdev/device and EC pointer. `struct telem_session_data` stores one open-file request/response and `has_msg`. `telem_open()`, `telem_write()`, `telem_read()`, and `telem_release()` implement the device semantics.

## Control Flow

Module init registers the class, major range, and platform driver. Probe allocates a minor and cdev for a core-created `wilco_telem` platform child. Only one process can open the device. A write copies and validates the request, sends a `WILCO_EC_MSG_TELEMETRY` mailbox command, stores a full 32-byte response, and marks it readable. A read copies a caller-selected byte count up to the response size and clears `has_msg`.

## State And Persistence

Device state is per minor; session state is per open file. Telemetry responses are volatile and overwritten by the next write in the same session. No EC telemetry is persisted by the driver.

## Dependencies And Integration Points

It depends on cdev/device core, IDA minor allocation, userspace copy helpers, Wilco mailbox, and the core platform child that passes `struct wilco_ec_device` as platform data.

## Risks

Only one opener is allowed, so long-lived clients can block diagnostics. `telem_read()` rejects counts greater than response size and returns exactly the requested count, not necessarily the whole response. The allowlist must stay aligned with EC firmware to avoid rejecting useful safe requests or permitting unsafe ones.

## Test Signals

Test class/major setup, single-open enforcement, all allowlisted commands, invalid reserved byte, oversized writes, PPID `always1` validation, mailbox short response rejection, read-before-write, partial reads, and device removal with open sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/wilco_ec/telemetry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/Kconfig

## Purpose

This Kconfig file defines platform support for CZ.NIC Turris hardware, primarily the Turris Omnia MCU multi-function driver and the supporting Turris signing key type.

## Important APIs, Types, And Functions

`CZNIC_PLATFORMS` gates the menu. `TURRIS_OMNIA_MCU` enables the I2C MCU core. Optional bool features are GPIO/IRQ, system-off wakeup, watchdog, TRNG, and keyctl signing. `TURRIS_SIGNING_KEY` is a tristate helper selected by keyctl support.

## Control Flow

When the platform menu and MCU core are enabled, the subordinate feature options select additional source files into the same MCU module. Several options default to yes so supported hardware exposes all MCU features by default.

## State And Persistence

The file has no runtime state. It determines which portions of `struct omnia_mcu` and which registration functions are compiled.

## Dependencies And Integration Points

Dependencies express Armada/Turris platform scope, I2C, OF GPIO IRQ chips, RTC class, watchdog core, hw_random, keyrings, and asymmetric key support.

## Risks

Feature options are bools under a tristate core, so optional code is compiled into the MCU module rather than separate modules. TRNG depends on GPIO because it requests an MCU interrupt through the GPIO/IRQ layer. Keyctl selects the signing-key helper, adding key subsystem exposure.

## Test Signals

Build with each feature disabled/enabled, compile-test non-Armada configs, dependency resolution for HW_RANDOM and KEYS, and module link coverage for feature-specific inline stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/Makefile

## Purpose

This Makefile links the Turris Omnia MCU core and optional feature objects, plus the Turris signing key helper.

## Important APIs, Types, And Functions

`turris-omnia-mcu-y` starts with `turris-omnia-mcu-base.o`. Conditional object additions include GPIO, keyctl, sys-off/wakeup, TRNG, and watchdog files. `obj-$(CONFIG_TURRIS_SIGNING_KEY)` builds `turris-signing-key.o`.

## Control Flow

Kbuild includes optional MCU objects into the same `turris-omnia-mcu` module based on bool feature symbols. The signing key helper is a separate module/object governed by its tristate.

## State And Persistence

No runtime state exists here; it controls link composition and symbol availability.

## Dependencies And Integration Points

It integrates with the Kconfig symbols from the same directory and with exported helper functions declared in `turris-omnia-mcu.h`.

## Risks

Optional source files assume the corresponding `struct omnia_mcu` fields are compiled in. Link failures would indicate mismatched Kconfig guards or missing inline stubs.

## Test Signals

Run builds for core-only, all features, and individual feature toggles; check module dependencies for `turris-signing-key` when keyctl is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-base.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-base.c

## Purpose

This is the core I2C driver for the CZ.NIC Turris Omnia MCU. It provides shared I2C command helpers, reads firmware features and board identity, exposes base sysfs attributes, and registers optional MCU subfeatures.

## Important APIs, Types, And Functions

`omnia_cmd_write_read()` is the exported raw I2C transaction helper. `omnia_get_version_hash()` reads application or bootloader firmware hashes. Sysfs show functions expose firmware hashes, feature bitmap, MCU type, reset selector, serial number, first MAC, and board revision. `omnia_mcu_read_features()` reads status/features, determines MCU type, logs missing features, and handles 16-bit vs 32-bit feature responses. `omnia_mcu_read_board_info()` reads serial/MAC/revision. `omnia_mcu_probe()` initializes `struct omnia_mcu` and calls optional registration helpers.

## Control Flow

Probe requires an IRQ, allocates MCU state, reads features, optionally reads board info, then registers sys-off/wakeup, watchdog, GPIO chip, keyctl signing, and TRNG in sequence. The device's `dev_groups` include base attributes and optional feature groups, with visibility controlled by feature bits.

## State And Persistence

Persistent hardware information is cached in `mcu->features`, `mcu->type`, serial number, first MAC, and board revision. Firmware state remains in the MCU. Sysfs reads either cached identity data or live command responses.

## Dependencies And Integration Points

It depends on I2C, OF compatible `cznic,turris-omnia-mcu`, the public MCU command interface header, optional feature files, and sysfs device groups.

## Risks

Feature detection has compatibility logic for old firmware; mistakes can hide or expose unsupported features. Probe aborts on optional registration failure once a feature reports present. Board-info visibility depends on the feature bit, and board info read failures fail probe. I2C partial transfers return `-EIO`.

## Test Signals

Test probe with missing IRQ, old firmware without feature command, 16-bit and 32-bit feature reads, bootloader firmware warning, board info parsing, sysfs visibility, optional feature registration failures, and I2C error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-gpio.c

## Purpose

This file implements the Turris Omnia MCU GPIO and nested IRQ controller. It exposes status/control bits as 64 GPIOs, maps MCU interrupt bits to GPIO IRQs, supports old and new MCU interrupt APIs, and adds a `front_button_mode` sysfs attribute.

## Important APIs, Types, And Functions

`struct omnia_gpio` describes command, control command, status bit, control bit, interrupt bit, and feature requirements. `omnia_gpios[]` and `omnia_int_to_gpio_idx[]` are the central hardware maps. GPIO callbacks implement request, direction, get, get-multiple, set, set-multiple, valid masks, and OF translation. IRQ callbacks maintain `mask`, `rising`, `falling`, `both`, cached values, and hardware masks. `omnia_irq_read_pending_new()` reads `OMNIA_CMD_GET_INT_AND_CLEAR`; `omnia_irq_read_pending_old()` derives edges from status-word deltas. `omnia_mcu_register_gpiochip()` registers the gpiochip and requests the parent MCU IRQ.

## Control Flow

Registration initializes the mutex, gpiochip methods, IRQ chip data, valid-mask callbacks, and optional old-firmware status cache/work item. Runtime GPIO reads group I2C status commands where possible. GPIO writes send general or extended control commands. IRQ mask/type updates alter software bitmaps and, with new firmware, synchronize interleaved rising/falling masks to the MCU. The threaded parent IRQ reads pending bits, maps them through the gpiochip IRQ domain, and calls `handle_nested_irq()`.

## State And Persistence

The MCU state includes GPIO control bits and interrupt masks in firmware. Kernel state caches IRQ masks, edge configuration, both-edge cached values, old-firmware last status, and front-button release emulation state. `front_button_mode` changes MCU control state.

## Dependencies And Integration Points

It depends on gpiolib, gpiolib IRQCHIP, OF GPIO translation with three cells, I2C command helpers, feature bits from the MCU interface header, workqueues, and optional consumers such as TRNG and keyctl using `omnia_mcu_request_irq()`.

## Risks

Hardware maps are dense and feature-dependent; wrong bit mappings affect power rails, reset lines, LEDs, and interrupts. `front_button_mode_store()` calls the locked control helper without taking the mutex, relying on helper naming rather than lock enforcement. Old firmware emulates button release and ignores stuck overcurrent bits, so behavior differs by feature bit. `omnia_mcu_request_irq()` uses the first set bit in `spec`; multi-bit specs would select only one interrupt.

## Test Signals

Test GPIO valid masks by feature bitmap, OF translation banks, input/output direction, PHY SFP auto/manual direction, get/set multiple, new interrupt mask programming, old firmware edge derivation, button release emulation, nested IRQ delivery for TRNG/signing/front button, and sysfs front-button mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-keyctl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-keyctl.c

## Purpose

This optional MCU feature exposes the Turris Omnia board private signing key through the kernel keyctl asymmetric signing interface, while keeping private key operations inside the MCU.

## Important APIs, Types, And Functions

`omnia_msg_signed_irq_handler()` collects a completed signature from the MCU. `omnia_mcu_sign()` sends a SHA-256 digest to `OMNIA_CMD_CRYPTO_SIGN_MESSAGE`, waits for the message-signed completion, and copies the signature. `omnia_mcu_get_public_key()` returns the cached board public key. `omnia_signing_key_subtype` describes key size, digest size, signature size, hash algorithm, and callbacks. `omnia_mcu_register_keyctl()` reads the public key, initializes synchronization, requests the message-signed IRQ, and creates a Turris signing key.

## Control Flow

Registration is skipped unless `OMNIA_FEAT_CRYPTO` is present. A keyctl sign request enters `omnia_mcu_sign()`, takes `sign_lock`, rejects concurrent signing, sends the digest command, marks a request pending, and waits. The nested IRQ handler reads the signature response, stores result/error, clears pending state, and completes the waiter. The signer copies the signature out and clears the stored signature buffer.

## State And Persistence

The public key is cached in `mcu->board_public_key`. Signing state includes a completion, lock, pending flag, error code, and temporary signature buffer. The private key remains persistent inside the MCU and is never exposed to the kernel.

## Dependencies And Integration Points

It depends on the Turris signing key helper, Linux keyrings/asymmetric key operations, SHA-256 constants, the MCU GPIO IRQ helper, and crypto feature bits.

## Risks

Only one signing request can be active; concurrent callers get `-EBUSY`. If the IRQ is lost, sign waits indefinitely unless interrupted. The API signs exactly `SHA256_DIGEST_SIZE` bytes and assumes callers selected compatible raw/sha256 parameters. Signature data is explicitly cleared only after successful copy.

## Test Signals

Test feature absence, public-key read length validation, key creation, valid keyctl sign/query/read, concurrent sign rejection, interrupt completion, MCU error propagation, interruptible wait, and signature buffer clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-keyctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-sys-off-wakeup.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-sys-off-wakeup.c

## Purpose

This optional feature registers Turris Omnia MCU restart, true poweroff, and wake-from-poweroff support. It exposes the wakeup feature as an RTC alarm even though the MCU provides uptime-relative wake scheduling rather than a real wall clock.

## Important APIs, Types, And Functions

`omnia_get_uptime_wakeup()` reads current MCU uptime and wakeup time. RTC ops implement `read_time`, `read_alarm`, `set_alarm`, and `alarm_irq_enable`. `omnia_power_off()` sends the poweroff command with magic, optional front-button wake flag, and big-endian CRC32. `omnia_restart()` sends light or hard reset control bits. `front_button_poweron` sysfs controls whether front-button power-on is requested. `omnia_mcu_register_sys_off_and_wakeup()` registers sys-off handlers and the RTC device.

## Control Flow

Registration always installs a restart handler. If `OMNIA_FEAT_POWEROFF_WAKEUP` is absent, it stops there. Otherwise it installs a poweroff handler, allocates/registers an RTC wakeup-only device, and defaults front-button power-on to true. RTC alarm operations translate between `rtc_time` and MCU seconds since reset.

## State And Persistence

Kernel state stores the last requested `rtc_alarm` and `front_button_poweron` flag. The MCU stores wakeup scheduling and performs reset/poweroff actions. The RTC time base is not persistent wall time; it is MCU uptime.

## Dependencies And Integration Points

It depends on sys-off handlers, reboot mode, RTC class, CRC32, I2C MCU commands, sysfs visibility, and feature bits.

## Risks

Users may mistake the RTC for a real clock; it is wakeup-only and uptime-relative. `front_button_poweron` is mutable kernel state and not persisted unless userspace reapplies it. Poweroff CRC byte order is intentionally unusual and must match MCU firmware. Restart returns `NOTIFY_DONE` after sending reset and delaying 1 ms.

## Test Signals

Test restart handler for normal and hard reboot modes, poweroff command bytes/CRC, RTC read/set/alarm-enable, feature-gated sysfs visibility, front-button power-on toggling, and behavior across MCU reset or driver reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-sys-off-wakeup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-trng.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-trng.c

## Purpose

This optional feature registers the Turris Omnia MCU true random number generator with the Linux hwrng framework.

## Important APIs, Types, And Functions

`omnia_trng_irq_handler()` completes `trng_entropy_ready`. `omnia_trng_read()` waits for entropy if requested, reads `OMNIA_CMD_TRNG_COLLECT_ENTROPY`, bounds the returned byte count to caller size and the 64-byte command maximum, and copies entropy. `omnia_mcu_register_trng()` clears any stale entropy condition, requests the TRNG IRQ via the GPIO IRQ helper, and registers `mcu->trng`.

## Control Flow

Registration is skipped unless `OMNIA_FEAT_TRNG` is present. Before requesting the IRQ, it performs a one-byte collect command to ensure future IRQ generation. Reads either return 0 immediately when nonblocking and no completion is available or wait for the completion, collect entropy, and retry if blocking reads return zero bytes.

## State And Persistence

The only kernel state is the hwrng object and completion. Entropy is produced by the MCU and not cached beyond one read buffer.

## Dependencies And Integration Points

It depends on the MCU GPIO interrupt layer, hwrng framework, I2C command helpers, and TRNG feature bit.

## Risks

The completion is not reinitialized before every read; completion semantics must match the MCU interrupt/collect behavior. Lost interrupts can block waiting readers. Nonblocking reads return 0 rather than an error when entropy is unavailable, as hwrng expects.

## Test Signals

Test feature absence, stale entropy clearing, IRQ completion, blocking and nonblocking reads, zero-byte retry, maximum 64-byte reads, I2C errors, and hwrng registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-watchdog.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-watchdog.c

## Purpose

This optional feature exposes the Turris Omnia MCU watchdog through the Linux watchdog subsystem.

## Important APIs, Types, And Functions

Module parameters `timeout` and `nowayout` configure default timeout and stop behavior. Watchdog ops start, stop, ping, set timeout, and get time left through MCU commands. `omnia_mcu_register_watchdog()` initializes `struct watchdog_device`, applies timeout, reads current hardware running state, sets nowayout and stop-on-reboot policy, and registers the device.

## Control Flow

Registration is skipped unless the MCU advertises `OMNIA_FEAT_WDT_PING`. The driver sets a default 120-second timeout, lets watchdog core apply a module-parameter override, writes the timeout to the MCU in deciseconds, checks if hardware is already running, and registers with devm.

## State And Persistence

Kernel state is the watchdog device struct. The actual watchdog timer, running state, timeout, and countdown live in the MCU and can persist across driver binding if hardware was already running.

## Dependencies And Integration Points

It depends on watchdog core, module parameters, MCU I2C command helpers, and watchdog feature bits.

## Risks

`omnia_wdt_set_timeout()` writes `timeout * DECI`, so max timeout is constrained to `65535 / DECI`. Registration writes the timeout before checking running state. If command errors occur during get-timeleft, the watchdog core sees zero.

## Test Signals

Test start/stop/ping, timeout set bounds, module timeout override, nowayout behavior, already-running hardware detection, stop-on-reboot, command error propagation, and get-timeleft conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu-watchdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu.h -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu.h

## Purpose

This internal header defines the shared Turris Omnia MCU driver state, feature-specific fields, constants for MCU cryptographic sizes, and optional feature registration prototypes or stubs.

## Important APIs, Types, And Functions

`struct omnia_mcu` is the central state object. It always contains the I2C client, MCU type, feature bitmap, board serial/MAC/revision, and conditionally contains GPIO/IRQ state, RTC wake state, watchdog, hwrng, TRNG completion, signing completion/lock/signature/public key, and related fields. It declares `omnia_mcu_register_gpiochip()`, `omnia_mcu_request_irq()`, `omnia_mcu_register_keyctl()`, `omnia_mcu_register_sys_off_and_wakeup()`, `omnia_mcu_register_trng()`, and `omnia_mcu_register_watchdog()` or no-op inline stubs.

## Control Flow

`turris-omnia-mcu-base.c` includes this header and can call every registration helper regardless of feature configuration. Kconfig guards decide whether calls link to real implementations or return success from inline stubs.

## State And Persistence

The header defines the layout of all per-device runtime state. Persistent hardware data is cached in identity fields, while feature state fields mirror kernel-side state for GPIO, RTC, watchdog, RNG, and signing operations.

## Dependencies And Integration Points

It includes completion, gpio, hwrng, Ethernet address, interrupt, mutex, watchdog, and workqueue headers. It is private to the CZ.NIC platform driver directory.

## Risks

Conditional fields must remain aligned with conditional source files; using a field without the matching `CONFIG_` guard breaks builds. Inline stubs make absent features silently successful, so the core must rely on feature files to enforce real registration.

## Test Signals

Compile all feature combinations, inspect `struct omnia_mcu` field availability, and verify no optional source references fields outside their Kconfig guards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-omnia-mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-signing-key.c -->
# sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-signing-key.c

## Purpose

This helper module implements a kernel key type for Turris device signing keys and creates a global built-in keyring `.turris-signing-keys`. Device drivers register keys whose signing operation is delegated to device-specific callbacks.

## Important APIs, Types, And Functions

`turris_signing_key_type` defines instantiate, describe, read, asymmetric query, and asymmetric EDS operation callbacks. `turris_signing_key_asym_valid_params()` enforces raw encoding and the subtype's hash algorithm. `turris_signing_key_asym_query()` reports sign-only capabilities. `turris_signing_key_asym_eds_op()` dispatches sign requests to the subtype. `devm_turris_signing_key_create()` creates a built-in key, stores the device pointer and subtype, and registers devm cleanup.

## Control Flow

Module init registers the key type and allocates the global keyring. A device driver calls `devm_turris_signing_key_create()`, which creates a key in that keyring, associates subtype callbacks under RCU, and arranges unlink/put on device removal. Userspace keyctl operations query/read/sign the key and are routed through the key type callbacks.

## State And Persistence

Global state is the key type and keyring. Per-key state is the key payload's device pointer and subtype pointer. Public keys are read from the device-specific subtype; private keys are not stored here.

## Dependencies And Integration Points

It depends on Linux keyrings, asymmetric key operation hooks, device-managed cleanup, and `linux/turris-signing-key.h`. The Omnia MCU keyctl feature is one consumer.

## Risks

`turris_signing_key_read()` copies `public_key_size` bytes even if it reduces local `buflen`, which makes short user buffers a review hotspot. The key payload stores a raw device pointer, so devm cleanup order must ensure keys are unlinked before device data disappears. The key type supports only signing, not verify/encrypt/decrypt.

## Test Signals

Test module init/exit, keyring allocation failure, key creation/removal, key description, public-key read with full and short buffers, asymmetric query parameter validation, sign op dispatch, unsupported op rejection, and cleanup on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/cznic/turris-signing-key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/goldfish/Kconfig

## Purpose

This Kconfig file defines support for Android Goldfish virtual platform devices and the Goldfish QEMU pipe driver.

## Important APIs, Types, And Functions

`GOLDFISH` is a bool menuconfig depending on `HAS_IOMEM` and `HAS_DMA`, defaulting from `X86_GOLDFISH`. `GOLDFISH_PIPE` is a tristate option under that menu.

## Control Flow

Enabling `GOLDFISH` exposes the pipe option. Enabling `GOLDFISH_PIPE` builds the virtual pipe driver used by Android emulator guests.

## State And Persistence

This file has no runtime state. It controls whether Goldfish platform code is compiled.

## Dependencies And Integration Points

It integrates with architecture Goldfish defaults and the platform driver Makefile.

## Risks

The menu help notes that non-emulator builds generally should not enable these drivers. Missing DMA or IOMEM support correctly hides the menu.

## Test Signals

Check config visibility on Goldfish and non-Goldfish architectures, allmodconfig builds, and disabled behavior when DMA/IOMEM support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/goldfish/Makefile

## Purpose

This Makefile builds the Goldfish QEMU pipe platform driver object when configured.

## Important APIs, Types, And Functions

`obj-$(CONFIG_GOLDFISH_PIPE) += goldfish_pipe.o` is the only build mapping.

## Control Flow

Kbuild links `goldfish_pipe.o` as built-in or module according to `CONFIG_GOLDFISH_PIPE`.

## State And Persistence

There is no runtime state in this file.

## Dependencies And Integration Points

It integrates the Kconfig symbol with the `goldfish_pipe.c` source file.

## Risks

No local risks beyond keeping the object name aligned with the source file and Kconfig symbol.

## Test Signals

Build `CONFIG_GOLDFISH_PIPE=y`, `m`, and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe.c -->
# sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe.c

## Purpose

This driver implements `/dev/goldfish_pipe`, a fast guest-to-QEMU communication channel for Android Goldfish virtual devices. It opens logical host pipes, passes pinned user pages directly to the emulator, and uses MMIO commands plus interrupts for readiness notification.

## Important APIs, Types, And Functions

`struct goldfish_pipe_command` is the per-pipe command page shared with the host. `struct goldfish_pipe` stores pipe ID, flags, command buffer, mutex, wait queue, parent device, and pinned-page scratch array. `struct goldfish_pipe_dev` stores MMIO base, IRQ, miscdevice, pipe table, and shared device buffers. `goldfish_pipe_read_write()` handles read/write loops. `transfer_max_buffers()` pins pages, populates scatter/gather physical addresses, issues `PIPE_CMD_READ` or `PIPE_CMD_WRITE`, and unpins pages. Interrupt handlers read signalled pipe entries and wake blocked operations. Open/close issue host pipe open/close commands.

## Control Flow

Probe maps the MMIO page, exchanges driver/device versions, allocates shared buffers, registers IRQ and miscdevice, and writes buffer physical addresses to host registers. Opening `/dev/goldfish_pipe` allocates a pipe object and command page, reserves a pipe ID under the device spinlock, provides the command page physical address through the open buffer, and issues `PIPE_CMD_OPEN`. Reads and writes pin user pages in batches of up to 336 buffers, send physical buffer lists to the host, advance by consumed bytes, and wait for host wake events on `PIPE_ERROR_AGAIN` unless nonblocking. Interrupt top half copies signalled pipe IDs/flags into a protected list; threaded handler updates pipe flags and wakes wait queues.

## State And Persistence

All state is runtime-only. Per-pipe state exists from open to release. The global pipe table can grow atomically under spinlock. Host pipe state exists in QEMU and is closed on file release or host-side close. There is no disk persistence.

## Dependencies And Integration Points

It depends on platform MMIO/IRQ resources, miscdevice, user-page pinning, DMA-capable physical addressing, OF compatible `google,android-pipe`, ACPI ID `GFSH0003`, and constants shared with QEMU in `goldfish_pipe_qemu.h`.

## Risks

The driver passes guest physical addresses to the host, so page pinning, dirtying, and unpinning correctness are critical. Device removal frees the pipe table and buffers without explicitly closing open pipes, so open-file lifetime assumptions should be tested. The pipe table grows with `GFP_ATOMIC` while interrupts are disabled. Host protocol version mismatch rejects probe only when older than current device version.

## Test Signals

Test probe resources and version exchange, miscdevice creation, open/close host commands, service name write/read, large transfers crossing many pages, nonblocking `EAGAIN`, wait/wake on read/write, host close behavior, poll flags, IRQ batching above 64 signalled pipes, and module unload with active pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe_qemu.h -->
# sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe_qemu.h

## Purpose

This header defines the guest/host ABI constants shared with QEMU's Goldfish pipe implementation.

## Important APIs, Types, And Functions

It defines enums for pipe poll flags, host error statuses, wake flags, close reasons, per-pipe flag bits, MMIO register offsets, and pipe command codes. Key commands include open, close, poll, read, write, and wake-on-read/write. Key registers include command, signal buffer address/count, open buffer address, version, and get-signalled.

## Control Flow

`goldfish_pipe.c` uses these constants to write MMIO registers, interpret host statuses, build commands, and process host wake events.

## State And Persistence

The header owns no state. It specifies values that both guest and host must treat as stable ABI.

## Dependencies And Integration Points

It is tightly coupled to QEMU's `goldfish_pipe.h` constants and the Goldfish pipe driver.

## Risks

Any numeric mismatch with QEMU breaks communication. Some wake flags such as DMA unlock are defined but not handled by this driver, so host behavior must remain compatible.

## Test Signals

Validate ABI values against the emulator source, probe version negotiation, every command code, every poll flag, and host error conversion in the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/goldfish_pipe_qemu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/loongarch/Kconfig

## Purpose

This Kconfig file defines LoongArch platform-specific device-driver options, currently including the generic Loongson laptop/all-in-one ACPI driver.

## Important APIs, Types, And Functions

`LOONGARCH_PLATFORM_DEVICES` gates the menu and defaults to yes on LoongArch. `LOONGSON_LAPTOP` is a tristate depending on `ACPI_EC`, `BACKLIGHT_CLASS_DEVICE`, `INPUT`, and `MACH_LOONGSON64`; it selects `ACPI_VIDEO` and `INPUT_SPARSEKMAP`.

## Control Flow

When enabled, the Loongson laptop driver is built and can register ACPI hotkey, input, and backlight support.

## State And Persistence

The file has no runtime state. It determines whether the Loongson ACPI driver is available.

## Dependencies And Integration Points

It integrates LoongArch platform support with ACPI EC, input sparse keymap, ACPI video, and backlight subsystems.

## Risks

The option defaults to enabled for the platform, so compile/runtime issues affect default Loongson laptop kernels. Dependency selection must avoid exposing the driver without ACPI EC or input support.

## Test Signals

Check Kconfig visibility on LoongArch, dependency pruning, default selection, and module/built-in builds for `LOONGSON_LAPTOP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/loongarch/Makefile

## Purpose

This Makefile links the Loongson laptop ACPI platform driver when configured.

## Important APIs, Types, And Functions

It maps `CONFIG_LOONGSON_LAPTOP` to `loongson-laptop.o`.

## Control Flow

Kbuild includes the object as built-in or module according to Kconfig.

## State And Persistence

No runtime state is defined here.

## Dependencies And Integration Points

The file connects the LoongArch platform Kconfig symbol to `loongson-laptop.c`.

## Risks

No special local risks beyond object-symbol consistency.

## Test Signals

Build with `CONFIG_LOONGSON_LAPTOP=y`, `m`, and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/loongson-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/loongarch/loongson-laptop.c

## Purpose

This ACPI driver supports Loongson laptops and all-in-one systems. It registers a hotkey input device from firmware keymap data, handles ACPI notifications, manages vendor backlight control, and reports lid/switch events.

## Important APIs, Types, And Functions

`struct generic_sub_driver` abstracts ACPI subdrivers. Global state includes `generic_inputdev`, `hotkey_handle`, `hotkey_keycode_map`, and `bl_powered`. `acpi_evalf()` is a local ACPI method helper. Hotkey setup uses `hotkey_map()`, `sparse_keymap_setup()`, and `event_notify()`. Backlight functions call ACPI methods `ECBG`, `ECBS`, `ECLL`, `ECSL`, `VCBL`, and `\BLSW`. `generic_acpi_laptop_init()` is the module entry point.

## Control Flow

Module init requires ACPI and an EC HID `PNP0C09`, enables SCI, allocates an input device, registers the hotkey platform subdriver for `LOON0000`, parses the `KMAP` ACPI package, installs an ACPI notify handler, registers the input device, and optionally registers a platform backlight if brightness methods exist. ACPI notifications are decoded into event type and scan code, looked up in the sparse keymap, and reported. Resume refreshes backlight state and may report lid state if firmware supports `SW_LID`.

## State And Persistence

Most state is global singleton state: the input device, hotkey ACPI handle, keymap, registered flag, and backlight power flag. Firmware owns brightness and hotkey status. No settings are persisted by the driver beyond ACPI method effects.

## Dependencies And Integration Points

It depends on ACPI, ACPI EC, ACPI video backlight policy, input sparse keymap, backlight class, platform driver core, and Loongson-specific ACPI methods/HIDs.

## Risks

`hotkey_map()` does not visibly free the ACPI allocated buffer and does not clamp package count to `GENERIC_HOTKEY_MAP_MAX`, making malformed firmware a risk. `backlight_device_register()` return value is ignored, and no unregister path stores the pointer. The driver uses global singleton state, so multiple matching devices are not supported. ACPI helper format handling is minimal.

## Test Signals

Test systems with and without `PNP0C09`/`LOON0000`, valid and oversized `KMAP`, hotkey and lid notifications, vendor vs non-vendor backlight policy, brightness get/set bounds, suspend/resume lid/backlight handling, module unload, and ACPI method failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/loongson-laptop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/mellanox/Kconfig

## Purpose

This Kconfig file defines platform support options for Mellanox/Nvidia systems, switches, line cards, BlueField SoCs, and the Nvidia SN2201 platform.

## Important APIs, Types, And Functions

`MELLANOX_PLATFORM` gates the menu for X86, ARM, ARM64, or compile testing. Feature symbols include `MLX_PLATFORM`, `MLXREG_DPU`, `MLXREG_HOTPLUG`, `MLXREG_IO`, `MLXREG_LC`, `MLXBF_TMFIFO`, `MLXBF_BOOTCTL`, `MLXBF_PMC`, and `NVSW_SN2201`. Dependencies select or require ACPI, I2C, PCI, HWMON, REGMAP, REGMAP_I2C, ARM64, NET, and virtio console/net.

## Control Flow

Enabling the top-level menu exposes individual platform drivers. Each symbol controls a separate source module under `drivers/platform/mellanox`, ranging from x86 platform support to BlueField firmware/monitoring and switch-management drivers.

## State And Persistence

No runtime state is defined here. The options determine which hardware-management drivers may run.

## Dependencies And Integration Points

It integrates Mellanox platform code with ACPI/I2C/PCI discovery, regmap-backed device register access, hwmon, virtio, networking, and BlueField ARM64 support.

## Risks

Dependencies are hardware-specific; overly broad compile-test exposure can reveal missing stubs, while overly narrow dependencies can hide usable drivers. Some help text refers to Nvidia-rebranded hardware but symbols retain Mellanox naming, so user-facing config clarity matters.

## Test Signals

Check Kconfig visibility across X86/ARM/ARM64/COMPILE_TEST, dependency selections, allmodconfig builds, and each symbol's object linkage in the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/mellanox/Makefile

## Purpose

This Makefile maps Mellanox/Nvidia platform Kconfig symbols to their driver objects.

## Important APIs, Types, And Functions

It builds `mlx-platform.o`, `mlxbf-bootctl.o`, `mlxbf-pmc.o`, `mlxbf-tmfifo.o`, `mlxreg-dpu.o`, `mlxreg-hotplug.o`, `mlxreg-io.o`, `mlxreg-lc.o`, and `nvsw-sn2201.o` according to their corresponding `CONFIG_` symbols.

## Control Flow

Kbuild includes each driver independently as built-in or module. The object list mirrors the Kconfig feature list.

## State And Persistence

The Makefile has no runtime state.

## Dependencies And Integration Points

It integrates the Mellanox platform driver directory with Kbuild and the Kconfig file in the same directory.

## Risks

Object-symbol mismatches would lead to missing drivers or stale builds. Formatting inconsistency on a few lines is cosmetic but worth avoiding in future edits.

## Test Signals

Build every Mellanox platform symbol as built-in and module, and verify each expected object is linked with no unresolved dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mellanox/Makefile -->
