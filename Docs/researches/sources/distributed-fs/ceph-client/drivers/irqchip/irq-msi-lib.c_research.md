<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-msi-lib.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-msi-lib.c

### Purpose
`irq-msi-lib.c` is a shared helper library for irqchip drivers that expose MSI parent domains. It normalizes child MSI domain flags/chip callbacks and provides a common domain selection function for NEXUS or generic MSI parent domains.

### Important APIs, Types, And Functions
`msi_lib_init_dev_msi_info()` validates `msi_parent_ops`, reconciles child `msi_domain_info` flags with parent required/supported flags, installs default EOI/ACK/mask/affinity callbacks when requested, and prepares device MSI or wired-to-MSI domains. `msi_lib_irq_domain_select()` matches an IRQ domain by fwnode and bus token against the parent ops bus selection mask. Both are exported GPL symbols.

### Control Flow
Initialization first verifies the real parent has MSI parent ops and that the selected domain bus token matches the parent token. It switches on the requested child bus token, rejects unsupported PCI MSI configurations, adjusts required flags for device and wired-to-MSI domains, masks unsupported flags, enforces required flags, and fills missing chip operations. Selection obtains the relevant fwnode, rejects nonzero firmware parameters or fwnode mismatch, then returns true for direct parent token matches or supported child bus tokens.

### State, Persistence, And Dependencies
The file owns no persistent state. It mutates caller-provided `msi_domain_info` and IRQ chip structures during domain creation. It depends on generic MSI core types, irqdomain flags/tokens, and parent-driver `msi_parent_ops`.

### Integration Points
Used by Loongson PCH MSI, Layerscape SCFG MSI, Marvell GICP/ODMI/SEI, and similar irqchip MSI parent drivers to avoid duplicating MSI domain policy.

### Risks
The helpers intentionally warn and fail for unexpected bus-token combinations. Because they mutate chip callbacks, callers must pass a chip structure that can be safely modified for the child domain. Incorrect parent flags can silently mask child features before required flags are re-added.

### Test Signals
Create PCI MSI, PCI MSI-X, platform MSI, device MSI, and wired-to-MSI domains against several parent ops configurations; verify flag filtering, default affinity/mask/eoi/ack injection, fwnode-parent matching, and rejection of nonzero fwspec parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-msi-lib.c -->
