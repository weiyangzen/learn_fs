# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-k3.c

Purpose: provides HiSilicon K3/Hi6220/Hi3660/Hi4511 DesignWare MMC extensions for clock-rate control, voltage switching through syscon bits, timing register programming, and sample-phase tuning.

Important APIs and functions: variant hooks include `dw_mci_k3_set_ios`, `dw_mci_hi6220_parse_dt`, `dw_mci_hi6220_switch_voltage`, `dw_mci_hi6220_set_ios`, `dw_mci_hi3660_init`, `dw_mci_hi3660_set_ios`, `dw_mci_hi3660_execute_tuning`, and `dw_mci_hi3660_switch_voltage`. Shared helpers include `dw_mci_hs_set_timing`, `dw_mci_get_best_clksmpl`, and `dw_mci_set_sel18`.

Control flow: OF matching selects drv_data for Hi3660, Hi4511, or Hi6220. Hi6220 parsing optionally obtains a peripheral syscon. Voltage switching updates syscon select-1.8V bits and regulators for supported voltages. Hi3660 init enables a read threshold, scales bus frequency by `GENCLK_DIV + 1`, and applies legacy timing. `set_ios` adjusts CIU/BIU clock rates and programs timing registers. Hi3660 tuning loops through 40 attempts over 32 sample phases, sends tuning commands, records good phases, chooses the middle of the longest valid window, and programs it.

State and persistence: `struct k3_priv` stores current speed and optional syscon regmap. Static timing tables encode drive phase, sample delay, and valid sample range by controller index and timing mode. Register state is reprogrammed on timing and voltage changes.

Dependencies and integration points: depends on common DW platform glue, Linux clock/regmap/regulator APIs, MMC tuning and voltage-switch interfaces, OF matching, and shared DW core callbacks.

Risks: controller index is used to index timing tables; unexpected indexes return `-EINVAL`. Some variants implement tuning as a no-op. Voltage switching silently succeeds if syscon is absent, which may hide board description mistakes. Hi3660 tuning uses 40 iterations with modulo 32 phases, so repeated phase samples can influence the bitmask. Clock programming differs between `biu_clk` and `ciu_clk` by variant.

Test signals: DT probe for all compatibles, 1.8V/3.0V voltage switch with regulator and syscon observation, SDR50/SDR104 tuning, timing-register reads, SD versus SDIO controller index coverage, and shared DW I/O stress.
