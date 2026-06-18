## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/fadump-internal.h

Purpose: defines internal Firmware-Assisted Dump configuration, crash-info headers, memory range tracking, and platform operations.

Important APIs/types/functions: constants such as `FADUMP_MAX_MEM_REGS`, `FADUMP_REGISTER`, crash-info magic/version, `fadump_str_to_u64()`, `struct fadump_crash_info_header`, `fadump_memory_range`, `fadump_mrange_info`, `fw_dump`, `fadump_ops`, helper declarations for CPU notes and ELF core header updates, and RTAS/OPAL device-tree scan hooks.

Control flow: common FADump code fills `fw_dump`, calls platform ops to initialize metadata, register/unregister/invalidate firmware dumps, process active dumps, and trigger crash capture. `fadump_str_to_u64()` builds stable 8-byte magic values.

State and persistence: `fw_dump` holds persistent dump reservation, boot memory ranges, CPU state destination, metadata, flags, and platform ops. Crash-info headers persist across crash/reboot so the capture kernel can identify and process prior crash data.

Dependencies and integration: integrates with memblock, pt_regs, cpumasks, seq_file reporting, pseries RTAS FADump, PowerNV OPAL FADump, CMA, and ELF core generation.

Risks and test signals: structure layout is cross-kernel persistent; new fields must append and bump versions. Memory range limits and reservation flags affect crash survivability. Test signals include FADump registration, crash trigger and capture boot, old/new header compatibility, OPAL/RTAS paths, reserved-memory contiguity, and ELF vmcore validation.
