# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-legacy-common.c

## Purpose
`acp-legacy-common.c` provides common hardware operations for legacy/non-SOF AMD ACP ASoC platforms. It defines per-generation resources, IRQ handling, PDM/I2S parameter restoration, ACP power/reset init/deinit, machine-device selection, pin-configuration detection, and hardware-op initialization for ACP3.1, ACP6.x, ACP6.3, and ACP7.x.

## Important APIs, Types, And Functions
Exported resources include `rn_rsrc`, `rmb_rsrc`, `acp63_rsrc`, and `acp70_rsrc`. Exported functions include `acp_irq_handler()`, `acp_enable_interrupts()`, `acp_disable_interrupts()`, `restore_acp_pdm_params()`, `restore_acp_i2s_params()`, `acp_init()`, `acp_deinit()`, `acp_machine_select()`, `check_acp_config()`, and `acp31_hw_ops_init()`, `acp6x_hw_ops_init()`, `acp63_hw_ops_init()`, `acp70_hw_ops_init()`.

## Control Flow
IRQ handling reads one or two external interrupt status registers, scans `chip->stream_list` under the ACP spinlock, clears matching stream bits, and calls `snd_pcm_period_elapsed()`. Init powers on ACP through generation-specific PGFSM registers, enables ACP control, performs soft reset, and clears ACP7 zero-shutdown DSP control. Deinit resets and disables control or sets ACP7 DSP control. Config detection reads pin config registers, checks ACPI child PDM devices and `_WOV`, and marks I2S/PDM availability. Machine selection either registers an `acp-pdm-mach` platform device for legacy-only DMIC or finds an ACPI machine and registers its driver name.

## State And Persistence
State persists in `acp_chip_info`: resource pointer, base MMIO, stream list, lock, revision, flags, machine table, PDM/I2S config booleans, channel masks, TDM/format arrays, and selected machine platform device. Hardware state persists in ACP power, reset, interrupt, PDM, I2S, ring, FIFO, and clock registers.

## Dependencies And Integration Points
The file depends on `amd.h`, ACPI, PCI, `mach-config.h`, ASoC ACPI machine matching, ACP PCM/I2S/PDM drivers, and machine drivers registered by name. It exports symbols under namespace `SND_SOC_ACP_COMMON`.

## Risks And Edge Cases
IRQ handling calls period elapsed while holding a spinlock, relying on ALSA expectations. Machine selection returns 0 even if platform-device registration fails after warning. Pin-config interpretation is generation-specific and can misclassify hardware if BIOS values change. ACPI `_WOV` can override child-device evidence for PDM presence.

## Test Signals
Test ACP init/deinit timeout paths, IRQ delivery for active streams on one- and two-controller resources, PDM and I2S restoration after resume, machine selection with matching/missing ACPI machines, pin-config matrices per generation, `_WOV` overrides, and namespace/module dependency checks.
