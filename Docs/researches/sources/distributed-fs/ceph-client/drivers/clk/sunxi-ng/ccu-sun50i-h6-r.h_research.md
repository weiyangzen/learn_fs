# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h6-r.h

Purpose: private ID bridge for the H6/H616 PRCM CCU driver. It imports public DT clock/reset IDs and defines local bus-root indexes that are not all exported in bindings.

Important APIs, types, and functions: includes `sun50i-h6-r-ccu` clock/reset bindings, defines `CLK_R_AHB`, `CLK_R_APB2`, and `CLK_NUMBER` as `CLK_R_APB1_RTC + 1`.

Control flow: none; macros drive array indexes in `ccu-sun50i-h6-r.c`.

State and persistence: no runtime state. The numeric definitions must remain stable relative to the binding header values used by DT consumers.

Dependencies and integration points: used only by the H6/H616 R_CCU implementation to size and populate `clk_hw_onecell_data`.

Risks and test signals: wrong `CLK_NUMBER` truncates provider arrays; wrong private indexes can alias exported IDs. Build coverage and boot-time onecell lookup for `CLK_R_APB1_RTC`, `CLK_R_AHB`, and R peripheral clocks are the main signals.
