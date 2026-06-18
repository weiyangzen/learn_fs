# sources/distributed-fs/ceph-client/arch/arc/include/asm/exec.h

Purpose: ARC process-exec stack alignment policy. Important APIs/types/functions: defines `arch_align_stack(p)` to align down to a 16-byte boundary. Control flow: single macro applied during exec stack setup. State and persistence: affects initial userspace stack pointer. Dependencies/integration: used by generic exec/binfmt code. Risks: ABI breakage if alignment changes unexpectedly. Test signals: userspace ABI tests, dynamic loader startup, and stack alignment checks.
