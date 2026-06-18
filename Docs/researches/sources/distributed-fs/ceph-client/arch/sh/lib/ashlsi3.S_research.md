# sources/distributed-fs/ceph-client/arch/sh/lib/ashlsi3.S

Purpose: implements the libgcc-compatible 32-bit arithmetic/logical left shift helper `__ashlsi3`.

Important symbols: `__ashlsi3`, `__ashlsi3_r0`, jump table `ashlsi3_table`, and count-specific labels `ashlsi3_0` through `ashlsi3_31`.

Control flow: dispatches by shift count, uses prearranged fall-through blocks to apply efficient `shll` sequences, and returns shifted result in the ABI result register.

State and persistence: register-only helper with no memory state.

Dependencies and integration: selected by `arch/sh/lib/Makefile` and used to satisfy compiler-generated left-shift calls.

Risks: table alignment, count masking, and ABI register conventions are critical because compiler output may call this frequently.

Test signals: libgcc arithmetic tests and kernel code paths using variable left shifts.
