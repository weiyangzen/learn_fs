# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_main.c

## Purpose
`mthca_main.c` is the top-level PCI/module driver for Mellanox Tavor, Arbel, and Sinai InfiniBand HCAs. It validates module parameters, probes PCI devices, resets and initializes firmware/HCA resources, registers the RDMA device, creates MAD agents, handles MSI-X fallback, removes devices, and supports catastrophic-error restart.

## Important APIs, types, and functions
Module parameters control debug, MSI-X, PCI tuning, and resource profile sizes. Major helpers include `mthca_tune_pci()`, `mthca_dev_lim()`, `mthca_init_tavor()`, `mthca_load_fw()`, `mthca_init_icm()`, `mthca_init_arbel()`, `mthca_close_hca()`, `mthca_init_hca()`, `mthca_setup_hca()`, `mthca_enable_msi_x()`, `__mthca_init_one()`, `__mthca_remove_one()`, `__mthca_restart_one()`, profile validation helpers, and module init/exit. The PCI ID table maps device IDs to Tavor, Arbel compatibility, Arbel native, or Sinai flags.

## Control flow
Module init validates profile parameters, initializes catastrophic-error infrastructure, and registers the PCI driver. Probe enables PCI, validates BARs, requests regions, sets DMA masks and segment size, allocates `mthca_dev`, resets hardware, initializes the command interface, optionally tunes PCI, initializes firmware/HCA differently for Tavor or mem-free devices, warns on old firmware, tries MSI-X, sets up UAR/PD/MR/EQ/CQ/SRQ/QP/AV/MCG tables, switches commands to event mode, verifies command interrupts with NOP, registers the RDMA device, creates MAD agents, stores drvdata, and marks active. Remove reverses agents, RDMA registration, IB ports, tables, command mode, EQs, PD/MR/UAR, firmware state, command interface, IRQ vectors, PCI regions, and device allocation.

## State and persistence
Persistent runtime state lives in `mthca_dev`: firmware version, board ID, HCA type flags, limits, mapped resources, resource tables, IRQ vectors, driver PD/MR/UAR, MAD agents, and active flag. Device persistent state includes firmware loaded into ICM, mapped context tables, initialized HCA/ports, event masks, and hardware object ownership until closed.

## Dependencies and integration points
It integrates Linux PCI and module frameworks, RDMA core registration/provider code, command interface, profile builder, reset code, memfree ICM management, all table managers, MAD agent handling, catastrophic reset worker, MSI-X APIs, and DMA mapping.

## Risks
Initialization has a deep failure tree where unwind order must exactly mirror setup. MSI-X fallback depends on detecting `-EBUSY` from the NOP interrupt test. Tavor and Arbel resource models diverge significantly. Parameter correction silently rounds values to powers of two. Catastrophic restart removes and reinitializes under a global mutex, invalidating old device pointers. Remove closes IB ports after unregistering the RDMA device, so callbacks must already be quiesced.

## Test signals
Test probe/remove for every PCI ID class, BAR validation failures, DMA mask failure, reset failure, firmware query/load/init failures, old firmware warnings, MSI-X success and fallback, NOP interrupt failure, table init unwind at each stage, RDMA registration failure, MAD agent failure, catastrophic restart, module parameter validation, Tavor versus Arbel native/compat/Sinai paths, and repeated load/unload under fault injection.
