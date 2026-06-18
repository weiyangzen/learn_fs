# sources/cloud-native/nydus/service/src/block_uffd.rs

## Purpose
`block_uffd.rs` exports a RAFSv6 `BlockDevice` through Linux userfaultfd. It supports a daemon socket protocol where clients send a userfaultfd and VMA regions, and an embeddable `UffdCore` that resolves page faults directly. Zerocopy mode returns blob fd/range metadata to clients; copy mode fills faulting pages with `UFFDIO_COPY`.

## Important APIs, Types, And Functions
Kernel-facing types are `UffdMsg`, `UffdPagefault`, `UffdioCopy`, and `UffdioZeropage`; low-level helpers are `read_uffd_msg()`, `uffdio_zeropage()`, `uffdio_copy()`, and `uffdio_wake()`. `UffdCore::handle_page_fault()` is the main resolution entry. It uses `resolve_zerocopy_ranges()`, `resolve_copy()`, and `prefault_ranges()`. `UffdWorker` handles socket connections, handshakes, stat requests, fd passing, UFFD events, response batching, and optional prefault. `UffdService` owns listener/workers/active connections. `UffdDaemon` implements `NydusDaemon`, and `create_uffd_daemon()` wires it to the state machine.

## Control Flow
Service startup creates worker threads with tokio-uring runtimes, binds the Unix socket, accepts clients, and distributes streams round-robin over flume channels. A connection waits for protocol messages and UFFD readiness. Handshake accepts either a `HandshakeRequest` or Firecracker-compatible bare VMA array, takes the first passed uffd fd, closes extras, makes it nonblocking, and optionally spawns prefault. On a page fault, `UffdCore` finds the containing VMA, aligns to the VMA page size, clamps to VMA and device bounds, zero-pages beyond-device or hole regions, then either fetches fd ranges from `BlockDevice::fetch_ranges()` or reads/copies data into the faulting address.

## State, Persistence, And Dependencies
Runtime state is active flags, active socket fd list, scoped blob id, shared `BlobCacheMgr`, socket path, broadcast sender, worker channels/threads, daemon state-machine channels, and per-connection `ConnState` with VMA regions, fault policy, and `AsyncFd<OwnedFd>` for the uffd. The service is explicitly stateless for save/restore. Persistent effects are limited to cache population through `BlockDevice`; page resolution mutates client memory through UFFD ioctls. Dependencies include `sendfd`, `flume`, `tokio::io::unix::AsyncFd`, `tokio_uring`, `mio::Waker`, and `uffd_proto` message types.

## Integration Points
`UffdCore` uses the same `BlockDevice` layout and cache manager as NBD/export. The daemon mode integrates with Nydus daemon lifecycle. The JSON+SCM_RIGHTS protocol is documented as Firecracker compatible and sends `PageFaultResponse` batches with up to `MAX_RANGES_PER_MSG` fds.

## Risks
There are many raw fd ownership transitions; incorrect test or caller ownership can double-close descriptors. `resolve_copy()` reads full block-rounded data but copies only requested `len`, so alignment assumptions matter. `UffdService::run()` computes `worker_num` once; running with zero workers would make round-robin indexing invalid on first connection. `try_recv_from_sock()` assumes one complete JSON message per recv buffer and has no framing for larger/split messages. UFFD tests may require kernel permissions and can be environment-sensitive.

## Test Signals
The file has broad tests for daemon lifecycle, service stop/save/restore, fd closing, socket receive parsing, Firecracker handshake format, prefault, batch responses, stat handling, handshake fd validation, worker creation, async fd sending, graceful shutdown, no-event UFFD handling, core construction, non-pagefault/no-VMA paths, copy and zerocopy page faults, beyond-device zeroing, `resolve_copy`, `resolve_zerocopy_ranges`, `prefault_ranges`, and `uffdio_wake`. Coverage is substantial but relies on Linux userfaultfd support.
