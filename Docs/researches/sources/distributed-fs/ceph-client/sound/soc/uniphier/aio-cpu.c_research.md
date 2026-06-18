<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-cpu.c -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-cpu.c

## Purpose
UniPhier AIO ASoC CPU DAI/component driver. It binds SoC-specific DAI specs to common AIO hardware helpers, handles sysclk/PLL/format selection, PCM lifecycle, compressed DAI creation hooks, suspend/resume, mixer volume controls, and platform probe/remove.

## APIs, Types, and Functions
Exports DAI ops tables for LD11 and PXs2 I2S/SPDIF variants, with `*_ops2` enabling compressed streams. Exports `uniphier_aio_probe()` and `uniphier_aio_remove()` for SoC glue drivers. Important helpers are `is_valid_pll()`, `find_volume()`, `find_spec()`, `find_divider()`, `uniphier_aio_set_sysclk()`, `uniphier_aio_set_pll()`, `uniphier_aio_set_fmt()`, PCM startup/shutdown/hw_params/hw_free/prepare, DAI probe/remove and LD11/PXs2 PLL initialization, suspend/resume helpers, and volume get/put.

## Control Flow, State, and Persistence
Platform probe obtains chip spec from OF match data, optional syscon regmap, `aio` clock, shared reset, allocates AIO instances and PLL table copies, initializes per-substream locks and default I2S format, enables clock/reset, registers the component/DAIs, and registers the AIO DMA platform. DAI probe matches substreams to SoC specs by DAI name/group and direction, assigns switch-matrix data, initializes volumes, enables IEC output, initializes chip registers, and marks chip active. PCM startup stores the substream and initializes mapping. `hw_params` supports selected rates, auto-selects an audio PLL divider, stores params, sets volume, and resets port/SRC. Prepare programs port/SRC/interface and converter blocks. Suspend disables clock/reset when active DAIs are quiesced; resume restores chip/substream mapping and resets configured blocks.

## Dependencies and Integration
Depends on `aio.h` SoC specs, AIO core helpers, AIO DMA platform registration, regmap syscon, clk/reset frameworks, OF match data, ASoC component/DAI APIs, and ALSA controls. LD11/PXs2 device drivers provide DAI arrays and specs used here.

## Risks and Test Signals
Risks include `uniphier_aio_vol_put()` returning 0 even after changing volume, resume accumulating bitwise OR of negative return codes, limited `hw_params` rates despite core supporting more FS values, auto-PLL search depending on enabled PLL table, compressed support tied only to specific SPDIF ops tables, and clock/reset reference counting via `num_wup_aios`. Test signals are probe/remove with optional syscon absent/present, I2S and SPDIF DAIs on LD11/PXs2, PLL set_sysclk auto-selection, PCM startup/hw_params/prepare for 32/44.1/48 kHz families, compressed DAI creation, volume controls for all output ports, and suspend/resume with active and inactive DAIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-cpu.c -->
