# sources/distributed-fs/ceph-client/drivers/pinctrl/sophgo/pinctrl-cv1800b.c

## Purpose
This file is the Sophgo CV1800B SoC-specific pinctrl front end. It supplies pin descriptors, generated vendor pin metadata, voltage-domain names, and CV1800B-specific electrical mapping callbacks to the shared Sophgo pinctrl core.

## Important APIs, Types, and Data
`enum CV1800B_POWER_DOMAIN` defines five power domains: audio 1.8 V, USB/PLL/ETH/CSI 1.8 V, ETH/USB/SD1 3.3 V-capable domain, RTC VDDIO, and SD0/SPI VDDIO. `cv1800b_power_domain_desc` gives names for these domains. Electrical callbacks are `cv1800b_get_pull_up()`, `cv1800b_get_pull_down()`, `cv1800b_get_oc_map()`, and `cv1800b_get_schmitt_map()`, grouped in `cv1800b_vddio_cfg_ops`.

`cv1800b_pins` lists the public pinctrl pin descriptors, using IDs from `dt-bindings/pinctrl/pinctrl-cv1800b.h`. `cv1800b_pin_data` maps each pin to its power domain, IO type, mux register area/offset/mask width, and pinconf register area/offset using macros from `pinctrl-cv18xx.h`. `cv1800b_pindata` ties those arrays to common CV1800 operations: `cv1800_cfg_ops`, `cv1800_pctrl_ops`, `cv1800_pmx_ops`, and `cv1800_pconf_ops`.

## Control Flow
The platform driver matches `sophgo,cv1800b-pinctrl` and calls `sophgo_pinctrl_probe()` with `cv1800b_pindata` from the OF match data. The common Sophgo probe registers the pins and uses the provided operation tables for mux and config. When pinconf needs bias, drive-strength/open-current, or schmitt thresholds, the common CV18xx layer calls back into the CV1800B VDDIO functions with the pin metadata and current power-domain state map.

## State and Persistence
This file's state is static constant descriptor data. Runtime state, including power-domain voltage state, register mappings, and pinctrl registration, is owned by the shared Sophgo core. The electrical callbacks are pure lookups based on `struct sophgo_pin`, converted to `struct cv1800_pin`, and `psmap[pin->power_domain]`.

## Dependencies and Integration Points
The file depends on Linux module/platform/OF APIs, pinctrl core headers, `dt-bindings/pinctrl/pinctrl-cv1800b.h`, and `pinctrl-cv18xx.h`. It integrates with Kconfig through `CONFIG_PINCTRL_SOPHGO_CV1800B`, with the Makefile as `pinctrl-cv1800b.o`, and with device tree through the `sophgo,cv1800b-pinctrl` compatible.

## Risks
Electrical maps are voltage- and IO-type-sensitive. A wrong power-domain assignment can return the wrong pull resistance, drive map, or schmitt threshold. Unsupported IO types return `-ENOTSUPP`, while invalid voltage state returns `-EINVAL` in some paths; callers must preserve that distinction. The generated pin data must stay ordered and sized exactly with `cv1800b_pins`; otherwise pin IDs and metadata can drift. MIPI pins using `CV1800_GENERATE_PIN_MUX2` have multiple mux locations and are especially sensitive to offset mistakes.

## Test Signals
Test with DT binding validation, probe of `sophgo,cv1800b-pinctrl`, pinmux selection for all listed pins, pinconf bias/drive/schmitt queries under both 1.8 V and 3.3 V domain states, unsupported audio/ETH behavior where appropriate, and module load/unload. Compile tests should verify the generated pin IDs match the binding header and array sizes.
