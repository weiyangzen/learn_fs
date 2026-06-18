# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_easrc.c` implements the NXP Enhanced Asynchronous Sample Rate Converter ASoC driver. It exposes a CPU DAI for playback/capture sample-rate conversion, registers the common ASRC m2m platform hooks, loads coefficient firmware, programs resampler and prefilter coefficient memories, manages up to four eASRC contexts with slot allocation, and integrates runtime/system PM around the eASRC memory clock and regmap cache. The source was read as a complete 2425-line file.

## Important APIs, Types, and Functions

Important ALSA controls include per-context dither, IEC958 validity, IEC958 bits-per-sample, and IEC958 channel-status register get/put handlers. Core coefficient and ratio helpers are `fsl_easrc_set_rs_ratio`, `fsl_easrc_normalize_rates`, `fsl_easrc_coeff_mem_ptr_reset`, `fsl_easrc_resampler_config`, `fsl_easrc_normalize_filter`, `fsl_easrc_write_pf_coeff_mem`, and `fsl_easrc_prefilter_config`. Context lifecycle is handled by `fsl_easrc_request_context`, `fsl_easrc_release_context`, `fsl_easrc_config_context`, `fsl_easrc_start_context`, and `fsl_easrc_stop_context`. DAI entry points are `startup`, `trigger`, `hw_params`, `hw_free`, and `dai_probe`. m2m integration is provided through `fsl_easrc_m2m_prepare`, `m2m_start`, `m2m_stop`, `m2m_calc_out_len`, `m2m_get_maxburst`, pair suspend/resume, ratio modification, and capability reporting.

## Control Flow

Probe allocates `struct fsl_asrc` plus `struct fsl_easrc_priv`, maps registers, creates a regmap, requests the IRQ, obtains the `mem` clock, reads `fsl,asrc-rate`, `fsl,asrc-format`, and `firmware-name`, initializes common ASRC callbacks, enables runtime PM, registers the eASRC DAI component and common ASRC platform component, then initializes the m2m device. Runtime resume enables the memory clock, syncs the regcache, loads firmware once per resume epoch, programs global resampler coefficients, and restores active context coefficient state. PCM `hw_params` requests a context, derives input/output rates and formats depending on playback versus capture, writes format fields, configures ratio, prefilter, slot allocation, watermarks, and FIFO organization. Trigger start enables FIFO watermark DMA requests and the context; trigger stop requests a run stop, drains output FIFO samples until run-stop-done or timeout, then clears enable/DMA bits.

## State and Persistence Behavior

Driver state lives in the platform device drvdata, the common `fsl_asrc` object, `fsl_easrc_priv`, and per-context `fsl_easrc_ctx_priv`. Firmware is requested by name and kept as pointers into the firmware image for interpolation and prefilter tables. Runtime suspend sets regcache cache-only, disables `mem_clk`, and marks `firmware_loaded` false so coefficient RAM is reloaded on resume. Context allocation state is protected with `easrc->lock`, including `easrc->pair[]`, `channel_avail`, and the two-slot-per-pipe allocation table. No file-backed persistence is present; persistent behavior is hardware register state plus regcache and loaded firmware pointers.

## Dependencies and Integration Points

The file depends on Linux platform, firmware, clk, IRQ, regmap, runtime PM, DMA, and ALSA ASoC/PCM APIs. It includes `fsl_easrc.h` and `imx-pcm.h`, and it registers with the shared Freescale ASRC layer through callbacks in `struct fsl_asrc` and `fsl_asrc_m2m_init/exit/suspend/resume`. Device-tree bindings provide compatible `fsl,imx8mn-easrc`, ASRC output rate/format, firmware name, clocks, IRQ, and DMA channel names like `ctx0_rx` and `ctx0_tx`.

## Risks and Edge Cases

The firmware format is trusted after `request_firmware`; malformed counts or coefficient layout can make the parsed pointer arithmetic unsafe unless validated elsewhere. Ratio arithmetic uses fixed-point shifts and `do_div`, so extreme rates, taps, or ratio modifiers can overflow or exceed hardware range. Slot allocation splits large channel counts across processing slots and depends on prefilter memory accounting; off-by-one errors directly affect channel routing. `fsl_easrc_stop_context` has a bounded drain loop and only warns on timeout. The source snapshot also shows apparent compile-risk typos such as an extra brace in the DAI driver initializer; those should be checked against the actual build tree.

## Test Signals

Useful signals include kernel build coverage with `CONFIG_SND_SOC_FSL_EASRC`, device-tree probe with valid firmware, ALSA PCM playback and capture at all constrained rates, IEC958 capture format tests, m2m conversion tests for integer/float and rate-up/rate-down paths, suspend/resume while contexts are active, IRQ injection or stress tests for FIFO overrun/underrun, and DMA channel-name verification.
