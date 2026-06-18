# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/utils/index.ts

## Purpose
This file holds dashboard utility logic for status badges, failure diagnostics, pod status calculation, API base URL construction, fetch wrappers, image capability checks, upgrade status, and TTL formatting.

## APIs, Control Flow, and State
Status helpers map Node/PV/PVC/pod/job states to Ant Design colors/statuses. Diagnostic helpers inspect PVC/PV phases, pod readiness, scheduling, node readiness, CSI node and mount pod health, sidecar labels, deletion timestamps, finalizers, and container statuses to return localization IDs. `podStatus` mirrors kubectl pod status logic for init containers, waiting/terminated states, deletion, and NodeLost. `getBasePath` detects subpath hosting, `getHost` uses `VITE_HOST`, and `apiFetch`/`apiFetchBlob` wrap fetch error handling. Image helpers parse CE/EE tags and compare versions for smooth upgrade/debug support.

## Dependencies and Integration Points
Almost every page imports this module for badges, failure tooltips, API calls, or feature gating. Hooks use fetch wrappers; modals use version/image helpers.

## Risks and Test Signals
Some readiness logic assumes both Ready and ContainersReady must be true. Terminating helpers compare `node.status?.phase` to `Ready`, which is not a standard Node phase. Query/base-path logic must match deployment paths. Test kubectl-like pod statuses, failure message IDs, version parsing for latest/dev/nightly, fetch 204 handling, and subpath hosting.
