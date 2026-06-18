# sources/distributed-fs/ceph-client/drivers/clk/microchip/clk-core.c

Purpose: This file implements reusable PIC32 clock operations for peripheral bus clocks, reference oscillators, system PLL, system clock mux/slew divider, and secondary oscillator.

Important APIs, types, and functions: Exported ops and constructors include `pic32_pbclk_ops` with `pic32_periph_clk_register`, `pic32_roclk_ops` with `pic32_refo_clk_register`, `pic32_spll_ops` with `pic32_spll_clk_register`, `pic32_sclk_ops`/`pic32_sclk_no_div_ops` with `pic32_sys_clk_register`, and `pic32_sosc_ops` with `pic32_sosc_clk_register`. Key helpers include `calc_best_divided_rate`, `roclk_calc_rate`, `roclk_calc_div_trim`, `spll_calc_mult_div`, `sclk_set_parent`, and `sclk_init`.

Control flow: SoC-specific code registers clock descriptors through the constructors. CCF callbacks then read/write PIC32 registers directly. Protected writes call `pic32_syskey_unlock`, use `reg_lock`, and poll ready, active, lock, or busy bits. SPLL rate changes are refused while SPLL is the active system-clock parent. System clock parent changes program `NOSC`, set `OSC_SWEN`, wait for switch completion, and verify `COSC`.

State and persistence behavior: Runtime state lives in MMIO clock registers and small allocated clock wrapper structs. `pic32_sclk_hw` caches the system clock hardware so SPLL changes can detect active use. There is no disk persistence. Hardware settings persist until firmware reset or later clock operations.

Dependencies and integration points: It depends on CCF, MMIO accessors, polling helpers, PIC32 platform syskey APIs, and descriptor structs from `clk-core.h`. `clk-pic32mzda.c` is the main in-tree user.

Risks and edge cases: Clock switching is CPU-sensitive and uses NOP delays to avoid hangs during transitions. Poll timeouts, failed oscillator switching, reference oscillator active state, and SPLL in-use checks are critical. Several routines must preserve lock ordering around syskey-protected writes. Test signals include rate round/set for PBCLK/REFO/SPLL/SCLK, oscillator parent switching, timeout injection, critical-clock enable, and NMI/failsafe scenarios on PIC32 hardware.
