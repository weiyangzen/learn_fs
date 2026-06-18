# sources/distributed-fs/ceph-client/drivers/firmware/efi/embedded-firmware.c

Purpose: scans EFI boot-services code regions for known embedded peripheral firmware blobs on DMI-matched systems and makes matched blobs available to drivers.

Important APIs/types/functions: exports test namespace symbols `efi_embedded_fw_list` and `efi_embedded_fw_checked`, and exports `efi_get_embedded_fw()`. Main helpers are `efi_check_for_embedded_firmwares()` and `efi_check_md_for_embedded_firmware()`.

Control flow: `efi_check_for_embedded_firmwares()` iterates DMI tables such as `touchscreen_dmi_table`, skips empty descriptors, then scans each EFI memory descriptor of type `EFI_BOOT_SERVICES_CODE`. Each descriptor is memremapped, searched at 8-byte offsets for the descriptor prefix, verified by SHA-256 over the expected blob length, duplicated into kernel memory, and linked into `efi_embedded_fw_list`. Lookup later requires the scan-complete flag and returns data/size by firmware name.

State and persistence behavior: matched firmware blobs are copied into heap memory and retained in a global list for driver requests. The checked flag records that scanning has completed.

Dependencies and integration points: depends on DMI matching, EFI memory map descriptors, crypto SHA-256, memremap, and firmware consumers using `efi_get_embedded_fw()`.

Risks and test signals: assumptions are explicit: blobs are in boot-services code and aligned to 8 bytes. False positives are mitigated by prefix plus SHA-256. Test signals include DMI-matched hardware finding the expected blob, test firmware namespace checks, and `-ENOENT` before scan completion or for unknown names.
