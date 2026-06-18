# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/desc.h

## Purpose
`desc.h` defines the packed hardware DMA descriptor layouts and bit fields used by ath5k TX/RX descriptor setup and status parsing. It documents the differences between AR5210/AR5211 2-word TX descriptors, AR5212 4-word TX descriptors, and common RX descriptors.

## Important APIs, types, and constants
- RX descriptor structs: `struct ath5k_hw_rx_ctl`, `struct ath5k_hw_rx_status`, `struct ath5k_hw_all_rx_desc`.
- TX descriptor structs: `struct ath5k_hw_2w_tx_ctl`, `struct ath5k_hw_4w_tx_ctl`, `struct ath5k_hw_tx_status`, `struct ath5k_hw_5210_tx_desc`, `struct ath5k_hw_5212_tx_desc`.
- Unified descriptor: `struct ath5k_desc` with `ds_link`, `ds_data`, and a union for TX/RX hardware-specific payload.
- Bit definitions for RX length/status/rate/RSSI/antenna/timestamp/key/PHY/MIC errors across 5210/5211 and 5212.
- Bit definitions for TX frame length, buffer length, key index, frame type, antenna, interrupt, RTS/CTS, no-ack, VEOL, txpower, retries, rates, final status, retry counters, sequence, ACK RSSI, and antenna.
- Public descriptor flags: `AR5K_RXDESC_INTREQ`, `AR5K_TXDESC_CLRDMASK`, `NOACK`, `RTSENA`, `CTSENA`, `INTREQ`, and `VEOL`.

## Control flow and integration
`desc.c` uses these definitions to encode control words before handing descriptors to hardware and to decode completion status after hardware DMA. `base.c` allocates arrays of `struct ath5k_desc`, links them into RX/TX/beacon rings through `ds_link`, and stores data-buffer physical addresses in `ds_data`. The hardware reads control fields for transmit/receive operations and writes status fields on completion.

## State and persistence behavior
The structures in this file describe DMA-coherent runtime memory. Hardware and driver share ownership of descriptor fields, so the exact packed layout and 4-byte alignment are part of the hardware ABI. There is no persistent storage; descriptor contents are recreated during allocation, reset, RX refill, TX enqueue, and beacon setup.

## Dependencies
This header relies on fixed-width integer types and kernel packing/alignment attributes supplied by includers. Semantic use depends on `ath5k.h` register helper macros, `desc.c`, and hardware generation state.

## Risks and edge cases
- Any layout, packing, alignment, or bit-mask change can break hardware DMA.
- Several fields differ by MAC generation, including antenna encoding, key index width, frame type location, timestamp width, and error bits.
- Some comments indicate historical ambiguity, such as retry count naming and AR5210 timestamp interpretation.
- PHY error code bits overlay key-index fields on AR5212, so parsers must branch on error state before interpreting key metadata.
- Endianness and DMA coherency assumptions must match the platform and descriptor initialization paths.

## Test signals
Descriptor tests are mostly integration-level: successful RX/TX DMA on AR5210, AR5211, and AR5212 hardware; correct RSSI/rate/key/error status in mac80211; no corrupted descriptor dumps; stable operation on big-endian builds; no queue hangs after beacons or MRR traffic; and no invalid memory accesses under high RX/TX load.
