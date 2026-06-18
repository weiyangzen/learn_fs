<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.c

### Purpose
`voltage.c` implements the OMAP voltage-domain registry and common voltage-management APIs used by DVFS, SmartReflex, VC, and VP code.

### Important APIs, Types, And Functions
Public APIs include `voltdm_get_voltage()`, `voltdm_reset()`, `omap_voltage_get_volttable()`, `omap_voltage_get_voltdata()`, `omap_voltage_register_pmic()`, `omap_voltage_late_init()`, `voltdm_lookup()`, and `voltdm_init()`. The internal list is `voltdm_list`.

### Control Flow
`voltdm_init()` registers SoC-provided voltage-domain objects. Late init walks scalable domains, obtains the system clock rate, initializes VC and/or VP blocks, and assigns the scale callback. Scaling chooses the first OPP voltage greater than or equal to the target, calls the domain scale method, and updates the nominal voltage on success.

### State, Persistence, And Dependencies
Voltage-domain objects persist on a global list and hold PMIC data, OPP voltage tables, current nominal voltage, sysclk rate, and register callbacks. Dependencies include clock lookup, debug/logging, SoC PRM register helpers, VC/VP modules, power domains, and OPP voltage data.

### Integration Points
SmartReflex uses voltage tables and domain lookup, PMIC code registers `omap_voltdm_pmic`, and DVFS paths use domain scale/reset behavior.

### Risks
`_voltdm_register()` does not check duplicates. Late init can return early on one clock failure and skip later domains. If both VC and VP exist, VP force-update overwrites the scale callback after VC init. Nominal voltage starts at zero unless initialized elsewhere.

### Test Signals
Boot should register expected domains, late init should resolve sysclk for all scalable domains, and DVFS tests should verify target rounding, nominal voltage update, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/voltage.c -->
