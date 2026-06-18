<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/pvc-with-selector.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/pvc-with-selector.tsx

## Purpose
`pvc-with-selector.tsx` displays the PVCs matched by a selector, plus their mount pods, or indicates that all PVCs match when no PVC list is supplied.

## Important APIs, Types, and Functions
It defines `columns: ProColumns<PVCWithPod>[]` for PVC name links and mount pod links, then `PVCWithSelector` manages simple pagination around a `ProTable`.

## Control Flow, State, and Persistence
Pagination state is local and total is recalculated when `pvcs` changes. If `pvcs` is undefined, the component renders an "all PVC" message. If `pvcs` is an empty array, it renders nothing. Multiple mount pods are rendered as separate links.

## Dependencies and Integration Points
It is used by patch detail and config update confirmation. It relies on `PVCWithPod` shape from backend selector APIs and React Router resource paths `/pvcs` and `/syspods`.

## Risks and Test Signals
Risks include ambiguous distinction between undefined and empty PVC arrays, no namespace column separate from the link text, and pagination total not resetting current page when data shrinks. Signals are rendering tests for undefined/empty/single/multiple mount pods and route-link correctness.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/pvc-with-selector.tsx -->
