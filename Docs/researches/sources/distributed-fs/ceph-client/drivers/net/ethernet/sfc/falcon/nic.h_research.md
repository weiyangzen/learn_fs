# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/nic.h

## Purpose
`nic.h` is the Falcon-specific internal interface layered on top of `net_driver.h`. It declares Falcon revision constants, event/descriptor helpers, PHY type IDs, board and SPI data structures, Falcon hardware statistics, Falcon NIC-private state, data-path wrappers, Falcon architecture operation prototypes, interrupt/global resource helpers, register tests, stats helpers, and event generation.

## Important APIs, Types, And Functions
Inline helpers include `ef4_nic_rev()`, `ef4_nic_is_dual_func()`, `ef4_event()`, `ef4_event_present()`, `ef4_tx_desc()`, `ef4_tx_queue_partner()`, `ef4_nic_may_push_tx_desc()`, and `ef4_rx_desc()`. Board and hardware-private types include `struct falcon_board_type`, `struct falcon_board`, `struct falcon_spi_device`, and `struct falcon_nic_data`. The file exports `falcon_a1_nic_type` and `falcon_b0_nic_type`, wrappers that dispatch TX/RX/event operations through `efx->type`, and prototypes for Falcon architecture queue/event/filter/interrupt/reset/stat functions.

## Control Flow
The inline dispatch wrappers are used by generic driver code to call the active NIC type's queue and event operations without exposing the whole vtable at every call site. Event presence checks treat all-ones dwords as empty and avoid a single 64-bit comparison because event DMA writes may not be atomic. TX push eligibility clears `empty_read_count` and only allows a descriptor push when the NIC-visible queue was empty and exactly one descriptor is pending, avoiding known Falcon/Siena push hazards.

## State And Persistence
`struct falcon_nic_data` persists Falcon-private hardware state: optional secondary PCI function, board data, hardware stats array, stats-disable nesting, pending stats DMA, stats timer, SPI flash/EEPROM descriptors, SPI and MDIO locks, and whether XMAC polling is required. Descriptor helpers expose persistent DMA rings owned by TX/RX queue structures. Board/SPI structures persist per-board peripheral and NVRAM information.

## Dependencies And Integration Points
The header depends on timestamping, I2C bit-bang APIs, `net_driver.h`, and `efx.h`. It integrates generic driver code with Falcon-specific implementations in files such as queue/event/filter/MAC/SPI/board code, PHY drivers, and ethtool register/stat logic. PHY type constants connect probe-time hardware identification to operation tables in `phy.h` and PHY implementation files.

## Risks
The event-present algorithm relies on the event-clearing convention that both dwords are all ones and on valid events never having all ones in either dword. TX push logic is a latency optimization with hardware bug constraints; changing empty-count semantics can reintroduce lost or unsafe pushes. Many prototypes are hardware-facing and require callers to hold the correct locks or be in the correct lifecycle phase, but those requirements are spread across implementation files.

## Test Signals
Signals include event queue polling and clearing correctness, TX push counters and low-latency single-packet behavior, RX/TX descriptor ring indexing, Falcon A dual-function behavior, SPI flash/EEPROM detection, board initialization, Falcon filter operations, interrupt tests, DMA queue flushes, register self-tests, and hardware stats monotonicity via `ef4_update_diff_stat()`.
