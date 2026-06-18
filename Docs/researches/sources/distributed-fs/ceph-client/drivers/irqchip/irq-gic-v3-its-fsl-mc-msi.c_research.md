# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-v3-its-fsl-mc-msi.c

## Purpose
Creates Freescale Management Complex bus MSI domains backed by GICv3 ITS domains.

## Important APIs, Types, and Functions
`its_msi_irq_chip` forwards mask/unmask/eoi/affinity to the parent MSI stack. `fsl_mc_msi_domain_get_msi_id()` maps an MC device ICID to an ITS DeviceID via OF MSI translation or ACPI IORT. `its_fsl_mc_msi_prepare()` validates DPRC devices and prepares parent allocation. Discovery uses `its_fsl_mc_of_msi_init()`, ACPI MADT parsing, and `early_initcall()`.

## Control Flow
Early init scans OF ITS nodes with `msi-controller` and ACPI generic translator entries. For each ITS fwnode it finds the DOMAIN_BUS_NEXUS parent and creates an FSL-MC MSI irqdomain. During allocation prepare, only FSL-MC DPRC devices are accepted; their ICID-derived DeviceID is placed in scratchpad slot 0, vector count is rounded up with a minimum of 32, and parent ITS prepare is invoked.

## State and Persistence
The MSI domain info and ops are static, with ops marked `__ro_after_init`. No mutable global list is maintained here; created domains are owned by MSI/irqdomain core. Per-allocation DeviceID state is passed through `msi_alloc_info_t`.

## Dependencies and Integration Points
Depends on FSL-MC bus helpers, GICv3 ITS parent MSI domains, OF MSI xlate, ACPI IORT, MADT generic translator parsing, and generic MSI domain infrastructure.

## Risks and Test Signals
Risks include accepting only DPRC devices, missing ITS parent domains at early init, ICID translation mismatches, and ACPI node-name allocation failure paths. Test signals include "fsl-mc MSI domain created" logs, successful DPRC MSI allocation, correct ICID-to-DeviceID mapping in OF and ACPI boots, and parent ITS teardown/allocation behavior.
