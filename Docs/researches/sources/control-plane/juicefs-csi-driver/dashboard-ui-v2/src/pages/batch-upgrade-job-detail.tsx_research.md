# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/batch-upgrade-job-detail.tsx

## Purpose
`BatchUpgradeJobDetail` shows one batch upgrade job, streams its logs, and visualizes per-pod progress.

## APIs, Control Flow, and State
It fetches `UpgradeJobWithDiff` with `useUpgradeJob`, derives total pods, per-pod status map, job status, TTL deletion countdown, and progress percent from `config.batches`. It opens a log WebSocket at `/api/v1/ws/batch/upgrade/jobs/:jobName/logs`, appends logs, parses `POD-START`, `POD-SUCCESS`, and `POD-FAIL` messages into status and fail-reason maps, and refreshes job data on close. The UI composes `UpgradeBasic`, progress, `PodUpgradeTable`, and a Monaco log collapse.

## Dependencies and Integration Points
It depends on job API hooks, `useWebsocket`, upgrade components, backend log grammar, and `timeToBeDeletedOfJob`.

## Risks and Test Signals
`calculatePercent` can use stale `diffStatus` immediately after `setDiffStatus`. Regexes accept only DNS-like pod names. Test live status parsing, completed jobs with no logs, failed pods, TTL display, and WebSocket reconnect/close.
