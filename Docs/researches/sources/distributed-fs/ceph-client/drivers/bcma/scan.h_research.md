# sources/distributed-fs/ceph-client/drivers/bcma/scan.h

Purpose: defines the BCMA scanner's physical base addresses and enumeration ROM bitfields. It is a private header consumed by `scan.c` and SoC host registration code.

Important definitions: `BCMA_ADDR_BASE` and `BCMA_WRAP_BASE` identify the standard SoC core and wrapper address ranges. `SCAN_ER_VALID`, `SCAN_ER_TAG`, `SCAN_ER_TAGX`, and tag constants classify EROM entries as component info, master port, address descriptor, or end. `SCAN_CIA_*` and `SCAN_CIB_*` masks decode core class, ID, manufacturer, master/slave ports, master/slave wrappers, and revision. `SCAN_ADDR_*` masks decode address descriptor size, type, port, 32-bit extension, and base address. `SCAN_SIZE_*` masks support explicitly sized descriptors.

Control flow role: this header has no executable flow, but its constants directly drive `bcma_erom_get_ci()`, `bcma_erom_get_addr_desc()`, and `bcma_get_next_core()`. A wrong mask changes how the scanner advances the EROM pointer and can turn valid cores into skipped components or invalid sequences.

State and persistence: no runtime state is defined. The values describe persistent hardware ROM formats and fixed SoC physical address conventions.

Dependencies and integration points: included by `scan.c` and `host_soc.c`; indirectly affects all BCMA bus registration because scanner output feeds `main.c`, PCI/SoC host ops, SPROM, and core driver initialization.

Risks: the comment on `SCAN_ER_TAGX` notes that bit 0x8 must be ignored for address tags; changing this would break address parsing. Constants assume 4 KiB alignment and 32-bit address descriptor layout. Test signals are indirect: chip scan should enumerate expected core IDs, revisions, wrappers, and addresses on known hardware, and malformed EROM should fail predictably rather than overrun.
