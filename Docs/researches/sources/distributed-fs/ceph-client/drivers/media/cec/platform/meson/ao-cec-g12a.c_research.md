# sources/distributed-fs/ceph-client/drivers/media/cec/platform/meson/ao-cec-g12a.c

## Purpose
This is the Amlogic Meson AO-CECB CEC controller driver for G12A/SM1 generation SoCs. It exposes a Linux CEC adapter backed by a memory-mapped AO CEC block, integrates with an HDMI CEC notifier for connector information, and registers an internal dual-divider clock that derives the 32.768 kHz CEC core clock from the oscillator.

## Important APIs, Types, and Functions
The main state type is `struct meson_ao_cec_g12a_device`, holding the platform device, top-level regmap, indirect CEC regmap, CEC adapter, notifier, clock handles, RX message buffer, and SoC-specific data. `struct meson_ao_cec_g12a_data` gates the SM1-only `CECB_CTRL2` setup. The internal clock is represented by `struct meson_ao_cec_g12a_dualdiv_clk` and `clk_ops` for recalc/enable/disable/is_enabled. CEC framework callbacks are `meson_ao_cec_g12a_adap_enable`, `meson_ao_cec_g12a_set_log_addr`, and `meson_ao_cec_g12a_transmit`.

## Control Flow
Probe parses the HDMI phandle, allocates a CEC adapter, maps MMIO, creates two regmaps, requests a threaded IRQ, obtains `oscin`, registers/enables the dual-divider clock, optionally resets the device, registers the notifier, and registers the adapter. Enable resets the controller, configures glitch filtering and system/gated clocks, optionally programs `CECB_CTRL2`, and unmasks interrupts. Transmit checks RX lock and TX busy state, writes TX bytes/count, and starts the controller with the correct signal-free-time type. The hard IRQ only wakes the thread if interrupt status is nonzero; the thread clears status and reports TX done/NACK/arbitration/error or dispatches RX data.

## State and Persistence
Driver state is in `meson_ao_cec_g12a_device`. Hardware logical address bits are stored in `CECB_LADD_LOW/HIGH`, always adding unregistered/broadcast address 15. RX state is transient in `rx_msg`; TX completion is reported directly from interrupt status. There is no persistent configuration beyond DT-compatible match data and clock/reset resources.

## Dependencies and Integration Points
The driver depends on platform device resources, regmap, clock provider APIs, optional reset control, `media/cec.h`, and `cec-notifier`. DT compatibles are `amlogic,meson-g12a-ao-cec` and `amlogic,meson-sm1-ao-cec`. The indirect CEC register bus is wrapped as an 8-bit regmap using custom read/write callbacks through `CECB_RW_REG`.

## Risks and Test Signals
Important risks are timing correctness in the dual-divider setup, indirect-register polling timeouts, RX lock handling before TX, and correct interrupt status translation. `meson_ao_cec_g12a_dualdiv_clk_recalc_rate` reads `CECB_CLK_CNTL_REG0` twice where the second read appears intended for REG1, and the M2 extraction uses `CECB_CLK_CNTL_M1`; tests should inspect reported clock rate. Hardware tests should cover logical address add/remove, poll messages, directed and broadcast transmit, NACK/arbitration loss, RX length clamping, and SM1-specific `CTRL2` behavior.
