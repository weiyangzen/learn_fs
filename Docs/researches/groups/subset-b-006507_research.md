# Research: subset-b-006507

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_sai.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_sai.c

## Purpose
`fsl_sai.c` is the Freescale/NXP SAI CPU DAI driver for Linux ASoC. It binds SAI MMIO registers, clocks, IRQs, DMA parameters, pinctrl states, SoC variants, and ALSA DAI callbacks into playback and capture interfaces. It supports I2S, left-justified, DSP A/B, PDM-style DSD, TDM slot configuration, multi-dataline and multi-FIFO DMA, timestamp/bit-counter controls, runtime PM, and multiple i.MX/VF610 SAI revisions.

## Important APIs, Types, And Functions
The public integration surface is the platform driver `fsl_sai_driver`, matched by `fsl_sai_ids`, and the ASoC component `fsl_component`. The DAI templates expose a combined `sai-tx-rx` DAI plus split `sai-tx` and `sai-rx` DAIs, each backed by `fsl_sai_pcm_dai_ops`, `fsl_sai_pcm_dai_tx_ops`, or `fsl_sai_pcm_dai_rx_ops`.

Key callback functions are `fsl_sai_probe`, `fsl_sai_remove`, `fsl_sai_dai_probe`, `fsl_sai_startup`, `fsl_sai_set_dai_fmt*`, `fsl_sai_set_dai_sysclk`, `fsl_sai_set_dai_bclk_ratio`, `fsl_sai_set_dai_tdm_slot*`, `fsl_sai_hw_params`, `fsl_sai_hw_free`, and `fsl_sai_trigger`. Interrupt and PM logic is in `fsl_sai_isr`, `fsl_sai_runtime_suspend`, and `fsl_sai_runtime_resume`.

Important helpers include `fsl_sai_set_bclk` for MCLK/divider selection, `fsl_sai_read_dlcfg` for parsing `fsl,dataline`, `fsl_sai_check_version` for VERID/PARAM discovery, `fsl_sai_get_pins_state` for high-rate PCM/DSD pinctrl selection, and `fsl_sai_dir_is_synced` for determining which direction provides clocks in synchronous mode.

## Control Flow
Probe allocates `struct fsl_sai`, maps MMIO, configures the regmap defaults for either offset-0 or offset-8 register layouts, acquires the bus and MCLK clocks, gets optional PLL clocks, constrains rates from available clocks, detects multi-FIFO SDMA from `dmas`, parses dataline masks, requests the shared IRQ, copies the DAI templates, parses synchronous/asynchronous and MCLK-direction properties, initializes DMA addresses, enables runtime PM, reads hardware version data, optionally enables MCLK output, configures i.MX95 audio-mix mode through SCMI, registers the PCM DMA platform, and registers the component.

At DAI probe, both Tx and Rx paths are software-reset, FIFO watermarks are initialized from FIFO depth and maxburst, and ALSA DMA data is attached. `startup` applies EDMA period-size constraints and either the full SAI rate list in clock-consumer mode or clock-derived constrained rates in provider mode.

Format setup writes CR2/CR4 bit clock, frame clock, polarity, master/consumer, DSP, PDM, and bit-order fields. `hw_params` derives slot width, slots, pins/dataline type, BCLK, pinctrl state, MCLK divider, DMA FIFO address, multi-FIFO peripheral config, FIFO watermark, TRCE enabled dataline mask, CR4/CR5 frame and word layout, and channel mask registers. `trigger` enables FRDE, TERE, interrupt bits, and synchronized opposite direction when starting, and disables DMA request/interrupts, synchronized partners, TERE/BCE, FIFO reset, and software reset on stop.

## State And Persistence
Persistent driver state is in `struct fsl_sai`: regmap, bus and master clocks, PLL handles, selected MCLK IDs, `mclk_streams`, stream slots and widths, BCLK ratio, sync mode, consumer/provider mode, PDM/DSP flags, dataline config, pinctrl state, DMA params, SDMA peripheral config, version/parameter data, PM QoS request, and constrained-rate storage. Hardware register state is cached through regmap and restored across runtime PM. Runtime suspend disables active MCLKs and the bus clock, removes PM QoS when needed, and switches regmap cache-only on. Resume reenables clocks, resets Tx/Rx, syncs cached registers, and reasserts TERE for SoCs where MCLK generation depends on TERE.

## Dependencies And Integration Points
The file integrates with ALSA ASoC, DMAEngine PCM, `imx-pcm`, regmap, runtime PM, pinctrl, Linux clocks, optional system controller GPRs for i.MX6UL MCLK direction, SCMI i.MX misc controls for i.MX952 audio-mix routing, and SDMA peripheral configuration for multi-FIFO transfers. It includes `fsl_utils.h` for PLL rate constraints and runtime-PM-safe mixer controls used by timestamp kcontrols.

## Risks And Edge Cases
Clock selection is sensitive: provider mode must find a valid MCLK divisor, skip unsupported 1:1 ratios on older hardware, and handle synchronized directions that require programming the opposite CR2 register. Dataline masks from DT can reject channel layouts or enable non-successive FIFOs, and multi-FIFO DMA changes addresses, maxburst, and watermarks. PDM and high-rate PCM require matching pinctrl states. The `mclk_with_tere` path intentionally toggles frame-master bits around word-width programming to avoid frame-clock glitches. Runtime suspend/resume must keep `mclk_streams` and selected `mclk_id` coherent or clocks can be disabled/enabled on the wrong source. Shared IRQ handling only clears write-one-to-clear status bits masked by enabled IRQs.

## Test Signals
Useful test signals are probe success across each compatible string, successful regmap version reads on offset-8 parts, `aplay` and `arecord` for I2S provider and consumer modes, simultaneous Tx/Rx in synchronous and asynchronous modes, TDM slot masks, PDM/DSD rates, multi-FIFO DMA with multi-dataline channel counts, suspend/resume while a stream is configured, timestamp kcontrol reads under runtime PM, and absence of underrun/overflow debug messages from `fsl_sai_isr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_sai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_sai.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_sai.h

## Purpose
`fsl_sai.h` defines the register map, bit fields, constants, SoC data, version/parameter descriptors, dataline configuration, and private state for the Freescale/NXP SAI driver. It is the contract used by `fsl_sai.c` to translate ALSA DAI operations into register writes.

## Important APIs, Types, And Functions
There are no exported functions. The file provides register address macros like `FSL_SAI_TCSR(ofs)`, `FSL_SAI_RCR4(ofs)`, `FSL_SAI_xCR*`, `FSL_SAI_xDR0`, and `FSL_SAI_xMR`; control bit masks such as `FSL_SAI_CSR_TERE`, `FSL_SAI_CR2_BCD_MSTR`, `FSL_SAI_CR4_FRSZ`, `FSL_SAI_CR5_WNW`, and timestamp counter fields; and audio capability constants such as `FSL_SAI_FORMATS`, `FSL_SAI_MCLK_MAX`, and maxburst defaults.

The key types are `struct fsl_sai_soc_data`, `struct fsl_sai_verid`, `struct fsl_sai_param`, `struct fsl_sai_dl_cfg`, and `struct fsl_sai`. `TX` and `RX` are direction indexes used throughout the C file.

## Control Flow
The header itself has no runtime flow, but its macros encode how the driver selects offset-0 vs offset-8 register layouts, how Tx/Rx symmetric operations share code through `FSL_SAI_x*` selectors, how MCLK sources are selected through CR2/MCTL masks, and how FIFO, frame, sync, and timestamp operations are programmed.

## State And Persistence
`struct fsl_sai` contains the driver lifetime state: platform device, regmap, clocks, resource, stream mode flags, dataline configuration pointer/count, selected MCLK IDs, stream counters, slots, slot widths, DMA data, SoC data, hardware version data, PM QoS state, pinctrl state, SDMA peripheral configs, and constrained-rate storage. This state persists for the platform device lifetime and is used to reconstruct hardware state after runtime PM.

## Dependencies And Integration Points
The header depends on Linux DMA and ALSA DMAEngine PCM types. It is tightly coupled to ASoC DAI callbacks, regmap register programming, device-tree SoC match data, SDMA peripheral configuration, pinctrl, runtime PM, and timestamp kcontrols in `fsl_sai.c`.

## Risks And Edge Cases
Register macros must stay aligned with hardware revisions; an incorrect `reg_offset`, `max_register`, or volatile/writeable decision in the C file can cause regmap caching or access failures. `FAL_SAI_NUM_RATES` must remain large enough for constrained-rate output. `struct fsl_sai_dl_cfg` assumes up to eight datalines, so future hardware with more lanes would need expanded masks and parsing.

## Test Signals
Compile coverage should catch missing field or macro changes. Runtime signals include correct regmap access on all compatible devices, correct rate constraints, valid multi-dataline DMA addressing, and working timestamp controls where `FSL_SAI_VERID_TSTMP_EN` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_sai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_spdif.c

## Purpose
`fsl_spdif.c` is the Freescale/NXP S/PDIF ASoC CPU DAI driver. It exposes stereo S/PDIF playback/capture, configures transmitter and receiver clocks, handles DPLL lock and user/channel-status interrupts, provides IEC958 ALSA controls, supports raw capture and bypass on selected SoCs, and manages runtime PM clock/regcache state.

## Important APIs, Types, And Functions
The platform driver is `fsl_spdif_driver`, matched by `fsl_spdif_dt_ids`. The ASoC component is `fsl_spdif_component`; the DAI template is copied into `fsl_spdif_priv.cpu_dai_drv` and uses `fsl_spdif_dai_ops`.

Important types are `struct fsl_spdif_soc_data`, `struct spdif_mixer_control`, and `struct fsl_spdif_priv`. Key functions include `fsl_spdif_probe`, `fsl_spdif_dai_probe`, `fsl_spdif_startup`, `fsl_spdif_hw_params`, `fsl_spdif_trigger`, `fsl_spdif_shutdown`, `fsl_spdif_runtime_suspend`, `fsl_spdif_runtime_resume`, `spdif_softreset`, `spdif_set_sample_rate`, `fsl_spdif_probe_txclk`, `fsl_spdif_txclk_caldiv`, and `spdif_get_rxclk_rate`.

ALSA controls are implemented by `fsl_spdif_pb_get/put`, `fsl_spdif_capture_get`, `fsl_spdif_subcode_get`, `fsl_spdif_qget`, `fsl_spdif_rx_vbit_get`, `fsl_spdif_tx_vbit_get/put`, `fsl_spdif_rx_rcm_get/put`, `fsl_spdif_bypass_get/put`, `fsl_spdif_rxrate_get`, and `fsl_spdif_usync_get/put`.

## Control Flow
Probe allocates private data, copies the DAI template, maps registers, initializes regmap, requests one or two IRQs depending on SoC data, gets all `rxtx0..7` clocks, treats `rxtx5` as sysclk and `rxtx1` as the default RX clock, acquires core/spba clocks, initializes IEC958 channel status defaults, sets DMA addresses to STL/SRL, enables runtime PM, switches regmap to cache-only, initializes the i.MX PCM DMA platform, and registers the component.

Startup soft-resets the module on first active stream, disables interrupts, configures TX or RX FIFO modes in SCR, and powers up the block. Playback `hw_params` reparents the root clock when allowed, selects a usable TX clock/divider for the requested sample rate, updates channel-status sample-frequency bits, writes channel status registers, and sets clock accuracy. Capture `hw_params` configures SRPC receive clock source and gain. Trigger enables/disables stream-specific interrupts and DMA bits and clears TX data registers on stop. Shutdown disables FIFO modes or TX clock and powers down the module when both directions are inactive.

The IRQ path reads SIS and SIE, writes SIC to clear enabled pending bits, updates DPLL lock state and notifies the RX sample-rate kcontrol, captures U/Q subcode bytes into double buffers, marks ready buffers on sync, drops buffers on framing error, and logs FIFO, parity, validity, and lock events.

## State And Persistence
`fsl_spdif_priv` holds SoC capabilities, the mixer/control buffers, DAI template copy, card/kcontrol pointers, regmap, DPLL lock flag, per-rate clock source/divider caches, clock handles, DMA data, cached SRPC value, bypass state, and PLL clocks. `spdif_mixer_control` holds transmit channel status, U/Q buffers, buffer positions, and a spinlock for userspace reads racing with IRQ updates. Runtime suspend disables interrupts, caches SRPC, puts regmap in cache-only mode, disables all TX/RX clocks plus SPBA/core clocks, and resume reenables clocks, restores SRPC, and syncs regcache.

## Dependencies And Integration Points
The driver depends on ALSA ASoC, IEC958 definitions, DMAEngine PCM, i.MX PCM DMA, regmap, runtime PM, Linux clocks, firmware-independent clock tree behavior, and `fsl_utils` PLL reparenting. It uses the macros and rate/format masks from `fsl_spdif.h`.

## Risks And Edge Cases
TX clock calculation searches multiple clocks and dividers with a 0.1 percent quick-exit threshold, so bad clock tree rates can produce approximate output or zero divider failures. Bypass mode rewrites PCM substream counts and is blocked while streams are active; incorrect card/runtime assumptions can affect availability. U/Q buffer handling stores both U and Q data into `subcode` in the shared helper even when `qget` reads `qsub`, so this path is worth close validation. DPLL unlock disables symbol-error interrupt noise. Raw capture mutates the DAI capture format mask at runtime. Runtime PM must preserve SRPC because it is volatile and used for RX rate measurement.

## Test Signals
Test with playback rates 22.05 kHz through 192 kHz, capture DPLL lock/unlock and RX sample-rate kcontrol notifications, IEC958 playback channel-status writes, capture channel status after `INT_CNEW`, U/Q subcode reads after sync, raw capture toggle on i.MX8MM, bypass enable/disable with no active stream, suspend/resume after configured clocks, and IRQ logging for lock loss, FIFO resync, and validity errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_spdif.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_spdif.h

## Purpose
`fsl_spdif.h` defines the Freescale/NXP S/PDIF register map, control/status bit fields, interrupt masks, clock divider fields, gain and TX-rate enums, IEC958 buffer sizes, and supported ALSA rate/format masks used by `fsl_spdif.c`.

## Important APIs, Types, And Functions
There are no functions. The important definitions are register offsets such as `REG_SPDIF_SCR`, `REG_SPDIF_SRPC`, `REG_SPDIF_SIE/SIS/SIC`, data/status registers, extended 192-bit channel-status registers, SCR FIFO/DMA/TXSEL fields, SRPC DPLL/clock/gain fields, interrupt masks, STC clock divider fields, `enum spdif_gainsel`, `enum spdif_txrate`, `SPDIF_CSTATUS_BYTE`, `SPDIF_UBITS_SIZE`, `SPDIF_QSUB_SIZE`, and playback/capture rate and format masks.

## Control Flow
The header shapes runtime flow by defining which SCR bits are toggled at startup/shutdown/trigger, which interrupts are enabled and cleared in the ISR, how SRPC clock source and gain are encoded for RX DPLL measurement, and how STC encodes TX clock source, TX divider, system divider, and all-clock enable.

## State And Persistence
No storage is allocated here. The defined register fields are cached through regmap in the C file, while data sizes determine persistent channel-status and subcode buffers in `struct spdif_mixer_control`.

## Dependencies And Integration Points
The file assumes ALSA PCM rate and format constants are available through the including C file. It provides the low-level hardware constants for ASoC DAI callbacks, IEC958 kcontrols, regmap access tables, and runtime PM restore logic in `fsl_spdif.c`.

## Risks And Edge Cases
The interrupt and register constants are reused as read and write-clear addresses (`REG_SPDIF_SIS` and `REG_SPDIF_SIC` share an offset), so regmap writeability and clear semantics must match hardware. The extended channel-status registers are only valid for selected SoCs. Playback and capture support different formats and rates, and capture is fixed to 24-bit unless raw capture mode is enabled by the C file.

## Test Signals
Compile-time users should catch missing constants. Runtime evidence includes correct IRQ clearing, valid STC divider programming for each `enum spdif_txrate`, correct RX DPLL rate calculation using `SRPC` and `SRFM`, and working 192-bit channel-status writes on SoCs that set `cchannel_192b`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_spdif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi.c

## Purpose
`fsl_ssi.c` is the Freescale SSI ASoC CPU DAI driver for MPC8610 and i.MX SSI blocks. It supports I2S, left-justified, DSP A/B, AC97, synchronous/asynchronous operation, DMA or FIQ stream filtering, single/dual/dynamic FIFO use, TDM masks, legacy machine-card instantiation, AC97 codec register access, debug IRQ statistics, and system sleep register caching.

## Important APIs, Types, And Functions
The platform driver is `fsl_ssi_driver`, matched by `fsl_ssi_ids`. The core private state is `struct fsl_ssi`, with SoC policy in `struct fsl_ssi_soc_data` and cached per-direction register bits in `struct fsl_ssi_regvals`.

Key functions are `fsl_ssi_probe`, `fsl_ssi_probe_from_dt`, `fsl_ssi_imx_probe`, `fsl_ssi_hw_init`, `fsl_ssi_hw_clean`, `fsl_ssi_startup`, `fsl_ssi_shutdown`, `fsl_ssi_set_bclk`, `fsl_ssi_hw_params`, `fsl_ssi_hw_free`, `_fsl_ssi_set_dai_fmt`, `fsl_ssi_set_dai_fmt`, `fsl_ssi_set_dai_tdm_slot`, `fsl_ssi_trigger`, `fsl_ssi_config_enable`, `fsl_ssi_config_disable`, `fsl_ssi_isr`, `fsl_ssi_suspend`, and `fsl_ssi_resume`. AC97 access is implemented through `fsl_ssi_ac97_read`, `fsl_ssi_ac97_write`, and `fsl_ssi_ac97_ops`.

## Control Flow
Probe parses DT for IPG clock naming, AC97 mode, synchronous mode, DMA vs FIQ, FIFO depth, dual/dynamic FIFO SDMA type, and legacy card creation. It selects the normal or AC97 DAI template, maps registers, adapts regmap max register for i.MX21-class SSI, requests the IRQ, applies symmetric constraints in synchronous mode, sets FIFO watermarks/maxburst from FIFO depth, initializes i.MX clocks and PCM backend, sets AC97 ops when needed, registers the component, requests IRQ for DMA mode, creates debugfs, initializes SSI registers, and optionally registers an old-style sound-card or AC97 codec platform device.

Runtime stream setup enables the register clock and adds even-period constraints for dual/dynamic FIFO. `set_fmt` programs SCR/STCR/SRCR for audio format, polarity, clock provider mode, I2S/network mode, and synchronous mode. `set_tdm_slot` programs frame slot count, masks STMSK/SRMSK while temporarily enabling SSIEN, and stores slot metadata. `hw_params` optionally calculates and enables baudclk for master mode, handles word length and I2S/network overrides, and configures dynamic FIFO SDMA peripheral parameters by channel count. Trigger starts by refreshing AC97 slot status when needed and calling `fsl_ssi_config_enable`; stop calls `fsl_ssi_config_disable`.

`fsl_ssi_config_enable` clears the FIFO, writes cached SRCR/STCR/SIER bits either for both directions on offline-config SoCs or for the active direction on online-config SoCs, primes TX DMA by waiting for FIFO fill, then enables SCR bits and marks the stream active. Disable computes shared-bit exclusions so stopping one direction does not break the other, handles offline-config restrictions, clears SIER/SxCR bits, and clears FIFO.

## State And Persistence
`struct fsl_ssi` persists DAI format, active stream mask, synchronous flag, DMA/FIQ and FIFO mode flags, clock handles, baudclk stream mask, slot settings, cached register values, DMA/FIQ parameters, physical address, legacy card device, debug stats, FIFO watermarks, AC97 mutex, and SDMA peripheral config. System suspend caches `SFCSR` and `SACNT`, marks regcache dirty/cache-only, and resume restores FIFO watermarks/AC97 control before syncing regcache. AC97 register access uses a global `fsl_ac97_data` pointer and a mutex because AC97 bus ops lack per-instance context.

## Dependencies And Integration Points
The driver integrates with ALSA ASoC, DMAEngine PCM, `imx-pcm` DMA/FIQ backends, AC97 bus operations, OF platform legacy card registration, Linux clock framework, regmap, debugfs via `fsl_ssi_dbg.c`, and register definitions from `fsl_ssi.h`.

## Risks And Edge Cases
Offline-config SoCs cannot safely reprogram critical bits while SSIEN is set, so the cached register-bit merge/exclusion logic is crucial when both streams are active. Master BCLK generation requires a valid baudclk, must stay below IPG/5, and searches dividers with approximate matching. AC97 mode has hardware limitations described in the file header, including fixed practical 48 kHz capture and unreliable status polling, so it uses fixed delays. Dynamic FIFO mode mutates cached FIFO-enable bits based on mono vs multi-channel layout. Legacy card registration and global AC97 data are single-instance-sensitive.

## Test Signals
Exercise I2S provider/consumer, synchronous full-duplex, asynchronous mode, TDM masks, mono handling, dual FIFO and dynamic FIFO DMA, FIQ stream filter boards, AC97 codec register read/write and playback/capture, suspend/resume preserving SFCSR/SACNT, old DT legacy card creation, debugfs `stats`, and interrupt counters for underrun/overrun/frame events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi.h

## Purpose
`fsl_ssi.h` defines the SSI register map, control/status bit fields, FIFO helpers, AC97 fields, and optional debugfs statistics interface used by `fsl_ssi.c` and `fsl_ssi_dbg.c`.

## Important APIs, Types, And Functions
The main content is register constants `REG_SSI_*`, selector macros `REG_SSI_SxCR`, `REG_SSI_SxCCR`, and `REG_SSI_SxMSK`, SCR/SISR/SIER/STCR/SRCR/SxCCR/SFCSR/STR/SOR/SACNT masks, and helper encoders such as `SSI_SxCCR_WL`, `SSI_SxCCR_DC`, `SSI_SxCCR_PM`, and FIFO counter/watermark macros.

When `CONFIG_DEBUG_FS` is enabled, `struct fsl_ssi_dbg` contains a debugfs dentry and per-status-bit counters, with prototypes for `fsl_ssi_dbg_isr`, `fsl_ssi_debugfs_create`, and `fsl_ssi_debugfs_remove`. When debugfs is disabled, the struct is empty and inline no-op replacements keep the main driver code unconditional.

## Control Flow
The header has no direct execution, but it defines how the SSI driver sets or clears transmitter/receiver enable, clock/frame direction, DMA/IRQ enable, FIFO clear, AC97 read/write mode, TDM masks, and suspend/resume cache fields. The debugfs conditional flow compiles statistics support in or out without changing call sites.

## State And Persistence
No live state is allocated by the header except through `struct fsl_ssi_dbg` embedded in `struct fsl_ssi`. The counters persist for the device lifetime and are incremented from the IRQ path. Register masks define which hardware values are cached by the C file for suspend/resume.

## Dependencies And Integration Points
It depends on Linux device declarations and debugfs availability. It is consumed by the SSI driver for regmap access and by `fsl_ssi_dbg.c` for human-readable interrupt statistics.

## Risks And Edge Cases
Several registers are marked as undocumented or internal in comments (`STR`, `SOR`) but are still used to clear FIFOs and observe state. i.MX21-class hardware lacks AC97 channel status/enable/disable registers, so users of these constants must gate access. Debugfs no-op stubs must remain signature-compatible with the enabled implementation.

## Test Signals
Build with and without `CONFIG_DEBUG_FS`, run SSI playback/capture to confirm SIER and SISR bit meanings, check AC97 paths on non-i.MX21 hardware, and validate debugfs counter increments for FIFO, frame, underrun, overrun, and command status interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi_dbg.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi_dbg.c

## Purpose
`fsl_ssi_dbg.c` provides optional debugfs support for the SSI driver. It counts interrupt/status events observed by `fsl_ssi_isr` and exposes them in a `stats` debugfs file per SSI device.

## Important APIs, Types, And Functions
The functions exported to the main driver are `fsl_ssi_dbg_isr`, `fsl_ssi_debugfs_create`, and `fsl_ssi_debugfs_remove`. The internal display callback is `fsl_ssi_stats_show`, wrapped by `DEFINE_SHOW_ATTRIBUTE(fsl_ssi_stats)`. The `SIER_SHOW` macro prints a counter when the corresponding interrupt enable constant exists.

## Control Flow
The SSI IRQ handler calls `fsl_ssi_dbg_isr` with the raw SISR value. The function increments counters in `struct fsl_ssi_dbg.stats` for each set SISR bit. Probe calls `fsl_ssi_debugfs_create`, which creates a directory named after the device and a read-only `stats` file. Remove and probe error paths call `fsl_ssi_debugfs_remove`, which recursively removes the directory. Reading `stats` prints all tracked counters.

## State And Persistence
Counters live inside the parent driver's `struct fsl_ssi_dbg` and persist until device removal. They are not reset by reads, suspend/resume, or stream restarts. The debugfs dentry pointer is stored in the same struct for cleanup.

## Dependencies And Integration Points
The file depends on debugfs, seq_file show helpers, Linux device names, and SISR/SIER constants from `fsl_ssi.h`. It is only compiled when debugfs support is enabled through the header's conditional declarations.

## Risks And Edge Cases
Counter increments are not explicitly locked; they occur in IRQ context and can race with debugfs reads, so values are diagnostic rather than synchronized accounting. The `SIER_SHOW` macro tests compile-time constants, so it does not filter by the runtime SIER register value. Failure to create debugfs entries is not checked, consistent with debugfs being optional.

## Test Signals
With debugfs enabled, run playback/capture and inspect `/sys/kernel/debug/<device>/stats`. Force or observe underrun/overrun/frame events and verify corresponding counters increase. Build with debugfs disabled to ensure main SSI calls compile to no-ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_ssi_dbg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_utils.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_utils.c

## Purpose
`fsl_utils.c` provides shared Freescale/NXP ASoC helpers for legacy DMA phandle resolution, PLL clock discovery/reparenting, clock-derived PCM rate constraints, and runtime-PM-safe wrappers around volatile ALSA mixer controls.

## Important APIs, Types, And Functions
Exported functions are `fsl_asoc_get_dma_channel`, `fsl_asoc_get_pll_clocks`, `fsl_asoc_reparent_pll_clocks`, `fsl_asoc_constrain_rates`, `fsl_asoc_get_xr_sx`, `fsl_asoc_put_xr_sx`, `fsl_asoc_get_enum_double`, `fsl_asoc_put_enum_double`, `fsl_asoc_get_volsw`, and `fsl_asoc_put_volsw`.

## Control Flow
`fsl_asoc_get_dma_channel` parses a named phandle from an SSI node, validates `fsl,ssi-dma-channel`, derives the platform name from the DMA channel resource address and node name, and returns DMA channel/controller IDs from `cell-index`. `fsl_asoc_get_pll_clocks` optionally acquires `pll8k` and `pll11k`. `fsl_asoc_reparent_pll_clocks` walks parent clocks until it finds either PLL and reparents to the 8 kHz or 11.025 kHz family based on divisibility of the requested ratio by 8000. `fsl_asoc_constrain_rates` filters an original rate list to rates that divide at least one available PLL/external clock, falling back to the original list if no match is found.

The mixer wrappers resume the component device with `pm_runtime_resume_and_get`, call the standard ASoC get/put implementation, suppress positive change notifications for volatile put operations by returning zero, and drop runtime PM with autosuspend.

## State And Persistence
The file does not own long-lived state. It writes caller-provided DMA IDs/platform name buffers, returns clock pointers acquired through devm, mutates caller-provided rate constraint/list storage, and temporarily changes device runtime PM state around volatile control access.

## Dependencies And Integration Points
It depends on Linux clocks, clock provider parent inspection, OF address parsing, runtime PM, and ASoC mixer helpers. SAI and XCVR use PLL helpers and rate constraints; SAI and XCVR timestamp controls use the runtime-PM-safe mixer wrappers; legacy PowerPC/i.MX machine code can use DMA channel lookup.

## Risks And Edge Cases
`fsl_asoc_get_dma_channel` relies on legacy `cell-index` properties and manually builds a platform name to match ASoC platform devices. `fsl_asoc_reparent_pll_clocks` mutates the local `ratio` with `do_div`, so callers should pass a value, not expect it preserved. Rate constraints depend on current clock rates, and null clocks are treated as rate zero. Mixer wrappers return immediately on runtime PM failure, which surfaces PM issues to userspace controls.

## Test Signals
Validate legacy SSI DMA lookup on old DT bindings, check rate constraints with only 8 kHz PLL, only 11.025 kHz PLL, both PLLs, and no PLLs, verify parent switch when changing between 48 kHz-family and 44.1 kHz-family rates, and read/write timestamp or other volatile kcontrols while the device is runtime suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_utils.h -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_utils.h

## Purpose
`fsl_utils.h` declares shared Freescale/NXP ASoC helper functions and defines helper macros for volatile or read-only ALSA controls that need runtime-PM-safe handlers.

## Important APIs, Types, And Functions
The header declares DMA lookup, PLL lookup/reparenting, rate constraint, and mixer get/put helpers implemented in `fsl_utils.c`. It defines `DAI_NAME_SIZE` and three kcontrol-construction macros: `FSL_ASOC_SINGLE_XR_SX_EXT_RO`, `FSL_ASOC_SINGLE_EXT`, and `FSL_ASOC_ENUM_EXT`.

## Control Flow
There is no direct runtime flow. The macros construct `struct snd_kcontrol_new` initializers with access flags and private values wired to caller-provided get/put handlers. The function declarations allow drivers such as SAI and XCVR to add volatile timestamp controls that resume the hardware before accessing registers.

## State And Persistence
The header owns no state. The macros embed private control descriptors in kcontrol initializers, and the declared helpers operate on caller-owned clocks, constraints, DAI links, and controls.

## Dependencies And Integration Points
The declarations depend on ASoC DAI link/control types, OF device nodes, Linux clocks, and PCM hardware constraint lists. This file is included by multiple FSL sound drivers to avoid duplicating PLL and volatile-control logic.

## Risks And Edge Cases
The macros must match ASoC's expected `private_value` layout for `soc_mreg_control`, `SOC_SINGLE_VALUE`, and enum controls. The volatile access flags mean user reads and writes may hit hardware frequently, so paired PM-safe handlers are required.

## Test Signals
Compile all users after ASoC API changes, inspect created controls for correct access flags, and exercise runtime-suspended reads/writes for controls created with these macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_xcvr.c -->
# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_xcvr.c

## Purpose
`fsl_xcvr.c` is the NXP Audio Transceiver ASoC DAI driver for S/PDIF, ARC receive, and eARC modes on i.MX8MP/i.MX93/i.MX95-family hardware. It manages the main XCVR register block, optional PHY/PLL access through an AI sideband interface, firmware loading into XCVR RAM, PCM constraints per mode, IEC958 channel status controls, capabilities data, DMA datapath start/stop, IRQ handling, RX reset work, and runtime PM.

## Important APIs, Types, And Functions
The platform driver is `fsl_xcvr_driver`, matched by `fsl_xcvr_dt_ids`. Important types are `struct fsl_xcvr_soc_data`, `enum fsl_xcvr_pll_verison`, and `struct fsl_xcvr`. The ASoC DAI callbacks are in `fsl_xcvr_dai_ops`: `fsl_xcvr_dai_probe`, `fsl_xcvr_prepare`, `fsl_xcvr_startup`, `fsl_xcvr_shutdown`, and `fsl_xcvr_trigger`.

Mode/control functions include `fsl_xcvr_mode_get/put`, `fsl_xcvr_arc_mode_get/put`, `fsl_xcvr_capds_get/put`, `fsl_xcvr_activate_ctl`, `fsl_xcvr_rx_cs_get`, `fsl_xcvr_tx_cs_get/put`, and timestamp controls built with `fsl_utils`. Hardware access helpers include `fsl_xcvr_ai_read/write`, `fsl_xcvr_phy_reg_read/write`, `fsl_xcvr_pll_reg_read/write`, `fsl_xcvr_en_phy_pll`, `fsl_xcvr_en_aud_pll`, `fsl_xcvr_load_firmware`, `irq0_isr`, `reset_rx_work`, `fsl_xcvr_runtime_suspend`, and `fsl_xcvr_runtime_resume`.

## Control Flow
Probe gets IPG, PHY, SPBA, PLL-IPG, and optional PLL-family clocks, constrains SPDIF rates for SPDIF-only SoCs, maps RAM and registers, initializes main and optional PHY/PLL regmaps, gets reset control, requests IRQ0, records FIFO DMA resources, enables runtime PM, puts regmaps into cache-only state, registers DMAEngine PCM and the ASoC component, and initializes reset work and a spinlock.

DAI probe attaches DMA params, sets mode to SPDIF for SPDIF-only hardware, or adds mode/ARC/CAPDS controls for multi-mode hardware, then adds IEC958 playback/capture controls. Startup rejects duplicate same-direction streams, applies EDMA period constraints, applies channel/rate constraints based on current mode, marks the stream active, and disables mode controls while a stream runs. Prepare configures the PHY/PLL and datapath for SPDIF, ARC, or eARC: SPDIF TX sets audio PLL and frame format, SPDIF/ARC RX configures RX datapath and 175 MHz PHY PLL, eARC configures CMDC mode, RX FIFO, and EXT_CTRL mode/reset bits. Trigger uses a spinlock to set datapath reset, start/stop TX data and CMDC TX bits, enable/disable DMA, enable/disable eARC IRQs, and clear reset. Shutdown clears stream state, reenables controls when idle, disables eARC IRQs, clears SPDIF mode as needed, and asserts CMDC reset for eARC.

Runtime resume asserts reset, enables clocks, deasserts reset, syncs regmaps, releases AI reset, syncs PHY/PLL regmaps, loads optional firmware into 10 RAM pages, writes capabilities data, releases the M0+ core, and waits for firmware initialization. Runtime suspend optionally asserts M0+ core reset for eARC, switches regmaps to cache-only, and disables clocks.

The IRQ handler reads external ISR bits, captures new channel-status blocks either from firmware-managed RAM buffers or direct RX CS registers, bit-reverses each 32-bit word, acknowledges received channel status, logs and clears other status bits, and schedules `reset_rx_work` on preamble mismatch errors. The work item temporarily disables DMA read, toggles RX datapath reset, and reenables DMA read under the same spinlock as trigger.

## State And Persistence
`struct fsl_xcvr` holds SoC data, regmaps, clocks, reset, active stream mask, current mode and ARC mode, mapped firmware RAM, DMA params, RX/TX IEC958 status, 256-byte eARC capabilities data, reset work, spinlock, and constrained SPDIF rate storage. Regmap caches persist hardware register intent across runtime PM. Firmware and capabilities data are rewritten to RAM on resume. IEC958 status and CAPDS controls are software state visible through ALSA controls.

## Dependencies And Integration Points
The driver integrates with ALSA ASoC, DMAEngine PCM, regmap MMIO and custom bus regmaps, reset controller, firmware loader, runtime PM, Linux clocks, i.MX PCM helpers, `fsl_utils` PLL/rate/control helpers, and register definitions from `fsl_xcvr.h`.

## Risks And Edge Cases
Mode controls mutate PCM substream availability and are disabled while streams are active; userspace mode changes must therefore be sequenced before opening streams. Firmware size is limited to 16 KiB code RAM and assumes IPG clock is running before `memcpy_toio`. AI sideband accesses poll toggle/done bits and can timeout if PHY/PLL clock or reset state is wrong. PLL configuration supports a fixed table of output frequencies and rejects rates that do not divide them. Trigger and reset work share register bits, making the spinlock important. Channel-status access uses casts to `u32 *` over byte arrays, so alignment and endian/bit-reversal behavior are part of the hardware contract.

## Test Signals
Test probe/runtime resume with and without firmware, SPDIF-only i.MX93 and PHY-backed i.MX8MP/i.MX95 data, all modes where available, playback disable in ARC/eARC modes, rate/channel constraints for SPDIF vs eARC, IEC958 status get/put, CAPDS read/write and firmware RAM copy, suspend/resume with firmware reload, IRQ-driven channel-status updates, preamble-error reset work, and concurrent trigger/IRQ reset races under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_xcvr.c -->
