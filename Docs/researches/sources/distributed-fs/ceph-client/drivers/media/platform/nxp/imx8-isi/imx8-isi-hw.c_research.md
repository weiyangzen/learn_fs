# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-hw.c

## Purpose
`imx8-isi-hw.c` contains the low-level ISI channel register programming and channel resource management. It programs input and output DMA addresses, memory-to-memory triggers, scaling, crop, color-space conversion, alpha, flip, panic thresholds, channel control, interrupts, reset/clock state, and line-buffer chaining.

## Important APIs, Types, and Functions
Buffer APIs are `mxc_isi_channel_set_inbuf()`, `mxc_isi_channel_set_outbuf()`, and `mxc_isi_channel_m2m_start()`. Pipeline configuration APIs include `mxc_isi_channel_config()`, `mxc_isi_channel_set_input_format()`, `mxc_isi_channel_set_output_format()`, `mxc_isi_channel_set_alpha()`, and `mxc_isi_channel_set_flip()`. IRQ APIs include `mxc_isi_channel_irq_status()` and `mxc_isi_channel_irq_clear()`. Lifecycle and resource APIs include `mxc_isi_channel_acquire()`, `mxc_isi_channel_release()`, `mxc_isi_channel_get()`, `mxc_isi_channel_put()`, `mxc_isi_channel_enable()`, `mxc_isi_channel_disable()`, `mxc_isi_channel_chain()`, and `mxc_isi_channel_unchain()`.

Private helpers cover scaling ratio selection, scaler setup, crop setup, CSC coefficient programming, panic threshold programming, channel control register updates, IRQ enable/disable, and software reset. Static CSC coefficient tables implement YUV-to-RGB and RGB-to-YUV conversions.

## Control Flow
Users of a pipe acquire required resources with `mxc_isi_channel_acquire()`, selecting output-buffer resource always and line-buffer resource unless the channel can bypass processing. `mxc_isi_channel_get()` resets and clocks the channel on first use. Configuration writes input frame size, scaler decimation and factors, crop window, CSC mode and coefficients, panic thresholds, input source selection, bypass bit, chain bit, and memory/device source type. Format helpers program memory input type, input pitch, output format, and output pitch.

During streaming, callers program output buffer 1 or 2 DMA addresses and toggle the corresponding load bit. On 36-bit DMA platforms, upper address registers are also written. Enabling a channel clears and enables interrupts, then sets `CHNL_EN`; disabling clears interrupt enable and clears `CHNL_EN`. Memory-to-memory operation toggles `READ_MEM` with a short delay to start a memory read. Release returns resources and, on final put, resets and disables the channel clock.

## State and Persistence
Hardware register state is volatile. Software state lives in `struct mxc_isi_pipe`: `use_count`, `irq_handler`, `available_res`, `acquired_res`, `chained_res`, and `chained`. `pipe->lock` serializes resource accounting and channel control updates. No state persists across driver unload or power loss.

## Dependencies and Integration Points
The file depends on ISI register macros from `imx8-isi-regs.h`, platform interrupt-layout and threshold data from `struct mxc_isi_plat_data`, and pipe state from `imx8-isi-core.h`. Higher-level pipe, video, and m2m code call these functions to implement capture and mem2mem streaming.

## Risks and Edge Cases
Scaling uses integer ratios and clamps to `ISI_DOWNSCALE_THRESHOLD`; unusual up/downscale combinations need visual validation. The CSC coefficients are fixed and do not vary with V4L2 colorimetry. Crop lower-right coordinates are built from upper-left plus width/height, so off-by-one interpretation must match hardware documentation. `mxc_isi_channel_set_outbuf()` XORs load bits based on current state, so lost register state or concurrent callers would cause wrong buffer loading; callers rely on pipe locking and buffer sequencing outside this file. `mxc_isi_channel_put()` decrements `use_count` without underflow protection. Chaining assumes the adjacent channel exists and reserves both line and output buffer resources from the next pipe.

## Test Signals
Important tests include 32-bit and 36-bit DMA address programming, both output buffers, m2m read start, identity processing bypass, scaling up/down, crop windows, RGB/YUV CSC in both directions, alpha and flip controls, interrupt status clear and enable masks for each SoC IER layout, acquire/release conflict handling, line-buffer chaining above unchained width, and suspend/resume paths that reset and reprogram channel state.
