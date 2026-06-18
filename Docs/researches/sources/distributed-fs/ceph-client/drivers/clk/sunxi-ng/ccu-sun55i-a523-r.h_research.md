# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun55i-a523-r.h

Purpose: minimal private header for the A523 R_CCU provider. It imports public A523 R-domain clock/reset IDs and defines provider array size.

Important APIs, types, and functions: includes `dt-bindings/clock/sun55i-a523-r-ccu.h` and `dt-bindings/reset/sun55i-a523-r-ccu.h`; defines `CLK_NUMBER` as `CLK_BUS_R_CPUCFG + 1`.

Control flow: none; used by the A523 R_CCU C file at compile time.

State and persistence: no state. The macro determines the number of `clk_hw` slots exposed by the provider.

Dependencies and integration points: tightly coupled to `ccu-sun55i-a523-r.c` and the binding header’s highest exported clock ID.

Risks and test signals: if new binding IDs are added without updating `CLK_NUMBER`, later clocks become inaccessible. Test by build coverage and boot-time lookups for the highest R-domain clock ID.
