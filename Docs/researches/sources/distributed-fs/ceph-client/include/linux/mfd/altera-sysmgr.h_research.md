<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/altera-sysmgr.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/altera-sysmgr.h

## Purpose
This header exposes a small lookup API for Intel/Altera system manager regmaps referenced from device tree phandles. It lets drivers obtain a shared system-manager regmap without directly owning the MFD implementation.

## Important APIs, Types, And Functions
- `altr_sysmgr_regmap_lookup_by_phandle(struct device_node *np, const char *property)` returns a system-manager regmap for a named phandle property when `CONFIG_MFD_ALTERA_SYSMGR` is enabled.
- The disabled-Kconfig inline stub returns `ERR_PTR(-ENOTSUPP)`.
- The header includes error helpers and Stratix10 SMC firmware definitions needed by the implementation ecosystem.

## Control Flow
Consumers call the lookup helper during probe, passing their device node and the property that references the system manager. With the MFD enabled, the implementation resolves the phandle and returns the regmap. Without it, callers receive an encoded unsupported error and should defer or disable dependent features.

## State And Persistence
The header defines no state. Returned regmaps access shared system-manager hardware state. The fallback path creates no persistent state and signals unsupported configuration through an error pointer.

## Dependencies And Integration Points
It depends on device-tree nodes, regmap, Linux error-pointer conventions, and Intel Stratix10 firmware/SMC context. It integrates with SoC drivers needing system-manager registers for pin, clock, reset, FPGA, or firmware-mediated configuration.

## Risks And Edge Cases
- Consumers must check `IS_ERR()` before using the returned regmap, especially because the disabled stub returns `-ENOTSUPP`.
- Missing phandles and disabled Kconfig are different operational cases but both surface as lookup errors.
- Shared system-manager register writes may affect unrelated subsystems; consumers need mask-specific updates and documented ownership.

## Test Signals
Build with and without `CONFIG_MFD_ALTERA_SYSMGR`, test successful phandle lookup, missing-property error handling, disabled-Kconfig fallback, regmap read/update from a consumer, and conflict-free access when multiple consumers share the same system manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/altera-sysmgr.h -->
