# sources/distributed-fs/ceph-client/arch/arm/kernel/phys2virt.S

Purpose: patches physical-to-virtual and virtual-to-physical conversion instruction sequences based on the boot-time `PHYS_OFFSET - PAGE_OFFSET` delta.

Important APIs/types/functions: `__fixup_pv_table` runs early from head code, `fixup_pv_table` patches module tables, and `__fixup_a_pv_table` handles ARM/Thumb-2 and LPAE/non-LPAE encodings. Data symbols `__pv_phys_pfn_offset` and `__pv_offset` export the calculated offset.

Control flow: early fixup stores PFN offset and signed PV delta, verifies 2 MiB alignment, then iterates linker-provided table entries and rewrites immediate fields in patchable instruction sequences. Module finalization calls the public wrapper for `.pv_table`.

State and persistence: patched instructions and exported offset data persist for the kernel lifetime.

Dependencies and integration: depends on linker pv tables, head.S register contracts, ARM/Thumb instruction encodings, endian modes, LPAE, and module finalization.

Risks: unsupported alignment deadloops early; wrong immediate patching corrupts all address translation helpers. Test signals include boot on varied RAM offsets, LPAE/non-LPAE and BE8/LE builds, module loading with `.pv_table`, and virt/phys conversion self-checks.
