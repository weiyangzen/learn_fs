# sources/distributed-fs/ceph-client/drivers/net/ethernet/sgi/meth.h

Purpose: hardware layout and bit definitions for the SGI O2 MACE Ethernet driver.

Important types/macros: defines TX/RX ring sizes and buffer offsets, `tx_status_vector`, `tx_packet_hdr`, `tx_cat_ptr`, `tx_packet`, `rx_status_vector`, and `rx_packet`. It enumerates MAC control bits, DMA control bits, RX FIFO pointer extraction, RX status/error masks, interrupt bits, TX status bits, TX command flags, MDIO busy/data masks, known PHY IDs, and `ADVANCE_RX_PTR()`.

State and integration: this header is consumed by `meth.c` to format descriptors and parse hardware status. It has no runtime state but its bitfields describe hardware-visible memory layout.

Risks and tests: C bitfield layout and endian assumptions are sensitive; descriptor definitions must match the MACE block. Test with real hardware or emulator RX/TX descriptor completion, plus build coverage on the SGI IP32 architecture.
