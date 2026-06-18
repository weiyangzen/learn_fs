# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_pci.h

Purpose: PCI identity constant catalog for AIC7xxx-supported Adaptec controllers and chips. It defines the 64-bit composed IDs and masks consumed by Linux PCI ID tables and the common PCI identity matcher.

Important APIs/types/functions: this header has no functions or structs; it exports macros such as `ID_ALL_MASK`, `ID_DEV_VENDOR_MASK`, `ID_9005_GENERIC_MASK`, `ID_9005_SISL_MASK`, `ID_AIC7850`, `ID_AHA_2940`, `ID_AIC7890`, `ID_AHA_29160`, `ID_AIC7899`, and many board-specific subsystem IDs. Each ID packs device, vendor, subsystem device, and subsystem vendor into the format produced by `ahc_compose_id()` in `aic7xxx_pci.c`.

Control flow role: `aic7xxx_osm_pci.c` uses these macros to build the kernel-facing `pci_device_id` table. `aic7xxx_pci.c` uses the same macros in `ahc_pci_ident_table` with masks and setup callbacks. Exact IDs match known boards; vendor/device masks permit generic chip probes; special masks exclude SISL/container RAID-style devices.

State and persistence: none. These are compile-time constants that determine probe eligibility and variant identification.

Dependencies and integration: included by both OS PCI glue and common PCI setup code. The constants must remain synchronized with Linux PCI matching macros such as `ID_C()`/`ID16()` and the composed-ID layout in `ahc_compose_id()`.

Risks: a wrong constant or mask can prevent a supported adapter from binding or cause the driver to bind hardware that needs different firmware/termination rules. Generic masks trade coverage for specificity, so ordering in `ahc_pci_ident_table` matters. Some names represent board families rather than single revisions, so feature setup must be validated in the matching C file.

Test signals: compile-time reference checks from both PCI tables, PCI modalias generation, boot probing on representative boards, negative tests for SISL/RAID IDs, and comparison against known device/subsystem ID inventories.
