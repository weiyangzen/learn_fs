# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-server-quorum.h

## Purpose
Declares GlusterD server-quorum policy helpers and the public action entry point used by operation validation, peer-state changes, and brick start decisions.

## Important APIs, types, and functions
Defines `GLUSTERD_SERVER_QUORUM` as `"server"`. Declares `glusterd_is_quorum_changed()`, `glusterd_do_quorum_action()`, `glusterd_is_quorum_option()`, `glusterd_is_volume_in_server_quorum()`, `glusterd_is_any_volume_in_server_quorum()`, `does_gd_meet_server_quorum()`, and `does_quorum_meet()`.

## Control flow
Consumers use the option helpers during set/reset validation, use the volume helpers to determine whether quorum applies, call `does_gd_meet_server_quorum()` for current-node eligibility, and call `glusterd_do_quorum_action()` when peer connectivity or imported cluster view changes require service convergence.

## State and persistence behavior
The header stores no state. Its APIs operate on `glusterd_conf_t`, peer quorum contribution state, volume quorum status, and local brick process state in the implementation.

## Dependencies and integration points
Includes `glusterd.h` for volume and translator types. It is included by the friend state machine, quorum implementation, op-sm validation, and brick start paths.

## Risks and test signals
The exposed API is small but high impact: semantic changes affect whether writes and admin operations are allowed. Compile and integration tests should verify all declarations match implementation signatures and that quorum action is reachable from peer-state transitions.
