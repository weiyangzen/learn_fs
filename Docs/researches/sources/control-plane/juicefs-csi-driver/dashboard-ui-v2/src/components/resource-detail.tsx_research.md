# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/resource-detail.tsx

## Purpose
`ResourcesDetail` is the central route dispatcher for resource detail URLs.

## APIs, Control Flow, and State
It reads `resources`, `namespace`, and `name` from `useParams<DetailParams>()` and switches to `PodDetail`, `SCDetail`, `PVDetail`, `PVCDetail`, `CgDetail`, or `BatchUpgradeJobDetail`. Unknown route segments render `Not Found`. It has no persistent state.

## Dependencies and Integration Points
The route parameter contract is defined in `types/index.ts`. It bridges the router to page components for `/pods`, `/syspods`, `/storageclass`, `/pvs`, `/pvcs`, `/cachegroups`, and `/jobs`.

## Risks and Test Signals
The batch job branch passes only `jobName`, while `BatchUpgradeJobDetail` also checks `namespace === ''`; because undefined is not equal to empty string this currently proceeds. Test every route segment and unknown values with missing params.
