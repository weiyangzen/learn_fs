# subset-b-008131 grouped research

This grouped report covers the Recon web files assigned to `subset-b-008131`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/public/manifest.json -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/public/manifest.json

Purpose: CRA/PWA manifest metadata for the Recon web bundle, currently generic `React App` / `Create React App Sample` branding with `favicon.ico`, `start_url: "."`, standalone display, black theme color, and white background.

Important APIs/types/functions: Static JSON consumed by browser install/PWA metadata and the build pipeline; no runtime code.

Control flow/state/persistence: None in the file itself. Browser may cache manifest metadata and use it when the app is installed or bookmarked.

Dependencies/integration points: Referenced from the public HTML/build output. It must stay valid JSON and keep icon paths aligned with public assets.

Risks/test signals: Branding is stale for Ozone Recon and could surface in install prompts. No direct tests cover it; validation is build-time JSON parsing and manual browser/PWA inspection.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/public/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/Overview.test.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/Overview.test.tsx

Purpose: Vitest/Testing Library coverage for the V2 Overview page under both populated and null/faulty API scenarios.

Important APIs/types/functions: Defines `WrappedOverviewComponent` with `BrowserRouter`, mocks `@/v2/components/eChart/eChart`, uses `overviewServer` and `faultyOverviewServer`, and asserts locator constants from `overviewLocators`.

Control flow/state/persistence: `describe.each([true,false])` starts the appropriate MSW server, renders once per scenario, waits 100 ms for requests/state, then checks card text. Cleanup is intentionally deferred with `dont-cleanup-after-each` and done in `afterAll`.

Dependencies/integration points: Exercises `/api/v1/clusterState`, `/api/v1/task/status`, `/api/v1/keys/open/summary`, and `/api/v1/keys/deletePending/summary` through MSW and the real V2 overview component.

Risks/test signals: The fixed timeout can be flaky compared with `findBy`/`waitFor`; skipped cleanup trades speed for possible cross-test coupling. Tests strongly signal expected fallback strings: `N/A` and zero-byte capacity values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/Overview.test.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/assistant/Assistant.test.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/assistant/Assistant.test.tsx

Purpose: End-to-end component tests for the V2 Recon AI assistant page, covering health gating, model loading, chat success, provider-specific errors, disabled/busy/timeout states, and in-flight UI.

Important APIs/types/functions: `WrappedAssistantComponent`, `assistantServer`, multiple exported MSW handlers, `CHATBOT_ENDPOINTS`, `userEvent`, `waitFor`, and the real `Assistant` page.

Control flow/state/persistence: A single MSW server is opened for the suite. Each test installs handlers, renders inside `BrowserRouter`, waits for health-derived UI, interacts with input/provider dropdown/send/stop buttons, then clears `sessionStorage` and DOM in `afterEach`.

Dependencies/integration points: Integrates with `/api/v1/chatbot/health`, models, and chat endpoints via constants. It asserts markdown rendering, provider choices (`OpenAI`, `Google Gemini`, `Anthropic Claude`), and error message mapping.

Risks/test signals: The imported `rest` and `mockModelsDisabled` are unused. Tests reveal user-facing error contracts and state transitions; changes to labels/placeholders will break them.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/assistant/Assistant.test.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/capacity/Capacity.test.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/capacity/Capacity.test.tsx

Purpose: Tests the V2 Capacity page’s cluster capacity, pending deletion, datanode detail, and SCM sentinel-error rendering.

Important APIs/types/functions: Renders `Capacity`, uses `capacityServer`, capacity response mocks, and inline MSW override for `api/v1/pendingDeletion?component=scm`. Mocks legacy `AutoReloadPanel` and chart components.

Control flow/state/persistence: Server starts once and resets after each test. Tests render the page, find cards by headings, then assert card-local text content and `pending-deletion-scm-error`.

Dependencies/integration points: Exercises `/api/v1/storageDistribution` and `/api/v1/pendingDeletion` for `scm`, `om`, and `dn`. Integrates with AntD card/table markup and chart count expectations.

Risks/test signals: Uses card DOM traversal with `.closest('.ant-card')`, so AntD markup changes can break tests. Sentinel `-1` handling for SCM is a documented behavior signal that should be preserved.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/capacity/Capacity.test.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/datanodes/Datanodes.test.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/datanodes/Datanodes.test.tsx

Purpose: Page-level tests for V2 Datanodes, validating initial render, API data load, empty data, debounced search, case behavior, no-result UI, and API error handling.

Important APIs/types/functions: Uses `Datanodes`, `datanodeServer`, `waitForDNTable`, locator constants, and spies `showDataFetchError`. Mocks `AutoReloadPanel` and V2 `multiSelect` to isolate search/table behavior.

Control flow/state/persistence: MSW server starts once. Tests render the page, wait for rows/table, update search input, pause 310 ms for debounce, and check row counts. One removal modal test is skipped because the static mock response never reflects removal.

Dependencies/integration points: Covers `api/v1/datanodes` and `api/v1/datanodes/decommission/info`, plus common error reporting.

Risks/test signals: The debounce sleep is timing-sensitive. Error expectation checks a stringified Axios error, which may change with axios versions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/datanodes/Datanodes.test.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/datanodes/DatanodesTable.test.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/datanodes/DatanodesTable.test.tsx

Purpose: Component-level tests for `DatanodesTable`, focused on rendering, client filtering, row selection rules, and storage tooltip content.

Important APIs/types/functions: Defines `defaultProps` and `getDataWith`, imports `DatanodeTableProps`, `DatanodesTable`, and `waitForDNTable`.

Control flow/state/persistence: Builds synthetic datanode rows with storage reports and pipelines, renders the table with controlled props, then interacts with AntD checkboxes and storage bar hover.

Dependencies/integration points: Integrates with V2 datanode table types, AntD table row selection, `.capacity-bar-v2`, and tooltip labels for filesystem capacity/used/available.

Risks/test signals: Checkbox indexes depend on AntD table DOM order. The first test calls `waitForDNTable()` without awaiting it, so it mostly asserts immediate render. It documents that only DEAD nodes are selectable for removal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/datanodes/DatanodesTable.test.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/locators/locators.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/locators/locators.ts

Purpose: Centralizes `data-testid` strings and row-test regular expressions used by Recon web tests.

Important APIs/types/functions: Exports `overviewLocators`, `datanodeLocators`, `pipelineLocators`, `autoReloadPanelLocators`, and `searchInputLocator`. Includes helper functions for datanode and pipeline row IDs.

Control flow/state/persistence: No runtime state; constants only.

Dependencies/integration points: Tests depend on these constants matching V2 Overview, Datanodes, Pipelines, AutoReloadPanel, and search components. Regex entries are passed to `screen.getAllByTestId`.

Risks/test signals: Typos such as `datanodeSearchcDropdown` are harmless only while unused. Any production `data-testid` rename must update this file and related tests together.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/locators/locators.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/assistantMocks/assistantServer.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/assistantMocks/assistantServer.ts

Purpose: MSW server and reusable handlers for Recon AI assistant tests.

Important APIs/types/functions: Exports health handlers (`mockHealthEnabled`, disabled, not configured), model handlers, chat handlers for success/delay/busy/timeout/error/disabled/interrupted/empty, and `assistantServer`.

Control flow/state/persistence: Handlers respond to `CHATBOT_ENDPOINTS.HEALTH`, `.MODELS`, and `.CHAT` with status-specific JSON. The default `assistantServer` includes enabled health, model list, and successful chat.

Dependencies/integration points: Used by `Assistant.test.tsx` and any future assistant tests. Model names encode provider choices consumed by the assistant UI.

Risks/test signals: Error bodies are user-facing contract fixtures. Model names can become stale as providers evolve. `mockModelsDisabled` and `mockChatEmpty` are available but not currently asserted by the visible tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/assistantMocks/assistantServer.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/capacityMocks/capacityResponseMocks.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/capacityMocks/capacityResponseMocks.ts

Purpose: Static payloads for V2 Capacity tests.

Important APIs/types/functions: Exports `StorageDistribution`, `ScmPendingDeletion`, `OmPendingDeletion`, and `DnPendingDeletion` with byte/count fields used by capacity cards and charts.

Control flow/state/persistence: No behavior; data fixtures only. Values are deliberately small powers of two so UI renders predictable `KB` labels.

Dependencies/integration points: Consumed by `capacityServer.ts` and by inline test handler overrides. Mirrors backend API shapes for `/api/v1/storageDistribution` and `/api/v1/pendingDeletion`.

Risks/test signals: Fixture field names are an implicit contract with the capacity page. Sentinel failure values are not here, but tests override SCM with `-1` fields, signaling separate error handling logic.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/capacityMocks/capacityResponseMocks.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/capacityMocks/capacityServer.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/capacityMocks/capacityServer.ts

Purpose: MSW server for Capacity page tests.

Important APIs/types/functions: Creates `handlers` for `api/v1/storageDistribution` and `api/v1/pendingDeletion`, then exports `capacityServer = setupServer(...handlers)`.

Control flow/state/persistence: The pending deletion handler branches on query param `component` and returns SCM, OM, DN, or 400 unsupported responses.

Dependencies/integration points: Consumed by `Capacity.test.tsx`; provides the main API surface for capacity data and pending deletion breakdown.

Risks/test signals: Uses relative paths without leading slash (`api/v1/...`), matching the test environment’s request style. Unsupported component behavior is present but not directly asserted.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/capacityMocks/capacityServer.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/datanodeMocks/datanodeResponseMocks.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/datanodeMocks/datanodeResponseMocks.ts

Purpose: Datanode API fixture set for V2 datanode page and table tests.

Important APIs/types/functions: Exports `DatanodeResponse`, `NullDatanodeResponse`, `NullDatanodes`, and `DecommissionInfo`.

Control flow/state/persistence: Static JSON-like data. The main response contains five datanodes spanning HEALTHY, STALE, DEAD, DECOMMISSIONING, and DECOMMISSIONED op states, with storage reports, pipeline memberships, version/build info, and rack location.

Dependencies/integration points: Used by `datanodeServer.ts`, page search tests, table row tests, and decommission info UI.

Risks/test signals: Mixed-case hostname `ozone-DataNode-5...` intentionally tests case-sensitive/case-insensitive behavior. Null fixtures are exported for edge-case tests but not used by the primary suite shown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/datanodeMocks/datanodeResponseMocks.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/datanodeMocks/datanodeServer.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/datanodeMocks/datanodeServer.ts

Purpose: MSW servers for datanode tests, including normal and null-response variants.

Important APIs/types/functions: Exports `datanodeServer`, `nullDatanodeResponseServer`, and `nullDatanodeServer`; handlers cover `api/v1/datanodes` and `api/v1/datanodes/decommission/info`.

Control flow/state/persistence: Each server uses a different datanode payload while sharing decommission info. No mutable state beyond MSW server lifecycle.

Dependencies/integration points: Primary suite uses `datanodeServer`; null servers are ready for robustness tests around partially null payloads.

Risks/test signals: Like other mocks, paths are relative. Decommission endpoint shape must remain consistent with V2 datanode summary consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/datanodeMocks/datanodeServer.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/overviewMocks/overviewResponseMocks.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/overviewMocks/overviewResponseMocks.ts

Purpose: Overview dashboard fixture values for health, capacity, and key summaries.

Important APIs/types/functions: Exports `ClusterState`, `OpenKeys`, and `DeletePendingSummary`. `overviewServer.ts` also references `TaskStatus`, so this fixture file is expected to define or re-export it in the current tree state; if absent, tests/build would fail.

Control flow/state/persistence: Static data only. Values map directly to expected Overview cards: datanodes `3/5`, containers `20`, volumes `2`, buckets `24`, keys `1424`, pipelines `7`, and byte summaries.

Dependencies/integration points: Consumed by overview MSW handlers and `Overview.test.tsx`.

Risks/test signals: Missing or renamed exports are caught at test compile time. Byte values are chosen to exercise filesize rendering (`1 KB`, `4 KB`, etc.).
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/overviewMocks/overviewResponseMocks.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/overviewMocks/overviewServer.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/overviewMocks/overviewServer.ts

Purpose: MSW normal and faulty servers for Overview tests.

Important APIs/types/functions: Defines `handlers`, `faultyHandlers`, `overviewServer`, and `faultyOverviewServer`. Endpoints include `api/v1/clusterState`, `api/v1/task/status`, `api/v1/keys/open/summary`, and `api/v1/keys/deletePending/summary`.

Control flow/state/persistence: Normal handlers return fixture data; faulty handlers return `null` with HTTP 200 to test UI fallback behavior rather than transport errors.

Dependencies/integration points: Used by `Overview.test.tsx` to assert both populated and `N/A`/zero states.

Risks/test signals: `TaskStatus` must exist in the response mock module. Returning null with 200 is a strong signal that the Overview page should treat schema absence separately from HTTP failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/overviewMocks/overviewServer.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/pipelineMocks/pipelineResponseMocks.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/pipelineMocks/pipelineResponseMocks.ts

Purpose: Pipeline API fixture for V2 pipeline page tests.

Important APIs/types/functions: Exports `PipelinesResponse` with `totalCount` and three visible pipeline records in the file content read, each including pipeline id, status, leader, datanodes, timing/election fields, replication type/factor, and container count.

Control flow/state/persistence: Static fixture only. Datanode entries include rich backend node details, ports, network info, and persisted op state, even though table tests mostly assert pipeline fields.

Dependencies/integration points: Consumed by `pipelinesServer.ts` and page tests.

Risks/test signals: `totalCount` says 6 while the fixture contains 3 records, which tests codify by expecting 3 rows. That mismatch can mask pagination/count behavior if the table later uses `totalCount`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/pipelineMocks/pipelineResponseMocks.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/pipelineMocks/pipelinesServer.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/pipelineMocks/pipelinesServer.ts

Purpose: MSW server for V2 Pipelines tests.

Important APIs/types/functions: Defines one handler for `api/v1/pipelines` returning `PipelinesResponse`, and exports `pipelineServer`.

Control flow/state/persistence: No branching; tests override the handler for empty and error cases.

Dependencies/integration points: Used by `Pipelines.test.tsx` server lifecycle and API override checks.

Risks/test signals: Relative endpoint path must match axios/fetch calls in tests. Because only one default handler exists, additional pipeline endpoints require explicit test additions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/mocks/pipelineMocks/pipelinesServer.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/pipelines/Pipelines.test.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/pipelines/Pipelines.test.tsx

Purpose: Page-level tests for V2 Pipelines covering render, data load, row count, empty data, debounced search, no results, and API error propagation.

Important APIs/types/functions: Uses `Pipelines`, `pipelineServer`, locator constants, `waitForPipelineTable`, and a spy on `showDataFetchError`. Mocks AutoReloadPanel and V2 MultiSelect.

Control flow/state/persistence: Starts MSW once, renders the page, waits for table or rows, changes search input, waits 310 ms for debounce, and overrides `api/v1/pipelines` for empty/error cases.

Dependencies/integration points: Tests the page’s integration with table rows, multi-select/search controls, and common error notification path.

Risks/test signals: Search tests depend on debounce timing. Error expectation is axios-string specific. The “no results” comment mentions datanode, a copy/paste artifact.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/pipelines/Pipelines.test.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/pipelines/PipelinesTable.test.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/pipelines/PipelinesTable.test.tsx

Purpose: Component tests for V2 `PipelinesTable`, validating render, search filtering, dynamic selected columns, sorting, and pagination.

Important APIs/types/functions: Defines `defaultProps` and `getPipelineWith`, imports `Pipeline` and `PipelinesTableProps`, mocks AntD `scrollTo`, and uses `pipelineLocators`.

Control flow/state/persistence: Renders controlled data arrays, simulates header clicks for sorting, and clicks pagination next page for an 11-row data set.

Dependencies/integration points: Exercises AntD table sorting/pagination and the table’s selected-column projection.

Risks/test signals: Pagination test catches and suppresses `ReferenceError`, which can hide real failures. Sorting expectations depend on default AntD sort direction after one header click.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/pipelines/PipelinesTable.test.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/utils/datanodes.utils.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/utils/datanodes.utils.tsx

Purpose: Small Testing Library helper for waiting on the datanode table.

Important APIs/types/functions: Exports `waitForDNTable`, returning `waitFor(() => screen.getByTestId('dn-table'))`.

Control flow/state/persistence: No state. It wraps an async polling assertion in a reusable function.

Dependencies/integration points: Used by datanode page and table tests; depends on the V2 datanodes table retaining `data-testid="dn-table"`.

Risks/test signals: Callers must `await` it; one table test currently does not, reducing the helper’s value there.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/utils/datanodes.utils.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/utils/pipelines.utils.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/utils/pipelines.utils.tsx

Purpose: Testing helper for waiting until the pipelines table exists.

Important APIs/types/functions: Exports `waitForPipelineTable`, returning `waitFor(() => screen.getByTestId('pipelines-table'))`.

Control flow/state/persistence: Stateless async wrapper.

Dependencies/integration points: Used in V2 Pipelines page tests and depends on `PipelinesTable` emitting the expected `data-testid`.

Risks/test signals: This helper only waits for table container presence, not data rows, so callers still need row/text assertions for data-load completeness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/utils/pipelines.utils.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/vitest.setup.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/vitest.setup.ts

Purpose: Global Vitest/jsdom setup for Recon web tests.

Important APIs/types/functions: Imports `@testing-library/jest-dom/vitest`, installs `window.localStorage`, `window.matchMedia`, and `Element.prototype.scrollIntoView` mocks.

Control flow/state/persistence: `localStorageMock` stores values in a closure with `getItem`, `setItem`, `removeItem`, and `clear`. Other browser APIs are replaced with `vi.fn()` shims.

Dependencies/integration points: Supports AntD, components using storage, and tests expecting jest-dom matchers.

Risks/test signals: Comment says jsdom lacks local storage, though modern jsdom often provides it; overriding may diverge from browser semantics. It mocks localStorage but not sessionStorage, even several tests/components use sessionStorage directly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/vitest.setup.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/app.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/app.tsx

Purpose: Top-level React app shell that chooses legacy vs V2 navigation/routes, owns sidebar collapse and UI-version preference, and wraps the route switch in a hash router.

Important APIs/types/functions: `IAppState`, functional `AppLayout`, class `App`, `onCollapse`, and `onToggleUI` callback. Uses `routes`, `routesV2`, `MakeRouteWithSubRoutes`, legacy/V2 navbars and breadcrumbs, AntD `Layout` and `Switch`.

Control flow/state/persistence: `App` initializes `collapsed: false` and `enableOldUI` from `sessionStorage`. Toggle writes `enableOldUI` back to session storage. Root `/` redirects to `/Overview`; unknown routes render V2 `NotFound`.

Dependencies/integration points: Integrates with `HashRouter`, route arrays, Suspense `Loader`, and special Assistant layout/footer suppression.

Risks/test signals: `AppLayout` props are `any`; route switch mixes legacy and V2 not-found behavior. Session storage JSON parsing can throw if corrupted.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/app.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/aclDrawer/aclDrawer.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/aclDrawer/aclDrawer.tsx

Purpose: Legacy ACL drawer component showing ACL entries for an OM entity in an AntD drawer/table.

Important APIs/types/functions: Exports `AclPanel` class. Props include `visible`, `acls`, `objName`, and `objType`. Uses `renderAclList`, `renderAclIdentityType`, `IAcl`, `ACLIdentityTypeList`, and color maps.

Control flow/state/persistence: Copies incoming `visible` prop into local state in `componentWillReceiveProps`; closing only sets local state false. Table columns sort/filter by name/type and render ACL rights as tags.

Dependencies/integration points: Used by legacy volume/bucket/object metadata views; depends on AntD `Drawer`, `Table`, `Tag`, and OM ACL types/constants.

Risks/test signals: `componentWillReceiveProps` is deprecated, and the file references `RouteComponentProps` without importing it. Parent may not learn about drawer close because no `onClose` callback is exposed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/aclDrawer/aclDrawer.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/autoReloadPanel/autoReloadPanel.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/autoReloadPanel/autoReloadPanel.tsx

Purpose: Legacy auto-refresh control panel that shows refresh time, OM DB sync time, manual refresh, auto-refresh toggle, and manual OM sync trigger.

Important APIs/types/functions: `IAutoReloadPanelProps`, `AutoReloadPanel` class, `autoReloadToggleHandler`, and default export wrapped in `withRouter`.

Control flow/state/persistence: Reads `sessionStorage.autoReloadEnabled` every render to set the switch default. Toggle delegates to parent `togglePolling`; reload and OM sync buttons call parent callbacks. Timestamps are formatted with Moment and exposed through tooltips.

Dependencies/integration points: Used by pages that own data polling via `AutoReloadHelper`; depends on AntD `Tooltip`, `Button`, `Switch`, and icons.

Risks/test signals: `Switch` uses `defaultChecked`, so it may not reflect external session changes after mount. `omStatus` is typed string but used truthily as status.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/autoReloadPanel/autoReloadPanel.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/breadcrumbs/breadcrumbs.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/breadcrumbs/breadcrumbs.tsx

Purpose: Legacy breadcrumb renderer for route paths.

Important APIs/types/functions: Class `Breadcrumbs` wrapped with `withRouter`, uses `breadcrumbNameMap`, `HomeOutlined`, and `Link`.

Control flow/state/persistence: Splits `location.pathname`, builds cumulative URLs, maps them to labels, and prepends a home crumb linking to `/`.

Dependencies/integration points: Used by legacy app shell when old UI is enabled. Depends on routes and `breadcrumbNameMap` staying aligned.

Risks/test signals: Unknown paths render undefined labels. No tests directly cover breadcrumb labels in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/breadcrumbs/breadcrumbs.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/eChart/eChart.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/eChart/eChart.tsx

Purpose: Legacy React wrapper around ECharts.

Important APIs/types/functions: Exports `EChartProps` and named function `EChart`. Props include `option`, `style`, `settings`, `loading`, `theme`, and `onClick`.

Control flow/state/persistence: Initializes chart on mount/theme change, registers click handler, adds window resize listener, disposes on cleanup, then updates options and loading state in separate effects.

Dependencies/integration points: Used by legacy charts and mocked in tests because jsdom cannot supply chart dimensions reliably.

Risks/test signals: `getInstanceByDom` can return undefined, but code calls `chart.setOption`/`showLoading` without null checks. Re-registering click handlers on option updates may duplicate handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/eChart/eChart.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/multiSelect/multiSelect.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/multiSelect/multiSelect.tsx

Purpose: Legacy `react-select` multi-select wrapper with optional “Select all” support and compact value display.

Important APIs/types/functions: Exports `IOption` and `MultiSelect` `PureComponent`. Props extend `ReactSelectProps<IOption>` and add `allowSelectAll`, `allOption`, and `maxShowValues`.

Control flow/state/persistence: When select-all is enabled, custom `Option` renders checkboxes and custom `ValueContainer` shows “Select all” or `N selected`. `onChange` rewrites selections to include/drop the all option.

Dependencies/integration points: Used by legacy tables/forms needing column or filter selection; depends on `react-select` and animated components.

Risks/test signals: `components` object incorrectly includes `animatedComponents` as a key rather than spreading animated components. Non-null assertions around `onChange` assume controlled usage.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/multiSelect/multiSelect.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/navBar/navBar.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/navBar/navBar.tsx

Purpose: Legacy sidebar navigation for Ozone Recon.

Important APIs/types/functions: `INavBarProps`, `NavBar` class, `componentDidMount`, `fetchDisableFeatures`, and default `withRouter(NavBar)`.

Control flow/state/persistence: On mount, fetches `/api/v1/features/disabledFeatures` with axios, then enables/disables Heatmap based on whether `HEATMAP` appears. Renders fixed AntD `Sider` menu with route links and selected key from `location.pathname`.

Dependencies/integration points: Used by `app.tsx` old UI path; depends on logo asset, AntD Menu, route names, and `showDataFetchError`.

Risks/test signals: Props type includes state fields that are actually internal state. Heatmap is hidden on fetch failure. No direct tests in this subset cover legacy navbar.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/navBar/navBar.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/overviewCard/overviewCard.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/overviewCard/overviewCard.tsx

Purpose: Legacy Overview metric card with icon selection, optional storage bar, error highlighting, and optional link wrapping.

Important APIs/types/functions: `IconSelector`, `OverviewCardWrapper`, `OverviewCard`, `IOverviewCardProps`, and storage integration via `IStorageReport`.

Control flow/state/persistence: Selects icon by string, marks card error when `error` or `data === 'N/A'`, embeds `StorageBar` when `storageReport` exists, and wraps cards in `Link`. For `/Om`, it derives tab state from card title.

Dependencies/integration points: Used by legacy Overview and OM Insights navigation.

Risks/test signals: `OverviewCardWrapper` reaches into `children._owner.stateNode.props`, a React internal that is brittle and unsafe. V2 wrapper replaces this with explicit title props.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/overviewCard/overviewCard.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/quotaBar/quotaBar.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/quotaBar/quotaBar.tsx

Purpose: Legacy quota usage progress bar with tooltip metadata.

Important APIs/types/functions: `IQuotaBarProps`, `QuotaBar` class, `renderQuota` helper, and default `withRouter`.

Control flow/state/persistence: Computes `remaining = quota - used`, formats size quotas with `filesize`, and renders AntD `Progress` using `getCapacityPercent(used, quota)`. Tooltip shows used and remaining with themed square icons.

Dependencies/integration points: Used by legacy volume/bucket namespace quota displays. Depends on `FilledIcon`, `getCapacityPercent`, AntD `Progress`, and `filesize`.

Risks/test signals: Quota `<= -1` displays `-`, but percent still divides by quota, producing negative/invalid percentages. No direct tests cover this component.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/quotaBar/quotaBar.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/rightDrawer/rightDrawer.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/rightDrawer/rightDrawer.tsx

Purpose: Legacy right-side metadata summary drawer.

Important APIs/types/functions: Exports `DetailPanel` class. Props include `visible`, `keys`, `values`, and `path`.

Control flow/state/persistence: Mirrors incoming `visible` to local state using `componentWillReceiveProps`, closes locally, zips `keys` and `values` into table rows, and renders AntD Drawer/Table.

Dependencies/integration points: Used by legacy namespace/disk usage metadata views.

Risks/test signals: References `RouteComponentProps` without import. `keys`/`values` are typed as empty tuple arrays (`[]`), losing real element types. Close state is internal only, so parent visibility may become inconsistent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/rightDrawer/rightDrawer.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/storageBar/storageBar.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/storageBar/storageBar.tsx

Purpose: Legacy storage capacity progress bar with tooltip breakdown.

Important APIs/types/functions: `IStorageBarProps`, `StorageBar` class, `filesize.partial`, `getCapacityPercent`, and `FilledIcon`.

Control flow/state/persistence: Computes non-Ozone used as `total - remaining - used`, total used as `total - remaining`, and renders AntD `Progress` with overall percent plus success percent for Ozone used.

Dependencies/integration points: Used by legacy overview and datanode capacity cells.

Risks/test signals: Divide-by-zero in `getCapacityPercent` can produce invalid percent when `total` is zero. Negative non-Ozone values can render if backend fields are inconsistent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/components/storageBar/storageBar.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/aclDrawer.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/aclDrawer.constants.tsx

Purpose: Legacy color maps for ACL identity types and ACL rights.

Important APIs/types/functions: Exports `aclIdentityTypeColorMap` and `aclRightColorMap` with string index signatures.

Control flow/state/persistence: None; constants only.

Dependencies/integration points: Used by legacy `AclPanel` to color AntD `Tag` elements for identities and rights.

Risks/test signals: Maps are not type-checked against `ACLIdentityTypeList`/`ACLRightList`; new backend ACL enum values render uncolored unless the map is updated.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/aclDrawer.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/autoReload.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/autoReload.constants.tsx

Purpose: Defines the legacy global auto-reload interval.

Important APIs/types/functions: Exports `AUTO_RELOAD_INTERVAL_DEFAULT = 60 * 1000`.

Control flow/state/persistence: None here; `AutoReloadHelper` uses it for recursive polling timeouts.

Dependencies/integration points: Any component using `AutoReloadHelper` inherits a 60 second refresh cadence.

Risks/test signals: No tests assert the interval. Changing it affects page network load and freshness globally.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/autoReload.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/breadcrumbs.constants.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/breadcrumbs.constants.tsx

Purpose: Legacy route-to-label map for breadcrumbs.

Important APIs/types/functions: Exports `breadcrumbNameMap` with labels for Overview, Volumes, Buckets, Datanodes, Pipelines, Missing Containers, Containers, Insights, Namespace Usage, Heatmap, and Om.

Control flow/state/persistence: None; constants only.

Dependencies/integration points: Consumed by legacy `Breadcrumbs`. Must align with `routes.tsx` and nav menu paths.

Risks/test signals: Missing `/Capacity` and `/Assistant` reflect legacy route scope. Unknown route breadcrumbs render undefined labels.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/constants/breadcrumbs.constants.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/index.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/index.tsx

Purpose: Client entry point for the Recon React app.

Important APIs/types/functions: Imports React, `ReactDOM`, Roboto font weights, global `index.less`, and `App`; calls `ReactDOM.render(<App/>, document.querySelector('#root'))`.

Control flow/state/persistence: No local state. Bootstraps the app into the root DOM node.

Dependencies/integration points: Depends on the HTML root element and React 17-style render API.

Risks/test signals: React 18 migrations would replace `ReactDOM.render` with `createRoot`. If `#root` is absent, render receives null and fails at startup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/index.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/makeRouteWithSubRoutes.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/makeRouteWithSubRoutes.tsx

Purpose: Shared route factory for legacy and V2 route arrays.

Important APIs/types/functions: Exports `MakeRouteWithSubRoutes(route: IRoute)`, returning a React Router `Route` that renders `route.component` with router props and `routes={route.routes}`.

Control flow/state/persistence: Stateless functional renderer. Route matching uses the `path` supplied by each route object and is not `exact`.

Dependencies/integration points: Used by `app.tsx` when mapping `routes` and `routesV2`; depends on `IRoute`.

Risks/test signals: Non-exact matching can allow broader route matches depending on order. Component type is dynamically rendered as `<route.component>`, which is valid but relies on route objects being well-formed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/makeRouteWithSubRoutes.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/react-app-env.d.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/react-app-env.d.ts

Purpose: TypeScript ambient reference for Create React App/react-scripts.

Important APIs/types/functions: `/// <reference types="react-scripts" />` supplies declarations for asset imports and environment types.

Control flow/state/persistence: None.

Dependencies/integration points: Supports TypeScript compilation for CRA-style imports such as images and less/css assets.

Risks/test signals: If the build migrates away from react-scripts, this reference may become stale. No runtime tests apply.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/react-app-env.d.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/routes.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/routes.tsx

Purpose: Legacy route table for old Recon UI pages.

Important APIs/types/functions: Exports `routes: IRoute[]` mapping path strings to legacy view components: Overview, Datanodes, Volumes, Buckets, Pipelines, Insights, Om, MissingContainers, DiskUsage, Containers, Heatmap, and NotFound.

Control flow/state/persistence: No state; route order drives React Router matching when old UI is enabled.

Dependencies/integration points: Used by `app.tsx` through `MakeRouteWithSubRoutes`, and aligned with legacy navbar and breadcrumbs.

Risks/test signals: `/:NotFound` catch-all inside the array can interact with non-exact routing. `/Containers` currently maps to `MissingContainers`, indicating either reuse or naming drift.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/routes.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/axios.types.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/axios.types.tsx

Purpose: Minimal axios response typing helper.

Important APIs/types/functions: Exports generic `IAxiosResponse<T>` with `data: T`.

Control flow/state/persistence: None.

Dependencies/integration points: Intended for components/helpers that want a narrowed response type without importing full axios generics.

Risks/test signals: It only models `data`, omitting status/headers/config. Overuse can hide response metadata needs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/axios.types.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/datanode.types.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/datanode.types.tsx

Purpose: Legacy datanode enum and storage report types.

Important APIs/types/functions: Exports `DatanodeStateList`, `DatanodeState`, `DatanodeOpStateList`, `DatanodeOpState`, and `IStorageReport`.

Control flow/state/persistence: Type declarations and const lists only.

Dependencies/integration points: Used by legacy tables/cards and ACL/storage components. Lists correspond to Hadoop/Ozone protobuf enums noted in comments.

Risks/test signals: Backend enum additions require list updates. `IStorageReport` omits newer filesystem capacity fields present in V2 datanode fixtures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/datanode.types.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/om.types.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/om.types.tsx

Purpose: Legacy Ozone Manager metadata types for ACLs, volumes, and buckets.

Important APIs/types/functions: Exports `IAcl`, `IVolume`, `IBucket`, bucket storage/layout lists and union types, `ACLIdentityTypeList`, `ACLIdentity`, `ACLRightList`, and `ACLRight`.

Control flow/state/persistence: Type-only module plus enum-like arrays.

Dependencies/integration points: Used by legacy ACL drawer, volume/bucket views, quota display, and metadata tables.

Risks/test signals: The list-to-union pattern uses mutable arrays, so types are broader than literal unions unless `as const` is used. Backend enum drift requires updates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/om.types.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/routes.types.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/routes.types.tsx

Purpose: Shared route object type.

Important APIs/types/functions: Exports `IRoute` with `path`, `component: React.ElementType`, and optional nested `routes`.

Control flow/state/persistence: None; type definition only.

Dependencies/integration points: Used by `routes.tsx`, V2 route tables, and `MakeRouteWithSubRoutes`.

Risks/test signals: It does not model route exactness, guards, labels, or sidebar metadata, so route behavior lives outside the type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/types/routes.types.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/autoReloadHelper.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/autoReloadHelper.tsx

Purpose: Legacy polling helper for pages with auto-refresh.

Important APIs/types/functions: Class `AutoReloadHelper` with `loadData`, `interval`, `initPolling`, `startPolling`, `stopPolling`, and `handleAutoReloadToggle`.

Control flow/state/persistence: `initPolling` calls `loadData` and schedules itself with `window.setTimeout` using `AUTO_RELOAD_INTERVAL_DEFAULT`. Toggle writes `autoReloadEnabled` to `sessionStorage` and starts/stops polling.

Dependencies/integration points: Works with `AutoReloadPanel` callbacks and page-level data loaders.

Risks/test signals: Uses recursive `setTimeout`, not `setInterval`, which is good for drift but requires cleanup on unmount. `stopPolling` does not reset `interval` to 0, and scheduled callbacks can continue if lifecycle cleanup is missed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/autoReloadHelper.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/axiosRequestHelper.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/axiosRequestHelper.tsx

Purpose: Utility wrappers for cancellable axios GET/PUT/POST and batch GET requests.

Important APIs/types/functions: Exports `AxiosGetHelper`, `AxiosPutHelper`, `AxiosPostHelper`, `PromiseAllSettledGetHelper`, and `cancelRequests`.

Control flow/state/persistence: Each helper aborts an existing controller if provided, creates a new `AbortController`, and returns the axios request plus controller. Batch helper maps URLs to GET promises and wraps them in `Promise.allSettled`.

Dependencies/integration points: Used by data-heavy legacy/V2 pages that need cancellation during reloads or unmounts.

Risks/test signals: Types use `any` heavily. Aborting an existing request as a side effect can surprise callers if controllers are shared. `cancelRequests` expects an array but does not clear it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/axiosRequestHelper.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/clipboard.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/clipboard.ts

Purpose: Cross-context clipboard copy helper.

Important APIs/types/functions: Exports async `copyToClipboard(text): Promise<boolean>`.

Control flow/state/persistence: Tries `navigator.clipboard.writeText`; on denial/unavailability falls back to creating a hidden readonly textarea, selecting it, and calling `document.execCommand('copy')`. Cleans up the textarea on normal fallback path.

Dependencies/integration points: Used by UI controls that copy IDs, paths, or generated assistant text, especially on HTTP clusters where async Clipboard API may be unavailable.

Risks/test signals: If `execCommand` throws after append but before removal, textarea cleanup is skipped. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/clipboard.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/columnSearch.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/columnSearch.tsx

Purpose: Legacy AntD table column-search prop builder.

Important APIs/types/functions: `ColumnSearch` `PureComponent`, `getColumnSearchProps(dataIndex)`, `handleSearch`, and `handleReset`.

Control flow/state/persistence: Renders filter dropdown with input/search/reset buttons, tracks input ref, focuses/selects on dropdown open, and filters records by scalar string or array/object values.

Dependencies/integration points: Spread into AntD table column definitions in legacy tables.

Risks/test signals: `if (record[dataIndex] !== undefined || record[dataIndex] !== null)` should be `&&`; as written it attempts `toString()` on null/undefined. Object detection via `typeof {}` is imprecise.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/columnSearch.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/common.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/common.tsx

Purpose: Shared formatting, error notification, comparison, merge, and promise-result helpers.

Important APIs/types/functions: Exports `getCapacityPercent`, `timeFormat`, `showInfoNotification`, `showDataFetchError`, `byteToSize`, `numberWithCommas`, `nullAwareLocaleCompare`, `removeDuplicatesAndMerge`, and `checkResponseError`.

Control flow/state/persistence: Error handler suppresses canceled axios requests, formats server/network errors, emits AntD error notifications, and turns metadata initialization strings into warn notifications. `checkResponseError` scans `Promise.allSettled` results and either throws cancellation or reports failures.

Dependencies/integration points: Used broadly by navbars, storage/quota bars, metadata, tests, and API hooks.

Risks/test signals: `getCapacityPercent` has no zero guard. `removeDuplicatesAndMerge` indexes generic objects by string without constraints. Tests spy on `showDataFetchError` for API failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/common.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/themeIcons.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/themeIcons.tsx

Purpose: Shared custom SVG/CSS icons for charts, storage legends, and replication display.

Important APIs/types/functions: Exports `FilledIcon`, `RatisIcon`, `StandaloneIcon`, `ReplicationIcon`, and `GraphLegendIcon`.

Control flow/state/persistence: `ReplicationIcon` chooses RATIS or STAND_ALONE icon by replication type and wraps it in a tooltip with type/factor/leader details. Other icons render SVG or styled letter glyphs.

Dependencies/integration points: Used by storage/quota bars, datanode/pipeline tables, and graph legends. Relies on CSS classes for visual meaning.

Risks/test signals: Unsupported replication types render null. `GraphLegendIcon` has inline SVG and optional height but fixed circle coordinates, so small heights can clip.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/utils/themeIcons.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/aclDrawer/aclDrawer.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/aclDrawer/aclDrawer.tsx

Purpose: V2 functional ACL drawer for displaying ACLs on volumes/buckets/objects.

Important APIs/types/functions: Default export `AclPanel`, `AclDrawerProps`, `renderAclList`, `renderAclIdentityType`, `COLUMNS`, V2 ACL types/constants.

Control flow/state/persistence: Mirrors `visible` prop into `isVisible` with `useEffect`; uses parent `onClose` for drawer close. Renders AntD Table with typed columns, filtering ACL type and sorting name/type.

Dependencies/integration points: Used by V2 namespace/OM metadata views. Depends on V2 ACL constants and AntD Drawer/Table.

Risks/test signals: Local `isVisible` duplicates controlled prop and can desync briefly. ACL color maps require updates for new ACL enum values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/aclDrawer/aclDrawer.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/breadcrumbs/breadcrumbs.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/breadcrumbs/breadcrumbs.tsx

Purpose: V2 hook-based route breadcrumb renderer.

Important APIs/types/functions: Default export `Breadcrumbs`, uses `useLocation`, `breadcrumbNameMap`, `HomeOutlined`, and `Link`.

Control flow/state/persistence: Splits current pathname, builds cumulative breadcrumb links, prepends home, and renders AntD `Breadcrumb`.

Dependencies/integration points: Used by `app.tsx` when new UI is active. Depends on V2 breadcrumb constants and route names.

Risks/test signals: Unknown path segments display undefined. Assistant route still participates in app header unless specially styled by app shell.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/breadcrumbs/breadcrumbs.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewCardWrapper.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewCardWrapper.tsx

Purpose: V2 link wrapper for overview cards, including OM Insights tab routing.

Important APIs/types/functions: Default export `OverviewCardWrapper`, `OverviewCardWrapperProps`, local `setCurrentActiveTab`.

Control flow/state/persistence: If `linkToUrl === '/Om'`, wraps children in `Link` with `state.activeTab` derived from title. Otherwise wraps in a normal `Link` when `linkToUrl` is non-empty, or returns children unchanged.

Dependencies/integration points: Used by V2 overview cards that navigate to detail pages and OM tabs.

Risks/test signals: Title string matching (`Open Keys Summary`, `Pending Deleted Keys Summary`, `OM Service`) is fragile; renaming cards changes navigation state.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewCardWrapper.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewHealthCard.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewHealthCard.tsx

Purpose: V2 overview health card showing healthy/unhealthy state and availability counts.

Important APIs/types/functions: Default export is named internally `OverviewSummaryCard`; props include `title`, `available`, `total`, optional `linkToUrl`, `loading`, and `error`.

Control flow/state/persistence: Returns `ErrorCard` on missing/error values; otherwise computes `available == total` and renders success/warning icon plus `available/total`, with optional “View More” link in title.

Dependencies/integration points: Used by Overview health sections such as datanode/container health. Depends on AntD Card/Grid, icons, and router Link.

Risks/test signals: Imports `HTMLAttributes`, `Table`, and `ColumnType` but does not use them. Equality uses `==` instead of `===`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewHealthCard.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewSimpleCard.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewSimpleCard.tsx

Purpose: V2 simple metric card with icon, formatted numeric value, optional “View More” link, and error fallback.

Important APIs/types/functions: `IconSelector`, `OverviewSimpleCard`, icon map, and props for `icon`, `data`, `title`, `loading`, `hoverable`, `linkToUrl`, and `error`.

Control flow/state/persistence: On error returns compact `ErrorCard`; otherwise maps the icon string to AntD icon, formats `data` with `numberWithCommas`, and emits `data-testid="overview-${title}"`.

Dependencies/integration points: Used by V2 Overview metric cards and tested through Overview locators.

Risks/test signals: `data` is typed number, so string fallback like `N/A` must be handled before reaching this card. Unknown icons render question mark.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewSimpleCard.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewStorageCard.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewStorageCard.tsx

Purpose: V2 cluster capacity card with ECharts gauge, usage table, modal explanation, and high-usage highlighting.

Important APIs/types/functions: `OverviewStorageCard`, `getUsagePercentages`, `StorageReport`, `EChart`, and modal/table data for Ozone used, non-Ozone used, remaining, and pre-allocated space.

Control flow/state/persistence: Uses `useMemo` for percentages and `useState` for info modal visibility. Builds gauge series from positive percentage segments, links to `/NamespaceUsage`, and marks card border red above 79% usage.

Dependencies/integration points: Used by V2 Overview and Capacity contexts; tests assert `capacity-*` row IDs and formatted values.

Risks/test signals: Division by zero when capacity is 0 produces NaN/Infinity. This file is duplicated under `v2/components/overviewCard/overviewStorageCard.tsx`, creating maintenance drift risk.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewStorageCard.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewSummaryCard.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewSummaryCard.tsx

Purpose: V2 generic summary card with optional lead content and a fixed-layout AntD table.

Important APIs/types/functions: `OverviewSummaryCard`, `TableData`, `OverviewTableCardProps`, and `onRow` test id generation.

Control flow/state/persistence: Returns `ErrorCard` when `error` exists. Otherwise builds a title with optional “View Insights” link and state, renders optional `data`, and renders `tableData` with supplied `columns`.

Dependencies/integration points: Used by overview open-key/delete-pending summaries and tested via `overview-${title}-${record.name}` locators.

Risks/test signals: Table row IDs depend on display names, so label changes break tests. `data` can be string or element; callers own formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/cards/overviewSummaryCard.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/decommissioningSummary/decommissioningSummary.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/decommissioningSummary/decommissioningSummary.tsx

Purpose: Hover popover showing decommissioning details for a datanode UUID.

Important APIs/types/functions: `DecommissionSummary`, `getDescriptions`, `SummaryData`, `useApiData`, and `showDataFetchError`.

Control flow/state/persistence: Fetches `/api/v1/datanodes/decommission/info/datanode?uuid=${uuid}`. While loading shows `Spin`; on error shows AntD `Result`; when summary data has datanode details, metrics, and containers, renders `Descriptions`.

Dependencies/integration points: Used in V2 datanode table/decommission views. Depends on API hook retry/error behavior and datanode types.

Risks/test signals: Query parameter is not URL-encoded. Typo `DecommisioningSummaryProps` is harmless. Empty data leaves spinner-like content until conditions change, potentially ambiguous.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/decommissioningSummary/decommissioningSummary.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/duBreadcrumbNav/duBreadcrumbNav.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/duBreadcrumbNav/duBreadcrumbNav.tsx

Purpose: Namespace Usage/Disk Usage breadcrumb navigation with dropdown subpath drilldown and free-form path search.

Important APIs/types/functions: `DUBreadcrumbNav`, props `path`, `subPaths`, `updateHandler`, and local handlers for menu click, search, breadcrumb click, submenu generation, and current path state.

Control flow/state/persistence: Maintains `currPath` from `path` in state. Breadcrumb clicks construct parent paths; submenu items navigate to non-key subpaths; search appends an entered path segment.

Dependencies/integration points: Used by namespace usage pages with `NUSubpath` data from backend.

Risks/test signals: Path construction comments note double-slash edge cases handled by substring. Menu item keys rely on raw paths. Key subpaths are intentionally not drillable.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/duBreadcrumbNav/duBreadcrumbNav.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/eChart/eChart.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/eChart/eChart.tsx

Purpose: V2 ECharts wrapper with generic event handler support.

Important APIs/types/functions: Default `EChart`, `EChartProps` with `eventHandler`, ECharts `init`, `getInstanceByDom`, `setOption`, loading controls, and resize listener.

Control flow/state/persistence: Initializes/disposes chart on theme changes, registers `onClick` and arbitrary event handler, updates options/settings on dependency changes, and toggles chart loading.

Dependencies/integration points: Used by V2 overview, capacity, and insight plots. Tests often mock it because ECharts needs real layout.

Risks/test signals: Non-null assertions on chart instance can throw if initialization fails. Event handlers are registered on both init and update without removing old handlers, risking duplicates.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/eChart/eChart.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/errors/errorBoundary.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/errors/errorBoundary.tsx

Purpose: Generic React error boundary for V2 UI sections.

Important APIs/types/functions: `ErrorBoundary` class with props `fallback` and `children`, state `hasError`, `getDerivedStateFromError`, `componentDidCatch`, and `render`.

Control flow/state/persistence: Sets `hasError` when descendants throw during render/lifecycle, logs error info to console, and then renders fallback.

Dependencies/integration points: Can wrap fragile chart/table/page sections.

Risks/test signals: No reset behavior when children or route changes, so once tripped it stays tripped until remount. Fallback is generic and logging only goes to console.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/errors/errorBoundary.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/errors/errorCard.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/errors/errorCard.tsx

Purpose: Visual error placeholder card for V2 overview/summary cards.

Important APIs/types/functions: Default `ErrorCard`, props `title` and optional `compact`, uses `DisconnectOutlined` and AntD `Card`.

Control flow/state/persistence: Stateless. Chooses compact or large body padding and emits `data-testid="error-${title}"`.

Dependencies/integration points: Used by V2 overview cards, health cards, and storage cards when data is missing/error.

Risks/test signals: If `title` is a React node, test id becomes unhelpful (`[object Object]`). The card displays only an icon, so accessibility text may be limited.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/errors/errorCard.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/loader/loader.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/loader/loader.tsx

Purpose: Full-area loading spinner for V2 route Suspense and loading states.

Important APIs/types/functions: Default `Loader`, `loaderStyle`, AntD `Spin`, and `LoadingOutlined`.

Control flow/state/persistence: Stateless render of centered green spinner with large icon.

Dependencies/integration points: Used as `Suspense` fallback in `app.tsx` and potentially elsewhere.

Risks/test signals: No accessible label/text. Inline `paddingTop: '25%'` may not center in all layouts, especially Assistant’s special flex layout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/loader/loader.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/navBar/navBar.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/navBar/navBar.tsx

Purpose: V2 sidebar navigation with feature-gated Heatmap and Recon AI links.

Important APIs/types/functions: `NavBar`, `NavBarProps`, `useApiData` calls for disabled features and chatbot health, and route menu items.

Control flow/state/persistence: Fetches `/api/v1/features/disabledFeatures` and chatbot health. Heatmap is shown when `HEATMAP` is not disabled; Assistant is shown when health loaded and enabled. Menu selected key tracks `useLocation().pathname`.

Dependencies/integration points: Used by new UI app shell. Integrates with `CHATBOT_ENDPOINTS.HEALTH`, logo asset, AntD `Sider/Menu`, and route paths.

Risks/test signals: Imports `useEffect` and stores `error` but does not use them. Chatbot link ignores `llmClientAvailable`, while the page itself handles not configured state. False menu items are spread among items.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/navBar/navBar.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/nuMetadata/nuMetadata.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/nuMetadata/nuMetadata.tsx

Purpose: Namespace Usage metadata table that merges namespace summary, quota, and key usage data for a selected path.

Important APIs/types/functions: `NUMetadata`, local response types, `getObjectInfoMapping`, `processMetadata`, `useApiData`, `fetchData`, `removeDuplicatesAndMerge`, and `byteToSize`.

Control flow/state/persistence: Fetches summary and quota in parallel, waits for both to finish and update, then transforms object info, count stats, quota fields, and special KEY usage into table rows. Maintains table state, processing flag, and pagination page; resets page on path change.

Dependencies/integration points: Calls `/api/v1/namespace/summary`, `/api/v1/namespace/quota`, and for keys `/api/v1/namespace/usage?replica=true`. Uses common error notifications.

Risks/test signals: Path is interpolated without URL encoding. KEY branch returns before `finally` resets processing only because `finally` still runs; state may remain stale on some errors. Many response types are local and permissive.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/nuMetadata/nuMetadata.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/overviewCard/overviewStorageCard.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/overviewCard/overviewStorageCard.tsx

Purpose: Duplicate V2 cluster capacity card under an older folder name.

Important APIs/types/functions: Same as `v2/components/cards/overviewStorageCard.tsx`: `OverviewStorageCard`, `getUsagePercentages`, info modal, gauge chart, and usage table.

Control flow/state/persistence: Uses `useState` for info modal and `useMemo` for usage percentages, builds gauge data from storage report, and exposes `capacity-*` test IDs.

Dependencies/integration points: Imports from V2 EChart and overview types. The duplicate path may support older imports during refactor.

Risks/test signals: Exact duplication creates maintenance risk; bug fixes must be applied in both places. Same zero-capacity divide risk and chart rendering concerns apply.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/overviewCard/overviewStorageCard.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/heatmapPlot.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/heatmapPlot.tsx

Purpose: AG Charts treemap renderer for Heatmap data.

Important APIs/types/functions: `HeatmapPlot`, `capitalize`, `tooltipContent`, treemap `heatmapConfig`, and `AgChartsReact`.

Control flow/state/persistence: Builds chart options from `data`, `colorScheme`, and `entityType`. Tooltip shows size, access count or max access count, and entity name. Node click drills into `data.path` only for non-leaf/group nodes without `color`.

Dependencies/integration points: Used by V2 Heatmap page with `HeatmapResponse` and path update callback.

Risks/test signals: Tooltip content is HTML string with interpolated labels. `if (!data.color) if (data.path)` is terse and may misclassify nodes if color is falsy. No tests in this subset cover it.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/heatmapPlot.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/insightsContainerPlot.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/insightsContainerPlot.tsx

Purpose: Pie chart for container size distribution in Insights.

Important APIs/types/functions: `ContainerSizeDistribution`, `ContainerSizeDistributionProps`, `ContainerPlotData`, `updatePlotData`, and ECharts pie options.

Control flow/state/persistence: Aggregates `containerCountResponse` by `containerSize` into a `Map`, derives human-readable power-of-two ranges, stores plot data in state, and updates on response changes. If `containerSizeError` exists, overlays a “No data available” graphic.

Dependencies/integration points: Used by V2 Insights pages and V2 EChart wrapper.

Risks/test signals: `rgba(256, 256, 256, 0.5)` uses out-of-range RGB values. Map key order follows response order, not sorted, so legend/range order can be inconsistent.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/insightsContainerPlot.tsx -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/insightsFilePlot.tsx -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/insightsFilePlot.tsx

Purpose: Bar chart for file size distribution with volume and bucket filters.

Important APIs/types/functions: `FileSizeDistribution`, `handleVolumeChange`, `handleBucketChange`, `updatePlotData`, V2 `MultiSelect`, `FileCountResponse`, and `FilePlotData`.

Control flow/state/persistence: Maintains selected volumes/buckets, bucket option list, bucket select enablement, and sorted file-count map. Volume changes repopulate buckets and selection; plot data filters by selected volumes/buckets, aggregates by file size, sorts ascending, then renders EChart bars. Error state overlays a chart graphic.

Dependencies/integration points: Used by V2 Insights pages and V2 select/chart components.

Risks/test signals: `if (selectedVolumes.length >= 0)` is always true, so empty selected volumes filter out all data. Effects call `updatePlotData` before and after selection updates, causing extra renders.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/v2/components/plots/insightsFilePlot.tsx -->
