<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.c

### Purpose
`vp.c` implements OMAP Voltage Processor initialization, force-update voltage scaling, error-gain updates, and VP enable/disable operations.

### Important APIs, Types, And Functions
Public APIs are `omap_vp_init()`, `omap_vp_update_errorgain()`, `omap_vp_forceupdate_scale()`, `omap_vp_enable()`, and `omap_vp_disable()`. Internal helper `_vp_set_init_voltage()` writes INITVOLTAGE and toggles INITVDD.

### Control Flow
Init validates PMIC callbacks and register access, computes timeout and wait times from sysclk and PMIC slew data, clamps VP min/max to PMIC limits, and programs VP_CONFIG, VSTEPMIN, VSTEPMAX, and VLIMITTO. Force-update scaling performs VC pre-scale setup, clears stale transaction-done status, loads the target voltage, asserts FORCEUPDATE, waits for transaction done, runs VC post-scale delay, clears status, and drops FORCEUPDATE.

### State, Persistence, And Dependencies
The `enabled` flag persists in each `omap_vp_instance`. Hardware state persists in VP registers and transaction-done status. Dependencies include PMIC voltage conversion, VC pre/post scale helpers, voltage OPP data for error gain, and SoC-specific VP ops.

### Integration Points
`omap_voltage_late_init()` initializes VP and selects `omap_vp_forceupdate_scale()` as the domain scale callback when VP is present. SmartReflex class drivers use VP enable/disable.

### Risks
Timeouts are fixed constants and may not match all PMIC latency. `omap_vp_forceupdate_scale()` logs but still returns success if transaction done never sets after FORCEUPDATE. `_vp_set_init_voltage()` uses `char vsel`, so unusually high VSEL values deserve attention.

### Test Signals
DVFS force-update tests should verify transaction-done set/clear behavior, error-gain updates per OPP, VP enable/disable idempotence, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/vp.c -->
