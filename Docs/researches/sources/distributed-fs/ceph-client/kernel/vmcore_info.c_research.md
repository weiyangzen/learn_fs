<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/vmcore_info.c -->
# sources/distributed-fs/ceph-client/kernel/vmcore_info.c

Purpose: builds and updates the `VMCOREINFO` ELF note used by crash dump tooling to interpret kernel memory after kexec/kdump. It records kernel layout, type sizes, offsets, symbols, page flags, build ID, and crash-time data.

Important APIs and state: global state includes `vmcoreinfo_data`, `vmcoreinfo_size`, `vmcoreinfo_note`, `vmcoreinfo_data_safecopy`, and `hwerr_data`. Public helpers include `append_elf_note()`, `final_note()`, `crash_update_vmcoreinfo_safecopy()`, `crash_save_vmcoreinfo()`, `vmcoreinfo_append_str()`, weak `arch_crash_save_vmcoreinfo()`, weak/exported `paddr_vmcoreinfo_note()`, and `hwerr_log_error_type()`.

Control flow: init allocates a data buffer and note buffer, appends standard OS/build/page/memory-management metadata through `VMCOREINFO_*` macros, lets architecture code append extra data, and writes the ELF note. On crash save, it switches to a safe copy if one exists, appends `CRASHTIME`, and updates the note. Hardware error logging increments per-type counters and records timestamps.

State and persistence: vmcoreinfo buffers are allocated for kernel lifetime and consumed by crash/kexec paths. `vmcoreinfo_size` monotonically grows until full; overflow is truncated with a warning. Safe copy pointer can redirect writes for crash memory.

Dependencies and integration: depends on kexec/crash infrastructure, ELF notes, memblock/memory layout symbols, kallsyms, build ID, log buffer vmcoreinfo, architecture sections, and optional memory model configs.

Risks: truncation can omit metadata needed by dump tools. Note buffer allocation failure disables vmcoreinfo. Architecture overrides must preserve format. Test signals include boot-time vmcoreinfo allocation, generated note parsing by crash tools, crash-time CRASHTIME update, safe-copy use, memory model config coverage, and hardware error counter updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/vmcore_info.c -->
