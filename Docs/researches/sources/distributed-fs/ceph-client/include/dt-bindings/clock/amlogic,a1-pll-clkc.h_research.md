# sources/distributed-fs/ceph-client/include/dt-bindings/clock/amlogic,a1-pll-clkc.h

Purpose: defines Amlogic A1 PLL clock IDs for fixed PLL, fixed divisors, HIFI PLL, and SYS PLL.

Important APIs/types/functions: constants identify fixed PLL DCO/output, fixed clock divider nodes for div2/div3/div5/div7 and their outputs, HIFI PLL, and SYS PLL.

Control flow: DTS consumers reference PLL-derived clocks; the PLL clock controller registers DCOs, dividers, and outputs under these IDs.

State and persistence: IDs are DT ABI; runtime PLL rates and enable state live in the clock provider.

Dependencies and integration: standalone Amlogic A1 PLL binding.

Risks and test signals: provider and consumer ID mismatch can select wrong PLL roots. Test clock tree registration, fixed divisor rates, audio HIFI clock consumers, and CPU/system PLL dependencies.
