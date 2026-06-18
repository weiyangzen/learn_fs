# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_base.h

## Purpose
`igc_base.h` declares base helper functions and defines advanced TX/RX descriptor layouts and SRRCTL bit helpers for the I225/I226 driver.

## Important APIs, Types, And Functions
The header declares `igc_rx_fifo_flush_base()`, `igc_power_down_phy_copper_base()`, `igc_is_device_id_i225()`, and `igc_is_device_id_i226()`. It defines `union igc_adv_tx_desc`, `struct igc_adv_tx_context_desc`, `union igc_adv_rx_desc`, advanced TX command/timestamp bits, `IGC_RAR_ENTRIES`, and SRRCTL field macros such as `IGC_SRRCTL_BSIZEPKT()`, `IGC_SRRCTL_BSIZEHDR()`, and `IGC_SRRCTL_DESCTYPE_ADV_ONEBUF`.

## Control Flow
There is no direct control flow. The descriptor definitions are consumed by TX/RX paths, and the declared helpers are implemented in `igc_base.c`.

## State And Persistence
No software state is stored. Descriptor layouts define the DMA contract between driver memory and hardware. SRRCTL macros define how RX buffer sizing and descriptor type are persisted in hardware registers.

## Dependencies And Integration Points
The header is included by base and main driver code. It depends on Linux endian types and bitfield helpers made available through includers. It complements `igc.h`, which provides descriptor accessors and ring/adapter state around these layouts.

## Risks
Descriptor structures must match hardware byte-for-byte. Incorrect command bits can break timestamping, VLAN insertion, checksum offload, TSO, or descriptor writeback. SRRCTL helper units are encoded in KB or 64-byte granularity; callers must pass sizes that match those expectations.

## Test Signals
Compile tests catch type visibility issues. Runtime tests include TX/RX traffic, VLAN/TSO/checksum offloads, PTP TX timestamp descriptor selection, and RX buffer-size configuration across MTUs.
