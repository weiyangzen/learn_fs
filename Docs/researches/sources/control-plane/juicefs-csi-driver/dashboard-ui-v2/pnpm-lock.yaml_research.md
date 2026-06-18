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
