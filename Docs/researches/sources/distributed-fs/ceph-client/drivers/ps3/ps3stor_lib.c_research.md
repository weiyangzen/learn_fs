# sources/distributed-fs/ceph-client/drivers/ps3/ps3stor_lib.c Research

## Purpose
`ps3stor_lib.c` provides common setup, teardown, and synchronous command helpers for PS3 storage devices. It abstracts hypervisor device open/close, event-port IRQ setup, DMA bounce mapping, accessible-region probing, and LV1 read/write or command completion waits.

## Important APIs, Types, And Functions
Public exports are `ps3stor_setup()`, `ps3stor_teardown()`, `ps3stor_read_write_sectors()`, and `ps3stor_send_command()`. The private `ps3_flash_workaround` tracks flash/disk open ordering to delay disk close while flash remains open. `ps3stor_probe_access()` probes all regions by reading one sector through the bounce LPAR and records accessible regions in `dev->accessible_regions`.

## Control Flow
Setup opens the HV device, creates an event receive port, requests the driver IRQ, validates bounce buffer alignment, creates a PS3 DMA region, maps the bounce buffer for bidirectional DMA, converts it to an LPAR address, then probes accessible regions. Failure paths unwind in reverse order. Teardown unmaps DMA, frees the DMA region, frees IRQ, destroys the receive port, and closes the HV device. Read/write and device-command helpers initialize `dev->done`, submit the LV1 call, wait for interrupt completion, then return either submission failure, stored LV1 status, or zero.

## State And Persistence
Device state is stored in the caller-owned `struct ps3_storage_device`: IRQ, DMA region, bounce DMA address, bounce LPAR, selected region index, completion, tag, and LV1 status. The library mutates `accessible_regions` and chooses the first accessible region. The flash workaround is process-global and persists across storage device setup/teardown calls.

## Dependencies And Integration Points
The file integrates with PS3 system-bus devices, LV1 storage calls, PS3 DMA region management, Linux DMA mapping, completions, IRQ handling, and concrete PS3 storage frontends that provide a bounce buffer and interrupt handler.

## Risks
The flash/disk close workaround is global and has no explicit locking, relying on probe/remove serialization. `ps3stor_probe_access()` performs real sector reads during setup and treats ROM as always accessible. Read/write helpers wait indefinitely for completion if the interrupt path never completes. Submission failures return `-1`, while completion failures return raw LV1 status, so callers must handle mixed error domains.

## Test Signals
Validation should cover flash, disk, and ROM devices; unformatted-disk flash workaround ordering; DMA alignment below 4K and 64K thresholds; failure-path unwinding for every setup step; inaccessible regions; interrupt completion with LV1 error status; and read/write sector calls across the chosen region.
