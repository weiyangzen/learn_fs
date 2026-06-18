# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/mmu-hash.h

Purpose: defines 64-bit Book3S hash MMU structures, HPTE/SLB encodings, VSID allocation, hash calculations, segment handling, and hash-specific `mm_context` data.

Important APIs/types/functions: core types are `struct mmu_hash_ops`, `struct hash_pte`, `struct slb_entry`, `struct slice_mask`, `struct hash_mm_context`, and optional `struct subpage_prot_table`. Helpers include page-size conversions, `hpte_encode_avpn()`, old/new HPTE conversion, `hpte_encode_v/r()`, `hpt_vpn()`, `hpt_hash()`, `vsid_scramble()`, `user_segment_size()`, `get_vsid()`, `get_kernel_context()`, `get_kernel_vsid()`, `mk_esid_data()`, and `mk_vsid_data()`. Numerous externs cover hash faulting, HPTE insertion/removal, SLB management, and setup.

Control flow: hash faults compute VSIDs from context and EA, encode HPTE V/R words, hash VPNs into HPTE groups, then call `mmu_hash_ops` to insert/update/remove entries. SLB helpers encode ESID/VSID data for bolted and dynamic segment entries. Context helpers assign different kernel contexts to linear, vmalloc, IO, and vmemmap regions.

State and persistence: persistent boot state includes `mmu_hash_ops`, `htab_address`, `htab_size_bytes`, `htab_hash_mask`, page-size definitions, segment sizes, SLB size, and per-mm `hash_mm_context` slice masks. Hardware state includes SLB and HPTE entries.

Dependencies and integration points: included by `book3s/64/mmu.h` and pgtable code; integrates with pSeries/native HPTE backends, SLB miss handlers, subpage protection, slices, hugepages, KVM/firmware page-size capabilities, and kexec cleanup.

Risks: VSID math must avoid zero/reserved VSIDs and stay bijective. ISA 3.0 HPTE format conversion must match CPU features. Kernel context counts depend on physical memory bits. Any mismatch between page-size encodings and HPTE insertion can cause hard-to-debug translation faults.

Test signals: hash MMU boot on pre- and post-POWER9 systems, SLB miss stress, hugepage and subpage protection tests, pSeries/native HPTE backend tests, kexec, and memory configurations above 512TB where supported.
