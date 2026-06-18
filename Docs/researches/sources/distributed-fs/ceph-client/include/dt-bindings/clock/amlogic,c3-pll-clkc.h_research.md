# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,c3-pll-clkc.h

Purpose: defines Amlogic C3 PLL clock IDs for fixed clocks, GP0, HIFI, MCLK PLL, and MCLK output trees.

Important APIs/types/functions: constants cover FCLK 50M, div2/div2.5/div3/div4/div5/div7 dividers and outputs, GP0 PLL DCO/output, HIFI PLL DCO/output, MCLK PLL DCO/OD/output, and MCLK0/MCLK1 selectors, enables, dividers, and outputs.

Control flow: DTS references select PLL roots and audio clocks; the C3 PLL provider registers and manages them.

State and persistence: DT ABI constants; PLL and divider runtime state belongs to the clock provider.

Dependencies and integration: standalone Amlogic C3 PLL binding.

Risks and test signals: audio MCLK and fixed divisor IDs are easy to confuse. Test rate calculations, MCLK0/MCLK1 consumers, and provider registration coverage.
