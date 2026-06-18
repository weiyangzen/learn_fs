# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/ivsrcid/thm/irqsrcs_thm_9_0.h

## Purpose
Defines THM 9.0 digital thermal threshold interrupt source IDs for low-to-high and high-to-low transitions.

## Important APIs, Types, and Functions
There are no functions or structs. `THM_9_0__SRCID__THM_DIG_THERM_L2H` is `0` for ASIC temperature rising above `CG_THERMAL_INT.DIG_THERM_INTH`; `THM_9_0__SRCID__THM_DIG_THERM_H2L` is `1` for temperature falling below `CG_THERMAL_INT.DIG_THERM_INTL`.

## Control Flow
No direct code flow exists. Thermal interrupt handlers use these IDs to choose alarm/throttle behavior for rising temperature and recovery/hysteresis behavior for falling temperature.

## State and Persistence
The header stores no state. It encodes stable hardware interrupt identifiers.

## Dependencies and Integration Points
The header depends only on its guard. It integrates with AMDGPU thermal management, power-management throttling, and `CG_THERMAL_INT` interrupt enablement.

## Risks and Test Signals
Incorrect mapping could invert thermal state transitions. Test signals include controlled threshold-crossing tests showing L2H before thermal mitigation and H2L during recovery.
