# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/asp2/bcmasp_intf_defs.h

Purpose: `bcmasp_intf_defs.h` is the per-interface register map for the Broadcom ASP2 driver. It defines offset formulas and bit fields for UniMAC, UMAC-to-forwarding-buffer, RGMII, TX SPB DMA/control/top, TX EPKT core, TX pause, RX EDPKT DMA/config, RX SPB, RX pause, and ring sizing.

Important APIs/types/functions: this header is macro-only. Major groups are `UMC_OFFSET()`, `UMC_CMD` and UniMAC MIB counters, `UMAC2FB_OFFSET`/`UMAC2FB_CFG`, `RGMII_OFFSET()` plus EPHY/OOB/port/LED controls, `TX_SPB_DMA_OFFSET()`, `TX_SPB_CTRL_OFFSET()`, `TX_EPKT_C_OFFSET()`, `RX_EDPKT_DMA_OFFSET()`, `RX_EDPKT_CFG_OFFSET()`, and constants `NUM_4K_BUFFERS`, `RING_BUFFER_SIZE`, `DESC_RING_COUNT`, `DESC_SIZE`, and `DESC_RING_SIZE`.

Control flow: the implementation uses these constants during interface resource mapping, MAC reset/init, link adjustment, TX/RX channel initialization, PHY power control, and statistics collection. For example, `UMC_CMD` speed/duplex/pause bits are updated from PHY link state, TX SPB offsets program descriptor DMA windows, and RX EDPKT offsets configure the streaming RX data ring and descriptor ring.

State and persistence: the header stores no state, but it describes where per-interface state resides in hardware. Ring sizing constants define the amount of coherent descriptor memory and streaming RX memory that `bcmasp_intf.c` allocates and programs.

Dependencies and integration points: it assumes Linux bit macros and is included by all ASP2 implementation files. It complements `bcmasp.h`, which defines core/global registers and structures, while this file provides per-port/per-channel register layout.

Risks: offset formulas depend on `port` and `channel` values parsed from device tree; invalid DT values can point an interface at wrong hardware windows. Ring constants are coupled to descriptor layout and RX buffer mode. Test signals include interface creation for each supported port/channel, TX/RX descriptor base/end/valid programming, RGMII/internal PHY mode switching, UniMAC MIB reads, and compile-time use across all ASP2 objects.
