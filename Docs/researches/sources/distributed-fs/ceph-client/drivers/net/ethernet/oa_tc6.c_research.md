# sources/distributed-fs/ceph-client/drivers/net/ethernet/oa_tc6.c

## Purpose
Reusable OPEN Alliance TC6 10BASE-T1x MAC-PHY SPI library. It provides control register access, direct PHY access through MDIO, MAC-PHY reset/configuration, an IRQ-driven SPI data thread, TX chunking, RX reassembly, and exported APIs for concrete SPI MAC-PHY netdev drivers.

## Important APIs, Types, And Functions
`struct oa_tc6` holds SPI/netdev/PHY/MDIO handles, control/data buffers, locks, one waiting and one ongoing TX skb, RX reassembly skb, kthread/waitqueue, TX credits, RX chunk count, and interrupt/error flags. Exported APIs: `oa_tc6_init()`, `oa_tc6_exit()`, `oa_tc6_start_xmit()`, register read/write helpers, and `oa_tc6_zero_align_receive_frame_enable()`.

## Control Flow
Init allocates state and buffers, sets SPI realtime mode, resets MAC-PHY, unmasks errors, registers MDIO, attaches the internal PHY, enables config sync, reads buffer status, starts a FIFO SPI kthread, requests IRQ, and sends an empty data chunk to clear reset IRQ state. Control transfers are serialized by mutex. Data transfers run in the kthread, using TX credits for skb chunks and empty chunks to clock out RX data, then processing received footers and payloads.

## State And Persistence
Runtime-only memory and MAC-PHY register state. TX state is `waiting_tx_skb`, `ongoing_tx_skb`, and `tx_credits`; RX state is `rx_chunks_available`, `rx_skb`, and `rx_buf_overflow`. No persistent storage.

## Dependencies And Integration Points
Depends on SPI, kthreads, waitqueues, phylib, MDIO, netdevice stats, and `<linux/oa_tc6.h>`. Concrete drivers call the exported init/xmit/exit and register helpers.

## Risks And Edge Cases
Only one waiting TX skb is accepted. TX linearization can fail or be expensive. Several stream/header/config errors are currently fatal. `oa_tc6_mdiobus_read()` stores a signed error in a bool. Exit disconnects PHY before stopping the thread, so caller teardown ordering matters.

## Test Signals
SPI echo validation, reset-complete polling, C22/C45 MDIO, PHY attach, IRQ wakeups, TX credit exhaustion/restart, RX frames across chunks, overflow recovery, zero-align enablement, and fatal footer error behavior.
