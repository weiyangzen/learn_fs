# subset-b-006416 Research

This grouped report covers the requested AMD ACP ASoC driver files under `sources/distributed-fs/ceph-client/sound/soc/amd/ps`, `raven`, `renoir`, and `vangogh`. Each section is delimited for reconciliation into the required source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/pci-ps.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/ps/pci-ps.c

## Purpose
This is the PCI parent driver for AMD ACP6.3, ACP7.0, ACP7.1, and ACP7.2 platforms. It owns the PCI BAR mapping, revision dispatch, top-level ACP initialization, interrupt dispatch, SoundWire discovery, PDM/DMIC platform-device creation, SoundWire DMA platform-device creation, and machine-driver registration.

## Important APIs, Types, And Functions
The central state is `struct acp63_dev_data`, allocated in `snd_acp63_probe()` and stored with `pci_set_drvdata()`. Probe uses `snd_amd_acp_find_config()`, `acp_hw_init_ops()`, `acp_hw_init()`, `get_acp63_device_config()`, `create_acp63_platform_devs()`, and `acp63_machine_register()`. IRQ entry points are `acp63_irq_handler()` and threaded `acp63_irq_thread()`. SoundWire-specific helpers include `acp_scan_sdw_devices()`, `amd_sdw_probe()`, `amd_sdw_exit()`, and `acp63_sdw_machine_select()`.

## Control Flow
Probe rejects non-ACP6.3/7.x revisions and configurations claimed by other AMD audio stacks, enables PCI, maps BAR0, initializes revision-specific hardware ops, requests a shared threaded IRQ, discovers PDM and SoundWire availability from ACP pin config, ACPI DMIC properties, `_WOV`, and SoundWire ACPI scan results, then registers platform children. PDM creates `acp_ps_pdm_dma` and `dmic-codec`; SoundWire calls `sdw_amd_probe()` then creates `amd_ps_sdw_dma`; a machine device is registered for either SoundWire match data or the local PDM machine. Remove reverses SoundWire, PDM, machine, hardware, runtime PM, PCI regions, and PCI enable state.

## State And Persistence Behavior
Persistent runtime state lives in `acp63_dev_data`: MMIO base, PCI revision, platform devices, ACP lock, subsystem IDs, PDM/SoundWire capability flags, SoundWire machine table, wake-event latches, and DMA interrupt status arrays. The IRQ handler acknowledges hardware status bits by writing the same bit back, records SoundWire DMA stream interrupt flags, and defers period-elapsed calls to the threaded handler through `acp_hw_sdw_dma_irq_thread()`. Runtime/system PM delegates to revision-specific ops through `acp_hw_suspend()`, `acp_hw_runtime_resume()`, and `acp_hw_resume()`.

## Dependencies And Integration Points
The driver integrates with Linux PCI, platform devices, runtime PM, ACPI, ASoC machine selection, AMD SoundWire core (`sdw_amd_probe`, `sdw_amd_exit`, `amd_sdw_scan_controller`), and AMD machine tables from `mach-config.h`. It depends on `acp63.h` for register offsets, revisions, masks, platform-data fields, and helper wrappers implemented in `ps-common.c`.

## Risks And Edge Cases
The probe intentionally continues if no PDM or SoundWire device is found, leaving only the initialized PCI device and PM state. IRQ handling assumes child platform devices and SoundWire manager platform devices exist before matching interrupt bits are delivered; malformed firmware could expose null paths. ACP70 wake handling uses per-manager latches and `pm_request_resume()`, so wake regression tests should include suspended SoundWire links. Error IRQ handling clears error registers but does not report per-manager SoundWire error details.

## Test Signals
Useful signals are successful module bind for PCI device `0x15e2` with expected revisions, child platform devices under `/sys/bus/platform/devices`, `dmesg` errors from platform registration paths, SoundWire machine selection logs with SSID, PDM capture period interrupts, SoundWire playback/capture period interrupts, and suspend/resume with SoundWire wake events. Kconfig coverage should include both `CONFIG_SND_SOC_AMD_SOUNDWIRE=y/m` and disabled SoundWire builds because this file has compiled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/pci-ps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-common.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-mach.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-mach.c

## Purpose
This is the simple ASoC machine driver for Pink Sardine DMIC capture. It connects the ACP PDM CPU DAI to the generic `dmic-codec` codec through the `acp_ps_pdm_dma` platform component.

## Important APIs, Types, And Functions
The file defines DAI link components with `SND_SOC_DAILINK_DEF()`, one `struct snd_soc_dai_link` named `acp63_dai_pdm`, one `struct snd_soc_card` named `acp63_card`, and a platform probe `acp63_probe()` that registers the card with `devm_snd_soc_register_card()`.

## Control Flow
The PCI parent registers a platform device named `acp_ps_mach` when DMIC is present without SoundWire. The platform probe attaches `acp63_card` to the platform device, associates null private machine data, and registers the card. The card has a single capture-only link named `acp63-dmic-capture`.

## State And Persistence Behavior
The only persistent state is the static card and DAI-link description. No runtime stream state, GPIO state, jack state, or codec clock state is maintained here. Power management delegates to `snd_soc_pm_ops` through the platform driver.

## Dependencies And Integration Points
It depends on the `acp_ps_pdm_dma.0` CPU/platform DAI provided by `ps-pdm-dma.c` and the generic `dmic-codec.0`/`dmic-hifi` codec platform device created by `pci-ps.c`. It includes `acp63.h` for local machine type declarations.

## Risks And Edge Cases
Because the card is static, concurrent multiple device instances would share one global card object; this matches typical single-ACP hardware assumptions. Registration fails if either the PDM DMA DAI or `dmic-codec` component is missing. No constraints are added here, so stream format constraints come from the PDM component and codec.

## Test Signals
Expected runtime signals are an ASoC card named `acp63`, one capture PCM for `DMIC capture`, successful bind of platform device `acp_ps_mach`, and no playback devices from this machine driver. Suspend/resume coverage should ensure `snd_soc_pm_ops` does not disturb the PDM DMA restore path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-mach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-pdm-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-pdm-dma.c

## Purpose
This platform driver implements the ACP6.3/ACP7.x PDM DMA capture component used for digital microphones. It exposes an ASoC component and DAI named `acp_ps_pdm_dma.0`, programs the PDM ring buffer and page table entries, manages PDM DMA start/stop, handles period interrupts through the PCI parent, and restores capture state after resume.

## Important APIs, Types, And Functions
Important entry points are `acp63_pdm_audio_probe()`, `acp63_pdm_dma_open()`, `acp63_pdm_dma_hw_params()`, `acp63_pdm_dai_trigger()`, `acp63_pdm_dma_pointer()`, `acp63_pdm_dma_close()`, `acp63_pdm_resume()`, `acp63_pdm_suspend()`, and `acp63_pdm_runtime_resume()`. Hardware helpers include `acp63_config_dma()`, `acp63_init_pdm_ring_buffer()`, `acp63_enable_pdm_clock()`, `acp63_start_pdm_dma()`, `acp63_stop_pdm_dma()`, and interrupt-mask helpers guarded by the parent ACP mutex.

## Control Flow
Probe maps the parent-provided MMIO resource, obtains the parent `acp63_dev_data` lock, registers the component and DAI, and enables runtime PM. Open allocates `struct pdm_stream_instance`, installs fixed capture hardware constraints, enables PDM interrupts, and records `capture_stream`. `hw_params` writes PTE entries for the runtime DMA buffer and sets ring-buffer address, size, and watermark. Trigger start programs channel count and decimation, snapshots the byte counter, and starts PDM DMA if not already active; stop checks status and stops/flushed DMA. Pointer reports ALSA position from the PDM linear position counter modulo buffer size.

## State And Persistence Behavior
Per-stream state is allocated in `runtime->private_data` with DMA address, page count, base MMIO pointer, and baseline byte count. Device state in `struct pdm_dev_data` keeps the capture substream and shared ACP lock. The module parameter `pdm_gain` is clamped to 0..3 and written into `ACP_WOV_MISC_CTRL` when enabling the PDM clock. Resume reprograms PTEs and ring buffer if a capture stream remains open, then reenables interrupts.

## Dependencies And Integration Points
It depends on the PCI parent for platform-device creation, MMIO resource, top-level IRQ dispatch, and parent `acp_lock`. The parent IRQ handler calls `snd_pcm_period_elapsed()` on `capture_stream` when `PDM_DMA_STAT` is observed. The machine driver `ps-mach.c` binds this DAI to `dmic-codec`.

## Risks And Edge Cases
Only 48 kHz stereo S32_LE capture is supported; unexpected channels return `-EINVAL`. Stop/start polling can return `-ETIMEDOUT`, which should propagate to ALSA trigger failures. The open path returns `-EINVAL` on allocation failure instead of `-ENOMEM`. Interrupt masking is shared with other ACP users, so lock coverage around `ACP_EXTERNAL_INTR_CNTL` is important. A stale `capture_stream` would cause period callbacks after close, but close clears it before freeing private data.

## Test Signals
Validate `arecord` at 48 kHz, 2 channels, S32_LE; invalid channel counts; period elapsed cadence; pointer monotonicity and wrap; suspend/resume while capture is open; runtime suspend/resume with no open stream; and `pdm_gain` values outside 0..3 clamping as expected in hardware register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-pdm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-sdw-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-sdw-dma.c

## Purpose
This file implements the common SoundWire PCM DMA platform component for ACP6.3, ACP7.0, ACP7.1, and ACP7.2. It maps ALSA PCM streams to SoundWire manager instances and ACP DMA channel registers, programs page tables/ring buffers/watermarks, enables or disables DMA channels, and restores active streams after system resume.

## Important APIs, Types, And Functions
The component callbacks are `acp63_sdw_dma_open()`, `acp63_sdw_dma_hw_params()`, `acp63_sdw_dma_trigger()`, `acp63_sdw_dma_pointer()`, `acp63_sdw_dma_close()`, and `acp63_sdw_dma_new()`. Probe/remove are `acp63_sdw_platform_probe()` and `acp63_sdw_platform_remove()`. Key helpers are `acp63_config_dma()`, `acp63_configure_sdw_ringbuffer()`, `acp63_sdw_get_byte_count()`, `acp63_sdw_dma_enable()`, `acp63_restore_sdw_dma_config()`, and `acp70_restore_sdw_dma_config()`. Static register tables describe ACP63 and ACP70 SDW0/SDW1 stream register layouts.

## Control Flow
Open finds the CPU DAI's `amd_sdw_manager`, copies DAI id to `stream_id`, copies manager instance to the private stream, and applies fixed 48 kHz two-channel playback/capture constraints. `hw_params` selects the correct register table and interrupt bit based on ACP revision and manager instance, stores the substream in the matching stream array, programs PTEs and ring buffer registers, enables the relevant external interrupt bit, and writes the period watermark. Trigger writes the stream's DMA enable register and polls the adjacent status register until it matches. Resume iterates every possible live stream in both manager instances, replays PTE/ring-buffer/watermark programming, and reenables all SDW DMA interrupt masks for the relevant revision.

## State And Persistence Behavior
Per-stream state in `struct acp_sdw_dma_stream` holds stream id, SoundWire instance, DMA address, page count, and baseline byte count. Device state in `struct sdw_dma_dev_data` holds the MMIO base, revision, parent lock pointer, and per-revision arrays mapping active stream ids to ALSA substreams. Pointer state is derived from ACP linear position counters. Interrupt status is not consumed here; the PCI parent and `ps-common.c` mark and process period interrupts using these substream arrays.

## Dependencies And Integration Points
It depends on SoundWire CPU DAI driver data (`struct amd_sdw_manager`), ACP PCI-created platform resources, `acp63.h` register definitions and stream constants, and ALSA/ASoC PCM callbacks. It is registered as platform driver `amd_ps_sdw_dma` and is used by SoundWire machine drivers selected by `pci-ps.c`.

## Risks And Edge Cases
Register selection is dense and revision-specific; incorrect stream id or manager instance can index the wrong table or return `-EINVAL`. ACP63 SDW1 supports only one TX and one RX stream while ACP70 SDW1 supports six, so tests must distinguish both. Interrupt mask writes in `hw_params` do not use the parent lock even though shared interrupt control registers are modified elsewhere. Trigger polling requires the status register to equal exactly the boolean enable value. Resume reenables broad DMA masks even if only some streams were active.

## Test Signals
Run playback and capture over SDW0 and SDW1 on ACP63 and ACP70-class hardware, validate period interrupts for all stream ids, check trigger timeout paths, verify pointer wrap behavior, and suspend/resume with multiple active SoundWire streams. Build coverage with SoundWire enabled is required, and runtime testing should confirm the parent IRQ thread sees stream arrays populated by this component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/ps/ps-sdw-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/amd/raven/Makefile

## Purpose
This Makefile wires Raven Ridge ACP3x legacy ASoC modules into Kbuild.

## Important APIs, Types, And Functions
It defines object lists for `snd-pci-acp3x`, `snd-acp3x-pcm-dma`, and `snd-acp3x-i2s`, then includes each object under `CONFIG_SND_SOC_AMD_ACP3x`.

## Control Flow
When the ACP3x Kconfig symbol is enabled, Kbuild compiles `pci-acp3x.o`, `acp3x-pcm-dma.o`, and `acp3x-i2s.o` into separate modules or built-in objects according to kernel build mode.

## State And Persistence Behavior
There is no runtime state. The file controls build inclusion and module composition only.

## Dependencies And Integration Points
The Makefile integrates the Raven PCI parent, PCM DMA component, and I2S DAI component as a coordinated driver set. Machine drivers are outside this directory or platform-specific selection.

## Risks And Edge Cases
All three objects are tied to one Kconfig symbol, so partial builds of only PCI or only I2S/DMA are not represented here. Build failures in register headers or shared declarations affect all three outputs.

## Test Signals
Use kernel build coverage with `CONFIG_SND_SOC_AMD_ACP3x=m` and `=y`, then confirm generated objects or modules include `snd-pci-acp3x`, `snd-acp3x-pcm-dma`, and `snd-acp3x-i2s`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x-i2s.c

## Purpose
This is the Raven ACP3x CPU DAI driver for I2S/TDM playback and capture. It configures DAI format, TDM slot format, sample resolution, I2S/BT instance selection, and stream start/stop registers.

## Important APIs, Types, And Functions
The DAI callbacks are `acp3x_i2s_set_fmt()`, `acp3x_i2s_set_tdm_slot()`, `acp3x_i2s_hwparams()`, and `acp3x_i2s_trigger()`, assembled into `acp3x_i2s_dai_ops`. The platform probe `acp3x_dai_probe()` maps a register resource and registers `acp3x_i2s_dai`.

## Control Flow
The PCI parent creates multiple `acp3x_i2s_playcap` devices for SP and BT TDM register windows. `set_fmt` selects I2S versus DSP_A/TDM mode. `set_tdm_slot` calculates the frame-format register value. `hw_params` obtains `struct acp3x_platform_info` from the card, selects playback or capture I2S instance, maps sample format to hardware sample length, optionally enables TDM and writes TX/RX format, then writes the sample length bits. Trigger start sets watermarks and ring-buffer size, enables the chosen TX/RX iterator/receiver register, and enables the matching IER; trigger stop clears enable bits and disables IER only when both playback and capture are inactive for that instance.

## State And Persistence Behavior
Driver state is `struct i2s_dev_data`, carrying TDM mode and format plus MMIO base. Stream-specific state in `struct i2s_stream_instance` is created by the DMA component and read here through `runtime->private_data`. The DAI driver does not allocate stream memory; it mutates fields such as `i2s_instance`, `xfer_resolution`, and `bytescount`.

## Dependencies And Integration Points
It depends on `acp3x.h` for register offsets, constants, read/write helpers, and `acp3x_platform_info`. It integrates tightly with `acp3x-pcm-dma.c`, which owns DMA buffer programming and substream registration, and with an ASoC card that sets card driver data to choose SP or BT instances.

## Risks And Edge Cases
The DAI assumes `runtime->private_data` was already installed by the DMA component. Capture supports only up to 48 kHz while playback supports up to 96 kHz. TDM register restore is handled in the DMA component resume path, so DAI and DMA state must stay synchronized. Unsupported formats and slot widths return `-EINVAL`.

## Test Signals
Exercise I2S and DSP_A formats, slot widths 8/16/24/32, SP and BT instances, playback/capture trigger transitions, and suspend/resume with TDM enabled. ALSA PCM tests should verify no IER remains enabled after both directions stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x-pcm-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x-pcm-dma.c

## Purpose
This platform driver implements Raven ACP3x PCM DMA for I2S/SP and BT playback/capture. It supplies the ASoC component callbacks for buffer allocation, DMA page-table programming, IRQ-driven period notifications, pointer reporting, runtime PM, and resume restore.

## Important APIs, Types, And Functions
Main functions are `i2s_irq_handler()`, `config_acp3x_dma()`, `acp3x_dma_open()`, `acp3x_dma_hw_params()`, `acp3x_dma_pointer()`, `acp3x_dma_new()`, `acp3x_dma_close()`, `acp3x_audio_probe()`, `acp3x_resume()`, `acp3x_pcm_runtime_suspend()`, and `acp3x_pcm_runtime_resume()`. The component driver is named `acp3x_rv_i2s_dma`.

## Control Flow
Probe consumes platform IRQ flags from the PCI parent, maps MMIO, registers the PCM component, requests the shared ACP IRQ, and enables runtime PM. Open allocates `struct i2s_stream_instance`, applies playback or capture hardware constraints, and stores MMIO in private data. `hw_params` obtains card platform info, records the substream in one of four device fields based on direction and SP/BT instance, computes pages, and calls `config_acp3x_dma()`. The IRQ handler checks BT/SP TX/RX threshold bits, acknowledges each matching bit, and calls `snd_pcm_period_elapsed()`. Resume replays DMA setup and sample-format/TDM registers for active streams.

## State And Persistence Behavior
`struct i2s_dev_data` persists active substream pointers for BT playback/capture and SP playback/capture plus TDM settings. Each stream private object persists DMA address, page count, instance, transfer resolution, and baseline byte count. Runtime suspend disables external interrupts; runtime resume reenables them. Close clears the active substream pointer but does not free the private `i2s_stream_instance`, which is a notable ownership issue compared with newer drivers.

## Dependencies And Integration Points
It depends on the Raven PCI parent for platform resources and IRQ flags, `acp3x.h` for register helpers and constants, the CPU DAI driver for format/trigger setup, and the card's `acp3x_platform_info` for instance routing.

## Risks And Edge Cases
The missing `kfree()` in `acp3x_dma_close()` can leak stream private data over repeated opens. The pointer helper in `acp3x.h` appears to OR high and low words rather than shifting high into the upper 32 bits, so long-running position values may be wrong. IRQ handling assumes active stream pointers are cleared before future interrupts for a stopped stream. A missing card platform info only prints `pinfo failed` but still continues to program DMA with whatever instance is in private data.

## Test Signals
Run repeated open/close leak detection, SP and BT playback/capture, IRQ threshold period notifications, pointer accuracy under long captures/playback, runtime suspend interrupt gating, and system resume with active TDM streams. KASAN/Kmemleak would be useful for close-path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x-pcm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x.h

## Purpose
This header provides Raven ACP3x register constants, memory-window layout, buffer limits, data structures, and inline MMIO/position helpers for the Raven PCI, I2S DAI, and PCM DMA drivers.

## Important APIs, Types, And Functions
It defines instance constants `I2S_SP_INSTANCE` and `I2S_BT_INSTANCE`, platform/device structures `struct acp3x_platform_info`, `struct i2s_dev_data`, and `struct i2s_stream_instance`, MMIO helpers `rv_readl()` and `rv_writel()`, and position helper `acp_get_byte_count()`.

## Control Flow
There is no standalone control flow, but the macros drive all register programming in the C files. `rv_readl()` and `rv_writel()` subtract `ACP3x_PHY_BASE_ADDRESS` because the included register header uses absolute offsets while drivers add offsets to an ioremapped BAR base.

## State And Persistence Behavior
The structures declared here define persistent runtime state for Raven: card-selected I2S instances, per-device TDM and active substream pointers, and per-stream DMA/position metadata. Buffer constants fix min/max ALSA buffer sizes to hardware-supported periods and period sizes.

## Dependencies And Integration Points
The header includes `chip_offset_byte.h` and `<sound/pcm.h>`, and is included by all Raven driver sources. `snd_amd_acp_find_config()` is not declared here because Raven's PCI driver does not use the shared machine-config helper.

## Risks And Edge Cases
`acp_get_byte_count()` combines high and low linear position registers with bitwise OR rather than shifting the high register by 32 bits; this risks wrong positions once the low counter wraps. The read/write helpers depend on absolute register definitions matching the fixed physical base. Any future BAR layout change would require revisiting the subtraction logic.

## Test Signals
Compile all Raven sources with this header, verify MMIO accesses target the intended BAR offsets, and test PCM pointer wrap over long-running streams. Static analysis should flag structure ownership and high/low counter composition issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/acp3x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/chip_offset_byte.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/raven/chip_offset_byte.h

## Purpose
This generated-style register header enumerates ACP3.0 absolute byte offsets for Raven hardware blocks, including DMA, AXI2AXI ATU, clock/reset, external interrupts, PGFSM, scratch SRAM, SoundWire-related registers, audio buffers, I2S/TDM, BT/TDM, Azalia, and ACP/Azalia page tables.

## Important APIs, Types, And Functions
It contains macro definitions only, all prefixed primarily with `mmACP_`, `mmSW_`, or `mmAudio_Az_`. There are no functions or data structures.

## Control Flow
No executable control flow exists. Driver code includes this file through `acp3x.h` and uses the macros to calculate register addresses for `rv_readl()` and `rv_writel()`.

## State And Persistence Behavior
The header itself has no state. It defines the persistent MMIO register layout that the driver uses to control DMA descriptors, ring buffers, linear position counters, interrupt control/status, power-gating state, and I2S/BT TDM registers.

## Dependencies And Integration Points
The offset values are absolute addresses based around the ACP3x physical base `0x1240000`, so the Raven helper subtracts `ACP3x_PHY_BASE_ADDRESS` to convert them to offsets from the mapped BAR. The Raven I2S and DMA code depends on audio-buffer and TDM register names from this file.

## Risks And Edge Cases
Because the macros are absolute and not relative BAR offsets, using them directly with `readl(base + macro)` without the subtraction helper would access the wrong address. The file contains many registers unused by the current Raven drivers; stale or incorrect definitions may go unnoticed without hardware access.

## Test Signals
Build-time signal is successful compilation of all Raven drivers. Runtime signals are correct register side effects for external interrupt enable/status, I2S/BT ring-buffer programming, and linear position counters. Hardware register tracing can validate that helper subtraction maps macros to expected BAR-relative offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/chip_offset_byte.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/pci-acp3x.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/raven/pci-acp3x.c

## Purpose
This is the Raven ACP3x PCI parent driver. It powers and resets the ACP3x block, reads the I2S pin configuration, creates child platform devices for I2S DMA and CPU DAIs, and owns top-level runtime/system PM and cleanup.

## Important APIs, Types, And Functions
The private parent state is `struct acp3x_dev_data`. Hardware helpers include `acp3x_power_on()`, `acp3x_reset()`, `acp3x_enable_interrupts()`, `acp3x_disable_interrupts()`, `acp3x_init()`, and `acp3x_deinit()`. PCI callbacks are `snd_acp3x_probe()`, `snd_acp3x_suspend()`, `snd_acp3x_resume()`, and `snd_acp3x_remove()`.

## Control Flow
Probe accepts only PCI revision `0x00`, enables PCI, requests BAR regions, maps BAR0, saves `ACP_PME_EN`, initializes hardware, reads `mmACP_I2S_PIN_CONFIG`, and when in I2S mode creates four platform devices: one `acp3x_rv_i2s_dma` with MMIO and IRQ resources and three `acp3x_i2s_playcap` DAI devices for SP/BT windows. It then enables runtime PM autosuspend. Suspend deinitializes ACP; resume reinitializes it.

## State And Persistence Behavior
Parent state stores MMIO base, audio mode, resources, child platform devices, and saved PME enable value. Power-on restores saved PME state because ACP power-on clears `ACP_PME_EN`. Platform children persist until remove or probe-error unwind.

## Dependencies And Integration Points
It depends on PCI device `0x15e2` class multimedia other, `acp3x.h` register helpers, and Kbuild entries in the Raven Makefile. It passes IRQ flags as platform data to the DMA component and MMIO resources to both DMA and DAI children.

## Risks And Edge Cases
The platform-device unwind loop unregisters all four child slots even after a partial registration failure, which may include uninitialized pointers. Probe silently ignores non-I2S pin modes after initializing hardware and PM. Runtime suspend returns 0 even if deinit failed. MSI is not used; IRQ is shared.

## Test Signals
Bind on Raven revision `0x00`, confirm four child platform devices in I2S mode, validate PME register restoration after power-on, runtime suspend/resume cycles, remove-path child unregistering, and non-I2S pin mode behavior. Probe-error injection around child registration is useful for unwind validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/raven/pci-acp3x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/Makefile

## Purpose
This Makefile wires Renoir ACP3x PDM/DMIC support into Kbuild.

## Important APIs, Types, And Functions
It defines object lists for `snd-rn-pci-acp3x`, `snd-acp3x-pdm-dma`, and `snd-acp3x-rn`. The PCI parent and PDM DMA component are built under `CONFIG_SND_SOC_AMD_RENOIR`; the machine driver is built under `CONFIG_SND_SOC_AMD_RENOIR_MACH`.

## Control Flow
Kbuild compiles `rn-pci-acp3x.o` and `acp3x-pdm-dma.o` when Renoir support is enabled, and separately includes `acp3x-rn.o` when the machine-driver symbol is enabled.

## State And Persistence Behavior
There is no runtime state. It controls module composition and dependency visibility only.

## Dependencies And Integration Points
The split between platform and machine Kconfig symbols allows the PDM DMA/PCI layer to exist independently from the Renoir DMIC ASoC card registration.

## Risks And Edge Cases
If `CONFIG_SND_SOC_AMD_RENOIR_MACH` is disabled while the PCI parent still creates `acp_pdm_mach`, the machine platform device may not bind. Object name `snd-acp3x-pdm-dma` is shared-looking with ACP3x naming but implemented by Renoir-specific source in this directory.

## Test Signals
Build with Renoir support as module and built-in, with machine-driver symbol both enabled and disabled, and verify expected module/object names are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/acp3x-pdm-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/acp3x-pdm-dma.c

## Purpose
This is the Renoir ACP3x PDM DMA capture driver for DMIC. It provides the ASoC component/DAI, programs PDM DMA buffers, handles PDM IRQ period notifications, and restores active capture state after runtime or system resume.

## Important APIs, Types, And Functions
Key callbacks are `acp_pdm_audio_probe()`, `acp_pdm_dma_open()`, `acp_pdm_dma_hw_params()`, `acp_pdm_dai_trigger()`, `acp_pdm_dma_pointer()`, `acp_pdm_dma_close()`, `acp_pdm_resume()`, `acp_pdm_runtime_suspend()`, and `acp_pdm_runtime_resume()`. Hardware helpers include `pdm_irq_handler()`, `config_acp_dma()`, `init_pdm_ring_buffer()`, `enable_pdm_clock()`, `start_pdm_dma()`, and `stop_pdm_dma()`.

## Control Flow
Probe reads IRQ flags from platform data, maps the ACP MMIO resource, gets the platform IRQ, registers component and DAI, requests the IRQ, and enables runtime PM. Open allocates stream private data, applies fixed 48 kHz stereo capture constraints, enables PDM interrupts, and records the capture substream. `hw_params` writes PTEs and ring-buffer/watermark registers. Trigger start sets channel count and decimation, snapshots byte count, and starts DMA if needed; trigger stop stops and flushes active DMA.

## State And Persistence Behavior
Device state in `struct pdm_dev_data` stores the IRQ, base pointer, and active capture stream. Per-stream state stores page count, DMA address, baseline byte count, and base pointer. The `pdm_gain` module parameter is clamped and written into `ACP_WOV_MISC_CTRL`. Resume restores PTEs/ring buffer when capture is open and reenables PDM interrupts.

## Dependencies And Integration Points
It depends on the Renoir PCI parent for platform resources, IRQ flags, and child creation, on `rn_acp3x.h` for constants and read/write helpers, and on `acp3x-rn.c` machine registration for the DMIC card path.

## Risks And Edge Cases
`disable_pdm_interrupts()` uses `ext_int_ctrl |= ~PDM_DMA_INTR_MASK` rather than clearing the bit with `&= ~`, which can set many unrelated interrupt bits; this is a significant risk. Open returns `-EINVAL` for allocation failure. Capture hardware advertises S32_LE in PCM hardware while the DAI capture formats include S24_LE and S32_LE, which may expose constraint mismatches. Only two-channel capture is accepted.

## Test Signals
Test 48 kHz stereo capture, unsupported channels/formats, interrupt mask state after close/runtime suspend, trigger timeout behavior, long-run pointer wrap, and suspend/resume with an open capture stream. Register tracing should specifically verify `ACP_EXTERNAL_INTR_CNTL` after `disable_pdm_interrupts()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/acp3x-pdm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/acp3x-rn.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/acp3x-rn.c

## Purpose
This is the Renoir DMIC ASoC machine driver. It binds the Renoir PDM DMA CPU/platform DAI to the generic DMIC codec and registers a one-link capture-only sound card.

## Important APIs, Types, And Functions
It defines `SND_SOC_DAILINK_DEF()` entries for `acp_rn_pdm_dma.0`, `dmic-codec.0`/`dmic-hifi`, and platform `acp_rn_pdm_dma.0`, then defines `acp_dai_pdm`, `acp_card`, and platform probe `acp_probe()`.

## Control Flow
The Renoir PCI parent creates platform device `acp_pdm_mach`. Probe assigns `acp_card.dev`, stores card data on the platform device, associates null machine private data, and registers the card. The single DAI link is capture-only and named `acp3x-dmic-capture`.

## State And Persistence Behavior
The file uses static card/link structures and does not hold runtime stream state. Power management uses `snd_soc_pm_ops`.

## Dependencies And Integration Points
It depends on `acp_rn_pdm_dma.0` from `acp3x-pdm-dma.c`, `dmic-codec.0` from the PCI parent, and `rn_acp3x.h` declarations. It is included only when `CONFIG_SND_SOC_AMD_RENOIR_MACH` is enabled.

## Risks And Edge Cases
The global static card assumes a single Renoir ACP card instance. If the machine-driver Kconfig is disabled, the PCI parent-created `acp_pdm_mach` device will not produce a sound card. No extra constraints or DAPM widgets are provided beyond component defaults.

## Test Signals
Expected signals are card name `acp`, one capture PCM named `DMIC capture`, successful component binding to `acp_rn_pdm_dma.0`, and no playback device from this card. Build coverage should include the machine Kconfig symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/acp3x-rn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn-pci-acp3x.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn-pci-acp3x.c

## Purpose
This is the Renoir ACP PCI parent driver for DMIC/PDM support. It initializes the ACP block, gates device creation through config, PCI revision, ACPI `_WOV`, DMI quirks, and module parameters, and creates PDM DMA, DMIC codec, and machine platform devices.

## Important APIs, Types, And Functions
Private state is `struct acp_dev_data`. Module parameters are `acp_power_gating` and `dmic_acpi_check`. Hardware functions are `rn_acp_power_on()`, `rn_acp_power_off()`, `rn_acp_reset()`, `rn_acp_enable_interrupts()`, `rn_acp_disable_interrupts()`, `rn_acp_init()`, and `rn_acp_deinit()`. PCI callbacks are `snd_rn_acp_probe()`, `snd_rn_acp_suspend()`, `snd_rn_acp_resume()`, and `snd_rn_acp_remove()`.

## Control Flow
Probe first rejects systems configured for another AMD ACP stack via `snd_amd_acp_find_config()` and rejects non-Renoir revision `0x01`. It enables PCI, requests regions, attempts MSI, maps BAR0, initializes ACP, checks DMIC policy (`dmic_acpi_check`), evaluates ACPI `_WOV` in auto mode, applies DMI quirks that suppress DMIC on listed Lenovo systems, allocates two resources, and registers three platform devices: `acp_rn_pdm_dma`, `dmic-codec`, and `acp_pdm_mach`. PM suspend deinitializes ACP; resume reinitializes it.

## State And Persistence Behavior
Parent state persists MMIO base, resource array, and three child platform devices. `acp_power_gating` controls whether deinit powers off the block after reset. MSI enable state is persisted in PCI core and disabled during remove/error paths. Runtime PM autosuspend is enabled after successful child creation.

## Dependencies And Integration Points
It depends on Linux PCI, ACPI, DMI, runtime PM, the shared AMD machine-config helper `snd_amd_acp_find_config()`, and `rn_acp3x.h` register definitions. The children bind to Renoir PDM DMA, generic DMIC codec, and Renoir machine drivers.

## Risks And Edge Cases
`dmic_acpi_check=0` forces probe failure even if hardware exists; auto mode can fail if `_WOV` is absent. DMI quirks suppress DMIC for listed Lenovo systems by using entries with null `driver_data`. Error unwind unregisters all `ACP_DEVS` children even after partial registration, which may encounter uninitialized entries. Optional power gating changes hardware state across suspend and should be validated per platform.

## Test Signals
Test revision filtering, `snd_amd_acp_find_config()` interaction, MSI and shared IRQ paths, `_WOV` present/absent/false, each `dmic_acpi_check` setting, DMI-quirked Lenovo systems, runtime/system suspend/resume, and remove/error unwind. Expected successful platforms show three child platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn-pci-acp3x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn_acp3x.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn_acp3x.h

## Purpose
This header provides Renoir ACP3x PDM driver constants, structures, MMIO helpers, and the machine-config declaration used by the Renoir PCI and PDM DMA drivers.

## Important APIs, Types, And Functions
It defines `ACP_DEVS`, physical/register bounds, PCI device ID, power/reset masks, PDM DMA masks, capture buffer sizes, `struct pdm_dev_data`, `struct pdm_stream_instance`, `union acp_pdm_dma_count`, `rn_readl()`, `rn_writel()`, and external declaration `snd_amd_acp_find_config()`.

## Control Flow
No executable control flow exists beyond inline MMIO helpers. The helpers subtract `ACP_PHY_BASE_ADDRESS` from absolute register constants so callers can use an ioremapped BAR base plus absolute-style offsets.

## State And Persistence Behavior
The declared structures define the PDM runtime state: active capture stream, IRQ number, MMIO base, per-stream DMA address, page count, and baseline byte count. Constants fix the DMIC capture profile to four periods of 4096..8192 bytes at 48 kHz stereo.

## Dependencies And Integration Points
It includes `rn_chip_offset_byte.h` for register offsets and is included by `rn-pci-acp3x.c`, `acp3x-pdm-dma.c`, and `acp3x-rn.c`. The external config helper connects this legacy driver with shared AMD ACP stack selection.

## Risks And Edge Cases
Like the Raven header, absolute offsets require consistent use of `rn_readl()`/`rn_writel()`. The header exposes only PDM-oriented state; I2S registers in the offset header are not used by this Renoir path. The PDM DAI advertises S24/S32 in C code while hardware constants emphasize S32 capture, so constraints should be checked at runtime.

## Test Signals
Compile all Renoir files, verify BAR-relative MMIO calculations, and validate DMA byte-count high/low composition through the union under long-running capture. Static analysis can check all callers use the inline helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn_acp3x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn_chip_offset_byte.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn_chip_offset_byte.h

## Purpose
This register header enumerates ACP3.1/Renoir absolute byte offsets for DMA, AXI2AXI ATU, clock/reset, miscellaneous interrupt/error registers, PGFSM, scratch space, audio buffers, I2S/TDM, BT/TDM, and WOV/PDM blocks.

## Important APIs, Types, And Functions
It contains macro definitions only. Important groups for the active Renoir driver path are `ACP_EXTERNAL_INTR_*`, `ACP_PGFSM_*`, `ACP_SOFT_RESET`, `ACP_CONTROL`, `ACP_CLKMUX_SEL`, `ACP_SCRATCH_REG_0`, `ACPAXI2AXI_*`, and WOV/PDM registers such as `ACP_WOV_PDM_ENABLE`, `ACP_WOV_RX_RINGBUFADDR`, and linear position counters.

## Control Flow
There is no control flow. The macros are consumed through `rn_acp3x.h` helpers and PDM/PCI code.

## State And Persistence Behavior
The header has no runtime state but defines where the driver persists hardware state: power status, interrupt masks/status, DMA PTEs in scratch, ring-buffer configuration, PDM enable/DMA enable bits, FIFO flush, gain/misc control, and linear counters.

## Dependencies And Integration Points
The offsets are absolute around `0x1240000`; `rn_readl()` and `rn_writel()` convert them to BAR-relative accesses. The Renoir PDM DMA driver depends on the WOV block definitions, while the PCI parent depends on PGFSM and clock/reset definitions.

## Risks And Edge Cases
Unused I2S/BT register definitions may not be validated by the Renoir DMIC-only path. Any mismatch between absolute offsets and `ACP_PHY_BASE_ADDRESS` would misprogram MMIO. Because this is a low-level register contract, errors usually surface as probe timeouts, missing interrupts, or silent audio capture failure.

## Test Signals
Build coverage plus hardware register tracing during power-on/reset, PDM start/stop, PTE programming, interrupt mask changes, and pointer reads. Long capture tests can validate the linear counter offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/renoir/rn_chip_offset_byte.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/Makefile

## Purpose
This Makefile wires Vangogh ACP5x legacy ASoC support into Kbuild.

## Important APIs, Types, And Functions
It defines object lists for `snd-pci-acp5x`, `snd-acp5x-i2s`, `snd-acp5x-pcm-dma`, and `snd-soc-acp5x-mach`. The PCI, I2S, and DMA objects build under `CONFIG_SND_SOC_AMD_ACP5x`; the machine driver builds under `CONFIG_SND_SOC_AMD_VANGOGH_MACH`.

## Control Flow
Kbuild compiles the ACP5x PCI parent, CPU DAI, PCM DMA component, and optionally the codec-specific machine driver according to these Kconfig symbols.

## State And Persistence Behavior
There is no runtime state. It only defines build-time composition.

## Dependencies And Integration Points
The file ties together `pci-acp5x.c`, `acp5x-i2s.c`, `acp5x-pcm-dma.c`, and optionally `acp5x-mach.c`. The optional machine driver is needed for Valve Jupiter/Galileo cards.

## Risks And Edge Cases
If the machine symbol is disabled, the PCI parent can still create `acp5x_mach` but no card driver will bind. The legacy driver may be bypassed by SOF config selection in the PCI driver even when these objects are built.

## Test Signals
Build with ACP5x as module and built-in, with and without `CONFIG_SND_SOC_AMD_VANGOGH_MACH`, and confirm module/object names and dependencies resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-i2s.c

## Purpose
This is the Vangogh ACP5x CPU DAI driver for SP and HS I2S/TDM streams. It configures DAI format, master/slave clock mode, TDM slot format, sample resolution, master clock dividers, and stream start/stop registers.

## Important APIs, Types, And Functions
DAI callbacks are `acp5x_i2s_set_fmt()`, `acp5x_i2s_set_tdm_slot()`, `acp5x_i2s_hwparams()`, and `acp5x_i2s_trigger()`. Probe is `acp5x_dai_probe()`, and the DAI driver is `acp5x_i2s_dai`.

## Control Flow
The PCI parent creates `acp5x_i2s_playcap` platform devices for SP and HS register windows. `set_fmt` records I2S versus DSP_A/TDM and bit/frame clock provider mode. `hw_params` selects stream instance from card driver data, maps PCM format to sample length, optionally writes TDM format, and when in master mode computes BCLK/LRCLK dividers for supported sample rates and 16/32-bit formats. Trigger start writes period watermark, ring-buffer size, optional master clock generator, enables TX/RX register bit 0, and enables the instance IER. Trigger stop clears bit 0 and disables IER when both directions are idle.

## State And Persistence Behavior
Device state holds `tdm_mode`, `master_mode`, `tdm_fmt`, and MMIO base. Stream private data owned by the DMA component carries instance, resolution, byte count, and computed clock dividers. The probe defaults `master_mode` to enabled.

## Dependencies And Integration Points
It depends on `acp5x.h` for register definitions, helpers, data structures, and `acp5x_set_i2s_clk()`. It works with `acp5x-pcm-dma.c` for DMA setup and with `acp5x-mach.c` for card-level instance selection and codec constraints.

## Risks And Edge Cases
Master-mode divider tables only support S16_LE and S32_LE; S8/U8 formats are listed in the DAI but return `-EINVAL` in master clock setup when master mode is active. Supported DAI rates list 8..96 kHz, while divider code includes 192 kHz cases not advertised. The DAI assumes DMA private data exists before `hw_params` and trigger.

## Test Signals
Test SP and HS playback/capture, I2S and DSP_A modes, clock provider modes, 16- and 32-bit formats at each supported rate, invalid rates/formats, and trigger stop IER gating. Machine-driver tests should confirm correct instance selection for headset codec versus speaker amplifier paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-mach.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-mach.c

## Purpose
This Vangogh machine driver registers Valve-platform sound cards using NAU8821 headset codec with either CS35L41 or MAX98388 stereo speaker amplifiers. It defines DAI links, DAPM widgets/routes, headset jack detection, codec clock setup, constraints, and DMI-based card selection.

## Important APIs, Types, And Functions
Key functions are `platform_clock_control()`, `acp5x_8821_init()`, `acp5x_8821_startup()`, `acp5x_nau8821_hw_params()`, `acp5x_cs35l41_startup()`, `acp5x_cs35l41_hw_params()`, `acp5x_max98388_startup()`, and platform probe `acp5x_probe()`. It defines two cards: `acp5x_8821_35l41_card` and `acp5x_8821_98388_card`.

## Control Flow
Probe looks up DMI entries: Valve Jupiter selects the NAU8821+CS35L41 card, and Valve Galileo selects the NAU8821+MAX98388 card. It allocates `struct acp5x_platform_info`, attaches the selected static card to the platform device, and registers it. NAU8821 startup selects SP I2S for playback/capture and constrains streams to 48 kHz, two channels, and 32-bit samples. Speaker amplifier startup selects HS I2S for playback and constrains to 48 kHz stereo. Codec `hw_params` programs NAU8821 FLL from BCLK or sets CS35L41 SYSCLK for 48 kHz.

## State And Persistence Behavior
Persistent state includes static DAI-link/card descriptions, static headset jack `vg_headset`, and per-device `acp5x_platform_info` stored as card driver data. DAPM supply `Platform Clock` switches NAU8821 clocking between internal clock off-state and FLL/BCLK active-state. Jack detection is enabled through `nau8821_enable_jack_detect()`.

## Dependencies And Integration Points
It depends on codec drivers for NAU8821, CS35L41, and MAX98388; ACPI/I2C/SPI component names such as `i2c-NVTN2020:00`, `spi-VLV1776:00/01`, and `i2c-ADS8388:00/01`; CPU DAIs `acp5x_i2s_playcap.0/1`; and platform component `acp5x_i2s_dma.0`. It uses `acp5x.h` for instance identifiers.

## Risks And Edge Cases
Only two DMI products are supported; other Vangogh boards return `-ENODEV`. Static card objects are mutated with `card->dev`, so multiple instances are not expected. Codec component names are firmware-enumeration sensitive. MAX98388 path lacks a custom `hw_params` clock setup unlike CS35L41, relying on codec defaults or other configuration. Constraint lists force 48 kHz stereo, which may reject otherwise hardware-supported rates.

## Test Signals
On Valve Jupiter and Galileo, verify the expected card name, two DAI links, headset jack events, button media key mapping, speaker playback, headset playback/capture, DAPM clock transitions, and codec sysclk/FLL programming. DMI-negative systems should not register a card.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-mach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-pcm-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-pcm-dma.c

## Purpose
This platform driver implements Vangogh ACP5x PCM DMA for SP and HS I2S playback/capture. It provides ALSA PCM hardware constraints, DMA PTE/ring-buffer programming, shared IRQ handling, pointer reporting, and runtime/system PM restore.

## Important APIs, Types, And Functions
Main functions are `i2s_irq_handler()`, `config_acp5x_dma()`, `acp5x_dma_open()`, `acp5x_dma_hw_params()`, `acp5x_dma_pointer()`, `acp5x_dma_new()`, `acp5x_dma_close()`, `acp5x_audio_probe()`, `acp5x_pcm_resume()`, `acp5x_pcm_suspend()`, and `acp5x_pcm_runtime_resume()`. The component is named `acp5x_i2s_dma`.

## Control Flow
Probe consumes IRQ flags from platform data, maps the ACP MMIO resource, gets the IRQ, registers the ASoC component, requests the IRQ, and enables runtime PM. Open allocates `struct i2s_stream_instance` and applies playback/capture constraints. `hw_params` reads card platform info to route playback/capture to HS or SP, stores the substream in the appropriate active pointer, computes page count, and calls `config_acp5x_dma()`. IRQ handling acknowledges HS/SP TX/RX threshold bits and calls `snd_pcm_period_elapsed()`. Resume reprograms DMA and sample/TDM registers for all active stream pointers and reenables external interrupts.

## State And Persistence Behavior
Device state persists active substream pointers for HS playback/capture and SP playback/capture plus TDM settings shared with DAI state. Per-stream private data persists DMA address, page count, selected instance, transfer resolution, byte count, and clock dividers. Close clears the active pointer and frees stream private data.

## Dependencies And Integration Points
It depends on the Vangogh PCI parent for resources and IRQ flags, `acp5x.h` for register constants and helpers, `acp5x-i2s.c` for DAI format/trigger control, and `acp5x-mach.c` for routing through `acp5x_platform_info`.

## Risks And Edge Cases
`hw_params` fails if machine driver data is missing, making this component dependent on a correctly registered card. Resume writes fixed HS or SP sample registers based on stored active pointers; stale pointers would misprogram hardware. The DMA interrupt control register is programmed with all four threshold bits whenever any stream configures DMA. Tests should verify interrupt behavior with simultaneous SP and HS streams.

## Test Signals
Run SP headset playback/capture and HS speaker playback on supported boards, period interrupt validation for all four threshold bits, pointer wrap tests, repeated open/close memory checks, runtime suspend/resume interrupt gating, and system resume with active TDM and non-TDM streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x-pcm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x.h

## Purpose
This header defines Vangogh ACP5x constants, memory layout, stream structures, MMIO helpers, byte-count helper, and I2S master clock programming helper for the Vangogh PCI, I2S, DMA, and machine drivers.

## Important APIs, Types, And Functions
Important declarations include `struct i2s_dev_data`, `struct i2s_stream_instance`, `struct acp5x_platform_info`, `union acp_dma_count`, `union acp_i2stdm_mstrclkgen`, inline `acp_readl()`, `acp_writel()`, `acp_get_byte_count()`, and `acp5x_set_i2s_clk()`, plus external `snd_amd_acp_find_config()`.

## Control Flow
Inline helpers perform BAR-relative MMIO by subtracting `ACP5x_PHY_BASE_ADDRESS` from absolute register constants. `acp_get_byte_count()` selects HS or SP playback/capture linear position counters and returns a 64-bit union view. `acp5x_set_i2s_clk()` selects the master clock generator register based on stream instance and writes bitfields for master mode, format mode, BCLK divider, and LRCLK divider.

## State And Persistence Behavior
The structures define persistent per-device and per-stream state used across hw_params, trigger, pointer, and resume. Constants define fixed memory windows for SP/HS playback/capture, PTE offsets, FIFO offsets, DMA sizes, and ALSA buffer limits.

## Dependencies And Integration Points
It includes `vg_chip_offset_byte.h` for register offsets and `<sound/pcm.h>` for stream direction constants. All Vangogh sources include this header. The machine-config declaration connects the PCI parent to global AMD ACP stack selection.

## Risks And Edge Cases
`union acp_i2stdm_mstrclkgen mclkgen` in `acp5x_set_i2s_clk()` is not explicitly zero-initialized before bitfield assignment, so reserved bits may contain stack data unless the compiler clears it by chance; this is a register-programming risk. The helper subtraction requires all accesses to use `acp_readl()`/`acp_writel()` rather than raw `readl(base + absolute_offset)`. DAI rates and divider tables are not perfectly aligned.

## Test Signals
Build all Vangogh sources, trace master clock register values for reserved-bit cleanliness, validate byte-count reads over counter wrap, and verify each SP/HS memory window and PTE offset with DMA playback/capture tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/acp5x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/pci-acp5x.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/pci-acp5x.c

## Purpose
This is the Vangogh ACP5x PCI parent driver. It initializes ACP5x hardware, chooses legacy driver binding based on AMD audio configuration and SOF availability, creates I2S DMA/DAI and machine platform children in I2S mode, and handles PM/remove cleanup.

## Important APIs, Types, And Functions
Private state is `struct acp5x_dev_data`. Hardware helpers are `acp5x_power_on()`, `acp5x_reset()`, `acp5x_enable_interrupts()`, `acp5x_disable_interrupts()`, `acp5x_init()`, and `acp5x_deinit()`. PCI callbacks are `snd_acp5x_probe()`, `snd_acp5x_suspend()`, `snd_acp5x_resume()`, and `snd_acp5x_remove()`.

## Control Flow
Probe calls `snd_amd_acp_find_config()` and rejects the device unless legacy is selected, or SOF is selected but the SOF Vangogh driver is not enabled. It accepts PCI revision `0x50`, enables PCI, requests regions, maps BAR0, initializes ACP, reads `ACP_PIN_CONFIG`, and in I2S mode registers four platform devices: `acp5x_i2s_dma`, two `acp5x_i2s_playcap` DAIs for SP and HS, and `acp5x_mach`. It enables runtime PM autosuspend. Suspend deinitializes ACP; resume reinitializes it; remove unregisters children and disables PCI resources.

## State And Persistence Behavior
Parent state stores MMIO base, audio mode, resource array, and child platform devices. ACP init powers on, sets `ACP_CONTROL`, resets, selects clock mux `0x03`, and enables external interrupts. Deinit disables interrupts, resets, clears clock mux, and clears control.

## Dependencies And Integration Points
It depends on PCI, platform devices, runtime PM, `acp5x.h`, and `../mach-config.h`. It creates children consumed by `acp5x-pcm-dma.c`, `acp5x-i2s.c`, and `acp5x-mach.c`.

## Risks And Edge Cases
The config gate has nuanced interaction with SOF: legacy binds for `FLAG_AMD_LEGACY`, and can bind for `FLAG_AMD_SOF` only when SOF Vangogh support is not enabled. Probe ignores non-I2S pin modes after hardware init and PM setup. Error unwind unregisters only already-created children by decrementing `i`, which is safer than some older drivers. No MSI path is used; IRQ is shared.

## Test Signals
Test revision filtering, legacy versus SOF config combinations, I2S pin mode child creation, runtime/system suspend/resume, remove cleanup, and DMI-specific machine card binding downstream. Successful I2S mode should show `acp5x_i2s_dma.0`, `acp5x_i2s_playcap.0`, `acp5x_i2s_playcap.1`, and `acp5x_mach.0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/vangogh/pci-acp5x.c -->
