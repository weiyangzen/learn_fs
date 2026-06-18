# sources/distributed-fs/ceph-client/drivers/thunderbolt/ctl.h

## Purpose

`ctl.h` is the private interface for the Thunderbolt control channel and configuration command layer. It exposes the opaque `struct tb_ctl`, request lifecycle APIs, synchronous and asynchronous request helpers, packet result metadata, route header helpers, and standard configuration operations used by the rest of the driver.

## Important APIs, Types, and Functions

`event_cb` is the domain callback type for control-channel events. `struct tb_cfg_result` records the route and port that responded, whether the error was a Linux errno or a Thunderbolt configuration error, and the raw `enum tb_cfg_error` for Thunderbolt errors. `struct ctl_pkg` wraps a received or transmitted control packet with its DMA-backed `ring_frame`.

`struct tb_cfg_request` is the reusable request object. It stores request and response buffers, packet types, expected response size, multipacket count, matching/copy callbacks, completion callback, flags, work item, result, and queue linkage. `TB_CFG_REQUEST_ACTIVE` and `TB_CFG_REQUEST_CANCELED` define request state bits.

The header exports control lifecycle functions, request refcounting and cancellation functions, `tb_cfg_request_sync()`, route helpers `tb_cfg_get_route()` and `tb_cfg_make_header()`, event acknowledgment helpers, raw config read/write, translated config read/write, reset, and upstream-port discovery.

## Control Flow

Higher layers allocate a control channel with `tb_ctl_alloc()`, start it when the domain is ready, and stop/free it during suspend or teardown. Standard config operations allocate a `tb_cfg_request`, fill the packet metadata and callbacks, submit through `tb_cfg_request_sync()`, then release the request.

The header deliberately separates generic request transport from common configuration commands. Callers that need custom matching, such as ICM or DMA safe-mode mailbox access, can fill `struct tb_cfg_request` directly and still use the shared queue, timeout, and completion machinery.

## State and Persistence Behavior

This header defines volatile request and transport contracts. It does not define persistent storage. Persistence-like effects occur only through functions declared here when callers write router or port configuration space, reset devices, acknowledge hotplug notifications, or drive firmware mailboxes over the control channel.

`tb_cfg_make_header()` and `tb_cfg_get_route()` preserve route information across packet headers. The warning in `tb_cfg_make_header()` is important because route high bits are not a full 32-bit field in the wire header.

## Dependencies and Integration Points

The header depends on kernel krefs, Thunderbolt public types, NHI definitions, and message ABI structures from `tb_msgs.h`. It is included by the control-channel implementation, ICM firmware manager, DMA-port mailbox implementation, and other Thunderbolt files that need low-level config-space access.

Request matching and copy function pointers are the main extension point. They allow strict config packet validation for normal requests and relaxed validation for safe-mode DMA mailbox traffic or multipacket ICM responses.

## Risks and Edge Cases

Because `struct tb_cfg_request` stores pointers to caller-owned request and response buffers, those buffers must outlive the request until completion or cancellation is fully flushed. Synchronous helpers satisfy this with stack buffers and `tb_cfg_request_sync()`, but asynchronous users must manage lifetime carefully.

`response_size` and `npackets` are trusted by request-specific copy callbacks. Incorrect values can under-copy, over-copy, or cause unrelated packets to be accepted. Custom match functions must be strict enough to reject stale replies from timed-out requests.

The route helpers warn but do not fail on overflow. Callers should not ignore route construction warnings when adding new packet formats or wider route uses.

## Test Signals

Header-level validation should come from build coverage across all Thunderbolt objects, plus tests or static checks for request lifetime, callback signatures, route round trips, and packet size assumptions. Any changes to `struct tb_cfg_request` should be tested against normal config requests, ICM requests, DMA-port safe-mode requests, and asynchronous NVM authentication requests.
