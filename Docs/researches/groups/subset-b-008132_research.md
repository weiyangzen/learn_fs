# subset-b-008132 research

Grouped research for Recon v2 React components, hooks, constants, assistant UI, capacity pages, containers, buckets, and datanodes. Each section preserves the original source path in its title and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/nuPieChart.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/nuPieChart.tsx

Purpose: Renders the namespace-usage pie chart for a path, converting Recon namespace usage responses into ECharts pie slices with an optional synthetic `Other Objects` slice.

Important APIs, types, and functions: Exports `NUPieChart`. Props include `path`, `limit`, `size`, `subPaths`, `subPathCount`, `sizeWithReplica`, and `loading`. Local helpers are `getSubpathSize`, `updatePieData`, and `handleLegendChange`.

Control flow: The component derives visible subpaths, slices to the requested limit, computes percentages against total path size, inflates positive pie values by `MIN_BLOCK_SIZE` for visibility, and sends an `option` object to `EChart`. A legend-selection event recomputes the subtotal shown under the chart.

State and persistence behavior: Stores only `subpathSize` in React state. It recalculates on `subPaths` or `limit` changes and memoizes pie data from path/subpath/limit inputs. There is no persistent browser storage.

Dependencies: Depends on the local `EChart` wrapper, `byteToSize`, and the `NUSubpath` namespace-usage type.

Integration points: Used by the namespace-usage page to visualize children of the currently selected volume, bucket, directory, or key path.

Risks and edge cases: `getSubpathSize` takes an argument but tests `subPaths.length` from props, so stale closure behavior can affect filtered legend totals. `sizeWithReplica - remainingSize` looks suspicious for the synthetic replica size. Tooltip HTML is assembled manually and chart labels depend on path splitting.

Test signals: Cover empty paths, zero size, more subpaths than limit, exactly max-limit responses, key versus directory labels, legend-selection subtotal updates, and `sizeWithReplica === -1` handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/nuPieChart.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/search/search.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/search/search.tsx

Purpose: Provides a compact Ant Design search input with an optional column selector prefix for Recon table filters.

Important APIs, types, and functions: Exports `Search`. Props include disabled state, current search column, input value, optional `Option[]` search choices, `onSearchChange`, and selector `onChange`.

Control flow: If `searchColumn` is provided, the component renders an AntD `Select` in `addonBefore`; otherwise it renders a plain `Input`. Search text is controlled by the parent and `allowClear` is enabled.

State and persistence behavior: Stateless controlled component; all search text and selected column persistence live in parent pages.

Dependencies: Uses Ant Design `Input` and `Select`, `DownOutlined`, and the shared single-select `Option` shape.

Integration points: Shared by Buckets, Containers, Datanodes, Pipelines/Volumes-style pages, and several insights tables.

Risks and edge cases: The select uses `defaultValue`, not `value`, so parent changes to `searchColumn` after mount may not be reflected. The dropdown arrow is hidden for single-option selectors, and handlers default to no-op, which can hide wiring mistakes.

Test signals: Verify controlled input clearing, disabled propagation, one-option versus multi-option suffix icon behavior, and changing search column resets parent search where expected.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/search/search.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/columnTag.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/columnTag.tsx

Purpose: Legacy/parked helper that renders closable selected-column tags into an external container using a React portal.

Important APIs, types, and functions: Exports `ColumnTag` and `TagProps` with `label`, `closable`, `tagRef`, and `onClose`.

Control flow: If `tagRef.current` exists, it creates an AntD `Tag` portal. Mouse down is prevented to avoid accidental text selection while closing a tag.

State and persistence behavior: No internal state and no persistence. Rendering depends entirely on the external DOM ref.

Dependencies: Uses Ant Design `Tag` and `createPortal` from `react-dom`.

Integration points: Kept for possible future column-filter display; current comments say the design no longer uses these tags.

Risks and edge cases: Defaulting `tagRef` to `null` conflicts with the declared `React.RefObject` type. Because it portals into arbitrary DOM, lifecycle timing and missing refs cause silent no-render behavior.

Test signals: If revived, test absent ref, close callback label propagation, mouse-down prevention, and cleanup when the portal target unmounts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/columnTag.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/multiSelect.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/multiSelect.tsx

Purpose: Wraps `react-select` as Recon's multi-column/filter selector with checkboxes, fixed non-removable options, optional embedded search, and optional select-all behavior.

Important APIs, types, and functions: Exports `MultiSelect` and re-exports `Option`. Props extend `react-select` multi props and add `selected`, `fixedColumn`, `columnLength`, `showSearch`, `showSelectAll`, `onChange`, and `onTagClose`.

Control flow: Normalizes fixed columns, filters selectable options by local search, renders a custom value container showing selected counts, and delegates menu rendering to `MultiSelectMenuList`. Selection always re-adds fixed options before notifying the parent.

State and persistence behavior: Tracks local `searchTerm` and menu open state; refs track search interaction and the containing DOM node. Selected options are controlled by the parent.

Dependencies: Uses `react-select`, shared `selectStyles`, and the sibling custom menu/input components.

Integration points: Used by Buckets, Containers, Datanodes, Pipelines, Volumes, and plots to control visible table columns or high-cardinality filters.

Risks and edge cases: `filteredOptions` omits `selectableOptions` from its dependency list and uses `options` instead, which can be stale. DOM access to `document.body` assumes browser runtime. The value-container child-name check depends on react-select internals.

Test signals: Cover fixed columns surviving unselect-all, select-all including fixed options, search focus not closing the menu, option list updates after props change, disabled state, and portal rendering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/multiSelect.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/multiSelectMenuList.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/multiSelectMenuList.tsx

Purpose: Provides the custom `react-select` menu body used by `MultiSelect`, adding a search input and Select All/Unselect All row above options.

Important APIs, types, and functions: Exports `Option`, `MultiSelectInput`, and default `MultiSelectMenuList`. Reads extended data from `props.selectProps` rather than direct typed props.

Control flow: The input suppresses react-select blur while search is active. The menu computes `allSelected`, calls parent `customOnChange` with fixed plus selectable options, and closes/search-resets on outside blur or Escape.

State and persistence behavior: Only an input ref is local. Search term, menu open state, selected options, fixed options, and search-interaction ref are owned by `MultiSelect`.

Dependencies: Uses `react-select` `components` and raw inline styles.

Integration points: Tightly coupled to `MultiSelect`'s injected `selectProps` names and focus-management assumptions.

Risks and edge cases: Heavy `any` typing means missing selectProps fail at runtime. The 150ms blur timeout is race-prone. Checkbox `onChange={() => null}` relies on wrapper click handling for behavior.

Test signals: Exercise keyboard Escape, outside click while search is focused, Select All with zero selectable options, filtering plus select all, and fixed-option-only unselect behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/multiSelectMenuList.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/singleSelect.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/singleSelect.tsx

Purpose: Wraps `react-select` as a compact single-value selector with Recon styling and a custom value label prefix.

Important APIs, types, and functions: Exports `SingleSelect` and `Option`. Props extend non-multi `react-select` props and add `options`, `placeholder`, and `onChange`.

Control flow: Renders a non-clearable, non-searchable select. Custom `ValueContainer` displays `placeholder: selectedLabel` while preserving react-select's hidden dummy input child.

State and persistence behavior: Stateless controlled/defaulted select; selected value is managed by parent via react-select props.

Dependencies: Uses `react-select` and shared `selectStyles`.

Integration points: Used for limit selectors and similar single-choice controls across buckets and insights tables.

Risks and edge cases: Style type is cast from a multi-select `StylesConfig`, and the child-name check depends on react-select internals. Like other selectors it portals to `document.body`.

Test signals: Cover default value display, onChange value shape, empty selection rendering, disabled inherited props, and menu portal z-index with AntD tables.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/select/singleSelect.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/storageBar/storageBar.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/storageBar/storageBar.tsx

Purpose: Renders Ozone datanode storage usage as an Ant Design progress bar with a detailed filesystem/Ozone tooltip.

Important APIs, types, and functions: Exports `StorageBar`. Props combine `DatanodeStorageReport` with optional `showMeta` and `strokeWidth`.

Control flow: Detects whether filesystem-capacity fields are available, computes filesystem used if absent, builds a tooltip table, computes Ozone used percentage from `capacity - remaining`, and colors the bar red above 80 percent.

State and persistence behavior: Pure render component with no React state or persistence.

Dependencies: Uses Ant Design `Progress` and `Tooltip`, `filesize`, local `getCapacityPercent`, and storage-report types.

Integration points: Used by `DatanodesTable` to render each datanode's capacity column.

Risks and edge cases: `reserved` is cast to number when filesystem view exists and may display undefined as a size. Capacity math assumes `remaining` is sane and does not clamp negative/over-100 values itself.

Test signals: Test missing filesystem fields, zero capacity, threshold at 80/81 percent, showMeta text, committed values, and tooltip table contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/storageBar/storageBar.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/bucketsTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/bucketsTable.tsx

Purpose: Displays bucket inventory rows with sorting, storage/layout filters, quota bars, and a dynamic ACL action column.

Important APIs, types, and functions: Exports `BucketsTable` and mutable `COLUMNS`. Helpers render versioning icons, storage-type icons, and layout tags.

Control flow: On mount the table appends or replaces an ACL column that captures the current `handleAclClick`. It filters visible columns from parent-selected options and filters rows by the selected search column before rendering AntD `Table`.

State and persistence behavior: No own state, but it mutates module-level `COLUMNS` and the `selectedColumns` prop array in its mount effect.

Dependencies: Uses AntD table/tag/icons, `moment`, `QuotaBar`, `nullAwareLocaleCompare`, and bucket type constants.

Integration points: Consumed by `pages/buckets/buckets.tsx`; ACL links open `AclPanel` in the parent.

Risks and edge cases: Mutating exported `COLUMNS` and props can duplicate/stale action columns across mounts or tests. `bucket[searchColumn].includes` assumes all searchable fields are strings. ACL effect has an empty dependency list despite using props.

Test signals: Cover ACL callback after remount, selected-column filtering with fixed columns, storage/layout filters, search by name and volume, null owner sorting, and quota rendering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/bucketsTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/containersTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/containersTable.tsx

Purpose: Displays unhealthy/quasi-closed containers with manual cursor pagination and expandable key listings per container.

Important APIs, types, and functions: Exports `ContainerTable` and `COLUMNS`. Props include selected columns, expansion state/setter, search config, page navigation callbacks, page size, and optional unhealthy-since title.

Control flow: Filters columns and rows, maps selected container expansion to `/api/v1/containers/{id}/keys` via `fetchData`, stores fetched key rows in parent-owned `expandedRow`, renders nested key table, and draws explicit previous/next buttons.

State and persistence behavior: Expansion data lives in parent state; this component triggers updates and displays per-row loading. No persistence.

Dependencies: Uses AntD table, popover, select, buttons, `filesize`, moment utils, `fetchData`, and container types.

Integration points: Shared by the Containers page for five unhealthy tabs plus the quasi-closed tab.

Risks and edge cases: Expanded row loading is not set true before fetch in this component, so parent initialization must provide it. Search assumes string `pipelineID` or numeric `containerID`. Nested key table pagination does not use server-side paging despite total count.

Test signals: Cover row expansion success/error, manual next/previous boundaries, page-size changes from parent, search by ID/pipeline, checksum popover rendering, and alternate title for quasi-closed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/containersTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/datanodesTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/datanodesTable.tsx

Purpose: Displays datanode inventory, health/op-state, storage usage, pipeline membership, and dead-node row selection for removal.

Important APIs, types, and functions: Exports `DatanodesTable` and mutable `COLUMNS`. Local render helpers map health/op states to icons and pipeline popovers.

Control flow: Filters columns by parent selection, filters rows by selected search field, updates a module-level `decommissioningUuids` from props, and uses AntD rowSelection while disabling checkboxes for non-DEAD nodes.

State and persistence behavior: No local state, but uses module-level `decommissioningUuids` for UUID-column rendering.

Dependencies: Uses AntD table/popover/tooltip/icons, `StorageBar`, `DecommissionSummary`, `ReplicationIcon`, moment utilities, and datanode/pipeline types.

Integration points: Consumed by `pages/datanodes/datanodes.tsx`, which supplies decommission data, selected rows, and removal workflow.

Risks and edge cases: Module global `decommissioningUuids` can leak between component instances/tests. `isSelectable` returns `record.state !== 'DEAD' && true`, which is semantically a disabled predicate but awkward. Search assumes all fields have `includes`.

Test signals: Cover dead-only selectable behavior, decommission summary display, pipeline leader icon, storage report rendering, search by hostname/uuid/version/revision, and test-id row attributes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/datanodesTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/containerMismatchTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/containerMismatchTable.tsx

Purpose: Shows containers that exist in OM or SCM but are missing from the other service, with limit, search, and existence-side filter controls.

Important APIs, types, and functions: Exports `ContainerMismatchTable`. Props provide table pagination, current limit, limit handler, expanded row renderer, and expand callback.

Control flow: Builds `/api/v1/containers/mismatch?limit=...&missingIn=...`, debounces container-ID search, refetches when limit or missing side changes, and renders expandable rows supplied by the parent.

State and persistence behavior: Local `data`, `searchTerm`, and `missingIn`. API loading/error/data is held by `useApiData`.

Dependencies: Uses AntD dropdown/menu/popover/table/tooltip, `SingleSelect`, `Search`, `useDebounce`, `useApiData`, and insights types.

Integration points: Used inside the Insights page where expanded rows typically show mismatched keys.

Risks and edge cases: The menu label says `Exists At` while state variable is `missingIn`, and the click handler inverses the clicked key. `initialFetch: false` plus refetch effect depends on hook behavior and can produce rejected promises without local catch.

Test signals: Test OM/SCM toggle URL semantics, limit changes, expansion callbacks, empty-data disabled search, debounced ID filtering, and error toast path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/containerMismatchTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletePendingDirsTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletePendingDirsTable.tsx

Purpose: Displays OM directories pending deletion with limit selection and debounced name search.

Important APIs, types, and functions: Exports `DeletePendingDirTable`. Props include shared pagination, selected limit, and limit-change handler.

Control flow: Uses `/api/v1/keys/deletePending/dirs?limit=...`, copies `deletedDirInfo` into local rows, refetches on limit changes, filters by directory key, and renders size/time/path columns.

State and persistence behavior: Local `data` and `searchTerm`; API state is from `useApiData` with no persistence.

Dependencies: Uses AntD table, shared `Search`, `SingleSelect`, `LIMIT_OPTIONS`, `useDebounce`, `useApiData`, `byteToSize`, and moment utils.

Integration points: Part of the Insights pending-deletion views.

Risks and edge cases: `initialFetch: false` means the refetch effect owns initial loading. Row key is only `key`, which may collide across paths. Search only checks `key`, not full path.

Test signals: Cover limit refetch, duplicate directory names under different paths, zero/large sizes, timestamp formatting, and disabled search when no rows exist.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletePendingDirsTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletePendingKeysTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletePendingKeysTable.tsx

Purpose: Aggregates OM delete-pending key entries by key name and provides expandable details for individual pending-key versions.

Important APIs, types, and functions: Exports `DeletePendingKeysTable`. Defines aggregate row and expanded-list helper types internally.

Control flow: Fetches `/api/v1/keys/deletePending?limit=...`, reduces each `omKeyInfoList` to total data size and count, stores original lists separately, filters aggregate rows by path, and renders `ExpandedPendingKeysTable` for matching rows.

State and persistence behavior: Local aggregate `data`, `searchTerm`, and `expandedDeletePendingKeys`. API state is managed by `useApiData`.

Dependencies: Uses AntD table, `Search`, `SingleSelect`, `ExpandedPendingKeysTable`, `byteToSize`, `useDebounce`, and insights types.

Integration points: Used by Insights pending deletion tabs.

Risks and edge cases: The reducer assumes `omKeyInfoList[0]` exists and will fail on empty lists. Expansion matches only `keyName`, so duplicate key names can merge details. Row key is also `keyName`.

Test signals: Cover empty `omKeyInfoList`, duplicate keys in different buckets, aggregate size/count correctness, limit refetch, and expansion detail filtering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletePendingKeysTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletedContainerKeysTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletedContainerKeysTable.tsx

Purpose: Shows containers with deleted keys for mismatch/deleted-container insights and delegates expanded key details to the parent.

Important APIs, types, and functions: Exports `DeletedContainerKeysTable`. Props include limit, pagination, limit-change handler, `onRowExpand`, and `expandedRowRender`.

Control flow: Fetches `/api/v1/containers/mismatch/deleted?limit=...`, stores `containers`, debounces ID search, and renders an expandable AntD table with pipelines listed inline.

State and persistence behavior: Local `data` and `searchTerm`; API state comes from `useApiData`.

Dependencies: Uses AntD table, `Search`, `SingleSelect`, `LIMIT_OPTIONS`, `useDebounce`, `useApiData`, and insights container types.

Integration points: Part of Insights deleted-container key drill-down flow.

Risks and edge cases: Row key is `containerId`, which is good, but pipeline rendering assumes nested `pipeline.id.id`. Search only filters ID and not pipeline. Initial fetch depends on the limit effect.

Test signals: Cover limit refetch, empty pipelines, malformed pipeline IDs, expansion callback, debounced search, and API error handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/deletedContainerKeysTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/expandedKeyTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/expandedKeyTable.tsx

Purpose: Nested table for mismatch key details under an expanded container row.

Important APIs, types, and functions: Exports `ExpandedKeyTable`. Props are `loading`, mismatch key `data`, and shared `paginationConfig`.

Control flow: Formats volume, bucket, key, IEC size, creation time, and modification time into a plain AntD table.

State and persistence behavior: Stateless render component with no persistence.

Dependencies: Uses AntD table, `moment`, `filesize`, and `MismatchKeys` type.

Integration points: Used as expanded-row content by container mismatch/deleted-container insights.

Risks and edge cases: Row key `uid` must be supplied by the API; if absent, React row identity degrades. `moment(date)` assumes parseable API strings.

Test signals: Cover loading state, missing/duplicate UID, invalid dates, zero data size, and pagination handoff.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/expandedKeyTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/expandedPendingKeysTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/expandedPendingKeysTable.tsx

Purpose: Nested table for individual delete-pending key records under an aggregate pending-key row.

Important APIs, types, and functions: Exports `ExpandedPendingKeysTable`. Props include `DeletePendingKey[]` data and pagination config.

Control flow: Renders data size, replicated size, creation time, and modification time. Positive sizes are converted to human-readable strings while zero/negative values display raw.

State and persistence behavior: Stateless.

Dependencies: Uses AntD table, `byteToSize`, `getFormattedTime`, and insights types.

Integration points: Used by `DeletePendingKeysTable` as expanded-row detail content.

Risks and edge cases: Row key is `dataSize`, which can collide for multiple records with the same size. The render functions assign to their parameters and mix numeric/string return shapes.

Test signals: Cover duplicate sizes, zero/negative sizes, timestamp formatting, and parent pagination reuse.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/expandedPendingKeysTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/openKeysTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/openKeysTable.tsx

Purpose: Displays open keys, switching between FSO and Non-FSO result sets, with limit selection and debounced path search.

Important APIs, types, and functions: Exports `OpenKeysTable`. Props include selected limit, pagination config, and limit-change handler.

Control flow: Builds `/api/v1/keys/open?includeFso=...&includeNonFso=...&limit=...`, maps the active result array to rows with a `type`, filters by `path`, and renders replication type/factor/EC details.

State and persistence behavior: Local `isFso` and `searchTerm`; API state is from `useApiData`, which refetches when the URL changes.

Dependencies: Uses AntD dropdown/menu/table, `Search`, `SingleSelect`, `useDebounce`, `useApiData`, byte/time formatting helpers, and insights types.

Integration points: Insights open-key tab.

Risks and edge cases: Only one of FSO or Non-FSO is fetched at a time; switching type discards the other view. Row key is `key`, which may not be globally unique. Search is path-only.

Test signals: Cover FSO/Non-FSO toggle URLs, RATIS versus EC replication rendering, limit changes, duplicate keys, and long path search.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/insights/openKeysTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/pipelinesTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/pipelinesTable.tsx

Purpose: Displays pipeline inventory with replication, status filters, datanode membership, leader metrics, and duration fields.

Important APIs, types, and functions: Exports `PipelinesTable` and `COLUMNS`. Includes a local `SummaryDatanodeDetails` type until datanode types are shared.

Control flow: Filters columns from parent-selected options, filters rows by `pipelineId` search text, and renders AntD table with tooltips for datanode UUIDs and metrics descriptions.

State and persistence behavior: Stateless.

Dependencies: Uses AntD table/tooltip/icons, `ReplicationIcon`, moment duration utilities, and pipeline types.

Integration points: Consumed by the Pipelines page and receives data from the Recon pipelines API.

Risks and edge cases: Datanode list items lack explicit React keys. Search is only by pipeline ID. The TODO local type can drift from backend/shared datanode type.

Test signals: Cover status filters, replication icon variations, missing leader metrics showing NA, datanode UUID tooltips, selected-column filtering, and row test IDs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/pipelinesTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/volumesTable.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/volumesTable.tsx

Purpose: Displays volume inventory with quotas, namespace capacity, navigation to buckets, and a dynamic ACL action column.

Important APIs, types, and functions: Exports `VolumesTable` and mutable `COLUMNS`; props come from `VolumesTableProps`.

Control flow: On mount appends/replaces an Actions column that links to `/Buckets?volume=...` and calls parent ACL handler. It filters selected columns and rows by the requested search column.

State and persistence behavior: No local state, but mutates module-level `COLUMNS` and the `selectedColumns` prop array.

Dependencies: Uses AntD table, `QuotaBar`, `byteToSize`, `moment`, and `Link` from react-router.

Integration points: Consumed by the Volumes page; the generated bucket link seeds the Buckets page volume filter.

Risks and edge cases: Mutable columns/prop mutation can leak across mounts. Search assumes selected field supports `includes`. Action-column effect does not update when `handleAclClick` changes.

Test signals: Cover action links, ACL callback after remount, quota NA behavior for -1, selected columns, search by owner/admin/volume, and duplicate mount behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/tables/volumesTable.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/acl.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/acl.constants.tsx

Purpose: Defines Ant Design color mappings for ACL identity types and rights.

Important APIs, types, and functions: Exports `AclIdColorMap` and `AclRightsColorMap` objects.

Control flow: No control flow; consumers look up a color by ACL enum-like string.

State and persistence behavior: Static constants only.

Dependencies: No imports.

Integration points: Used by ACL drawer/panel rendering to color identity and right tags.

Risks and edge cases: Maps are untyped, so new backend ACL strings silently produce undefined/default colors. Color names assume AntD tag palette support.

Test signals: Validate all known ACL identity/right enums are present and unknown values fall back safely in consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/acl.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/breadcrumbs.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/breadcrumbs.constants.tsx

Purpose: Maps Recon v2 route paths to breadcrumb display names.

Important APIs, types, and functions: Exports `breadcrumbNameMap` typed as path string to display string.

Control flow: Static lookup only.

State and persistence behavior: No state or persistence.

Dependencies: No imports.

Integration points: Consumed by layout/navigation breadcrumb components and includes `/Assistant` as `Recon AI`.

Risks and edge cases: Route strings must stay synchronized with `routes-v2.tsx`; missing dynamic paths or renamed routes produce blank breadcrumbs.

Test signals: Check every top-level v2 route has a breadcrumb and renamed routes update this map.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/breadcrumbs.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/capacity.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/capacity.constants.tsx

Purpose: Provides typed default response objects for capacity and pending-deletion API hooks.

Important APIs, types, and functions: Exports `DEFAULT_CAPACITY_UTILIZATION`, `DEFAULT_SCM_PENDING_DELETION`, `DEFAULT_OM_PENDING_DELETION`, and `DEFAULT_DN_PENDING_DELETION`.

Control flow: No runtime flow; values seed `useApiData` before network responses arrive or after failed requests.

State and persistence behavior: Static defaults only.

Dependencies: Imports capacity response types.

Integration points: Used by the Capacity page to avoid null checks when rendering cluster/service/datanode cards.

Risks and edge cases: Defaults can mask absent API fields as real zero values. The DN default includes a synthetic unknown host that can appear in selectors if not replaced by data.

Test signals: Ensure UI handles defaults without showing misleading unknown hosts after successful empty responses and updates when response fields are added.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/capacity.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/chatbot.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/chatbot.constants.tsx

Purpose: Centralizes Recon AI endpoints, provider/model classification, provider-specific error messages, loading-stage text, and seed prompts.

Important APIs, types, and functions: Exports `CHATBOT_ENDPOINTS`, `DEFAULT_MODEL_SENTINEL`, `PROVIDER_LABELS`, `getProviderForModel`, `resolveRequestProvider`, `isMaskedLlmProcessingError`, `getLlmProviderFailureMessage`, `LOADING_STAGES`, and `SEED_PROMPTS`.

Control flow: Model names are classified by lowercase prefixes. Error handling distinguishes generic/masked LLM failures from backend errors and returns provider-specific remediation text plus a server-log hint.

State and persistence behavior: Static constants and pure helpers only.

Dependencies: No imports.

Integration points: Used by Assistant, ModelPicker, LoadingIndicator, EmptyState, and `useChat`.

Risks and edge cases: Provider detection is prefix-based and misses newer model naming schemes unless updated. Error masking depends on backend exception text. Seed prompts are UI content coupled to backend query support.

Test signals: Cover model/provider classification, sentinel handling, masked error variants, provider failure message text, loading-stage thresholds, and seed prompt rendering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/chatbot.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/description.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/description.constants.tsx

Purpose: Defines reusable quota description labels with inline Ant Design popovers.

Important APIs, types, and functions: Exports JSX constants `QuotaInNamespace`, `QuotaUsed`, and `QuotaAllowed`.

Control flow: Each constant renders label text and an `InfoCircleOutlined` inside an AntD `Popover` with explanatory content.

State and persistence behavior: Static JSX constants only.

Dependencies: Uses React, AntD `Popover`, and `InfoCircleOutlined`.

Integration points: Consumed by quota-related table/card headers in Recon UI.

Risks and edge cases: JSX constants are created at module load and cannot be parameterized or localized. Text contains a minor grammar issue (`it's quota`).

Test signals: Snapshot/popover tests for labels, placement, icon class, and consumer rendering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/description.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/heatmap.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/heatmap.constants.tsx

Purpose: Defines heatmap palette and allowed query dimensions for the Heatmap page.

Important APIs, types, and functions: Exports `colourScheme`, `TIME_PERIODS`, `ENTITY_TYPES`, and `ROOT_PATH`.

Control flow: Static constants only.

State and persistence behavior: No state.

Dependencies: No imports.

Integration points: Heatmap page and API query builders use these choices for time period, entity type, and root path.

Risks and edge cases: Arrays are plain strings rather than literal union types, so invalid consumer values are not prevented. Palette length must match heatmap bucket assumptions.

Test signals: Validate Heatmap controls only use these values and palette bucket count matches chart scale.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/heatmap.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/limit.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/limit.constants.tsx

Purpose: Defines shared row-limit options for select controls.

Important APIs, types, and functions: Exports `LIMIT_OPTIONS` as `Option[]` with 1000, 5000, 10000, and 20000 values.

Control flow: Static list only.

State and persistence behavior: No state.

Dependencies: Imports `Option` from `singleSelect`.

Integration points: Used by Buckets and Insights tables to build API `limit` query parameters.

Risks and edge cases: Option values are strings and must be parsed or accepted by APIs. Large defaults can be expensive for browser rendering and backend queries.

Test signals: Confirm consumers pass expected string values to APIs and handle each limit without pagination regressions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/limit.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/overview.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/overview.constants.tsx

Purpose: Provides typed default values for Overview and shared cluster summary responses.

Important APIs, types, and functions: Exports `DEFAULT_CLUSTER_STATE`, `DEFAULT_TASK_STATUS`, `DEFAULT_OPEN_KEYS_SUMMARY`, and `DEFAULT_DELETE_PENDING_KEYS_SUMMARY`.

Control flow: Static defaults seed `useApiData` and summary components before data arrives.

State and persistence behavior: No state.

Dependencies: Imports overview response types.

Integration points: Used by Overview and Containers page cluster-state hook.

Risks and edge cases: Zero defaults can be indistinguishable from an actual empty cluster unless paired with loading/error state. Service IDs default to `N/A`.

Test signals: Verify loading/error states do not present defaults as fresh data and new backend fields are added to defaults.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/overview.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/select.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/select.constants.tsx

Purpose: Centralizes `react-select` styling for Recon single and multi select controls.

Important APIs, types, and functions: Exports `selectStyles` as a `StylesConfig`.

Control flow: Style callbacks customize control border, option selected/active colors, menu shadow, placeholder color, hidden separator, and portal z-index.

State and persistence behavior: Static style object only.

Dependencies: Imports `StylesConfig` and the shared multi-select `Option` type.

Integration points: Used by `MultiSelect` and cast for `SingleSelect`.

Risks and edge cases: Typed for multi-select but reused for single-select. Uses hard-coded colors and z-index 9999, which can conflict with AntD modals/dropdowns.

Test signals: Visual regression for focused/selected/active states, portal stacking over tables/modals, and single-select compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/constants/select.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useAPIData.hook.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useAPIData.hook.ts

Purpose: Generic Axios-backed data hook and one-shot request helper for Recon v2 APIs.

Important APIs, types, and functions: Exports `HttpMethod`, `ApiState<T>`, `UseApiDataOptions`, `useApiData<T>`, and `fetchData<T>`.

Control flow: `useApiData` initializes state, optionally fetches GET URLs, cancels prior requests via `AbortController`, sends data as body or params by method, retries network/5xx failures with linear backoff, calls success/error callbacks, and resets to default data on final failure. `fetchData` performs one manual Axios request.

State and persistence behavior: Hook state includes data/loading/error/lastUpdated/success. Refs hold active abort controller, retry count, retry timer, and mounted marker. No browser persistence.

Dependencies: Uses React hooks and Axios.

Integration points: Core fetch primitive for most v2 pages, tables, Assistant health/models, and manual row expansion/export helpers.

Risks and edge cases: Retry branch rejects immediately while a retry is scheduled, so callers may see errors before final retry outcome. The effect depends only on URL and intentionally suppresses exhaustive deps. `mountedRef` can skip initial fetch when URL starts empty then changes depending on flow.

Test signals: Cover initialFetch true/false, URL changes, abort of prior request, GET params, non-GET body, retryable versus non-retryable errors, callbacks, reset/clearError, and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useAPIData.hook.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useAutoReload.hook.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useAutoReload.hook.tsx

Purpose: Reusable auto-refresh controller that starts/stops timeout-based polling and persists the enabled toggle in sessionStorage.

Important APIs, types, and functions: Exports `useAutoReload(refreshFunction, interval?)` returning `startPolling`, `stopPolling`, `isPolling`, and `handleAutoReloadToggle`.

Control flow: On mount it reads `sessionStorage.autoReloadEnabled` and starts polling unless explicitly false. Poll invokes the latest refresh function immediately and then schedules the next timeout, suppressing duplicate calls within 100ms.

State and persistence behavior: Tracks `isPolling` and interval value; refs hold timeout id, latest refresh function, and last call timestamp. Persists enabled/disabled state in `sessionStorage`.

Dependencies: Uses React hooks and `AUTO_RELOAD_INTERVAL_DEFAULT`.

Integration points: Used by Overview, Buckets, Containers, Datanodes, and Capacity pages with `AutoReloadPanel`.

Risks and edge cases: Uses `clearTimeout` on a numeric ref and browser `window.setTimeout`, so typing assumes DOM. `startPolling` immediately calls refresh, which can duplicate explicit mount fetches. Persisted toggle is global across pages.

Test signals: Cover default-on behavior, persisted false, interval changes, stop cleanup on unmount, duplicate-call guard, and page-specific refresh functions changing over time.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useAutoReload.hook.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useChat.hook.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useChat.hook.tsx

Purpose: Manages Recon AI chat message state, in-flight request lifecycle, elapsed timer, cancellation, persistence, and user-facing error normalization.

Important APIs, types, and functions: Exports `useChat` returning messages, in-flight state, elapsed seconds, error bubble, current query, `sendMessage`, `cancelRequest`, `clearMessages`, and `setCurrentQuery`.

Control flow: Loads messages from `sessionStorage`, appends a user message unless it duplicates the last user message, builds a chat request with optional provider/model, posts via `AxiosPostHelper`, appends assistant response, and maps HTTP 400/500/503/504 errors to display text. Abort cancels the request and timer.

State and persistence behavior: Persists `messages` under `recon_ai_messages`; local state tracks in-flight, elapsed seconds, error bubble, and current query. Refs hold abort controller, timer, and in-flight guard.

Dependencies: Uses `AxiosPostHelper`, Axios error helpers, chatbot types/constants, React hooks, and `crypto.randomUUID`.

Integration points: Consumed by `pages/assistant/assistant.tsx` and its Composer/MessageList components.

Risks and edge cases: Session storage JSON parse failures only log. Duplicate suppression can skip intentional repeated prompts after navigation. Error mapping depends on backend text and provider/model selection. `crypto.randomUUID` requires modern browser support.

Test signals: Cover persistence load/save/clear, duplicate user-message behavior, cancel path, timer cleanup, provider/model request body, status-specific error bubbles, masked LLM errors, and retry/regenerate flows.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useChat.hook.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useDebounce.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useDebounce.tsx

Purpose: Small generic debounce hook for delaying derived values such as search terms.

Important APIs, types, and functions: Exports `useDebounce<T>(value, timeout): T`.

Control flow: Initializes debounced value from input, schedules `setDebounceValue` after the requested timeout whenever value/timeout changes, and clears the timeout on cleanup.

State and persistence behavior: Local debounced value only; no persistence.

Dependencies: Uses React state/effect.

Integration points: Used by table search controls across Buckets, Containers, Datanodes, and Insights.

Risks and edge cases: No special handling for negative/zero timeout beyond native `setTimeout`. Frequent timeout changes reset pending updates.

Test signals: Use fake timers to verify delayed update, cleanup cancelling old timeout, generic object/string values, and timeout changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/hooks/useDebounce.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/assistant.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/assistant.tsx

Purpose: Top-level Recon AI page coordinating feature health, model loading, chat state, disabled states, and composer/message layout.

Important APIs, types, and functions: Exports default `Assistant` React component.

Control flow: Fetches chatbot health on mount, fetches models only when health says enabled and LLM client available, gates rendering through loading/disabled/not-configured states, wires prompt chips to current query, and supports retry/regenerate by finding prior user messages.

State and persistence behavior: Local `isHealthLoaded` and `isModelsLoaded`; chat state and persistence come from `useChat`; API state comes from `useApiData`.

Dependencies: Uses AntD Spin/Button/Tag/icons, chatbot constants/types, `useApiData`, `useChat`, and assistant subcomponents.

Integration points: Loaded from v2 routes at `/Assistant` and linked by the nav/breadcrumb constants.

Risks and edge cases: The models effect depends on the whole `healthData.data` object, so identity changes can refetch. Retrying uses the latest user message and may not remove prior failed assistant/error state. Health errors show disabled/not-configured UI using default data.

Test signals: Cover health disabled, not configured, enabled with models load, model-load error, new chat disabled during in-flight, prompt click, retry, regenerate, and loading gate timing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/assistant.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/Composer.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/Composer.tsx

Purpose: Input composer for Recon AI, including provider/model picker, textarea, send-on-enter, and stop button.

Important APIs, types, and functions: Exports default `Composer`. Props include send/cancel callbacks, in-flight flag, models, controlled current query, and setter.

Control flow: Tracks selected provider/model locally. Provider changes reset model. Enter without Shift sends; Shift+Enter inserts a newline. In-flight state disables input/model picker and swaps send for stop.

State and persistence behavior: Local selected provider/model. Query text is controlled by the parent/useChat.

Dependencies: Uses AntD `Input.TextArea` and `Button`, send/stop icons, and `ModelPicker`.

Integration points: Rendered by Assistant and calls `useChat.sendMessage`/`cancelRequest` through props.

Risks and edge cases: Selected provider/model are not persisted between chats. Sending does not clear `currentQuery` immediately; `useChat` clears it after success only. Keyboard handling may surprise IME composition users.

Test signals: Cover disabled in-flight state, provider reset clearing model, Enter versus Shift+Enter, empty-query disabled send, stop callback, and selected model/provider passed to `onSend`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/Composer.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/DisabledState.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/DisabledState.tsx

Purpose: Displays the disabled or not-configured Recon AI page state.

Important APIs, types, and functions: Exports `DisabledState` with `reason: 'disabled' | 'not-configured'`.

Control flow: Branches on reason and renders an AntD `Result` warning with corresponding title/subtitle.

State and persistence behavior: Stateless.

Dependencies: Uses AntD `Result`.

Integration points: Used by Assistant after health check when chatbot is disabled or no LLM client is available.

Risks and edge cases: Messages are static and administrator-oriented. No action link or config docs are provided.

Test signals: Snapshot both reasons and verify warning status/title/subtitle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/DisabledState.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/EmptyState.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/EmptyState.tsx

Purpose: Initial Recon AI empty chat screen with hero text and seed prompt chips.

Important APIs, types, and functions: Exports `EmptyState` with `onPromptClick(prompt)`.

Control flow: Maps `SEED_PROMPTS` to clickable chips, maps prompt icon identifiers to AntD icons, and calls the parent with the selected prompt text.

State and persistence behavior: Stateless.

Dependencies: Uses chatbot constants, AntD icons, and `ReconAIMark`.

Integration points: Shown by Assistant when there are no persisted messages.

Risks and edge cases: Clickable chips are divs rather than semantic buttons, affecting keyboard accessibility. Prompt list depends on backend capabilities.

Test signals: Cover every seed prompt rendered, icon fallback, click callback payload, and accessibility/keyboard behavior if improved.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/EmptyState.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/LoadingIndicator.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/LoadingIndicator.tsx

Purpose: Displays animated assistant loading state, stage text based on elapsed time, and long-request warning.

Important APIs, types, and functions: Exports `LoadingIndicator` with `elapsedSeconds` prop.

Control flow: Chooses the first `LOADING_STAGES` entry whose max seconds contains elapsed time, renders skeleton lines and typing dots, and shows a timeout warning after 60 seconds.

State and persistence behavior: Pure derived rendering; no local state.

Dependencies: Uses React `useMemo`, chatbot loading constants, and `ReconAIMark`.

Integration points: Used by `MessageList` while `useChat` has an in-flight request.

Risks and edge cases: The warning says timeout after 3 minutes but enforcement is backend/hook dependent. Stage thresholds must stay aligned with user expectations.

Test signals: Check stage boundaries at 3/10/45 seconds, long warning after 60 seconds, `aria-live` status, and active mark rendering.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/LoadingIndicator.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/MessageBubble.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/MessageBubble.tsx

Purpose: Renders one user or assistant chat message, including markdown, copy, and regenerate controls for assistant messages.

Important APIs, types, and functions: Exports `MessageBubble` with `message` and optional `onRegenerate`.

Control flow: User messages render plain text with user icon. Assistant messages render `ReactMarkdown` with GFM, show copy button using `copyToClipboard`, transient copied/copy-failed tooltip states, and optional regenerate button.

State and persistence behavior: Local `copied` and `copyFailed` booleans reset after two seconds.

Dependencies: Uses AntD Button/Tooltip/icons, `react-markdown`, `remark-gfm`, `classNames`, clipboard utility, and `ReconAIMark`.

Integration points: Used by `MessageList` for all persisted chat messages.

Risks and edge cases: Markdown rendering may allow unexpected link behavior unless markdown sanitization is handled by defaults. Copy timers are not cleared on unmount. User text is not markdown-rendered by design.

Test signals: Cover user/assistant rendering, markdown tables/lists, copy success/failure, timer reset, regenerate callback, and no actions for user messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/MessageBubble.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/MessageList.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/MessageList.tsx

Purpose: Scrollable chat transcript with auto-scroll, loading bubble, and retryable error bubble.

Important APIs, types, and functions: Exports `MessageList` with messages, in-flight state, elapsed seconds, error bubble, retry callback, and regenerate callback.

Control flow: Maps messages to `MessageBubble`, auto-scrolls to a bottom ref whenever messages/loading/error change, adds `LoadingIndicator` during in-flight requests, and renders an assistant-styled error bubble with Retry button.

State and persistence behavior: Uses only a bottom DOM ref; no persisted state.

Dependencies: Uses AntD Button, `MessageBubble`, `LoadingIndicator`, `ReconAIMark`, and chatbot types.

Integration points: Used by Assistant when messages exist.

Risks and edge cases: Error icon is a Unicode symbol, unlike the icon library. Auto-scroll always uses smooth behavior, which can fight manual scrollback. Error bubble is not part of persisted message history.

Test signals: Cover auto-scroll trigger, regenerate index wiring, retry button, loading indicator, error bubble text, and empty/nonempty messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/MessageList.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/ModelPicker.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/ModelPicker.tsx

Purpose: Provider/model selection controls for Recon AI requests.

Important APIs, types, and functions: Exports `ModelPicker` with model list, selected provider/model, provider/model change callbacks, and disabled flag.

Control flow: Groups models by provider using `getProviderForModel`, lists available providers plus the default sentinel, and shows a model select only after a non-default provider is selected.

State and persistence behavior: No local state; grouping is memoized from props.

Dependencies: Uses AntD `Select`, chatbot provider constants/helpers.

Integration points: Embedded in Composer and feeds provider/model to `useChat.sendMessage`.

Risks and edge cases: Unknown-provider models are grouped into `other` only if the group exists; current groups do. Prefix classification can be stale. Model select disappears when default provider is selected, losing selected model.

Test signals: Cover grouping, default sentinel, provider-specific model list, disabled state, unknown models, and provider/model callback values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/ModelPicker.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/ReconAIMark.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/ReconAIMark.tsx

Purpose: Inline SVG mark for Recon AI avatars, hero, and active loading states.

Important APIs, types, and functions: Exports `ReconAIMark` with optional `size`, `active`, and `className`.

Control flow: Defines a reusable sparkle path and places four scaled `use` instances in a group, applying CSS classes for active animation/styling.

State and persistence behavior: Stateless.

Dependencies: No external UI dependencies beyond React/SVG.

Integration points: Used by Assistant header, empty state, message bubbles, loading indicator, and error bubble.

Risks and edge cases: SVG IDs can collide if embedded in complex documents, though scoped use is usually fine. Styling/animation depends on external CSS classes.

Test signals: Snapshot size/class/active output and verify avatar contexts inherit color correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/assistant/components/ReconAIMark.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/buckets/buckets.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/buckets/buckets.tsx

Purpose: Top-level Buckets page that fetches bucket inventory, builds volume filters, manages visible columns/limit/search, and opens ACL details.

Important APIs, types, and functions: Exports default `Buckets`. Local helpers build volume-to-bucket maps and selected-volume bucket lists.

Control flow: Uses `/api/v1/buckets?limit=...`, normalizes bucket response rows, builds volume options, seeds selected volumes from URL query or all volumes, applies debounced search, and renders `BucketsTable` plus `AclPanel`.

State and persistence behavior: Tracks table metadata, selected columns/volumes/limit, search term/column, ACL panel visibility, and current row. Auto-reload state persists globally through `useAutoReload`.

Dependencies: Uses React Router `useLocation`, moment, `AutoReloadPanel`, `AclPanel`, `Search`, `MultiSelect`, `SingleSelect`, `BucketsTable`, `useApiData`, `useDebounce`, and `useAutoReload`.

Integration points: Receives `/Buckets?volume=...` links from Volumes table and talks to bucket API plus ACL drawer.

Risks and edge cases: The reviewed source contains a duplicated/nested `useEffect(() => {` near initial volume handling, which appears syntactically suspicious. State updates spread stale `state` in some handlers. Selected volume defaults can conflict with URL-seeded selection after data arrives.

Test signals: Compile/typecheck this file, then test URL volume seeding, all-volumes default, limit refetch, auto-reload, ACL drawer data, volume filter search/select-all, and table search by bucket/volume.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/buckets/buckets.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/capacity.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/capacity.tsx

Purpose: Cluster Capacity page combining storage distribution, SCM/OM/DN pending deletion, per-datanode details, auto-reload, and CSV download readiness polling.

Important APIs, types, and functions: Exports default `Capacity`. Local async helpers are `waitForDnFinished` and `downloadCsv`; derived values include `selectedDNDetails`, status labels, and breakdown descriptors.

Control flow: Fetches storage distribution and three pending-deletion endpoints, refreshes all APIs through auto-reload, adjusts polling interval while DN scans are running, derives cluster/service cards, waits for DN status FINISHED before downloading CSV, and renders `CapacityBreakdown` and `CapacityDetail` cards.

State and persistence behavior: Tracks `lastUpdated` and selected datanode. API state comes from four `useApiData` calls. Auto-reload enabled state is persisted via sessionStorage.

Dependencies: Uses AntD Popover/Tag/Typography/icons, `filesize`, moment, capacity constants/types, capacity subcomponents, `useApiData`, and `useAutoReload`.

Integration points: Consumes `/api/v1/storageDistribution`, `/api/v1/pendingDeletion?component=scm|om|dn`, and `/api/v1/storageDistribution/download`.

Risks and edge cases: CSV polling uses raw `fetch` outside `useApiData` and can run for 10 minutes. The total-capacity popover duplicates `File System Capacity` text. Default DN data can produce unknown host selections. Poll interval restart depends on autoReload object identity and suppressed deps.

Test signals: Cover API loading/errors, DN scan RUNNING versus FINISHED interval, CSV not-ready/content-type/filename handling, selected DN disabled options, SCM negative error path, and capacity math.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/capacity.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityBreakdown.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityBreakdown.tsx

Purpose: Reusable capacity summary card with statistics and a stacked progress strip.

Important APIs, types, and functions: Exports `CapacityBreakdown`. Props include title, item list, loading flag, and optional error string.

Control flow: If error is present, renders `ErrorCard`; otherwise maps items to AntD `Statistic` values using `filesize`, prefixes colored items with `GraphLegendIcon`, and passes colored items to `StackedProgress`.

State and persistence behavior: Stateless.

Dependencies: Uses AntD Card/Statistic, `filesize`, `GraphLegendIcon`, `ErrorCard`, `StackedProgress`, style constants, and capacity segment type.

Integration points: Used by Capacity and Overview pages for cluster/service capacity cards.

Risks and edge cases: Always formats values as bytes even though item type has an unused `format` property. Negative values are clamped to zero for display. Title React nodes are used in generated keys.

Test signals: Cover loading, error, zero/negative values, colored and uncolored items, stacked-progress inputs, and non-byte formats if implemented.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityBreakdown.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityDetail.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityDetail.tsx

Purpose: Reusable detailed capacity card with optional datanode selector, download link, statistic rows, legend breakdowns, and mini stacked bar charts.

Important APIs, types, and functions: Exports `CapacityDetail`. Props support dropdown items, disabled options, download URL/click handler, data detail items with loading/error metadata, and optional extra header content.

Control flow: Builds dropdown options, creates a card extra download link, shows a selector when requested, maps each detail item to a `Statistic`, shows `CapacityDetailError` on item error, otherwise renders legend rows and an EChart stacked bar generated by `getEchartOptions`.

State and persistence behavior: Stateless controlled component; selected value is handled by parent callback.

Dependencies: Uses AntD Card/Divider/Row/Select/Spin/Statistic, `filesize`, EChart wrapper, `GraphLegendIcon`, `CapacityDetailError`, and style constants.

Integration points: Used by Capacity for pending deletion and datanode-level capacity breakdowns.

Risks and edge cases: Select uses `defaultValue` not controlled `value`, so parent changes may not show. `filesize(data.size).split(' ')` assumes two-part output. Chart option stacks by title, which may be a React node.

Test signals: Cover dropdown disabled options, download click preventing navigation, loading per item and whole card, error item rendering with test ID, zero values, and chart segment radii.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityDetail.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityDetailError.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityDetailError.tsx

Purpose: Small inline error row for unavailable capacity detail data.

Important APIs, types, and functions: Exports `CapacityDetailError` with optional `message` and `testId`.

Control flow: Renders a disconnect icon and message inside a `capacity-detail-error` div.

State and persistence behavior: Stateless.

Dependencies: Uses React and `DisconnectOutlined`.

Integration points: Displayed by `CapacityDetail` for SCM or other detail cards with unavailable metrics.

Risks and edge cases: Only a visual message; no retry/action. Test ID is optional and consumer-controlled.

Test signals: Snapshot default/custom messages and test-id propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/CapacityDetailError.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/StackedProgress.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/StackedProgress.tsx

Purpose: Draws a horizontal proportional strip from capacity segment values.

Important APIs, types, and functions: Exports `StackedProgress` with `segments: Segment[]`.

Control flow: Memoizes total segment value, renders an empty placeholder if total is zero, otherwise maps each segment to a div with percentage width and background color.

State and persistence behavior: Pure derived render.

Dependencies: Uses React `useMemo` and the global `Segment` type available in the project typings/import context.

Integration points: Used by `CapacityBreakdown`.

Risks and edge cases: The file references `Segment` without importing it, relying on ambient/global type availability or causing a TypeScript error depending on config. Negative segment values can produce negative widths.

Test signals: Typecheck import behavior, zero total, single/multiple segments, negative values, and stable keys for duplicate labels.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/StackedProgress.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/WrappedInfoIcon.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/WrappedInfoIcon.tsx

Purpose: Reusable tooltip-wrapped info icon for capacity labels.

Important APIs, types, and functions: Exports `WrappedInfoIcon` with `title` and optional AntD tooltip placement.

Control flow: Renders an `InfoCircleOutlined` styled in blue with a tooltip.

State and persistence behavior: Stateless.

Dependencies: Uses AntD `Tooltip` and info icon.

Integration points: Used throughout Capacity labels and descriptions.

Risks and edge cases: Title is typed as string only, so rich tooltip content requires different components. Inline style duplicates icon styling.

Test signals: Check placement default/override, title rendering, and icon style/class integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/components/WrappedInfoIcon.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/constants/descriptions.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/constants/descriptions.constants.tsx

Purpose: Holds explanatory copy for Capacity page tooltips.

Important APIs, types, and functions: Exports `totalCapacityDesc`, `otherUsedSpaceDesc`, `ozoneUsedSpaceDesc`, `datanodesPendingDeletionDesc`, and `nodeSelectorMessage`.

Control flow: Static string constants only.

State and persistence behavior: No state.

Dependencies: No imports.

Integration points: Consumed by Capacity page labels and `WrappedInfoIcon` tooltips.

Risks and edge cases: Descriptions must remain accurate as backend semantics evolve; `totalCapacityDesc` is exported here but Capacity also defines a JSX variable with the same conceptual name.

Test signals: Content snapshot in Capacity tooltips and review when capacity API definitions change.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/constants/descriptions.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/constants/styles.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/constants/styles.constants.tsx

Purpose: Shared React CSS style objects for capacity cards and statistics.

Important APIs, types, and functions: Exports `cardHeadStyle` and `statisticValueStyle`.

Control flow: Static style objects only.

State and persistence behavior: No state.

Dependencies: Uses React CSSProperties type implicitly through `React.CSSProperties`.

Integration points: Imported by CapacityBreakdown and CapacityDetail.

Risks and edge cases: The file references `React.CSSProperties` without importing React, which relies on global JSX/React type availability and can fail under stricter TS settings. Styles hard-code Roboto/colors.

Test signals: Typecheck under project TS config and visual regression for card headers/statistics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/capacity/constants/styles.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/containers/containers.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/containers/containers.tsx

Purpose: Top-level Containers page for unhealthy container tabs, quasi-closed containers, export job submission/polling/download/delete, highlights, search, columns, and manual pagination.

Important APIs, types, and functions: Exports default `Containers` plus `PAGE_SIZE_OPTIONS`. Important helpers include `toContainer`, `fetchExportJobs`, `handleSubmitExport`, `downloadFile`, `deleteJob`, `fetchQuasiClosedCount`, `fetchTabData`, and pagination handlers.

Control flow: Loads cluster state and first missing-container page on mount, lazily loads tab data by unhealthy state, fetches one extra record to compute `hasNextPage`, maps quasi-closed responses into shared container rows, manages page history for previous navigation, polls export jobs while active, and renders `ContainerTable` for data tabs plus export job tables.

State and persistence behavior: Tracks highlight counts, page size, per-tab pagination/data/loading state, expanded rows, selected columns, search term/column, selected tab, export jobs/state/submitting, and a polling interval ref. Auto-reload state persists through `useAutoReload`.

Dependencies: Uses AntD Card/Tabs/Table/Select/Button/Progress/Tag/Tooltip/message, shared Search/MultiSelect/ContainerTable/AutoReloadPanel, `useApiData`, `fetchData`, `useAutoReload`, overview constants, and container/overview types.

Integration points: Consumes `/api/v1/clusterState`, `/api/v1/containers/unhealthy/:state`, `/api/v1/containers/quasiClosed`, and `/api/v1/containers/unhealthy/export` endpoints.

Risks and edge cases: There is a duplicated `key: 'submittedAt'` property in `submittedColumn`. Export duplicate checks block new exports even for completed jobs until delete. Polling uses raw fetch/fetchData and ignores polling errors. Shared search/columns apply across tabs, and expanded-row cache can outlive tab data.

Test signals: Cover each tab fetch URL/count update, cursor pagination and page-size reset, quasi-closed mapping/title, auto-reload reset, export submit 429/error/success, polling lifecycle, download/delete actions, duplicate export guard, and row expansion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/containers/containers.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/datanodes/datanodes.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/datanodes/datanodes.tsx

Purpose: Top-level Datanodes page that combines datanode inventory, decommission info, visible columns, search, auto-reload, and dead-node removal confirmation.

Important APIs, types, and functions: Exports default `Datanodes`. Local functions handle column changes, removal, combined data load, selection, and modal OK/cancel.

Control flow: Uses three `useApiData` hooks for decommission info, datanodes, and PUT remove. Combined effect maps API datanodes to table rows and rewrites op state to `DECOMMISSIONING` for decommissioning UUIDs. Removal calls PUT then reloads and clears selection.

State and persistence behavior: Tracks lastUpdated/dataSource/columns, selected columns, selected rows, search term/column, and modal open. A module-level `decommissionUuids` mirrors API data. Auto-reload persists via `useAutoReload`.

Dependencies: Uses AntD Button/Modal/icons, moment, shared Search/MultiSelect/DatanodesTable/AutoReloadPanel, `useApiData`, `useDebounce`, and datanode types.

Integration points: Talks to `/api/v1/datanodes`, `/api/v1/datanodes/decommission/info`, and `/api/v1/datanodes/remove`; renders `DatanodesTable` and remove modal.

Risks and edge cases: Global `decommissionUuids` can leak stale data. Combined effect spreads stale `state`. It manually starts polling on mount even though `useAutoReload` already starts based on session storage, risking duplicate initial refresh. Search column type includes revision but options omit it.

Test signals: Cover data/decommission merge, remove success/error, modal cancel clearing rows, auto-reload no-duplicate behavior, selectable dead nodes only, search fields, and decommission op-state rewrite.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/pages/datanodes/datanodes.tsx -->
