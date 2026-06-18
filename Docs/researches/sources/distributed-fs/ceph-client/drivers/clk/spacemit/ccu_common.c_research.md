# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.c -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.c

Purpose: provides common SpacemiT CCU platform probe support. It registers per-SoC `clk_hw` arrays as onecell providers, injects regmaps into each CCU clock object, and optionally creates reset-controller auxiliary devices for syscon regions that also host reset bits.

Important APIs and control flow: `spacemit_ccu_probe()` maps the platform node to a base regmap, optionally parses `spacemit,mpmu` and obtains a lock regmap for PLL-compatible nodes, fetches match data, calls `spacemit_ccu_register()`, then calls `spacemit_ccu_reset_register()`. `spacemit_ccu_register()` allocates `clk_hw_onecell_data`, iterates the SoC `hws` array, stores `ERR_PTR(-ENOENT)` for holes, fills `common->regmap` and `common->lock_regmap`, registers each clock with `devm_clk_hw_register()`, and publishes `of_clk_hw_onecell_get`. Reset publication uses `spacemit_ccu_adev`, `auxiliary_device_init/add`, IDA IDs, and a devm cleanup action.

State and persistence behavior: persistent global state is the `auxiliary_ids` IDA. Per-device state includes devm-allocated onecell data and auxiliary reset devices whose lifetime is tied to the platform device. Clock hardware objects are static in SoC files, but their regmap pointers are set at probe time. Reset auxiliary devices own a syscon regmap pointer and are deleted/uninitialized by `spacemit_adev_unregister()` during device teardown.

Dependencies and integration points: depends on regmap syscon lookup through `device_node_to_regmap()`, OF match data containing `struct spacemit_ccu_data`, the local `hw_to_ccu_common()` embedding contract, CCF devm registration, OF clock provider APIs, auxiliary bus APIs, IDA allocation, and `soc/spacemit/ccu.h` for auxiliary device container types. PLL lock polling depends on SoC files passing the PLL compatible string into `spacemit_ccu_probe()`.

Risks and test signals: risks include assuming every non-NULL `clk_hw` embeds `struct ccu_common`, static clock objects being mutated by per-device probe state, holes depending on consumers tolerating `-ENOENT`, reset auxiliary device error paths needing balanced IDA/device cleanup, and PLL probe failure if the MPMU phandle is absent. Test signals include successful clock provider registration, valid `-ENOENT` returns for missing IDs, devm cleanup on driver removal, reset auxiliary devices appearing for reset-capable regions, MPMU lock regmap acquisition only for PLL nodes, and meaningful `dev_err_probe()` diagnostics on failed regmap, clock, or reset registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_common.c -->
