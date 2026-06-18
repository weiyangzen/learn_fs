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
