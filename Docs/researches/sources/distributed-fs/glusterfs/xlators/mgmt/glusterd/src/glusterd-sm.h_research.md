# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-sm.h

## Purpose
Defines the friend state-machine types, peerinfo structure, event/context payloads, quorum contribution enum, and public APIs for GlusterD peer orchestration.

## Important APIs, types, and functions
`gd_quorum_contrib_t` tracks quorum contribution as none, waiting, down, or up. `glusterd_friend_sm_state_t` enumerates peer states from default through request, accepted, rejected, connected, and unfriend states. `glusterd_peerinfo_t` stores peer UUID/hostname(s), state, connection/RPC program pointers, store handle, transition log, quorum flags, generation, and RCU cleanup fields. Context structs include `glusterd_peerctx_t`, `glusterd_friend_sm_event_t`, `glusterd_friend_req_ctx_t`, `glusterd_friend_update_ctx_t`, and `glusterd_probe_ctx_t`. Public functions create/inject/run the state machine, destroy contexts, name states/events, and broadcast friend deletion.

## Control flow
RPC callbacks and connection handlers allocate `glusterd_friend_sm_event_t`, fill peer identity and context, inject it, then call `glusterd_friend_sm()`. State-machine tables in the C file consume the enum values and action-function type declared here.

## State and persistence behavior
The header defines the in-memory peer model that is stored and restored by GlusterD store helpers. Peerinfo includes store handles and transition logs, plus RCU fields for safe deletion. Persistent volume and snapshot state is not defined here but is imported or cleaned by handlers using these contexts.

## Dependencies and integration points
Includes pthread, UUID compatibility, RPC client/server, call stubs, Gluster store, and GlusterD RCU. It is included by RPC ops, connection management, server quorum, op-sm integration, and peer utility code.

## Risks and test signals
Risks include enum/table ordering drift, incorrect context destructor selection for a new event type, RCU lifetime misuse of `glusterd_peerinfo_t`, and quorum contribution semantics changing without updating quorum code. Tests should compile all state-table initializers and exercise every event enum through name lookup and context cleanup.
