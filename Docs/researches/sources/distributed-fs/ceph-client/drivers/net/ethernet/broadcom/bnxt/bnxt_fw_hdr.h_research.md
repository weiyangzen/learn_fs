# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_fw_hdr.h

## Purpose

`bnxt_fw_hdr.h` defines the on-file binary header and trailer formats used by BNXT firmware and microcode flashing paths. `bnxt_ethtool.c` uses these definitions to validate firmware image signatures, code type, device family, trailer metadata, and CRC placement before writing images to device NVM.

## Important APIs, types, and macros

- `BNXT_FIRMWARE_BIN_SIGNATURE` identifies APE-bin style firmware images.
- `BNXT_UCODE_TRAILER_SIGNATURE` identifies microcode/pre-boot trailer records.
- `enum SUPPORTED_FAMILY` names legacy Broadcom device families; `bnxt_flash_firmware()` currently requires `DEVICE_CUMULUS_FAMILY` for this driver path.
- `enum SUPPORTED_CODE` enumerates firmware code types such as bootcode, APE patch, KONG, BONO, and ChiMP patch. The flashing code maps NVM directory types to these values.
- `enum SUPPORTED_MEDIA` is a firmware-image metadata field.
- `struct bnxt_fw_header` describes the leading APE-bin header, including signature, flags, code type, device family, media, version string, and version bytes.
- `struct bnxt_ucode_trailer` describes the trailing microcode metadata, including RSA signature bytes, flags, version fields, directory type, trailer length, trailer signature, and CRC.

## Control flow role

The header is passive. `bnxt_flash_firmware()` casts firmware data to `struct bnxt_fw_header`, checks the signature/code type/device family, and validates the final CRC word. `bnxt_flash_microcode()` casts the end of the firmware data to `struct bnxt_ucode_trailer`, checks the signature, directory type, and trailer length, then validates CRC.

## State and persistence behavior

No runtime state is defined. These structures describe persistent firmware files and NVM payload metadata. Incorrect interpretation can affect whether persistent firmware is accepted or rejected before flashing.

## Dependencies and integration points

- Uses Linux fixed-width endian types such as `__le16` and `__le32`.
- Integrated by `bnxt_ethtool.c` flash paths and indirectly by ethtool `flash_device`.
- Tied to Broadcom firmware package/file format contracts, not to Linux kernel-internal persistence.

## Risks and edge cases

- Structures are not explicitly marked packed; the field layout relies on natural C layout matching the binary format. Current fields are byte arrays and little-endian integers arranged to avoid surprising padding, but format changes must be checked carefully.
- Firmware validation currently hard-codes accepted device family for APE-bin images; broader hardware support would require deliberate changes.
- CRC location is assumed to be the last 32 bits of the image, independent of the trailer's internal `chksum` field.

## Test signals

- Unit-style validation with known-good and malformed firmware buffers for short size, bad signature, wrong code type, wrong device family, bad trailer length, wrong directory type, and CRC mismatch.
- Build checks on 32-bit and 64-bit architectures for structure size/layout assumptions.
- Flash dry-run or firmware-loader tests should confirm each NVM directory type selects the expected header or trailer validation path.
