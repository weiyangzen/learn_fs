<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi.c

## Purpose
Generic legacy ULPI transceiver support. It creates a managed `usb_phy`/`usb_otg`, probes ULPI IDs, verifies scratch-register access, programs control flags, and supplies OTG host/VBUS callbacks.

## Important APIs, Types, And Functions
`devm_otg_ulpi_create()` allocates the managed PHY/OTG pair. `ulpi_init()` reads vendor/product IDs, logs known IDs, checks scratch integrity, and programs flags. `ulpi_set_otg_flags()`, `ulpi_set_fc_flags()`, and `ulpi_set_ic_flags()` write ULPI OTG/function/interface registers. `ulpi_set_host()` updates serial/carkit mode and `otg->host`; `ulpi_set_vbus()` updates VBUS drive bits.

## Control Flow
A controller supplies `usb_phy_io_ops`, flags, and later an `io_priv` backend. PHY init uses `usb_phy_io_read/write()` for ULPI access. Host and VBUS changes are applied by OTG callbacks.

## State And Persistence
Managed `usb_phy`, `usb_otg`, flags, I/O ops, `otg->host`, and hardware ULPI control/scratch registers.

## Dependencies And Integration Points
Integrates with legacy `usb_phy`, `usb_otg`, and controller-specific I/O backends such as the viewport backend.

## Risks
Read errors in `ulpi_set_host()`/`ulpi_set_vbus()` are stored in unsigned variables, so negative errors can become bit patterns. Bad platform flags can program invalid electrical modes. Scratch integrity is the main I/O sanity check.

## Test Signals
Known/unknown IDs, scratch failure, all board-used flag combinations, VBUS transitions, host attach/detach, and injected I/O errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-ulpi.c -->
