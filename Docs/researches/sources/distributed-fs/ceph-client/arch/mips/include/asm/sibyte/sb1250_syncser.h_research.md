<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_syncser.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_syncser.h

Purpose: Defines control, clocking, DMA, status, and sequencer-table bits for the SB1250 synchronous serial block, including HDLC/CRC-oriented operation.

Important APIs/types/functions: Mode flags `M_SYNCSER_CRC_MODE`, `M_SYNCSER_MSB_FIRST`, `V_SYNCSER_FLAG_NUM`, `M_SYNCSER_HDLC_EN`, loopback flags; clock/interface flags `M_SYNCSER_RXCLK_EXT`, `V_SYNCSER_RXSYNC_DLY`, `M_SYNCSER_TXCLK_EXT`; command bits `M_SYNCSER_CMD_RX_EN`, `M_SYNCSER_CMD_TX_EN`, reset and pause bits; DMA bits `M_SYNCSER_DMA_RX_EN`, `M_SYNCSER_DMA_TX_EN`; status bits for CRC, abort, overrun, sync, descriptor, high/low-watermark, and sequencer-entry macros.

Control flow: Drivers use the masks to configure framing and line timing, reset RX/TX engines, enable command and DMA paths, and react to status interrupts. Sequencer entries describe byte/strobe/count/last behavior for programmed serial waveforms.

State and persistence: State lives in device registers, DMA descriptors, watermarks, and sequencer table entries. The header does not allocate state but exposes flags that enable DMA engines, clear or reset FIFOs, and report underrun/overrun and frame-boundary conditions.

Dependencies and integration points: Depends on `sb1250_defs.h`. It integrates with platform serial or WAN-style drivers that own register base addresses and DMA descriptor management.

Risks: Incorrect clock polarity, sync delay, or byte-order flags can make line protocols silently fail. RX/TX reset and DMA-enable bits interact with descriptor ownership, so ordering errors may lose frames. `V_SYNCSER_FLAG_NUM` omits an `(x)` parameter in the macro body definition, a legacy typo that can break new use.

Test signals: Compile coverage plus loopback, DMA RX/TX, CRC-error, abort, underrun/overrun, and sequencer waveform tests are the useful signals.

Source read size: 133 lines, 4482 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sibyte/sb1250_syncser.h -->
