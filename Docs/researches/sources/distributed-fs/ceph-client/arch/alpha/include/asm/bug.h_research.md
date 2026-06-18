# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/bug.h

This header defines Alpha's architecture `BUG()` implementation when `CONFIG_BUG` is enabled. The macro emits `call_pal PAL_bugchk`, followed by the source line and file pointer, then marks the path unreachable.

It integrates with PALcode and `asm-generic/bug.h`, providing `HAVE_ARCH_BUG`. The comment notes why `.gprel32` is avoided: modules might not have GP loaded for the file reference. Persistent state is crash/debug metadata embedded in the instruction stream.

Risks are module relocation/GP assumptions and tooling expectations around the inline `.long`/`.8byte` data after the PAL call. Test signals are build coverage and decoding of BUG reports on Alpha.
