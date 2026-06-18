# sources/distributed-fs/ceph-client/drivers/mfd/sec-core.h

### Purpose
`sec-core.h` is the private header joining the Samsung SEC PMIC bus drivers, shared core, and IRQ implementation. It declares the shared probe/shutdown/IRQ APIs and PM ops used across direct I2C and ACPM-backed variants.

### Important APIs, Types, And Functions
The header forward-declares `struct i2c_client`, declares `extern const struct dev_pm_ops sec_pmic_pm_ops`, `sec_pmic_probe()`, `sec_pmic_shutdown()`, and `sec_irq_init()`. It references `struct sec_pmic_dev`, `struct device`, and `struct regmap` through included translation-unit context rather than including all type headers itself.

### Control Flow
There is no runtime control flow. Bus drivers include this header to invoke the common core and shutdown paths; the common core includes it to call `sec_irq_init()`; the IRQ file includes it to expose that implementation.

### State, Persistence, And Dependencies
The header owns no state. Its declarations define the linkage contract for shared SEC PMIC runtime state managed in `struct sec_pmic_dev`. Dependencies are compile-time type declarations from the including files and the Samsung public core header.

### Integration Points
`sec-i2c.c` and `sec-acpm.c` consume `sec_pmic_pm_ops`, `sec_pmic_probe()`, and `sec_pmic_shutdown()`. `sec-common.c` consumes `sec_irq_init()`. `sec-irq.c` implements the IRQ initializer declared here.

### Risks
Because this is a private API boundary, signature changes require synchronized edits in all SEC MFD files. Minimal includes keep it light but mean include ordering matters; missing type definitions in a new user could cause compile errors.

### Test Signals
Compile tests across `sec-i2c.c`, `sec-acpm.c`, `sec-common.c`, and `sec-irq.c` are the main validation. Runtime signals are indirect: successful probe, IRQ setup, PM suspend/resume, and shutdown through both bus paths.
