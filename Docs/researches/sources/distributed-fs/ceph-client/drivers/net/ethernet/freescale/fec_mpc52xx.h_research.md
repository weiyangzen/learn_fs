# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fec_mpc52xx.h

### Purpose
`fec_mpc52xx.h` describes the MPC5200 FEC hardware register block and bit definitions used by the MPC52xx Ethernet and MDIO drivers. It is a low-level register contract, not a public API.

### Important APIs, Types, And Functions
The main type is `struct mpc52xx_fec`, a full memory-map layout from `fec_id` through MAC, FIFO, DMA/status, and RMON/IEEE MIB counters. The header defines queue and buffer constants (`FEC_RX_BUFFER_SIZE`, `FEC_RX_NUM_BD`, `FEC_TX_NUM_BD`), reset/watchdog timings, MIB disable bit, interrupt event/mask bits, receive/transmit control bits, Ethernet control bits, MII management frame fields, FIFO status/control bits, reset control bits, transmit FSM CRC bits, and pause opcode constants. It also declares `extern struct platform_driver mpc52xx_fec_mdio_driver`.

### Control Flow
No executable flow is present. `fec_mpc52xx.c` uses the structure and constants to reset/configure the MAC, enable interrupts, program FIFO thresholds, update link mode, set MAC address and multicast filters, read statistics, and control RX/TX. `fec_mpc52xx_phy.c` uses the MII frame constants and `mii_speed` register to implement MDIO transfers.

### State, Persistence, And Dependencies
The structure maps hardware state directly through big-endian MMIO. The only dependency is `<linux/phy.h>` for the MDIO platform driver declaration context. Runtime persistence is hardware-defined; register state is reinitialized by probe/start/resume/reset paths.

### Integration Points
This header is shared only inside the MPC52xx FEC driver pair. The exported MDIO driver declaration lets `fec_mpc52xx.c` register the MDIO bus driver before the MAC driver when built together.

### Risks
Register offsets must match the MPC5200 reference manual; any field displacement corrupts all MMIO access. The structure contains reserved arrays to preserve offsets, so edits are risky. MII bit shifts/masks are used by both MAC and MDIO logic; incorrect values cause PHY access timeouts or wrong register access.

### Test Signals
Build tests should cover `CONFIG_FEC_MPC52xx` and optional `CONFIG_FEC_MPC52xx_MDIO`. Runtime signals include successful reset, MDIO read/write, FIFO setup, interrupt acknowledgement, MAC address programming, RMON/IEEE stat reads, and link duplex transitions.
