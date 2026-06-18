# sources/distributed-fs/ceph-client/arch/arc/net/bpf_jit.h

Purpose: declares the backend contract between ARC BPF JIT core logic and architecture-specific instruction emitters.

Important APIs/types/functions: defines `ARC_ADDR`, temporary JIT register index `JIT_REG_TMP`, safe buffer advancement macro `BUF()`, backend emitter prototypes for moves, loads/stores, arithmetic, bitwise ops, shifts, frame handling, jumps, calls, return marshalling, and byte swapping. Defines `enum ARC_CC` for backend-independent ARC jump conditions.

Control flow: no executable control flow. The prototypes encode a two-pass JIT model where emitters can be called with `buf == NULL` to compute lengths and with a real buffer to emit bytes. `BUF()` preserves NULL during dry runs.

State and persistence: no owned state.

Dependencies and integration: included by ARC BPF JIT core and ARCv2 backend. Depends on Linux BPF register definitions and filter infrastructure.

Risks: length-return contracts are critical; divergent lengths between dry run and emit pass corrupt branch offsets and code layout. `enum ARC_CC` order is used by array sizing/indexing in the backend and must not be changed casually.

Test signals: BPF JIT dry-run/emission consistency, branch offset selftests, all ALU/memory/call op translations, and compile coverage for debug mode.
