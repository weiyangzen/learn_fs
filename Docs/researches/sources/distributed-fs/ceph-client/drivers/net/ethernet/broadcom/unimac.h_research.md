# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/unimac.h

Purpose: compact register definition header for Broadcom UniMAC blocks. It names offsets and bit fields used to configure a UniMAC Ethernet MAC for transmit/receive enablement, link speed, promiscuous mode, flow control, CRC/pause handling, loopback, Energy Efficient Ethernet, VLAN tag handling, and FIFO/status controls.

Important APIs/types/functions: no functions or structures are defined. Important macros include `UMAC_CMD` with `CMD_TX_EN`, `CMD_RX_EN`, `CMD_SPEED_*`, `CMD_PROMISC`, `CMD_SW_RESET`, `CMD_AUTO_CONFIG`, loopback and pause bits; address and frame registers `UMAC_MAC0`, `UMAC_MAC1`, `UMAC_MAX_FRAME_LEN`; status/config registers `UMAC_MODE`, `UMAC_FRM_TAG0`, `UMAC_FRM_TAG1`; and EEE/FIFO control registers `UMAC_EEE_CTRL`, `UMAC_EEE_LPI_TIMER`, `UMAC_EEE_WAKE_TIMER`, `UMAC_PAUSE_CTRL`, `UMAC_TX_FLUSH`, `UMAC_RX_FIFO_STATUS`, and `UMAC_TX_FIFO_STATUS`.

Control flow: this is declarative hardware metadata. MAC setup code composes `UMAC_CMD` bits to reset, choose speed, enable TX/RX, set filtering and pause behavior, then uses the address, max-frame, tag, EEE, and FIFO registers during link changes or power-management transitions.

State and persistence behavior: the header defines volatile MMIO state only. There is no stored driver state and no persistence beyond the hardware register values programmed by the consuming driver.

Dependencies and integration points: intended for Broadcom Ethernet MAC drivers that use a UniMAC register block. It integrates with Linux netdev link setup, multicast/promiscuous configuration, pause/EEE configuration, and hardware reset paths in the corresponding implementation files.

Risks: bit definitions are shared hardware contracts; a wrong speed field, reset bit, or EEE bit can leave the MAC disabled, negotiating at the wrong speed, discarding control frames, or entering low-power states incorrectly. `CMD_SW_RESET_OLD` and `CMD_SW_RESET` indicate revision-specific reset behavior that callers must select carefully.

Test signals: validate with link-up/link-down transitions at 10/100/1000/2500 speeds, promiscuous and multicast filtering changes, pause-frame behavior, EEE enable/disable, loopback where supported, and FIFO status/flush behavior after reset.
