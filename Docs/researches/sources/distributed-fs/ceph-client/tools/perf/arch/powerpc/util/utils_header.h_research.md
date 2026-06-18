# sources/distributed-fs/ceph-client/tools/perf/arch/powerpc/util/utils_header.h

Purpose: PowerPC utility macros for reading and decoding the processor version register.

Important APIs/types/functions: `__PERF_UTIL_HEADER_H`, `mfspr`, `SPRN_PVR`, `PVR_VER`, `PVR_REV`.

Control flow: `mfspr` emits inline assembly, and PVR macros split version/revision fields.

State and persistence behavior: No persistent runtime state is owned directly here; the durable effect is build metadata, generated ELF contents, perf.data metadata, or process-local helper state as described by the declarations.

Dependencies and integration points: Depends on PowerPC SPR assembly support.

Risks: Including on non-PowerPC would fail; callers must guard architecture.

Test signals: Build and CPU header reporting on PowerPC.

Source coverage: researched from the complete local file (16 lines, 493 bytes).
