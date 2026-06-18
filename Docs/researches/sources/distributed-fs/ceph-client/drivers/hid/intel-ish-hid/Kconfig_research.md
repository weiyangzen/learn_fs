<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Kconfig

## Purpose
`Kconfig` exposes configuration for Intel Integrated Sensor Hub HID support and its optional host firmware downloader.

## Important APIs, Types, and Functions
`INTEL_ISH_HID` is a tristate for the ISH HID/ISHTP stack. It is presented under an `Intel ISH HID support` menu that depends on `(X86_64 || COMPILE_TEST) && PCI`; the option itself depends on `X86`. `INTEL_ISH_FIRMWARE_DOWNLOADER` is a tristate that depends on `INTEL_ISH_HID` and `X86`, adding host firmware loading from the filesystem.

## Control Flow
There is no runtime control flow. Configuration selects whether the Makefile builds the ISHTP bus/core, IPC PCI driver, HID client, and optional firmware loader modules/objects.

## State and Persistence Behavior
The file owns build-time state only. User or distribution kernel configuration determines whether the ISH stack is unavailable, built in, or modular.

## Dependencies and Integration Points
The menu ties the ISH driver family to x86 and PCI because ISH is exposed as an Intel PCI function. The firmware downloader cannot be enabled without the base transport and HID support.

## Risks and Edge Cases
The top menu allows `COMPILE_TEST`, but the concrete options still depend on `X86`, limiting cross-architecture build coverage. Enabling the firmware downloader without appropriate firmware files and device properties can produce runtime load failures even though build-time dependencies are satisfied.

## Test Signals
Check all `n`, `m`, and `y` combinations for `INTEL_ISH_HID`; verify the downloader appears only when base support is enabled; and run build coverage for built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/intel-ish-hid/Kconfig -->
