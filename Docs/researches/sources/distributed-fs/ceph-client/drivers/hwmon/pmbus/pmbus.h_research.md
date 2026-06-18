## sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/pmbus.h

Purpose: defines the internal PMBus driver contract shared by `pmbus_core.c`, the generic driver, and chip-specific hwmon drivers. It centralizes standard and virtual register IDs, status bits, sensor classes, formats, capability flags, regulator helper macros, callback hooks, and exported helper prototypes.

Important APIs, types, and functions: `enum pmbus_regs` lists standard PMBus commands and virtual registers for history, VMON, fan/PWM, and sample controls. `struct pmbus_driver_info` is the main integration object: pages, phases, formats, coefficients, function masks, callbacks, regulator descriptors, custom attribute groups, and timing delays. Function masks such as `PMBUS_HAVE_VIN`, `PMBUS_HAVE_STATUS_VOUT`, `PMBUS_PHASE_VIRTUAL`, and `PMBUS_PAGE_VIRTUAL` drive core attribute generation. Regulator macros create `regulator_desc` entries bound to PMBus regulator ops.

Control flow: chip drivers fill `pmbus_driver_info` and pass it to `pmbus_do_probe()`. The core uses callback return conventions: `-ENODATA` means fall back to standard PMBus access, while other negative errors mean the register should be treated as unavailable or failed. Virtual registers must be implemented by chip callbacks unless the core supplies default fan target handling.

State and persistence behavior: this header has no state, but it defines how state is represented: per-page formats and coefficients, per-phase masks, cached core data reached through exported helpers, and access/write/page-change delays consumed by the core.

Dependencies and integration points: includes Linux bitops, cleanup guard support, and regulator descriptors. It exports PMBus namespace helpers for SMBus access, cache clearing, page setting, fault clearing, fan control, driver-info retrieval, locking, and debugfs directory discovery.

Risks and test signals: callback semantics and unit formats are easy to misuse. Test by building multiple chip drivers against the header, verifying namespace exports, virtual-register behavior, write-protection effects, regulator descriptor macros, and guard-based PMBus locking.
