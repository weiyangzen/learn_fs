# sources/distributed-fs/ceph-client/include/linux/mfd/davinci_voicecodec.h

Purpose: This header defines the TI DaVinci voice codec MFD core interface. It describes memory-mapped voice codec registers, interrupt and FIFO control bits, child cells, and shared parent state used by VCIF and CQ93VC child devices.

Important APIs, types, and constants: Register macros cover PID, control, interrupt enable/status/clear, emulation control, read/write FIFOs, FIFO status, test control, and codec-specific registers. Bit macros describe ADC/DAC reset, 8-bit/unsigned sample format, FIFO enable/clear/mode, interrupt masks, PGA gain, mute/digital attenuation, and power-all-on/off values. `enum davinci_vc_cells` names the VCIF and CQ93VC cells. `struct davinci_vcif` stores DMA channels and FIFO DMA addresses. `struct davinci_vc` stores the parent device, platform device, clock, MMIO base, regmap, MFD cells, and child VCIF data.

Control flow, state, and persistence: The parent driver maps hardware, enables the codec clock, initializes regmap, and registers two MFD child devices. Child audio drivers manipulate FIFO, interrupt, sample-format, and power fields. Runtime state is primarily in hardware FIFOs, interrupt status, and codec control registers; the C structs hold live resources and DMA routing.

Dependencies and integration points: The header depends on MFD core, clock, regmap, platform device, and DMA address types. It integrates with ALSA SoC codec/interface drivers and platform DMA channels.

Risks and test signals: Risks include FIFO overrun/underrun mask confusion, mismatched DMA addresses, clock enable ordering, and bit typo risk around `DAVINCI_VC_INT_WERROVF_MASKBIT`. Test signals include loopback audio capture/playback, interrupt storm/clear behavior, FIFO status under stress, runtime PM clock tests, and child cell probe ordering.
