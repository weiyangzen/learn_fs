<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2.c

Purpose: common CPM2 global management support for mapping CPM registers, issuing CPM commands, configuring baud-rate generators, setting CPM mux clocks, and configuring CPM2 pins.

Important APIs/types/functions: globals `cpmp` and exported `cpm2_immr`; functions `cpm2_reset()`, exported `cpm_command()`, exported `__cpm2_setbrg()`, `cpm2_clk_setup()`, `cpm2_smc_clk_setup()`, and `cpm2_set_pin()`.

Control flow: `cpm2_reset()` maps IMMR/CPM register space, initializes the CPM pointer, and optionally issues CPM reset. `cpm_command()` serializes command register writes with a spinlock, writes command/opcode/flag, and polls until CPM clears the flag or times out. Clock setup functions map target/clock pairs to mux bits and update CPM mux registers. Pin setup toggles direction, peripheral/GPIO, secondary option, and open-drain bits.

State and persistence: persistent state is the ioremapped CPM register block and global `cpmp` pointer. CPM command and mux/pin register writes persist in hardware until reset or reconfiguration.

Dependencies and integration points: depends on SoC IMMR base discovery, CPM2 register definitions, `asm/cpm2.h`, endian MMIO helpers, and consumers such as serial, Ethernet, and GPIO drivers that need BRG, clock, or pin setup.

Risks: CPM command polling can fail if hardware is wedged. Clock map tables are static and invalid target/clock pairs return `-EINVAL` after still writing zero bits if not checked carefully by callers. Pin indexing assumes valid port/pin arguments.

Test signals: CPM reset success, BRG output frequency, serial/network channels receiving expected clocks, command timeout logs absent, and GPIO/pin mux behavior on CPM2 boards validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/cpm2.c -->
