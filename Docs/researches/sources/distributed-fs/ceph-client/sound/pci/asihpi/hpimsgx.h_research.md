# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsgx.h

## Purpose
This header exposes the extended HPI message entry point and aliases it as the lower-layer message implementation.

## Important APIs, Types, And Functions
It defines `HPIMSGX_ALLADAPTERS` as `0xFFFF`, declares `hpi_send_recv_ex(struct hpi_message *, struct hpi_response *, void *h_owner)`, and maps `HPI_MESSAGE_LOWER_LAYER` to that function.

## Control Flow
There is no runtime flow in the header. Including files call `hpi_send_recv_ex()` directly or through the macro.

## State, Persistence, And Dependencies
The header stores no state. It depends on `hpi_internal.h` for HPI message and response structures.

## Integration Points
Used by `hpioctl.c`, `hpimsgx.c`, and lower common HPI code to bind the generic HPI message path to the Linux extended router.

## Risks
The macro alias can hide the true dispatch target in call graphs and makes replacement require preprocessor coordination. The owner argument is untyped, so misuse is only detected by conventions in `hpimsgx.c`.

## Test Signals
Builds should verify that generic lower-layer calls resolve to `hpi_send_recv_ex()`, and open/cleanup tests should pass distinct file-owner pointers through this API.
