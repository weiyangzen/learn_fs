# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-milbeaut.c

Purpose: this is the Socionext/Fujitsu Milbeaut SDHCI host driver for the f_sdh30-derived controller. It wraps the generic SDHCI platform core with Milbeaut bridge setup, vendor register programming, two input clocks, and f_sdh30-specific voltage, reset, and delay handling.

Important APIs, types, and functions: `struct f_sdhost_priv` stores the interface clock, core clock, device, and `enable_cmd_dat_delay` device-property state. `sdhci_milbeaut_ops` supplies `.voltage_switch`, `.get_min_clock`, `.reset`, `.set_clock`, `.set_bus_width`, `.set_uhs_signaling`, and `.set_power`. Bridge helpers program `MLB_SOFT_RESET`, `MLB_CR_SET`, `MLB_CDR_SET`, and `MLB_WP_CD_LED_SET`. `sdhci_milbeaut_vendor_init()` configures f_sdh30 IO voltage select, AHB burst behavior, endian/bus-lock bits, and optional command/data delay.

Control flow: probe allocates an `sdhci_host`, parses MMC DT properties, records SDHCI quirks, maps the MMIO resource, enables `iface` and `core` clocks, calls `sdhci_milbeaut_init()`, and registers the host with `sdhci_add_host()`. Initialization deasserts bridge reset, disables card/internal clocks, asserts reset while writing bridge timing fields from the core clock rate, deasserts reset, and applies vendor register defaults. Reset preserves the internal clock enable, runs `sdhci_reset()`, reenables the card clock, waits up to 10 ms for `SDHCI_CLOCK_INT_STABLE`, and reapplies command/data delay.

State and persistence: state is almost entirely hardware register state plus the enabled clock handles. The only persistent software flag is the DT-derived delay selection. Suspend/resume is not custom here; remove unregisters the host and disables both clocks.

Dependencies and integration points: the file depends on `sdhci-pltfm.h`, `sdhci_f_sdh30.h`, common clock APIs, OF/device properties, and the standard MMC/SDHCI host registration path. DT matching is limited to `socionext,milbeaut-m10v-sdhci-3.0`; the optional `fujitsu,cmd-dat-delay-select` property changes ESD control programming.

Risks: bridge clock calculations clamp values but assume a sane, enabled core clock. Probe error paths rely on clock pointer validity after optional OF setup; this driver is effectively DT-oriented. Reset failure only logs and dumps registers, leaving recovery to upper layers. Voltage switch sequencing is fixed delays and direct register writes, so board-specific electrical timing problems may surface as tuning or IO errors.

Test signals: useful signals are successful probe and `sdhci_add_host()`, absence of "Internal clock never stabilised" logs, correct 1.8 V switching in UHS modes, card detect/write-protect polarity, and reliable tuning with and without `fujitsu,cmd-dat-delay-select`.
