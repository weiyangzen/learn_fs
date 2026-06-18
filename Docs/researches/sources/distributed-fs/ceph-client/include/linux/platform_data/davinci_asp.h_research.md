
# sources/distributed-fs/ceph-client/include/linux/platform_data/davinci_asp.h

## Purpose
This header describes TI DaVinci McASP audio serial port platform data. It feeds board-specific DMA offsets, SRAM use, serializer layout, TDM slot counts, and clocking modes into the McASP audio driver.

## Important APIs And Types
`struct davinci_mcasp_pdata` includes TX/RX DMA offsets, EDMA event queues, SRAM playback/capture sizes and pool, channel-combine mode, `i2s_accurate_sck`, TDM slot counts, operation mode, serializer count and directions, hardware version, DMA event watermarks, and explicit TX/RX DMA channels. Constants enumerate McASP hardware versions, inactive/TX/RX serializer modes, and IIS/DIT operation modes. `snd_platform_data` aliases this structure for legacy users.

## Control Flow, State, And Persistence
The header has no executable control flow. During probe, the audio driver reads this data to configure serializers, DMA channels, SRAM buffering, and bit-clock behavior. State is board/static hardware description plus runtime audio stream configuration derived from it.

## Dependencies And Integration Points
It depends on `linux/genalloc.h` for SRAM pools and integrates with ALSA SoC, EDMA, DaVinci/OMAP platform code, and board wiring that decides serializer direction and clocking.

## Risks And Test Signals
Risks include left/right channel swaps when channel combine changes behavior, underruns if DMA queues or event thresholds are wrong, incorrect serializer direction, and clock accuracy problems with asymmetric frame sync. Test signals include playback/capture on all serializers, TDM slot mapping, underrun recovery, DMA channel allocation, and I2S bit-clock/frame-sync measurements.
