# sources/distributed-fs/ceph-client/include/sound/acp63_chip_offset_byte.h

## Purpose
`acp63_chip_offset_byte.h` is an AMD ACP 6.3 register offset map. It names byte offsets for DMA engines, address translation windows, clock/reset, always-on control, interrupts, audio buffers, I2S/TDM, Bluetooth/HS TDM, wake-on-voice PDM, SoundWire controllers, HDA-like command rings, and scratch registers.

## Important APIs, Types, and Functions
The file defines only macros. Major groups include `ACP_DMA_*`, `ACPAXI2AXI_ATU_*`, `ACP_SOFT_RESET`, `ACP_CONTROL`, `ACP_EXTERNAL_INTR_*`, `ACP_AUDIO{0,1,2}_{RX,TX}_*`, `ACP_I2STDM_*`, `ACP_WOV_*`, `ACP_SW0_*`, `ACP_SW1_*`, and `ACP_SCRATCH_REG_0`.

## Control Flow
No executable flow exists. ACP platform drivers use these offsets with a mapped MMIO base to reset hardware, configure DMA descriptors, set ring buffers and FIFO sizes, enable serial ports, service interrupts, read position counters, and control SoundWire command/response paths.

## State and Persistence Behavior
The header owns no software state. Values at these offsets are hardware state that persists while the ACP block is powered and may be reset by ACP soft reset, power-gating, or system suspend.

## Dependencies and Integration Points
It is standalone and intended for AMD ACP ASoC/PCI platform code. It integrates with regmap or raw MMIO helpers in drivers that know the ACP 6.3 base address and clock/power sequencing.

## Risks and Test Signals
Risks are offset drift from hardware documentation, wrong port instance selection, uppercase `0X` constants mixed with `0x`, and accidental use on a non-6.3 ACP IP. Test signals include MMIO smoke tests, DMA playback/capture position tracking, interrupt mask/status handling, suspend/resume, SoundWire bus bring-up, and comparing register offsets with generated hardware headers.
