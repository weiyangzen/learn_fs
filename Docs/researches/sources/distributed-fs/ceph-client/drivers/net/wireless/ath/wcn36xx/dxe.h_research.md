# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.h

## Purpose
Defines the WCN36xx DXE DMA engine register map, descriptor control bits, channel defaults, descriptor-ring structures, buffer-pool structures, and public DXE entry points used by the mac80211-facing driver. It is the shared contract between `dxe.c`, TX/RX code, and the platform MMIO resources mapped by `main.c`.

## Important APIs, Types, and Functions
The header declares descriptor control macros for valid/EOP/BD handling, host-to-BMU and BMU-to-host transfer types, queue source/destination selection, interrupt enable, endianness, priority, BMU threshold, and template index fields. Composite descriptor controls include `WCN36XX_DXE_CTRL_TX_L`, `WCN36XX_DXE_CTRL_TX_H`, RX controls, and split BD/SKB TX controls. Channel control defaults `WCN36XX_DXE_CH_DEFAULT_CTL_RX_L`, `RX_H`, `TX_H`, and `TX_L` encode the per-channel mode registers.

Key types are `struct wcn36xx_dxe_desc`, the hardware-visible packed descriptor; `struct wcn36xx_dxe_ctl`, the software ring node that tracks descriptor, SKB, BD CPU/DMA addresses, and ring order; `struct wcn36xx_dxe_ch`, the per-channel descriptor ring and register configuration; and `struct wcn36xx_dxe_mem_pool`, the DMA pool backing BD headers. Public entry points include `wcn36xx_dxe_allocate_mem_pools`, `wcn36xx_dxe_alloc_ctl_blks`, `wcn36xx_dxe_init`, `wcn36xx_dxe_init_channels`, `wcn36xx_dxe_tx_frame`, `wcn36xx_dxe_rx_frame`, `wcn36xx_dxe_tx_flush`, and `wcn36xx_dxe_tx_ack_ind`.

## Control Flow and State
This file has no executable control flow, but it describes the DXE runtime pipeline. TX low/high channels move host descriptors and SKB payloads into BMU work queues, while RX low/high channels move BMU packets back to host buffers. The descriptor-count enum fixes ring depths: 128 TX-low, 10 TX-high, 512 RX-low, and 40 RX-high descriptors. `struct wcn36xx_dxe_ch` stores head/tail control blocks protected by its spinlock, the DMA allocation base, descriptor count, work-queue number, control words for BD and SKB descriptors, and register offsets used by the implementation.

## Dependencies and Integration Points
Depends on `wcn36xx.h` for the main device type and indirectly on Linux DMA, SKB, and spinlock types. `main.c` allocates resources and calls DXE start/stop from mac80211 `.start`, `.stop`, `.tx`, and `.flush` paths. `txrx.c` supplies TX BD format, while `dxe.c` consumes the register constants to program `wcn->dxe_base` and CCU interrupt routing. SMSM bits `WCN36XX_SMSM_WLAN_TX_ENABLE` and `WCN36XX_SMSM_WLAN_TX_RINGS_EMPTY` tie the DMA rings to Qualcomm shared-state signaling.

## Risks and Test Signals
The constants are a hardware ABI: wrong bit positions, ring sizes, queue numbers, or channel offsets can deadlock DMA, corrupt frames, or lose interrupts. The `WCN36XX_DXE_WQ_TX_*` macros contain a TODO and branch on `is_pronto_v3`, so platform variants need explicit traffic testing. The software ring stores both CPU and DMA pointers, making DMA mapping lifetime and head/tail locking critical. Test signals include probe/start DMA initialization, sustained TX/RX on low and high queues, IRQ completion and error paths, TX flush during interface teardown, suspend/resume with IRQ masking, and Pronto versus Riva/Pronto-v3 platform coverage.
