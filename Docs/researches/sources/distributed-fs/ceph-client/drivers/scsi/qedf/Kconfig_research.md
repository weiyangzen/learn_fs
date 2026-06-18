# sources/distributed-fs/ceph-client/drivers/scsi/qedf/Kconfig

## Purpose
This Kconfig entry exposes `CONFIG_QEDF`, the QLogic FastLinQ 41000-series FCoE offload initiator driver, as a tristate option.

## Important APIs, types, and functions
No C symbols are defined. The configuration symbol is `QEDF` with prompt `QLogic QEDF 25/40/100Gb FCoE Initiator Driver Support`. It depends on `PCI`, `SCSI`, `QED`, `LIBFC`, and `LIBFCOE`, and selects `QED_LL2` and `QED_FCOE`.

## Control flow
Build-system control flow is dependency-driven: the option is visible only when the required PCI, SCSI, QED, libfc, and libfcoe infrastructure is enabled. Enabling it forces lower-level QED LL2 and FCoE support so the driver can bind to hardware and offload FCoE traffic.

## State and persistence behavior
The file has no runtime state. Its persistent effect is kernel configuration state in `.config`, which determines whether `qedf.o` is built in, built as a module, or omitted.

## Dependencies and integration points
It integrates the driver into the kernel's SCSI and FCoE stacks and into QED core support. The selected options imply that QEDF relies on QED firmware/hardware services plus libfc/libfcoe protocol layers.

## Risks and test signals
The main risks are dependency drift and accidental prompt invisibility or missing selected transport support. Test signals are Kconfig resolution for built-in and module builds, compile coverage with `QEDF=m` and `QEDF=y`, and verification that disabling `QED`, `LIBFC`, or `LIBFCOE` correctly hides or rejects QEDF.
