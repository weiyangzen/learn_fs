# sources/distributed-fs/ceph-client/arch/sparc/lib/libgcc.h

Purpose: Shared type definitions for SPARC libgcc-style helper implementations.

Important APIs/functions: Defines `word_type` with GCC `mode(__word__)`.

Control flow: Header-only; no runtime control flow.

State and persistence: No state.

Dependencies/integration: Includes `asm/byteorder.h`; supports arithmetic helper files that need compiler word-sized types.

Risks/test signals: Type width must match compiler ABI. Test by building SPARC32 arithmetic helpers and checking generated symbol ABI.
