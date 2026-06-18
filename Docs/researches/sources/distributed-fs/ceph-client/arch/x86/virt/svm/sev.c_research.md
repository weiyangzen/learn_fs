<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/sev.c -->
# sources/distributed-fs/ceph-client/arch/x86/virt/svm/sev.c

## Purpose
`sev.c` implements AMD SEV-SNP host RMP table discovery, setup, lookup, update, direct-map adjustment, page leak tracking, and SNP enable/shutdown preparation.

## Important APIs, types, and functions
Key types are `struct rmpentry`, `struct rmpentry_raw`, and `struct rmp_segment_desc`. Major APIs include `snp_probe_rmptable_info()`, `snp_fixup_e820_tables()`, `snp_rmptable_init()`, `snp_prepare()`, `snp_shutdown()`, `snp_lookup_rmpentry()`, `snp_dump_hva_rmpentry()`, `psmash()`, `rmp_make_private()`, `rmp_make_shared()`, `__snp_leak_pages()`, and `kdump_sev_callback()`.

## Control flow
Boot probes contiguous or segmented RMP MSRs/CPUID, reserves unaligned RMP edges in e820/memblock, maps RMP bookkeeping and segment tables, validates RAM coverage, and enables SNP through MSR programming on all CPUs after clearing RMP and HSAVE state. Runtime lookups use RMPREAD when available or raw mapped RMP entries otherwise, with nospec bounds. RMPUPDATE transitions pages between shared/private, splitting large direct-map mappings when 4K private pages could conflict with host writes.

## State and persistence behavior
Persistent global state includes RMP configuration/base/size, segment table descriptors, bookkeeping mapping, leaked-page list and count, and `crash_kexec_post_notifiers`. RMP hardware state persists in firmware-owned RMP memory and CPU MSRs.

## Dependencies and integration points
It depends on AMD SNP/SME MSRs and instructions (`RMPREAD`, `RMPUPDATE`, `PSMASH`), IOMMU SNP enablement, e820/memblock, direct-map page attribute APIs, CPUID leaf `0x80000025`, CCP firmware sequencing, KVM users of exported RMP functions, and crash/kdump callbacks.

## Risks and edge cases
Coverage and alignment checks are safety-critical: an RMP table that misses RAM or overlaps 2 MiB boundaries can cause fatal RMP faults. RMP updates can fail on overlap and are retried, but other failures dump RMP state and stack. Raw RMP format is model-specific when RMPREAD is absent. Leaked pages are intentionally withheld from the allocator.

## Test signals
Signals include SNP-capable AMD boot, RMP table probe logs, SNP_INIT/SHUTDOWN via CCP, KVM SNP guest private/shared page transitions, RMP fault diagnostics, kdump with SNP enabled, and direct-map split warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/svm/sev.c -->
