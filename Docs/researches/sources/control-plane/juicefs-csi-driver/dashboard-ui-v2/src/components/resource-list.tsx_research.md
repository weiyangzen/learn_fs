# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/resource-list.tsx

## Purpose
`ResourcesList` dispatches list routes to the correct dashboard list page.

## APIs, Control Flow, and State
It reads `resources` from `useParams<Params>()`, switches over known resource keys, and renders the corresponding page: application pods, system pods, PVs, PVCs, StorageClasses, CacheGroups, or batch jobs. It is stateless.

## Dependencies and Integration Points
This component couples route names to page modules and must stay aligned with navigation and `getBasePath` known route segments.

## Risks and Test Signals
Adding a new top-level resource requires updates here, `Params`, localization/navigation, and possibly base-path detection. Test direct navigation to each route and unknown routes.
