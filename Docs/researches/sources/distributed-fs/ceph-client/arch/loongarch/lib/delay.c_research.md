# sources/distributed-fs/ceph-client/arch/loongarch/lib/delay.c

Purpose: implements busy-wait delay primitives for LoongArch.

Important APIs, types, and functions: exported `__delay(unsigned long cycles)`, `__udelay(unsigned long us)`, and `__ndelay(unsigned long ns)`.

Control flow: `__delay()` snapshots `get_cycles()` and loops with `cpu_relax()` until the requested cycle delta has elapsed. Microsecond and nanosecond helpers scale arguments by constants, `HZ`, and `lpj_fine`, then call `__delay()`.

State and persistence: no owned state; depends on global calibrated `lpj_fine` and cycle counter behavior.

Dependencies and integration points: used by generic delay APIs and low-level timing paths, including KVM timer restore settling.

Risks: busy waits depend on stable cycle counters and calibration. Very short delays are sensitive to multiplication overhead; long delays waste CPU.

Test signals: boot calibration sanity, delay accuracy tests, driver timing behavior, and KVM timer paths that use `__delay()`.
