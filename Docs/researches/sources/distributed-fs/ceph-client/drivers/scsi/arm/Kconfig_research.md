# sources/distributed-fs/ceph-client/drivers/scsi/arm/Kconfig

## Purpose
This Kconfig file defines build-time options for legacy Acorn ARM SCSI host drivers under `drivers/scsi/arm`. It gates each card driver on `ARCH_ACORN && SCSI` and selects SPI transport attributes for drivers that expose traditional parallel SCSI parameters.

## Important configuration symbols
- `SCSI_ACORNSCSI_3`: tristate support for the Acorn SCSI card (`aka30`), depends on `ARCH_ACORN && SCSI`, selects `SCSI_SPI_ATTRS`.
- `SCSI_ACORNSCSI_SYNC`: bool enabling SCSI-2 synchronous transfer negotiation for `SCSI_ACORNSCSI_3`.
- `SCSI_ARXESCSI`: tristate support for an ARXE NCR53c94-based controller on Acorn Archimedes systems.
- `SCSI_CUMANA_2`: tristate support for Cumana SCSI II.
- `SCSI_EESOXSCSI`: tristate support for EESOX SCSI.
- `SCSI_POWERTECSCSI`: tristate support for PowerTec SCSI.
- `SCSI_CUMANA_1` and `SCSI_OAK1`: marked after a comment as not fully supported; both depend on `ARCH_ACORN && SCSI`, and `SCSI_OAK1`/`SCSI_CUMANA_1` select `SCSI_SPI_ATTRS`.

## Control flow and state behavior
Kconfig has declarative build control rather than runtime flow. User selections determine which object lists in the adjacent Makefile become built-in or modules. `SCSI_ACORNSCSI_SYNC` is a feature flag consumed by the Acorn SCSI implementation for synchronous negotiation behavior.

## Persistence behavior
Selections persist in the kernel `.config`, not in runtime driver state. The file does not store data or affect runtime persistence directly.

## Dependencies and integration points
The file integrates with the kernel Kconfig menu for SCSI drivers and the `drivers/scsi/arm/Makefile`. It depends on architecture support (`ARCH_ACORN`), the SCSI core, and, for selected drivers, `SCSI_SPI_ATTRS`.

## Risks and edge cases
- These drivers are architecture-specific and legacy; enabling them outside Acorn ARM hardware is prevented by dependency checks.
- The "not fully supported" comment covers CumanaSCSI I and Oak SCSI, signalling higher maintenance and runtime risk.
- `SCSI_ACORNSCSI_SYNC` can improve performance but the help text warns that some devices mishandle synchronous transfer negotiation.

## Test signals
- Kconfig tests should verify symbols appear only for `ARCH_ACORN && SCSI`.
- Build tests should cover `y` and `m` selections for each tristate and synchronous negotiation enabled/disabled for Acorn SCSI.
- Runtime tests require real or emulated Acorn SCSI hardware, with special attention to synchronous negotiation compatibility.
