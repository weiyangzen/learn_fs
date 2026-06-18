# sources/distributed-fs/ceph-client/arch/powerpc/platforms/chrp/pegasos_eth.c

Purpose: registers legacy platform devices for Pegasos II Marvell MV6436x Ethernet, MDIO, and port 1 SRAM-backed queue resources.

Important APIs and control flow: static `resource`, `platform_device`, and `mv643xx_eth_platform_data` objects describe shared Ethernet registers, Orion MDIO window, IRQ 9, PHY address 7, and integrated SRAM queue layout. `Enable_SRAM` maps the Marvell register block, configures SRAM base/size registers, enables the SRAM window, and unmaps. `mv643xx_eth_add_pds` runs as a `device_initcall`, checks for the Marvell PCI device, adds platform devices, and disables SRAM fields if SRAM setup fails.

State, dependencies, and risks: state is the transient `mv643xx_reg_base` mapping and static platform data handed to network drivers. Dependencies include PCI device presence, Marvell register layout, `mv643xx_eth` platform bindings, and platform-device probing. Risks include hard-coded physical addresses and IRQ/PHY values, SRAM setup ordering after device registration, and fallback to non-SRAM queues only on setup failure. Test signals are platform-device creation, MDIO probe, Ethernet link on port 1, and absence of MMIO faults during SRAM programming.
