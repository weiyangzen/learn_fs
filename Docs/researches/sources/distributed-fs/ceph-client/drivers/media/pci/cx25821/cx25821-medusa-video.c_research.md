# sources/distributed-fs/ceph-client/drivers/media/pci/cx25821/cx25821-medusa-video.c

Purpose: programs the Medusa/Athena video decoder and encoder over I2C for video standard, resolution, monitor routing, blue-field output, and V4L2 procamp controls.

Important APIs and functions: exported functions are `medusa_video_init`, `medusa_set_videostandard`, `medusa_set_resolution`, `medusa_set_brightness`, `medusa_set_contrast`, `medusa_set_hue`, and `medusa_set_saturation`. Internal helpers include `medusa_initialize_ntsc`, `medusa_initialize_pal`, `medusa_PALCombInit`, `medusa_enable_bluefield_output`, `medusa_set_decoderduration`, `mapM`, and `convert_to_twos`.

Control flow: core setup calls `medusa_video_init`, which disables auto/master source selection, sets decoder display duration to 0 for all decoders, configures DENC/monitor bypass/pin output registers, then calls `medusa_set_videostandard`. Standard selection chooses PAL initialization for PAL-BG/DK and NTSC otherwise. NTSC/PAL init loops over all decoders to write mode, horizontal/vertical timing, subcarrier step, VIP active output, special-play/chroma-runaway mitigations, VBI gating, comb-filter setup for PAL, and blue-field output. It loops over two encoders to write standard-specific DENC timing and subcarrier values. Resolution selection maps widths 160/176/320/352/720 to hscale/vscale constants for one decoder or all decoders. Procamp setters map V4L2 0-10000 ranges to signed/unsigned byte hardware values and update only the relevant low byte register.

State and persistence: state is hardware register state on Medusa. Driver software keeps the selected V4L2 standard and channel dimensions in `struct cx25821_dev`/channel state; this file writes hardware to match those values. There is no readback cache or transactional rollback.

Dependencies and integration points: depends on `cx25821_i2c_read/write`, Medusa register constants, bit helpers, V4L2 standard bits, and channel IDs. It is called from core initialization, video standard ioctl, format-setting/resolution path, and V4L2 control callbacks in `cx25821-video.c`.

Risks: many I2C writes overwrite `ret_val`, so earlier failures can be lost if later writes succeed. Several functions accept decoder indexes without complete validation; procamp setters compute `base + 0x200 * decoder` after only range-checking value, relying on callers to pass valid channel IDs. `convert_to_twos` ignores `bits_len` and uses 8-bit conversion unconditionally. Blue-field enable returns early for decoders E-H, so behavior differs across channels. Magic constants dominate and need hardware documentation for safe changes.

Test signals: real hardware initialization for NTSC and PAL inputs, scaler output at 720/352/320/176/160 widths, V4L2 brightness/contrast/hue/saturation controls per channel, and I2C failure injection to verify error propagation.
