# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-aspeed.c

## Purpose
`pcie-aspeed.c` is the ASPEED AST2600/AST2700 PCIe root complex driver. It programs H2X/SCU/AHBC setup, per-port clock/PHY/PERST sequencing, custom root and child config transactions, address remapping, INTx handling, and an integrated 64-vector MSI parent domain.

## Important APIs, Types, And Functions
`struct aspeed_pcie` stores host bridge, device, H2X register base, syscon regmaps, platform descriptor, port list, TX tag, root bus number, H2X reset, INTx/MSI domains, MSI bitmap, and AST2700 MSI-clear workaround state. `struct aspeed_pcie_rc_platform` selects setup, mapping, interrupt register offsets, and MSI doorbell address. Config paths are split into AST2600 (`aspeed_ast2600_conf()`) and AST2700 (`aspeed_ast2700_config()`, `aspeed_ast2700_child_config()`) operations. IRQ logic uses `aspeed_pcie_intr_handler()`, `aspeed_pcie_intx_map()`, `aspeed_irq_msi_domain_alloc()`, and `aspeed_irq_compose_msi_msg()`.

## Control Flow, State, And Persistence
Probe allocates the host bridge, records root bus number, maps H2X registers, gets H2X reset, initializes the mutex, runs platform setup, maps the first MEM range, parses DT child PCI ports, creates INTx/MSI domains, requests the shared IRQ, and calls `pci_host_probe()`. AST2600 setup unlocks AHBC, enables RC memory, resets H2X, enables RX/MSI paths, sets TX tags, and assigns root/child PCI ops. AST2700 setup programs SCU decode/path registers, disables endpoint function, resets H2X, enables direct bridge mode, prepares 64-bit prefetch remap, assigns ops, and enables double MSI status clearing. Runtime state includes TX tag and MSI allocation bitmap; hardware state is volatile and rebuilt at probe.

## Dependencies, Integration Points, Risks, And Test Signals
The driver integrates with OF child port nodes, clocks, generic PHY in RC mode, reset controls, syscon regmaps (`aspeed,ahbc` or `aspeed,pciecfg`), IRQ domains, MSI library, host bridge `ops`/`child_ops`, and shared platform IRQs. Risks include short config timeout windows, AST2600 slot-8 and AST2700 devfn-0 root-port assumptions, generation-specific MSI clearing, and remap configuration errors. Test root/child config cycles, TX tag wraparound, MEM remap, per-port PHY/clock/reset sequencing, INTx level handling, MSI/MSI-X allocation across both status registers, and no CR tx/rx timeout logs for present devices.
