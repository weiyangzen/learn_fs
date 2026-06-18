# sources/distributed-fs/ceph-client/arch/arm64/lib/delay.c

Purpose: implements calibrated busy-wait delay primitives on ARM64 using the architectural counter, optional WFxT wait instructions, and timer event stream hints.

Important APIs/types/functions: `USECS_TO_CYCLES`, `xloops_to_cycles`, `__delay_cycles`, `__delay`, `__const_udelay`, `__udelay`, and `__ndelay`.

Control flow: delay requests convert loop or time units to counter cycles. `__delay` captures a stable CNTVCT start value, optionally uses `wfit` and `wfet` until the deadline on WFxT-capable CPUs, otherwise uses event-stream `wfe` for long enough waits, and finally spins with `cpu_relax` until elapsed cycles reach the target.

State and persistence: reads `loops_per_jiffy`, `HZ`, and the architectural counter. No persistent state.

Dependencies/integration: exported to generic delay APIs; depends on ARM arch timer, alternatives for `ARM64_HAS_WFXT`, preemption guards, and event-stream availability.

Risks: counter source must match WFxT deadline semantics, especially under KVM/EL1 CNTVOFF behavior. Calibration overflow or early wake handling can produce too-short delays. Busy waits consume CPU when WFxT/event stream is unavailable.

Test signals: delay calibration tests, udelay/ndelay minimum-duration checks, WFxT and non-WFxT hardware, KVM host/guest counter offset scenarios, and preemption/interrupt stress during delays.
