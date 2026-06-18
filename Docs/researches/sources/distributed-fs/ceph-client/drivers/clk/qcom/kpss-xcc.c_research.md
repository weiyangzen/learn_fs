# sources/distributed-fs/ceph-client/drivers/clk/qcom/kpss-xcc.c

## Purpose

This small KPSS XCC driver registers the auxiliary CPU/L2 mux used by Krait processor subsystem clocking. It selects between `pll8_vote` and board PXO for either per-CPU ACC v1 nodes or a GCC-style shared L2 auxiliary clock.

## Important APIs, types, and functions

The core data is `aux_parents`, `aux_parent_map`, `kpss_xcc_match_table`, and `kpss_xcc_driver_probe()`. Probe uses `devm_platform_ioremap_resource()` and `devm_clk_hw_register_mux_parent_data_table()` to create a mux with selector width two bits and selector mapping `{3, 0}`.

## Control flow, state, and persistence

For `"qcom,kpss-acc-v1"`, probe reads the first `clock-output-names` entry and uses register offset `0x14`. For `"qcom,kpss-gcc"`, it registers the fixed name `acpu_l2_aux` at offset `0x28`. It then adds an OF clock provider with `of_clk_add_hw_provider()`. Runtime state is just the mux register selection and registered `clk_hw`.

## Dependencies and integration points

The file depends on DT compatibles, parent clocks named or firmware-named `pll8_vote` and `pxo`, and downstream Krait CPU clock code. It is consumed by Krait CPU/L2 clock trees as the safe or auxiliary source while HFPLLs are reprogrammed.

## Risks and test signals

Risks include wrong offset for ACC/GCC mode, missing `clock-output-names` on ACC nodes, parent-name mismatch, and selector-map errors. Test by booting Krait platforms, checking `acpu*_aux` or `acpu_l2_aux` providers, validating parent switching through debugfs, and running cpufreq transitions that require auxiliary fallback.
