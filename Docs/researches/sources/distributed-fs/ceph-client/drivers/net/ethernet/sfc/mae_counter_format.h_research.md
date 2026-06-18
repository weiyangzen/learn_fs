<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae_counter_format.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae_counter_format.h

## Purpose
Defines the version 2 EF100 MAE counter packet layout used to parse streamed action-rule, conntrack, and outer-rule counter updates.

## Important APIs, types, and functions
- Header word constants define a 160-bit header with version, identifier, header/payload offsets, index, count, and reserved fields.
- Payload word constants define a 128-bit entry with counter index, packet count, and byte count.
- Identifier values distinguish AR, CT, and OR counter packet types.

## Control flow
No executable code is present. Consumers use bit offsets, widths, byte offsets, and sizes to extract counter stream fields from RX packet data.

## State and persistence behavior
No state is stored. The constants describe wire-format packet contents delivered by firmware/hardware.

## Dependencies and integration points
Integrated with MAE counter streaming in `mae.c` and RX-side counter packet parsing elsewhere in the driver. The version constant must match firmware output from `MC_CMD_MAE_COUNTERS_STREAM_START`.

## Risks and test signals
Risks include format drift with firmware, incorrect 48-bit counter extraction, endian mistakes, or accepting unknown identifiers/versions. Test signals are parser tests with AR/CT/OR samples, wrap/large 48-bit counts, malformed offsets/counts, and mixed counter stream packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mae_counter_format.h -->
