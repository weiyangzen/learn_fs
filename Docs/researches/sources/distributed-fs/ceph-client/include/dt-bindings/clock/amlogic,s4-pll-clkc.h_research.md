# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,s4-pll-clkc.h

Purpose: defines Amlogic S4 PLL clock IDs for fixed PLL divisors, GP0, HIFI, HDMI, and MPLL outputs.

Important APIs/types/functions: constants cover fixed PLL DCO/output, FCLK div2/div3/div4/div5/div7/div2.5 divider and output nodes, GP0 PLL, HIFI PLL, HDMI PLL DCO/OD/output, MPLL 50M, MPLL predivider, and MPLL0-3 dividers/outputs.

Control flow: DTS consumers and peripheral clock parents refer to these IDs; the PLL provider supplies rate/parent data.

State and persistence: IDs are DT ABI; runtime PLL state is provider-managed.

Dependencies and integration: standalone S4 PLL binding.

Risks and test signals: HDMI and audio PLL rate correctness is high impact. Test HDMI modes, audio clocks, FCLK divisor rates, and provider count.
