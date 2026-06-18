# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/mpc10x.h

Purpose: shared constants and prototypes for Motorola/Freescale MPC106/8240/107 host bridge, memory maps, embedded utility block devices, and Linkstation AVR helpers.

Important APIs and control flow: defines bridge IDs, Map A/Map B PCI config/ISA/memory windows, DRAM offsets, interrupt acknowledge addresses, config register offsets, EUMB offsets, and `ppc_sys_devices` identifiers. Declares bridge initialization, memory-size query, store-gathering toggles, OpenPIC setup, and AVR UART functions.

State, dependencies, and risks: the header has no runtime state but encodes hardware address contracts used by board files and bridge code elsewhere. Dependencies include Linux PCI IDs and `pci_controller`. Risks are stale hard-coded windows for board variants and accidental mismatch between Map A/Map B selection and firmware-provided ranges. Test signals are compile coverage and correct PCI/ISA/EUMB behavior on Linkstation and StorCenter style MPC10x boards.
