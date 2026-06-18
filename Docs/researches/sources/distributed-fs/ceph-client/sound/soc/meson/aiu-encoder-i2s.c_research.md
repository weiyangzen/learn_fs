# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-encoder-i2s.c

Purpose: Implements the AIU I2S encoder DAI ops, configuring source descriptors, bit/sample clocks, LRCLK/BCLK polarity, channel constraints, sysclk rate, and clock enable sequencing for I2S output.

Important APIs and functions: Exported `aiu_encoder_i2s_dai_ops` supplies `startup`, `shutdown`, `hw_params`, `hw_free`, `set_fmt`, and `set_sysclk`. Key helpers are `aiu_encoder_i2s_setup_desc()`, `aiu_encoder_i2s_set_clocks()`, `aiu_encoder_i2s_set_legacy_div()`, `aiu_encoder_i2s_set_more_div()`, and `aiu_encoder_i2s_divider_enable()`.

Control flow: Startup constrains channels to either 2 or 8 and enables the I2S clock bulk. `set_fmt` accepts CPU bit/frame master mode only, handles I2S versus left-justified skew, and programs LRCLK/AOCLK inversion. `hw_params` disables the divider, resets the I2S fast pipeline, validates physical width and channel count, writes the descriptor mode, derives the MCLK/sample-rate oversampling ratio, programs a 64 BCLK/LRCLK ratio and divider, selects HDMI AMCLK, then reenables the divider. `hw_free` disables the divider.

State and persistence: The master clock rate is stored in the clock framework and used to derive dividers. AIU descriptor and clock-control register bits persist until reconfigured. No private heap state is allocated here.

Dependencies and integration points: Depends on the `struct aiu` clock arrays populated by `aiu.c`, platform data `has_clk_ctrl_more_i2s_div`, ALSA hw_params, and AIU CPU DAI registration. It feeds the I2S encoder playback DAPM route and can be routed onward to HDMI/internal codec controls.

Risks: The hardware has a special 16-bit/8-channel divider adjustment in the newer divider path; wrong handling causes incorrect BCLK. Legacy dividers support only powers 1,2,4,8. The code assumes the MCLK rate is already set by `set_sysclk()` and divisible into the requested sample rate by a multiple of 64. Only 16-bit and 32-bit physical widths are accepted.

Test signals: 2-channel and 8-channel playback, S16 and S24/S32 containers, I2S and left-justified formats with inversion variants, legacy Meson8 and newer GX/GXL divider behavior, sysclk changes from card drivers, and regmap traces on `AIU_I2S_SOURCE_DESC`, `AIU_CLK_CTRL`, and `AIU_CLK_CTRL_MORE`.
