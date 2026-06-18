<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/northstar2/Makefile -->
## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/northstar2/Makefile

### Purpose
This Makefile registers Broadcom Northstar2 iProc DTBs.

### Important APIs, Types, And Functions
It exports `ns2-svk.dtb` and `ns2-xmc.dtb` through `dtb-$(CONFIG_ARCH_BCM_IPROC)`.

### Control Flow
Kbuild builds both Northstar2 DTBs when the iProc architecture option is enabled and the parent Broadcom Makefile recurses into this directory.

### State, Persistence, And Dependencies
Generated DTBs are the only persistent outputs. Dependencies include matching DTS files, DTC, parent `subdir-y`, and `CONFIG_ARCH_BCM_IPROC`.

### Integration Points
The DTBs support Northstar2 SVK/XMC hardware and integrate with Broadcom iProc platform drivers.

### Risks
Shared `CONFIG_ARCH_BCM_IPROC` also gates Stingray targets, so coverage must include both subfamilies. Missing parent recursion would hide this file entirely.

### Test Signals
Build iProc DTBs and run schema checks for `ns2-svk` and `ns2-xmc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/boot/dts/broadcom/northstar2/Makefile -->
