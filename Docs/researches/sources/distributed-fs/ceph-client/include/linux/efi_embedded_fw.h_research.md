# sources/distributed-fs/ceph-client/include/linux/efi_embedded_fw.h

Purpose: describes the EFI embedded firmware discovery interface used to locate firmware blobs baked into platform firmware and expose them by Linux firmware name.

Important APIs/types/functions: `EFI_EMBEDDED_FW_PREFIX_LEN`, private test-visible `struct efi_embedded_fw`, public match descriptor `struct efi_embedded_fw_desc`, `touchscreen_dmi_table`, and `efi_get_embedded_fw()`.

Control flow: platform-specific DMI matching supplies descriptors; EFI embedded firmware code scans firmware memory for entries matching prefix, length, and SHA256, registers found blobs, and consumers retrieve them by name through `efi_get_embedded_fw()`.

State/persistence: firmware data itself is persistent in EFI/platform firmware. Kernel runtime state is a list of discovered blobs with pointers and lengths. No file-backed persistence is introduced by this header.

Dependencies/integration: integrates DMI matching, firmware loader tests (`lib/test_firmware.c` is explicitly called out), and drivers that need fallback firmware for devices such as touchscreens.

Risks/test signals: risks are false-positive blob matches, stale SHA256/length descriptors, lifetime of firmware memory pointers, and disabled `CONFIG_EFI_EMBEDDED_FIRMWARE`. Test with DMI-matched and unmatched systems, valid/invalid hashes, duplicate names, and firmware-loader retrieval paths.
