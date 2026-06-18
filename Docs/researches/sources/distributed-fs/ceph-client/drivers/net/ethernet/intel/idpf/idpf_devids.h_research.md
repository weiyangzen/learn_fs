# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_devids.h

## Purpose
This header defines the PCI device ids recognized by the IDPF driver for PF and VF functions. It is a small shared include used by PCI probe/id-table code and device-type selection logic.

## Important APIs, Types, And Functions
The two definitions are `IDPF_DEV_ID_PF` with value `0x1452` and `IDPF_DEV_ID_VF` with value `0x145C`. There are no functions or structures.

## Control Flow
The ids influence probe-time control flow in `idpf_main.c`: matching PCI ids select the driver, and device id checks choose PF-specific `idpf_dev_ops_init()` or VF-specific `idpf_vf_dev_ops_init()`.

## State And Persistence
No runtime state is stored. The constants are compiled into the module PCI id table and device dispatch logic.

## Dependencies And Integration Points
The header is guarded by `_IDPF_DEVIDS_H_` and is included by IDPF PCI code. It integrates with Linux PCI matching through `PCI_VDEVICE(INTEL, ...)` entries elsewhere.

## Risks
An incorrect id prevents the driver from binding to supported hardware or can bind it to the wrong function type. PF/VF id confusion would select the wrong register operation table and break mailbox/reset setup.

## Test Signals
Probe tests should confirm both PF and VF PCI ids match the driver and route to the expected device ops. Static analysis can verify no duplicate or stale ids conflict with adjacent Intel drivers.
