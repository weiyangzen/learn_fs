# sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/common.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/common.c -->
## sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/common.c

### Purpose
Common OF platform-device publication for 86xx systems.

### Important APIs, Types, And Functions
Defines `mpc86xx_common_ids[]` with compatibles such as `soc`, `simple-bus`, and `fsl,mpc8641-pcie`. `mpc86xx_common_publish_devices()` calls `of_platform_bus_probe()` with that match table.

### Control Flow
Board machine files call `mpc86xx_common_publish_devices()` from `machine_arch_initcall()` after machine setup. It walks the device tree and creates platform devices for matching buses/controllers.

### State, Persistence, And Dependencies
State is runtime platform-device registration. No durable persistence. Dependencies include OF platform APIs and compatible strings used by 86xx DTS files.

### Integration Points
Shared by GE and MVME 86xx boards to instantiate PCIe/simple-bus children and SoC devices.

### Risks
Changing the match table can hide devices or probe too much of the tree. The function assumes device tree layout follows 86xx conventions.

### Test Signals
Boot 86xx boards and verify platform devices under `soc`, `simple-bus`, and PCIe-compatible nodes are created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/86xx/common.c -->
