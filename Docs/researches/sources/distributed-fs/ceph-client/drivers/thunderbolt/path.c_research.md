<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/path.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/path.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/path.c` owns Thunderbolt tunnel path discovery, allocation, activation, deactivation, HopID reservation, NFC credit accounting, and path membership checks. The source was read as a complete 618-line file.

## Important APIs, Types, and Functions

Public APIs are `tb_path_discover()`, `tb_path_alloc()`, `tb_path_free()`, `tb_path_deactivate_hop()`, `tb_path_deactivate()`, `tb_path_activate()`, `tb_path_is_invalid()`, and `tb_path_port_on_path()`. Important helpers include `tb_path_find_dst_port()`, `tb_path_find_src_hopid()`, `tb_dump_hop()`, `__tb_path_deactivate_hop()`, `__tb_path_deactivate_hops()`, and `__tb_path_deallocate_nfc()`.

## Control Flow

Discovery follows enabled hop entries from a source port/HopID through path config space until a disabled entry, missing remote port, or `TB_PATH_MAX_HOPS`. It can infer the source HopID by scanning possible source HopIDs until a path ends at the requested destination/HopID. After counting hops, it allocates a flexible `struct tb_path`, optionally reserves exact in/out HopIDs for each discovered hop, records ports and next HopIDs, and marks the path already activated.

Allocation builds a new path between two ports by walking the topology with `tb_next_port_on_path()`, choosing the requested link on non-bonded dual-link segments, reserving the requested source/destination HopIDs and intermediate HopIDs, and filling `path->hops`. Activation runs backward: clear counters, add NFC credits, deactivate any stale hop, populate `struct tb_regs_hop`, set flow-control/shared-buffer bits according to source/internal/destination masks, write hop registers, and unwind written hops/credits on failure. Deactivation clears enable bits, waits for pending to drain, optionally clears flow-control bits, releases NFC credits, and marks the path inactive.

## State and Persistence Behavior

The owned state is heap-allocated `struct tb_path` with flexible hop array plus HopID reservations held in per-port IDAs. Hardware-visible persistent state is the path config space written to each input port. NFC credit changes mutate `port->config.nfc_credits` and hardware `ADP_CS_4` values until reversed.

## Dependencies and Integration Points

The file depends on `tb.h`, port read/write helpers, switch topology helpers from `switch.c`, and constants for path config space. It is used by tunnel builders for PCIe, DisplayPort, USB3, DMA, and XDomain traffic to create hardware routes through the fabric.

## Risks and Edge Cases

Backward activation is intentional to avoid traffic entering an incomplete path; changing order is risky. Failure unwinds must match exactly or leak HopIDs/NFC credits. Incomplete paths are discoverable and callers must validate destination/last port. USB4 and pre-USB4 flow-control clearing differ. Timeout draining disabled hops can leave stale hardware state. Dual-link and bonded/non-bonded transitions can select the wrong lane if link metadata is stale.

## Test Signals

Path allocation/free leak checks, activation/deactivation with injected write failures, discovery of complete and incomplete paths, HopID exhaustion, dual-link lane selection, bonded link transitions, NFC credit accounting, and tunnel-level PCIe/DP/USB3 traffic tests are important validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/path.c -->
