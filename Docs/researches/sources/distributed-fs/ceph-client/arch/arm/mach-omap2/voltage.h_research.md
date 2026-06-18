<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.h

### Purpose
`voltage.h` defines the core OMAP voltage-domain data model, PMIC callback contract, voltage processor/controller parameters, limits, and public voltage-management APIs.

### Important APIs, Types, And Functions
Key types are `struct voltagedomain`, `struct omap_voltdm_pmic`, `struct omap_vp_param`, `struct omap_vc_param`, and `struct omap_vfsm_instance`. It declares voltage-domain init functions for OMAP2/3/4/5 and common lookup/register/query APIs.

### Control Flow
The header has no runtime flow. Its function pointers define how generic voltage code reads, writes, and read-modify-writes SoC PRM registers and how domains scale voltage.

### State, Persistence, And Dependencies
Instances of `struct voltagedomain` carry persistent platform state, current nominal voltage, PMIC data, voltage tables, and VC/VP pointers. The header depends on VC/VP definitions and platform voltage data.

### Integration Points
Every OMAP voltage-domain data file, VC/VP implementation, PMIC registration code, and SmartReflex setup uses this contract.

### Risks
The `sys_clk` union changes meaning from clock name during init to rate after late init, so callers must respect initialization phases. PMIC callbacks are mandatory for scalable domains, and missing callbacks produce runtime failures.

### Test Signals
Builds across OMAP2/3/4/5 configurations validate the structure relationships; runtime voltage scaling validates PMIC callback behavior and domain registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.h -->
