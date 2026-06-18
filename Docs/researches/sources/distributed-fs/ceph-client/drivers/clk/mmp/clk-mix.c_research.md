# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-mix.c

Purpose: implements MMP "mix" clocks that combine mux and divider fields which must be programmed together, often with a hardware frequency-change request bit.

Important APIs/functions: exported `mmp_clk_mix_ops` and `mmp_clk_register_mix`. Internal helpers translate divider/mux encodings (`_get_div`, `_get_div_val`, `_get_mux`, `_get_mux_val`), filter suggested tables, and `_set_rate` performs the atomic hardware update.

Control flow: initialization optionally filters a rate table based on actual parent rates. `determine_rate` either searches that table or brute-forces parents and divisors. `set_rate`, `set_parent`, and `set_rate_and_parent` convert selected parent/divider values to register encodings and call `_set_rate`. `_set_rate` handles V1 direct writes, V2 writes with a polling frequency-change bit, and V3 split control/select registers.

State and persistence: software state stores copied table and mux table data plus register descriptors and type. Persistent state is in hardware mux/divider fields.

Dependencies and integration: MMP SoC files use it for SDH, CCIC, GPU, and other clocks where mux and divider share registers. It depends on CCF composite-style semantics but registers as a single `clk_hw`.

Risks: division by zero is possible if a register encoding maps to divisor zero. V2 polling has a fixed 50-iteration timeout without delay. The table filter mutates the copied table at init and assumes parent rates are already available.

Test signals: requested-rate coverage for table and non-table clocks, parent switching, timeout/error path tests on emulated FC bits, and hardware boot checks for SDH/CCIC/GPU clocks.
