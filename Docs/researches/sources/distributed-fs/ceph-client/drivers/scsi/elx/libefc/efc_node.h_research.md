# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_node.h

## Purpose
`efc_node.h` declares node-level helpers, generic state handlers, frame receive entry points, and inline utilities for remote-node state tracking.

## Important APIs, Types, And Functions
The header defines node database pause bits, `MAX_ACC_REJECT_PAYLOAD`, `enum efc_node_enable`, tracing helpers, `efc_node_evt_set`, frame hold/accept helpers, `efc_node_get_enable`, allocation/attach/free APIs, event posting, common state handler, cleanup, pause state, pending-frame processing, WWN helpers, node lookup, ELS response posting, and receive handlers for ELS/CT/FCP.

## Control Flow And State
Inline helpers update state names and current/previous events on enter/exit, toggle `hold_frames`, and compute local/remote initiator/target capability combinations. Declared functions support the lifecycle from node allocation through attach, login, frame dispatch, pause/resume, shutdown, and free.

## Dependencies And Integration Points
The header includes FC name-server definitions and depends on `struct efc_node`, `struct efc_nport`, `struct efc_sm_ctx`, `struct efc_hw_sequence`, and `struct list_head` from libefc/Linux headers. Device and fabric state machines include it through `efc.h`.

## Risks And Test Signals
Risks include exposing many internals across files, state-name buffers becoming misleading if handlers do not call `efc_node_evt_set`, and capability enum assumptions. Test signals include state trace correctness, pause/resume behavior, `efc_node_get_enable` coverage for all 16 combinations, and frame hold/unhold with pending queues.
