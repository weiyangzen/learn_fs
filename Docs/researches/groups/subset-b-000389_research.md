# Research Report: subset-b-000389

This grouped report covers the requested JuiceFS CSI driver dashboard UI files and the generated Kubernetes deployment manifest. Each section is titled with the original source path and wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pv-basic.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pv-basic.tsx

## Purpose
`PVBasic` renders the detail-card view for a Kubernetes PersistentVolume in the dashboard. It shows identity, binding, storage, CSI, lifecycle, labels, annotations, volume attributes, mount options, and a YAML modal.

## APIs, Control Flow, and State
The component accepts a `PV` prop, keeps local modal state, and derives `volumeAttributes`, `labels`, and `annotations` arrays with `useEffect` when the PV object changes. `ProDescriptions` links claim refs to `/pvcs/:namespace/:name`, storage classes to `/storageclass/:name`, maps access modes through `accessModeMap`, and uses `getPVStatusBadge` for status coloring. `YamlModal` receives `YAML.stringify(pv)`.

## Dependencies and Integration Points
It depends on Ant Design Pro, `react-intl`, `react-router-dom`, `yaml`, `YamlIcon`, `YamlModal`, `PV` typing, and utility badge logic. It is used by the PV detail page after `usePV` fetches `/api/v1/pv/:name/`.

## Risks and Test Signals
Creation timestamps are cast directly and can render invalid dates if absent. Derived arrays are local duplicated state rather than pure render derivations. Test with PVs that have no claimRef, no labels, many CSI attributes, missing status, and different access modes.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pv-basic.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pvc-basic.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pvc-basic.tsx

## Purpose
`PVCBasic` renders a PersistentVolumeClaim summary for the PVC detail page, including Kubernetes identity, bound PV, namespace, capacity request, access modes, storage class, phase, labels, annotations, and raw YAML.

## APIs, Control Flow, and State
The component accepts a `PVC`, manages YAML modal visibility, and derives display arrays for labels and annotations in `useEffect`. The descriptions table links `spec.volumeName` to `/pvs/:name` and `spec.storageClassName` to `/storageclass/:name`, maps access modes through `accessModeMap`, and colors phase with `getPVCStatusBadge`.

## Dependencies and Integration Points
It integrates with `PVCDetail`, `YamlModal`, `YamlIcon`, `react-intl`, router links, and the `PVC` type from `types/k8s`. It expects the hook layer to provide a complete PVC object from `/api/v1/pvc/:namespace/:name/`.

## Risks and Test Signals
`getPVCStatusBadge(pvc)` is called while the render callback parameter is named `pv`, which is harmless but confusing. Timestamp and nested spec/status fields are optimistic. Test pending/unbound PVCs, PVCs without storage class, and PVCs with empty metadata maps.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pvc-basic.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pvs-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pvs-table.tsx

## Purpose
`PVsTable` shows the PersistentVolumes associated with a StorageClass inside the StorageClass detail page.

## APIs, Control Flow, and State
It accepts an `sc` name, calls `usePVOfSC(sc)`, returns `null` when no PVs are available, and otherwise renders an Ant Design table with PV name, phase badge, and creation timestamp. Names link to `/pvs/:name/`.

## Dependencies and Integration Points
The hook calls `/api/v1/storageclass/:name/pvs`; status color comes from `getPVStatusBadge`. `SCDetail` embeds this table below StorageClass parameters and mount options.

## Risks and Test Signals
The table does not show loading or error state and renders raw timestamp strings unlike other pages that localize dates. Test empty StorageClasses, PVs with missing UID row keys, and status phase variants.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pvs-table.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/resource-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/resource-detail.tsx

## Purpose
`ResourcesDetail` is the central route dispatcher for resource detail URLs.

## APIs, Control Flow, and State
It reads `resources`, `namespace`, and `name` from `useParams<DetailParams>()` and switches to `PodDetail`, `SCDetail`, `PVDetail`, `PVCDetail`, `CgDetail`, or `BatchUpgradeJobDetail`. Unknown route segments render `Not Found`. It has no persistent state.

## Dependencies and Integration Points
The route parameter contract is defined in `types/index.ts`. It bridges the router to page components for `/pods`, `/syspods`, `/storageclass`, `/pvs`, `/pvcs`, `/cachegroups`, and `/jobs`.

## Risks and Test Signals
The batch job branch passes only `jobName`, while `BatchUpgradeJobDetail` also checks `namespace === ''`; because undefined is not equal to empty string this currently proceeds. Test every route segment and unknown values with missing params.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/resource-detail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/resource-list.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/resource-list.tsx

## Purpose
`ResourcesList` dispatches list routes to the correct dashboard list page.

## APIs, Control Flow, and State
It reads `resources` from `useParams<Params>()`, switches over known resource keys, and renders the corresponding page: application pods, system pods, PVs, PVCs, StorageClasses, CacheGroups, or batch jobs. It is stateless.

## Dependencies and Integration Points
This component couples route names to page modules and must stay aligned with navigation and `getBasePath` known route segments.

## Risks and Test Signals
Adding a new top-level resource requires updates here, `Params`, localization/navigation, and possibly base-path detection. Test direct navigation to each route and unknown routes.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/resource-list.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/sc-basic.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/sc-basic.tsx

## Purpose
`SCBasic` renders core StorageClass metadata for the detail page and exposes the full StorageClass YAML.

## APIs, Control Flow, and State
It accepts a Kubernetes `StorageClass`, stores YAML modal visibility, and renders reclaim policy, allow-volume-expansion as localized boolean text, and creation time via `ProDescriptions`. `YamlModal` displays `YAML.stringify(sc)`.

## Dependencies and Integration Points
It uses Ant Design Pro, `react-intl`, `yaml`, `YamlIcon`, and `YamlModal`. `SCDetail` composes it with parameter, mount-option, and related PV cards.

## Risks and Test Signals
Only a small subset of StorageClass fields is shown here; provisioner and volume binding mode are omitted. Test classes without `allowVolumeExpansion`, no creationTimestamp, and non-JuiceFS provisioners.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/sc-basic.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/stats-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/stats-modal.tsx

## Purpose
`StatsModal` streams real-time JuiceFS mount statistics for a selected container and lets users choose schema sections.

## APIs, Control Flow, and State
The memoized component accepts namespace, pod name, `ContainerStatus`, and a render-prop trigger. It derives CE/EE behavior from `isEEImage`, tracks modal/open/start state, Monaco editor instance, auto-scroll, and schema checkboxes. `getSchema()` builds the query string for `/api/v1/ws/pod/:ns/:pod/:container/stats`. WebSocket messages are ANSI-stripped via `createAnsiStrippedMessageHandlerWithCallback`, appended to editor data, and used to decide whether auto-reveal should continue.

## Dependencies and Integration Points
It integrates with `Containers`, `useWebsocket`, Monaco, Ant Design modal controls, `isEEImage`, and the backend stats WebSocket protocol.

## Risks and Test Signals
Long streams accumulate entirely in React state. Auto-scroll depends on Monaco visible range timing. Schema defaults differ for CE and EE. Test CE/EE image tags, start/refresh/close behavior, WebSocket close, ANSI output, and manual scrolling.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/stats-modal.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/upgrade-basic.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/upgrade-basic.tsx

## Purpose
`UpgradeBasic` displays and controls a batch mount-pod upgrade job.

## APIs, Control Flow, and State
It receives an `UpgradeJob` plus `freshJob`. It fetches the targeted PVC via `usePVCWithUniqueId(upgradeJob.config.uniqueId)`, keeps a local status mirror, and conditionally renders pause, resume, stop, and delete actions. Actions call `useUpdateUpgradeJob` with `pause`, `resume`, or `stop`; delete calls `useDeleteUpgradeJob` and redirects to `/jobs`. Descriptions show node, worker parallelism, ignore-error flag, PVC link, and status badge.

## Dependencies and Integration Points
It uses job hooks, PV hook, icon components, `getUpgradeStatusBadge`, router links, and localized labels. `BatchUpgradeJobDetail` embeds it and refreshes job state after mutations.

## Risks and Test Signals
Redirect uses `window.location.href`, bypassing router navigation. Delete does not await before redirect. Test each status transition, API errors, empty `config.status`, and missing PVC resolution.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/upgrade-basic.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/upgrade-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/upgrade-modal.tsx

## Purpose
`UpgradeModal` performs an interactive smooth upgrade or binary upgrade for a single mount pod and streams progress logs.

## APIs, Control Flow, and State
It accepts namespace, pod name, `recreate`, and a render-prop trigger. When opened it fetches the latest image with `useMountPodImage`, initializes help text, and connects to `/api/v1/ws/pod/:namespace/:name/upgrade` only after Start. It sends `recreate=true|false` as query data, appends logs, and detects `POD-SUCCESS` plus a specific backend message to redirect to the recreated pod after a countdown.

## Dependencies and Integration Points
It is used by container/pod controls, depends on `useWebsocket`, Monaco, Ant Design, and backend log grammar.

## Risks and Test Signals
The success regex accepts DNS-like names but is tightly coupled to English backend output. Logs are unbounded in state. Test recreate and non-recreate flows, missing latest image, failed upgrade, close before completion, and success redirect parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/upgrade-modal.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/volumeMounts-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/volumeMounts-table.tsx

## Purpose
`VolumeMountsTable` correlates an application pod's volume mounts with PVCs, PVs, and JuiceFS mount pods.

## APIs, Control Flow, and State
It fetches mount pods, PVCs, and PVs for the given pod with `usePods`, `usePVCsOfPod`, and `usePVsOfPod`. `dataSource()` builds maps by volume mount name, PVC name, PV claimRef name, and mount pod `volume-id`, then walks `pod.spec.volumes` to create rows containing PVC, PV, volume mount, and mount pod. Rows show PVC status/link, container path, subPath, and mount pod status/link.

## Dependencies and Integration Points
It integrates with pod detail pages, hook endpoints under `/api/v1/pod/:ns/:name/*`, Kubernetes volume types, and badge/status utilities.

## Risks and Test Signals
`rowKey` uses `volumeMount?.name`, which may be empty or duplicated across containers. The PV map ignores namespace and assumes claim names are unique in the pod context. Test multi-container same volume names, CSI volumeHandle matching, storage-class fallback matching, and pods with no PVC volumes.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/volumeMounts-table.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/warmup-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/warmup-modal.tsx

## Purpose
`WarmupModal` starts and streams JuiceFS cache warmup for a mount container.

## APIs, Control Flow, and State
The memoized component tracks modal/open/start state plus warmup parameters: threads, IO retries, max failure, background, check, and subPath. It chooses CE or EE help text from `isEEImage`; EE exposes retries and max-failure controls. Start connects to `/api/v1/ws/pod/:ns/:pod/:container/warmup` with query parameters and appends ANSI-stripped output to a read-only Monaco editor.

## Dependencies and Integration Points
It is launched from container actions and depends on `useWebsocket`, Ant Design form controls, Monaco, Kubernetes `ContainerStatus`, and the backend warmup WebSocket endpoint.

## Risks and Test Signals
The component has a local ANSI stripper duplicated with `utils/ansi.ts`. `InputNumber` changes ignore `0` because of truthy checks. Long output is unbounded. Test CE/EE images, zero/negative numeric values, query serialization, close/reopen reset, and backend close.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/warmup-modal.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/xterm-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/xterm-modal.tsx

## Purpose
`XTermModal` provides an interactive terminal into a selected pod container.

## APIs, Control Flow, and State
It accepts namespace, pod name, container, and a render-prop trigger. Opening the modal connects to `/api/v1/ws/pod/:ns/:pod/:container/exec`. It creates an xterm instance, fits it on open and resize, writes incoming socket data to the terminal, sends `stdin` messages from user input, and sends `resize` messages with cols and rows.

## Dependencies and Integration Points
It depends on `xterm`, `xterm-react`, `@xterm/addon-fit`, Ant Design modal, and the shared `useWebsocket` heartbeat/base-path behavior. It is exposed from container action tables.

## Risks and Test Signals
The resize listener uses inline functions for add/remove, so removal will not unregister the original listener. `onOpen` may run before `terminal` state is set. Test open/close cycles, resizing, stdin delivery, backend close/error messages, and terminal disposal.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/xterm-modal.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/yaml-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/yaml-modal.tsx

## Purpose
`YamlModal` is a reusable Monaco-backed YAML viewer/editor used across resource detail, config, and CacheGroup flows.

## APIs, Control Flow, and State
Props include `isOpen`, `onClose`, `content`, optional `editable`, `onSave`, and `saveButtonText`. It stores edited data in local state, renders an Ant Design modal, and when editable adds a primary save button that passes the current editor data to `onSave`.

## Dependencies and Integration Points
It depends on Monaco and Ant Design. Callers stringify Kubernetes resources or YAML templates and optionally parse/update them on save.

## Risks and Test Signals
The editor value is bound to `content`, not local `data`, so external content changes dominate display while `onChange` only affects saved data. Local state is initialized once and not reset on `content` changes. Test editable saves, reopening with different content, and read-only rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/yaml-modal.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/cg-api.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/cg-api.ts

## Purpose
This file defines SWR and async hooks for CacheGroup listing, detail, worker metrics, worker membership, and CRUD operations.

## APIs, Control Flow, and State
`useCacheGroups`, `useCacheGroup`, `useWorkerCacheBytes`, `useCacheGroupWorkers`, and `useNodes` use SWR keys under `/api/v1/cachegroup(s)`. Mutating hooks wrap `apiFetch` with `useAsync`: `useRemoveWorker`, `useAddWorker`, `useCreateCacheGroup`, `useUpdateCacheGroup`, and `useDeleteCacheGroup`, sending JSON bodies or DELETE requests.

## Dependencies and Integration Points
The hooks support `cg-list`, `cg-detail`, worker tables, and YAML edit/create workflows. Types come from `CacheGroup`, Kubernetes `Pod`/`Node`, and pagination args.

## Risks and Test Signals
Hooks interpolate optional namespace/name into URLs even when undefined. Worker list query values may become `undefined`. Test create/update/delete error propagation, worker pagination filters, refresh intervals, and empty parameter cases.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/cg-api.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/cm-api.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/cm-api.ts

## Purpose
This file provides hooks for the CSI dashboard configuration ConfigMap and related PVC impact analysis.

## APIs, Control Flow, and State
`useConfig` fetches `/api/v1/config`, `useConfigPVC` fetches PVC matches for config patches, `useConfigPVCSelector` posts a candidate ConfigMap to `/api/v1/config/pvcs/selector`, `useUpdateConfig` PUTs the ConfigMap, and `useConfigDiff` queries diff pods with node, uniqueId, pageSize, and current parameters.

## Dependencies and Integration Points
Config pages and update confirmation modals use these hooks to edit `config.yaml`, preview affected PVCs/pods, and decide whether batch upgrade should be offered.

## Risks and Test Signals
`useConfigDiff('', '')` produces empty query filters by design. Query strings are not URL-encoded. Test invalid YAML update errors, selector preview, All Nodes behavior, pagination defaults, and diff refresh after config saves.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/cm-api.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/job-api.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/job-api.ts

## Purpose
This hook module encapsulates batch mount-pod upgrade job creation, listing, detail, deletion, and control actions.

## APIs, Control Flow, and State
`useCreateUpgradeJob` POSTs `/api/v1/batch/upgrade/jobs` with jobName, normalized nodeName, recreate=true, worker count, ignoreError, and uniqueId, returning the created job name. `useUpgradeJob` fetches one job. `useUpgradeJobs` builds paginated/sorted list query parameters. `useDeleteUpgradeJob` DELETEs one job. `useUpdateUpgradeJob` PUTs an action such as pause, resume, or stop.

## Dependencies and Integration Points
Used by batch job list, detail, creation modal, and `UpgradeBasic`. Types are `UpgradeJob`, `UpgradeJobWithDiff`, and list args.

## Risks and Test Signals
`All Nodes` is a UI sentinel converted to empty string. Query values are unencoded and status action strings are unchecked. Test create payload variants, pagination continue tokens, delete/update failures, and list sorting.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/job-api.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/pv-api.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/pv-api.ts

## Purpose
This module defines storage-resource hooks for StorageClasses, PVs, PVCs, PVC unique IDs, basic PVC info, and storage events.

## APIs, Control Flow, and State
List hooks build SWR URLs with sort, filter, page, and Kubernetes continue parameters: `/api/v1/storageclasses`, `/api/v1/pvs`, and `/api/v1/pvcs`. Detail hooks fetch `/api/v1/storageclass/:name/`, `/api/v1/pv/:name/`, `/api/v1/pvc/:namespace/:name/`, and related PVs/events. Unique-ID helpers resolve PVCs by namespaced name or unique ID.

## Dependencies and Integration Points
Storage list/detail pages, `PVsTable`, upgrade job basic info, and config/job workflows depend on these hooks.

## Risks and Test Signals
Some hooks emit URLs with undefined path segments; `usePVC` guards with an empty SWR key only when name is missing. `usePVCEvents` names its argument `pvName`. Test empty params, continue pagination, storage class filtering, unique-ID split edge cases, and event fetching.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/pv-api.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/use-api.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/use-api.ts

## Purpose
This file provides general pod, node, WebSocket, and download hooks for the dashboard.

## APIs, Control Flow, and State
`useAppPods` and `useSysAppPods` build paginated/sorted pod list SWR URLs. Detail and relationship hooks fetch pod, event, mount pod, CSI node, PV, PVC, and node data. `useWebsocket` wraps `react-use-websocket`, computes `ws`/`wss`, uses `VITE_HOST` or current host plus `getBasePath`, adds a ping heartbeat, filters `pong`, and forwards other messages. Download hooks fetch blobs and create temporary anchor downloads for logs/debug ZIPs.

## Dependencies and Integration Points
Nearly all pod pages and modals use this layer. It depends on `apiFetchBlob`, `getBasePath`, Kubernetes types, SWR, `useAsync`, and `react-use-websocket`.

## Risks and Test Signals
WebSocket URLs are built even when `uri` is undefined, relying on `shouldConnect`. Downloads create browser object URLs. Test hosted subpath deployments, HTTPS, VITE_HOST override, heartbeat handling, blob errors, and SWR keys with optional params.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/use-api.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/use-version.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/use-version.ts

## Purpose
`use-version.ts` exposes backend build/version data and the dashboard feature flag for graceful upgrade.

## APIs, Control Flow, and State
`VersionInfo` contains driverVersion, gitCommit, buildDate, goVersion, compiler, platform, and `disableGraceUpgrade`. `useVersion` fetches `/api/v1/version` with SWR, refreshes every five minutes, and disables focus revalidation.

## Dependencies and Integration Points
Batch upgrade list, config apply controls, pod/container action buttons, and smooth-upgrade gating use this hook.

## Risks and Test Signals
Feature controls depend on a timely version response; until loaded, some UI may appear enabled. Test disabled graceful-upgrade behavior, backend errors, and cache refresh.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/hooks/use-version.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/icons/index.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/icons/index.tsx

## Purpose
This module centralizes custom dashboard icons for resource navigation and actions.

## APIs, Control Flow, and State
It imports Ant Design `Icon`, image assets for common Kubernetes resources, and defines React wrapper components such as `DSIcon`, `PODIcon`, `PVIcon`, `PVCIcon`, `SCIcon`, `CMIcon`, and `LOGOIcon`. It also defines inline SVG icons for locale, terminal, logs, access logs, YAML, debug, warmup, stats, upgrade, gather, resources, diff, delete, pause, resume, and stop. All are exported as named components accepting partial Ant Design icon props.

## Dependencies and Integration Points
Components throughout the dashboard import these icons for buttons, menus, and toolbars. The path alias `@/assets/*` depends on Vite/tsconfig aliasing.

## Risks and Test Signals
Inline SVGs are large and untyped beyond icon props; image icons use `width` but not alt text. Test asset bundling, tree-shaking, button rendering at different sizes, and missing asset paths.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/icons/index.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/locales/en-US.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/locales/en-US.ts

## Purpose
This file is the English message catalog for dashboard internationalization.

## APIs, Control Flow, and State
It exports a default object mapping message IDs to English strings for resource table labels, pod/PV/PVC failure diagnostics, config editing, batch upgrade workflows, CacheGroup management, YAML display, diagnosis, warmup, and smooth-upgrade disabled messaging. There is no runtime state.

## Dependencies and Integration Points
`FormattedMessage` usages across components reference these IDs. The catalog must stay aligned with the Chinese catalog and any route/page additions.

## Risks and Test Signals
Missing keys render fallback IDs in UI. Some strings include operational guidance and must match current CSI behavior. Test locale switching, search for `FormattedMessage id=` keys missing in this file, and verify diagnostics against utility return values.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/locales/en-US.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/locales/zh-CN.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/locales/zh-CN.ts

## Purpose
This file is the Simplified Chinese message catalog for the dashboard.

## APIs, Control Flow, and State
It exports a default object keyed by the same message IDs used by the UI. It covers table labels, resource states, diagnostic explanations, config editing, batch upgrade, CacheGroup, YAML, diagnosis, and smooth-upgrade disabling. It contains no executable control flow.

## Dependencies and Integration Points
The application locale provider consumes this object when Chinese is selected. Utility functions return message IDs that must exist here.

## Risks and Test Signals
Catalog drift with `en-US.ts` can leave untranslated or missing keys. One key uses `batch` while English uses `stage`, so key parity should be checked. Test all `FormattedMessage` references and language toggle rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/locales/zh-CN.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/main.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/main.tsx

## Purpose
`main.tsx` is the Vite React entry point for the dashboard UI.

## APIs, Control Flow, and State
It imports React, ReactDOM, `App`, and global CSS, then mounts `<App />` into `document.getElementById('root')!` under `React.StrictMode`. It has no persistence or custom state.

## Dependencies and Integration Points
The file depends on the HTML root element supplied by Vite and all top-level providers/routes configured in `App.tsx`.

## Risks and Test Signals
StrictMode can double-invoke effects in development, which matters for WebSocket hooks and fetch side effects during local testing. Test production build boot, root element existence, and dev mode modal/WebSocket behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/main.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/app-pod-list.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/app-pod-list.tsx

## Purpose
`PodList` renders the paginated searchable table of application pods that use JuiceFS CSI.

## APIs, Control Flow, and State
It defines columns for pod name, namespace, PVs, mount pods, status, CSI node, and creation time. Failure badges call `failedReasonOfAppPod`; status uses `podStatus` and `getPodStatusBadge`. Component state tracks pagination, continue token, filters, and sorter. `getSortBy` maps table keys to backend sort fields. `useAppPods` fetches `/api/v1/pods` with current state, and the Next button advances Kubernetes continue pagination.

## Dependencies and Integration Points
It links to pod, PV, and system pod detail routes and depends on pod relationship data returned by the backend.

## Risks and Test Signals
Server-side continue tokens are modeled separately from ProTable pagination. Search form values are flattened from nested metadata. Test sorting by name/CSI node/time, filtering, continue token paging, multi-PV/multi-mount-pod rows, and failure reason tooltips.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/app-pod-list.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/batch-job-list.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/batch-job-list.tsx

## Purpose
`UpgradeJobList` lists batch upgrade jobs and opens the creation modal.

## APIs, Control Flow, and State
It reads `modalOpen` from search params, tracks pagination, filter, continue token, and modal visibility, fetches jobs with `useUpgradeJobs`, and fetches version data to disable graceful upgrade creation. Columns show job name, status badge, and creation time. Successful creation closes the modal and mutates the job list.

## Dependencies and Integration Points
It integrates with `BatchUpgradeModal`, `useVersion`, `useUpgradeJobs`, route `/jobs/:namespace/:name`, and localized text.

## Risks and Test Signals
The create button is initially enabled until version data says otherwise. Continue-token paging coexists with current/pageSize. Test disabled graceful-upgrade mode, `?modalOpen=true`, list mutation after create, and status display for empty config status.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/batch-job-list.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/batch-upgrade-job-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/batch-upgrade-job-detail.tsx

## Purpose
`BatchUpgradeJobDetail` shows one batch upgrade job, streams its logs, and visualizes per-pod progress.

## APIs, Control Flow, and State
It fetches `UpgradeJobWithDiff` with `useUpgradeJob`, derives total pods, per-pod status map, job status, TTL deletion countdown, and progress percent from `config.batches`. It opens a log WebSocket at `/api/v1/ws/batch/upgrade/jobs/:jobName/logs`, appends logs, parses `POD-START`, `POD-SUCCESS`, and `POD-FAIL` messages into status and fail-reason maps, and refreshes job data on close. The UI composes `UpgradeBasic`, progress, `PodUpgradeTable`, and a Monaco log collapse.

## Dependencies and Integration Points
It depends on job API hooks, `useWebsocket`, upgrade components, backend log grammar, and `timeToBeDeletedOfJob`.

## Risks and Test Signals
`calculatePercent` can use stale `diffStatus` immediately after `setDiffStatus`. Regexes accept only DNS-like pod names. Test live status parsing, completed jobs with no logs, failed pods, TTL display, and WebSocket reconnect/close.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/batch-upgrade-job-detail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/cg-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/cg-detail.tsx

## Purpose
`CgDetail` displays one JuiceFS CacheGroup and lets users edit or delete it.

## APIs, Control Flow, and State
It fetches a CacheGroup with `useCacheGroup`, tracks YAML modal visibility and worker auto-refresh, and renders namespace, phase, expected/ready workers, and cache group status. Editable YAML omits `metadata.managedFields`, saves through `useUpdateCacheGroup`, shows success/error messages, mutates the SWR cache, and enables worker auto-refresh. Delete calls `useDeleteCacheGroup` then navigates to `/cachegroups`.

## Dependencies and Integration Points
It composes `YamlModal`, `CgWorkersTable`, CacheGroup hooks, Ant Design notifications, `YAML.parse/stringify`, and router navigation.

## Risks and Test Signals
The update hook returns parsed JSON from `apiFetch`, but this component casts it to `Response` and checks `resp.status`, which may not work with the utility contract. Test YAML update success/failure, delete failure JSON parsing, and worker refresh after update.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/cg-detail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/cg-list.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/cg-list.tsx

## Purpose
`CgList` lists CacheGroups and provides a YAML template flow to create one.

## APIs, Control Flow, and State
It fetches CacheGroups with `useCacheGroups`, defines columns for name, filesystem, phase, ready string, and creation time, and uses an editable `YamlModal` seeded with a default CacheGroup manifest. Saving parses YAML and calls `useCreateCacheGroup`, then mutates the list and closes the modal.

## Dependencies and Integration Points
It uses CacheGroup API hooks, Ant Design Pro table, `react-intl`, YAML parsing, and routes to `/cachegroups/:namespace/:name`.

## Risks and Test Signals
The template includes an EE mount image and host networking defaults that may not suit all clusters. Creation errors assume JSON-formatted error messages. Test malformed YAML, API validation errors, empty list, and successful mutate after create.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/cg-list.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-detail.tsx

## Purpose
`ConfigDetail` is the main configuration editor for the CSI driver's dashboard ConfigMap.

## APIs, Control Flow, and State
It fetches config, matched PVCs, global config diff, and version data. It stores normalized YAML text, edit mode, active tab, update flag, diff flag, errors, and confirmation modal state. Effects parse `data.data['config.yaml']`, show YAML errors via notification, update diff state, and refresh config/diff when not locally updated. It renders Detail and YAML tabs, edit/reset/save controls, docs link, and Apply navigation to `/jobs?modalOpen=true` when config changes require mount pod upgrades and graceful upgrade is enabled.

## Dependencies and Integration Points
It composes `ConfigTablePage`, `ConfigYamlPage`, `ConfigUpdateConfirmModal`, config hooks, version hook, router navigation, and JuiceFS docs URL.

## Risks and Test Signals
The save disabled comparison stringifies strings rather than parsed objects. `updated` controls refresh suppression and must be reset carefully. Test missing ConfigMap, invalid YAML, tab switching, save confirmation, diff apply disabled states, and version-disabled upgrades.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-detail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-table-page.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-table-page.tsx

## Purpose
`ConfigTablePage` presents `config.yaml` mount-pod patches as structured forms or read-only detail panels.

## APIs, Control Flow, and State
It parses `configData` into `OriginConfig`, converts it to UI `Config` via `ToConfig`, stores it, and pushes form values into a ProForm ref. In edit mode, `ProFormList` renders collapsible `MountPodPatchForm` entries and converts all values back to YAML with `ToOriginConfig` on every change. In read-only mode it maps patches to `MountPodPatchDetail`. `PvcPop` shows a popover of PVCs matched by each patch.

## Dependencies and Integration Points
It depends on config conversion types, YAML, Ant Design Pro forms, patch form/detail components, and matched PVC data from `useConfigPVC`.

## Risks and Test Signals
Parsing happens whenever `configData` or `edit` changes; invalid YAML only reports via `setError`. Form changes rewrite YAML order/shape. Test round-trip conversion, adding/removing patches, PVC popovers, invalid config text, and read-only rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-table-page.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-yaml-page.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-yaml-page.tsx

## Purpose
`ConfigYamlPage` is the raw YAML editor tab for CSI driver configuration.

## APIs, Control Flow, and State
It receives YAML text, edit flag, and setters from `ConfigDetail`. It renders a Monaco YAML editor with read-only mode when not editing. On change, non-empty values update parent config data, mark the config updated, and clear errors.

## Dependencies and Integration Points
It is one of the two tabs in `ConfigDetail`, sharing state with the structured table editor and save confirmation flow.

## Risks and Test Signals
Empty editor contents do not propagate because `if (v)` skips empty strings. Syntax validation is deferred to save or table parsing. Test read-only cursor behavior, empty YAML edits, invalid YAML, and switching between YAML and table tabs.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/config-yaml-page.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pod-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pod-detail.tsx

## Purpose
`PodDetail` renders a full detail view for an application pod or system pod.

## APIs, Control Flow, and State
It fetches pod data with `useAppPod(namespace, name)` and returns a localized not-found `PageContainer` for missing params/data. The detail page composes `PodBasic`, `Containers` with combined regular and init container statuses via `lodash/union`, app pod relationship table, `VolumeMountsTable`, CSI node pod table, and events.

## Dependencies and Integration Points
It depends on components from the shared components index, `VolumeMountsTable`, and pod API hooks. Route dispatch passes both app and system pod resources here.

## Risks and Test Signals
`union` on status objects compares by reference and may not deduplicate semantically. The same `useAppPod` endpoint is used for syspods. Test missing pods, init containers, sidecar pods, mount pod relationships, and event loading.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pod-detail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pv-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pv-detail.tsx

## Purpose
`PVDetail` composes the PersistentVolume detail screen.

## APIs, Control Flow, and State
It accepts a PV name, fetches the PV with `usePV(name)`, returns `null` until data exists, then renders a fixed-header `PageContainer` with `PVBasic`, related mount pods via `PodsTable`, and PV events through `EventTable`.

## Dependencies and Integration Points
It integrates PV API hooks, storage basic component, shared relationship/event tables, and route `/pvs/:name`.

## Risks and Test Signals
There is no explicit not-found page; missing data renders nothing. Test loading, nonexistent PVs, related mount pods, event endpoint behavior, and PVs without CSI fields.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pv-detail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pv-list.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pv-list.tsx

## Purpose
`PVList` renders the searchable, paginated PersistentVolume table.

## APIs, Control Flow, and State
Columns show PV name with failure tooltip, claimRef link, capacity, access modes, reclaim policy, StorageClass link, phase badge, and creation time. State tracks pagination, filters, sorter, and continue token. It calls `usePVs` with table state and updates pagination totals and continue token from SWR data.

## Dependencies and Integration Points
It depends on PV hooks, `failedReasonOfPV`, status badge utilities, router links, ProTable, and localized labels.

## Risks and Test Signals
Search value flattening assumes `values.spec.claimRef.name` exists when spec is present; optional chaining is incomplete for claimRef. Test filters for name/PVC/SC, unbound PVs, continue token Next, sort resets, and failure reason messages.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pv-list.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pvc-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pvc-detail.tsx

## Purpose
`PVCDetail` composes the PersistentVolumeClaim detail screen.

## APIs, Control Flow, and State
It accepts namespace and name, fetches the PVC with `usePVC(namespace, name)`, returns `null` until data exists, then renders `PVCBasic`, related mount pods via `PodsTable`, and PVC events.

## Dependencies and Integration Points
It depends on PVC hooks and shared detail components. Routes point to `/pvcs/:namespace/:name`.

## Risks and Test Signals
Like `PVDetail`, nonexistent resources produce a blank area rather than a not-found message. Test missing PVCs, bound and pending PVCs, related mount pods, and event namespace/name URL building.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pvc-detail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pvc-list.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pvc-list.tsx

## Purpose
`PVCList` renders the searchable, paginated PersistentVolumeClaim table.

## APIs, Control Flow, and State
Columns show PVC name with failure tooltip, namespace, PV link, requested storage, access modes, StorageClass link, phase badge, and creation time. Component state tracks pagination, flattened filters, sorter, and continue token. It calls `usePVCs` and updates total/continue state from results.

## Dependencies and Integration Points
It depends on PVC hooks, `failedReasonOfPVC`, `getPVCStatusBadge`, ProTable, router links, and localization.

## Risks and Test Signals
The name column has a required form rule even though searches should allow partial/empty filters. Creation time uses `toLocaleDateString` with time options, unlike other pages. Test filtering, no storage class, unbound PVC diagnostics, continue pagination, and sort defaults.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/pvc-list.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sc-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sc-detail.tsx

## Purpose
`SCDetail` renders a StorageClass detail page.

## APIs, Control Flow, and State
It fetches the StorageClass with `useSC(name)`, shows a localized not-found header when name/data is absent, and otherwise renders `SCBasic`, parameter and mount-option lists, and related PVs through `PVsTable`. A local `ConfigProvider` sets Ant Design token overrides for this page subtree.

## Dependencies and Integration Points
It integrates storage hooks, `SCBasic`, `scParameter`, and PV relationship table with route `/storageclass/:name`.

## Risks and Test Signals
The not-found localization ID in code is `StorageClassNotFound`, while catalogs define `scNotFound`. Test missing classes, empty parameters/mount options, theme overrides, and related PV loading.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sc-detail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sc-list.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sc-list.tsx

## Purpose
`ScList` renders the StorageClass list page.

## APIs, Control Flow, and State
It defines columns for name, reclaim policy, allow volume expansion, and creation time. State tracks pagination, name filter, and time sorter. `useSCs` fetches `/api/v1/storageclasses` with current pagination, name, and sort. Form changes update the name filter; table changes update pagination and sorter.

## Dependencies and Integration Points
It uses StorageClass types, `useSCs`, ProTable, router links, and localized labels.

## Risks and Test Signals
Pagination is always enabled even if no total is returned. Name filter does not reset current page. Test empty lists, missing creationTimestamp, boolean rendering, name search, and sorting.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sc-list.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sys-pod-list.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sys-pod-list.tsx

## Purpose
`SysPodList` renders system pods related to JuiceFS CSI, such as mount pods, CSI driver pods, and cache group workers.

## APIs, Control Flow, and State
Columns show name with mount-pod failure tooltip, namespace, computed pod status, creation time, and node readiness badge. `getSortBy` maps table keys to backend sort fields. State tracks pagination, filters, sorter, and continue token. `useSysAppPods` fetches `/api/v1/syspods` with node/name/namespace filters.

## Dependencies and Integration Points
It depends on pod API hooks, `failedReasonOfMountPod`, node/pod badge utilities, router links to `/syspods/:namespace/:name`, and localized labels.

## Risks and Test Signals
Filter flattening accepts both `values.node` and `values.spec?.nodeName`. Continue pagination and table page numbers can diverge. Test node sorting, missing node objects, terminating mount pods, continue tokens, and failure tooltips.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/pages/sys-pod-list.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/config.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/config.ts

## Purpose
This file defines UI-friendly configuration types and conversion functions between the dashboard form model and the backend/original `config.yaml` model.

## APIs, Control Flow, and State
Types include `Config`, `mountPodPatch`, `pvcSelector`, `MountPatch`, resource and key/value helpers. `ToConfig` converts maps to arrays, mount options to key/value rows, env vars to rows with `valueType`, PVC selectors to form shape, and resources to cpu/memory strings. `ToOriginConfig` performs the reverse, omitting empty structures and removing env `value` or `valueFrom` based on `valueType`.

## Dependencies and Integration Points
`ConfigTablePage`, patch form/detail components, and config update flows rely on these conversions. Types import Kubernetes probes, lifecycle, volumes, env vars, quantities, and selector requirements.

## Risks and Test Signals
Round-trip conversion can drop empty values and reorder maps. `convertPVCSelector` uses a mutable `noMatch` flag that can be overwritten by later empty fields. Test map/list/env/resource round trips, selector combinations, empty patches, and cacheDirs handling.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/config.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/index.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/index.ts

## Purpose
This file defines shared route parameter and pagination/filter argument types for dashboard list hooks and route dispatchers.

## APIs, Control Flow, and State
`Params` enumerates supported resource route keys. `DetailParams` adds namespace and name. Paging interfaces define optional pageSize/current, filters, sort maps, and Kubernetes continue tokens for app pods, system pods, StorageClasses, PVs, PVCs, CacheGroup workers, and upgrade jobs.

## Dependencies and Integration Points
Route dispatch components and hook modules use these types to keep URL params and query-building inputs consistent.

## Risks and Test Signals
Route keys must stay aligned with router declarations, `ResourcesList`, `ResourcesDetail`, and `getBasePath`. Test TypeScript compilation after adding resources and verify sort keys accepted by backend.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/index.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/k8s.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/k8s.ts

## Purpose
This file extends Kubernetes TypeScript models with dashboard-specific JuiceFS relationships and configuration/job types.

## APIs, Control Flow, and State
It defines enriched `Pod`, `PV`, `PVC`, unique-ID PVC types, `accessModeMap`, batch upgrade config/status models, config diff models, original config and mount patch shapes, cache directory/cache volume settings, CacheGroup templates and status, and upgrade job wrappers.

## Dependencies and Integration Points
Components, hooks, config conversion, batch upgrade pages, CacheGroup pages, and pod/storage tables all import these contracts. It depends on `kubernetes-types` API models.

## Risks and Test Signals
Several fields use backend-specific casing such as `PVC`, `PV`, `UniqueId`, `HostnameKey`, and `InitContainers`; these must match API JSON exactly. Test API contract decoding, optional field handling, and TypeScript strictness when backend models evolve.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/types/k8s.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/utils/ansi.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/utils/ansi.ts

## Purpose
This utility strips ANSI terminal sequences from streamed WebSocket output and provides a reusable React state append handler.

## APIs, Control Flow, and State
`removeAnsiSequences(text)` applies a control-sequence regex. `createAnsiStrippedMessageHandlerWithCallback(setData, callback)` returns an `onMessage` handler that strips `msg.data`, appends it to a React string state, and invokes an optional callback with the cleaned data.

## Dependencies and Integration Points
`StatsModal` uses this shared handler. Similar logic exists locally in `WarmupModal`, which could be consolidated.

## Risks and Test Signals
The regex covers common CSI-style ANSI escape sequences but not every terminal control form. Test colored output, cursor control, plain text, binary/unicode output, and callback invocation order.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/utils/ansi.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/utils/index.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/utils/index.ts

## Purpose
This file holds dashboard utility logic for status badges, failure diagnostics, pod status calculation, API base URL construction, fetch wrappers, image capability checks, upgrade status, and TTL formatting.

## APIs, Control Flow, and State
Status helpers map Node/PV/PVC/pod/job states to Ant Design colors/statuses. Diagnostic helpers inspect PVC/PV phases, pod readiness, scheduling, node readiness, CSI node and mount pod health, sidecar labels, deletion timestamps, finalizers, and container statuses to return localization IDs. `podStatus` mirrors kubectl pod status logic for init containers, waiting/terminated states, deletion, and NodeLost. `getBasePath` detects subpath hosting, `getHost` uses `VITE_HOST`, and `apiFetch`/`apiFetchBlob` wrap fetch error handling. Image helpers parse CE/EE tags and compare versions for smooth upgrade/debug support.

## Dependencies and Integration Points
Almost every page imports this module for badges, failure tooltips, API calls, or feature gating. Hooks use fetch wrappers; modals use version/image helpers.

## Risks and Test Signals
Some readiness logic assumes both Ready and ContainersReady must be true. Terminating helpers compare `node.status?.phase` to `Ready`, which is not a standard Node phase. Query/base-path logic must match deployment paths. Test kubectl-like pod statuses, failure message IDs, version parsing for latest/dev/nightly, fetch 204 handling, and subpath hosting.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/utils/index.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/vite-env.d.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/vite-env.d.ts

## Purpose
This declaration file extends Vite client typings with dashboard-specific environment variables.

## APIs, Control Flow, and State
It references `vite/client` and declares `ImportMetaEnv.VITE_HOST` as a readonly string, plus `ImportMeta.env`. There is no runtime output.

## Dependencies and Integration Points
`getHost` and `useWebsocket` read `import.meta.env.VITE_HOST` to override the API/WebSocket host.

## Risks and Test Signals
`VITE_HOST` is typed as always present even though runtime code treats it as optional. Test TypeScript compilation and builds with and without the variable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/vite-env.d.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/tsconfig.json -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/tsconfig.json

## Purpose
This TypeScript config defines the browser app compilation contract for the Vite React dashboard.

## APIs, Control Flow, and State
It targets ES2020 with DOM libs, ESNext modules, bundler resolution, JSON modules, isolated modules, no emit, React JSX transform, strict checks, unused checks, fallthrough checks, and `@/*` alias to `./src/*`. It includes `src`, excludes `node_modules`, and references `tsconfig.node.json`.

## Dependencies and Integration Points
Vite, editor tooling, and type checking depend on this config. The alias must match `vite.config.ts`.

## Risks and Test Signals
`allowImportingTsExtensions` supports existing `.ts`/`.tsx` import suffixes but may affect portability. Test `tsc -b`, Vite build, path alias resolution, and strict unused parameter/local failures.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/tsconfig.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/tsconfig.node.json -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/tsconfig.node.json

## Purpose
This TypeScript config covers Node-side tooling code, currently Vite configuration.

## APIs, Control Flow, and State
It enables composite project output metadata, skips library checks, uses ESNext modules with bundler resolution, allows synthetic default imports, enables strict mode, and includes only `vite.config.ts`.

## Dependencies and Integration Points
It is referenced from the main tsconfig and supports `tsc -b` checking of Vite config.

## Risks and Test Signals
Because the include set is narrow, any additional Node scripts need explicit inclusion or another config. Test project references and Vite config type checking.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/tsconfig.node.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/vite.config.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/vite.config.ts

## Purpose
This file configures Vite for the React dashboard development server and production build.

## APIs, Control Flow, and State
`defineConfig` enables the React plugin, relative `base: './'`, `@` alias to `src`, dev-server proxies for `/api` HTTP and `/api/v1/ws` WebSocket traffic to localhost:8088, and a production build target list. Build output config uses `rolldownOptions.output.codeSplitting.groups` to group `antd` and `@ant-design` dependencies.

## Dependencies and Integration Points
It must align with tsconfig paths, dashboard backend port, static hosting under the CSI dashboard image, and Vite/Rolldown version support.

## Risks and Test Signals
`rolldownOptions` is version-sensitive; older Vite versions may not accept it. Relative base supports embedded static serving but can affect router refreshes. Test `npm run dev`, WebSocket proxying, production build, and serving assets from subpaths.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/vite.config.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/k8s.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/k8s.yaml

## Purpose
This generated manifest installs the JuiceFS CSI driver, dashboard, RBAC, default config, controller, node daemon, and CSIDriver object into `kube-system`.

## APIs, Control Flow, and State
It creates service accounts for controller, dashboard, and node components; ClusterRoles and bindings for dashboard reads/exec/jobs/config, node service operations, external provisioner, and snapshotter; a `juicefs-csi-driver-config` ConfigMap with `enableNodeSelector: false`; a dashboard Service and Deployment on port 8088; a controller StatefulSet with `juicefs-plugin`, `csi-provisioner`, `csi-resizer`, and liveness sidecar; a node DaemonSet with `juicefs-plugin`, registrar, and liveness sidecar; and a `storage.k8s.io/v1` CSIDriver named `csi.juicefs.com`.

## Dependencies and Integration Points
Images include `juicedata/csi-dashboard:v0.31.3`, `juicedata/juicefs-csi-driver:v0.31.3`, and Kubernetes CSI sidecars. HostPaths include kubelet plugin directories, `/var/lib/juicefs/volume`, `/var/lib/juicefs/config`, `/dev`, and `/var/run/juicefs-csi`. Dashboard RBAC backs the UI API actions researched in this subset.

## Risks and Test Signals
The manifest grants broad cluster permissions, privileged containers, SYS_ADMIN, hostPath mounts, and bidirectional mount propagation. It assumes kubelet paths and plugin registry layout. Test with `kubectl apply --dry-run=server`, RBAC `can-i`, controller leader election, PVC provision/resize, node registration, dashboard API access, and health probes.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/k8s.yaml -->
