# Research Report: subset-b-008133

Grouped research for Apache Ozone Recon web UI files in work item `subset-b-008133`. Each source file has a separate section delimited for reconciliation into the mapped source-tree-aligned research document.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/heatmap/heatmap.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/heatmap/heatmap.tsx

Purpose: Functional React implementation of the v2 Recon heatmap page. It displays read-access treemap data for Ozone paths, filtered by entity type and time period, and blocks the page when the backend reports the Heatmap feature as disabled.

Important APIs/types/functions: The component uses `useApiData<HeatmapResponse>` for `/api/v1/heatmap/readaccess`, `useApiData<{data:string[]}>` for `/api/v1/features/disabledFeatures`, `HeatmapPlot` for rendering, and Ant Design `Input.Search`, `Dropdown`, `Menu`, `DatePicker`, `Result`, and `Spin`. Local helpers include `handleChange`, `handleSubmit`, `normalize`, recursive `updateSize`, `updateHeatmapParent`, `isDateDisabled`, `handleDatePickerChange`, `handleMenuChange`, and `handleCalendarChange`.

Control flow: Initial state starts at root path `/`, entity type `key`, and the default configured period. When Heatmap is enabled and all query parts are present, the hook fetches `/api/v1/heatmap/readaccess?startDate=...&path=...&entityType=...`. Successful non-empty responses update module-level `minSize`/`maxSize`, mutate the response tree with `normalizedSize`, and clear `treeEndpointFailed`. Failed non-404 requests show a fetch error, reset the input/search path to root, and put the page in the endpoint-failed result path. Disabled-feature responses override the initial `location.state.isHeatmapEnabled` value.

State and persistence: Component state holds `heatmapResponse`, `entityType`, and `date`; separate state tracks path validation and committed `searchPath`; `treeEndpointFailed` and `isHeatmapEnabled` drive error rendering. There is no persistent browser storage. The file uses module-level `minSize` and `maxSize`, so normalization bounds are shared across component instances until manually reset on entity change or overwritten by a response.

Dependencies and integration points: Depends on v2 heatmap constants and types, the shared `showDataFetchError` helper, `useLocation` from React Router, and `HeatmapPlot`. It integrates with Recon REST endpoints `/api/v1/heatmap/readaccess` and `/api/v1/features/disabledFeatures`; child-node clicks call back with a path and trigger another heatmap fetch.

Risks: Query parameters are string-interpolated without URL encoding, so path characters outside the local regex or future relaxed validation can break requests. `updateSize` mutates hook response objects in place and assumes `children` is always present when `hasOwnProperty('children')` is true. `minSize`/`maxSize` are module globals, which can produce stale normalization if multiple heatmap instances ever coexist. The hook error branch assumes `error.response` shape for status checks. Date custom selection stores a Unix timestamp while menu periods are string keys, so UI comparison and default selected keys mix types.

Test signals: Useful tests should cover disabled-feature handling, 404 versus non-404 heatmap errors, path validation, entity/date menu changes, custom date disabling for future and older-than-90-day dates, recursive `normalizedSize` assignment for zero and nonzero nodes, and child click path refresh behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/heatmap/heatmap.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/insights/insights.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/insights/insights.tsx

Purpose: Functional v2 Insights page that renders two utilization charts: file-size frequency distribution and container-size distribution.

Important APIs/types/functions: Uses `useApiData<FileCountResponse[]>('/api/v1/utilization/fileCount')` and `useApiData<any[]>('/api/v1/utilization/containerCount')`, then passes responses to `FileSizeDistribution` and `ContainerSizeDistribution`. Its state is `InsightsState` for volume/bucket filter metadata plus a `PlotResponse` wrapper for both datasets.

Control flow: Both API hooks fetch on mount. An effect waits until both hooks are no longer loading, then derives a `Map<volume, Set<bucket>>`, converts volume keys into `Option[]`, records per-API errors, and updates `plotResponse` with either real data or default one-row placeholders. Rendering shows a loading `Result`, then two Ant Design cards with chart components or "No Data" results.

State and persistence: All state is local and volatile. Volume/bucket maps are recalculated from the latest file-count response. There is no polling, URL state, or persisted selection in this page; downstream chart components own filter interaction.

Dependencies and integration points: Integrates with Recon utilization endpoints, v2 chart components, the v2 multi-select option type, Ant Design grid/card/result, and shared fetch-error notifications.

Risks: The effect closes over `state` but does not include it in the dependency list, so concurrent state changes could be overwritten. `containerCountAPI` is typed as `any[]` instead of `ContainerCountResponse[]`, weakening compile-time checks. Default placeholder rows make `length > 0` true and can render charts with sentinel data if an endpoint returns undefined. Error values are passed as `string | undefined` in the type but hook errors may be richer objects.

Test signals: Tests should mock partial and complete API success, per-endpoint failures, empty arrays, duplicate volume/bucket pairs, and ensure chart props receive stable volume options, bucket maps, data, and error flags.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/insights/insights.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/insights/omInsights.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/insights/omInsights.tsx

Purpose: v2 OM DB Insights page shell. It assembles tabbed OM/SCM consistency and key-state tables, shares a limit selector across them, and supports expandable rows for container-to-key details.

Important APIs/types/functions: Uses `ContainerMismatchTable`, `DeletedContainerKeysTable`, `DeletePendingDirTable`, `DeletePendingKeysTable`, `ExpandedKeyTable`, and `OpenKeysTable`. It relies on `AxiosGetHelper` for row expansion against `/api/v1/containers/{containerId}/keys`, `MismatchKeysResponse`, `ExpandedRow`, and a `react-select` `Option` limit value. Primary callbacks are `onRowExpandClick`, `expandedRowRender`, and `handleLimitChange`.

Control flow: The page reads `activeTab` from React Router location state, defaults to tab `1`, and renders five Ant Design tab panes. Expanding a container row sets a shared loading flag, fetches keys for the selected container, stores them in `expandedRowData[containerId]`, and renders an `ExpandedKeyTable` with a generated `uid`. Each tab table receives the selected limit, common pagination config, and limit-change handler.

State and persistence: Local state holds global `loading`, all expanded row data, and the selected limit. No state is persisted. `rowExpandSignal` keeps the most recent row-expansion `AbortController`, but there is no unmount cleanup in this component.

Dependencies and integration points: Integrates with multiple v2 insights table components that own their own endpoint fetches. Router state from Overview summary cards selects Open Keys or Delete Pending Keys. It uses Ant Design tabs/tooltips and the shared fetch helper.

Risks: `setLoading(false)` is not called in the row-expansion catch path, so failures can leave expanded tables loading. A single global loading flag can make one expanded row affect all expanded row tables. The expansion request is not cancelled on unmount. `expandedRowData` updates read from the closure, so rapid row expansions can drop prior rows. The `activeTab` location destructuring assumes `location.state` is an object when present.

Test signals: Tests should cover route-state tab selection, limit propagation to each table, successful and failed expansion fetches, multiple expanded containers, and unmount/cancel behavior if it is later added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/insights/omInsights.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/namespaceUsage/namespaceUsage.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/namespaceUsage/namespaceUsage.tsx

Purpose: Functional v2 Namespace Usage page that visualizes size distribution under the current Ozone path and shows metadata for the selected path.

Important APIs/types/functions: Uses `useApiData<NUResponse>` for `/api/v1/namespace/usage?path=...&files=true&sortSubPaths=true`, `NUPieChart`, `NUMetadata`, `DUBreadcrumbNav`, `SingleSelect`, and local `LIMIT_OPTIONS`. Important handlers are `loadData` and `handleLimitChange`.

Control flow: The page starts at `/` with display limit `10`. Changing the breadcrumb path or clicking reload updates `currentPath`, which changes the hook URL. A side effect inspects `duResponse.status` and emits an error for `PATH_NOT_FOUND` or info notification for `INITIALIZING`. Rendering always shows an informational alert, breadcrumb/reload controls, a limit selector, the pie chart, and metadata panel.

State and persistence: Local state tracks selected limit and current path. There is no persistent storage or polling. Reloading the current path calls `loadData(duResponse.path)`, which may be a no-op if the path string is unchanged and the hook does not refetch on same URL.

Dependencies and integration points: Integrates with Recon namespace usage API, v2 namespace usage types, breadcrumb navigation, pie chart, metadata component, and shared notification helpers.

Risks: Path is interpolated without URL encoding. Reload via setting the same state value may not force a refetch depending on hook internals. Status handling notifies but does not replace stale data with an error view. `LIMIT_OPTIONS` only affects display in `NUPieChart`; it is not sent to the backend.

Test signals: Tests should cover initial root fetch, breadcrumb path changes, `PATH_NOT_FOUND` and `INITIALIZING` statuses, limit selection passed as a number, and reload semantics for same-path refresh.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/namespaceUsage/namespaceUsage.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/notFound/notFound.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/notFound/notFound.tsx

Purpose: v2 404 page with an inline SVG illustration and a primary "Go Back" button.

Important APIs/types/functions: Defines `notFoundIcon`, `contentStyles`, and functional component `NotFound`. It uses Ant Design `Button`, `ArrowLeftOutlined`, and React Router `useHistory`.

Control flow: Rendering centers the SVG, message text, and button. Clicking the button calls `history.goBack()`, delegating navigation behavior to React Router browser history.

State and persistence: Stateless component with no side effects beyond history navigation. The SVG is embedded directly in the module, so no asset loading or caching dependency is required.

Dependencies and integration points: Used as the fallback page in the v2 route layer or app shell. It depends on Ant Design styling and React Router history context.

Risks: `goBack()` may keep users on an invalid route if the previous entry is also invalid or if there is no meaningful prior page. The inline SVG is large and includes fixed font references, which can affect bundle size and rendering consistency.

Test signals: Tests should verify that the component renders a 404 message and that clicking the button invokes `history.goBack`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/notFound/notFound.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/overview/overview.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/overview/overview.tsx

Purpose: v2 Recon Overview dashboard. It aggregates cluster health, capacity, object counts, OM sync status, and open/delete-pending key summaries into cards and summary tables.

Important APIs/types/functions: Uses four `useApiData` hooks for `/api/v1/clusterState`, `/api/v1/task/status`, `/api/v1/keys/open/summary`, and `/api/v1/keys/deletePending/summary`, all with `initialFetch:false`. Uses `useAutoReload(loadOverviewPageData)`, `AutoReloadPanel`, `OverviewHealthCard`, `OverviewSimpleCard`, `OverviewSummaryCard`, `CapacityBreakdown`, `WrappedInfoIcon`, and imperative `syncOmData` via `AxiosGetHelper('/api/v1/triggerdbsync/om')`. Helper `getSummaryTableValue` formats byte or count values.

Control flow: `loadOverviewPageData` refetches all four hooks and sets `lastRefreshed`. Auto-reload and manual reload call that function. The task-status response is searched for `OmDeltaRequest` and `OmSnapshotRequest` timestamps for display in `AutoReloadPanel`. `syncOmData` triggers OM DB sync and stores the backend status string. Rendering lays out health cards, capacity breakdown, object count cards, two OM summary cards linking to `/Om` with tab state, and service identifiers.

State and persistence: Local state only stores `omStatus` and `lastRefreshed`. `cancelOMDBSyncSignal` persists the active sync request controller across renders and is cancelled on unmount. There is no local storage. Hook data is managed by the custom hooks.

Dependencies and integration points: Integrates with Recon cluster state, task status, OM key summary, and DB sync endpoints. Links drive navigation to Datanodes, Containers, Capacity, Volumes, Buckets, Pipelines, and OM DB Insights tabs. Uses `filesize` for sizes and `moment` for refresh timestamps.

Risks: Because all hooks use `initialFetch:false`, first render depends on `useAutoReload` invoking the loader; if that hook does not fire immediately, cards can remain at defaults. `storageReport` is destructured from default data, so defaults must always include it. Other-used-space arithmetic can go negative if backend reports inconsistent capacity fields. `syncOmData` catches `Error` but Axios errors can have richer shape. Links use capitalized paths that must match route definitions exactly.

Test signals: Tests should cover initial auto-load, manual reload, OM sync success/failure/cancel, missing task statuses, capacity item calculations, summary formatting for `null`, empty strings, counts, and byte values, and route state for summary-card links.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/overview/overview.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/pipelines/pipelines.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/pipelines/pipelines.tsx

Purpose: v2 Pipelines page that lists SCM pipelines with column selection, pipeline-ID search, and auto-reload controls.

Important APIs/types/functions: Uses `useApiData<PipelinesResponse>('/api/v1/pipelines')`, `useAutoReload`, `useDebounce`, `PipelinesTable`, v2 `Search`, and `MultiSelect`. `defaultColumns` is derived from `PipelinesTable.COLUMNS`.

Control flow: The hook is configured with `initialFetch:false`; `loadPipelinesData` calls `refetch` and is wired to auto reload and manual reload. When data changes, an effect stores the pipelines as `activeDataSource` and updates `lastUpdated`. UI changes update selected columns and the search term; debounced search is passed to the table.

State and persistence: Local state holds active rows, available column options, and last update timestamp. Separate local state tracks selected columns and search term. No persistence or URL state is used.

Dependencies and integration points: Integrates with `/api/v1/pipelines`, shared reload panel, v2 table/search/select components, and pipeline type definitions.

Risks: The data effect spreads `state` from the closure and omits `state` from dependencies, so unrelated state fields can become stale if extended later. `defaultColumns` assumes every table column title is either a string or callable returning props with `children[0]`; table-column title changes can break label generation. With `initialFetch:false`, first load depends on auto-reload hook behavior.

Test signals: Tests should cover refetch on mount/auto reload/manual reload, column selection and tag close, search debounce passed to the table, disabled search when no rows exist, and behavior when the API returns empty or malformed pipeline arrays.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/pipelines/pipelines.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/volumes/volumes.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/volumes/volumes.tsx

Purpose: v2 Volumes page that fetches Ozone volumes, supports limit selection, column selection, search by volume/owner/admin, and shows ACLs in a drawer.

Important APIs/types/functions: Uses `useApiData<VolumesResponse>(/api/v1/volumes?limit=...)`, `useAutoReload`, `useDebounce`, `VolumesTable`, `AclPanel`, `SingleSelect`, `MultiSelect`, and `Search`. Main handlers are `handleColumnChange`, `handleLimitChange`, `handleTagClose`, `handleAclLinkClick`, and `loadVolumesData`.

Control flow: Selected limit is included in the hook URL. Refetch is invoked by auto reload and manual reload. When volume data changes, the effect maps backend rows into `Volume` objects and updates table data plus `lastUpdated`. Search column changes clear the term. Clicking an ACL link stores the current row and opens the drawer.

State and persistence: Local state stores table data, last update, and column options. Separate state stores current ACL row, selected columns, selected limit, search column/term, and drawer visibility. There is no persistence or URL state.

Dependencies and integration points: Integrates with `/api/v1/volumes`, v2 volume and ACL types, the shared limit constants, and table/drawer components. The table calls back to `handleAclClick`.

Risks: The `currentRow` state is typed as `Volume | Record<string, never>` but rendered as though it always has `acls` and `volume`, which can produce undefined props before a row is selected. The data effect spreads stale `state` from a closure. Changing `selectedLimit` changes the hook URL, but first load still relies on `initialFetch:false` and explicit refetch behavior. It maps only known fields, so new backend fields are intentionally discarded.

Test signals: Tests should cover limit changes, reload, column selection/tag close, all three search columns, ACL drawer open/close, empty data, and fetch errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/volumes/volumes.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/routes-v2.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/routes-v2.tsx

Purpose: Defines the lazy-loaded route table for the v2 Recon UI.

Important APIs/types/functions: Imports `lazy` from React, creates lazy component factories for Overview, Volumes, Buckets, Datanodes, Pipelines, NamespaceUsage, Containers, Insights, OMDBInsights, Capacity, Heatmap, and Assistant, and exports `routesV2`.

Control flow: There is no runtime control flow beyond lazy import resolution when a route is matched by the app shell. Each route object has a capitalized path and component reference.

State and persistence: Stateless module. Lazy imports are cached by the bundler/runtime after load; no application state is held here.

Dependencies and integration points: Consumed by the v2 router/shell. It is the integration surface tying route URLs such as `/Overview`, `/Om`, and `/Heatmap` to page modules.

Risks: Paths are case-sensitive in common router configurations and must match all `Link` targets. There is no explicit catch-all route in this file. Adding a page requires adding both the lazy import and route object. Lazy loading requires a Suspense boundary in the consuming app.

Test signals: Route tests should verify every route path renders the expected lazy component and that existing navigation links use matching path casing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/routes-v2.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/acl.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/acl.types.ts

Purpose: Defines v2 ACL identity/right constants and the common ACL row shape used by volume and bucket UI.

Important APIs/types/functions: Exports `ACLIdentityTypeList`, union type `ACLIdentity`, `ACLRightList`, union type `ACLRight`, and `Acl` with `type`, `name`, `scope`, and `aclList`.

Control flow: Type-only and constant module; no runtime logic except exporting arrays used for validation or UI option generation.

State and persistence: No state. Constants are immutable by TypeScript `as const` typing but not frozen at runtime.

Dependencies and integration points: Referenced by v2 bucket/volume types and ACL drawer components. Values correspond to Ozone ACL identity and right enums.

Risks: `Acl.type` remains plain `string` rather than `ACLIdentity`, and `aclList` is `string[]` rather than `ACLRight[]`, so compile-time validation is weaker than the exported lists imply. Backend enum changes require updating these lists.

Test signals: Type-level or component tests should ensure ACL drawer/selectors render every identity/right and tolerate unknown backend values when types remain strings.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/acl.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/bucket.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/bucket.types.ts

Purpose: Declares v2 bucket API, state, and table prop types.

Important APIs/types/functions: Exports `BucketStorageTypeList`/`BucketStorage`, `BucketLayoutTypeList`/`BucketLayout`, `Bucket`, `BucketResponse`, `BucketsState`, and `BucketsTableProps`. It imports `Acl` and v2 multi-select `Option`.

Control flow: Type module only. Constants are used by table filters and UI display; interfaces shape API transformation and component props.

State and persistence: No runtime state. `BucketsState` models page-local state including `volumeBucketMap`, selected bucket collections, and column/volume options.

Dependencies and integration points: Couples bucket UI to Ozone Manager storage type and bucket layout enums, ACL display, and table/select components.

Risks: Backend enum additions need list updates. `volumeBucketMap: Map<string, Set<Bucket>>` stores object identities, so duplicate bucket records are only deduplicated by object reference. `acls` is optional and consumers must handle absence.

Test signals: Compile and component tests should verify filter options align with supported backend enum values, ACL-optional buckets render safely, and table props support search by name and volumeName.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/bucket.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/capacity.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/capacity.types.ts

Purpose: Defines v2 capacity and utilization API response types for global storage, namespace usage, data-node usage, pending deletion, and chart segments.

Important APIs/types/functions: Important exported types are `DataNodeUsage`, `UtilizationResponse`, `DNPendingDeletion`, `OMPendingDeletion`, `SCMPendingDeletion`, and `Segment`. Internal helper shapes include `GlobalStorage`, `GlobalNamespace`, `UsedSpaceBreakdown`, `OpenKeyBytesInfo`, and `DNPendingDeleteStat`.

Control flow: Type-only module. It encodes nested REST response contracts consumed by capacity components.

State and persistence: No runtime state. Nullable fields in pending deletion types model backend jobs that may not have completed.

Dependencies and integration points: Used by v2 capacity page/components and any chart code requiring segment labels as strings or React nodes. Values map to Recon capacity/utilization endpoints.

Risks: Several internal types are not exported, limiting reuse outside this module. `DNPendingDeletion.status` is a strict union, so backend status additions break typing until updated. `React.ReactNode` is referenced without importing React in modern TS configs that do not provide global React types.

Test signals: Type-checking and API fixture tests should cover complete, in-progress, failed, and null pending deletion responses plus utilization responses with all nested storage fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/capacity.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/chatbot.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/chatbot.types.ts

Purpose: Defines request/response and local message types for the v2 Assistant/chatbot feature.

Important APIs/types/functions: Exports `ChatbotHealthResponse`, `ChatbotModelsResponse`, `ChatbotChatRequest`, `ChatbotChatResponse`, `ChatbotErrorResponse`, and `ChatMessage`.

Control flow: Type-only contract. `ChatbotChatRequest` permits optional model/provider/userId, while `ChatMessage` models rendered conversation entries with role, text, timestamp, and optional model/provider.

State and persistence: No runtime state. `ChatMessage` is suitable for local UI state or persisted transcript storage elsewhere, but this file does not persist anything.

Dependencies and integration points: Used by v2 Assistant page and services integrating with chatbot health, model listing, and chat endpoints.

Risks: `ChatbotChatResponse` has only `response` and `success`; if failures return the separate `ChatbotErrorResponse`, callers must branch on HTTP/error handling rather than a discriminated union. `role` excludes future system/tool messages.

Test signals: API-client tests should cover health unavailable, empty model list, successful chat, error response, and optional model/provider propagation into rendered messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/chatbot.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/container.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/container.types.ts

Purpose: Declares v2 container, unhealthy-container pagination, key expansion, quasi-closed container, table prop, and export job types.

Important APIs/types/functions: Exports `ContainerReplica`, `Container`, `KeyResponse`, `ContainerKeysResponse`, `ContainersPaginationResponse`, `QuasiClosedContainer`, `QuasiClosedContainersResponse`, `TabPaginationState`, `ContainerTableProps`, `ExpandedRow`, `ExpandedRowState`, `ContainerState`, `ExportJobStatus`, and `ExportJob`.

Control flow: Type-only module. It models cursor/pagination state through first/last keys and page history, expanded rows keyed by container id, and export job lifecycle from queued through completed/failed.

State and persistence: No state in the module. Several types are designed to represent page-local state (`TabPaginationState`, `ContainerState`) and long-running backend export state (`ExportJob` with timestamps and remaining downloads).

Dependencies and integration points: Used by v2 containers tables/pages and row expansion against `/api/v1/containers/{id}/keys`. Imports v2 multi-select `Option` for table-column selection props.

Risks: The file has both `containerID` and `containerId` naming conventions across types, mirroring backend inconsistencies and increasing mapping mistakes. `ExportJob.state` is an unconstrained string even though `status` is constrained. `KeyResponse.Blocks` is keyed by `number`, but JSON object keys are strings at runtime.

Test signals: Fixture tests should cover all unhealthy count fields, row expansion key shapes, quasi-closed container rows, cursor pagination state transitions, and export job status rendering for queued/running/completed/failed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/container.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/datanode.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/datanode.types.ts

Purpose: Defines v2 datanode API rows, UI rows, operational state constants, decommission summary shapes, and table props.

Important APIs/types/functions: Exports `DatanodeStateList`/`DatanodeState`, `DatanodeOpStateList`/`DatanodeOpState`, `DatanodeResponse`, `DatanodesResponse`, `Datanode`, `DatanodeDetails`, `DatanodeDecomissionInfo`, `DatanodesState`, `SummaryData`, and `DatanodeTableProps`.

Control flow: Type-only module. It separates raw `DatanodeResponse.storageReport` from flattened `Datanode` storage fields used by tables. Summary types model `/api/v1/datanodes/decommission/info` style nested responses.

State and persistence: No runtime state. `DatanodesState` represents page-local table data and column options.

Dependencies and integration points: Imports `Pipeline`, `DatanodeStorageReport`, and multi-select `Option`. Constants correspond to HDDS node state and operational state enums.

Risks: The decommission spelling is inconsistent (`DatanodeDecomissionInfo`) and can propagate typos. `SummaryPort` is a single object, but backend details may expose multiple ports. Some summary fields are typed as broad `unknown | null` or nested ByteString-like internals, so components remain coupled to backend serialization details.

Test signals: Type/API fixture tests should cover each node state/op state, flattened storage transformations, decommission summary with and without metrics/containers, and table selection/search props.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/datanode.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/datanodeStorageReport.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/datanodeStorageReport.types.ts

Purpose: Defines the storage-report shape used by the v2 Datanodes page.

Important APIs/types/functions: Exports `DatanodeStorageReport` with required Ozone-usable fields `capacity`, `used`, `remaining`, and `committed`, plus optional `reserved`, `minimumFreeSpace`, `filesystemCapacity`, `filesystemUsed`, and `filesystemAvailable`.

Control flow: Type-only module. The comments document the semantic distinction between Ozone-usable stats and raw filesystem stats.

State and persistence: No state. Optional fields allow older or partial backend responses.

Dependencies and integration points: Imported by datanode types and table/card components that display storage bars or detailed capacity fields.

Risks: Components must not assume optional raw filesystem fields exist. Numeric units are implied bytes but not enforced in type names. Backend field renames will surface as undefined values rather than compile errors if data is treated dynamically.

Test signals: Storage display tests should include responses with only required fields and responses with all optional raw/reserved fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/datanodeStorageReport.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/heatmap.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/heatmap.types.ts

Purpose: Defines v2 heatmap input, response, and page-state types.

Important APIs/types/functions: Exports `InputPathValidTypes`, `HeatmapChild`, `InputPathState`, `HeatmapResponse`, `HeatmapState`, and `IResponseError`.

Control flow: Type-only module. It models a root response with min/max access counts and children, and leaf children with size/access/color fields.

State and persistence: No runtime state. `HeatmapState` covers the main page state while `InputPathState` covers form validation state.

Dependencies and integration points: Used by v2 heatmap page and heatmap plot components. `InputPathValidTypes` mirrors Ant Design `Form.Item` validation states.

Risks: `HeatmapChild` lacks optional `path`, `children`, and `normalizedSize` fields even though the page recursively traverses children and mutates `normalizedSize`. `IResponseError` is exported but unused in the v2 heatmap page import set. `date` is `string | number`, reflecting mixed period keys and custom Unix timestamps.

Test signals: Type tests or fixture-driven component tests should include nested child structures, zero-size children, custom timestamp dates, and invalid path states.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/heatmap.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/insights.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/insights.types.ts

Purpose: Central v2 type contract for Insights and OM DB Insights data.

Important APIs/types/functions: Exports chart response types (`FileCountResponse`, `ContainerCountResponse`, `PlotResponse`, `FilePlotData`, `ContainerPlotData`, `InsightsState`), mismatch/deleted container types, mismatch key types, replication discriminated union (`RatisInfo`, `EcInfo`, `ReplicationInfo`), open key types, delete-pending key/dir response types, and expanded-row types.

Control flow: Type-only module. The replication union controls rendering logic for RATIS versus EC keys. OM insight responses model multiple endpoints: container mismatch, deleted container keys, open keys, delete-pending keys, delete-pending directories, and container key expansion.

State and persistence: No module state. `InsightsState` and `ExpandedRow` are page-local UI state models.

Dependencies and integration points: Imports v2 multi-select `Option`. Used by v2 insights charts, OM insight page, and insights table components.

Risks: Some backend shapes are very specific and inconsistently named (`Volume`, `Bucket`, `Key` uppercase; `DeletedDirReponse` typo). `MismatchKeys.Blocks` is `Record<string, []>`, losing block detail. `ReplicationInfo` requires checking `replicationType` before accessing RATIS/EC-specific fields. `fileCountError` and `containerSizeError` are strings while hook errors may be objects.

Test signals: Tests should cover RATIS and EC open-key rows, empty and populated file/container distributions, mismatch container expansion, delete-pending key summary aggregation, and typo-sensitive response mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/insights.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/namespaceUsage.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/namespaceUsage.types.ts

Purpose: Defines v2 namespace usage response and pie chart data types.

Important APIs/types/functions: Exports `NUSubpath`, `NUResponse`, and `PlotData`.

Control flow: Type-only module. `NUResponse.status` determines page notifications and error paths; `subPaths` drives breadcrumb and chart content.

State and persistence: No state. `PlotData` represents derived chart slices with display strings for size and percentage.

Dependencies and integration points: Used by Namespace Usage page, pie chart, metadata, and breadcrumb components. Mirrors `/api/v1/namespace/usage` response fields.

Risks: `status` is plain `string`, so known statuses such as `PATH_NOT_FOUND` and `INITIALIZING` are not type-checked. `sizeDirectKey` exists in the response but is not used by the v2 page. Paths must be normalized by backend or breadcrumb/chart path logic can misbehave.

Test signals: Fixtures should include root, directory, key, empty, `PATH_NOT_FOUND`, and `INITIALIZING` responses, including mixed `isKey` values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/namespaceUsage.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/overview.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/overview.types.ts

Purpose: Defines v2 Overview dashboard response and local state types.

Important APIs/types/functions: Exports `ClusterStateResponse`, `TaskStatus`, `KeysSummary`, `StorageReport`, and `OverviewState`.

Control flow: Type-only module. `TaskStatus.taskName` includes known OM task names while allowing arbitrary strings, and `StorageReport` supports capacity-breakdown arithmetic.

State and persistence: No runtime state. `OverviewState` contains local OM sync status and refresh timestamp only.

Dependencies and integration points: Used by v2 Overview page and overview card components. Maps to `/api/v1/clusterState`, `/api/v1/task/status`, and key summary endpoints.

Risks: `ClusterStateResponse` requires all count and service-id fields, so default constants must stay complete. `KeysSummary` omits `totalOpenKeys`/`totalDeletedKeys`, causing pages to use intersections for those endpoint-specific fields. `TaskStatus.taskName` is not a discriminated union because of the catch-all `string`.

Test signals: Fixture tests should cover missing/zero counts, storage report arithmetic, known and unknown task names, and summary endpoints with additional count fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/overview.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/pipelines.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/pipelines.types.ts

Purpose: Defines v2 pipeline status constants, API response types, page state, and table props.

Important APIs/types/functions: Exports `PipelineStatusList`, `PipelineStatus`, `Pipeline`, `PipelinesResponse`, `PipelinesState`, and `PipelinesTableProps`.

Control flow: Type-only module. Status constants support filters/rendering, while `Pipeline` records leader, datanodes, election timing, replication, and container count.

State and persistence: No runtime state. `PipelinesState` models local table data, column options, and refresh timestamp.

Dependencies and integration points: Imports multi-select `Option`. Used by v2 pipelines page/table and by datanode types for pipeline lists.

Risks: Backend status additions must update `PipelineStatusList`. `replicationType` and `replicationFactor` are plain strings rather than unions. `datanodes` is a string list, so richer datanode metadata is not available at this layer.

Test signals: Tests should include every pipeline status, empty datanode lists, multiple datanodes, missing leader, and table search/column-selection props.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/pipelines.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/volume.types.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/volume.types.ts

Purpose: Defines v2 volume API rows, response, page state, and table props.

Important APIs/types/functions: Exports `Volume`, `VolumesResponse`, `VolumesState`, and `VolumesTableProps`. It imports common `Acl` and multi-select `Option`.

Control flow: Type-only module. The table props define ACL click callbacks, selected columns, and search by `volume`, `owner`, or `admin`.

State and persistence: No runtime state. `VolumesState` models local data, last refresh, and column options.

Dependencies and integration points: Used by v2 Volumes page/table and ACL drawer integration. Mirrors `/api/v1/volumes` response fields.

Risks: `acls` is optional, so drawer/table code must handle absent ACLs. Quota fields are numeric and likely bytes/counts but not branded by units. Backend additions are ignored unless the type and mapper are updated.

Test signals: Tests should cover ACL-present and ACL-missing rows, quota edge values, search over volume/owner/admin, and empty response handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/types/volume.types.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/utils/momentUtils.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/utils/momentUtils.ts

Purpose: Centralizes compact time formatting helpers for the v2 UI and customizes Moment's English relative-time strings.

Important APIs/types/functions: Calls `moment.updateLocale('en', { relativeTime: ... })` at module load. Exports `getTimeDiffFromTimestamp(timestamp)`, `getDurationFromTimestamp(timestamp)`, and `getFormattedTime(time, format)`.

Control flow: Importing the module globally changes Moment's `en` locale relative-time output. `getTimeDiffFromTimestamp` converts a numeric timestamp to `Date` and returns `fromNow()`. `getDurationFromTimestamp` treats input as milliseconds, decomposes years/months/days/hours/minutes/seconds, returns an empty string for invalid/zero ISO `P0D`, and otherwise returns compact parts or "Just now". `getFormattedTime` formats strings directly and formats positive numeric times, returning `N/A` for nonpositive numeric values.

State and persistence: The locale mutation is global process/browser state for Moment. Helpers themselves are stateless.

Dependencies and integration points: Used wherever v2 table/cards need compact elapsed time, durations, or formatted timestamps. Depends entirely on Moment.

Risks: `moment.updateLocale` affects all Moment relative-time formatting in the app after import. `getDurationFromTimestamp(0)` returns empty string, while sub-second positive durations return "Just now"; callers need to distinguish those semantics. String times are formatted even if invalid, which can produce Moment's invalid-date output.

Test signals: Unit tests should cover past timestamps, zero/invalid duration, multi-unit durations, sub-second durations, numeric `0`, negative numbers, string dates, invalid strings, and global relative-time formatting expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/utils/momentUtils.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/buckets/buckets.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/buckets/buckets.tsx

Purpose: Legacy class-component Buckets page. It lists buckets with volume filtering, column selection, limit selection including custom values, quota bars, ACL drawer, and auto reload.

Important APIs/types/functions: Defines backend response interfaces, `IBucketsState`, limit options, render helpers for versioning/storage type/bucket layout, mutable `COLUMNS`, and class methods `_addAclColumn`, `_handleColumnChange`, `_handleLimitChange`, `_onCreateOption`, `_handleVolumeChange`, `_getSelectedColumns`, `_handleAclLinkClick`, `_getVolumeSearchParam`, and `_loadData`. Uses `AxiosGetHelper('/api/v1/buckets', ..., {limit})`, `AutoReloadHelper`, `ColumnSearch`, `QuotaBar`, `AclPanel`, `MultiSelect`, and `CreatableSelect`.

Control flow: Constructor injects an ACL column into module-level column arrays and initializes auto reload. On mount, an optional `volume` query parameter preselects a volume, `_loadData` fetches buckets, maps backend `name` to UI `bucketName`, builds a `Map<volume, Set<bucket>>`, builds volume options, and selects all volumes or preserves prior selection. Rendering filters `COLUMNS` by selected columns and applies `ColumnSearch` to searchable columns. Unmount stops polling and aborts the latest request.

State and persistence: Local state stores loading, total count, selected columns/volumes/buckets, volume map/options, current ACL row, drawer visibility, selected limit, and refresh timestamp. No storage persistence. Module-level `COLUMNS`, `defaultColumns`, and `cancelSignal` are shared across instances.

Dependencies and integration points: Integrates with `/api/v1/buckets`, legacy OM types, common ACL drawer, quota bars, Ant Design Table, React Router location search, and the legacy auto-reload helper.

Risks: Mutating module-level `COLUMNS`/`defaultColumns` can leak across reloads or tests. `_onCreateOption` accepts `parseInt(created)` truthiness, rejecting `0` but accepting partially numeric strings in some cases. `selectedVolumes` can contain the all-volumes sentinel `*`; `_handleVolumeChange` ignores it unless the real volume options are also included. Request cancellation uses a module global controller. Query-param typing assumes `props.location.search` exists although props are declared generically.

Test signals: Tests should cover URL volume preselection, fetch mapping, all-volume selection, custom limit validation, ACL column/drawer behavior, quota columns, column search injection, polling start/stop, and aborted in-flight requests on unmount.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/buckets/buckets.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/datanodes/datanodes.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/datanodes/datanodes.tsx

Purpose: Legacy class-component Datanodes page. It lists datanodes, displays health/operational state, storage and pipeline details, overlays decommissioning status, and allows removing dead datanodes from Recon tracking.

Important APIs/types/functions: Defines datanode/pipeline interfaces, render helpers `renderDatanodeState`, `renderDatanodeOpState`, local `getTimeDiffFromTimestamp`, table `COLUMNS`, and class methods `_loadData`, `_loadDecommisionAPI`, `_loadDataNodeAPI`, `removeDatanode`, selection handlers, and confirmation handlers. Uses `AxiosGetHelper` for `/api/v1/datanodes/decommission/info` and `/api/v1/datanodes`, `AxiosPutHelper('/api/v1/datanodes/remove')`, `AutoReloadHelper`, `ColumnSearch`, `StorageBar`, `ReplicationIcon`, and `DecommissionSummary`.

Control flow: Each refresh first fetches decommission info to collect UUIDs, then fetches datanodes and maps rows into table data. If a UUID appears in the decommission set and is not already `DECOMMISSIONED`, displayed `opState` is forced to `DECOMMISSIONING`. Auto reload starts on mount. Row selection is enabled only for records with state `DEAD`; confirming removal sends selected row keys to the remove endpoint and reloads.

State and persistence: Local state stores loading, row data, total count, selected columns, selected row keys, and last update. Module-level globals hold cancellation controllers and `decommissionUuids`, which are shared across component instances. No persisted storage.

Dependencies and integration points: Integrates with Recon datanode and decommission endpoints, Ant Design Table/Popover/Popconfirm, storage/pipeline visualization components, and legacy auto reload.

Risks: Module-level `decommissionUuids` is read inside column renderers, making rendering depend on shared mutable state outside React. `lastHeartbeat` is typed as string in the backend response but treated numerically in table rows. Errors in the decommission call prevent the datanode call from showing otherwise valid data. `removeDatanode` reuses `cancelSignal` also used for datanode GET requests. `onDisable` returns `undefined` for enabled rows, relying on Ant Design truthiness.

Test signals: Tests should cover sequential decommission+datanode fetches, display override for decommissioning UUIDs, row selection disabled for non-DEAD nodes, remove PUT payload and reload, pipeline popovers, storage rendering, search/filter columns, and cancellation on unmount.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/datanodes/datanodes.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/datanodes/decommissionSummary.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/datanodes/decommissionSummary.tsx

Purpose: Legacy row-level popover component that fetches and displays decommission details for a datanode UUID.

Important APIs/types/functions: Class component `DecommissionSummary` wrapped with `withRouter`. It uses `axios.get('/api/v1/datanodes/decommission/info/datanode?uuid=...')`, Ant Design `Descriptions`, `Popover`, `Tooltip`, and `InfoCircleOutlined`. Main methods are `componentDidMount`, `fetchDecommissionSummary`, and `render`.

Control flow: On mount, it marks itself loading and fetches summary data for `props.uuid` if local `record` and `summaryData` exist. Successful response selects the first `DatanodesDecommissionInfo` entry. Rendering builds a descriptions panel when summary data has `datanodeDetails`, optionally including metrics and under-replicated/unclosed container lists, and wraps the UUID in a hover popover.

State and persistence: State is initialized from props and later stores `summaryData` and loading flags. No persistent storage. There is no request cancellation on unmount.

Dependencies and integration points: Used by the legacy Datanodes table UUID column when a row is actively decommissioning. Integrates directly with the decommission detail endpoint and shared fetch-error helper.

Risks: Props and state are typed as `string[]` but used as objects with fields such as `datanodeDetails`, causing weak type safety. State sets `loading` while the interface names `isLoading`. No cancellation means unmounted row components can set state after fetch completion. The mount guard checks `summaryData` even though the initial empty array is truthy, so it always fetches when a record exists.

Test signals: Tests should cover successful summary with metrics/containers, empty summary fallback to plain UUID, fetch error notification, and unmount behavior if cancellation is added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/datanodes/decommissionSummary.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/diskUsage/diskUsage.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/diskUsage/diskUsage.tsx

Purpose: Legacy Namespace Usage/Disk Usage page. It renders a navigable pie chart of namespace usage, supports path input, back/refresh, display-limit selection, and a metadata drawer for the current path.

Important APIs/types/functions: Defines DU response/subpath/plot/state interfaces, constants `DEFAULT_DISPLAY_LIMIT`, `OTHER_PATH_NAME`, `MAX_DISPLAY_LIMIT`, and `MIN_BLOCK_SIZE`, and class methods `handleChange`, `handleSubmit`, `goBack`, `updatePieChart`, `clickPieSection`, `refreshCurPath`, and `showMetadataDetails`. Uses `AxiosGetHelper` against `/api/v1/namespace/usage`, `/api/v1/namespace/summary`, and `/api/v1/namespace/quota`, `cancelRequests`, `EChart`, `DetailPanel`, and `byteToSize`.

Control flow: Mount loads root usage. Submitting a path cancels outstanding requests and calls `updatePieChart`. That method fetches namespace usage, handles `PATH_NOT_FOUND`, slices subpaths to the selected limit, computes an "Other Objects" slice when needed, adds `MIN_BLOCK_SIZE` to nonzero slices for visibility, and stores chart data. Clicking a slice navigates into it unless it is "Other Objects". Metadata fetch starts summary and quota requests in parallel and appends fields to shared key/value arrays before showing the drawer.

State and persistence: Local state stores loading, current response, plot data, drawer visibility/content, normalized return path, input path, and display limit. Module-level cancellation controllers and `valuesWithMinBlockSize` are shared. No browser persistence.

Dependencies and integration points: Integrates with Recon namespace usage, summary, and quota endpoints, Ant Design controls, ECharts wrapper, and legacy right drawer.

Risks: Paths are interpolated without URL encoding. `IDUResponse` is typed as an array in state but used as an object throughout. The synthetic `other` subpath omits required `sizeWithReplica` and `isKey` fields. Summary and quota requests mutate the same `keys`/`values` arrays asynchronously, so drawer order/content can race. The form `onSubmit` does not visibly prevent default. `structuredClone` may be unavailable in older browsers.

Test signals: Tests should cover root load, path submit, invalid path, empty object rendering, limit changes, "Other Objects" calculation, slice navigation, back path calculation, metadata for KEY and non-KEY paths, quota append behavior, and request cancellation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/diskUsage/diskUsage.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/constants/heatmapConstants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/constants/heatmapConstants.tsx

Purpose: Legacy heatmap constants module.

Important APIs/types/functions: Exports `TIME_PERIODS = ['24H','7D','90D']`, `ENTITY_TYPES = ['key','bucket','volume']`, and `ROOT_PATH = '/'`.

Control flow: Constant-only module; no logic.

State and persistence: No state. Arrays are mutable at runtime despite TypeScript annotations.

Dependencies and integration points: Imported by legacy heatmap page for default state and menu keys. Values must match backend accepted `startDate` period strings and `entityType` query values.

Risks: Backend enum/period changes require updating this module and any v2 counterpart constants. Mutable arrays can be altered by consumers unless treated read-only by convention.

Test signals: Heatmap menu tests should verify all constants appear in the UI and are accepted by request construction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/constants/heatmapConstants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/heatMapConfiguration.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/heatMapConfiguration.tsx

Purpose: Legacy AG Charts treemap configuration component for Heatmap data.

Important APIs/types/functions: Class component `HeatMapConfiguration` accepts `data`, `onClick`, and `colorScheme`; builds `AgChartsReact` options in constructor; defines `tooltipContent` for size/access/entity details.

Control flow: Constructor snapshots props into chart options. The treemap series uses `labelKey='label'`, `sizeKey='normalizedSize'`, `colorKey='color'`, a fixed color domain/range, custom tooltip renderer, and `nodeClick` listener. Clicking a non-leaf/group node with a `path` calls `props.onClick(path)`; leaf nodes with a truthy `color` do not trigger fetches.

State and persistence: Stores chart `options` in component state once. It does not update options if props change after construction unless remounted.

Dependencies and integration points: Depends on `ag-charts-react` and shared `byteToSize`. Used by legacy heatmap page after that page mutates API responses with `normalizedSize`.

Risks: Prop changes to `data` or `colorScheme` may not refresh the chart because options are initialized only in the constructor. The click logic treats falsy `color` as non-leaf; a leaf with color `0` may be misclassified. Tooltip content builds HTML strings from labels without escaping.

Test signals: Tests should cover initial render options, tooltip content for child and root nodes, click behavior for group versus leaf nodes including color `0`, and response to prop changes if component is refactored.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/heatMapConfiguration.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/heatmap.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/heatmap.tsx

Purpose: Legacy class-component Heatmap page. It fetches read-access data, normalizes node sizes, and renders an AG Charts treemap with path/entity/date filters.

Important APIs/types/functions: Defines heatmap response/state interfaces, module-level `minSize`/`maxSize`, `colourScheme`, and class methods `handleChange`, `handleSubmit`, `updateTreeMap`, `updateTreemapParent`, `disabledDate`, `resetInputpath`, `minmax`, `updateSize`, and `normalize`. Uses `AxiosGetHelper('/api/v1/heatmap/readaccess?...')`, `HeatMapConfiguration`, constants, Ant Design menus/date picker/result, and `showDataFetchError`.

Control flow: Mount fetches root/key/24H data. Filter changes call `updateTreeMap`, which sets loading, builds the query string, fetches data, computes min/max leaf sizes via `minmax`, recursively adds `normalizedSize`, and stores `treeResponse`. Fetch errors reset input/entity/date to empty strings, set endpoint failure, and mark Heatmap disabled on 404. Clicking a parent node updates the path and refetches. Render switches among loading, disabled, endpoint-failed, treemap, and no-data states.

State and persistence: Local state tracks loading, response, input path validity/help, entity type, date, endpoint failure, and Heatmap-enabled flag from route location state. Module globals hold min/max and cancellation controller. No persisted storage.

Dependencies and integration points: Integrates with the heatmap read-access endpoint, route location state from whatever page links to Heatmap, AG Charts configuration component, and backend-accepted time/entity constants.

Risks: Query params are not URL-encoded. `updateTreeMap` accepts `date: string` but state stores `string | number`. Catch block assumes `error.response.status`, which can fail for cancellation/network errors without response. `minmax` and `updateSize` mutate response data and use module-level bounds. Reset button only changes input path and does not refetch root immediately. Component reads `this.props.location` although props are typed generically.

Test signals: Tests should cover initial fetch, successful normalization, 404 disabled state, non-404 endpoint failure, filter/date changes, custom date restrictions, path validation, parent click refetch, cancellation on unmount, and no-data rendering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/heatMap/heatmap.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/insights/insights.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/insights/insights.tsx

Purpose: Legacy class-component Insights page that visualizes file-size and container-size distributions with ECharts and volume/bucket filters.

Important APIs/types/functions: Uses `PromiseAllSettledGetHelper` to fetch `/api/v1/utilization/fileCount` and `/api/v1/utilization/containerCount`, `MultiSelect`, `EChart`, and ECharts `graphic` overlays. Key methods are `handleVolumeChange`, `handleBucketChange`, `updatePlotData`, `componentDidMount`, and `componentWillUnmount`.

Control flow: Mount fetches both endpoints using all-settled semantics. Rejected file/container calls are converted into per-chart error overlays unless cancellation is detected. File counts build `volumeBucketMap` and volume options; default selection is all volumes. `updatePlotData` filters file counts by selected volumes/buckets, aggregates counts by size bucket, sorts by numeric size, formats lower/upper size ranges, aggregates container counts, and builds bar/pie chart options.

State and persistence: Local state holds loading, raw responses, ECharts options, volume/bucket maps and selections, bucket dropdown disabled state, and per-chart error strings. A module-level cancellation controller is aborted on unmount. No persistence.

Dependencies and integration points: Integrates with Recon utilization endpoints, legacy multi-select component, ECharts wrapper, `filesize`, Ant Design Tabs/Grid, and shared error notifications.

Risks: Placeholder fallback uses `fileSize: '0'` as a string despite the interface requiring number. All-settled error handling depends on string matching `CanceledError`. `graphic` overlay uses `fill: 'rgba(256, 256, 256, 0.5)'`, an out-of-range RGB value. Volume all-selection logic is subtle when exactly one real volume and the `*` sentinel coexist.

Test signals: Tests should cover both endpoints success, one endpoint failure with chart overlay, cancellation, all-volume/all-bucket selection, single-volume bucket enablement, multi-volume bucket disablement, sorted size labels, and empty data messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/insights/insights.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/insights/om/om.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/insights/om/om.tsx

Purpose: Legacy OM DB Insights page. It provides tabbed tables for container mismatch, open keys, delete-pending keys, deleted-container keys, and delete-pending directories, with shared limit selection and expandable key details.

Important APIs/types/functions: Defines column sets for mismatch, open keys, pending keys, deleted keys, pending dirs, and expanded container keys. Uses `AxiosGetHelper` for `/api/v1/containers/mismatch`, `/api/v1/keys/open`, `/api/v1/keys/deletePending`, `/api/v1/containers/mismatch/deleted`, `/api/v1/keys/deletePending/dirs`, and `/api/v1/containers/{id}/keys`. Key methods include `addexistAtColumn`, `handleExistsAtChange`, `addfsoNonfsoKeyColumn`, `handlefsoNonfsoMenuChange`, `_loadData`, fetch methods for each tab, `expandedKey`, `changeTab`, row expansion methods, column-search builders, and limit handlers.

Control flow: Constructor mutates module-level column arrays to add dropdown filter columns and initializes active tab from route state. `_loadData` dispatches to the fetch method matching the current tab. Each fetch cancels other outstanding tab requests, sets loading, calls its endpoint with selected limit/filter flags, and stores tab-specific data. Tab changes reset data, filters, expanded rows, and limit, then fetch the new tab. Container rows fetch keys on expansion. Delete-pending key groups are flattened for summary rows and use a module-level `keysPendingExpanded` array for expansion detail.

State and persistence: Local state stores tab data arrays, expanded rows, current filters, active tab, FSO flags, and selected limit. Module-level cancellation controllers, mutable columns, and `keysPendingExpanded` are shared across instances. No persistent storage.

Dependencies and integration points: Integrates with multiple Recon OM/SCM consistency endpoints, legacy `ColumnSearch`, `CreatableSelect`, Ant Design Table/Tabs/Dropdown/Tooltip, and v2 `ReplicationInfo` for open-key replication rendering.

Risks: `fetchMismatchContainers` appears to set `mismatchContainers` to `[]` when `containerDiscrepancyInfo` exists because of `response?.data?.containerDiscrepancyInfo && []`, likely dropping real mismatch data. Column arrays are mutated at module scope. Custom limit validation uses `parseInt` truthiness. Many props are typed generically while reading `props.location.state`. Multiple cancellation controllers are manually coordinated. `keysPendingExpanded` is global and can become stale across instances/tests.

Test signals: Tests should cover each tab's endpoint and data mapping, route-state initial tab, exists-at and FSO/non-FSO filters, limit changes and custom limits, mismatch data mapping bug, delete-pending aggregation/expansion, container key expansion success/failure, cancellation when switching tabs, and searchable columns.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/insights/om/om.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/missingContainers/missingContainers.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/missingContainers/missingContainers.tsx

Purpose: Legacy Containers page focused on unhealthy containers. It displays Missing, Under-Replicated, Over-Replicated, and Mis-Replicated tabs with cursor-style pagination and expandable container keys.

Important APIs/types/functions: Defines unhealthy container/key response interfaces, key and container column sets, `IMissingContainersState`, and class methods `fetchUnhealthyContainers`, `onRowExpandClick`, `expandedRowRender`, `onShowSizeChange`, `searchColumn`, `fetchPreviousRecords`, `fetchNextRecords`, `itemRender`, and `changeTab`. Uses `/api/v1/containers/unhealthy/{state}?limit=...&minContainerId=...` or `maxContainerId=...`, `/api/v1/containers/{containerID}/keys`, `ColumnSearch`, and `cancelRequests`.

Control flow: Mount selects tab `1`, which maps to `MISSING` and fetches the first page. Tab changes reset data/counts/cursors/expanded rows and fetch the new state. Pagination next/prev uses cursor keys from the previous response. Page size changes reset `lastSeenKey` to `firstSeenKey - 1` then fetch next records. Expanding a row stores a loading row state, fetches keys, and renders an inner Ant Design table.

State and persistence: Local state stores loading, current container rows, count totals for all unhealthy states, expanded row data, current unhealthy state, page size, and first/last cursor keys. Two module-level abort controllers track container and row-expansion requests. No persistence.

Dependencies and integration points: Integrates with Recon unhealthy container and container key endpoints, Ant Design Table/Tabs/Tooltip, React Router `Link` for pagination controls, `filesize` for key sizes, and shared time formatting.

Risks: `IContainerResponse.unhealthySince` is typed as string but rendered/sorted as number. Cursor pagination does not track disabled prev/next states, so users can request invalid ranges. Aborting row expansion on collapse cancels the single global expansion controller, which can affect another expanded row. Count totals are reset on tab switch and repopulated from each endpoint response; if the endpoint omits cross-counts, labels can disappear.

Test signals: Tests should cover all tab state mappings, first/next/previous cursor URLs, page-size changes, row expansion success/error/collapse cancellation, count label rendering, searchable container ID column, and empty response cursor preservation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/missingContainers/missingContainers.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/notFound/notFound.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/notFound/notFound.tsx

Purpose: Minimal legacy 404 component.

Important APIs/types/functions: Exports `NotFound: React.FC`, rendering a `page-header` with `404 Page Not Found :(`.

Control flow: No branching or interaction; it only renders static markup.

State and persistence: Stateless and side-effect free.

Dependencies and integration points: Used by the legacy route layer or app shell as a fallback page. Depends only on React and existing CSS for `page-header`.

Risks: No navigation action, explanatory text, or route recovery option is provided. The legacy and v2 404 pages have different UX and export styles.

Test signals: Simple render test should assert the 404 message is visible.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/views/notFound/notFound.tsx -->
