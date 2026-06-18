<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mediatek.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-mediatek.c

Purpose: implements the MediaTek general-purpose PWM controller for many SoCs using the PWM waveform API. It supports multiple channels with top/main/per-channel clocks, SoC-specific register base/stride, optional PWM4/5 register fixups, and optional 26 MHz clock-select clearing.

Important APIs/types/functions: `struct pwm_mediatek_of_data` supplies channel count and register layout. `struct pwm_mediatek_chip` stores MMIO base, top/main clocks, SoC data, and per-channel clock/rate pairs. `pwm_mediatek_round_waveform_tohw/fromhw()`, `pwm_mediatek_read_waveform()`, `pwm_mediatek_write_waveform()`, `pwm_mediatek_clk_enable/disable()`, and `pwm_mediatek_init_used_clks()` are the core routines.

Control flow: probe gets SoC data, maps MMIO, acquires `top`, `main`, and `pwmN` clocks, locks per-channel rates exclusively, preserves clocks for channels already enabled by hardware, and registers the chip. Waveform conversion computes clock divider, 13-bit period, duty threshold, and enable bit from nanoseconds. Write enables clocks, optionally increments the clock usage count when transitioning from disabled to enabled, clears 26 MHz selection when needed, writes channel registers, and disables clocks on transition to off.

State and persistence: hardware registers hold enable, divider, period, and duty. Software caches per-channel clock rates after first use and uses clock prepare counts to keep already-enabled outputs alive. There is no explicit system PM state.

Dependencies and integration: depends on platform/OF match data for many MediaTek SoCs, clk framework including exclusive rate locks, MMIO, PWM waveform callbacks, and PWM core.

Risks and test signals: clock enable reference counting is subtle because write paths temporarily enable clocks and may add an extra enable for active outputs. Test bootloader-enabled channels, SoC-specific register bases/widths, PWM4/5 fixup on MT7623/MT7628, 26 MHz selector clearing, max 1 GHz rate validation, waveform round-trip accuracy, and remove/unbind clock balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-mediatek.c -->
