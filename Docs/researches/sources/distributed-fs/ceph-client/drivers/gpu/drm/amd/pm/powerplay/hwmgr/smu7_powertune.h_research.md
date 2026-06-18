# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_powertune.h

Purpose: public interface and local register-field definitions for SMU7 PowerTune.

Important APIs/types: defines missing DIDT `UNUSED_0` masks/shifts for SQ, TD, and TCP control/tuning registers; defines `POWERCONTAINMENT_FEATURE_DTE`, `POWERCONTAINMENT_FEATURE_TDCLimit`, and `POWERCONTAINMENT_FEATURE_PkgPwrLimit`; provides indirect offsets for GC CAC and selected DIDT control registers; declares CAC, power containment, power limit, power-control, and DIDT enable/disable functions.

Control flow and state: callers do not manipulate DIDT or CAC registers directly; they call the implementation functions declared here. State is stored in SMU7 backend fields and SMC/hardware registers, while this header only defines the bit contract.

Dependencies and integration: included by SMU7 hwmgr code and requires `struct pp_hwmgr` / integer type visibility. The constants must match generated AMD register definitions and SMC firmware semantics.

Risks and test signals: `smu7_set_power_limit()` and `smu7_power_control_set_level()` carry unit-sensitive contracts. Compile all SMU7 users and test CAC, power containment, DIDT, and power-limit operations on supported ASICs.
