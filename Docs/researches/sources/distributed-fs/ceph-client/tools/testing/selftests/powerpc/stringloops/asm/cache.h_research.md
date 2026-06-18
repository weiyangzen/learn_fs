# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/cache.h

Purpose: minimal local replacement for a kernel asm cache header needed by imported `strlen_32.S`.

Important APIs/types/functions: defines `IFETCH_ALIGN_BYTES 4`.

Control flow: no executable logic; used by assembly `.balign IFETCH_ALIGN_BYTES`.

State and persistence behavior: no state.

Dependencies and integration points: included through local `-I$(CURDIR)` when building stringloop assembly.

Risks and test signals: if imported assembly begins relying on more kernel cache definitions, this one-line shim would become insufficient.
