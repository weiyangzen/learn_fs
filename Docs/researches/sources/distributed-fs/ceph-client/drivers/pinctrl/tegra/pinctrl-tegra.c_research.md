<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.c

## Purpose
Implements the shared NVIDIA Tegra pinctrl core used by Tegra SoC table files. It provides pinctrl group/function enumeration, DT map parsing, mux programming, group pinconf access, GPIO/SFIO switching, parked-bit cleanup, and suspend/resume register save/restore.

## Important APIs, Types, And Functions
Main exported API is `tegra_pinctrl_probe`; exported PM ops are `tegra_pinctrl_pm`. Internal callbacks include `tegra_pinctrl_dt_node_to_map`, `tegra_pinctrl_set_mux`, `tegra_pinctrl_gpio_request_enable`, `tegra_pinctrl_gpio_disable_free`, `tegra_pinconf_reg`, `tegra_pinconf_group_get/set`, `tegra_pinctrl_clear_parked_bits`, `tegra_pinctrl_suspend`, and `tegra_pinctrl_resume`. DT properties are mapped by `cfg_params`, including pull, tristate, input, open-drain, lock, IO reset, receiver select/IO HV, drive strengths, slew rates, drive type, and GPIO mode.

## Control Flow
SoC drivers call `tegra_pinctrl_probe` with static `tegra_pinctrl_soc_data`. Probe allocates `struct tegra_pmx`, builds reverse function-to-group lists from each pingroup's four mux slots, maps all MMIO banks, allocates register backup storage, registers pinctrl ops, clears parked bits, optionally adds a GPIO range, and stores driver data. DT subnodes emit mux/config maps for each `nvidia,pins` group. Mux writes select the matching function slot. Pinconf resolves a parameter to bank/register/bit/width metadata and performs range-checked read-modify-write.

## State And Persistence Behavior
Per-device state includes SoC descriptor data, generated function group lists, GPIO range, pinctrl descriptor, MMIO bank array, suspend backup register array, and per-pingroup cached SFIO state for GPIO requests. Suspend snapshots every mapped register word and forces pinctrl sleep; resume writes all saved words back, then flushes writes.

## Dependencies And Integration Points
Depends on Linux pinctrl core, pinctrl-utils, platform resources, DT parsing, debugfs seq output, gpiolib ranges, and SoC data from `pinctrl-tegra*.c`. GPIO cooperation depends on the companion Tegra GPIO DT node and `gpio-ranges`.

## Risks And Edge Cases
The generated function group array assumes each mux group appears in at most four function lists. `LOCK` bits cannot be cleared, so bad pinconf inputs can permanently change hardware state until reset. Some features are unsupported per group via negative register/bit fields. Suspend backup size is derived from resource bytes while loops treat it as 32-bit words, so resource sizing must be sane. GPIO/SFIO restoration depends on cached per-group state and correct group lookup by pin offset.

## Test Signals
Probe on each Tegra SoC table, DT pinctrl states with mux-only, config-only, and combined subnodes, unsupported property errors, lock-bit behavior, GPIO request/free with `sfsel_in_mux`, debugfs group dumps, parked-bit clearing, suspend/resume restoration, and builds with/without DT `gpio-ranges`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pinctrl/tegra/pinctrl-tegra.c -->
