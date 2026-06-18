# sources/control-plane/juicefs-csi-driver/package-lock.json lines 6447-6808

## Scope

This chunk covers the final portion of the npm v3 lockfile for `sources/control-plane/juicefs-csi-driver`. The source range starts inside the nested `node_modules/unified-engine/node_modules/parse-json` package record and continues through the last package record, `node_modules/zwitch`, and the closing braces of the lockfile.

The root `package.json` for this repository uses npm only for documentation quality gates: `markdownlint-cli2`, two custom markdownlint rules, `remark-cli`, `remark-validate-links`, and `remark-validate-links-heading-id`. The packages in this chunk are transitive dependencies for those commands, primarily unified/remark AST utilities, vfile reporting helpers, webpack-related dependencies pulled by a markdownlint rule package, and small utility packages. They do not participate in the Go CSI driver runtime.

## Purpose

`package-lock.json` pins exact package versions, registry tarball URLs, integrity hashes, engine constraints, executable entry points, and peer dependency relationships for the driver documentation lint/link-check toolchain. This final chunk is important because it closes the `packages` object and records several packages that materially affect whether `npm run lint`, `npm run markdown-lint`, and `npm run check-broken-link` are reproducible.

The dependency groups represented here are:

- Unified and remark support packages for parsing configuration, traversing unist/mdast trees, representing virtual files, and reporting diagnostics.
- Markdownlint rule support packages, including webpack and loader-related transitive dependencies for packaged rule assets.
- CLI-oriented packages with `bin` entries, such as `yaml`, `update-browserslist-db`, `uvu`, and `webpack`.
- Small low-level utilities such as `universalify`, `uri-js`, `util-deprecate`, `walk-up-path`, `wrappy`, `yallist`, and `zwitch`.

Because this is a lockfile chunk, there are no project-defined functions or exported application APIs here. The "APIs" are the locked package records consumed by npm and the command binaries made available under `node_modules/.bin`.

## Important Package Records And Interfaces

`node_modules/unified-engine/node_modules/parse-json` at lines 6444-6456 pins `parse-json@6.0.2` for `unified-engine`. It depends on `@babel/code-frame`, `error-ex`, `json-parse-even-better-errors`, and `lines-and-columns`, and requires Node `^12.20.0 || ^14.13.1 || >=16.0.0`. This package is used when unified/remark tooling reads JSON configuration and needs source-positioned error output.

`node_modules/unified-engine/node_modules/yaml` at lines 6458-6467 pins `yaml@2.5.1` under `unified-engine`. It exposes the `yaml` binary through `bin.mjs` and requires Node `>=14`. This nested copy is separate from the top-level `yaml@1.10.2` later in the chunk, so npm can satisfy different semver ranges without forcing one YAML implementation across all dependents.

The unist utility cluster at lines 6469-6507 pins:

- `unist-util-inspect@7.0.1`, dependent on `@types/unist`.
- `unist-util-is@5.1.1`.
- `unist-util-stringify-position@3.0.2`, dependent on `@types/unist`.
- `unist-util-visit@4.1.1`, dependent on `@types/unist`, `unist-util-is`, and `unist-util-visit-parents`.
- `unist-util-visit-parents@5.1.1`, dependent on `@types/unist` and `unist-util-is`.

These packages form the AST traversal and diagnostic-position layer used by remark plugins. In this repository, they are reached through `remark-cli`, `remark-validate-links`, and `remark-validate-links-heading-id`, which are invoked by `npm run check-broken-link`.

`node_modules/universalify` at lines 6509-6515 pins `universalify@2.0.0`, a callback/promise adapter with a Node `>=10.0.0` engine. It is a compatibility utility rather than a direct command surface.

`node_modules/update-browserslist-db` at lines 6517-6546 pins `update-browserslist-db@1.2.3`. It declares MIT license metadata, multiple funding entries, dependencies on `escalade` and `picocolors`, the executable `update-browserslist-db`, and a peer dependency on `browserslist >= 4.21.0`. It is present because packages such as webpack and Babel-family tooling depend on browserslist metadata. It is not called by the repository scripts directly.

`node_modules/uri-js` at lines 6547-6554 pins `uri-js@4.4.1`, dependent on `punycode`. It is typically used by schema validators and URL-aware tooling in the transitive dependency graph.

`node_modules/url-loader` at lines 6555-6576 pins `url-loader@4.1.1`. It depends on `loader-utils`, `mime-types`, and `schema-utils`; requires Node `>=10.13.0`; peers on `webpack ^4.0.0 || ^5.0.0`; and marks `file-loader` as an optional peer. This loader is not used by the Go driver, but it is part of the JavaScript packaging/tooling dependency closure.

`node_modules/util-deprecate` at lines 6577-6580 pins `util-deprecate@1.0.2`, a small compatibility package used by stream and utility dependencies.

`node_modules/uvu` at lines 6582-6597 pins `uvu@0.5.6`. It depends on `dequal`, `diff`, `kleur`, and `sade`, exposes the `uvu` test-runner binary, and supports Node `>=8`. The repository's npm scripts do not call `uvu`, so this is a transitive test utility shipped by one or more dependencies rather than a project test harness.

The vfile cluster at lines 6599-6655 pins:

- `vfile@5.3.6`, dependent on `@types/unist`, `is-buffer`, `unist-util-stringify-position`, and `vfile-message`.
- `vfile-message@3.1.3`, dependent on `@types/unist` and `unist-util-stringify-position`.
- `vfile-reporter@7.0.4`, dependent on `@types/supports-color`, `string-width`, `supports-color`, `unist-util-stringify-position`, `vfile-sort`, and `vfile-statistics`.
- A nested `supports-color@9.3.1` under `vfile-reporter`, requiring Node `>=12`.
- `vfile-sort@3.0.0`, dependent on `vfile-message`.
- `vfile-statistics@2.0.0`, dependent on `vfile-message`.

These records support the way unified/remark represents files and emits lint/link-check diagnostics. They are directly relevant to `remark --quiet --frail ./docs/`, because failures are surfaced as vfile messages and summarized by reporter/statistics helpers.

`node_modules/walk-up-path` at lines 6656-6659 pins `walk-up-path@1.0.0`, a path traversal utility used by config discovery and filesystem search code in the transitive graph.

`node_modules/watchpack` at lines 6661-6672 pins `watchpack@2.5.1`, a webpack file-watching dependency. It depends on `glob-to-regexp` and `graceful-fs`, carries MIT license metadata, and requires Node `>=10.13.0`.

`node_modules/webpack` at lines 6674-6721 pins `webpack@5.105.0`. It exposes the `webpack` binary, requires Node `>=10.13.0`, declares an optional `webpack-cli` peer, and depends on parsing, resolving, schema validation, source map, minification, and file-watching packages such as `acorn`, `enhanced-resolve`, `es-module-lexer`, `eslint-scope`, `schema-utils`, `terser-webpack-plugin`, `watchpack`, and `webpack-sources`. Its presence is a transitive consequence of the npm documentation lint rule stack, not an indication that this repo builds a frontend bundle for the CSI driver.

`node_modules/webpack-sources` at lines 6722-6730 pins `webpack-sources@3.3.3`, requiring Node `>=10.13.0`.

Nested webpack validation packages at lines 6731-6783 pin:

- `webpack/node_modules/ajv@8.18.0`, dependent on `fast-deep-equal`, `fast-uri`, `json-schema-traverse`, and `require-from-string`.
- `webpack/node_modules/ajv-keywords@5.1.0`, dependent on `fast-deep-equal` and peering on `ajv ^8.8.2`.
- `webpack/node_modules/json-schema-traverse@1.0.0`.
- `webpack/node_modules/schema-utils@4.3.3`, dependent on `@types/json-schema`, `ajv`, `ajv-formats`, and `ajv-keywords`, and requiring Node `>=10.13.0`.

These nested records matter because webpack has stricter schema-utils/AJV requirements than other packages in the lockfile. npm records them under `node_modules/webpack/node_modules/...` to prevent accidental resolution to incompatible top-level versions.

The final utility records are `wrappy@1.0.2` at lines 6784-6787, `yallist@4.0.0` at lines 6789-6792, top-level `yaml@1.10.2` at lines 6794-6800 with Node `>=6`, and `zwitch@2.0.4` at lines 6802-6805. Lines 6806-6808 close the package entry, the `packages` map, and the lockfile root object.

## Control Flow

There is no application control flow inside the lockfile. The operational flow is npm-driven:

1. `npm install` or `npm ci` reads `package-lock.json` with `lockfileVersion: 3`.
2. npm resolves the root dependencies from `package.json`, then uses each `packages["node_modules/..."]` record to install exact transitive versions.
3. npm verifies tarball integrity with each package's `integrity` hash and fetches from each `resolved` URL.
4. npm links package `bin` entries into `node_modules/.bin` where applicable.
5. Repository scripts call selected binaries: `markdownlint-cli2` for markdown linting and `remark` for link validation. The transitive packages in this chunk are loaded by those tools as needed.

Within the remark path, the relevant runtime sequence is:

1. `remark-cli` delegates project/file execution to unified tooling.
2. Unified/remark parses markdown into unist/mdast trees.
3. Plugins such as `remark-validate-links` and `remark-validate-links-heading-id` walk those trees through `unist-util-visit` and related helpers.
4. Diagnostics are represented as `vfile-message` instances on `vfile` objects.
5. `vfile-reporter`, `vfile-sort`, and `vfile-statistics` format and summarize errors. The `--frail` flag makes warnings/errors produce a failing exit status.

Within the webpack-related path, there is no repository script invoking webpack directly. The lockfile only ensures that if a transitive package imports webpack or validates loader options, npm installs the exact compatible webpack, watchpack, schema-utils, AJV, and loader packages recorded here.

## State And Persistence Behavior

The persistent state in this chunk is declarative dependency state:

- Exact package versions are persisted under `packages`.
- Tarball locations are persisted in `resolved` fields, using both `registry.npmjs.org` and `registry.npmmirror.com`.
- Supply-chain verification data is persisted in `integrity` SHA512 hashes.
- Runtime compatibility assumptions are persisted in `engines`.
- CLI surfaces are persisted in `bin`.
- Compatibility constraints across packages are persisted in `peerDependencies` and `peerDependenciesMeta`.

This file does not store runtime state for the CSI driver, Kubernetes resources, JuiceFS mounts, or documentation checks. npm may create or update local `node_modules`, package cache entries, and `.bin` links based on this file, but those are install artifacts outside the lockfile itself.

The nested package paths encode npm's dependency resolution state. For example, `unified-engine/node_modules/yaml@2.5.1` coexists with top-level `yaml@1.10.2`, and `webpack/node_modules/schema-utils@4.3.3` coexists with other possible schema-utils versions. This is intentional lockfile state and should not be flattened manually.

## Dependencies And Integration Points

Primary project integration points are the npm scripts in `sources/control-plane/juicefs-csi-driver/package.json`:

- `markdown-lint` runs `./node_modules/.bin/markdownlint-cli2 './docs/**/*.md'`.
- `markdown-lint-fix` runs the same markdownlint command with `--fix`.
- `check-broken-link` runs `./node_modules/.bin/remark --quiet --frail ./docs/`.
- `lint` composes markdown linting, remark link validation, and `autocorrect --lint ./docs/`.

The chunk integrates with those scripts indirectly:

- Unist and vfile packages support remark's markdown AST traversal and diagnostic reporting.
- `parse-json` and nested `yaml` support unified-engine configuration loading and parse-error reporting.
- `update-browserslist-db`, `watchpack`, `webpack`, `webpack-sources`, `schema-utils`, and nested AJV packages support the webpack/loader dependency closure pulled by markdownlint rule packages.
- `url-loader`'s peer on webpack is satisfied by the locked webpack record in this chunk.
- `update-browserslist-db`'s peer on browserslist is satisfied by an earlier lockfile record outside this chunk.

The chunk has no integration with Go packages under `pkg/`, Kubernetes manifests under `deploy/`, CSI gRPC interfaces, JuiceFS mount logic, or the driver control plane at runtime. Its blast radius is npm-based documentation tooling and any CI lane that runs the npm docs checks.

## Risks And Edge Cases

Mixed registries are visible in this range. Some packages resolve from `registry.npmjs.org`, while others resolve from `registry.npmmirror.com`. That may be intentional for local mirror performance, but it is a supply-chain and reproducibility detail: CI environments must be able to reach both registries or have an npm config that can honor the lockfile.

Node engine requirements vary. The strictest visible requirement in this chunk is Node `>=14` for nested `yaml@2.5.1`; several other packages require Node `>=12`, `>=10.13.0`, `>=10`, `>=8`, or `>=6`. Even though the root `package.json` does not declare an engine, the docs tooling can fail on older Node versions because npm and Node must satisfy transitive `engines`.

Peer dependency correctness is important. `url-loader` peers on webpack and optionally `file-loader`; `webpack` optionally peers on `webpack-cli`; `update-browserslist-db` peers on browserslist; `webpack/node_modules/ajv-keywords` peers on AJV. Manual lockfile edits or partial dependency upgrades can leave peer relationships inconsistent even when JSON syntax remains valid.

There are multiple versions of similar libraries. `yaml@2.5.1` is nested under `unified-engine` while `yaml@1.10.2` is top-level; `schema-utils@4.3.3` is nested under webpack while `url-loader` depends on `schema-utils ^3.0.0` elsewhere in the lockfile. Research and upgrade work should preserve the owning package path, not just the package name.

The webpack-related dependencies can be mistaken for an application frontend build. In this repository they are transitive docs-tooling dependencies. Removing them because the CSI driver is written in Go can break markdown rule packages or their bundled asset processing.

Lockfile-only dependency changes are hard to reason about in isolation. Any update to a record in this chunk should be generated by npm from `package.json` and the dependency graph, then verified with the actual npm scripts. Hand-editing integrity hashes, nested package placement, or peer metadata risks producing installs that are unreproducible or rejected by `npm ci`.

Because this chunk ends the JSON document, syntax errors here break the entire lockfile. Missing commas, mismatched braces, or truncating the final `packages`/root close at lines 6806-6808 would prevent all npm installation and docs checks from starting.

## Test Signals

Useful verification signals for this chunk are npm and docs-tooling oriented:

- `npm ci` from `sources/control-plane/juicefs-csi-driver` should complete without modifying `package-lock.json`.
- `npm run markdown-lint` should find `markdownlint-cli2` through `node_modules/.bin` and load its locked transitive dependency graph.
- `npm run check-broken-link` should run `remark --quiet --frail ./docs/`, exercise unified/unist/vfile packages from this chunk, and fail only on actual documentation diagnostics.
- `npm run lint` should compose markdownlint, remark link validation, and autocorrect checks without dependency-resolution failures.
- `npm ls webpack url-loader schema-utils ajv yaml vfile unist-util-visit` can confirm that nested package versions match the package paths recorded in the lockfile.
- JSON parsing of `package-lock.json` should succeed, especially because this chunk contains the final object closings.

For dependency-maintenance tests, the highest-signal checks are that npm does not rewrite the lockfile and that CI docs checks continue to produce the same class of markdown/link diagnostics rather than module resolution, peer dependency, or engine failures.
