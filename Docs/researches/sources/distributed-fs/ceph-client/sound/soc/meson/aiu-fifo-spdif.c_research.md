# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo-spdif.c

Purpose: Specializes the shared AIU FIFO implementation for SPDIF playback, configuring IEC958 FIFO/DCU behavior, period-byte IRQ generation, memory mode, and DAI probe state.

Important APIs and functions: Exported `aiu_fifo_spdif_dai_ops` composes common FIFO callbacks with SPDIF-specific `trigger`, `prepare`, `hw_params`, and probe. `aiu_fifo_spdif_dai_probe()` binds FIFO state to `AIU_MEM_IEC958_START`, SPDIF pclk, SPDIF IRQ, and SPDIF hardware limits. Helpers are `fifo_spdif_dcu_enable()`, `fifo_spdif_trigger()`, `fifo_spdif_prepare()`, and `fifo_spdif_hw_params()`.

Control flow: Prepare resets the common FIFO and toggles `AIU_MEM_IEC958_BUF_CNTL_INIT`. `hw_params` programs common DMA boundaries, configures DDR-read linear mode with optional 16-bit mode, writes bytes-per-frame/period interrupt count to `AIU_IEC958_BPF`, and disables compressed-sync default behavior for PCM mode. Trigger first enables/disables the common FIFO, then enables or disables the IEC958 DCU block.

State and persistence: Playback FIFO private data records the SPDIF memory offset and IRQ. Hardware state persists in `AIU_MEM_IEC958_CONTROL`, `AIU_IEC958_BPF`, and `AIU_IEC958_DCU_FF_CTRL`.

Dependencies and integration points: Uses the common AIU FIFO module, AIU SPDIF clock/IRQ data, and routes into the AIU SPDIF encoder DAI.

Risks: The probe defines `AIU_FIFO_SPDIF_BLOCK` as the PCM period minimum but sets `fifo_block` to 1 for common DMA boundary math; changing either without understanding the hardware can alter period constraints. Compressed IEC958 defaults are explicitly disabled for PCM, so non-PCM support would need new logic. Only 16- and 32-bit physical widths are supported.

Test signals: SPDIF PCM playback, pause/resume/stop trigger sequencing, IRQ cadence matching period bytes, S16 and S24/S32 containers, and regmap tracing of `AIU_MEM_IEC958_*` and `AIU_IEC958_DCU_FF_CTRL`.
