# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_relay.h

## Purpose
Declares the GuC SR-IOV relay communication API.

## Important APIs, Types, And Functions
Declares initialization, VF-to-PF send, GuC-to-VF processing, and conditional PF-to-VF send and GuC-to-PF processing. When `CONFIG_PCI_IOV` is disabled, PF APIs are inline stubs returning `-ENODEV`.

## Control Flow
PF and VF callers use send APIs for synchronous request/response relay and GuC CT dispatchers call process APIs for incoming relay events.

## State And Persistence
The header exposes only opaque `struct xe_guc_relay`; implementation-owned lists, mempool, worker, and counters persist in that object.

## Dependencies And Integration Points
Includes Linux types and errno. Integrated with SR-IOV PF services, VF drivers, and GuC CT receive dispatch.

## Risks And Test Signals
Build configuration changes API behavior for PF calls. Callers must handle `-ENODEV` when SR-IOV relay support is unavailable. Compile coverage across PCI_IOV enabled/disabled builds is important.
