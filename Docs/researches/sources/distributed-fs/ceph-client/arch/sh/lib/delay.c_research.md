# sources/distributed-fs/ceph-client/arch/sh/lib/delay.c

Purpose: implements busy-wait delay primitives for SH.

Important APIs: `__delay`, `__const_udelay`, `__udelay`, and `__ndelay`.

Control flow: `__delay` loops until the requested cycle count expires while calling `cpu_relax`. Microsecond/nanosecond helpers scale requested time by `loops_per_jiffy` and constants, then delegate to `__delay`.

State and persistence: reads global calibration state (`loops_per_jiffy`) but does not persist anything.

Dependencies and integration: used by generic kernel delay APIs and early/atomic code where sleeping is impossible.

Risks: incorrect scaling causes device timing failures or excessive spin time. CPU frequency/calibration changes can affect accuracy.

Test signals: boot delay calibration, driver timing behavior, and delay-loop sanity tests.
