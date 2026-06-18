# sources/distributed-fs/ceph-client/drivers/hid/amd-sfh-hid/sfh1_1/amd_sfh_init.c

## Purpose

`sfh1_1/amd_sfh_init.c` initializes AMD SFH 1.1 devices. It maps the firmware sensor memory window, discovers sensors from `sfh_base_info`, starts and stops sensors, registers HID devices, manages suspend/resume, toggles HPD, and removes the SFH 1.1 instance.

## Important APIs, Types, and Functions

`amd_sfh1_1_init()` is the public init entry. `amd_sfh1_1_hid_client_init()` mirrors the legacy client initialization but uses SFH 1.1 discovery and command semantics. `amd_sfh_hid_client_deinit()` tears down sensors and HID devices. `amd_sfh_resume()`, `amd_sfh_suspend()`, and `amd_sfh_toggle_hpd()` implement power and HPD policy. `amd_sfh_set_ops()` installs interface, interrupt, PM, and remove callbacks.

## Control Flow

Initialization reads the physical base from a C2P register, maps 128 KiB of SFH firmware memory, waits five seconds for firmware configuration, validates firmware version and sensor list, installs ops, initializes interrupts, and starts HID client setup. The client discovers sensors from the firmware sensor bitmask, handles SRA as a platform-info-only sensor, creates HID devices for enabled non-SRA sensors, marks HPD/ALS/SRA availability, and schedules periodic input work.

## State and Persistence Behavior

State persists in `amd_mp2_dev`, `sfh_dev_status`, `amdtp_cl_data`, and the global interface pointer cleared by `sfh_deinit_emp2()`. HPD enabled state is persistent until toggled by sysfs/policy, and suspend/resume intentionally leaves HPD alone.

## Dependencies and Integration Points

It depends on HID core, delays, PCI-managed memory mapping, the SFH 1.1 interface layer, descriptor callbacks, and generic AMD SFH HID helpers. It integrates with `amd_sfh_pcie.c` through `sfh1_1_ops`.

## Risks and Test Signals

Risks include the fixed five-second firmware wait, physical base calculation by shifting register contents, SRA not producing a HID device, and HPD policy interactions during suspend. Test signals include SFH 1.1 probe on supported hardware, `amd_get_sfh_info()` success for SRA/ALS/HPD, sysfs HPD toggling, suspend/resume preserving HPD policy, and cleanup after partial init failures.
