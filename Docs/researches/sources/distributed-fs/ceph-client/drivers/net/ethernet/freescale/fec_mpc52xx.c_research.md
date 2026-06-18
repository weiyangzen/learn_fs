# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx.c

### Purpose
`fec_mpc52xx.c` implements a separate Ethernet driver for the MPC5200/MPC52xx Fast Ethernet Controller. Unlike the modern `fec_main.c` driver, it uses the MPC52xx BestComm DMA engine and a big-endian register block described by `fec_mpc52xx.h`.

### Important APIs, Types, And Functions
The private state `struct mpc52xx_fec_priv` stores the net_device, duplex/speed/link state, control/RX/TX IRQs, MMIO register pointer, BestComm RX/TX tasks, a spinlock, message level, MDIO speed, optional PHY node, and seven-wire mode flag. Netdev operations are `mpc52xx_fec_open()`, `mpc52xx_fec_close()`, `mpc52xx_fec_start_xmit()`, `mpc52xx_fec_set_multicast_list()`, `mpc52xx_fec_set_mac_address()`, `mpc52xx_fec_tx_timeout()`, and `mpc52xx_fec_get_stats()`. Driver lifecycle functions are `mpc52xx_fec_probe()`, `mpc52xx_fec_remove()`, suspend/resume hooks, and module init/exit registering this driver plus the optional MDIO platform driver.

### Control Flow
Probe allocates an Ethernet device, maps the FEC control registers, initializes BestComm RX/TX tasks using FIFO register addresses, obtains control and BestComm task IRQs, reads a MAC address from DT or hardware registers, falls back to a random address if invalid, parses current speed/duplex and `phy-handle`, handles `fsl,7-wire-mode`, initializes hardware, resets stats, and registers the netdev. Open optionally connects to the PHY, requests three IRQs, resets BestComm tasks, allocates RX SKBs into the BestComm RX queue, enables DMA tasks, starts the FEC, and starts the netdev queue.

Transmit prepares a BestComm TX buffer descriptor, DMA maps the SKB data, submits it, timestamps in software, and stops the queue if the BestComm queue is full. The TX IRQ retrieves completed buffers, unmaps DMA, consumes SKBs, and wakes the queue. The RX IRQ loops completed RX buffers, drops errored frames, allocates a replacement SKB before handing up the completed one, unmaps DMA, strips the CRC, sets protocol, defers RX timestamp handling if needed, and calls `netif_rx()`. Control IRQ clears non-MII events and soft-resets the MAC on FIFO errors.

### State, Persistence, And Dependencies
State is volatile: MMIO registers, BestComm task rings, queued SKBs, PHY link state, and net_device stats. The driver depends on OF address/IRQ helpers, phylib/of_mdio, BestComm FEC task helpers, big-endian MMIO accessors, CRC32 multicast hashing, and the companion MDIO driver symbol when `CONFIG_FEC_MPC52xx_MDIO` is enabled.

### Integration Points
The module registers an OF platform driver for `fsl,mpc5200b-fec`, `fsl,mpc5200-fec`, and `mpc5200-fec`. It integrates with phylib through `of_phy_connect()`, with ethtool for message level/link settings, and with the BestComm subsystem for DMA queueing.

### Risks
The RX path allocates replacement SKBs under the RX interrupt path and drops packets on allocation failure. Reset paths run under spinlock and rebuild DMA queues, so BestComm queue state must stay consistent. There is no NAPI; heavy interrupt load can be expensive. Hardware register writes are endian-sensitive. Probe/open unwind paths involve several resources (mem region, ioremap, two BestComm tasks, three IRQs, PHY references), making error handling important.

### Test Signals
Test signals include OF probe on MPC5200-compatible nodes, MAC address fallback, open/close with and without PHY node, RX/TX traffic under stress, TX queue full/wakeup behavior, FIFO error reset recovery, multicast/promiscuous filters, stats counter reads/resets, suspend/resume while running, and optional MDIO-driver registration ordering.
