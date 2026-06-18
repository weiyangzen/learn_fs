# sources/distributed-fs/ceph-client/drivers/clk/renesas/clk-rz.c

Purpose: This legacy RZ/A1 CPG provider registers the PLL, I, and G clocks and installs the MSTP PM domain for module clocks.

Important APIs, types, and functions: Key functions are `rz_cpg_read_mode_pins()`, `rz_cpg_register_clock()`, and `rz_cpg_clocks_init()`. It uses hard-coded PPR0 and PIBC0 addresses to read MD_CLK from pin state.

Control flow: `CLK_OF_DECLARE()` binds `renesas,rz-cpg-clocks`. Init counts output names, maps the CPG register block if possible, registers each named clock, adds a onecell provider, then calls `cpg_mstp_add_clk_domain()`. `pll` registration reads mode pins and chooses the external parent and multiplier.

State and persistence: Hardware CPG registers hold FRQCR/FRQCR2 dividers for I and G clocks. Mode pin reads are performed through temporary ioremaps. The driver treats I/G as fixed current-speed factors due to known non-integer constraints.

Dependencies and integration: Depends on OF, CCF, IO mapping, Renesas MSTP helpers, and RZ/A1 DT output names. Module clocks depend on this provider for parent rates.

Risks: `BUG_ON()` is used if mode-pin ioremaps fail. Non-PLL clocks fail with `-ENXIO` if CPG register mapping fails, though the system may still boot with PLL only. I/G modeling is approximate and not suitable for dynamic scaling.

Test signals: Boot RZ/A1, verify MD_CLK parent choice, compare PLL/I/G rates against FRQCR values, ensure MSTP power domain registers, and test timer/peripheral module clocks.
