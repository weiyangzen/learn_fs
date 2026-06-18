<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.h -->
## sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.h

Purpose: private transport ABI for the ADXL34x core and bus wrappers.

Important APIs/types/functions: `struct adxl34x_bus_ops` provides bus type, single-register read/write, and block-read callbacks. The header declares exported `adxl34x_probe()`, `adxl34x_pm`, and `adxl34x_groups`.

Control flow and state: no executable code; bus drivers provide callbacks and receive an opaque `struct adxl34x *` from the core.

State and persistence behavior: this file stores no state. Persistence is in sensor registers and core runtime structures.

Dependencies and integration points: used by `adxl34x.c`, `adxl34x-i2c.c`, and `adxl34x-spi.c`; depends on `struct device` and input/PM declarations from included kernel headers in users.

Risks: bus callbacks must match the core's signed/unsigned return expectations and must fill little-endian axis buffers for block reads.

Test signals: build all transports, check symbol exports under module builds, and inject read/write callback failures in probe and IRQ paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/adxl34x.h -->
