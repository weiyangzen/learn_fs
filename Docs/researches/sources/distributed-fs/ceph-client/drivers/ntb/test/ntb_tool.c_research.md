# sources/distributed-fs/ceph-client/drivers/ntb/test/ntb_tool.c

## Purpose
Provides a comprehensive debugfs NTB exerciser. It exposes local and peer ports, link control, doorbells, scratchpads, messages, inbound MW allocation, outbound MW translation/mapping, and raw MW read/write operations to user space.

## Important APIs, Types, And Functions
- `struct tool_ctx` is per-device state containing waitqueues, peer descriptors, local message/scratchpad descriptors, outbound MW descriptors, and debugfs root.
- `struct tool_peer` holds per-peer inbound MW descriptors, outbound MW wrappers, outgoing messages/scratchpads, and peer debugfs directory.
- `struct tool_mw` represents either an inbound coherent buffer or an outbound ioremapped peer window depending on union member use.
- `tool_ops` handles link, DB, and message events by waking waitqueues.
- `tool_setup_mw()` allocates coherent inbound MW memory, validates alignment, programs inbound translation, and creates an `mwN` data file.
- `tool_setup_peer_mw()` programs peer outbound translation, maps the peer MW BAR, and creates a `peer_mwN` data file.
- `tool_setup_dbgfs()` creates the full debugfs file hierarchy.

## Control Flow
Probe allocates context and peer arrays, initializes inbound/outbound MW metadata, scratchpad metadata, message metadata, sets NTB callbacks, and creates debugfs. Link writes call `ntb_link_enable()` or disable. Doorbell/message/link event files block on waitqueues until the requested state/status appears. MW translation files allocate/free mappings on writes, while MW data files read/write memory buffers or MMIO mappings. Remove tears down debugfs, clears NTB context, disables link, frees MWs, and wakes waiters.

## State And Persistence
State is debugfs-driven and volatile. Inbound MW buffers are coherent DMA allocations until the corresponding translation is cleared or the module is removed. Outbound mappings remain until freed. Waitqueues track asynchronous hardware events. Hardware register state may persist outside the module unless explicitly cleared through the exposed operations.

## Dependencies And Integration Points
Depends on nearly all generic NTB provider operations, debugfs, coherent DMA allocation, ioremap WC, user copy helpers, waitqueues, and PCI DMA resources. It is a manual integration and debugging tool for NTB providers.

## Risks And Edge Cases
- Exposes raw low-level hardware operations to privileged user space; misuse can program bad translations or write arbitrary peer-visible memory.
- `tool_setup_peer_mw()` stores outbound windows globally by `widx`, so a window can be attached to only one peer at a time.
- Several files call provider ops only after checking pointer presence for some APIs, but not all optional APIs are guarded uniformly.
- Event waits compare exact DB/message status values; unrelated bits can keep waits blocked.
- Memory-window size/address inputs come from userspace and rely on provider validation for correctness.

## Test Signals
Debugfs hierarchy should reflect provider capabilities: ports, DB masks, SPADs, messages, and per-peer MW translation files. Manual tests can enable link, block on link events, ring/clear DBs, write/read SPADs/messages, allocate inbound MWs, map outbound MWs, and verify data across peers.
