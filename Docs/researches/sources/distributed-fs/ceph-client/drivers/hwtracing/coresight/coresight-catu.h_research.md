# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-catu.h

## Purpose
`coresight-catu.h` defines the register layout, bit fields, CATU driver state, typed register accessors, and helper-device identification predicate used by the CATU implementation.

## Important APIs, Types, And Functions
The register offsets cover control, mode, AXI attributes, IRQ enable, base table address (`SLADDR`), input address (`INADDR`), status, and device architecture. Bit definitions include `CATU_CONTROL_ENABLE`, translate/pass-through modes, AXI `ARCACHE`/`ARPROT` construction helpers, OS AXI defaults, status bits, and IRQ enable constants.

`struct catu_drvdata` is the shared per-device state: programming and AT clocks, MMIO base, registered CoreSight device, IRQ, and raw spinlock. `CATU_REG32()` and `CATU_REG_PAIR()` generate inline accessors over the CoreSight `csdev_access` abstraction, so the C file can use typed `catu_read_*()` and `catu_write_*()` helpers without open-coded offsets. `coresight_is_catu_device()` checks Kconfig, CoreSight device type, and helper subtype.

## Control Flow
The header itself has no runtime control flow. It shapes the C file by guaranteeing all register accesses go through `csdev_access_relaxed_*()` helpers and by providing the predicate used by other CoreSight/TMC code to detect a CATU helper.

## State And Persistence
No state is persisted in the header, but `struct catu_drvdata` is the in-memory state carried from probe through enable, disable, runtime PM, and removal. The generated accessor helpers depend on `drvdata->csdev` being initialized before use.

## Dependencies And Integration Points
The header depends on `coresight-priv.h` for CoreSight access helpers and device type constants. It is consumed by the CATU C file and by any code that needs to test whether a `coresight_device` is a CATU helper.

## Risks
Accessor macros hide offset and width decisions, so register definitions must be correct. `coresight_is_catu_device()` returns false when `CONFIG_CORESIGHT_CATU` is disabled, which protects generic code but means CATU-dependent paths must handle absence cleanly.

## Test Signals
Compile coverage with and without `CONFIG_CORESIGHT_CATU` should exercise the inline predicate. Hardware register smoke tests should confirm the generated 32-bit and paired 64-bit accessors read/write the expected CATU registers.
