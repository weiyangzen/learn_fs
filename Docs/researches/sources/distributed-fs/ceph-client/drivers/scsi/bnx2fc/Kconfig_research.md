# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/Kconfig

## Purpose

`Kconfig` declares `SCSI_BNX2X_FCOE`, a tristate option for QLogic FCoE offload support.

## Important APIs, Types, and Definitions

The option depends on `PCI`, `LIBFC`, and `LIBFCOE`; it selects `NETDEVICES`, `ETHERNET`, `NET_VENDOR_BROADCOM`, and `CNIC`. The help text identifies support for QLogic FCoE offload devices.

## Control Flow

There is no runtime control flow. Build-time control flow enables the `bnx2fc` composite object when the symbol is `m` or `y`.

## State and Persistence Behavior

The only persistence is kernel configuration state: absent, module, or built-in.

## Dependencies and Integration Points

The entry ties the driver into SCSI, FC/FCoE, PCI, Ethernet, Broadcom, and CNIC subsystems. CNIC is critical because firmware communication happens through the Broadcom CNIC ULP interface.

## Risks and Edge Cases

The symbol name contains `BNX2X` while the module is `bnx2fc`, which can make configuration less discoverable. Successful build does not guarantee runtime support if bnx2x/CNIC hardware support is unavailable.

## Test Signals

Build `n`, `m`, and built-in configurations; verify dependency resolution, module load, CNIC registration, and FCoE controller creation on supported bnx2x hardware.
