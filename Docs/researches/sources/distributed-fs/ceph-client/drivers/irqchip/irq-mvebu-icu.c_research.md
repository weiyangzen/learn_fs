<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-icu.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-icu.c

### Purpose
`irq-mvebu-icu.c` implements the Marvell CP110 ICU wired-to-MSI bridge. It supports NSR and SEI ICU subsets, legacy and child-node bindings, and configures ICU interrupt entries to emit MSI messages toward a platform MSI parent.

### Important APIs, Types, And Functions
`struct mvebu_icu` stores base and device. `struct mvebu_icu_msi_data` binds an ICU instance to subset data and one-time MSI address initialization. `mvebu_icu_translate()` validates firmware specs and trigger type. `mvebu_icu_write_msi_msg()` initializes set/clear message addresses and writes `ICU_INT_CFG()`. Separate MSI templates cover NSR and SEI behavior.

### Control Flow
The parent ICU probe maps registers, detects legacy single-node bindings, clears existing NSR/SEI configurations, stores drvdata, and either probes a synthetic subset or populates child subset devices. Subset probe gets the platform MSI parent domain, selects NSR or SEI template, and creates a device IRQ domain with `ICU_MAX_IRQS`. MSI message writes program the ICU set/clear target addresses once per subset, then enable the hwirq, encode type and group, and mirror SATA0/SATA1 entries when required.

### State, Persistence, And Dependencies
State includes mapped ICU registers, static key for legacy bindings, per-subset initialized atomics, MSI domain data, and ICU configuration registers. Dependencies include platform MSI domains, OF child population, MSI device domains, `irq-msi-lib.c`, and `mvebu-icu.h` group constants.

### Integration Points
Devices with wired ICU interrupts get a per-device MSI domain; the ICU converts their lines into MSIs routed through GICP/SEI-like platform MSI parents.

### Risks
Legacy binding mode globally affects parameter count and group interpretation. SEI subset translation forces edge-rising and comments that handling is unreliable because ICU input semantics differ. SATA entries are intentionally programmed in pairs. One-time address initialization relies on the first nonzero MSI message.

### Test Signals
Validate legacy and child-node bindings, NSR and SEI subsets, invalid hwirqs and parameter counts, MSI write and clear paths, SATA paired programming, probe deferral without MSI parent, and clearing firmware-provided ICU state on boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-mvebu-icu.c -->
