# sources/distributed-fs/ceph-client/drivers/thunderbolt/tunnel.h

## Purpose

`tunnel.h` is the public internal Thunderbolt tunneling interface. It declares tunnel protocol types, lifecycle states, the central `struct tb_tunnel`, allocation/discovery APIs for PCIe, DP, DMA, and USB3 tunnels, generic lifecycle and bandwidth APIs, tunnel event types, and logging helpers.

## Important APIs, Types, and Functions

`enum tb_tunnel_type` identifies `TB_TUNNEL_PCI`, `TB_TUNNEL_DP`, `TB_TUNNEL_DMA`, and `TB_TUNNEL_USB3`. `enum tb_tunnel_state` distinguishes inactive, activation-started, and fully active tunnels. `struct tb_tunnel` stores references, endpoints, path count and flexible `paths[]` array, protocol callback hooks (`pre_activate`, `activate`, `post_deactivate`, `destroy`, and bandwidth operations), list node, state, bandwidth limits/allocations, DP DPRX state, delayed work, and optional DP activation callback.

The header declares protocol-specific allocators/discoverers, `tb_tunnel_match_dma()`, `tb_tunnel_reserved_pci()`, `tb_tunnel_put()`, `tb_tunnel_activate()`, `tb_tunnel_deactivate()`, active/invalid/path membership checks, maximum/allocated/alloc/consumed/release/reclaim bandwidth functions, type predicate inlines, `tb_tunnel_direction_downstream()`, event emission, and `tb_tunnel_type_name()`.

## Control Flow

The header itself has no executable flow beyond inline predicates. It defines the callback-driven contract used by `tunnel.c`: callers allocate or discover a tunnel, optionally attach it to domain lists, activate it, query or adjust bandwidth while active, deactivate it, and release the reference. DP users may receive a callback when asynchronous DPRX completion changes state from activating to active.

## State and Persistence Behavior

The state model is in-memory. `TB_TUNNEL_INACTIVE` means activation has not been called or has been torn down, `TB_TUNNEL_ACTIVATING` means activation succeeded far enough to reserve/program paths but final completion may still be pending, and `TB_TUNNEL_ACTIVE` means fully active. `struct tb_tunnel` records bandwidth and DP work state across calls; hardware persistence is managed by `tunnel.c` and lower-level path/adapter helpers.

## Dependencies and Integration Points

The header includes `tb.h` for `struct tb`, `struct tb_port`, `struct tb_path`, route helpers, logging helpers, and Thunderbolt topology functions. It is consumed by the connection manager, XDomain code, tests, and any code that tracks or reacts to tunnel events. Logging macros format endpoint route/port pairs and tunnel type through `tb_*` domain logging functions.

## Risks and Edge Cases

The flexible array means allocation must use the correct `npaths` and all users must respect `tunnel->npaths`. Some fields are protocol-specific but live in the shared struct; callers must use the type predicates and exported APIs rather than assuming fields are meaningful for every tunnel. `tb_tunnel_is_active()` deliberately treats DP activating state as not fully active, while `tb_tunnel_consumed_bandwidth()` in the implementation may still report reserved bandwidth for activating DP tunnels. Logging macros assume non-null source and destination ports and are unsafe for incomplete discovered tunnels unless endpoints are validated first.

## Test Signals

Compile coverage and the `test.c` KUnit suite exercise most allocation contracts. Extra checks should cover state transitions, DP callback semantics, bandwidth API return values for inactive tunnels, logging/event behavior with valid endpoints, and misuse resistance for type-specific fields.
