<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.h

## Purpose
Declares aggregate properties UI and apply packet.

## Important APIs, Types, And Functions
`AGG_PROP_APPLY_PACKET` carries identity and warning-control values. `Aggregates_ShowProperties` opens properties and can jump to thresholds.

## Control Flow
No runtime flow.

## State And Persistence
No state declared; packets are async task payloads.

## Dependencies And Integration Points
Requires `LPIDENT`, `HWND`, and Win32 scalar types.

## Risks And Edge Cases
Packet field names mirror control IDs, coupling task code to dialog layout.

## Test Signals
Compile producer/consumer and verify apply semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/agg_prop.h -->
