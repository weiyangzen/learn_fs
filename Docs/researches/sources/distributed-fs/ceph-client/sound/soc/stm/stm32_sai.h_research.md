# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai.h

## Purpose
`stm32_sai.h` is the shared register and parent-state contract for the STM32 SAI ASoC drivers. It names the global SAI register bank, sub-block A/B register offsets, hardware capability registers, bit fields for clocking/frame/slot/DMA/PDM/error handling, and the parent `struct stm32_sai_data` consumed by the sub-block implementation in `stm32_sai_sub.c`.

## Important APIs, Types, And Functions
The file exports register offsets such as `STM_SAI_GCR`, `STM_SAI_CR1_REGX`, `STM_SAI_FRCR_REGX`, `STM_SAI_SLOTR_REGX`, `STM_SAI_SR_REGX`, `STM_SAI_PDMCR_REGX`, and hardware identity registers. Bitfield helpers cover synchronization (`SAI_GCR_SYNCIN_MASK`, `SAI_XCR1_SYNCEN_MASK`), data size (`SAI_XCR1_DS_*`), master clock division (`SAI_XCR1_MCKDIV_*`), FIFO threshold/flush, frame length and active frame-sync length, slot enable masks, interrupt/status/clear bits, and PDM microphone delay fields. `enum stm32_sai_syncout` identifies no sync, sub-block A, or sub-block B sync output. `struct stm32_sai_conf` carries version, FIFO size, SPDIF/PDM support, DMA-burst limits, and an optional callback for parent clock selection. `struct stm32_sai_data` stores the parent platform device, MMIO base, bus and parent clocks, hardware config, IRQ, synchronization callback, and cached global configuration register.

## Control Flow
This header has no executable control flow. Its definitions drive the parent SAI instance and sub-block driver: probe code determines version/capabilities, sub-block callbacks use the CR1/CR2/FRCR/SLOTR fields to program PCM formats and clocks, IRQ paths use SR/IMR/CLRFR masks, and PDM/SPDIF support is gated by `STM_SAI_HAS_SPDIF_PDM()`.

## State And Persistence
The persistent state modeled here is hardware state in SAI registers plus the parent driver's `stm32_sai_data`. Register cache behavior is implemented in the C files; this header defines which bits are meaningful and how hardware variants change divider width or feature availability.

## Dependencies And Integration Points
The header depends on Linux bitfield helpers and is included by STM32 SAI implementation files. It integrates with platform-device state, the common clock framework, STM32 device-tree synchronization, regmap/MMIO access in the C files, and ASoC DMA/DAI code that ultimately programs these fields.

## Risks And Edge Cases
Divider masks depend on `STM_SAI_STM32F4` versus H7-style versions; using the wrong `version` yields invalid MCKDIV programming. PDM registers are present only on newer hardware and only for sub-block A in the sub-driver. The sync input max helper is tied to the two-bit GCR field and constrains device-tree `st,sync` indices. This header has no include guard, so it relies on normal one-time inclusion patterns.

## Test Signals
Useful validation is mostly indirect: build both F4 and H7 SAI drivers, probe SAI nodes with and without PDM/SPDIF, exercise internal and external synchronization properties, verify divider masks written for F4 versus H7, and check IRQ status/clear handling with overrun, underrun, frame sync, and clock-configuration error conditions.
