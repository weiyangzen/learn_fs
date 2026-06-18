# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-div6.c

Purpose: This file implements Renesas CPG DIV6 clocks, which are 6-bit divider clocks with optional parent selection and clock-stop control. It supports both direct DT registration and internal registration by Renesas CPG drivers.

Important APIs, types, and functions: The main type is `struct div6_clock`, with CCF ops in `cpg_div6_clock_ops`. Important functions include enable/disable/is-enabled, `cpg_div6_clock_determine_rate()`, `cpg_div6_clock_set_rate()`, parent get/set helpers, `cpg_div6_clock_notifier_call()`, exported `cpg_div6_register()`, and OF init `cpg_div6_clock_init()`.

Control flow: `CLK_OF_DECLARE()` binds `renesas,cpg-div6-clock` nodes. The init path counts parents, maps the register, reads parent names, calls `cpg_div6_register()`, and adds a simple clock provider. Internal callers can pass a notifier chain for resume handling.

State and persistence: The driver caches the divisor in `clock->div` because stopping a DIV6 clock can require writing the divisor field. Hardware state is the divisor bits, CKSTP bit, and optional source-select field. A PM notifier restores enabled/disabled state on resume, but does not restore multi-parent source selection.

Dependencies and integration: Depends on CCF, OF address mapping, bitfield helpers, PM notifiers, and `clk-div6.h`. Other Renesas CPG drivers use this helper for SD/MMC and similar clock outputs.

Risks: Parent filtering mutates the `parent_names` array supplied by the caller. Multi-parent resume is explicitly incomplete. Invalid parent counts return `-EINVAL`. Writes are not protected by a spinlock in this helper, so callers rely on CCF serialization and hardware tolerance.

Test signals: Register DT DIV6 nodes with 1, 4, and 8 parents, test rate rounding and parent switching, suspend/resume with enabled and disabled clocks, and verify stopped clocks re-enable with the cached divider.
