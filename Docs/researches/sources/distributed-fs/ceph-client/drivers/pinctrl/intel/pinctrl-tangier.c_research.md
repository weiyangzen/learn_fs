# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-tangier.c

Purpose: Implements the common Intel Tangier pinctrl driver used by Tangier-family platform data. Unlike the Sunrisepoint/Tiger Lake files, this file contains active pinctrl, pinmux, pinconf, and probe logic for a family-based MMIO layout.

Important APIs/types/functions: Public entry is `devm_tng_pinctrl_probe()`, exported in namespace `PINCTRL_TANGIER`. Helper functions include `tng_get_family()`, `tng_buf_available()`, `tng_get_bufcfg()`, `tng_read_bufcfg()`, and `tng_update_bufcfg()`. Pinctrl callbacks are collected in `tng_pinctrl_ops`; pinmux callbacks in `tng_pinmux_ops`; pinconf callbacks in `tng_pinconf_ops`. BUFCFG bit definitions cover pin mode, pull enable/value, slew, input/output override, and open drain.

Control flow: Probe reads `device_get_match_data()`, duplicates static `struct tng_pinctrl` and family tables, maps BAR 0 once, splices each family to `regs + barno * TNG_FAMILY_LEN`, builds a `pinctrl_desc`, and registers with `devm_pinctrl_register()`. Pinctrl core callbacks then enumerate groups/functions, set mux modes by writing `BUFCFG_PINMODE_MASK`, force GPIO mode from `gpio_request_enable`, and get/set pin or group configs.

State and persistence: Runtime state is `struct tng_pinctrl`: device pointer, raw spinlock, registered pinctrl device, and copied family records with MMIO pointers. Hardware state persists in BUFCFG registers. Protected families are treated as unavailable and return `-EBUSY`/`-ENOTSUPP`, leaving firmware-owned pins untouched.

Dependencies and integration points: Uses generic pinctrl, pinmux, and pinconf APIs, `pinctrl-intel.h` data structures, local `pinctrl-tangier.h`, and platform resources. The source is a reusable implementation; SoC-specific Tangier files provide match data, pins, groups, functions, and family descriptors.

Risks: `tng_read_bufcfg()` assumes `tng_get_bufcfg()` succeeds after `tng_buf_available()`; keeping family data coherent is therefore required. The driver serializes read-modify-write register updates with a raw spinlock, but availability checks happen before the lock and depend on static family protection state. Pinconf supports only bias disable/up/down, push-pull/open-drain, and slew rate; unsupported generic properties must be rejected by tests. Pull strength accepts only 910, 2000, 20000/default, and 50000 ohms.

Test signals: Compile/link users of `devm_tng_pinctrl_probe`, platform probe with valid match data, debugfs pin dumps, protected-family access returning busy/unsupported, mux switching for every group, GPIO request forcing mode 0, pinconf get/set for supported pull/open-drain/slew cases, and group config propagation across all pins.
