# Research: subset-b-000388

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/node.go -->
# sources/control-plane/juicefs-csi-driver/cmd/node.go

## Purpose
`node.go` starts the JuiceFS CSI node service. It converts process flags and pod environment into `pkg/config` globals, starts pprof and Prometheus endpoints, optionally starts pod reconciliation, initializes graceful-upgrade file descriptor passing, and runs the CSI driver.

## Important APIs, Types, and Functions
The main entry points are `parseNodeConfig()` and `nodeRun(ctx)`. `parseNodeConfig` consumes environment variables such as `DRIVER_NAME`, `JUICEFS_IMMUTABLE`, `NODE_NAME`, `JUICEFS_MOUNT_NAMESPACE`, `POD_NAME`, mount image overrides, share-mount toggles, reconcile intervals, and `DISABLE_GRACE_UPGRADE`. It calls `k8s.NewClient()`, `GetPod`, `passfd.InitGlobalFds`, and `grace.ServeGfShutdown`. `nodeRun` registers Go metrics, creates `driver.NewDriver`, and calls `drv.Run()`.

## Control Flow, State, and Persistence
Configuration is stored by mutating package-level `config` variables. In process mode it exits early and avoids pod lookup. Otherwise it validates pod identity, reads the current CSI pod from Kubernetes, and starts graceful shutdown socket serving unless disabled. Runtime state is mostly in goroutines: pprof binds localhost from port 6060 upward, metrics binds `config.WebPort`, pod manager/reconciler may run in the background, and context cancellation stops the driver.

## Dependencies and Integration Points
This file connects CLI globals from the main package to Kubernetes clients, controller reconciliation, CSI driver construction, Prometheus, pprof, passfd/graceful upgrade, and image resolution utilities. It is deployment-sensitive because many behaviors are environment-driven by the node DaemonSet.

## Risks and Test Signals
Risks include fatal exits on missing pod metadata, ignored parse errors for duration values, unbounded pprof port retry loops, metrics bind conflicts, global mutable config, and graceful-upgrade socket startup failures blocking the node. Test signals are env-matrix unit tests around `parseNodeConfig`, node startup with and without kubelet access, metrics endpoint availability, graceful upgrade socket behavior, and integration tests that verify driver shutdown on context cancellation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/upgrade.go -->
# sources/control-plane/juicefs-csi-driver/cmd/upgrade.go

## Purpose
`upgrade.go` defines the `upgrade` Cobra command used to trigger smooth mount-pod upgrades through the node-side graceful shutdown socket.

## Important APIs, Types, and Functions
The file declares global command flags `recreate`, `batchConfigName`, and `crtBatchIndex`, plus `upgradeCmd`. The command checks `DISABLE_GRACE_UPGRADE`, validates an argument, and calls either `grace.TriggerBatchUpgrade(config.ShutdownSockPath, batchConfigName, crtBatchIndex)` for the sentinel pod name `BATCH`, or `grace.TriggerShutdown(config.ShutdownSockPath, name, recreate)` for a single mount pod. `init()` binds `--recreate`, `--batchConfig`, and `--batchIndex`.

## Control Flow, State, and Persistence
The command is synchronous and process-scoped. It derives behavior from environment, CLI args, and flags, then exits nonzero on disabled mode, missing target, or grace API error. Persistent effects are external: the grace socket recipient initiates mount pod shutdown/recreate or batch progress, while this command only reports success/failure.

## Dependencies and Integration Points
It integrates the CLI layer with `pkg/fuse/grace` and shared `pkg/config`. It must match the socket path served by the node process in `node.go` and the batch upgrade job logic that passes `BATCH`, config name, and batch index.

## Risks and Test Signals
Risks include the magic `BATCH` argument, absence of flag validation for batch config/index, reliance on shared socket path defaults, and hard process exits that complicate unit testing. Useful tests cover disabled grace mode, missing args, single-pod recreate/non-recreate calls, batch calls, and socket error propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/upgrade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/eslint.config.cjs -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/eslint.config.cjs

## Purpose
This CommonJS flat ESLint configuration defines linting for the Vite/React/TypeScript dashboard application.

## Important APIs, Types, and Functions
It uses `defineConfig` and `globalIgnores` from `eslint/config`, `FlatCompat` from `@eslint/eslintrc`, `fixupConfigRules` from `@eslint/compat`, `@typescript-eslint/parser`, `eslint-plugin-react-refresh`, `eslint-plugin-react-hooks`, `@eslint/js`, and `globals.browser`. It extends recommended ESLint, TypeScript, and React Hooks presets, enables `react-refresh/only-export-components`, and disables `react-hooks/set-state-in-effect`.

## Control Flow, State, and Persistence
The module exports a static config array. `FlatCompat` translates legacy `extends` entries into flat config entries. The ignore block excludes `dist` and the config file itself. There is no runtime persistence; the file affects lint command behavior and editor integrations.

## Dependencies and Integration Points
It is invoked by `pnpm lint` from `package.json`. Because the application package has `"type": "module"`, the `.cjs` extension is important for `require`-style config loading.

## Risks and Test Signals
Risks include version skew between ESLint 10 flat config and compatibility wrappers, linting all JS/TS files with the TypeScript parser without project-aware type checking, and hiding hook set-state-in-effect warnings. Signals are `pnpm lint` success, expected React Refresh warnings, and no accidental linting of build output.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/eslint.config.cjs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/package.json -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/package.json

## Purpose
`package.json` defines the dashboard UI package metadata, runtime engine constraints, scripts, and dependency graph for the React/Vite dashboard.

## Important APIs, Types, and Functions
Scripts are `dev` (`vite`), `build` (`tsc && vite build`), `lint`, `preview`, and `format`. Runtime dependencies include Ant Design, Pro Components, Monaco, xterm, React 18, React Router, SWR, websocket hooks, YAML, Kubernetes types, and react-intl. Dev dependencies include ESLint 10 flat-config tooling, TypeScript 5.9, Vite 8, React plugin, Prettier import sorting, and type packages.

## Control Flow, State, and Persistence
There is no application control flow in this manifest, but it controls package-manager resolution, script entry points, Node compatibility (`^20.19.0 || >=22.12.0`), and ESM semantics through `"type": "module"`. Lockfile state in `pnpm-lock.yaml` pins actual transitive versions.

## Dependencies and Integration Points
The dependencies mirror UI features: Ant Design tables/forms/modals, Monaco editors for logs/YAML/debug output, xterm for exec sessions, SWR/fetch hooks for API calls, React Router routes, and Kubernetes type definitions. The build script integrates TypeScript checks before Vite bundling.

## Risks and Test Signals
Risks include broad caret ranges, lockfile-resolved React 18.3.1 versus `^18.2.0`, modern Node requirements, and a frontend test gap because only lint/build scripts are declared. Signals are `pnpm install --frozen-lockfile`, `pnpm lint`, `pnpm build`, and manual route/API smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/package.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/pnpm-lock.yaml -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/pnpm-lock.yaml

## Purpose
`pnpm-lock.yaml` is the deterministic dependency resolution for the dashboard UI package. It pins direct and transitive package versions, peer dependency resolutions, integrity hashes, engines, optional native packages, and package snapshots.

## Important APIs, Types, and Functions
The lockfile uses `lockfileVersion: '9.0'` with `autoInstallPeers: true`. The importer pins concrete versions for Ant Design 5.29.3, Pro Components 2.8.10, Monaco 0.55.1, React/React DOM 18.3.1, React Router 6.30.3, SWR 2.4.1, TypeScript 5.9.3, ESLint 10.0.3, and Vite 8.0.5. It records many transitive packages such as `@rc-component/*`, `@formatjs/*`, `@typescript-eslint/*`, `@rolldown/binding-*`, `@xterm/*`, and Babel/Jridgewell utilities.

## Control Flow, State, and Persistence
The file has no executable flow, but it persists install state. `importers` maps the root project specs to resolved versions; `packages` lists registry package metadata and integrity; `snapshots` encode peer-expanded dependency graphs. Optional platform bindings allow Vite/Rolldown installation to select the correct native package per OS/architecture.

## Dependencies and Integration Points
It is consumed by pnpm for reproducible install and by CI when using frozen lockfile mode. It must stay in sync with `package.json`; otherwise install or CI can fail. Peer expansions integrate React, React DOM, antd, rc-field-form, eslint, and TypeScript versions across the UI stack.

## Risks and Test Signals
Risks include supply-chain exposure through a large UI graph, native optional dependency resolution on uncommon platforms, stale lock entries after package edits, and hidden behavioral changes when caret specs are refreshed. Signals are `pnpm install --frozen-lockfile`, `pnpm audit` or equivalent, successful cross-platform install, and reproducible `pnpm build`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/pnpm-lock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/App.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/App.tsx

## Purpose
`App.tsx` is the dashboard application root. It wires SWR fetching, Ant Design theming, Monaco worker setup, and React Router routes.

## Important APIs, Types, and Functions
The local generic `fetcher<T>` builds URLs from `getHost()` and `getBasePath()`, checks `res.ok`, and returns JSON. Monaco is configured through `self.MonacoEnvironment.getWorker()` and `loader.config({ monaco })`. The component renders `SWRConfig`, `ConfigProvider`, `BrowserRouter`, shared `Layout`, and routes for resource lists, resource details, and config detail.

## Control Flow, State, and Persistence
The root has no local React state. All data-fetch control passes through SWR's global fetcher. Routing redirects `/` to `/pods`, then matches `/:resources`, `/:resources/:namespace/:name`, `/:resources/:name`, and `/config`. Monaco worker state is global on `self`.

## Dependencies and Integration Points
It integrates generated Vite worker imports, Ant Design theme tokens, shared components from `@/components`, `ConfigDetail`, and utility base path resolution. It is the top-level place where backend API pathing and frontend routing must agree.

## Risks and Test Signals
Risks include generic fetch errors without response details, overlapping route patterns where `/:resources/:name` may catch namespaced-looking resources incorrectly, global Monaco worker assignment, and base-path misconfiguration behind reverse proxies. Signals are route smoke tests, API error handling checks, Monaco modal rendering, and deployment under a non-root basename.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/App.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/batch-upgrade-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/batch-upgrade-modal.tsx

## Purpose
`batch-upgrade-modal.tsx` presents the UI for creating a batch mount-pod upgrade job from selected PVC/node criteria and a preview of pods with config diffs.

## Important APIs, Types, and Functions
`BatchUpgradeModal` uses `usePVCsWithUniqueId`, `usePVCsBasicInfo`, `useNodes`, and `useCreateUpgradeJob`. It manages selected PVC, resolved unique ID, selected node, worker count, ignore-error flag, generated job name, and `PodDiffConfig[]`. Helper functions are `getAllPVCs` and `genNewJobName`.

## Control Flow, State, and Persistence
Opening the modal renders inputs and a `PodToUpgradeTable`. Selecting a PVC updates `selectedPVCName`, which resolves `uniqueId`; node data fills the dropdown. The start button is disabled until diff pods exist. On start, it calls `actions.execute(worker, ignoreError, newJobName, selectedNode, uniqueId)`, closes the modal, and navigates to `/jobs/{jobName}`. `resetState` resets only some fields and does not regenerate the job name or clear ignore-error/diff state.

## Dependencies and Integration Points
It connects config-diff discovery, PVC lookup, node lookup, upgrade job creation, and router navigation. The `PodToUpgradeTable` child reports whether there is actionable work by calling `setDiffPods`.

## Risks and Test Signals
Risks include stale generated job names across repeated opens, partial reset behavior, no catch path for create-job failures, using `"All Nodes"` as both UI label and API value, and possible layout overflow in the wide `Space`. Signals are modal open/close state tests, PVC/node filtering tests, disabled start when no diffs exist, successful job creation navigation, and error-path rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/batch-upgrade-modal.tsx -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/cg-workers-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/cg-workers-table.tsx

## Purpose
`cg-workers-table.tsx` renders and manages cache group worker pods, including listing, filtering, adding workers to nodes, removing workers, viewing cache bytes, and starting warmup.

## Important APIs, Types, and Functions
`CgWorkersTable` uses `useCacheGroupWorkers`, `useAddWorker`, `useRemoveWorker`, and `useNodes`. It manages table pagination/filter, refresh interval, existing worker nodes, and an add-worker `ModalForm`. Columns link to syspods, show node/status/cache bytes/start time, and provide a remove-worker `Popconfirm`.

## Control Flow, State, and Persistence
Initial refresh interval is 0 unless `autoRefresh` is true. API data updates pagination totals and existing node names. Adding or removing a worker executes the corresponding hook, shows a success message, and enables 1 second refresh. Table search values are flattened into `filter`, including nested metadata values.

## Dependencies and Integration Points
It integrates cache group worker backend endpoints, node inventory, pod status utility functions, `WorkerCacheBytes`, and `WarmupModal`. Worker status is affected by annotations such as `juicefs.io/waiting-delete-worker` and `juicefs.io/backup-worker`.

## Risks and Test Signals
Risks include duplicate disabled-node logic based only on current page data, success messages without error handling, nonlocalized Chinese success text, unsafe non-null assertions on pod specs/status, and repeated row polling. Signals are add/remove API tests, pagination/filter behavior, annotation status rendering, and ensuring warmup uses a valid container status.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/cg-workers-table.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/config-update-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/config-update-modal.tsx

## Purpose
`config-update-modal.tsx` confirms edits to the dashboard config ConfigMap by showing mount-pod patch diffs and the PVCs affected by each changed selector before saving.

## Important APIs, Types, and Functions
`ConfigUpdateConfirmModal` uses `useUpdateConfig`, `useConfigPVCSelector`, `YAML.parse/stringify`, `ReactDiffViewer`, `Collapse`, `PVCWithSelector`, and `PvcPop`. The internal `configDiff` compares `OriginConfig.mountPodPatch` entries and builds collapsible diff panels with matched PVC tables.

## Control Flow, State, and Persistence
When opened, the modal parses old and new YAML, asks the backend which PVCs match the proposed config, and stores old/new config plus PVC groups. Saving reparses YAML, executes an update ConfigMap request with `data['config.yaml']`, clears edit/update flags, and closes. Parse/API errors are sent to `setError`.

## Dependencies and Integration Points
It bridges the config editor page, ConfigMap update API, selector evaluation API, YAML config schema, diff viewer, and PVC display components. The positional relationship between `mountPodPatch[i]` and `pvcs[i]` is critical.

## Risks and Test Signals
Risks include index-based diffing that misses inserted/deleted/reordered patches, promise chaining where `.then()` runs after a caught update error, missing loading/error UI for selector fetch, and YAML parse errors typed narrowly. Signals are YAML parse tests, changed patch diff snapshots, backend selector alignment checks, and save error-path tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/config-update-modal.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-detail.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-detail.tsx

## Purpose
`mount-pod-patch-detail.tsx` displays a read-only view of one mount pod patch, including PVC selector criteria, images, labels, annotations, mount options, environment, resources, host flags, cache directories, and matched PVCs.

## Important APIs, Types, and Functions
`MountPodPatchDetail` takes a `mountPodPatch` and optional `PVCWithPod[]`. Its local `kvDescribe` renders key/value arrays. It uses `ProCard`, `ProDescriptions`, Ant Design `Checkbox`, `FormattedMessage`, and `PVCWithSelector`.

## Control Flow, State, and Persistence
The component is pure rendering. It conditionally renders the selector card when `patch.pvcSelector` exists, always renders basic patch descriptions, maps arrays to inline code blocks, switches on cache directory `type`, and appends matched PVC information.

## Dependencies and Integration Points
It depends on config type definitions and is likely used by config detail pages to turn stored YAML into operator-readable UI. It shares selector/PVC presentation with config update confirmation.

## Risks and Test Signals
Risks include uncontrolled checkboxes in read-only contexts, falsy numeric rendering for `terminationGracePeriodSeconds` equal to 0, incomplete environment rendering for `valueFrom` refs, and cache-dir fallback strings that may obscure invalid data. Signals are render snapshots for all patch fields, empty array handling, cache dir variants, and matched PVC link rendering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-detail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-form.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-form.tsx

## Purpose
`mount-pod-patch-form.tsx` renders the editable form for a mount pod patch, covering selector fields and all supported patch knobs.

## Important APIs, Types, and Functions
`MountPodPatchForm` composes `PVCSelectorForm`, `ProDescriptions`, `ProForm.Item`, `ProFormList`, `ProFormText`, `ProFormSelect`, `ProFormCheckbox`, `ProFormDependency`, `Input`, and `InputNumber`. It supports image overrides, labels, annotations, mount options, env vars with value/configMap/secret/fieldRef sources, resource requests/limits, host networking/PID flags, termination grace period, and cache directories of type HostPath/PVC/EmptyDir.

## Control Flow, State, and Persistence
The component has no local state; form state is owned by an ancestor ProForm. Dynamic subfields are selected by `ProFormDependency` for env `valueType` and cache `type`. Creator records set defaults for env and cache list entries.

## Dependencies and Integration Points
Field names are the persistence contract back to YAML serialization of `mountPodPatch`. It must match `MountPodPatchDetail`, backend config schema, and Kubernetes environment/resource/volume models.

## Risks and Test Signals
Risks include nested `ProForm.Item` structures that may not bind as intended, UI-only `valueType` fields leaking into serialized config, missing validation on CPU/memory quantities and mount option strings, and incomplete EmptyDir HugePages semantics. Signals are form submit serialization tests, edit-existing patch initialization, env valueFrom variants, cache dir validation, and round trip through YAML config update.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/mount-pod-patch-form.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/pvc-selector-form.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/pvc-selector-form.tsx

## Purpose
`pvc-selector-form.tsx` provides the editable selector subsection for mount pod patch rules.

## Important APIs, Types, and Functions
`PVCSelectorForm` accepts an optional `mountPodPatch`, renders a `ProCard` and `ProDescriptions`, and binds ProForm fields under `pvcSelector.matchName`, `pvcSelector.matchStorageClassName`, and `pvcSelector.matchLabels[]` entries with `key` and `value`.

## Control Flow, State, and Persistence
The component is stateless and relies on parent form context. It renders three selector categories: PVC name, storage class name, and label matches. Label matches are dynamically repeatable through `ProFormList`.

## Dependencies and Integration Points
It is embedded by `MountPodPatchForm` and must match backend config selector semantics used by `useConfigPVCSelector` and config diffing.

## Risks and Test Signals
Risks include no validation for mutually broad selectors, empty selector fields serializing as empty objects, and labels with empty key/value pairs. Signals are form serialization tests, selector evaluation against PVC fixtures, and UI checks for adding/removing label rows.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/config/pvc-selector-form.tsx -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/containers.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/containers.tsx

## Purpose
`containers.tsx` renders a pod's container status table and action buttons for logs, exec, access logs, debug collection, warmup, stats, and binary smooth upgrade.

## Important APIs, Types, and Functions
`Containers` accepts a `Pod` and optional `ContainerStatus[]`. It reads route params, version data, and utility predicates `isMountPod`, `isMountContainer`, `supportDebug`, and `supportBinarySmoothUpgrade`. It composes `LogModal`, `XTermModal`, `DebugModal`, `WarmupModal`, `StatsModal`, and `UpgradeModal`.

## Control Flow, State, and Persistence
The component is pure table rendering. For every container, basic log and terminal actions are always available. Mount pod/container conditions unlock access log, debug, warmup, stats, and upgrade actions. Upgrade is further gated by server-reported `disableGraceUpgrade` and image support.

## Dependencies and Integration Points
It integrates pod detail routes with websocket/download modals and smooth upgrade features. The actions depend on backend endpoints for logs, exec, debug, warmup, stats, and upgrade.

## Risks and Test Signals
Risks include using route params instead of pod metadata, invalid dates for non-running containers, record/c parameter confusion in render callbacks, and showing terminal/log actions for containers that backend may not permit. Signals are pod detail UI tests for mount and non-mount pods, image support gating, previous-log enablement, and action endpoint smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/containers.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/debug-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/debug-modal.tsx

## Purpose
`debug-modal.tsx` opens a modal for collecting runtime debug artifacts from a pod container, streaming progress over websocket, and downloading the collected files.

## Important APIs, Types, and Functions
`DebugModal` is memoized and uses Monaco `Editor`, Ant Design modal/buttons/input numbers, lodash `max`, `useCountdown`, `useWebsocket`, and `useDownloadPodDebugFiles`. It tracks modal state, collection state, streamed text, download readiness, and sampling durations for stats/trace/profile.

## Control Flow, State, and Persistence
The websocket connects only while the modal is open and collecting. Query parameters pass the three durations. Incoming messages append to the editor and set `canDownload` when the backend reports collection completion. Closing the modal resets the text to a help message and clears download state. Start resets countdown and begins collection; Download calls the download hook.

## Dependencies and Integration Points
It depends on backend websocket path `/api/v1/ws/pod/{namespace}/{name}/{container}/debug` and matching download endpoint in `useDownloadPodDebugFiles`. Monaco worker setup comes from `App.tsx`.

## Risks and Test Signals
Risks include brittle completion detection by substring, countdown not necessarily matching backend close, unlimited text accumulation, no websocket error display, and no min/max validation on duration inputs. Signals are websocket lifecycle tests, completion/download enablement, modal reset behavior, and large-output editor performance checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/debug-modal.tsx -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/index.ts -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/index.ts

## Purpose
`index.ts` is the barrel export for commonly used dashboard components.

## Important APIs, Types, and Functions
It imports and re-exports `Containers`, `DebugModal`, `EventTable`, `Layout`, `PodBasic`, `PodsTable`, `PVBasic`, `PVCBasic`, `ResourceDetail`, `ResourceList`, and `YamlModal`.

## Control Flow, State, and Persistence
There is no runtime control flow beyond module evaluation. It centralizes import paths for consumers such as `App.tsx`.

## Dependencies and Integration Points
The file creates a stable public surface for the components folder. Components not listed here must be imported directly, which separates generic/detail components from specialized modals/tables.

## Risks and Test Signals
Risks include circular dependencies because `containers.tsx` imports `DebugModal` from `.`, stale exports after component renames, and inconsistent import style across the app. Signals are TypeScript build success and dependency-cycle checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/index.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/layout.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/layout.tsx

## Purpose
`layout.tsx` defines the dashboard shell: fixed header, side navigation, localization provider, Ant Design locale/theme providers, and content area.

## Important APIs, Types, and Functions
It defines menu `items` for resource and tool navigation, then exports `Layout`. The component uses `useLocation`, `useVersion`, `IntlProvider`, nested `ConfigProvider`s, Ant Design `Layout`, `Menu`, `Button`, `Tooltip`, and locale dictionaries `en-US`/`zh-CN`.

## Control Flow, State, and Persistence
Locale is initialized from `window.localStorage`, defaults to `zh`, and is persisted whenever it changes. Menu selection derives from the first URL segment, with `/` treated as `/pods`. Header buttons show driver version, open docs/GitHub in new tabs, and toggle locale.

## Dependencies and Integration Points
It wraps all routed pages from `App.tsx`. It depends on browser localStorage/window, React Intl message IDs used by child components, Ant Design locale packages, icon components, and the backend version endpoint.

## Risks and Test Signals
Risks include client-only browser APIs, selected key mismatch for `/jobs` because the menu key is `/upgrade`, fixed layout responsiveness issues, and no validation of stored locale values. Signals are locale persistence tests, route/menu selection tests, mobile layout checks, and version display fallback.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/layout.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/log-modal.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/log-modal.tsx

## Purpose
`log-modal.tsx` streams pod container logs or mount access logs into a Monaco editor and supports full log download and current/previous log switching.

## Important APIs, Types, and Functions
`LogModal` is memoized and accepts namespace, pod name, container, previous-log capability, log type, and render-prop children. It uses `useWebsocket`, `useDownloadPodLogs`, Monaco editor refs, and Ant Design modal buttons.

## Control Flow, State, and Persistence
Opening the modal connects to `/api/v1/ws/pod/{namespace}/{name}/{container}/{type}` with `previous` as a query parameter. Incoming data appends to local text and auto-scrolls only if the user was already at the bottom. Closing clears log data. Previous/current toggling clears the buffer and changes websocket query params. Download is available only for normal logs.

## Dependencies and Integration Points
It is used by container action tables and depends on backend websocket/download APIs. Monaco worker setup is global in `App.tsx`.

## Risks and Test Signals
Risks include unlimited log buffer growth, no websocket error state, stale auto-scroll decisions if editor ranges are absent, a console log left in production, and no download type parameter for access logs. Signals are websocket append tests, previous-log switching, auto-scroll behavior, close/reset behavior, and large-log performance checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/log-modal.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-basic.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-basic.tsx

## Purpose
`pod-basic.tsx` renders basic pod metadata and top-level pod actions such as diagnosis download, smooth pod upgrade, and YAML viewing.

## Important APIs, Types, and Functions
`PodBasic` uses `useMountPodImage`, `useVersion`, `useDownloadPodDebugInfos`, `YamlModal`, `UpgradeModal`, YAML serialization, and pod utility functions `isMountPod`, `isSysPod`, `omitPod`, `podStatus`, `getPodStatusBadge`, and `supportPodSmoothUpgrade`.

## Control Flow, State, and Persistence
It tracks only YAML modal open state. For mount pods it shows a diagnosis gather/download button. Smooth upgrade is shown when grace upgrade is enabled and both original and resolved mount images support pod smooth upgrade. YAML content is desensitized through `omitPod` unless the utility treats the pod as a system pod.

## Dependencies and Integration Points
It appears in pod detail pages and integrates with debug-info download, mount pod image lookup, version configuration, smooth upgrade action, and YAML modal display.

## Risks and Test Signals
Risks include capturing the initial image in state so prop changes do not update it, assuming the first container image is the mount image, rendering invalid dates if creation timestamp is missing, and YAML modal placement inside a tooltip. Signals are mount/non-mount pod render tests, desensitization checks, upgrade gating tests, and debug download error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-basic.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-to-upgrade-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-to-upgrade-table.tsx

## Purpose
`pod-to-upgrade-table.tsx` previews mount pods whose current settings differ from the proposed config before a batch upgrade job is created.

## Important APIs, Types, and Functions
It defines `diffContent(podDiff)` using YAML and `ReactDiffViewer`, a `upgradeColumn` set for pod name and diff popover, and `PodToUpgradeTable` which calls `useConfigDiff(nodeName, uniqueId, pageSize, current)`.

## Control Flow, State, and Persistence
Pagination is local. When diff data changes, the table total is updated and `setDiffPods(diffPods?.pods || [])` informs the parent modal whether start should be enabled. Diff buttons show old/new setting YAML in a popover.

## Dependencies and Integration Points
It is used by `BatchUpgradeModal` and depends on backend config diff pagination. Links point to syspod details when namespace exists.

## Risks and Test Signals
Risks include large diff content inside a popover, no loading/error state, parent enablement based only on the current page of results, and non-null UID assertions. Signals are pagination tests, parent callback tests, diff rendering snapshots, and filters for node/PVC unique ID.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-to-upgrade-table.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-upgrade-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-upgrade-table.tsx

## Purpose
`pod-upgrade-table.tsx` renders the per-mount-pod status and config diff for an existing batch upgrade job.

## Important APIs, Types, and Functions
`PodUpgradeTable` consumes `UpgradeJobWithDiff`, `diffStatus`, and `failReasons`. It builds a `podMap`, flattens `upgradeJob.config.batches` into `UpgradeType[]`, renders pod links, status badges, failure tooltips, and diff popovers. Helper `getPodUpgradeStatus` prefers log-derived status, then falls back to batch config status.

## Control Flow, State, and Persistence
Effects rebuild map/table state when upgrade job or status map changes and update pagination total from `upgradeJob.total`. Diffs are disabled once `diffStatus` is `success`; otherwise they show YAML old/new settings. State is local and derived from props.

## Dependencies and Integration Points
It integrates upgrade job detail data, websocket/log-derived status maps, Ant Design table UI, diff viewer, YAML serialization, router links, and `getUpgradeStatusBadge`.

## Risks and Test Signals
Risks include missing `failReasons` in effect dependencies only affecting render because map reads are direct, pagination total not matching flattened rows, disabled diffs after success hiding historical changes, and empty dependency on `failReasons` for row status details. Signals are batch flattening tests, status precedence tests, failure tooltip rendering, and diff enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pod-upgrade-table.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pods-table.tsx -->
# sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pods-table.tsx

## Purpose
`pods-table.tsx` displays related pods for a pod, PV, or PVC detail page, such as app pods, mount pods, or CSI node pods.

## Important APIs, Types, and Functions
`PodsTable` takes `title`, `source`, `type`, `name`, and optional `namespace`, calls `usePods`, and renders an Ant Design table with pod link, namespace, status badge, and creation time. It uses `podStatus` and `getPodStatusBadge`.

## Control Flow, State, and Persistence
The component returns `null` when there is no data. It chooses route prefix `/pods` for `apppods` and `/syspods` otherwise. The table has no pagination and uses pod UID row keys.

## Dependencies and Integration Points
It integrates resource detail pages with backend related-pod lookup and shared pod status utilities.

## Risks and Test Signals
Risks include hiding the whole card during loading and empty states, unpaginated large pod lists, invalid dates for missing timestamps, and route assumptions tied to only one app-pod type. Signals are related-pod API fixtures, status badge tests, route-link checks, and large-list rendering checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/dashboard-ui-v2/src/components/pods-table.tsx -->
