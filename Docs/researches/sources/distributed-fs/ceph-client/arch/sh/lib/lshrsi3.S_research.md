# sources/distributed-fs/ceph-client/arch/sh/lib/lshrsi3.S

Purpose: implements the libgcc-compatible unsigned 32-bit logical right shift helper `__lshrsi3`.

Important symbols: `__lshrsi3`, `__lshrsi3_r0`, `lshrsi3_table`, and count-specific labels.

Control flow: dispatches by shift count and applies zero-filling right-shift sequences, unlike signed `__ashrsi3`.

State and persistence: register-only computation with no persistent state.

Dependencies and integration: satisfies compiler-generated unsigned right-shift helper calls.

Risks: zero-fill behavior and large-count handling are critical; confusing arithmetic and logical shifts corrupts bit operations.

Test signals: unsigned shift arithmetic tests with high-bit values and all representative counts.
