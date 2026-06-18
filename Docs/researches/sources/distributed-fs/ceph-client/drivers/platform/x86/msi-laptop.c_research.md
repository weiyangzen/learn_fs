<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-laptop.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-laptop.c

## Purpose
This legacy MSI laptop driver supports older MSI S270/S271/S420 and related netbook models. It exposes EC-controlled backlight, wireless device state, rfkill devices, touchpad/turbo/eco status, fan auto mode, and special SCM-load behavior.

## Important APIs, Types, And Functions
`struct quirk_entry` controls old EC model, SCM-load model, EC delay, and read-only behavior. Hardware helpers include `set_lcd_level()`, `get_lcd_level()`, `get_auto_brightness()`, `set_auto_brightness()`, `set_device_state()`, and wireless state readers. Sysfs attributes are grouped under `msi-laptop-pf`. RFKill handlers call `set_device_state()`. `msi_laptop_i8042_filter()` watches keyboard controller scan codes and schedules delayed work for rfkill or touchpad updates. `load_scm_model_init()` disables BIOS Fn-key handling and sets up rfkill/input/filter.

## Control Flow
Module init checks ACPI and DMI, defaults to SCM quirk if no DMI match, and uses `force` to select old EC behavior. Old EC models can register a vendor backlight when ACPI video detection allows. The platform driver/device are registered, sysfs groups are created, and SCM models initialize rfkill/input/i8042 filtering. Cleanup reverses this and restores automatic brightness for old EC models unless disabled by module parameter.

## State And Persistence
Global state tracks selected quirks, wireless booleans, 3G presence, rfkill objects, input device, platform/backlight devices, and delayed works. EC writes change firmware-controlled device state and brightness. SCM-load state is restored on resume by setting the EC bit again.

## Dependencies And Integration Points
Dependencies include ACPI EC transactions, DMI, backlight core, platform devices, rfkill, i8042 filter hooks, input sparse-keymap, ACPI video backlight detection, and delayed workqueues.

## Risks And Edge Cases
The module relies on old EC command semantics and DMI quirks. Installing an i8042 filter can affect keyboard event handling. Read-only models update rfkill hardware state but do not write EC bits. `force` may load on unsupported hardware. Delayed work and global rfkill cleanup require careful ordering.

## Test Signals
Tests should cover DMI quirk selection, old EC backlight get/set, auto-brightness policy, rfkill state changes, read-only behavior, i8042 scan-code-triggered updates, touchpad key reporting, resume SCM-load bit restoration, and cleanup with pending delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-laptop.c -->
