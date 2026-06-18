# sources/distributed-fs/ceph-client/arch/sparc/lib/M7copy_from_user.S

Purpose: M7/T4-style optimized copy-from-user wrapper over `M7memcpy.S`.

Important APIs/functions: Defines exception-table wrappers for integer and floating-point loads, `FUNC_NAME M7copy_from_user`, ASI-based `LOAD`, `EX_RETVAL(0)`, and a preamble that checks `%asi` before falling back to `raw_copy_in_user`.

Control flow: The included M7 copy engine handles alignment, block/VIS paths, and tails while all user loads are guarded through exception-table records. On load fault, fixup returns a residual count appropriate for raw copy-from-user semantics.

State and persistence: No persistent data; transiently uses `%asi`, VIS/FPU state through the included implementation, and exception metadata.

Dependencies/integration: Depends on `M7memcpy.S`, `Memcpy_utils.S` residual helpers, `asm/asi.h`, VIS support, and M7 patching.

Risks/test signals: M7-specific ASIs and VIS paths must fault cleanly and restore state. Test user-source page faults, all alignments, large block copies, and fallback to `raw_copy_in_user` when ASI context changes.
