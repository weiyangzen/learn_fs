# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_sm.h

## Purpose
`efc_sm.h` defines libefc's event vocabulary and generic state-machine API.

## Important APIs, Types, And Functions
`enum efc_sm_event` covers common lifecycle events, domain events, nport events, ELS/login events, unsolicited FC protocol events, node discovery/refound/missing events, shutdown reasons, and SCSI/backend completion events. `EFC_SM_EVENT_NAME` provides string mappings. The API declares `efc_sm_post_event`, `efc_sm_transition`, `efc_sm_disable`, and `efc_sm_event_name`.

## Control Flow And State
Events are the cross-file contract for all state machines. Hardware callbacks, ELS completions, receive-frame decoding, SCSI backend completions, timers, and shutdown paths all converge through these enum values. The must-be-last `EFC_EVT_LAST` bounds name lookup.

## Dependencies And Integration Points
The header forward-declares `struct efc_sm_ctx`; the actual context is defined in `efclib.h`. It is consumed by all domain/nport/node/device/fabric headers and implementations.

## Risks And Test Signals
Risks include incomplete string mapping for newer events, stale comments for "Sport" naming, and callers relying on events not handled by a given state. Test signals include compile coverage after enum edits, event-name assertions, and transition traces verifying every hardware/protocol callback maps to a meaningful event.
