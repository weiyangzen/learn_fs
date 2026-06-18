# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/linkstation.c

Purpose: Buffalo Linkstation/Kurobox machine descriptor for MPC8241 NAS boards.

Important APIs and control flow: `declare_of_platform_devices` probes `soc` and `simple-bus` children. `linkstation_setup_pci` finds `mpc10x-pci` host bridges and `linkstation_add_bridge` allocates indirect PCI controllers at hard-coded config addresses and processes OF ranges. `linkstation_init_IRQ` creates an EPIC/MPIC with ISUs for PCI, I2C, and DUART. Restart and power-off configure the AVR UART, send command `C` or `E`, then repeatedly send `G` kicks. `linkstation_probe` installs `pm_power_off`.

State, dependencies, and risks: state is machine callbacks plus AVR UART state owned by `ls_uart.c`. Dependencies include OF bridge nodes, MPIC, indirect PCI, MPC10x mapping, and an AVR power-management microcontroller. Risks are hard-coded PCI config addresses, infinite loops on failed AVR response, and limited tested hardware noted by Kconfig. Test signals are platform-device population, PCI enumeration, serial/AVR watchdog handling, and restart/poweroff behavior.
