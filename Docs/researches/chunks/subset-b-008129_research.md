# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/pnpm-lock.yaml lines 1-7316

## Purpose

This chunk is the first and larger part of the PNPM v9 lockfile for the Apache Ozone Recon web UI package at `hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web`. It records the deterministic dependency graph used to install, build, lint, test, mock, and run the React/Vite Recon frontend. The source package is private `ozone-recon` version `0.2.0` and declares `packageManager: pnpm@10.28.2` in `package.json`, while this lockfile uses `lockfileVersion: '9.0'`.

The covered lines include the global PNPM settings, the root importer, the full `packages:` catalog, and the beginning of the `snapshots:` graph through `is-glob@4.0.3`. Later lockfile lines continue the remaining snapshot resolutions.

## Structure And Important Records

- `settings.autoInstallPeers: true` means PNPM resolves peer dependencies automatically when possible.
- `settings.excludeLinksFromLockfile: false` means linked dependencies are retained in the lockfile if present.
- `importers .` is the root workspace/package importer for the Recon webapp. It pins top-level runtime dependencies and dev dependencies to exact resolved versions.
- `packages:` is the package metadata catalog. Each key is a package/version, optionally with peer context in later snapshot keys. Entries record integrity hashes, binary availability, Node engine constraints, OS/CPU/libc filters, peer dependency contracts, optional peer metadata, and deprecation notes.
- `snapshots:` starts at line 4700. Snapshot records bind concrete package instances to their resolved dependency trees, including peer expansions such as `antd@4.10.3(react-dom@16.14.0(react@16.14.0))(react@16.14.0)`.

This file does not define application APIs, functions, or types. Its "API surface" is the package manager contract consumed by `pnpm install`, `pnpm build`, `pnpm test`, `pnpm e2e`, and any Maven/CI wiring that builds the Recon web assets.

## Root Dependency Profile

The root importer describes an older React 16 UI coupled to a modernized Vite test/build stack:

- UI framework: `react@16.14.0`, `react-dom@16.14.0`, `antd@4.10.3`, `@ant-design/icons@4.8.3`, and a large `rc-*` Ant Design component family.
- Routing and forms/selects: `react-router@5.3.4`, `react-router-dom@5.3.4`, `react-select@3.2.0`.
- Visualization: `ag-charts-community@7.3.0`, `ag-charts-react@7.3.0`, `echarts@5.6.0`, and `zrender@5.6.1`.
- Data and formatting: `axios@1.16.0`, `filesize@6.4.0`, `pretty-ms@5.1.0`, `moment@2.30.1`, `classnames@2.5.1`.
- Markdown rendering: `react-markdown@8.0.7`, `remark-gfm@3.0.1`, and unified/micromark/mdast/hast dependencies.
- Styling/build-time CSS: `less@3.13.1`, `@fontsource/roboto@4.5.8`.
- TypeScript: `typescript@4.9.5` with React 16-era type packages.

Dev tooling in this chunk includes `vite@4.5.14`, `@vitejs/plugin-react-swc@3.11.0`, `vitest@1.6.1`, `jsdom@24.1.3`, `@playwright/test@1.60.0`, Testing Library packages, ESLint 7 plus TypeScript/React/import/promise/prettier plugins, `json-server@0.15.1`, `msw@1.3.3`, `npm-run-all@4.1.5`, and `prettier@2.8.8`.

## Dependency Graph And Control Flow

The install/build control flow is data-driven:

1. PNPM reads the root importer and installs the exact versions from `packages:` and `snapshots:`.
2. Peer resolution threads React 16 and React DOM 16 through Ant Design, `rc-*`, Testing Library, chart wrappers, routers, and selects.
3. Vite uses Rollup and esbuild/SWC packages. Optional native packages are selected by the current platform using `os`, `cpu`, and `libc` constraints.
4. `@vitejs/plugin-react-swc` pulls `@swc/core@1.15.18`, which in turn lists optional platform-specific SWC binaries.
5. `vite@4.5.14` depends on Rollup and esbuild, while the lockfile also contains `vite@5.4.21` as a transitive/peer-related package instance for other tooling context.
6. `vitest@1.6.1` uses `vite-node`, `@vitest/*`, `chai`, `jsdom`, `pretty-format`, `tinyspy`, and Node 18+ supporting packages.
7. Playwright is locked as `@playwright/test@1.60.0`, `playwright@1.60.0`, and `playwright-core@1.60.0`.
8. Mock API/dev support flows through `json-server`, `express`, `lowdb`, `request`, `method-override`, `morgan`, `cors`, and URL rewrite middleware.

The lockfile itself has no runtime branches, but package selection has implicit branch behavior through optional dependencies and platform filters. For example esbuild, Rollup, SWC, and `unrs-resolver` publish many platform-specific packages; only the compatible optional package should be installed for a given host.

## State And Persistence Behavior

The lockfile is persistent build state. It captures:

- Exact resolved versions for semver ranges in `package.json`, such as `^16.8.6` resolving to `react@16.14.0` and `~4.10.3` resolving to `antd@4.10.3`.
- Integrity hashes for supply-chain verification.
- Peer dependency resolutions, including nested peer contexts for React, React DOM, ESLint, TypeScript, Vite, Less, jsdom, and Testing Library.
- Optional platform packages that must remain present in the graph for cross-platform installs.
- Deprecation metadata for transitive packages.

No application state, Recon server state, browser local storage, or backend persistence appears in this file. Changing it changes install reproducibility and can indirectly change build output, test behavior, bundle size, and vulnerability surface.

## Integration Points

- `package.json` scripts consume this graph: `vite --port=3000`, `vite build`, `vitest`, `playwright test`, `json-server --watch api/db.json ... --port 9888`, `npm-run-all --parallel mock:api start`, and ESLint/Prettier commands.
- The React app integrates with Ozone Recon APIs through `axios`; mock API development is represented by `json-server` and `msw`.
- Ant Design 4 integration is broad: `antd` snapshots enumerate many `rc-*` packages for forms, menus, trees, selects, tables, upload, tabs, dialogs, pickers, sliders, pagination, notification, resize observers, virtual lists, and motion.
- Charting integration spans AG Charts React bindings and ECharts/ZRender.
- Markdown integration spans `react-markdown`, `remark-gfm`, `remark-parse`, `remark-rehype`, unified, micromark, mdast, hast, and unist utilities.
- Test integration spans Testing Library for React 16, jsdom for DOM emulation, Vitest for unit tests, and Playwright for browser tests.
- Lint integration spans ESLint 7, `@typescript-eslint` 5, React/import/promise/prettier plugins, and TypeScript resolver packages.

## Compatibility Notes

- Runtime UI dependencies are React 16-era. Testing Library React is locked to `12.1.5`, whose peer range is `<18.0.0`, matching the app.
- Several dev packages require Node 18 or newer: `@playwright/test@1.60.0`, `jsdom@24.1.3`, `vitest@1.6.1`, `vite-node@1.6.1`, `@inquirer/external-editor@1.0.3`, modern `@csstools/*`, `data-urls@5.0.0`, and `whatwg-*` packages. Vite 4 itself supports older Node, but the full dev/test graph effectively requires a newer Node runtime.
- `eslint@7.32.0` is deprecated and no longer supported, but the TypeScript ESLint packages are resolved against it.
- `@types/node@25.3.5` is much newer than `typescript@4.9.5` and the React 16 type set. This may be intentional for current Node APIs, but it is a type-compatibility risk if TypeScript 4.9 cannot parse or model future Node type declarations.
- `less@3.13.1` is older and runs under broad Node support, but modern Vite/plugin packages may exercise CSS handling through newer PostCSS and CSS parser dependencies.

## Notable Risks

- Supply-chain drift risk is concentrated here: edits to versions or integrity fields can change all downstream web build artifacts even if source code is unchanged.
- Deprecated transitive packages appear in the covered chunk, including `eslint@7.32.0`, `request@2.88.2`, `rimraf@3.0.2`, `glob@7.2.3`, `inflight@1.0.6`, `@humanwhocodes/config-array`, `@humanwhocodes/object-schema`, `@xmldom/xmldom@0.8.11`, and `uuid@3.4.0`.
- `@xmldom/xmldom@0.8.11` is marked in the lockfile as having critical issues. It is pulled through MSW/interceptor-related tooling, so exposure is likely test/dev, but it should still be tracked.
- `json-server@0.15.1` brings older Express/request/lowdb-era dependencies and should be treated as development-only.
- The graph mixes old UI packages with newer build/test packages. Upgrades can fail through peer expectations, React 16 compatibility, or Node engine constraints.
- Optional native package coverage is large. Removing apparently unused optional packages from the lockfile can break installs on other OS/CPU/libc combinations.
- Because this chunk ends mid-`snapshots`, analysis of the complete realized dependency tree must be reconciled with later chunks before producing a final per-file report.

## Test Signals

Useful validation after lockfile changes includes:

- `pnpm install --frozen-lockfile` in the Recon webapp directory to confirm the importer, package catalog, snapshots, peer contexts, and integrity hashes are self-consistent.
- `pnpm build` to verify Vite, SWC, Less, React 16, Ant Design 4, charting, markdown, and TypeScript all resolve together.
- `pnpm test` to validate Vitest, jsdom, Testing Library React 12, and MSW-related test dependencies.
- `pnpm e2e` to validate Playwright installation and browser-test dependency resolution.
- `pnpm lint` to catch ESLint 7, TypeScript parser, React plugin, import resolver, and Prettier plugin compatibility.
- For dependency/security work, compare `pnpm audit` results with the known deprecated or critical packages above, while separating dev-only risk from runtime bundle risk.
