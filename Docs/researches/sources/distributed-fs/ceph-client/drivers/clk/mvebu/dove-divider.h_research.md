# sources/distributed-fs/ceph-client/drivers/clk/mvebu/dove-divider.h

Purpose: header for Dove divider clock initialization.

Important APIs/types: declares `dove_divider_clk_init(struct device_node *np)`.

Control flow: no runtime flow in the header.

State and persistence: no header-local state; the C file registers static divider clocks.

Dependencies and integration: included by `dove.c` and implemented by `dove-divider.c`.

Risks: relies on other includes for `struct device_node` and `__init` visibility.

Test signals: build coverage of Dove clock support and link resolution for `dove_divider_clk_init`.
