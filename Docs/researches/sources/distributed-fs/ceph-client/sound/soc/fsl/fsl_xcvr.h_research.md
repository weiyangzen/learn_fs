# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_xcvr.h

## Purpose
Private register map and bitfield header for the NXP/Freescale XCVR digital audio block. It describes the SPDIF, ARC, and eARC transceiver register layout, FIFO sizing, IRQ bits, channel-status encodings, PHY access registers, and PLL/GP-PLL controls used by the corresponding DAI driver.

## APIs, Types, and Functions
This header exports macros only. Important groups are `FSL_XCVR_MODE_*`, FIFO constants such as `FSL_XCVR_FIFO_SIZE`, top-level register offsets from `FSL_XCVR_VERSION` through `FSL_XCVR_DEBUG_REG_1`, RX/TX datapath registers, channel status registers, `FSL_XCVR_IRQ_*` masks, PHY AI register controls, PLL register offsets, PHY control bits, IEC60958 channel-status sample-rate and channel-count encodings, and GP PLL numerator/denominator/divider masks.

## Control Flow, State, and Persistence
There is no executable control flow or persistent object state. Runtime state is held by the C driver that includes this header, while this file defines the fixed hardware contract: which bits reset command/data paths, disable DMA directions, select SPDIF/ARC/eARC mode, program watermarks, acknowledge channel/user-data updates, control PLL/PHY power, and encode channel status.

## Dependencies and Integration
The file assumes Linux bit helpers such as `BIT()` and `GENMASK()` are available before or through including contexts. It integrates with the XCVR platform driver, ALSA DAI setup, DMA configuration, interrupt handling, eARC firmware/PHY management, and IEC channel-status programming.

## Risks and Test Signals
Risks are register drift against SoC reference manuals, fragile ternary helper macros where `t` selects TX versus RX bits, and incorrect channel-status constants causing receiver compatibility problems. Test signals are clean compile with the XCVR driver, SPDIF/ARC/eARC playback and capture, FIFO watermark DMA behavior, IRQ status/clear handling, PLL lock and PHY enable sequencing, and channel-status sample-rate validation on external sinks.
