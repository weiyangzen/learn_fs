# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/isst_tpmi_core.h

## Purpose

This internal header declares the TPMI SST core entry points used by the auxiliary glue driver.

## Important APIs, Types, And Functions

It declares `tpmi_sst_init()`, `tpmi_sst_exit()`, `tpmi_sst_dev_add()`, `tpmi_sst_dev_remove()`, `tpmi_sst_dev_suspend()`, and `tpmi_sst_dev_resume()`.

## Control Flow

The glue driver calls init before adding the first auxiliary device, add/remove for each TPMI SST auxiliary device, suspend/resume from PM callbacks, and exit after removal.

## State And Persistence

No state is defined in the header; the implementation owns all state.

## Dependencies And Integration Points

The declarations require `struct auxiliary_device` from the auxiliary bus and connect `isst_tpmi.c` to `isst_tpmi_core.c`.

## Risks

The header has no include for `struct auxiliary_device`; it relies on including contexts or implicit forward visibility. Any signature changes must be coordinated with the glue driver and exported symbols.

## Test Signals

Compile/link of `isst_tpmi.o` with `isst_tpmi_core.o`, namespace exports, and probe/remove PM call paths validate it.
