<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/env.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/env.c

Purpose: parses LoongArch firmware environment and boot arguments into kernel setup state.
Important APIs and types: handles firmware argument variables, boot command line extraction, initrd/memmap/environment parsing, and Loongson boot parameter structures.
Control flow: early setup code reads `fw_arg*` values saved by `head.S`, identifies boot protocol style, copies command-line data, and discovers memory/initrd/platform descriptors.
State and persistence: populates global command line, firmware environment pointers, initrd bounds, and Loongson system configuration used later by ACPI/FDT and memory setup.
Dependencies and integration: integrates with `setup.h`, `bootinfo.h`, memblock, EFI/FDT fallback, Loongson platform config, and early printk/console paths.
Risks and test signals: malformed firmware data can corrupt early memory setup or lose command-line options. Signals include boot across firmware revisions, initrd boot, long command lines, and FDT/EFI fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/env.c -->
