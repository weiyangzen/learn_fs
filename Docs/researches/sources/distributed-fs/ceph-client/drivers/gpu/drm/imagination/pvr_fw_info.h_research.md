# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_info.h

## Purpose
Defines the driver-side metadata format appended to PowerVR firmware binaries: section IDs, section types, firmware info header, layout entries, and device-info header.

## Important APIs, types, and functions
- `FW_BLOCK_SIZE` fixes firmware metadata alignment to 4 KiB.
- `PVR_FW_INFO_MAX_NUM_ENTRIES` limits layout table entries to 8.
- `enum pvr_fw_section_id` names META, MIPS, and RISC-V code/data/private/core/boot sections.
- `enum pvr_fw_section_type` classifies entries as code, data, coremem code, coremem data, or none.
- `struct pvr_fw_info_header` carries metadata version, layout dimensions, BVNC, page size, compatibility flags, firmware version, and device-info size.
- `struct pvr_fw_layout_entry` maps firmware virtual sections to base address, max size, allocation size, and allocation offset.
- `struct pvr_fw_device_info_header` sizes BRN, ERN, feature, and feature-parameter masks that follow it.

## Control flow
This file has no runtime control flow. `pvr_fw.c` interprets the layout described in the comment: original firmware image, device info, info header, then layout table in the final 4 KiB block.

## State and persistence
No mutable state is defined here. The structs describe on-disk firmware metadata that is retained by pointer in `pvr_dev->fw_dev` after validation.

## Dependencies and integration points
Used by the common firmware validator and by processor-specific loaders to identify sections. Its IDs must match firmware build tooling and the Rogue firmware ABI expected by the kernel driver.

## Risks
Any incompatible struct layout, enum value change, or version mismatch makes firmware unloadable. The maximum layout entry count constrains future firmware section growth. Device-info size and mask sizes are parsed from firmware and must remain well-formed.

## Test signals
Firmware validation logs for unsupported info version, format mismatch, wrong BVNC, unsupported firmware version, and malformed layout entries are the primary signals. Build tests should catch enum users when new processor sections are added.
