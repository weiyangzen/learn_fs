<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.h

## Purpose
`xe_device_sysfs.h` is the small declaration header for device-level sysfs setup. It lets the probe path initialize the sysfs attribute groups without exposing implementation details.

## Important APIs, types, and functions
The file forward-declares `struct xe_device` and declares `int xe_device_sysfs_init(struct xe_device *xe);`.

## Control flow and integration points
There is no executable control flow. The implementation installs devm-managed groups for D3cold threshold, late-binding version, and PCIe auto-link-downgrade attributes. Probe or device initialization code includes this header to invoke the setup once the `xe_device` and capability flags are available.

## State and persistence behavior
The header owns no state. It describes a setup entry point that creates sysfs files whose lifetime follows the underlying PCI device through managed resource cleanup.

## Dependencies, risks, and test signals
The dependency surface is intentionally minimal. Risks are mostly build/API drift if the implementation signature changes or if callers invoke it before runtime PM, PCODE, or capability state is initialized. Test signals are successful driver build, probe-time sysfs registration, and correct cleanup on probe failure and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_device_sysfs.h -->
