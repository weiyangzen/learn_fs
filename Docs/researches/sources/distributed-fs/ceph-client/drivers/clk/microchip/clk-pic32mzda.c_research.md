# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-pic32mzda.c

Purpose: This file instantiates the PIC32MZDA clock tree using the shared PIC32 clock core. It registers fixed oscillators, FRC divider, system PLL mux and PLL, system clock, PBCLKs, reference oscillators, critical clocks, and a failsafe clock monitor NMI notifier.

Important APIs, types, and functions: Descriptor macros `DECLARE_PERIPHERAL_CLOCK` and `DECLARE_REFO_CLOCK` build `pic32_periph_clk_data` and `pic32_ref_osc_data`. Static descriptors include `ref_clks`, `periph_clocks`, `sys_mux_clk`, `sys_pll`, and `sosc_clk`. Runtime functions are `pic32_fscm_nmi`, `pic32mzda_clk_probe`, and `microchip_pic32mzda_clk_init`.

Control flow: Probe maps the clock register block, initializes the shared lock, registers fixed-rate clocks (`posc`, `frc`, `bfrc`, `lprc`, `usbphy`), optionally registers SOSC from a DT property, registers `frcdiv_clk`, SPLL input mux, SPLL, system clock, PB1-PB7 clocks, REF1-REF5 clocks, clkdev aliases, and the OF onecell provider. It then force-enables critical clocks and registers an NMI notifier for failsafe clock monitor alerts.

State and persistence behavior: Driver state is stored in `pic32mzda_clk_data`, including the clock array, common MMIO base/lock, onecell data, and notifier. Hardware clock configuration persists in PIC32 registers. Critical clocks PB2 and PB7 are enabled during probe and intentionally kept active.

Dependencies and integration points: It depends on PIC32 dt-bindings, CCF, clkdev, OF MMIO mapping, MIPS trap/NMI notifier support, and the shared `clk-core` registration helpers.

Risks and edge cases: Error unwinding is limited after partial clock registration. Optional SOSC changes parent availability. Critical clock indexes must match binding IDs. The NMI notifier only reports failsafe clock failure and does not recover. Test signals include DT probe, fixed-rate clock visibility, system clock parent/rate changes, PB and REFO rates, optional SOSC property behavior, critical clock enablement, and simulated FSCM NMI logging.
