# sources/distributed-fs/ceph-client/sound/soc/renesas/migor.c

Purpose: board machine driver for the Renesas Migo-R board, connecting the SIU CPU DAI to a WM8978 codec and modeling an external codec-derived SIUMCKB clock.

Important functions and state: `siumckb_recalc()` exposes the current `codec_freq`. `migor_hw_params()` configures the WM8978 PLL from 13 MHz, sets OPCLK to `rate * 512`, updates the synthetic SIUMCKB clock, and sets the SIU CPU DAI sysclk to half that frequency. `migor_hw_free()` reference-counts users and disables the codec PLL when the last stream frees. DAPM widgets/routes model headphone and onboard/external microphones.

Control flow: module init registers the external clock, creates a clkdev lookup, allocates a `soc-audio` platform device with the static card, and adds it. Exit drops lookup/clock and unregisters the platform device. Runtime hw_params programs codec and CPU clocks before streaming.

State and persistence: file-static `codec_freq`, `use_count`, `siumckb_clk`, lookup, and platform device pointer hold all state. It is module lifetime only.

Dependencies and integration: depends on legacy SH clock APIs, SH7722/Migo-R platform headers, SIU CPU DAI, WM8978 codec driver, and ASoC machine-card registration.

Risks: global `use_count` is not locked; unbalanced hw_free is only logged. The driver is board-specific and uses legacy `soc-audio` platform-device registration. Clock assumptions are tightly coupled to WM8978 and SIU CLKB wiring.

Test signals: module init creates the card, hw_params at common rates changes `codec_freq` and SIU sysclk, PLL is disabled after final hw_free, and DAPM routes expose headphone and both mic paths.
