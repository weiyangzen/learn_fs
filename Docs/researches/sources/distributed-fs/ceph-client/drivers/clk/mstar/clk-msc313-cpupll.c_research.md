# sources/distributed-fs/ceph-client/drivers/clk/mstar/clk-msc313-cpupll.c

Purpose: CPU PLL driver for MStar/SigmaStar MSC313-class SoCs, exposing a rate-changeable CPU PLL based on vendor-derived LPF registers.

Important APIs/functions: `msc313_cpupll_recalc_rate`, `msc313_cpupll_determine_rate`, and `msc313_cpupll_set_rate` implement CCF operations. `msc313_cpupll_reg_read32` and `_write32` combine/split 16-bit register pairs. `msc313_cpupll_setfreq` writes LPF transition registers and waits for lock.

Control flow: probe maps MMIO, seeds LPF low with current frequency, registers a single clock with parent index 0, and adds an OF simple provider. Set-rate converts desired frequency to the magic register divisor, writes the high target, configures transition controls, toggles LPF, polls lock, disables toggle, and stores the low value.

State and persistence: current PLL divisor is stored in hardware LPF/current registers; software holds only MMIO base and `clk_hw`.

Dependencies and integration: platform driver matching `mstar,msc313-cpupll`, CCF, OF provider, raw 16-bit MMIO, and boot parent clock from DT.

Risks: hardware is poorly documented; comments note low-frequency lockups. Poll timeout is 100 ms in a busy loop. `determine_rate` contains conservative rounding logic and a misspelled helper name but works locally.

Test signals: boot CPU frequency report, rate transition stress tests above 220 MHz, lock timeout logs, and comparing register values with vendor-known 400/600/800/1000 MHz examples.
