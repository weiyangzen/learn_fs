<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mbigen.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mbigen.c

### Purpose
`irq-mbigen.c` implements HiSilicon MBIGEN, a wired-interrupt-to-MSI generator. It creates device MSI domains for OF child interrupt-controller nodes or an ACPI device, programs MBIGEN vector/type/clear registers, and routes events to an ITS/MSI parent.

### Important APIs, Types, And Functions
`struct mbigen_device` stores the platform device and MMIO base. Address helpers compute node, vector, type, and clear register offsets. `mbigen_msi_template` supplies the MSI chip, translate, and descriptor setup callbacks. `mbigen_domain_translate()` validates pin numbers and trigger type. `mbigen_write_msi_msg()` writes the event ID into the vector register.

### Control Flow
Probe maps the MBIGEN resource, then either creates device domains for child OF interrupt-controller nodes using their `num-pins` or creates one ACPI device domain from the `num-pins` property. Allocation is handled by the MSI core using `mbigen_msi_template`: translation validates pins 64-1407 and level-high or edge-rising type; descriptor setup copies the firmware hwirq; EOI writes the clear register then EOIs the parent; type programming updates MBIGEN type registers.

### State, Persistence, And Dependencies
State is devm-managed private data and per-device MSI domains attached to child devices. It depends on MSI/ITS infrastructure, OF platform population, ACPI device properties, MBIGEN register layout, and `msi_create_device_irq_domain()`.

### Integration Points
MBIGEN child devices expose interrupt-controller domains that convert wired pins into MSI messages consumed by an ITS or other MSI parent domain.

### Risks
Pins 0-63 are reserved and rejected. Offset calculations skip the clear register window for high node IDs; regressions here can corrupt the clear register. `mbigen_write_msi_msg()` only programs event ID and assumes doorbell address is encoded in hardware. Failed OF child domain creation can leave previously created child devices.

### Test Signals
Validate OF and ACPI domain creation, invalid pin/type rejection, vector register event ID writes, type register updates for level/edge, EOI clear writes, high pin offsets around the clear-register skip, and MSI parent availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mbigen.c -->
