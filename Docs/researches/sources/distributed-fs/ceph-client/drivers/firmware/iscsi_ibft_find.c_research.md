# sources/distributed-fs/ceph-client/drivers/firmware/iscsi_ibft_find.c

Purpose: Finds and reserves a legacy BIOS iBFT/BIFT table in low memory before ACPI parsing, for non-UEFI systems.

Important APIs/types/functions: Exports `ibft_phys_addr`. `reserve_ibft_region()` scans physical memory from `IBFT_START` to `IBFT_END` in 16-byte increments, skipping VGA memory, looking for `iBFT` or `BIFT` signatures.

Control flow: The routine exits immediately on EFI boot because iBFT 1.03 requires UEFI systems to use ACPI. Otherwise it early-maps one page at a time, compares signatures, reads table length at signature+4, checks that the table stays below the scan limit, records the physical address, reserves the aligned length with memblock, logs the address, and unmaps the last page.

State and persistence behavior: Sets global `ibft_phys_addr` and reserves the firmware table memory in memblock. It does not alter table contents.

Dependencies and integration points: Depends on early memremap, memblock, EFI boot detection, architecture low-memory constants, and `iscsi_ibft.c`, which later maps `ibft_phys_addr` to virtual memory.

Risks and test signals: Signature/length probing trusts low memory contents enough to reserve a region. Page boundary mapping must remain correct when a signature is near the end of a page. Test BIOS boot with legacy iBFT, UEFI skip behavior, VGA gap skip, invalid lengths beyond 1 MiB, and memblock reservation.
