# sources/distributed-fs/ceph-client/include/soc/at91/sama7-sfrbu.h

Purpose: exposes SAMA7 backup special-function register offsets and bits for backup power-switch and DDR power state control.

Important APIs and types: under `CONFIG_SOC_SAMA7`, `AT91_SFRBU_PSWBU` identifies the power-switch backup control register; macros define the mandatory write key, state, soft-switch source, and control bits. `AT91_FRBU_DDRPWR` and its state bit expose DDR power mode state.

Control flow: SAMA7 power-management code writes the keyed control register to switch backup power behavior and reads DDR power state during suspend/resume or backup-domain transitions.

State and persistence: hardware backup-domain state may survive portions of system sleep, but this header stores no software state.

Dependencies and integration points: gated by `CONFIG_SOC_SAMA7` and consumed by SAMA7 platform power-management/backup-domain drivers.

Risks and test signals: risks include missing key bits when writing, wrong conditional compile expectations on non-SAMA7 builds, and entering DDR power modes without retention. Test SAMA7 compile, backup power switch state transitions, DDR power-state reads during low power, and resume correctness.
