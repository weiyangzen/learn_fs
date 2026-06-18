# sources/distributed-fs/ceph-client/sound/soc/dwc/local.h

## Purpose
`local.h` is the private interface for the DesignWare I2S ASoC driver. It defines register offsets/bitfields, hardware capability decoding macros, common constants, the shared device state structure, and conditional prototypes/stubs for the optional PIO PCM backend.

## Important APIs, Types, And Functions
Important definitions include common I2S registers (`IER`, `IRER`, `ITER`, `CER`, `CCR`, FIFO flush registers), per-channel register macros (`TER()`, `RER()`, `TCR()`, `RCR()`, `ISR()`, `IMR()`, FIFO threshold/status registers), component parameter registers, DMA control bits, parameter decoding macros such as `COMP1_TX_ENABLED()` and `COMP2_RX_WORDSIZE_0()`, and channel limits. `union dw_i2s_snd_dma_data` supports either platform-data DMA fields or DMAengine DAI data. `struct dw_i2s_dev` is shared by `dwc-i2s.c` and `dwc-pcm.c`.

## Control Flow
The header does not run code, but it defines the contract used by runtime paths. `dwc-i2s.c` programs registers and derives capabilities from these macros; `dwc-pcm.c` uses the shared PIO fields and FIFO register offsets. The `IS_ENABLED(CONFIG_SND_DESIGNWARE_PCM)` block selects real PIO function declarations or inline no-op/`-EINVAL` stubs.

## State And Persistence
`struct dw_i2s_dev` captures persistent per-device state: MMIO base, clock/reset, active count, capability/quirks, component parameters, cached audio config, FIFO/format parameters, DMA data, PIO mode and callbacks, TDM settings, RCU substreams, and software frame pointers. Hardware state itself lives in the MMIO register map described by the macros.

## Dependencies And Integration Points
The header depends on Linux clock/device/types headers, reset declarations through included users, ALSA PCM, DMAengine PCM, and public `sound/designware_i2s.h`. It is the local bridge between the core driver and optional PIO component.

## Risks And Edge Cases
Many register macros assume four register banks for up to eight channels, while constants expose `MAX_CHANNEL_NUM` as eight. PIO stubs compile successfully when the backend is disabled but cause runtime registration failure for IRQ/PIO-selected devices. Shared state fields are broad and mutable from both IRQ and PCM/DAI callbacks, so synchronization discipline must be maintained by users.

## Test Signals
Compile tests should cover both PIO-enabled and PIO-disabled configs. Driver tests should validate component-parameter decoding, register offset correctness, DMA data union use in platform-data and DT paths, TDM fields, and safe interaction of RCU substream fields between IRQ and PCM callbacks.
