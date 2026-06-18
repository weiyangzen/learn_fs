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
