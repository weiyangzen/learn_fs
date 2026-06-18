# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/delay.h

This header declares Alpha delay primitives: `__delay`, `udelay`, and `ndelay`, and marks `ndelay` as arch-provided. There is no local implementation or state.

Integration is with generic timing/delay users and Alpha library implementations calibrated from CPU timing data. Risks are calibration accuracy and overflow/rounding for very small or large delays. Test signals are boot calibration, device driver timing stability, and compile coverage for generic delay APIs.
