# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_main.c Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_main.c

### Purpose
`otx_cptpf_main.c` is the PCI physical-function driver for OcteonTX CPT. It probes the PF, resets and validates hardware, initializes engine-group management, services VF mailbox interrupts, and controls SR-IOV VF enablement.

### Important APIs, Types, And Functions
Important functions are `otx_cpt_probe()`, `otx_cpt_remove()`, `otx_cpt_sriov_configure()`, `otx_cpt_device_init()`, `otx_cpt_register_interrupts()`, `otx_cpt_unregister_interrupts()`, `otx_cpt_reset()`, `otx_cpt_find_max_enabled_cores()`, BIST readers, and mailbox interrupt wrapper `otx_cpt_mbx0_intr_handler()`. The PCI driver binds Cavium device `OTX_CPT_PCI_PF_DEVICE_ID` under name `octeontx-cpt`.

### Control Flow, State, And Persistence
Probe allocates `struct otx_cpt_device`, enables PCI, requests BAR regions, sets a 48-bit DMA mask, maps BAR0, resets CPT, waits 100 ms, checks RAM and engine BIST, reads PF constants to derive available SE/AE cores, determines PF type from subsystem ID and available cores, records total SR-IOV VFs, disables all cores, registers MSI-X mailbox interrupts, and initializes engine groups. `sriov_configure` creates default microcode-backed engine groups before enabling VFs, marks group configuration read-only while VFs are enabled, and pins the module; disabling VFs reverses read-only state and drops the module reference. Remove disables SR-IOV, cleans engine groups, unregisters interrupts, disables cores, unmaps BARs, releases regions, and clears drvdata.

### Dependencies, Integration Points, Risks, And Test Signals
The file integrates PCI core, MSI-X, DMA mask setup, SR-IOV, PF mailbox code, and microcode/engine-group management. Risks include reset/BIST timing, PF type inference when both SE and AE counts are present or absent, `module_put()` symmetry if SR-IOV disable is called without prior enable, interrupt registration rollback, and read-only engine groups while userspace attempts sysfs changes. Test signals include PF probe under hardware or emulation, BIST failure injection, SR-IOV enable with valid firmware tar, SR-IOV disable, mailbox IRQ receipt, module unload with VFs enabled, and DMA mask failure paths.
