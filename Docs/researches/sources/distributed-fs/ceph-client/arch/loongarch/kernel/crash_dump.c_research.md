<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/crash_dump.c -->
# sources/distributed-fs/ceph-client/arch/loongarch/kernel/crash_dump.c

Purpose: provides LoongArch crash dump memory copy support.
Important APIs and types: implements crash-dump copy helpers that map old memory and copy into kernel/user I/O vectors.
Control flow: kdump/vmcore code calls into this file to read physical memory from the crashed kernel using ioremap-style mappings and copy_to_iter semantics.
State and persistence: no long-lived local state; it reads crash memory and writes caller buffers.
Dependencies and integration: depends on `linux/crash_dump.h`, `io.h`, and `uio.h`; integrates with `/proc/vmcore` and kdump tooling.
Risks and test signals: address translation or copy faults break crash dump capture. Signals include kdump boot, vmcore read, makedumpfile, and sparse memory crash ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/kernel/crash_dump.c -->
