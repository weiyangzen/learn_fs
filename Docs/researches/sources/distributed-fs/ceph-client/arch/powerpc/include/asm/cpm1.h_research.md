## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cpm1.h

Purpose: describes MPC8xx CPM1 command fields, parameter-RAM layouts, channel register bits, interrupt vectors, GPIO/pin controls, and clock-routing APIs.

Important APIs/types/functions: declares `cpmp`, `cpm_setbrg()`, `cpm_load_patch()`, `cpm_reset()`, `cpm1_set_pin()`, `cpm1_clk_setup()`, `cpm1_gpiochip_add16()`, and `cpm1_gpiochip_add32()`. Key types include `smc_uart_t`, `smc_cent_t`, `sccp_t`, `scc_enet_t`, `scc_uart_t`, `scc_trans_t`, `iic_t`, `rt_pram_t`, and enums for CPM ports, clocks, directions, and targets.

Control flow: mostly declarative hardware layout. Runtime users build command words with `mk_cr_cmd()`, program parameter RAM offsets such as `PROFF_SCC1`, configure SMC/SCC modes and event masks, route BRG/CLK sources, and set pin modes. The RISC timer, CPM interrupt vectors, and GPIO helpers are configured by platform and driver code outside the header.

State and persistence: CPM registers and dual-port RAM are persistent device state accessed through `cpmp`. The structures mirror firmware/hardware parameter RAM, so field ordering is externally defined. GPIO, BRG, SCC/SMC, I2C, Ethernet, and timer settings persist until device reset.

Dependencies and integration: depends on `asm/8xx_immap.h`, `asm/ptrace.h`, and common CPM definitions. It integrates with 8xx serial, Ethernet, I2C, GPIO, timer, and interrupt-controller support.

Risks and test signals: register bit constants and parameter-RAM structures must exactly match MPC8xx manuals and board firmware quirks. Wrong offsets corrupt unrelated CPM channels. Test signals include MPC8xx boot, serial console, SCC Ethernet traffic, I2C/SPI transfers, GPIO export, CPM interrupt dispatch, and microcode patch loading.
