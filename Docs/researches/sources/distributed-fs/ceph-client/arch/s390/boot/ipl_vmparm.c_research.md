<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ipl_vmparm.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/ipl_vmparm.c

Purpose: Builds the boot-decompressor version of the s390 VM parameter parsing code by including `../kernel/ipl_vmparm.c` into the boot compilation unit.

Important APIs/types/functions: This file declares no local API. Its functional surface is inherited from the kernel implementation it includes, allowing the decompressor to share IPL VM parameter parsing behavior without maintaining a second copy.

Control flow: Compilation textual-includes the kernel source. Runtime control flow is therefore exactly the included implementation's flow, but linked into the boot environment with boot headers and symbol visibility.

State and persistence: No local state exists. Any state comes from the included IPL VM parameter implementation and from boot data symbols that the included file references.

Dependencies and integration points: Depends on the relative include path to `arch/s390/kernel/ipl_vmparm.c` and on that file staying compatible with the restricted boot environment. It is integrated by the boot Makefile as part of decompressor support.

Risks: Include-wrapper files are sensitive to implicit dependencies: if the kernel implementation begins depending on normal kernel services unavailable during decompression, boot builds can fail or early boot can fault. Review must cover the included file when behavior changes.

Test signals: s390 boot builds with changed IPL VM parameter parsing, IPL command-line/VM parameter parsing tests, and decompressor link checks are the relevant signals.

Source read size: 2 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/ipl_vmparm.c -->
