<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/fw_formats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/fw_formats.h

## Purpose
Defines firmware image header/trailer offsets, lengths, magic values, versions, CRC positions, and payload metadata for SFC/AMD firmware update formats recognized by the driver.

## Important APIs, types, and functions
- EF10 reflash header/trailer constants for magic, version, firmware type/subtype, payload size, header length, and trailer CRC.
- EF100 SmartNIC image constants for magic, version, header length, partition type/subtype, payload size, CRC, and minimum length.
- EF100 SmartNIC bundle constants for magic, version, bundle type/subtype, header length, CRC, and total fixed header length.

## Control flow
No executable control flow exists. Consumers use constants to scan firmware byte streams, identify candidate headers, and validate checksums before issuing firmware update operations.

## State and persistence behavior
No state is stored. The constants describe on-disk or in-memory firmware blob layouts.

## Dependencies and integration points
Designed for firmware update parsing code in the SFC driver. Comments explain that recognition must validate checksum fields because magic values are at differing offsets and signed/package headers may prepend data.

## Risks and test signals
Risks include stale offsets relative to firmware packaging changes, false-positive header detection if CRC validation is incomplete, and endian/length mistakes. Test signals are firmware parser unit tests with EF10 reflash, EF100 image, EF100 bundle, signed/prepended payloads, bad CRC, bad version, and truncated data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/fw_formats.h -->
