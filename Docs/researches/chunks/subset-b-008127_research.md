# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/db.json lines 9036-9231

## Scope And Purpose

This chunk covers the tail of the Recon web mock API database. It closes the final decommission-information datanode object, then defines mock response bodies for datanode removal, storage distribution, and pending-deletion capacity endpoints:

- `datanodesRemove`, mapped from `/datanodes/remove`.
- `utilization`, mapped from `/storageDistribution`.
- `pendingDeletionDN`, mapped from `/pendingDeletion?component=dn&limit=*`.
- `pendingDeletionOM`, mapped from `/pendingDeletion?component=om`.
- `pendingDeletionSCM`, mapped from `/pendingDeletion?component=scm`.

The file is data, not executable source. Its purpose is to give the local JSON mock server stable payloads that look like Recon backend API responses so the React UI can be developed and manually exercised without a live Ozone cluster.

## Important API Shapes And Fields

The first visible section, lines 9036-9077, finishes a decommission-info datanode entry. It includes topology fields such as `hostNameAsByteString`, `networkName`, `networkLocation`, `networkFullPath`, `numOfLeaves`, and byte-string wrappers with `validUtf8` and `empty` flags. It also includes decommission metrics:

- `decommissionStartTime`
- `numOfUnclosedPipelines`
- `numOfUnderReplicatedContainers`
- `numOfUnclosedContainers`
- `containers.UnderReplicated`
- `containers.UnClosed`

`datanodesRemove` is a minimal response body with `selectedRowKeys`, containing one selected datanode UUID. The frontend datanodes page sends a `PUT` to `/api/v1/datanodes/remove`; in mock mode this fixture acts as the route target for the removal call.

`utilization` is the main storage-distribution response. Its shape matches `UtilizationResponse` in `src/v2/types/capacity.types.ts`:

- `globalStorage`: filesystem capacity, reserved space, derived Ozone capacity, Ozone free/used/committed space.
- `globalNamespace`: total used namespace space and key count.
- `usedSpaceBreakdown`: open key bytes and finalized key bytes.
- `dataNodeUsage`: one record per datanode with UUID, host, capacity, used, remaining, committed, minimum free space, and reserved space.

`pendingDeletionDN` matches the datanode pending-deletion contract:

- `status`: here `FINISHED`, which lets the capacity page stop showing the DN scan as in progress.
- `totalPendingDeletionSize`: aggregate pending deletion bytes.
- `pendingDeletionPerDataNode`: per-datanode pending block size records.
- `totalNodesQueried` and `totalNodeQueriesFailed`: scan coverage metadata.

Two per-datanode entries have `pendingBlockSize: -1`. The v2 capacity page treats this as an error/unavailable sentinel by disabling those datanode options in the selector. The other entries carry concrete byte values used in charts and detail breakdowns.

`pendingDeletionOM` provides `totalSize`, `pendingDirectorySize`, and `pendingKeySize`. `pendingDeletionSCM` provides `totalBlocksize`, `totalReplicatedBlockSize`, and `totalBlocksCount`. These are read by the capacity page's "Pending Deletion" service breakdown.

## Control Flow And Integration

There is no in-file control flow, but the surrounding mock server routing gives this data request flow:

1. `api/routes.json` maps incoming API paths to top-level keys in `api/db.json`.
2. A request for `/api/v1/storageDistribution` resolves to the `utilization` object in this chunk.
3. Requests for `/api/v1/pendingDeletion?component=om`, `/api/v1/pendingDeletion?component=scm`, and `/api/v1/pendingDeletion?component=dn&limit=15` resolve to the three pending-deletion fixtures.
4. The v2 capacity page loads these objects through `useApiData`, combines their numeric fields, and renders utilization and pending-deletion cards.
5. The datanodes pages call `/api/v1/datanodes/remove` through a PUT helper or `useApiData` mutation path; the fixture provides a selected-row echo-like response.

The capacity page uses this data in several derived calculations. It computes "other used space" from Ozone capacity, free space, and used space; displays `totalOzoneCommittedSpace` as container pre-allocated space; sums OM, SCM, and DN pending deletion values; and merges `dataNodeUsage` with `pendingDeletionPerDataNode` by `hostName` for the selected datanode detail view.

## State And Persistence Behavior

The chunk is static JSON persisted in the repository. It does not mutate itself and has no runtime state. Any apparent state, such as `status: "FINISHED"` or `selectedRowKeys`, is fixed mock state returned by the local development API layer.

The persistence contract is still important because consumers assume stable field names and numeric units. The capacity UI treats values as byte counts and formats them for display. The datanode pending-deletion response also models a partially successful scan: `totalNodesQueried` is `7`, `totalNodeQueriesFailed` is `2`, and two datanodes use `-1` as the per-node unavailable sentinel. This lets mock mode exercise both successful and failed datanode pending-deletion paths without backend state transitions.

## Dependencies

Direct dependencies are data-shape dependencies rather than imports:

- `api/routes.json` must keep route-to-key mappings aligned with the top-level keys defined here.
- `src/v2/types/capacity.types.ts` defines the expected TypeScript shapes for storage distribution and pending-deletion responses.
- `src/v2/pages/capacity/capacity.tsx` consumes `utilization`, `pendingDeletionDN`, `pendingDeletionOM`, and `pendingDeletionSCM`.
- `src/v2/pages/datanodes/datanodes.tsx` and the older `src/views/datanodes/datanodes.tsx` consume the datanode remove endpoint.
- Capacity tests under `src/__tests__/capacity` and mock response files under `src/__tests__/mocks/capacityMocks` provide independent test payloads that overlap with these contracts.

The values also depend on Ozone Recon API conventions: SCM, OM, and datanode pending deletion are exposed as separate component-filtered queries, while storage distribution combines global and per-datanode capacity data.

## Risks And Maintenance Notes

The `globalStorage` object in this fixture omits `totalMinimumFreeSpace`, while `GlobalStorage` in `capacity.types.ts` declares it as required. Current capacity rendering paths may not read it, but this is a contract drift risk for future UI changes or stricter validation.

`totalOzoneCommittedSpace` is formatted without a space after the colon (`"totalOzoneCommittedSpace":1022024`). This is valid JSON, but it is inconsistent with the rest of the file and can make generated diffs noisier.

The DN pending-deletion fixture intentionally includes `pendingBlockSize: -1` sentinel values. That is useful for UI coverage, but any consumer that sums per-node values directly instead of using `totalPendingDeletionSize` would undercount. The capacity page currently uses the aggregate total for global DN pending deletion and the sentinel list to disable unavailable selector options.

The `pendingDeletionSCM` field name `totalBlocksize` uses a lowercase `s`, matching the TypeScript type. Renaming it to the more conventional `totalBlockSize` in only one layer would silently break mock-mode display.

The route for DN pending deletion in `routes.json` only matches `/pendingDeletion?component=dn&limit=*`. The v2 capacity page also defines a status URL `/api/v1/pendingDeletion?component=dn` for CSV download polling. If the mock route layer does not have broader matching elsewhere, that polling path may not resolve to this fixture in local mock mode.

The mock values use repeated identical capacities and usage numbers across datanodes. That keeps screenshots predictable, but it gives weak coverage for sorting, scaling, skewed capacity, and high-variance chart behavior.

The `datanodesRemove` object echoes `selectedRowKeys` but does not model failure, partial removal, server-side validation, or asynchronous decommission state changes. UI code that looks correct against this fixture may still need live-backend or MSW tests for real mutation outcomes.

## Test Signals

Useful validation signals for this chunk are mostly frontend and mock-route checks:

- Start the Recon web mock API and verify `/api/v1/storageDistribution` returns the `utilization` object with global storage, namespace, used-space breakdown, and seven datanode usage records.
- Verify `/api/v1/pendingDeletion?component=om`, `/api/v1/pendingDeletion?component=scm`, and `/api/v1/pendingDeletion?component=dn&limit=15` return the expected component-specific payloads.
- Render the v2 capacity page and confirm it shows container pre-allocated space from `totalOzoneCommittedSpace`, pending deletion totals from OM/SCM/DN payloads, and disabled datanode options for entries with `pendingBlockSize: -1`.
- Exercise the capacity CSV download path in mock mode; specifically check whether `/api/v1/pendingDeletion?component=dn` resolves, since the visible mock route only covers the DN query when a `limit` parameter is present.
- Exercise `/api/v1/datanodes/remove` from the datanodes page and confirm the success path reloads data and clears selected rows.
- Keep the existing capacity tests aligned with this fixture's response shapes, especially `DNPendingDeletion.status`, nullable aggregate fields, and the SCM `totalBlocksize` spelling.
