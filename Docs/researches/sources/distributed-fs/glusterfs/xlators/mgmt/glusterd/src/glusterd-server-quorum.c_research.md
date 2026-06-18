# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-server-quorum.c

## Purpose
Implements server-quorum validation and local brick start/stop reactions when the peer cluster gains or loses quorum. It decides which volume operations are blocked by quorum, computes active and required peer counts, and applies quorum status to each started volume.

## Important APIs, types, and functions
`glusterd_is_quorum_validation_required()` exempts get-like operations and quorum-option changes. `glusterd_validate_quorum()` blocks volume operations when the target volume uses server quorum and the node does not meet quorum. `glusterd_is_quorum_option()`, `glusterd_is_quorum_changed()`, `glusterd_get_quorum_cluster_counts()`, `does_quorum_meet()`, `does_gd_meet_server_quorum()`, `glusterd_is_volume_in_server_quorum()`, and `glusterd_is_any_volume_in_server_quorum()` provide policy helpers. `glusterd_do_volume_quorum_action()` starts or stops local bricks for one volume, and `glusterd_do_quorum_action()` applies this under the GlusterD cluster lock. `check_quorum_for_brick_start()` returns a three-way brick-start decision.

## Control flow
Validation skips status and set/reset of quorum keys, extracts `volname`, ignores nonexistent or non-server-quorum volumes, then checks current cluster quorum. Count calculation starts with self, iterates RCU-protected peers whose `quorum_contrib` is `QUORUM_UP` or `QUORUM_DOWN`, counts only `QUORUM_UP` as active, and derives the required count from `cluster.server-quorum-ratio` or strict majority. Quorum action marks `pending_quorum_action`, takes GlusterD lock, computes counts once, then updates every volume. A volume losing quorum stops local bricks; a volume regaining quorum starts local bricks that are not already start-triggered and stores volinfo because ports may change.

## State and persistence behavior
Runtime state includes peer `quorum_contrib`, volume `quorum_status`, brick `start_triggered`, and `conf->pending_quorum_action`. Persistent state changes occur when regained quorum restarts bricks and `glusterd_store_volinfo()` writes updated volume metadata, especially port changes. Event notifications report quorum lost/regained.

## Dependencies and integration points
Depends on GlusterD peer lists, volume/brick metadata, global options dict, store APIs, op-sm validation, syncop lock/unlock, and brick start/stop helpers. Friend state-machine transitions update quorum contribution and call this logic after peer views settle.

## Risks and test signals
Risks include incorrect percentage ceiling, treating `QUORUM_WAITING` peers as outside quorum, false reconfiguration detection when only one quorum option matches, stopping intentionally down bricks on unrelated peer events, and lock ordering around brick restart. Tests should cover default majority and ratio quorum, validation exemptions, non-server-quorum volumes, lost/regained quorum transitions, unchanged quorum reconnect behavior, volinfo store after restart, and operation rejection message propagation.
