# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/global1_atu.c

Purpose: implements Address Translation Unit operations for the switch forwarding database: aging configuration, hash selection, get-next iteration, load/purge, flush/move/remove, and ATU violation interrupt handling.

Important APIs/types/functions: exported functions include `mv88e6xxx_g1_atu_set_learn2all()`, `mv88e6xxx_g1_atu_set_age_time()`, `mv88e6165_g1_atu_get_hash/set_hash()`, `mv88e6xxx_g1_atu_getnext()`, `mv88e6xxx_g1_atu_loadpurge()`, `mv88e6xxx_g1_atu_flush()`, `mv88e6xxx_g1_atu_remove()`, and ATU problem IRQ setup/free. Private helpers pack FIDs across generation-specific registers and marshal `struct mv88e6xxx_atu_entry`.

Control flow: callers wait for the ATU busy bit, write MAC/data/FID context, issue an operation in `MV88E6XXX_G1_ATU_OP`, then wait for completion. Get-next writes the starting MAC only for the first invalid seed entry. Violation IRQ handling clears the violation latch, reads FID/data/MAC, updates per-port counters, traces, and may invoke MAB miss handling.

State and persistence: ATU entries and age/hash settings are hardware state. Per-port violation counters in `chip->ports[]` are runtime software state.

Dependencies/integration: used by bridge/FDB/switchdev code, devlink ATU snapshots/resources, tracepoints, IRQ domains, and MAB handling in `switchdev.h`.

Risks: FID packing differs by database count, so boundary chips need coverage. `spid` is derived from entry state in violation records and is used for counters; member/miss paths assume valid port indexing more strongly than the full-violation path. Flush/move semantics depend on magic entry state values.

Test signals: FDB add/delete/dump across FIDs, age-time range checks, devlink ATU hash get/set, ATU full/member/miss violation tracepoints and counters, and MAB miss learning behavior.
