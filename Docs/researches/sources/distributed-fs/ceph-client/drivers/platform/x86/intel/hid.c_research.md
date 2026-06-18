<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/hid.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/hid.c

## Purpose
ACPI platform driver for Intel HID hotkeys, virtual button arrays, power-button wake behavior, and optional tablet-mode switch reporting.

## Important APIs, Types, And Functions
The driver matches several ACPI IDs including `INT33D5` and `INTC10xx`. It uses sparse keymaps for hotkey events and five-button-array events. `intel_hid_execute_method()` and `intel_hid_evaluate_method()` abstract ACPI DSM calls with fallback to named methods. `notify_handler()` routes ACPI notifies to key, button-array, tablet-mode, or wakeup handling. `button_array_present()` checks HEBC capability bits plus DMI/module-param overrides.

## Control Flow
Probe initializes DSM support, requires simple mode from `HDMM`, allocates private state, decides tablet-mode policy from module parameter, DMI allow list, chassis type, and dual-accelerometer detection, registers input devices, installs an ACPI notify handler, enables hotkeys and button array, calls `BTNL` for HID power button support, marks the device wake-capable, and marks the EC GPE for wake. Notify `0xc0` means a HID event index is fetched via `HDEM`; other notify values are button-array or tablet events. Suspend disables button-array and hotkeys unless platform suspend is skipped; wakeup mode filters events so only relevant button events wake the system.

## State And Persistence
`struct intel_hid_priv` holds input devices and a wakeup-mode flag. Global module parameters tune button array and tablet-mode behavior. Firmware event enable state persists through ACPI method calls and is restored on resume.

## Dependencies And Integration Points
Depends on ACPI, DMI, input sparse-keymap, suspend core, EC wake handling, I2C dependency from Kconfig, and local `dual_accel_detect.h`.

## Risks And Test Signals
Risks are firmware-specific event codes, unreliable VGBS tablet state, wake storms, duplicate power button events, and global DSM mask shared across devices. Test hotkeys with `evtest`, five-button array press/release, tablet mode on allow-listed convertibles, suspend-to-idle wake filtering, hibernate freeze/thaw, and unknown event logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/hid.c -->
