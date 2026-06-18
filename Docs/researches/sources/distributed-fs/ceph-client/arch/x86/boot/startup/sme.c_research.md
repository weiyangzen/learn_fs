# sources/distributed-fs/ceph-client/arch/x86/boot/startup/sme.c

Purpose: detects and enables AMD memory encryption state during startup and performs in-place kernel/initrd encryption for SME.

Important APIs and state: exports `sme_encrypt_kernel(struct boot_params *bp)`, `sme_enable(struct boot_params *bp)`, and local PTI stub `__pti_set_user_pgtbl()` when needed. Internal state includes `sme_workarea` in `.init.scratch` and `struct sme_populate_pgd_data` for temporary page-table construction.

Control flow: `sme_enable()` initializes SNP, verifies AMD SME/SEV CPUID leaf, reads SEV MSR, checks CC blob/SNP consistency, filters SME in hypervisors, checks SYSCFG memory-encryption enablement, and sets `sme_me_mask`, `physical_mask`, `cc_vendor`, and `cc_mask`. `sme_encrypt_kernel()` returns unless SME is active and SEV is not. It computes kernel/initrd/workarea ranges, calculates page-table memory, maps workarea decrypted in current tables, builds a fresh PGD with encrypted identity mappings and decrypted write-protected alternate mappings for kernel/initrd, maps workarea in both views, calls `sme_encrypt_execute()`, removes decrypted mappings, and flushes TLBs.

Dependencies and integration: used by `map_kernel.c` before final virtual mapping. Depends on early page-table helpers, boot params/initrd fields, SNP setup, AMD MSRs, encryption execution assembly, and CoCo core mask state.

Risks and test signals: in-place encryption must not overlap boot params or initrd, and temporary mappings must be non-cacheable/write-protected where required. Test SME bare metal with and without initrd, SEV guests bypassing SME encryption, SNP blob consistency failure, hypervisor-bit SME suppression, and post-encryption execution with decrypted mappings removed.
