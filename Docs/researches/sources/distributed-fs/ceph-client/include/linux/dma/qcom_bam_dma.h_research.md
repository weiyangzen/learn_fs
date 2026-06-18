<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom_bam_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/qcom_bam_dma.h

## Purpose
Defines Qualcomm BAM DMA command element layout and helpers for preparing register read/write command descriptors.

## Important APIs, Types, And Functions
`struct bam_cmd_element` contains little-endian command/address, data, mask, and reserved words. `enum bam_command_type` defines write and read commands. Helpers `bam_prep_ce_le32()` and `bam_prep_ce()` pack a 24-bit target address and 8-bit command into `cmd_and_addr`, set data, and set a full mask.

## Control Flow
Drivers allocate command elements, prepare them with a register address, command type, and data or destination address, then submit them through BAM DMA command paths.

## State And Persistence
State is the command descriptor contents consumed by BAM hardware. No persistence exists after command completion.

## Dependencies And Integration Points
Depends on endian conversion and BAM DMA hardware command element format. Integrates peripheral register programming with DMA command streams.

## Risks And Edge Cases
Only the low 24 bits of address are encoded; higher bits are truncated. Data must be in little-endian form when using `_le32`. The helper does not initialize `reserved`, so callers may need to clear descriptors before use.

## Test Signals
Tests should verify command/address packing, endian conversion, read and write command elements, mask value, high-address truncation behavior, and hardware execution of register writes/reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/qcom_bam_dma.h -->
