## sources/distributed-fs/ceph-client/arch/arm64/boot/dts/airoha/Makefile

### Purpose
Declares the Airoha ARM64 DTB target.

### Important APIs, Types, And Functions
Adds `en7581-evb.dtb` under `CONFIG_ARCH_AIROHA`.

### Control Flow
Kbuild emits the DTB only when Airoha platform support is selected.

### State, Persistence, And Dependencies
Build metadata only; depends on `en7581-evb.dts` and `ARCH_AIROHA`.

### Integration Points
Adds Airoha evaluation board device tree coverage to ARM64 `dtbs`.

### Risks
Single-target directory means stale naming immediately removes Airoha board output.

### Test Signals
Build Airoha DTBs and run device-tree compiler warning checks.
