# sources/distributed-fs/ceph-client/include/uapi/linux/tps6594_pfsm.h

Purpose: Defines userspace ioctls for controlling the TPS6594 PMIC pre-configurable finite state machine.

Important APIs/types/functions: `struct pmic_state_opt` carries state options as `gpio_retention` and `ddr_retention` booleans/bytes. Ioctls under base `'P'` include standby, low-power standby, update PGM, set active state, set MCU-only state, and set retention state.

Control flow: Userspace opens the PMIC PFSM device and issues an ioctl. Some commands are pure transitions; MCU-only and retention transitions pass `pmic_state_opt` via `_IOW` so the kernel programs retention policy before state change.

State and persistence behavior: Commands alter PMIC power state and retention behavior. Effects may outlive the calling process and can influence system suspend/resume or power domains.

Dependencies and integration points: Includes `linux/const.h`, `linux/ioctl.h`, and `linux/types.h`; integrates with the TPS6594 PMIC driver and platform power-management stack.

Risks: Incorrect transition requests may power down domains unexpectedly. ABI leaves reserved expansion minimal, so future flags need compatibility care.

Test signals: Validate ioctl numbers, userspace structure size, permission checks, transition success/failure on supported boards, and retention options across suspend/resume cycles.
