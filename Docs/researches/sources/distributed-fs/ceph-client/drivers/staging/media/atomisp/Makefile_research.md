# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/Makefile

## Purpose
Defines the large AtomISP staging build. It builds the I2C sensor directory, the main `atomisp.o` object, platform glue, a long list of CSS/ISP runtime/kernel objects, include paths, and host-side defines.

## Important Entries and Integration
`obj-$(CONFIG_INTEL_ATOMISP) += i2c/` builds sensor modules under the AtomISP platform symbol. `obj-$(CONFIG_VIDEO_ATOMISP) += atomisp.o` and `pci/atomisp_gmin_platform.o` build the ISP driver and ACPI/GMIN platform glue. `atomisp-objs` aggregates V4L2, HMM, MMU, CSS host, runtime, ISP kernel, and system-local objects. `INCLUDES` points throughout the staging atomisp tree, and `ccflags-y` adds includes and defines such as `HRT_HW`, `HRT_ISP_CSS_CUSTOM_HOST`, `HRT_USE_VIR_ADDRS`, and `__HOST__`.

## Control Flow and State
This Makefile does not contain runtime state but heavily shapes compile-time integration. Debug is enabled while in staging, and a duplicate object/include entries are present in the list.

## Risks and Test Signals
Risks include brittle include-path sprawl, duplicate object entries, platform-specific defines, and high build fragility under compiler flag changes. Test signals are successful `CONFIG_VIDEO_ATOMISP` builds, no duplicate-symbol issues from repeated object entries, and sensor subdirectory compilation with `CONFIG_INTEL_ATOMISP`.
