<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_hid.h -->
# sources/distributed-fs/ceph-client/include/sound/sdca_hid.h

## Purpose
`sdca_hid.h` exposes the optional bridge from SDCA HIDE entities to the Linux HID subsystem. It lets SDCA functions instantiate HID devices for controls such as buttons and process HID reports received through SDCA interrupts.

## Important APIs, types, and functions
The public entry points are `sdca_add_hid_device()` and `sdca_hid_process_report()`. They operate on `struct device`, `struct sdw_slave`, `struct sdca_entity`, and `struct sdca_interrupt` without exposing implementation internals.

## Control flow
When `CONFIG_SND_SOC_SDCA_HID` is enabled, SDCA function/component code can call `sdca_add_hid_device()` after parsing a HIDE entity, then route interrupt handling to `sdca_hid_process_report()`. When the option is disabled, inline stubs return success and consume reports as no-ops so callers do not need configuration-specific branches.

## State and persistence behavior
The header has no state. Enabled builds create and attach HID runtime objects through implementation code; disabled builds deliberately create no HID state.

## Dependencies and integration points
It forward-declares SDCA, SoundWire, and device types and depends on the SDCA HIDE metadata defined in `sdca_function.h`. It integrates SDCA interrupt processing with HID core registration.

## Risks and test signals
Risks include callers assuming a real HID device exists when the feature is built out, report parsing mismatch with the HIDE report descriptor, and lifetime ordering between SDCA entity cleanup and HID unregister. Test signals include builds with and without `CONFIG_SND_SOC_SDCA_HID`, HIDE entity enumeration, interrupt-driven report delivery, unplug/reset cleanup, and HID userspace visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_hid.h -->
