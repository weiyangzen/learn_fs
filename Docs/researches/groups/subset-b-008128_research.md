# Research: subset-b-008128

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/pagination.js -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/pagination.js

## Purpose

`pagination.js` is a CommonJS json-server middleware used by the Recon web UI development mock API. It simulates backend-style cursor pagination for unhealthy container endpoints after `json-server` has already rewritten public Recon API paths through `api/routes.json`. The file exists because json-server v0.15 applies custom middlewares after its own URL rewriting, so the middleware must match internal mock resource paths such as `/unhealthyMissing` instead of the original `/api/v1/containers/unhealthy/MISSING`.

The behavior is scoped to five unhealthy-container resources: missing, under-replicated, over-replicated, mis-replicated, and replica-mismatch containers. All other requests are passed through to the next json-server handler.

## Important APIs, Types, and Functions

- `fs.readFileSync(DB_PATH, 'utf-8')` loads `api/db.json` synchronously on each matching request.
- `path.join(__dirname, 'db.json')` anchors the mock database path to the API directory.
- `PATH_TO_KEY` maps rewritten request paths to top-level keys in `db.json`.
- `module.exports = function paginationMiddleware(req, res, next)` exports the Express/json-server middleware.
- `req.path` is the post-rewrite json-server resource path.
- `req.query.limit` and `req.query.minContainerId` are parsed as decimal integers.
- `res.json(...)` sends the paginated response and terminates the middleware chain for supported paths.

There are no custom classes or TypeScript types. The effective response shape contains count fields, `firstKey`, `lastKey`, and `containers`.

## Control Flow

The middleware first resolves `dbKey = PATH_TO_KEY[req.path]`. If the path is not one of the five supported unhealthy-container resources, it calls `next()` immediately.

For supported paths it normalizes query values:

- `limit` defaults to `10` and is clamped to at least `1`.
- `minContainerId` defaults to `0` and is clamped to at least `0`.

It then reads and parses `db.json`. If file reading or JSON parsing fails, it logs an error prefixed with `[pagination]` and falls through via `next()`, allowing json-server's normal route handling to respond.

If the selected `dbKey` is missing from the parsed database, the middleware also calls `next()`. Otherwise, it filters `resource.containers` to entries where `containerID > minContainerId`, sorts the remaining rows ascending by `containerID`, slices the first `limit` entries, calculates `firstKey` and `lastKey` from the resulting page, and returns JSON with all unhealthy count fields plus the page.

## State and Persistence Behavior

The middleware is stateless between requests. It intentionally re-reads `db.json` for every matching request, so edits to mock data are visible without restarting json-server. It does not mutate the request, in-memory resource objects, or `db.json`; sorting is applied after `.filter(...)`, so it sorts a new array rather than the database array itself.

Pagination state is caller-owned. Clients pass the previous page's `lastKey` as `minContainerId` to request the next page. Empty pages return `firstKey: 0`, `lastKey: 0`, and an empty `containers` array.

## Dependencies and Integration Points

This middleware depends on:

- Node built-ins `fs` and `path`.
- json-server/Express middleware semantics for `req`, `res`, and `next`.
- `api/db.json` containing top-level resources named by `PATH_TO_KEY`.
- `api/routes.json` rewriting unhealthy container endpoints to `/unhealthyMissing`, `/unhealthyUnderReplicated`, `/unhealthyOverReplicated`, `/unhealthyMisReplicated`, and `/unhealthyReplicaMismatch`.
- The `mock:api` script in `package.json`, which invokes `json-server --watch api/db.json --routes api/routes.json --middlewares api/pagination.js --port 9888`.

The response contract is intended to match Recon backend unhealthy-container APIs closely enough for the React UI to exercise cursor pagination during local development and tests.

## Risks

- Because the middleware matches rewritten paths, route changes in `routes.json` can silently bypass pagination unless `PATH_TO_KEY` is updated.
- The synchronous file read is simple and acceptable for a local mock server, but it would block the event loop if copied into production code.
- Invalid numeric query values are silently coerced to defaults, which is convenient for mocks but may hide client bugs.
- `parseInt` accepts partial numeric strings, so values such as `10abc` become `10`.
- The filter uses strict `containerID > minContainerId`; duplicate or non-numeric `containerID` values in `db.json` could create skipped, repeated, or unsorted mock pages.
- Count fields are defaulted independently to `0`; inconsistent mock data can report counts that do not match `containers.length`.

## Test Signals

Useful validation is to run the mock API through `pnpm mock:api` or `pnpm dev` and request each unhealthy endpoint with `limit` and `minContainerId` query parameters. The expected signals are ascending `containerID` order, `firstKey`/`lastKey` matching the returned page, no more than `limit` rows, and correct pass-through behavior for unrelated routes. UI-level signals come from pages that request unhealthy containers through the mocked `/api/v1/containers/unhealthy/<state>` endpoints.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/pagination.js -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/routes.json -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/routes.json

## Purpose

`routes.json` is the json-server route rewrite table for the Recon web UI mock API. It maps public Recon REST paths, including query-specific variants, onto top-level collections in `api/db.json`. This allows the Vite/React UI to call production-looking `/api/v1/...` endpoints while local development serves deterministic fixture data from json-server.

The file covers unhealthy containers, namespace usage and metadata, quota, task status, volumes, buckets, heatmaps, feature flags, open/delete-pending keys, container mismatch reports, datanode decommission/remove endpoints, storage distribution, and pending deletion endpoints.

## Important APIs, Types, and Route Groups

The file is pure JSON consumed by json-server's `--routes` option. Keys are request path patterns and values are rewritten mock resource paths. Important groups include:

- Unhealthy containers: `/api/v1/containers/unhealthy/MISSING*`, `UNDER_REPLICATED*`, `OVER_REPLICATED*`, `MIS_REPLICATED*`, and `REPLICA_MISMATCH*` map to `/unhealthy...` resources.
- Generic `/api/v1/*` fallback maps to `/$1`, stripping the API prefix after the specific unhealthy rewrites.
- Namespace usage and summary routes map path/query combinations to `/root`, `/volume`, `/bucket`, `/dir`, `/key`, `/empty`, `/clunky`, `/replica`, `/metadata`, and `/quota`.
- Operational resources map to `/taskStatus`, `/unhealthyContainers`, `/volumes`, `/buckets`, `/disabledFeatures`, and heatmap fixtures.
- Container mismatch routes distinguish `missingIn=OM`, `missingIn=SCM`, and deleted-container variants.
- Open key and delete-pending key routes distinguish FSO, non-FSO, summary, key, and directory fixtures.
- Datanode and pending deletion routes map to decommission, removal, and component-specific deletion resources.

There are no executable functions, but json-server pattern syntax provides wildcard and parameter behavior through entries such as `*`, `:id`, and `$1`.

## Control Flow

json-server evaluates route rewrites before the `pagination.js` middleware listed in `package.json`. More specific rules at the top handle unhealthy-container endpoints before the generic `/api/v1/*` prefix stripper. After rewriting, json-server serves the target collection from `db.json`; for unhealthy-container rewritten paths, `pagination.js` intercepts and returns a custom paginated response instead.

The ordering matters because many patterns include query strings. For example, `/namespace/usage?...` variants distinguish root, volume, bucket, directory, key, empty, clunky, and replica responses. The routes also distinguish mismatch and key-list query combinations such as `missingIn=OM` versus `missingIn=SCM`, or `includeFso=false&includeNonFso=true` versus the reverse.

## State and Persistence Behavior

The route table stores no runtime state. It defines a deterministic mapping between incoming mock API requests and json-server resource names. Persistent fixture state lives in `api/db.json`, and json-server's `--watch` mode reloads that file during local development.

The apparent persistence model seen by the frontend is therefore fixture-based. Collection reads are backed by static JSON resources, while any write-like behavior would be json-server default behavior unless separately handled elsewhere.

## Dependencies and Integration Points

This file integrates with:

- `package.json` script `mock:api`, which passes this file to `json-server --routes`.
- `pagination.js`, which depends on the unhealthy-container rewrites landing on the exact `/unhealthy...` paths.
- `api/db.json`, whose top-level keys must match every rewrite target such as `volumes`, `buckets`, `metadata`, `quota`, `pendingDeletionDN`, and the unhealthy-container collections.
- The React frontend API client code, which issues `/api/v1/...` paths and expects backend-like response shapes.
- Playwright and development workflows that run the Vite frontend against local mock data.

## Risks

- Route matching is brittle where query strings are encoded as full keys. Differences in parameter order, casing, spelling, or omitted optional parameters can miss the intended fixture.
- There is inconsistent spelling/casing in patterns such as `sortSubpaths` and `sortSubPaths`; this likely mirrors client behavior, but future client changes must preserve or update these entries.
- The generic `/api/v1/*` rewrite can mask missing specific routes by rewriting to an unexpected resource name rather than failing clearly.
- `pagination.js` and this file are tightly coupled for unhealthy containers; changing either side alone breaks paginated mock behavior.
- Some routes include empty or unusual query forms, such as `/buckets?volume=` and `/containers/mismatch?&missingIn=OM`, which may not match if the client normalizes URLs differently.
- Fixture names such as `keysdeletePendingSummary`, `keydeletePending`, and `dirdeletePending` must remain aligned with `db.json` despite inconsistent capitalization.

## Test Signals

Validation should exercise representative URLs with json-server running: unhealthy container routes with pagination query parameters, namespace root/volume/bucket/dir/key usage routes, heatmap variants by `entityType`, mismatch routes for OM and SCM, and open/delete-pending key routes. A useful smoke test is to run `pnpm dev` and visit UI screens that use these APIs while watching the browser network panel for 404s or unpaginated unhealthy-container data.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/api/routes.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/e2e/chatbot-errors.spec.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/e2e/chatbot-errors.spec.ts

## Purpose

`chatbot-errors.spec.ts` is a Playwright end-to-end test suite for the Recon AI Assistant error and edge-state UI. It verifies that the Assistant page renders correct disabled/not-configured states, empty state, loading state, successful Markdown rendering, chat error messages for several HTTP failures, and model-fetch fallback behavior.

The suite is deliberately network-isolated for chatbot endpoints: each test intercepts `/api/v1/chatbot/health`, `/api/v1/chatbot/models`, and/or `/api/v1/chatbot/chat` with Playwright `page.route(...)`, then navigates to `/#/Assistant` and asserts visible UI text or rendered elements.

## Important APIs, Types, and Functions

- `test` and `expect` are imported from `@playwright/test`.
- `test.describe('Recon AI Error Handling Scenarios', ...)` groups all Assistant scenarios.
- `page.route('**/api/v1/chatbot/...', async route => route.fulfill(...))` stubs backend responses.
- `page.goto('/#/Assistant')` loads the hash-routed Assistant page using the base URL from `playwright.config.ts`.
- `page.fill('textarea', ...)` and `page.keyboard.press('Enter')` submit chat messages.
- `expect(page.locator(...)).toBeVisible()` asserts UI state.
- `page.screenshot({ path: 'e2e/screenshots/<name>.png' })` stores visual evidence for each scenario.

The mocked response shapes include health fields `enabled` and `llmClientAvailable`, model responses shaped as `{ models: [...] }`, successful chat responses shaped as `{ response, success: true }`, and error responses shaped as `{ error: ... }`.

## Control Flow

The suite contains these tests:

- `health-disabled`: health returns `{ enabled: false, llmClientAvailable: true }`; the page must show `Recon AI is Disabled`.
- `health-not-configured`: health returns `{ enabled: true, llmClientAvailable: false }`; the page must show `Recon AI is Not Configured`.
- `empty-state`: health and models succeed; the page must show `Welcome to Recon AI`.
- `chat-loading`: chat route delays for one second before success; after submitting `Hello`, `.loading-bubble` must be visible.
- `chat-success`: chat returns Markdown containing a GFM table; after submission, a `table` element must be visible.
- `chat-503-busy`: chat returns HTTP 503 with a busy message; the exact busy text must be visible.
- `chat-504-timeout`: chat returns HTTP 504 with a timeout message; the exact timeout text must be visible.
- `chat-500-internal`: chat returns HTTP 500; the UI must show a generic processing error and a server-log hint rather than only the raw backend string.
- `chat-503-interrupted`: chat returns HTTP 503 with an interrupted message; the exact message must be visible.
- `chat-503-disabled`: chat returns HTTP 503 with service-disabled text; the exact text must be visible.
- `models-500`: models endpoint returns HTTP 500 after health succeeds; the Assistant must still show the welcome state and `Default Provider`.
- `models-503`: models endpoint returns HTTP 503 after health succeeds; the Assistant must still show the welcome state and `Default Provider`.

Each test sets its own route handlers, navigates fresh, checks the state, and writes a screenshot.

## State and Persistence Behavior

The tests do not share application state intentionally. Playwright provides an isolated `page` fixture per test by default, and route handlers are registered per page. The UI state under test is transient browser state: health gating state, available-model selection state, chat message list, loading bubble state, and error rendering state.

The only persisted artifacts are screenshots under `e2e/screenshots`. Those files are generated by test runs and are useful for manual inspection or CI artifacts, but the test assertions themselves are DOM-based.

## Dependencies and Integration Points

This suite depends on:

- `@playwright/test`, configured by `playwright.config.ts`.
- The Vite dev server serving the Recon web app at `http://localhost:3000`.
- The React Router hash route `/#/Assistant`.
- Frontend Assistant implementation details such as visible text, a `textarea` input, `.loading-bubble`, Markdown-to-table rendering through `react-markdown` and `remark-gfm`, and fallback provider text `Default Provider`.
- Chatbot API contracts for `/api/v1/chatbot/health`, `/api/v1/chatbot/models`, and `/api/v1/chatbot/chat`.

Because the suite stubs chatbot endpoints, it does not require a live LLM provider or live Recon backend for these scenarios.

## Risks

- The tests use text locators and a CSS class selector, so UI copy or class renames can fail tests even if behavior is still acceptable.
- Pressing `Enter` in a generic `textarea` assumes the Assistant treats Enter as submit; changes to input behavior or accessibility semantics may require stronger selectors.
- The loading test relies on a one-second artificial delay and checks the loading bubble before fulfillment; slow rendering or timing differences could make this flaky.
- Screenshots are always written to fixed paths. Parallel execution can be safe because each test uses a distinct filename, but stale screenshots may be mistaken for current evidence if tests abort before writing.
- The route stubs cover only chatbot endpoints. Other page-level requests may still hit the dev server or mock API and can influence load behavior.
- The `chat-500-internal` assertion expects transformed UI text, while several 503/504 cases expect exact backend strings. Changes to error normalization need coordinated test updates.

## Test Signals

The suite itself is the primary test signal and is run via `pnpm e2e`. Passing results indicate that health gating, model fallback, chat submission, loading feedback, Markdown table rendering, and key error states are visible in Chromium. Generated screenshots under `e2e/screenshots` provide visual confirmation for disabled, not-configured, empty, loading, success, chat-error, and model-error states.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/e2e/chatbot-errors.spec.ts -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/package.json -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/package.json

## Purpose

`package.json` defines the Recon web UI package metadata, dependency graph, development scripts, lint/test commands, browser targets, and mock API proxy. It describes a private Vite-based React 16 application named `ozone-recon` at version `0.2.0`, managed with `pnpm@10.28.2`.

The package supports local UI development, production builds, unit tests, Playwright E2E tests, ESLint checks, and a json-server mock API for backend-like fixtures.

## Important APIs, Types, Scripts, and Dependencies

Key scripts:

- `start`: `vite --port=3000`, serving the frontend dev app.
- `build`: `vite build`, producing production assets.
- `serve`: `vite preview`, serving a built bundle.
- `test`: `vitest`, running unit/component tests.
- `e2e`: `playwright test`, running Playwright specs from the configured test directory.
- `mock:api`: `json-server --watch api/db.json --routes api/routes.json --middlewares api/pagination.js --port 9888`, starting the local fixture API.
- `dev`: `npm-run-all --parallel mock:api start`, running frontend and mock API together.
- `lint` and `lint:fix`: ESLint checks over `src/*`.

Runtime dependencies include React 16, React Router 5, Ant Design 4, Axios, ECharts, AG Charts, React Markdown with GFM support, Moment, Less, Roboto font assets, filesize, classnames, pretty-ms, react-select, and TypeScript.

Development dependencies include Vite 4, the SWC React plugin, Vitest, jsdom, Testing Library, MSW, Playwright, json-server 0.15.1, npm-run-all, ESLint/Prettier tooling, and React/React Router type packages.

## Control Flow

The scripts define the normal developer control flow:

1. `pnpm dev` starts `mock:api` on port 9888 and Vite on port 3000 in parallel.
2. The app calls `/api/v1/...` endpoints; the package-level `proxy` points to `http://localhost:9888` for development mock API traffic.
3. `mock:api` uses `api/routes.json` and `api/pagination.js` to serve fixture data with selected custom behavior.
4. `pnpm e2e` invokes Playwright, whose config starts `pnpm start` unless an existing dev server can be reused.
5. `pnpm build`, `pnpm test`, and lint scripts provide build, unit-test, and static-analysis gates.

No runtime application code is in this file, but the scripts orchestrate the frontend, mock server, and test runner.

## State and Persistence Behavior

Package state is dependency and tooling configuration. Installed package versions are constrained by semver ranges and exact pins in this manifest, while the actual resolved tree is expected to be captured in the package lockfile outside this file.

The `mock:api` script watches `api/db.json`, so fixture changes persist in that JSON file and are reflected during development. Playwright can generate HTML reports and screenshots, but those artifacts are controlled by test configuration and spec files rather than package metadata.

## Dependencies and Integration Points

This manifest integrates with:

- Vite and `playwright.config.ts`, both expecting the app on port 3000.
- json-server mock files `api/db.json`, `api/routes.json`, and `api/pagination.js`.
- React 16 and React Router 5 code under `src`.
- Markdown rendering in the Assistant via `react-markdown` and `remark-gfm`, which is exercised by `chatbot-errors.spec.ts`.
- Ant Design and charting libraries used by Recon dashboards.
- CI or developer commands that rely on `pnpm build`, `pnpm test`, `pnpm e2e`, and lint scripts.

## Risks

- React 16 plus newer testing/dev packages can create peer-dependency pressure, especially with Testing Library and React Markdown versions.
- The app uses Vite 4 and TypeScript 4.9.5; upgrades must account for plugin, JSX, and tsconfig compatibility.
- `axios` is pinned to `1.16.0`; dependency security updates should preserve API behavior in the frontend API layer.
- The `proxy` field is traditionally honored by Create React App, while Vite proxying is usually configured in `vite.config.*`. If the app relies on Vite alone, developers should confirm where API proxying is actually configured.
- `lint` only targets `src/*`, which may miss nested files depending on shell expansion and directory layout.
- `mock:api` is coupled to json-server v0.15 middleware ordering; upgrading json-server can affect `pagination.js`.
- Running Playwright through `pnpm e2e` starts only the Vite server per `playwright.config.ts`, not the `mock:api` server. Tests that do not fully mock backend calls may need `pnpm dev` or a webServer command that starts both services.

## Test Signals

Relevant checks are `pnpm build`, `pnpm test`, `pnpm lint`, `pnpm e2e`, and manual `pnpm dev` smoke testing. For mock API behavior, `pnpm mock:api` plus direct requests to rewritten endpoints validate that `routes.json`, `db.json`, and `pagination.js` still work as a set.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/package.json -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/playwright.config.ts -->
# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/playwright.config.ts

## Purpose

`playwright.config.ts` defines the Playwright test runner configuration for Recon web UI E2E tests. It points tests at the local Vite app, configures Chromium as the only browser project, controls CI retries/workers, enables HTML reporting, and starts the dev server automatically for test runs.

## Important APIs, Types, and Configuration

- `defineConfig` and `devices` are imported from `@playwright/test`.
- `testDir: './e2e'` tells Playwright to discover specs under the `e2e` directory.
- `fullyParallel: true` allows tests to run concurrently.
- `forbidOnly: !!process.env.CI` rejects committed `.only` tests in CI.
- `retries: process.env.CI ? 2 : 0` retries failing tests only in CI.
- `workers: process.env.CI ? 1 : undefined` serializes CI execution while allowing local default parallelism.
- `reporter: 'html'` produces an HTML Playwright report.
- `use.baseURL: 'http://localhost:3000'` lets specs navigate with relative paths such as `/#/Assistant`.
- `use.trace: 'on-first-retry'` captures trace artifacts for retry debugging.
- `projects` contains one Chromium project using `devices['Desktop Chrome']`.
- `webServer.command: 'pnpm start'` launches Vite.
- `webServer.url: 'http://localhost:3000'` is the readiness probe.
- `webServer.reuseExistingServer: !process.env.CI` allows local reuse of an already-running dev server, but forces a fresh managed server in CI.

## Control Flow

When `pnpm e2e` runs, Playwright loads this config, starts `pnpm start` if port 3000 is not already serving the app or if CI requires a managed server, waits for `http://localhost:3000`, discovers tests in `./e2e`, and executes them in the configured Chromium project. On retry in CI, traces are captured for the first retry. Results are written through the HTML reporter.

The `chatbot-errors.spec.ts` suite relies on `baseURL` so `page.goto('/#/Assistant')` resolves to the Vite app. Its chatbot network routes are stubbed inside the test, independent of the webServer command.

## State and Persistence Behavior

This file stores static test runner configuration. Runtime state includes Playwright's report output, trace artifacts generated on first retry, screenshots created by individual tests, and any browser contexts/pages created during tests. It does not persist application data itself.

CI-specific state is controlled through `process.env.CI`: CI gets retries, a single worker, `.only` protection, and no server reuse.

## Dependencies and Integration Points

This config depends on:

- `@playwright/test` and the bundled device descriptors.
- The `start` script in `package.json`, which runs Vite on port 3000.
- E2E specs under `e2e`, including `chatbot-errors.spec.ts`.
- The React app's ability to serve hash routes from the Vite dev server.
- Any backend or mocked network behavior required by individual tests.

It intentionally does not start the json-server mock API. Specs that need backend data must either stub routes with Playwright, rely on frontend fixtures, or run against a separately available mock/backend service.

## Risks

- `fullyParallel: true` can expose shared artifact or shared backend-state conflicts. The current chatbot screenshot names are unique, but future tests need the same discipline.
- CI uses one worker, so local parallel behavior can differ from CI timing and ordering.
- The web server command starts only `pnpm start`, not `pnpm dev`; tests depending on `api/routes.json` or `api/pagination.js` may fail unless they stub calls or a mock API is already running.
- `reuseExistingServer` can hide local server/configuration drift because Playwright may reuse a manually started app with different environment variables.
- Only Chromium/Desktop Chrome is covered; Firefox, WebKit, and mobile layout regressions are not caught by this config.
- HTML reporting is useful for humans but may need explicit CI artifact collection to be retained.

## Test Signals

The main signal is a successful `pnpm e2e` run. In CI, retries and first-retry traces help distinguish flaky failures from deterministic regressions. For broader browser confidence, additional projects for Firefox, WebKit, or mobile devices would be required; they are not currently configured here.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/playwright.config.ts -->
