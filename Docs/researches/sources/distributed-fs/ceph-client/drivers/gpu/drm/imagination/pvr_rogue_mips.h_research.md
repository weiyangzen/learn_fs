<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_mips.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_mips.h

Purpose: Defines the Rogue firmware MIPS address-space, TLB, remap, boot-data, exception, and debug-state ABI shared by host driver code and MIPS firmware diagnostics.

Important APIs/types/functions: This header is macro-heavy rather than function-heavy. Key exported layout types are `struct rogue_mipsfw_boot_data`, `struct rogue_mips_tlb_entry`, `struct rogue_mips_remap_entry`, and `struct rogue_mips_state`. Constants describe MIPS firmware page sizes, page-table sizing, cache policies, EntryLo/PFN encoding, remap trampoline regions, boot/data/code remap virtual and physical bases, NMI shared offsets, MIPS C0 cause/debug decoding, and TLB/remap decoders.

Control flow: The file has no runtime control flow; it is a compile-time contract consumed by MIPS firmware setup, boot-data writers, debug dump readers, and VM code such as `pvr_vm_mips.c`.

State and persistence behavior: The structures model persisted firmware-visible state in memory, especially bootloader configuration and the `rogue_mips_state` dump that includes registers, TLB entries, and remap entries. Layout is part of the firmware ABI and is checked by the included `pvr_rogue_mips_check.h`.

Dependencies: Uses Linux `BIT()` and fixed-width types. It depends conceptually on the PowerVR firmware heap geometry and is included by firmware/MIPS VM paths.

Integration points: `pvr_vm_mips.c` uses the page-size, PTE flag, PFN mask, and cache-policy macros to populate MIPS firmware page tables. Firmware boot/start paths use boot-data offsets and remap bases. Debug and dump paths can decode C0 state and TLB/remap entries using the macros and structs.

Risks: Any change to constants or struct layout can break firmware boot, TLB mapping, crash dump decoding, or compatibility with firmware binaries. Physical-address handling is sensitive to 32-bit versus wider physical buses, so PFN masks and cache policies must stay aligned with hardware behavior.

Test signals: Compile-time `static_assert()` coverage in `pvr_rogue_mips_check.h` is the primary direct signal. Runtime signals include successful MIPS firmware boot, correct firmware-object mapping through `pvr_vm_mips_map()`, MMU flush success, and meaningful MIPS debug dumps after firmware faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_mips.h -->
