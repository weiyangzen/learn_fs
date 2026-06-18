# sources/distributed-fs/ceph-client/arch/arm/mach-dove/common.c

Purpose: implements legacy Marvell Dove SoC initialization: static IO maps, clock gates, Orion device registration, MBUS windows, PMU domains, timer, and restart.

Important APIs/types/functions: `dove_map_io()`, `dove_clk_init()`, many peripheral init wrappers (`dove_ehci*`, `dove_ge00_init()`, `dove_sata_init()`, UART/SPI/I2C/SDIO init), `dove_setup_cpu_wins()`, `dove_init()`, and `dove_restart()`.

Control flow: early init sets timer and MBUS base, timer init programs Orion timer with a fixed TCLK, and main init sets up cache, MBUS address windows, clock tree, PMU domains, RTC, and XOR engines. Board files call the peripheral wrappers for devices they populate.

State and persistence: static IO maps, clock registrations, MBUS windows, platform devices, and PMU domains persist for the boot lifetime.

Dependencies and integration: heavily integrates with Orion/plat helpers, Dove PMU, Marvell MBUS, clock framework, Tauros2 cache, and legacy board files.

Risks: fixed clock rate and static MBUS windows are legacy assumptions. Resource-window mistakes affect PCIe, crypto, bootrom, and scratchpad access. Restart spins forever after writing reset registers.

Test signals: Dove boot with expected TCLK log, peripheral driver probes, MBUS window dump, PMU domain registration, and reboot test.
