# sources/distributed-fs/ceph-client/arch/x86/kernel/machine_kexec_64.c

Purpose: Handles 64-bit x86 kexec transition setup, relocation execution, purgatory relocations, crash-memory protection, and memory-encryption adjustments for kexec control pages.

Important APIs/types/functions: exports `kexec_file_loaders`, `machine_kexec_prepare()`, `machine_kexec_cleanup()`, `machine_kexec()`, `arch_kexec_apply_relocations_add()`, `arch_kimage_file_post_load_cleanup()`, crash resource protect/unprotect APIs, `arch_kexec_post_alloc_pages()`, and `arch_kexec_pre_free_pages()`. Helpers build identity mappings for RAM, segments, EFI tables, ACPI tables, MMIO serial debug, and transition virtual mapping.

Control flow: prepare rejects CPUs with the TDX partial-write machine-check erratum, creates identity page tables using control pages, maps current RAM and image segments, maps EFI/ACPI/debug ranges, maps the control page at its current virtual address, records global relocation arguments, prepares a debug IDT, copies relocation code into the control page, and marks it ROX. Execution disables ftrace, interrupts, hardware breakpoints, and CET, optionally resets IOAPIC for preserve-context, computes relocation flags including preserve-context and cache-incoherent state, reloads flat segments, and calls the copied relocation routine. Cleanup restores page permissions and frees transition page-table pages.

State and persistence: `image->arch` owns transition page-table pages. Globals such as `kexec_va_control_page`, `kexec_pa_table_page`, and optional swap-page physical address are consumed by relocation code. Crash kernel resources and dm-crypt key pages can be marked read-only or not-present while idle.

Dependencies and integration points: depends on generic kexec, x86 identity mapping helpers, EFI/ACPI resource discovery, memory encryption and confidential-computing attributes, CET disable, ftrace, IOAPIC, purgatory ELF relocation, crash dump resources, and kexec file loader for bzImage64.

Risks: `machine_kexec()` cannot allocate or call functions after GS is reset because percpu state is unavailable. Encryption attributes must match SME/SEV expectations for new-kernel access. Purgatory relocation supports only selected x86_64 relocation types and checks overflow. Crash resource protection must skip the active control page.

Test signals: 64-bit kexec and kdump tests should run with 4-level and 5-level paging, EFI/ACPI tables outside normal RAM, serial debug mapping, SME/SEV/TDX combinations, CET enabled, crash resource protection toggling, dm-crypt key preservation, purgatory relocation overflow failures, and kexec-jump preserve-context return.
