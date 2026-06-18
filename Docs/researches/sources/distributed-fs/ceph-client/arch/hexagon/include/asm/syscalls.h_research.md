# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/syscalls.h

Purpose: Hexagon syscall declarations via generic syscall header.

Important APIs/types/functions: No local public API surface; this file contributes declarations, constants, or selected objects to surrounding architecture code.

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm-generic/syscalls.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.
