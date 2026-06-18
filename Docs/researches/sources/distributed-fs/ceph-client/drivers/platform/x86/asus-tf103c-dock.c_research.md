# sources/distributed-fs/ceph-client/drivers/platform/x86/asus-tf103c-dock.c

## Purpose
`asus-tf103c-dock.c` is an I2C platform driver for the Asus TF103C keyboard dock. The dock has a private embedded controller plus separate I2C addresses for keyboard reports, interrupt status, EC command RAM, and an Elan touchpad, so the driver reconstructs normal Linux HID/input/touchpad behavior from nonstandard firmware protocols.

## Important APIs, Types, And Functions
The central state object is `struct tf103c_dock_data`, which owns the EC, interrupt, keyboard, and touchpad `i2c_client`s, GPIOs, IRQs, a delayed HPD work item, a synthetic HID keyboard, an input device for special top-row keys, touchpad nested IRQ plumbing, and runtime flags such as `enabled`, `tp_enabled`, `altgr_pressed`, and `fnlock` state. Probe binds only on TF103C DMI systems even though the ACPI ID is generic `NPCE69A`.

The keyboard path is split between `tf103c_dock_kbd_read()`, `tf103c_dock_kbd_write()`, a small `hid_ll_driver`, and `tf103c_dock_kbd_interrupt()`. Report ID `0x11` is forwarded as reconstructed keyboard HID, while report IDs `0x13`, `0x14`, and selected SCI events are mapped to top-row keys through `tf103c_dock_toprow_event()`. `tf103c_dock_report_toprow_kbd_hook()` strips Right Alt from normal HID reports and uses it as an Fn modifier; AltGr+Esc toggles the module-global `fnlock`.

The touchpad path creates an `elan_i2c` client dynamically in `tf103c_dock_enable_touchpad()`, using a software node to advertise `elan,clickpad`, and routes EC touchpad interrupts through a single-entry irqdomain using `handle_nested_irq()`. EC command helpers include `tf103c_dock_ec_cmd()`, `tf103c_dock_sci()`, and `tf103c_dock_smi()`.

## Control Flow
`tf103c_dock_probe()` installs GPIO lookups, reads the board revision, requests HPD and dock IRQs with `IRQF_NO_AUTOEN`, creates the extra I2C clients, registers the top-row input device and synthetic HID keyboard, creates a nested IRQ for the touchpad, and starts HPD polling through delayed work. HPD transitions call `tf103c_dock_enable()` or `tf103c_dock_disable()`: enable powers the dock on non-revision-2 boards, waits 500 ms, and enables the main EC IRQ; disable disables the IRQ, unregisters the touchpad, and drops power.

The threaded dock IRQ reads eight bytes from the interrupt client. Out-of-band report markers dispatch to either the nested touchpad IRQ or keyboard report handling. SCI bits trigger top-row multimedia events; SMI bits re-enable the EC/USB/keyboard after EC wake or instantiate the touchpad after HID status changes.

Suspend stops HPD handling and, if the dock is enabled, writes a suspend EC command and optionally enables wake on the dock IRQ. Resume disables wake, conditionally sends an enable command if HPD still says the dock is connected, and restarts HPD synchronization.

## State And Persistence
Most state is runtime-only in `struct tf103c_dock_data`. The exception is the module parameter `fnlock`, which can be set at load time or toggled at runtime through AltGr+Esc and affects top-row key interpretation. Device presence is not persisted; the touchpad client is recreated on dock/HID status changes and unregistered on dock removal or power-off. Board revision influences power GPIO behavior for the lifetime of the probe.

## Dependencies And Integration Points
The driver depends on ACPI/I2C enumeration, DMI matching, GPIO lookup tables for hardcoded Intel/Crystal Cove GPIOs, Linux HID core, input core, irqdomain/nested IRQ support, and the `elan_i2c` touchpad driver. It integrates with system suspend through `SIMPLE_DEV_PM_OPS` and with wakeup through `device_init_wakeup()`.

## Risks
The driver is highly board-specific despite matching a broad ACPI HID, so the DMI guard is essential. Firmware packet formats are inferred and only partially recognized; unknown keyboard or EC interrupt data is logged and ignored. Incorrect HPD, IRQ, or board-revision GPIO mappings can leave the dock powered incorrectly or make the EC unresponsive. The module-global `fnlock` is shared rather than per-device, which is acceptable for the single supported model but would not generalize.

## Test Signals
Useful validation includes TF103C boot/probe logs, HPD plug/unplug cycles, keyboard HID input including six-key boot reports, top-row multimedia/F1-F12 behavior with AltGr and `fnlock`, AltGr+Esc filtering, touchpad creation and nested IRQ delivery to `elan_i2c`, suspend/resume with dock attached and detached, wake from dock IRQ, and regression checks that unknown EC packets do not crash the threaded IRQ.
