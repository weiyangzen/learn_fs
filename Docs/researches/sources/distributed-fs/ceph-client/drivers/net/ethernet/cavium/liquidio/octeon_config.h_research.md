# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_config.h

## Purpose
Defines static configuration limits and structs for LiquidIO Octeon devices, including maximum device counts, queue counts, descriptor sizes, default RX/TX ring parameters, interrupt coalescing defaults, NIC interface limits, BAR1 mapping constants, dispatch table sizing, and PF/VF maximums.

## Important APIs, Types, and Functions
Key macros define `MAX_OCTEON_NICIF`, `MAX_OCTEON_DEVICES`, `MAX_OCTEON_LINKS`, CN6xxx and CN23xx IQ/OQ limits and defaults, `CN23XX_MAX_VFS_PER_PF`, `CN23XX_MAX_RINGS_PER_VF`, `MAX_TXQS_PER_INTF`, `MAX_RXQS_PER_INTF`, `MAX_IOQS_PER_NICIF`, BAR1 mapping constants, response-list count, opcode mask sizing, and possible queue/VF maxima. Config accessor macros such as `CFG_GET_IQ_MAX_Q`, `CFG_GET_OQ_REFILL_THRESHOLD`, `CFG_GET_NUM_TX_DESCS_NIC_IF`, and `CFG_SET_NUM_RX_DESCS_NIC_IF` centralize field access. Types include `enum lio_card_type`, `octeon_iq_config`, `octeon_oq_config`, `octeon_nic_if_config`, `octeon_misc_config`, and `octeon_config`.

## Control Flow
There is no direct execution. Initialization code in `octeon_device.c`, queue setup, and chip-specific modules use these constants to size rings, choose defaults, allocate arrays, and validate queue identifiers. `MAX_OCTEON_INSTR_QUEUES(oct)` and `MAX_OCTEON_OUTPUT_QUEUES(oct)` drive loops across active queue arrays.

## State and Persistence Behavior
`struct octeon_config` instances are static in memory and copied or referenced by chip-specific setup. These values determine persistent runtime allocation sizes for DMA rings, pending lists, output buffers, refill thresholds, and interface queue layouts for the device lifetime.

## Dependencies and Integration Points
Consumed by `liquidio_common.h`, `octeon_device.c`, `octeon_droq.c`, IQ setup, chip-specific CN6xxx/CN23xx code, and SR-IOV/representor logic. Constants must align with firmware queue assignment and hardware ring capabilities.

## Risks
Changing descriptor counts, buffer sizes, queue maxima, or bitfield widths can break DMA ring sizing, memory consumption, interrupt moderation, and PF/VF resource partitioning. `MAX_OCTEON_*_QUEUES` currently keys CN23xx PF separately from other devices, so VF behavior inherits the CN6xxx-side limit in the macro even though other code uses CN23xx VF config explicitly.

## Test Signals
Probe on CN6xxx, CN23xx PF, and CN23xx VF, queue setup with default and boundary descriptor counts, SR-IOV VF allocation limits, representor ifidx mapping, BAR1 console mapping, interrupt coalescing defaults, and static checks that array maxima cover all configured queues and VFs are useful validation.
