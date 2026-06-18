# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-lantiq.c

## Purpose
Provides the common Lantiq pinctrl/pinmux core used by SoC-specific Lantiq pad-controller drivers. It handles pin groups, mux function exposure, legacy Lantiq DT map parsing, and dispatches actual mux programming to a SoC callback.

## Important APIs, Types, and Functions
The public entry point is `ltq_pinctrl_register`. Pinctrl ops are implemented by `ltq_get_group_count`, `ltq_get_group_name`, `ltq_get_group_pins`, `ltq_pinctrl_dt_node_to_map`, and `ltq_pinctrl_dt_free_map`. Pinmux ops are `ltq_pmx_func_count`, `ltq_pmx_func_name`, `ltq_pmx_get_groups`, `ltq_pmx_set`, and `ltq_pmx_gpio_request_enable`. Validation helpers include `match_mux`, `match_mfp`, and `match_group_mux`.

## Control Flow and State
SoC drivers fill `struct ltq_pinmux_info` and call `ltq_pinctrl_register`, which installs common ops into the supplied descriptor and registers pinctrl. DT parsing walks child nodes, accepts either `lantiq,pins` or `lantiq,groups`, creates mux maps when `lantiq,function` is present, and packs configured Lantiq pinconf properties with `LTQ_PINCONF_PACK`. Mux setting validates that every pin in a group supports the requested mux value, translates logical pins to MFP table entries, then calls `info->apply_mux` per pin.

## Dependencies and Integration Points
Integrates with Lantiq SoC drivers that provide pads, MFP tables, groups, function lists, optional config parameters, memory bases, clocks, external interrupt mappings, and the `apply_mux` callback. It depends on OF properties with `lantiq,*` names, pinctrl core APIs, and dynamic allocation for generated pinctrl maps.

## Risks and Test Signals
Risks include malformed DT nodes producing too few or too many maps, missing allocation checks for per-map config copies, non-linear MFP table lookup mistakes, mux/group table drift in SoC-specific data, and function/group selector bounds assumptions. Test signals are DT parsing for pin-only, group-only, mux-only, and config-only nodes; GPIO request fallback to mux 0; invalid mux diagnostics; and boot tests on each Lantiq SoC using this common layer.
