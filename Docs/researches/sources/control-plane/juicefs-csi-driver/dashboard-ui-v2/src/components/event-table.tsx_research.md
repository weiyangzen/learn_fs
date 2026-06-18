<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/event-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/event-table.tsx

## Purpose
`event-table.tsx` displays Kubernetes events related to a pod, PV, or PVC.

## Important APIs, Types, and Functions
`EventTable` takes `source`, `name`, and optional `namespace`, calls `useEvents`, sorts events by `firstTimestamp` or `eventTime`, and renders type, reason, creation time, source component, and message columns in an Ant Design table.

## Control Flow, State, and Persistence
The component mutates the fetched `data` array in a `useEffect` to sort newest-first. It renders without pagination and uses event UID as row key.

## Dependencies and Integration Points
It integrates resource detail views with the backend events API. It depends on Kubernetes event timestamp fields from both old and new event API shapes.

## Risks and Test Signals
Risks include in-place mutation of SWR/cache data, invalid dates for missing timestamps, large event lists without pagination, and no empty/loading state. Signals are timestamp ordering tests, old/new event shape fixtures, and resource detail rendering with no events.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/event-table.tsx -->
