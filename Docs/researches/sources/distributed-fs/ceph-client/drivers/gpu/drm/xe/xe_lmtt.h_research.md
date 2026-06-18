# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt.h

## Purpose
`xe_lmtt.h` declares the SR-IOV PF Local Memory Translation Table API and provides minimal stubs when PCI IOV is disabled.

## Important APIs, Types, And Functions
- Declares software init, hardware init, hardware invalidation, VF page preparation/population/drop, PT-size estimate, and page-size query functions.
- Stubs only `xe_lmtt_init()` and `xe_lmtt_init_hw()` when `CONFIG_PCI_IOV` is disabled.

## Control Flow
PF setup and reset code call into this API when LMTT is supported. Build configuration either links the real implementation or compiles no-op initialization.

## State And Persistence
No state is owned by the header. It exposes operations over `struct xe_lmtt`, which stores root page directory and ops.

## Dependencies And Integration Points
It forward-declares `struct xe_bo`, `struct xe_lmtt`, and `struct xe_lmtt_ops`, and is used by SR-IOV provisioning code.

## Risks
Only two functions are stubbed for non-IOV builds; callers of other LMTT functions must be compiled out under the same config. Public functions assume PF-only usage and initialized ops/root where applicable.

## Test Signals
Build configurations with and without `CONFIG_PCI_IOV`, plus PF flows that call init, reset-time hardware init, map/unmap, and invalidation.
