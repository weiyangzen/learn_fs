# sources/distributed-fs/ceph-client/sound/soc/stm/stm32_sai.c

Purpose: STM32 SAI parent platform driver. It owns the common SAI global register block, discovers SoC capabilities, configures synchronization between SAI sub-blocks, and populates child platform devices that implement the audio sub-block DAIs.

Important APIs and types: uses `struct stm32_sai_data` and `struct stm32_sai_conf` from `stm32_sai.h`. SoC configs describe version, FIFO size, S/PDIF/PDM support, no-DMA-burst behavior, and optional parent-clock lookup. Core helpers include `stm32_sai_pclk_enable/disable()`, sync client/provider configuration, `stm32_sai_set_sync()`, parent clock acquisition, probe, suspend, and resume.

Control flow: probe allocates state, maps MMIO, copies match-data config, gets bus clock for non-F4 variants, optionally gets `x8k` and `x11k` parent clocks, gets IRQ and optional reset, enables pclk to read hardware capability registers, overrides FIFO/SPDIF/version fields when hardware ID matches, disables pclk, stores `set_sync`, and calls `devm_of_platform_populate()` to create child subdevices. Sync configuration locates the provider platform device from a phandle node, writes client `SYNCIN`, then writes provider `SYNCOUT` while rejecting conflicting provider assignments. Suspend saves the global control register and selects sleep pins; resume restores it and selects default pins.

State and persistence: parent state includes base, pclk, optional parent clocks, IRQ, SoC config, saved global control register, and sync callback. Sub-block runtime state lives in `stm32_sai_sub.c`, outside this subset. The GCR is saved/restored across system sleep.

Dependencies and integration points: compatibles `st,stm32f4-sai`, `st,stm32h7-sai`, `st,stm32mp25-sai`; clock names `pclk`, `x8k`, `x11k`; optional reset; pinctrl sleep/default; child nodes populated by OF; and synchronization contracts with SAI sub-block drivers.

Risks: F4 config does not require pclk, but probe unconditionally calls `clk_prepare_enable(sai->pclk)` later; verify `pclk` is valid or optional for F4 in the shared header expectations. Sync provider lookup depends on provider driver data already being set, creating probe-order sensitivity. A provider already set to A or B rejects conflicting sync but does not reference count clients. Suspend assumes pclk can be enabled during system sleep callbacks.

Test signals: boot all supported compatibles, child population, hardware capability register detection, sync provider/client phandle order, conflicting sync output requests, suspend/resume GCR and pinctrl restoration, and parent clock acquisition for 8k/11k families.
