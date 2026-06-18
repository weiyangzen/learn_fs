# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/clock-commonclk.c

## Purpose
`clock-commonclk.c` is the MPC512x common clock provider. It translates CCM reset/configuration registers and device-tree oscillator/bus-frequency data into Linux common-clock objects for MPC5121, MPC5123, and MPC5125 variants, then exposes public clock IDs from `dt-bindings/clock/mpc512x-clock.h`.

## Important APIs, Types, and Functions
The public entry point is `mpc5121_clk_init()`. It maps the `"fsl,mpc5121-clock"` registers, determines the SoC variant, creates fixed/factor/divider/gate/mux clocks, registers an OF onecell provider, and installs fallback `clkdev` aliases. Helpers such as `get_spmf_mult()`, `get_sys_div_x2()`, and `get_cpmf_mult_x2()` decode PLL fields. `mpc512x_clk_setup_clock_tree()` builds the hierarchy from `ref` through `sys`, `csb`, `ips`, and peripheral leaves. `mpc512x_clk_setup_mclk()` handles PSC, MSCAN, SPDIF, and output-clock MCLK subtrees.

## Control Flow, State, and Persistence
State is global boot-time state: `clks[]`, `clk_data`, mapped `clkregs`, `clklock`, and cached `soc`. Missing clocks are preset to `ERR_PTR(-ENODEV)`. The code pre-enables critical internal clocks, console PSC MCLK, and selected compatibility clocks so late clock cleanup does not disable boot-critical hardware.

## Dependencies and Integration Points
It integrates OF clock nodes, MPC512x CCM layout, the common clock framework, `clkdev` migration aliases, legacy DT properties such as `bus-frequency`, and `mpc512x_select_psc_compat()` from shared platform code. Peripheral drivers consume the resulting OF clocks or fallback aliases.

## Risks and Test Signals
Risks include register-field decode errors, variant-specific clock availability, fallback alias mismatches, the apparent SPDIF RX/TX slot overwrite in the external-clock setup, and unsupported MPC5125 NFC timing. Useful tests are boot logs on old and new DTBs, clock summary inspection, PSC serial console stability, PCI/DIU/FEC/USB probe behavior, and rate-change tests for SDHC, DIU, and MCLK users.
