<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8516-clk.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8516-clk.h

Purpose: Defines MediaTek MT8516 clock IDs for PLL, infrastructure, top, and audio system clock domains.

Important APIs, types, and functions: Exports `CLK_APMIXED_*`, `CLK_IFR_*`, `CLK_TOP_*`, and `CLK_AUD_*` constants, including sentinel values used by MT8167 extension headers. No functions or structs are declared.

Control flow: The file contains no executable behavior. Clock providers use the constants to map DT specifiers to CCF clocks.

State and persistence: IDs are stable binding ABI. Runtime rate and enable state is owned by the common clock framework and MediaTek provider drivers.

Dependencies and integration points: Used by MT8516 DTS, MT8167 derived headers, and consumers for infrastructure buses, Ethernet, I2C, audio interfaces, USB, NAND/flash, PWM, PMIC wrapper, and top PLL-derived clocks.

Risks and test signals: Risks include breaking MT8167 offset-based IDs, stale sentinels, and audio/top clock parent mistakes. Test by building MT8516 and MT8167 DTBs, checking provider counts, audio playback, Ethernet, I2C, USB, flash, and clk summary rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/mt8516-clk.h -->
