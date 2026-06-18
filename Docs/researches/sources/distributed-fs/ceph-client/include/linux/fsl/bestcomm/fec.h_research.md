# sources/distributed-fs/ceph-client/include/linux/fsl/bestcomm/fec.h

Purpose: declares BestComm task wrappers and descriptor bits for MPC52xx FEC Ethernet transmit and receive DMA.

Important APIs and types: `struct bcom_fec_bd` contains status and skb physical address. TX status bits include transmit frame done, transmit CRC, and append bad CRC. RX status bits report last buffer, broadcast/multicast, length violation, non-octet alignment, CRC error, overrun, truncation, length mask, and aggregate error mask. Functions include `bcom_fec_rx_init()`, `bcom_fec_rx_reset()`, `bcom_fec_rx_release()`, `bcom_fec_tx_init()`, `bcom_fec_tx_reset()`, and `bcom_fec_tx_release()`.

Control flow: the FEC driver creates RX/TX tasks with FIFO address and queue lengths, queues skb buffers, checks descriptor status in IRQ/NAPI paths, resets tasks on link/device reset, and releases them during teardown.

State and persistence: runtime DMA ring state tracks skb ownership and hardware error/status bits. No persistent state is stored.

Dependencies and integration points: depends on `struct bcom_task`, BestComm engine, FEC Ethernet driver, DMA mapping, and network stack skb lifecycle.

Risks and test signals: risks include mishandling RX error bits, length-mask interpretation, skb DMA address lifetime, reset while descriptors are owned by hardware, and TX CRC flags. Tests should cover RX/TX traffic, malformed frames, ring wraparound, reset under load, DMA mapping failures, and link down/up.
