<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/stackprotector.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/stackprotector.c

Purpose: Pulls the s390 kernel stack protector implementation into the boot build with a boot-specific logging prefix.

Important APIs/types/functions: Defines `boot_fmt(fmt) "stackprot: " fmt` and includes `../kernel/stackprotector.c`. Local behavior is inherited from the shared kernel implementation, including early application from `startup_kernel()`.

Control flow: The shared implementation is compiled into the decompressor and invoked by startup after alternatives and bootdata are prepared.

State and persistence: Stack protector state belongs to the included implementation and the vmlinux metadata it patches or initializes.

Dependencies and integration points: Integrated by `startup.c` through `stack_protector_apply_early(text_lma)`. Depends on the included kernel file remaining compatible with boot-only logging and memory access.

Risks: Stack protector setup is security-sensitive and runs before the normal kernel. Offset mismatches in vmlinux metadata or unsupported dependencies in the included file could leave canaries unapplied or corrupt early text/data.

Test signals: `CONFIG_STACKPROTECTOR` s390 builds, early boot with canary patching enabled, and inspection of patched stack-protector ranges after KASLR relocation.

Source read size: 6 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/stackprotector.c -->
