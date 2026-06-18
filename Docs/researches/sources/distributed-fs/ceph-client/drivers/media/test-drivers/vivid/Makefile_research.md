# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vivid/Makefile

## Purpose
`vivid/Makefile` defines the object composition for the VIVID kernel module.

## Important APIs, types, and functions
`vivid-objs` includes core, controls, common video, VBI, capture/output kthreads, radio RX/TX, RDS, SDR, metadata, and touch capture components. It conditionally adds `vivid-cec.o` when `CONFIG_VIDEO_VIVID_CEC=y` and `vivid-osd.o` when `CONFIG_VIDEO_VIVID_OSD=y`. `obj-$(CONFIG_VIDEO_VIVID) += vivid.o` ties the aggregate object to the Kconfig driver symbol.

## Control flow
The Makefile affects build composition only. Runtime control flow is determined by the compiled objects and module parameters in `vivid-core.c`.

## State and persistence
No runtime state is stored here. Build configuration state controls which symbols are linked.

## Dependencies and integration points
It integrates all VIVID source modules into one `vivid` module and mirrors optional Kconfig features.

## Risks and test signals
Risks are missing object entries for newly added source files or conditional objects getting out of sync with Kconfig. Test signals are successful builds with `VIDEO_VIVID=m/y`, with and without CEC/OSD.
