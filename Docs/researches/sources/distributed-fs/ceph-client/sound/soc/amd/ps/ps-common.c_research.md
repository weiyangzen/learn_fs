# sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-common.c

## Purpose
This file implements revision-specific hardware callback tables for the common ACP6.3/ACP7.x PCI driver. It abstracts power-on, reset, interrupt enable/disable, deinit, pin-configuration decoding, SoundWire DMA IRQ threading, and runtime/system PM for ACP63 and ACP70-family hardware.

## Important APIs, Types, And Functions
The exported entry points are `acp63_hw_init_ops()` and `acp70_hw_init_ops()`, which populate `struct acp_hw_ops`. ACP63 helpers include `acp63_power_on()`, `acp63_reset()`, `acp63_init()`, `acp63_deinit()`, `acp63_get_config()`, `snd_acp63_suspend()`, `snd_acp63_runtime_resume()`, `snd_acp63_resume()`, and `acp63_sdw_dma_irq_thread()`. ACP70 equivalents include `acp70_power_on()`, `acp70_reset()`, `acp70_init()`, `acp70_deinit()`, `acp70_get_config()`, `snd_acp70_suspend()`, `snd_acp70_runtime_resume()`, `snd_acp70_resume()`, and `acp70_sdw_dma_irq_thread()`.

## Control Flow
Initialization powers on the ACP block through PGFSM polling, enables `ACP_CONTROL`, performs soft reset, clears or enables DSP low-power control, and enables external interrupts. Deinit disables interrupts, resets hardware, and returns the block to a low-power state. Pin configuration is decoded into `is_pdm_config` and `is_sdw_config`, which the PCI probe later combines with ACPI discovery. Suspend snapshots SoundWire pad keeper and pulldown state, checks active SoundWire enable registers, and either only gates DSP control for active SoundWire or fully deinitializes the ACP block. Resume either ungates DSP control or fully reinitializes and restores pad registers.

## State And Persistence Behavior
The file persists power-management recovery data inside `acp63_dev_data`: pad keeper state, pad pulldown state, and `sdw_en_stat`. SoundWire DMA interrupt state arrays are consumed in the threaded handler and cleared after `snd_pcm_period_elapsed()`. ACP70 additionally enables PME and host-wake interrupt masks when wake registers indicate a SoundWire wake source.

## Dependencies And Integration Points
It depends on `acp63.h` for register addresses, timeouts, masks, revision constants, stream counts, and `struct acp_hw_ops`. It is called only through the PCI parent driver and directly reaches the SoundWire DMA child platform device with `dev_get_drvdata(&adata->sdw_dma_dev->dev)`.

## Risks And Edge Cases
The suspend path treats enabled SoundWire links specially and skips full ACP deinit, so mismatched SoundWire enable status could leave registers un-restored. `acp63_sdw_dma_irq_thread()` and `acp70_sdw_dma_irq_thread()` assume `sdw_dma_dev` has been created and has driver data. ACP70 host wake enabling depends on wake-enable registers already being programmed. Config decoding is register-value based and silently ignores unknown `ACP_PIN_CONFIG` values.

## Test Signals
Test with ACP63 and ACP70 revisions, including PDM-only, SoundWire-only, and mixed pin configs. Validate readl-poll timeout paths, suspend/resume with inactive SoundWire requiring full reinit, suspend/resume with active SoundWire requiring pad restore, ACP70 PME wake, and correct period-elapsed delivery for every SoundWire DMA stream array.
