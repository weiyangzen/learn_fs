<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/cache-bytes.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/cache-bytes.tsx

## Purpose
`cache-bytes.tsx` displays a cache worker's current cached-byte metric in human-readable units.

## Important APIs, Types, and Functions
`WorkerCacheBytes` accepts cache group namespace/name and worker name, calls `useWorkerCacheBytes(namespace, name, workerName, 5000)`, shows an Ant Design `Spin` while loading, and formats `data.result` with an internal `humanReadable(bytes)` helper.

## Control Flow, State, and Persistence
The component is stateless beyond hook data. It refreshes according to the hook's 5000 ms argument and renders `0` when data is absent. The formatter uses logarithms to choose B/KB/MB/GB/TB.

## Dependencies and Integration Points
It is used by `CgWorkersTable` for each worker row and depends on the cache-group API hook returning numeric bytes under `result`.

## Risks and Test Signals
Risks include out-of-range units for petabyte values, `Math.log` behavior for negative/non-numeric input, and many row-level polling hooks creating load on the backend. Signals are format unit tests for 0 and powers of 1024, worker table polling behavior, and API fallback rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/cache-bytes.tsx -->
