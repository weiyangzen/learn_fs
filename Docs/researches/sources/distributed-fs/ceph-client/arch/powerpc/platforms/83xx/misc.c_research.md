# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/misc.c

## Purpose
`misc.c` provides shared MPC83xx platform functions: restart, time init, IPIC init, OF device declaration, PCI setup, IMMR BAT mapping, and watchdog machine-check handling.

## Important APIs, Types, and Functions
`mpc83xx_restart_init()` maps the reset control register from `"fsl,modulo-reboot"` and is registered as an `arch_initcall`. `mpc83xx_restart()` disables interrupts and writes the reset request. `mpc83xx_time_init()` reads bus frequency for decrementer calibration. `mpc83xx_ipic_init_IRQ()` initializes IPIC. `mpc83xx_declare_of_platform_devices()` populates simple/FSL buses. `mpc83xx_setup_pci()` scans PCI nodes and calls `mpc83xx_add_bridge()`. `mpc83xx_setup_arch()` creates a BAT mapping for IMMR. `machine_check_83xx()` handles watchdog MCP machine checks specially.

## Control Flow, State, and Persistence
The reset register mapping persists in `restart_reg_base`. The IMMR BAT mapping is global CPU MMU state. OF platform population creates device state under the platform bus.

## Dependencies and Integration Points
It depends on FSL SOC frequency helpers, IPIC, FSL PCI, OF platform bus, fixed IMMR mapping, and PowerPC machine-check infrastructure.

## Risks and Test Signals
Risks include missing reboot node causing restart hang, invalid bus-frequency data, BAT size alignment assumptions, PCI node scan ordering, and watchdog MCP classification. Test signals are restart, timer/decrementer calibration, IPIC interrupts, PCI enumeration, OF device probing, and watchdog NMI reporting.
