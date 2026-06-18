# sources/distributed-fs/ceph-client/include/linux/clkdev.h

Purpose: This header provides the legacy clock lookup table helper layer used by the clock API to map device IDs and connection IDs to `struct clk` or `struct clk_hw`.

Important APIs/types/functions: It defines `struct clk_lookup` with list node, `dev_id`, `con_id`, `clk`, and `clk_hw`; macro `CLKDEV_INIT`; and APIs `clkdev_add`, `clkdev_drop`, `clkdev_create`, `clkdev_hw_create`, `clkdev_add_table`, `clk_add_alias`, `clk_register_clkdev`, `clk_hw_register_clkdev`, and `devm_clk_hw_register_clkdev`.

Control flow: Board or provider code creates lookup entries, adds them to the global clkdev list, and the consumer clock lookup path matches `dev_id`/`con_id` during `clk_get`-style calls. Devm registration binds lookup removal to device lifetime.

State and persistence behavior: Lookup entries persist in a global list until dropped or devres cleanup runs. Entries may point at either a consumer `struct clk` or provider `struct clk_hw`.

Dependencies and integration points: It includes `<linux/slab.h>` and integrates with the legacy non-DT clock lookup path, board files, CCF providers, and `clk_get_sys`.

Risks: Duplicate or overly broad `dev_id`/`con_id` entries can resolve the wrong clock. Lifetime must outlive consumers; dropping entries too early breaks lookup, while never dropping dynamically created entries leaks memory. Format-string creation must be used carefully.

Test signals: Legacy board boot, `clk_get` lookup success/failure tests, alias tests, module unload cleanup, and duplicate lookup audits validate behavior.
