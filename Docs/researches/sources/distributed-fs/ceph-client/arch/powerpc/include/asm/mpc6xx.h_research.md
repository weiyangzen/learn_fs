# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/mpc6xx.h

Purpose: declares the MPC6xx standby entry routine.

Important APIs/types/functions: `mpc6xx_enter_standby(void)`.

Control flow: platform idle or power-management code calls the routine to place an MPC6xx CPU into standby.

State and persistence: CPU power state changes in hardware; no software state is defined here.

Dependencies and integration points: integrates classic PowerPC 6xx platform power-management code with CPU-specific low-power assembly/C implementation.

Risks: standby entry must preserve enough CPU/platform state for resume; calling it on unsupported processors can hang.

Test signals: suspend/idle tests on MPC6xx-class hardware and build checks for platforms referencing the declaration.
