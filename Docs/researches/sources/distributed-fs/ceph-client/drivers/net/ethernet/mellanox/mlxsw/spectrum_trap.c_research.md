# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_trap.c

## Purpose

`spectrum_trap.c` implements devlink trap, trap group, trap policer, and RX listener support for mlxsw Spectrum. It maps hardware trap ids and mirror reasons to devlink-visible traps, registers core listeners, reports trapped/dropped/sampled packets to devlink and psample, programs trap groups and policers in hardware, and provides ASIC-specific trap additions.

## Important APIs, Types, And Functions

`struct mlxsw_sp_trap_policer_item`, `struct mlxsw_sp_trap_group_item`, and `struct mlxsw_sp_trap_item` extend devlink policer/group/trap definitions with hardware ids, priorities, fixed-policer flags, listener arrays, and source-trap markers. The common arrays define policers, groups, and a large table of L2/L3/tunnel/ACL/control traps. ASIC-specific arrays add Spectrum-1 ACL sampling and Spectrum-2 buffer drop/source sampling behavior.

RX listener functions include normal packet delivery with or without offload marks, L3 mark delivery, drop reporting, ACL drop reporting with flow action cookies, PTP delivery, and psample sampling for ingress, egress, and policy-engine sources. Public devlink callbacks include `mlxsw_sp_devlink_traps_init()`, `mlxsw_sp_devlink_traps_fini()`, `mlxsw_sp_trap_init()`, `mlxsw_sp_trap_fini()`, `mlxsw_sp_trap_action_set()`, `mlxsw_sp_trap_group_init()`, `mlxsw_sp_trap_group_set()`, `mlxsw_sp_trap_policer_init()`, `mlxsw_sp_trap_policer_fini()`, `mlxsw_sp_trap_policer_set()`, `mlxsw_sp_trap_policer_counter_get()`, and `mlxsw_sp_trap_group_policer_hw_id_get()`.

## Control Flow

Initialization first reserves and programs a thin CPU policer for the dummy group, initializes that dummy group, builds the policer item array from predefined policers plus dynamically generated extras, registers all policers with devlink, builds common plus ASIC-specific group arrays and registers them, then builds common plus ASIC-specific trap arrays and registers them. Failure unwinds registered objects in reverse order.

When devlink initializes a trap, `mlxsw_sp_trap_init()` looks up the trap item and registers each valid hardware listener with mlxsw core. Trap fini unregisters in reverse listener order. Trap action changes reject source traps and otherwise toggle listener state for DROP versus TRAP actions. Trap group init/set programs HTGT with the selected hardware group id, optional hardware policer id, and configured priority; fixed-policer groups reject policer rebinding.

Packet listeners first associate the skb with the mlxsw port, update per-CPU rx stats, derive the protocol, then either report and consume dropped packets, deliver packets to GRO, mark offloaded packets, invoke PTP receive handling, or sample through psample with metadata from RX mirror metadata.

## State And Persistence

State lives in `mlxsw_sp->trap`: registered policer/group/trap arrays, counts, thin policer hardware id, max policer count, and policer usage bitmap. Hardware state includes QPCR policer programming, HTGT trap group programming, and core trap listener state. Packet statistics are updated in per-port per-CPU counters. There is no disk persistence.

## Dependencies And Integration Points

The file depends on devlink traps, mlxsw core listener registration, register packing for QPCR/HTGT, skb RX metadata, ACL action cookie lookup, PTP receive handling, psample, sampling trigger parameter lookup, port devlink-port lookup, and Spectrum ASIC trap ops from `spectrum_trap.h`.

## Risks And Edge Cases

Listener arrays have a fixed maximum of three entries; adding traps with more hardware reasons requires increasing the limit and auditing loops. Source traps cannot have their action changed because they are controlled by the source subsystem. Policer burst sizes must be powers of two. The thin policer consumes a hardware policer before devlink policers are registered, so available-policer accounting must include reserved bits. Drop listeners push the Ethernet header before devlink reporting and must consume skbs on all paths. Sample metadata depends on RX metadata validity for Tx port, congestion, TC, and latency fields.

## Test Signals

Useful tests include devlink trap list/group/policer registration, trap action changes, rejection of source-trap action changes, fixed-policer rebinding rejection, policer rate/burst programming and counter reads, packet delivery with offload marks, ACL drop cookies, PTP traps, psample ingress/egress/ACL samples, and fault injection through registration and hardware write failures. No local executable tests were run for this research item.
