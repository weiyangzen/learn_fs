# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si_enums.h

Purpose: small SI-era macro header for priority, RLC power/clock status, and RLC state-table offsets.

Important APIs, types, and functions: defines masks such as `PRIORITY_MARK_MASK`, `PRIORITY_OFF`, `GFX_POWER_STATUS`, `RLC_BUSY_STATUS`, `RLC_PUD/PDD/TTPD/MSD` fields, and RLC save/restore offsets.

Control flow: no runtime flow. Consumers compose or test bitfields against SI hardware registers or RLC memory layouts.

State and persistence: no software state. The macros describe encoded hardware state and firmware table offsets.

Dependencies and integration points: included by SI common/GFX-related code alongside generated GFX and OSS register headers.

Risks and test signals: incorrect masks would cause invalid RLC power sequencing or status interpretation. Test signals are clock/power-gating stability, RLC save/restore behavior, and clean GPU reset/resume on SI parts.
