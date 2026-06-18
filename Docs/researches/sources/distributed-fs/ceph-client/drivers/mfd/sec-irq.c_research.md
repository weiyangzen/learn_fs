# sources/distributed-fs/ceph-client/drivers/mfd/sec-irq.c

### Purpose
`sec-irq.c` defines the regmap IRQ topology for Samsung SEC/S5M/S2M PMIC families and exports `sec_irq_init()` for the shared core. It supports classic single PMIC IRQ chips and the newer S2MPG1x two-stage common-to-PMIC chained IRQ design.

### Important APIs, Types, And Functions
The exported entry point is `sec_irq_init(struct sec_pmic_dev *sec_pmic)`. S2MPG-specific helpers are `sec_irq_init_s2mpg1x()` and `s2mpg1x_add_chained_pmic()`. Static data includes regmap IRQ arrays for S2MPG10/11 common and PMIC events, S2MPS11/14-style events, S2MPU02/05, and S5M8767, plus corresponding `struct regmap_irq_chip` definitions.

### Control Flow
For S2MPG10/11, `sec_irq_init()` delegates to `sec_irq_init_s2mpg1x()`, which obtains the named `"common"` regmap, registers a one-register common IRQ chip on the parent IRQ, maps the PMIC-source parent virq, and registers a second PMIC regmap IRQ chip on that virq with `IRQF_SHARED`. For classic devices, `sec_irq_init()` chooses a single regmap IRQ chip by device type and registers it against `sec_pmic->regmap_pmic` and `sec_pmic->irq`. S2DOS05 returns NULL because it has no interrupt setup here; missing IRQs also return NULL after warning.

### State, Persistence, And Dependencies
Runtime state is regmap IRQ chip data and generated IRQ domains. Persistent hardware state includes interrupt masks and acknowledgements managed by regmap-irq. Dependencies include regmap-irq, Samsung PMIC register headers, `struct sec_pmic_dev`, and the common regmap created by `sec-acpm.c` for S2MPG devices.

### Integration Points
`sec-common.c` calls `sec_irq_init()` during parent probe and passes the resulting IRQ domain to MFD children. S2MPG10/11 meter/regulator/RTC/GPIO children rely on the chained PMIC domain, while classic S2MPS/S2MPU/S5M children use direct PMIC IRQ domains.

### Risks
Returning NULL for S2DOS05 or missing IRQs requires callers to avoid blindly dereferencing IRQ data; the current common code's IRQ-domain handling should be scrutinized. S2MPG chained setup depends on the `"common"` regmap being attached before `sec_pmic_probe()`. Large hand-written IRQ tables can drift from datasheets. Some S2MPS-family chips share the S2MPS14 IRQ table through a macro, which assumes compatible bit assignments.

### Test Signals
Tests should validate classic IRQ delivery for S5M8767, S2MPS11/13/14/15, S2MPA01, S2MPU02, and S2MPU05, plus no-IRQ behavior. S2MPG tests should verify the common IRQ source maps to the chained PMIC chip and that PMIC child events are delivered from the second domain. Fault tests should cover missing `"common"` regmap, parent virq mapping failure, and regmap IRQ add failure.
