# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-a64.h

Purpose: private clock-ID header for the A64 CCU driver. It combines public DT binding IDs with internal IDs for non-exported or derived clocks used only inside the provider.

Important APIs, types, and functions: includes `<dt-bindings/clock/sun50i-a64-ccu.h>` and `<dt-bindings/reset/sun50i-a64-ccu.h>`, then defines internal IDs such as `CLK_OSC_12M`, `CLK_PLL_CPUX`, fixed-factor audio/peripheral/video clocks, bus roots, `CLK_USB_OHCI*_12M`, and `CLK_NUMBER`.

Control flow: no executable control flow; the macros are consumed by `ccu-sun50i-a64.c` when filling `struct clk_hw_onecell_data`.

State and persistence: no runtime state. The numeric values are ABI-adjacent because they index provider arrays and must not collide with DT binding IDs.

Dependencies and integration points: tightly coupled to the A64 binding headers and the `.hws` array in the C file. Comments document which clock ranges are exported by the public binding and which are local.

Risks and test signals: off-by-one `CLK_NUMBER` or ID overlap can make DT lookups return the wrong clock or `NULL`. Test by building the driver, checking all referenced IDs compile, and verifying clock consumers resolve expected providers at boot.
