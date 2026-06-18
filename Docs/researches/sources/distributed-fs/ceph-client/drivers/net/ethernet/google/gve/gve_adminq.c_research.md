# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_adminq.c

## Purpose
Implements the gVNIC admin queue control plane: admin queue allocation/release, command submission and completion polling, device descriptor and option parsing, queue/resource creation and destruction commands, QPL registration, stats/link/timestamp reports, PTYPE map retrieval, flow-rule configuration/query, and RSS configuration/query.

## Important APIs and Functions
Public functions include `gve_adminq_alloc/free/release()`, `gve_adminq_describe_device()`, resource configure/deconfigure, create/destroy Tx/Rx queues, register/unregister page lists, report stats/link/NIC timestamp, verify driver compatibility, get DQO ptype map, configure/query flow rules, and configure/query RSS. Internal command machinery includes `gve_adminq_issue_cmd()`, `gve_adminq_kick_and_wait()`, `gve_adminq_execute_cmd()`, `gve_adminq_execute_extended_cmd()`, and status mapping in `gve_adminq_parse_err()`.

## Control Flow
Allocation creates a DMA pool and one 4 KiB admin queue ring, programs revision-dependent BAR registers, initializes counters and lock, and marks admin queue OK. Synchronous command execution requires the queue to be empty, writes one command, rings the doorbell, waits for event counter advancement, then maps device statuses to errno. Batched queue create/destroy commands issue multiple entries under `adminq_lock` before one kick. Extended commands allocate coherent memory for payloads larger than the 56-byte inline command area.

## State and Persistence
Admin state is held in `gve_priv`: admin queue DMA memory, producer count/mask, per-op counters, fail/timeout counters, state flags, queue format, descriptor limits, feature limits, RSS sizes/cache mode, flow cache sync state, link speed, max pages, event counters, and timestamp support. Device descriptor parsing persists negotiated queue format and optional features into `gve_priv` and `net_device` feature flags.

## Dependencies and Integration Points
Depends on `gve_register.h` BAR register layout, `gve_adminq.h` command ABI, `gve.h` queue state, DMA coherent allocation, mutex locking, PCI device revision, and ethtool RSS structures. It is called by probe/configuration, queue setup/teardown, ethtool RSS/flow steering, stats reporting, reset paths, and PTP timestamp setup.

## Risks and Test Signals
Risks include admin queue timeout requiring reset, command ring overflow logic, endian conversion mistakes, descriptor option bounds, feature negotiation priority, coherent buffer lifetime around device DMA writes, extended command cleanup, flow/RSS descriptor length validation, and cache invalidation after flow changes. Test with descriptor options for GQI/DQO/RDA/QPL, queue create/destroy batches, QPL registration limits, admin status error injection, RSS set/query, flow rule add/delete/reset/query, link speed report, NIC timestamp report, and device reset/release handshakes.
