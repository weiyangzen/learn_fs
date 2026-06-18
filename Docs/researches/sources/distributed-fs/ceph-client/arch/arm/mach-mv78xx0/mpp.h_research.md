# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mpp.h

Purpose: MV78xx0 MPP pin function definitions.

Important APIs/types/functions: Defines per-pin MPP function macros and helper declarations used by board files.

Control flow: No runtime flow.

State and persistence: No mutable state.

Dependencies and integration points: Integrates with `mpp.c` and board setup pin arrays.

Risks: Incorrect function encodings write wrong mux values.

Test signals: Compile board files and validate pin functions on hardware.
