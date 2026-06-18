# sources/distributed-fs/ceph-client/include/linux/usb/ulpi.h

## Purpose
This header exposes ULPI OTG transceiver creation and capability flags for USB PHY drivers using the ULPI viewport/register model.

## Important APIs, types, and functions
Key definitions are `ULPI_OTG_*`, `ULPI_IC_*`, and `ULPI_FC_*` flag bits, `devm_otg_ulpi_create()`, and the exported `ulpi_viewport_access_ops`. Disabled-config stubs return `NULL` for transceiver creation.

## Control flow, state, and persistence
Controller drivers call `devm_otg_ulpi_create()` with access ops and capability flags to instantiate a managed `usb_phy`. Register IO is delegated through ULPI viewport ops. State is the transceiver's runtime register configuration and devres-managed lifetime; no persistence is defined.

## Dependencies and integration points
It depends on USB OTG and ULPI register definitions. It integrates host/device controller drivers, OTG role logic, and PHY creation for platforms with external ULPI transceivers.

## Risks and test signals
Risks include wrong capability flags, viewport read/write ordering bugs, and assuming the helper exists when `CONFIG_USB_ULPI` is disabled. Tests should cover creation/removal, register access ops, OTG flag programming, and disabled stubs.
