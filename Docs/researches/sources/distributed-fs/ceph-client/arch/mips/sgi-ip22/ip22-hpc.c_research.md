# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-hpc.c

Purpose: initializes IP22 HPC3 and IOC register mappings and identifies Indy versus Indigo2 interrupt-controller layout.

Important APIs and control flow: `sgihpc_init()` maps both HPC3 chips, locates IOC through PBUS channel 6, configures the IOC PIO channel for 16-bit access, selects `sgint` from either PBUS channel 4 on FullHouse or IOC INT3 on Guiness, sets `system_type`, initializes software copies of write-only IOC reset/write registers, and writes them to hardware.

State, persistence, and integration: exported globals `hpc3c0`, `hpc3c1`, `sgioc`, `sgi_ioc_reset`, and `sgi_ioc_write` feed interrupt, reset, NVRAM, platform-device, and memory-controller code. Dependencies include IP22 board detection and fixed HPC3 physical addresses. Risks include assuming `ioremap()` cannot fail, write-only register shadow drift, and ordering requirement that HPC init precedes MC init. Test signals are correct system type, valid IOC/HPC-backed devices, and functioning interrupts.
