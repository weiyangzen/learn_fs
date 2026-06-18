# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/pnpm-lock.yaml lines 7317-9974

## Scope And Purpose

This chunk covers lines 7317-9974 of the `pnpm-lock.yaml` for the Apache Ozone Recon web application. The file is a `lockfileVersion: '9.0'` lockfile generated for `pnpm@10.28.2`; the importer at the top of the file declares a private React/Vite package named `ozone-recon`. The assigned range is in the lockfile's `snapshots:` section, not in the `packages:` metadata section or the application source tree.

These lines define 540 resolved package snapshot records from `is-negative-zero@2.0.3` through `zwitch@2.0.4`. Snapshot records are the dependency graph pnpm uses after package resolution: they record the concrete transitive dependency edges, peer-qualified package identities, optional dependency edges, and transitive peer dependency notes needed to recreate the same `node_modules` layout. The chunk is therefore build and supply-chain infrastructure for the Recon UI, not executable application logic.

The importer ties this graph to the Recon UI's direct dependencies: React 16, React DOM 16, Ant Design 4, React Router 5, React Select 3, ECharts, AG Charts, Axios, Less, Moment, `react-markdown`, `remark-gfm`, TypeScript, Vite, Vitest, Playwright, Testing Library, MSW, `json-server`, ESLint, Prettier, and related tooling.

## Important APIs, Types, And Functions

No JavaScript or TypeScript APIs, types, classes, or functions are declared by this chunk. The important "interfaces" are pnpm lockfile keys and the package-level APIs made available to the rest of the source tree when pnpm installs this graph:

- Snapshot keys such as `react-dom@16.14.0(react@16.14.0)` and `rc-table@7.12.5(react-dom@16.14.0(react@16.14.0))(react@16.14.0)` encode resolved package instances plus peer dependency bindings. This is critical for React libraries because many packages in the chunk are peer-bound to the single React 16 runtime.
- `dependencies:` blocks define exact transitive edges. Examples include `vite@4.5.14` depending on `esbuild`, `postcss`, and `rollup@3.30.0`; `vitest@1.6.1` depending on `vite@5.4.21`, `vite-node`, Chai, Tinybench, Tinypool, and `@vitest/*`; and `json-server@0.15.1` depending on Express, LowDB, Morgan, Request, Yargs, and middleware packages.
- `optionalDependencies:` captures platform-specific or feature-optional packages. Examples in this chunk include `less@3.13.1` optional support packages, `rollup@3.30.0`/`rollup@4.59.0` native bindings and `fsevents`, `vite` optional `@types/node`/`less`/`fsevents`, `web-encoding` optional `@zxing/text-encoding`, and `unrs-resolver` platform bindings.
- `transitivePeerDependencies:` lists peer requirements that pnpm could not flatten into normal dependencies, such as `supports-color`, `encoding`, `bufferutil`, `utf-8-validate`, and style preprocessor peers used by Vite/Vitest.
- Empty snapshots such as `moment@2.30.1: {}` and `typescript@4.9.5: {}` mean the resolved package has no further dependency edges in this lockfile graph.

The package groups most relevant to the Recon app surface are:

- React runtime and UI libraries: `react@16.14.0`, `react-dom@16.14.0`, `scheduler`, `prop-types`, `react-is`, `react-transition-group`, `react-input-autosize`, `react-select`, and many Ant Design `rc-*` primitives including align, cascader, checkbox, collapse, dialog, drawer, dropdown, field form, image, input number, mentions, menu, motion, notification, overflow, pagination, picker, progress, rate, resize observer, select, slider, steps, switch, table, tabs, textarea, tooltip, tree, trigger, upload, util, and virtual list.
- Markdown and API-description rendering stack: `react-markdown@8.0.7`, `remark-gfm@3.0.1`, `remark-parse`, `remark-rehype`, `unified`, `vfile`, `mdast-util-*`, `micromark-*`, `unist-util-*`, `hast`/property/token helpers, and `zwitch`.
- Browser and testing DOM stack: `jsdom@24.1.3`, `parse5`, `nwsapi`, `cssstyle`, `rrweb-cssom`, `whatwg-url`, `whatwg-encoding`, `webidl-conversions`, `w3c-xmlserializer`, `symbol-tree`, `tough-cookie`, `ws`, and `xml-name-validator`.
- Build and test tools: `vite@4.5.14`, `vite@5.4.21`, `vite-node@1.6.1`, `vite-tsconfig-paths@3.6.0`, `vitest@1.6.1`, `rollup@3.30.0`, `rollup@4.59.0`, `magic-string`, `tinyglobby`, `picomatch`, `typescript@4.9.5`, `tsconfig-paths`, `tsutils`, `sucrase`, `prettier@2.8.8`, `table`, and `optionator`.
- Mock API and local development tooling: `json-server@0.15.1`, `lowdb`, `morgan`, `method-override`, `server-destroy`, `body-parser` transitive packages in adjacent chunks, `request@2.88.2`, `msw@1.3.3`, `node-fetch@2.7.0`, `strict-event-emitter`, `outvariant`, and `headers-polyfill`.
- CLI/process helpers: `npm-run-all`, `npm-run-path`, `cross-spawn` transitive helpers, `pidtree`, `shell-quote`, `ora`, `log-symbols`, `update-notifier`, `latest-version`, `package-json`, `yargs@14.2.3`, and `yargs@17.7.2`.

## Control Flow

The chunk has no runtime control flow by itself. Control flow is induced by tools that consume the lockfile:

1. `pnpm install` reads the importer and snapshot graph, resolves exact package instances, installs packages into pnpm's content-addressed store, and creates `node_modules` links that match the peer-qualified snapshot identities.
2. `pnpm start` or the package script `vite --port=3000` uses the locked Vite 4 path for the Recon development server. The snapshot graph fixes Vite's transitive Rollup, Esbuild, PostCSS, Less, and resolver dependencies.
3. `pnpm build` uses the same Vite 4 production build graph. Optional native Rollup packages may be selected according to the host platform, with JavaScript fallback/optional dependency behavior controlled by the lockfile.
4. `pnpm test` runs Vitest 1.6.1. In this graph Vitest is bound to Vite 5.4.21 and Vite Node 1.6.1 rather than the app's direct Vite 4.5.14 build dependency, so test execution can exercise a different Vite major than the production build path.
5. `pnpm e2e` uses Playwright 1.60.0, while `pnpm dev` runs `npm-run-all --parallel mock:api start`, starting the Vite dev server and the `json-server` mock API together.
6. Runtime bundling includes application imports of React, Ant Design, routing, charts, markdown rendering, date/size formatting, and selected utility packages. This chunk contributes many of those resolved transitive packages.

Within a pnpm install, the peer-qualified keys drive branching in the dependency graph. For example, all `rc-*` packages in this range are resolved against `react@16.14.0` and usually `react-dom@16.14.0`; `react-markdown@8.0.7` is resolved against `@types/react@16.8.15` and React 16; `msw@1.3.3` is resolved with `@types/node@25.3.5` and `typescript@4.9.5`; and `vitest@1.6.1` is resolved with `jsdom@24.1.3` and `less@3.13.1`.

## State And Persistence Behavior

The persistent state in this chunk is dependency state: exact package versions and their transitive edges. It is committed so build, test, and development environments resolve the same graph without floating semver decisions on every install.

The chunk also controls the shape of persistent/generated local artifacts outside git:

- pnpm's global store and project `node_modules` symlink layout are derived from these snapshot keys.
- Optional native packages for Rollup, `unrs-resolver`, `fsevents`, and related platform bindings are installed or skipped based on OS/CPU and optional dependency rules.
- `json-server` and `lowdb` are development-time tools for the mock API declared in `package.json`; their runtime data source is the app's `api/db.json` and route/middleware files, not this lockfile.
- `update-notifier` and `configstore` in the `json-server` dependency tree can write user-level notification state when those CLIs run outside CI, depending on package behavior and environment variables.
- `tough-cookie`, `jsdom`, `msw`, and `node-fetch` hold HTTP/cookie state during tests or mocked requests, but those are runtime library behaviors rather than lockfile state.

Because the lockfile pins versions, changes to this chunk are high-signal supply-chain changes. A one-line version drift can change bundler behavior, React peer resolution, testing DOM behavior, markdown parsing, or mock API behavior across the Recon web application.

## Dependencies And Integration Points

The chunk integrates with the source tree through the Recon web app's package scripts and imports:

- `package.json` declares `packageManager: pnpm@10.28.2`, so this lockfile is the authoritative dependency graph for normal installs.
- The app's `start`, `build`, and `serve` scripts consume Vite, Rollup, Esbuild, PostCSS, Less, and resolver packages locked here.
- The `test` script consumes Vitest, Vite Node, JSDOM, Chai, Tinybench, Tinypool, Testing Library dependencies from earlier chunks, and many DOM/URL/XML packages in this range.
- The `e2e` script consumes Playwright packages locked in this range.
- The `mock:api` and `dev` scripts consume `json-server`, `npm-run-all`, `lowdb`, Express middleware packages, Request, Yargs, and process helpers.
- React UI source imports rely indirectly on the locked `rc-*` component graph under Ant Design 4. These packages handle layout, popups, forms, tables, dropdowns, trees, tabs, pickers, upload controls, resize observation, virtual lists, and motion.
- Markdown rendering of Recon UI content relies on `react-markdown`, `remark-gfm`, `unified`, `micromark`, `mdast-util-*`, `unist-util-*`, and `hast` helpers locked in this range.
- ECharts depends on `zrender@5.6.1`, which appears near the end of the chunk and brings `tslib@2.3.0`.

The chunk also records integration edges to external package ecosystems: npm package names and versions, native optional package families for Rollup and `unrs-resolver`, Node/browser polyfill packages, and peer dependency conventions for React, TypeScript, Less, Node types, and optional WebSocket native accelerators.

## Risks And Edge Cases

- The app directly pins Vite 4.5.14, while Vitest is resolved through Vite 5.4.21 in this snapshot graph. That is intentional according to the lockfile, but it creates a split build/test toolchain where a test may pass under Vite 5 behavior while production bundling uses Vite 4.
- React is pinned to 16.14.0 with `@types/react@16.8.15`, while several modern packages in the graph are peer-compatible but newer than the original React 16 ecosystem. Peer-qualified snapshot keys should be preserved carefully to avoid accidental duplicate React installs or invalid hooks behavior.
- `json-server@0.15.1` pulls the deprecated `request@2.88.2` stack, including legacy packages such as `uuid@3.4.0`, `tough-cookie@2.5.0`, `oauth-sign`, and `sshpk`. This is development/mock tooling, but it is still part of the installed dependency graph.
- `update-notifier@3.0.1` is present through `json-server` and can introduce user-environment side effects or noisy network/update checks when CLI tools run outside CI.
- The lockfile includes broad optional native dependency families for Rollup 4 and `unrs-resolver`. Install behavior can vary by platform; CI should exercise the same platform family used for release builds.
- `jsdom@24.1.3` and several `@csstools` packages in other parts of the lockfile require modern Node versions. If the Maven/Ozone build environment uses an older Node runtime, install or test phases may fail even though the application code has not changed.
- Markdown parsing uses a large unified/micromark stack. Changes in this chunk can affect GFM table/task/autolink handling, sanitization-adjacent URL processing, and rendered Recon UI content without changing application code.
- The Ant Design 4 `rc-*` graph is sensitive to exact peer bindings. Upgrading one `rc-*` package independently through lockfile churn can break overlay positioning, table layout, form behavior, date picker behavior, or virtual list rendering.
- The lockfile records `axios@1.16.0` in the importer outside this chunk; this chunk includes supporting URL, proxy, and DOM/test packages. Dependency audits need to merge chunk-level findings with the final whole-file report, because security-relevant packages are distributed across multiple lockfile ranges.

## Test Signals

Useful verification signals for this chunk are dependency and webapp checks:

- Run `pnpm install --frozen-lockfile` in `hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web` to confirm the snapshot graph is internally consistent and no importer/lockfile drift exists.
- Run `pnpm build` to verify Vite 4, Rollup 3, Esbuild, Less, PostCSS, React, Ant Design, charts, markdown, and route bundling still work with the locked graph.
- Run `pnpm test` to verify Vitest 1.6.1 with Vite 5.4.21 and JSDOM 24 still matches the app's unit/integration test assumptions.
- Run `pnpm e2e` where browser dependencies are available to verify Playwright's locked version and the built/dev app still work end to end.
- Run `pnpm dev` or the two constituent scripts to verify `npm-run-all`, Vite dev server, `json-server`, LowDB-backed mock data, route rewrites, and mock pagination middleware start together.
- Run `pnpm lint` to exercise ESLint resolver/parser dependencies outside this chunk but affected by shared package graph state.
- Inspect the installed graph with `pnpm list react react-dom antd rc-table react-markdown remark-gfm vite vitest json-server msw --depth 2` to catch duplicate React instances, unexpected Vite version shifts, or peer-resolution changes.
- For supply-chain review, compare changes in this range with `pnpm-lock.yaml` package metadata above the snapshots section; snapshot-only changes should correspond to explicit package or peer dependency changes, not unexplained lockfile churn.
