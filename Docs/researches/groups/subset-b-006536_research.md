# subset-b-006536 R-Car audio driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/adg.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/adg.c

## Purpose

`adg.c` implements helper routines for the R-Car Audio Clock Generator. It discovers ADG input clocks, computes BRGA/BRGB divider settings for 44.1 kHz and 48 kHz clock families, registers optional ADG clock outputs, and programs clock selectors used by SSI, SRC, and CMD modules. The rest of the driver treats it as the clock authority behind `rsnd_adg_clk_query()`, `rsnd_adg_ssi_clk_try_start()`, and the Gen2 timing selector helpers.

## Important APIs, types, and functions

`struct rsnd_adg` stores the ADG clock, input clocks, clock-output provider state, cached input rates, BRG register values, and the embedded `rsnd_mod`. `rsnd_adg_probe()` allocates this state, initializes the pseudo module, gets clock inputs and outputs, enables clocks, and logs debug information. `rsnd_adg_remove()` unregisters clkouts, deletes the OF clock provider, disables clocks, and unregisters the null clock. `rsnd_adg_clk_control()` enables/disables the ADG and input clocks while caching rates to avoid `clk_get_rate()` in atomic paths. `rsnd_adg_clk_query()` maps a requested master rate to CLKA/B/C/I or BRGA/BRGB selector codes. `rsnd_adg_ssi_clk_try_start()` and `rsnd_adg_ssi_clk_stop()` program `AUDIO_CLK_SEL*` for SSI clock output. `rsnd_adg_set_src_timesel_gen2()` and `rsnd_adg_set_cmd_timsel_gen2()` program SRC/CMD timing selectors for rate conversion paths.

## Control Flow

Probe builds an ADG module with no real module clock, fetches `adg` and generation-specific `clkin` clocks, falls back to a registered fixed-rate null clock when optional clocks are missing, parses `clock-frequency`, computes BRRA/BRRB candidates, registers clkout providers when requested, and enables the ADG. Runtime clock selection flows from SSI/SRC/CMD callbacks into ADG: SSI asks for an exact main clock; SRC/CMD ask for timesel values based on runtime input/output rates. For conversion paths, `rsnd_adg_get_timesel_ratio()` defaults to SSI word-select timing and only searches clock/divider ratios when runtime rate differs from SRC input or output.

## State and Persistence Behavior

ADG persists cached register images (`ckr`, `brga`, `brgb`) and BRG rates so suspend/resume and runtime re-enable can restore hardware state. `clkin_rate[]` is valid only while clocks are enabled and is deliberately cleared on disable. Clock outputs are registered with the common clock framework and must be unregistered during remove or failed probe cleanup. The null clock is lazily created and explicitly cleaned after ADG clocks are disabled.

## Dependencies and Integration Points

The file depends on common clock framework APIs, OF clock-provider registration, pseudo-register access from `gen.c`, and `rsnd_priv`/`rsnd_mod` helpers from `rsnd.h`. SSI uses ADG for master-clock output, SRC and CMD use ADG for Gen2 timesel routing, and debugfs uses `rsnd_adg_clk_dbg_info()`.

## Risks and Test Signals

Key risks are clock-frequency DT mistakes, approximate CLKI-derived rates, BRG divider edge cases, SSI8/SSI9 special timing, and leaked OF clock providers on probe errors. Tests should exercise DTs with and without ADG clocks, 44.1 kHz and 48 kHz families, suspend/resume, clock-master startup for normal/TDM streams, SRC conversion rates, and debugfs clock output consistency.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/adg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/cmd.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/cmd.c

## Purpose

`cmd.c` implements the R-Car CMD block, the command/routing stage that connects SRC output into CTU, MIX, and DVC processing. It exists only when DVC units are present and is attached by CTU, MIX, or DVC probe callbacks through `rsnd_cmd_attach()`.

## Important APIs, types, and functions

`struct rsnd_cmd` wraps an `rsnd_mod`. `rsnd_cmd_probe()` allocates one CMD module per DVC, initializes each module with `rsnd_cmd_ops`, and records `priv->cmd_nr`. `rsnd_cmd_attach()` connects a CMD module to a stream. `rsnd_cmd_init()` is the main hardware setup path: it computes `CMD_ROUTE_SLCT`, programs `CMD_BUSIF_MODE`, `CMD_BUSIF_DALIGN`, and invokes `rsnd_adg_set_cmd_timsel_gen2()`. `rsnd_cmd_start()` writes `CMD_CTRL = 0x10`; `rsnd_cmd_stop()` clears it. Debugfs can dump the per-CMD SCU register window.

## Control Flow

During CTU/MIX/DVC module probe, the caller attaches a CMD module with a matching ID. At stream init, CMD decides whether the stream uses MIX or only DVC. For MIX, it scans all DAIs and ORs route bits for every SRC feeding the same MIX, relying on the integrator to provide valid compatible paths. Without MIX it uses the current SRC ID and a static `cmd_case` table to choose the route. It then configures BUSIF shifting/alignment from common helpers and programs ADG timing for converted-rate operation. Start/stop are simple control-register toggles.

## State and Persistence Behavior

CMD has no private mutable runtime state beyond the generic `rsnd_mod` lifecycle status. Route state lives in hardware registers and is rebuilt at each init. Module allocation is devm-managed, but `rsnd_cmd_remove()` still calls `rsnd_mod_quit()` for clock/module cleanup symmetry.

## Dependencies and Integration Points

CMD depends on DVC count for allocation, CTU/MIX/DVC for attachment, SRC identity for route selection, `core.c` helpers for BUSIF shift and data alignment, ADG for timing selection, and `gen.c` for pseudo-register access. It is part of the SCU processing path and is sequenced after CTU/MIX/DVC for capture and before them for playback through the common module-order arrays.

## Risks and Test Signals

Risks include invalid DT routes, SRC IDs not covered by `path[]` or `cmd_case[]`, using MIX with incompatible SRC combinations, and capture/playback data alignment regressions. Test signals include successful playback/capture through DVC-only and MIX paths, debugfs route register dumps, SRC+DVC conversion tests, and negative tests for unsupported route IDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/core.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/core.c

## Purpose

`core.c` is the central ASoC platform driver for Renesas R-Car SRU/SCU/SSIU/SSI audio. It binds generation-compatible devices, owns `rsnd_priv`, builds per-DAI playback/capture module chains from DT, implements the ASoC DAI/component callbacks, sequences module lifecycle callbacks, handles PCM constraints and DPCM conversion metadata, and registers/removes the platform driver.

## Important APIs, types, and functions

The file implements core module helpers (`rsnd_mod_init()`, `rsnd_mod_quit()`, `rsnd_mod_name()`, `rsnd_mod_next()`, `rsnd_dai_connect()`), runtime channel/rate/alignment helpers (`rsnd_runtime_channel_*()`, `rsnd_get_adinr_bit()`, `rsnd_get_dalign()`, `rsnd_get_busif_shift()`), DT parsing helpers (`rsnd_parse_connect_common()`, `rsnd_node_count()`, `rsnd_node_fixed_index()`), ASoC DAI ops (`startup`, `shutdown`, `trigger`, `prepare`, `set_fmt`, `set_tdm_slot`, `pcm_new`), component ops (`hw_params`, `hw_free`, `pointer`), and ALSA mixer-control helpers (`rsnd_kctrl_new()` plus `rsnd_kctrl_init_m/s()`). `rsnd_probe()` runs all module probe functions, performs fallback probing, registers components, and enables runtime PM.

## Control Flow

Probe allocates `rsnd_priv`, sets generation flags from OF match data, initializes gen/dma/ssi/ssiu/src/ctu/mix/dvc/cmd/adg/dai subsystems, then calls `rsnd_rdai_continuance_probe()` for each playback/capture stream. If a module probe returns `-EAGAIN`, the stream is disconnected back to SSI-only and reprobed in PIO fallback mode. Runtime `hw_params` clears conversion fields, reads DPCM BE params when dynamic, records converted rate/channel, bounds SRC ratios, then calls module `hw_params`. Trigger start calls module `init`, `start`, and `irq(enable)` under the spinlock; trigger stop disables IRQ, stops, and quits modules. `rsnd_dai_call()` uses per-direction module order arrays and per-module status nibbles to avoid duplicate init/start/hw_params and to call teardown only when matching setup happened.

## State and Persistence Behavior

`rsnd_priv` persists device-level module arrays, DAI driver arrays, generation flags, component split counts, and the spinlock. Each `rsnd_dai_stream` stores its module slots, DMA module, active substream pointer, converted rate/channel, parent SSI status, flags for HDMI/TDM/hw-rule warnings, and optional DMAC device for PCM buffer allocation. Each `rsnd_mod` stores ID, type, ops, clock, private pointer, and lifecycle status. ALSA control values persist in module-owned `rsnd_kctrl_cfg_*` structures and are applied during module init or control updates.

## Dependencies and Integration Points

The file integrates Linux ASoC, ALSA PCM constraints, OF graph/simple-card parsing, PM runtime, and all R-Car submodules. It depends on `gen.c` for register access through submodule callbacks, on ADG/SSI for clock constraints, and on DMA for PCM buffer device selection. It exposes helpers used by all sibling files via `rsnd.h`.

## Risks and Test Signals

Risks cluster around lifecycle ordering, status-nibble imbalance, DPCM conversion bounds, DT route parsing, TDM split detection, pin-sharing symmetric-rate handling, and fallback from DMA to PIO. Test signals include boot/probe on Gen1/2/3/4 DTs, simple-card and audio-graph bindings, start/stop/resume loops, DPCM SRC conversion, multi-SSI and TDM slot settings, shared-pin full-duplex streams, ALSA control duplicate registration, and module debug logs for unexpected negative status transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ctu.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ctu.c

## Purpose

`ctu.c` implements the Channel Count Conversion Unit. It exposes ALSA controls for pass-through channel routing and four matrix rows of scale values, applies those controls to CTU registers, and attaches the matching CMD block so CTU can participate in SCU processing chains.

## Important APIs, types, and functions

`struct rsnd_ctu` stores the embedded module, mixer-control configs for `CTU Pass`, `CTU SV0` through `CTU SV3`, a reset control, a channel cache, and flags. `rsnd_ctu_probe()` allocates one module per DT child, deriving hardware CTU ID as `id / 4` and sub-ID as `id % 4`. `rsnd_ctu_probe_()` attaches CMD by raw module ID. `rsnd_ctu_init()` powers the module, resets/activates it, and calls `rsnd_ctu_value_init()`. `rsnd_ctu_pcm_new()` registers the ALSA controls once per CTU module. `rsnd_ctu_value_reset()` clears software control values when the reset control is set.

## Control Flow

During probe each CTU child gets a clock named by CTU group (`ctu.0`, `ctu.1`, etc.) and an `rsnd_mod` with custom ID callbacks. During PCM creation the control set is installed. At stream init, CTU powers on, pulses `CTU_SWRSR`, initializes the CTU operation, writes channel count, pass routing (`CTU_CPMDR`), matrix row count (`CTU_SCMDR`), and selected scale registers, then cancels initialization. Quit halts the block and powers it off.

## State and Persistence Behavior

Control values live in `rsnd_kctrl_cfg_m/s` fields and persist across stream starts until explicitly changed or reset. Hardware register state is rebuilt at each init. `KCTRL_INITIALIZED` prevents duplicate ALSA control registration, important because shared or mixed paths may call `pcm_new` repeatedly.

## Dependencies and Integration Points

CTU depends on common control registration from `core.c`, pseudo-register access from `gen.c`, CMD attachment from `cmd.c`, and DT connection parsing through `rsnd_parse_connect_ctu()`. It feeds MIX/DVC or CMD paths and uses common module lifecycle sequencing.

## Risks and Test Signals

Risks include raw-vs-group CTU ID confusion, duplicated controls across mixed paths, invalid pass/matrix combinations, and CTU plus TDM split misuse noted by `core.c`. Tests should cover control creation, amixer-driven matrix changes before and during stream setup, reset behavior, CTU00-CTU13 ID mapping, and audio validation for channel swap/upmix/downmix cases.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ctu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/debugfs.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/debugfs.c

## Purpose

`debugfs.c` provides optional debugfs views for R-Car sound DAIs and modules when `CONFIG_DEBUG_FS` is enabled. It lets developers inspect ADG clock state, per-module lifecycle status, and module-specific register windows under the ASoC component debugfs tree.

## Important APIs, types, and functions

`rsnd_debugfs_probe()` creates `rdaiN/playback` and `rdaiN/capture` files under the component debugfs root, skipping Gen1. `rsnd_debugfs_show()` emits ADG clock debug information, iterates modules in the selected stream, prints module name/status, and calls each module's `debug_info` callback. `rsnd_debugfs_reg_show()` prints raw 32-bit register rows from a base physical/MMIO pair. `rsnd_debugfs_mod_reg_show()` resolves module base physical and virtual addresses through `gen.c` and delegates to the raw register dump helper.

## Control Flow

The component driver in `core.c` points `.probe` at `rsnd_debugfs_probe`. Opening a debugfs file invokes the generated show function with the relevant `rsnd_dai_stream` as private data. Register dumps are passive reads using `__raw_readl()` and do not acquire the audio spinlock.

## State and Persistence Behavior

This file does not own persistent driver state beyond debugfs dentries automatically cleaned by ASoC component cleanup. It reads live module status and hardware registers, so output reflects the current stream state and may change while audio is running.

## Dependencies and Integration Points

It depends on debugfs, seq_file, `rsnd_adg_clk_dbg_info()`, `for_each_rsnd_mod()`, module `get_status` callbacks, and `rsnd_gen_get_phy_addr()/rsnd_gen_get_base_addr()`. Each module file can contribute its own debug register dump through `struct rsnd_mod_ops.debug_info`.

## Risks and Test Signals

Risks are NULL assumptions when a stream lacks SSI, racing live register changes, and incorrect base/offset ranges in module debug callbacks. Test signals include mounted debugfs paths for Gen2/Gen3/Gen4 devices, readable playback/capture files for every DAI, sane ADG and status output while idle/running, and no crashes for DAIs missing optional modules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/dma.c

## Purpose

`dma.c` implements R-Car audio DMA integration. It supports normal DMAEngine transfers between memory and a module, Audio-DMAC peri-peri transfers between hardware modules, DMA address calculation for Gen2/Gen4, DMA channel discovery from DT, and fallback signaling to PIO when DMA cannot be used.

## Important APIs, types, and functions

`struct rsnd_dma_ctrl` stores Audio-DMAC PP MMIO state and allocation counters. `struct rsnd_dma` is a synthetic module carrying source/destination modules and DMA addresses plus mode-specific state. `rsnd_dma_probe()` creates the controller for Gen2+ and maps `audmapp` unless Gen4. `rsnd_dma_attach()` allocates and connects an `AUDMA` or `AUDMAPP` module. `rsnd_dma_alloc()` chooses normal vs peri-peri DMA based on whether both endpoints are hardware modules. `rsnd_dma_of_path()` derives the adjacent transfer endpoints from the stream's SSI/SRC/CTU/MIX/DVC chain. `rsnd_dma_request_channel()` walks DT child nodes by fixed index and requests named DMA channels. `rsnd_dmaen_*` implements DMAEngine open/config/start/stop/pointer; `rsnd_dmapp_*` programs peri-peri registers.

## Control Flow

Submodules request DMA attachment during their probe callbacks. The DMA layer first determines the logical path, chooses Audio-DMAC PP for hardware-to-hardware links and DMAEngine for memory-facing links, initializes a synthetic `rsnd_mod`, then runs the relevant attach path. Normal DMA probes channel availability early, records the DMA device for IPMMU-aware buffer allocation, releases the probe channel, and opens a real channel later in `.prepare` because DMAEngine channel operations may sleep. At stream start, normal DMA configures source/destination bus addresses and widths before triggering DMAEngine; peri-peri DMA writes source, destination, and channel control registers directly.

## State and Persistence Behavior

The controller tracks monotonically allocated DMA IDs. Each stream keeps a pointer to its DMA module in `io->dma`. Normal DMA keeps the live DMAEngine channel only between prepare and cleanup; cleanup releases it outside the trigger spinlock. Peri-peri DMA keeps fixed PP ID and CHCR values. DMA addresses are computed once during allocation from SoC base physical addresses and module IDs.

## Dependencies and Integration Points

The file depends on OF DMA, DMAEngine PCM helpers, module DMA request callbacks from SSI/SSIU/SRC/DVC, generation base addresses from `gen.c`, and common stream/module helpers from `core.c`. It feeds ASoC pointer and trigger behavior through synthetic module ops in the same lifecycle sequence as hardware blocks.

## Risks and Test Signals

Risks include fragile Gen2 address formulas, unsupported SSI9 BUSIF4-7, Gen4 non-SSI0 rejection, sleeping DMAEngine APIs accidentally called under spinlock, channel-name mismatches, and fallback not correctly reconnecting SSI-only PIO paths. Tests should cover DMA and PIO fallback probe, memory-to-SSI, memory-to-SRC-to-SSI, SRC-to-DVC peri-peri links, capture and playback address selection, mono bus-width selection, and DMA pointer progression.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/dvc.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/dvc.c

## Purpose

`dvc.c` implements the Digital Volume Control block. It creates playback/capture volume, mute, and volume-ramp ALSA controls, programs DVC registers during stream init and control updates, and attaches the matching CMD block for SCU routing.

## Important APIs, types, and functions

`struct rsnd_dvc` stores the embedded module and control configs for per-channel volume, per-channel mute, ramp enable, ramp-up rate, and ramp-down rate. `rsnd_dvc_probe()` allocates DT-described DVC modules and initializes their clocks. `rsnd_dvc_probe_()` attaches CMD by module ID. `rsnd_dvc_pcm_new()` registers controls named differently for playback (`DVC Out ...`) and capture (`DVC In ...`). `rsnd_dvc_volume_init()` programs initial ADINR, control, ramp, and volume registers. `rsnd_dvc_volume_update()` safely updates mute, ramp, and digital-volume registers by disabling/enabling DVC register access around the update.

## Control Flow

At module init, DVC powers on, resets, initializes volume/ramp state, applies current controls, and enables register access. ALSA control writes update software values through `core.c` kcontrol callbacks, then invoke `rsnd_dvc_volume_update()` immediately. Quit halts DVC and powers off. DMA request support returns the DVC `tx` channel for paths where DVC is DMA-adjacent.

## State and Persistence Behavior

Volume, mute, and ramp settings persist in module-owned `rsnd_kctrl_cfg_*` structures. Hardware state is rebuilt each stream start and can be updated while controls are accepted. Ramp mode temporarily writes maximum volume values to volume registers and uses derived ramp parameters for hardware ramping.

## Dependencies and Integration Points

DVC uses common control registration, common ADINR/channel helpers, CMD attachment, DMA channel request helpers, and pseudo-register access. It can be used after SRC/CTU/MIX and before memory or SSI depending on stream direction.

## Risks and Test Signals

Risks include incorrect channel count for controls, ramp scaling noted by the FIXME, stale control state after rebinding, and capture/playback alignment differences. Test signals include amixer volume/mute/ramp changes before and during playback/capture, DVC with and without SRC conversion, DMA channel availability, debugfs DVC register dumps, and no duplicate controls after card rebind.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/dvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/gen.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/gen.c

## Purpose

`gen.c` is the generation-specific register indirection layer. It maps logical `enum rsnd_reg` pseudo registers to MMIO regmap fields for Gen1, Gen2/Gen3, and Gen4, hiding different SRU/SCU/SSIU/SSI/ADG register layouts from the functional modules.

## Important APIs, types, and functions

`struct rsnd_gen` stores MMIO bases, physical resources, regmaps, per-pseudo-register `regmap_field` handles, and register names. `rsnd_mod_read()`, `rsnd_mod_write()`, and `rsnd_mod_bset()` are the exported accessors used everywhere else. `rsnd_gen_get_phy_addr()` and debug-only `rsnd_gen_get_base_addr()` expose base addresses for DMA calculations and debugfs. `_rsnd_gen_regmap_init()` maps a named resource, creates a regmap, allocates fields from a config table, and records register names. `rsnd_gen_probe()` chooses `rsnd_gen1_probe()`, `rsnd_gen2_probe()`, or `rsnd_gen4_probe()` from `rsnd_priv` generation flags.

## Control Flow

Generation probe allocates `struct rsnd_gen`, then initializes the resource groups required by that generation. Gen1 maps SSI and ADG. Gen2/Gen3 map SSI, SSIU, SCU, and ADG with 10 module IDs. Gen4 maps one SSIU, one SSI, ADG, and an SDMC resource with an empty register table. At runtime, module accessors verify the pseudo register exists for the generation, choose the instance index using `ops->id_cmd` when present or `rsnd_mod_id()` otherwise, and call regmap-field read/write/update operations.

## State and Persistence Behavior

MMIO mappings and regmap fields are devm-managed and persist for the device lifetime. The file does not cache register values; it provides forced writes/updates to hardware. Unsupported pseudo registers are logged and treated as no-op reads/writes rather than fatal errors.

## Dependencies and Integration Points

It depends on platform resources named `ssi`, `ssiu`, `scu`, `adg`, and `sdmc`, Linux regmap MMIO, and the pseudo-register enumeration in `rsnd.h`. ADG, SSI, SSIU, SRC, CMD, CTU, MIX, DVC, DMA, and debugfs all depend on these accessors.

## Risks and Test Signals

Risks include incorrect offsets or id strides, missing resource names in DT, silent no-op behavior for unsupported registers, and module ID callback mistakes. Tests should include probe on each generation, register smoke tests via debugfs, audio paths that touch every pseudo-register family, DMA physical address sanity checks, and negative DT tests for missing resources.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/mix.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/mix.c

## Purpose

`mix.c` implements the R-Car MIX block, which combines up to four CTU/SRC inputs into one stream with per-input volume and optional volume ramping. It registers ALSA controls for the relevant MIX input lane and shared ramp controls.

## Important APIs, types, and functions

`struct rsnd_mix` stores the module plus control configs for volume lanes A-D, ramp enable, ramp-up rate, ramp-down rate, and flags recording which lanes exist. `rsnd_mix_probe()` allocates DT-described MIX modules and initializes clocks. `rsnd_mix_probe_()` attaches the matching CMD module. `rsnd_mix_pcm_new()` maps SRC IDs to MIX volume lanes, creates a `MIX Playback Volume` control for that lane, initializes the software value to max, and installs shared ramp controls once. `rsnd_mix_volume_init()` and `rsnd_mix_volume_update()` program MIX channel count, ramp, lane volumes, and update enable state.

## Control Flow

On stream init, MIX powers on, resets/activates, writes general info and ramp settings, writes volume registers, then enables dB setting. ALSA control writes update software values and call `rsnd_mix_volume_update()` to disable dB setting, rewrite lane volumes, and re-enable it. Volume lane selection is based on the connected SRC ID: SRC3/6 to A, SRC4/9 to B, SRC0/1 to C, and SRC2/5 to D.

## State and Persistence Behavior

Per-lane and ramp control values persist in `struct rsnd_mix`. `ONCE_KCTRL_INITIALIZED` prevents duplicate shared ramp controls while allowing multiple lane controls for streams sharing one MIX. Hardware state is rebuilt on init and can be updated by control writes.

## Dependencies and Integration Points

MIX depends on SRC identity, CTU/CMD routing, common control helpers, `volume_ramp_rate[]` from `core.c`, and SCU pseudo-register access. It is primarily a playback-side multi-source integration point.

## Risks and Test Signals

Risks include unsupported SRC-to-lane mappings, duplicated or missing controls for shared MIX paths, ramp control scope across multiple inputs, and route assumptions delegated to the integrator. Tests should run two or more DAIs feeding one MIX, verify independent lane volumes, exercise ramp changes during playback, inspect `CMD_ROUTE_SLCT`, and validate error handling for unsupported SRC IDs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/mix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/msiof.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/msiof.c

## Purpose

`msiof.c` is a standalone ASoC platform driver that uses the R-Car MSIOF SPI-oriented hardware as an I2S-like audio interface on Gen4. It is separate from the `rsnd` module graph and supports DMAEngine playback/capture in clock/frame consumer mode only.

## Important APIs, types, and functions

`struct msiof_priv` stores device/MMIO/reset state, active substreams, a spinlock, physical base address, active stream count, error counters, and format flags. `msiof_probe()` validates sound-mode graph presence, maps MMIO, gets reset and IRQ, asserts reset, registers the IRQ handler, enables runtime PM, and registers the component plus one DAI. `msiof_dai_set_fmt()` accepts only clock/frame consumer mode, NB_NF polarity, and I2S or left-justified format. Component callbacks implement DMA open/close, PCM buffer preallocation, `hw_params` DMA slave config, trigger start/stop, and DMA pointer. `msiof_hw_start()` and `msiof_hw_stop()` program MSIOF registers and reset state. `msiof_interrupt()` records FIFO/frame-sync errors.

## Control Flow

Open requests the `rx` or `tx` DMA channel and opens DMAEngine PCM. `hw_params` converts ALSA params to DMA slave config and points DMA to `SITFDR`/`SIRFDR`. Trigger start records the active substream, deasserts reset for the first user, starts DMA, programs both TX and RX mode registers to avoid cross-direction FSERR, enables DMA/error interrupts for the target direction, clears status, and enables TXE or RXE. Trigger stop disables interrupts, clears TXE/RXE, stops DMA, logs accumulated errors, decrements the active count, and asserts reset when both directions are idle.

## State and Persistence Behavior

The driver persists active substream pointers under `priv->lock`, shared reset state through `count`, per-direction error counters, and the I2S data-delay flag. It deliberately ignores the first FSERR by initializing `err_syc` to `-1` on start and normalizing it on stop. It does not stop streams on error currently; `snd_pcm_stop_xrun()` calls are commented out and errors are counted/logged.

## Dependencies and Integration Points

It depends on `linux/spi/sh_msiof.h` register definitions, OF graph to distinguish sound mode from SPI mode, OF DMA channel names `rx` and `tx`, reset controls, DMAEngine PCM helpers, and ASoC component/DAI registration. It exposes a simple `msiof-dai` with 2-channel 16/32-bit audio and symmetric rate/channel/sample bits.

## Risks and Test Signals

Risks are inherent in consumer-clock operation: unavoidable FSERR windows, possible R/L capture reversal, no 24-bit format due to missing data shift, and unsupported provider mode. Other risks include reset coordination for full-duplex, not stopping on hardware errors, DMA channel leaks on open failure, and register updates while clocks are present. Tests should cover I2S and left-justified formats, playback/capture/full-duplex start-stop loops, suspend/resume-like reset cycles, DMA pointer movement, error-counter logging, and rejection of provider/inverted/24-bit configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/msiof.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/rsnd.h -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/rsnd.h

## Purpose

`rsnd.h` is the shared internal interface for the R-Car sound driver. It defines pseudo registers, module types and lifecycle operations, stream/DAI/private data structures, DT node names, generation flags, kcontrol helpers, and all cross-file function prototypes.

## Important APIs, types, and functions

`enum rsnd_reg` defines logical register IDs for SCU/SRC/CMD/CTU/MIX/DVC, ADG, SSIU, and SSI, with helper macros such as `SRCIN_TIMSEL(i)`, `CTU_SVxxR(i,j)`, and `SSI_BUSIF_MODE(i)`. `enum rsnd_mod_type` establishes module slots and ordering identifiers from synthetic DMA modules through SSIU. `struct rsnd_mod_ops` is the lifecycle vtable, including DMA request, probe/remove, init/quit, start/stop, IRQ, PCM creation, hw params/free, pointer, fallback, prepare/cleanup, status, ID overrides, and debugfs callbacks. `struct rsnd_mod`, `struct rsnd_dai_stream`, `struct rsnd_dai`, `struct rsnd_priv`, and `struct rsnd_kctrl_cfg*` define the main in-memory object model. The header also declares subsystem probe/remove APIs and convenience macros for stream direction, module lookup, and generation checks.

## Control Flow

The header enables the common pattern used by all modules: subsystem probe initializes arrays inside `rsnd_priv`, DT parsing connects module pointers into each `rsnd_dai_stream`, and `core.c` invokes lifecycle callbacks through `rsnd_mod_ops` in direction-specific order. Register users call `rsnd_mod_read/write/bset()` against pseudo registers instead of generation-specific offsets.

## State and Persistence Behavior

The structures declared here define all persistent driver state. `rsnd_priv` owns device-wide module arrays and DAI drivers. `rsnd_dai_stream` owns active stream links, conversion metadata, DMA module, flags, and runtime substream pointer. `rsnd_mod` owns lifecycle status and clock state. Kcontrol configs persist ALSA control values and update hooks.

## Dependencies and Integration Points

The header depends on Linux clock, device, DMA, IO, list, module, OF, workqueue, and ASoC/PCM headers. Every R-Car driver source in this directory, except standalone `msiof.c`, includes it. It also exposes debugfs helpers conditionally.

## Risks and Test Signals

Risks include ABI drift between vtable definitions and users, pseudo-register additions not mapped in `gen.c`, status-nibble macro errors, and misuse of stream/module lookup macros with NULL modules. Test signals include full-tree compilation with `CONFIG_DEBUG_FS` on/off, all generation probes, lifecycle balance under repeated triggers, and static analysis for unchecked module pointers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/rsnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/src.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/src.c

## Purpose

`src.c` implements the Sampling Rate Converter module. It configures SRC hardware for fixed or DPCM-derived rate conversion, exposes optional synchronous conversion controls, manages SRC interrupts, attaches DMA, and provides converted-rate helpers used by SSI/ADG/CMD.

## Important APIs, types, and functions

`struct rsnd_src` stores the module, DMA module, synchronous-conversion enable/rate controls, current sync rate, and IRQ. `rsnd_src_get_rate()` reports input or output rate based on stream direction and conversion state. `rsnd_src_init_convert_rate()` calculates register settings for ADINR, IFSCR, SRCCR, route mode, BSDSR/BSISR, BUSIF mode/alignment, and ADG timesel. `rsnd_src_set_convert_rate()` updates `SRC_IFSVR` gradually in synchronous mode. `rsnd_src_irq()`, `rsnd_src_error_occurred()`, and `rsnd_src_interrupt()` manage overflow/underflow status. `rsnd_src_pcm_new()` registers `SRC In/Out Rate Switch` and `SRC In/Out Rate` controls when supported. `rsnd_src_probe()` allocates modules, IRQs, clocks, and ops.

## Control Flow

Probe creates SRC modules from the `rcar_sound,src` node. During stream probing, `rsnd_src_probe_()` requests an IRQ if available and attaches DMA. At init, SRC clears synchronous conversion state, powers on, activates, computes conversion settings from runtime and DPCM metadata, writes registers, sets ADG timesel, and clears status. Start writes `SRC_CTRL`, with a workaround for DVC plus non-sync conversion. IRQ enable writes per-SRC interrupt bits unless no IRQ or disabled. Interrupts scan all streams using the module and stop the PCM on SRC error after clearing status.

## State and Persistence Behavior

Synchronous conversion controls persist in `sen` and `sync`, but `sync.val` and `current_sync_rate` are reset on init/quit. `current_sync_rate` avoids redundant `SRC_IFSVR` writes and tracks gradual runtime adjustments. DMA module state is retained in `src->dma` after first attachment.

## Dependencies and Integration Points

SRC depends on ADG timing, DMA attachment, common channel/data-alignment helpers, ALSA controls, DPCM conversion metadata from `core.c`, SCU pseudo registers, and optional CMD/DVC interactions. It is a central rate-conversion module in both playback and capture paths.

## Risks and Test Signals

Risks include SRC ratio limits, channel-pattern tables that vary by SRC ID and E3 SoC variant, synchronous-conversion overflow workaround behavior, runtime control updates while streaming, and DPCM BE/FE mismatch handling. Tests should cover no-conversion, upsample/downsample, DPCM converted rate/channel, synchronous rate-control updates, SRC interrupt error handling, and unsupported channel/rate combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/src.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ssi.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ssi.c

## Purpose

`ssi.c` implements the Serial Sound Interface transport modules. It handles SSI clock master setup through ADG, serial format/register configuration, DMA and PIO transfer modes, IRQ handling, multi-SSI and shared-pin support, parent SSI clocking, DT parsing, and PIO fallback.

## Important APIs, types, and functions

`struct rsnd_ssi` stores module state, control-register fragments, word-select state, runtime channel/rate, IRQ, user count, and PIO pointer counters. Public helpers include `rsnd_ssi_use_busif()`, `rsnd_ssi_clk_query()`, `rsnd_ssi_multi_secondaries_runtime()`, `rsnd_ssi_is_dma_mode()`, `__rsnd_ssi_is_pin_sharing()`, `rsnd_parse_connect_ssi()`, and `rsnd_ssi_mod_get()`. Core callbacks include `rsnd_ssi_init()/quit()`, `rsnd_ssi_start()/stop()`, `rsnd_ssi_irq()`, `rsnd_ssi_hw_params()`, DMA probe/fallback, PIO init/pointer/interrupt, and common IRQ request/remove.

## Control Flow

Probe parses each `ssi-N` DT child, gets `ssi.N` clock and IRQ, records `shared-pin`, `no-busif`, and `pio-transfer`, then initializes modules in DMA or PIO mode. DT connection parsing fills the primary SSI slot and optional multi-SSI secondary slots, expanding DAI max channels and SSI lane count. At PCM creation, shared-pin clock parents can be attached. Init starts a master clock when needed, increments `usrcnt`, powers the module, builds SSICR/SSIWSR settings, writes registers, and clears status. Start enables SSI unless multi-SSI control is delegated to SSIU or the module is only a parent. Stop drains playback, disables SSI, and waits for idle. DMA probe attaches DMA; if DMA allocation fails with `-EAGAIN`, fallback switches ops to PIO and the core reprobes.

## State and Persistence Behavior

`usrcnt` protects shared clock/module state across parent/child and multi-path users. Register fragments (`cr_own`, `cr_clk`, `cr_mode`, `cr_en`, `wsr`) are rebuilt at init and cleared when the last user quits. PIO state (`byte_pos`, `byte_per_period`, `next_period_byte`) tracks software PCM position. Parent SSI lifecycle status is stored in the stream rather than the module to handle shared-pin full-duplex cases.

## Dependencies and Integration Points

SSI depends on ADG for master clock selection, SSIU for BUSIF and multi-SSI/TDM control, DMA for transfer attachment, core format/TDM/channel helpers, OF IRQ/DT parsing, and ASoC PCM runtime state. SSI interrupts also delegate BUSIF error clearing to SSIU.

## Risks and Test Signals

Risks include clock-rate search failures, shared-pin parent status imbalance, multi-SSI synchronization, TDM split fixed-width handling, PIO byte-position correctness, DMA-to-PIO fallback, and underflow/overflow handling. Tests should cover DMA and PIO playback/capture, full-duplex shared pins, multi-lane TDM, TDM split, 16/24/32-bit formats, clock-master and clock-consumer modes, IRQ xrun paths, and repeated trigger cycles.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ssi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ssiu.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ssiu.c

## Purpose

`ssiu.c` implements the Serial Sound Interface Unit, especially BUSIF configuration, TDM/multi-SSI mode bits, HDMI lane selection, BUSIF error interrupt/status handling, DMA channel requests, and compatibility mapping between old SSI-only DTs and explicit `rcar_sound,ssiu` nodes.

## Important APIs, types, and functions

`struct rsnd_ssiu` stores the module, per-BUSIF lifecycle status, user count, hardware SSI ID, and BUSIF sub-ID. `rsnd_ssiu_probe()` allocates modules either from explicit SSIU children or from SSI count for compatibility, chooses Gen1 or Gen2-style ops, and maps flat child indices to `(id,id_sub)` using generation tables. `rsnd_parse_connect_ssiu()` connects explicit SSIU phandles or compatible BUSIF0 modules. `rsnd_ssiu_init()` configures SSI mode registers and error interrupts. `rsnd_ssiu_init_gen2()` adds TDM mode, BUSIF ADINR/MODE/DALIGN setup, and HDMI selection. `rsnd_ssiu_start_gen2()`/`stop_gen2()` enable BUSIF and multi-SSI control. `rsnd_ssiu_busif_err_status_clear()` is called from SSI IRQ handling.

## Control Flow

Probe determines module count and ID callbacks based on generation and DT shape. Connection parsing prefers explicit SSIU nodes; otherwise DMA-mode SSI streams get BUSIF0 for backward compatibility. During init, SSIU clears previous BUSIF errors, configures `SSI_MODE0` for BUSIF use, sets sharing/synchronization bits for pin sharing and multi-SSI, enables BUSIF error interrupts, writes TDM extend/split mode, configures BUSIF registers if used, and selects HDMI output lanes when stream flags indicate HDMI. Start enables the selected BUSIF and, for multi-SSI, writes `SSI_CONTROL`. Stop disables BUSIF, decrements users, and clears multi-SSI control when the last user stops.

## State and Persistence Behavior

Per-BUSIF status is stored in `busif_status[]`, so lifecycle tracking is per sub-ID rather than per SSIU module object. `usrcnt` guards shared multi-SSI control teardown. Hardware mode and BUSIF registers are rebuilt at init.

## Dependencies and Integration Points

SSIU depends on SSI runtime state, core TDM/HDMI flags, BUSIF alignment helpers, DMA channel request helpers, pseudo-register mapping, and generation-specific BUSIF index tables. It is tightly coupled to SSI interrupt handling for overrun/underrun reporting.

## Risks and Test Signals

Risks include Gen2/Gen3/Gen4 flat-index mapping mistakes, SSI9 special BUSIF registers, shared-pin/multi-SSI bit combinations, user-count underflow, and compatibility behavior when DT lacks `rcar_sound,ssiu`. Tests should cover explicit and legacy DTs, BUSIF0-7 where supported, TDM extend and split modes, HDMI0/HDMI1 lane selection, multi-SSI start/stop, and BUSIF error IRQ clearing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rcar/ssiu.c -->
