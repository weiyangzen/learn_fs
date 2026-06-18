# sources/control-plane/juicefs-csi-driver/package-lock.json lines 1-6446

## Purpose

This chunk is the npm v3 lockfile metadata for the JuiceFS CSI driver repository's documentation quality tooling. The root package is `juicefs-csi-driver` version `1.0.0`, licensed as Apache, and the direct npm dependencies in this range are Markdown/documentation tools rather than CSI runtime code:

- `markdownlint-cli2`
- `markdownlint-rule-enhanced-proper-names`
- `markdownlint-rule-no-trailing-slash-in-links`
- `remark-cli`
- `remark-validate-links`
- `remark-validate-links-heading-id`

The lockfile pins the resolved package graph used to lint Markdown, enforce custom Markdown link/name rules, parse and stringify Markdown with remark/unified, validate internal links and heading IDs, and support Docusaurus-style heading/link behavior. It is generated dependency state, but it is operationally important because it fixes versions, tarball URLs, integrity hashes, executable entry points, peer dependency expectations, optional platform packages, and Node engine constraints for the docs validation lane.

The full lockfile has 562 `packages` entries; this chunk covers the root metadata and most of that package graph through `node_modules/unified-engine/node_modules/yaml` around line 6446. Later lines continue the tail of the lockfile and are outside this chunk's research boundary.

## Important APIs, Types, and Functions

There are no application APIs, Go types, Kubernetes controller functions, or CSI call paths in this chunk. The important "interfaces" are package-lock schema fields and CLI package entry points consumed by npm:

- Root package fields: `name`, `version`, `lockfileVersion: 3`, `requires: true`, and `packages`.
- Per-package fields: `version`, `resolved`, `integrity`, `dependencies`, `optionalDependencies`, `peerDependencies`, `peerDependenciesMeta`, `bin`, `engines`, `license`, `funding`, `deprecated`, `os`, and `hasInstallScript`.
- CLI binaries exposed in this range include `markdownlint-cli2`, `remark`, `webpack`, `svgo`, `terser`, `semver`, `js-yaml`, `json5`, `acorn`, `browserslist`, `markdown-it`, `nopt`, `resolve`, `shjs`, and parser utilities such as `@babel/parser`.
- The highest-level documentation tools are:
  - `markdownlint-cli2@0.21.0`, which resolves to `markdownlint@0.40.0`, `markdown-it@14.1.1`, `jsonc-parser@3.3.1`, `globby@16.1.0`, `micromatch@4.0.8`, and the default formatter.
  - `remark-cli@11.0.0`, which invokes `remark@14.0.2` and `unified-args@10.0.0`.
  - `remark-validate-links@12.1.0`, which depends on `github-slugger`, `hosted-git-info`, `mdast-util-to-string`, `propose`, `to-vfile`, `trough`, `unified`, `unified-engine`, `unist-util-visit`, and `vfile`.
  - `remark-validate-links-heading-id@0.0.3`, which depends on `@docusaurus/utils@2.2.0` and `unist-util-visit`.
  - The two custom markdownlint rules depend on `markdownlint-rule-helpers@0.17.2`.
- Notable transitive subsystems in this chunk include Babel parser/transform packages, SVGR, webpack, micromark CommonMark/GFM/math/directive extensions, Docusaurus utilities, YAML/JSON parsing utilities, glob/path matching utilities, and schema validation utilities such as `ajv`.

## Control Flow

The lockfile itself has no runtime control flow. Its effective control flow is npm installation and CLI execution:

1. npm reads the root `packages[""]` dependency declarations and lockfile version 3 metadata.
2. npm resolves each package from the pinned `node_modules/...` entry instead of re-solving semver ranges.
3. npm verifies each package tarball against `integrity` and installs transitive dependencies, peer dependencies, optional dependencies, and executable `bin` shims.
4. Documentation validation commands then run the installed CLIs:
   - `markdownlint-cli2` loads markdownlint, configuration, formatter, and custom rules.
   - `remark` loads unified/remark processors and plugins such as link validators.
   - `remark-validate-links-heading-id` pulls Docusaurus heading/link behavior through `@docusaurus/utils`.

The dependency graph shape matters because several packages are nested to satisfy conflicting versions. Examples in this chunk include separate `ajv` versions under `ajv-formats` and webpack plugins, `glob`/`minimatch` versions under npm/unified helpers, and nested micromark 1.x and 2.x utilities for different Markdown parsers/extensions.

## State and Persistence Behavior

The persistent state is the lockfile itself. It records reproducible dependency state for documentation tooling:

- Package tarball sources are pinned with `resolved` URLs and Subresource Integrity hashes.
- The graph mixes `registry.npmjs.org` and `registry.npmmirror.com` tarball hosts. In this file, most resolved packages point at `registry.npmmirror.com`, with many newer packages and some direct tools pointing at `registry.npmjs.org`.
- Optional platform behavior is represented by `fsevents@2.3.2`, which is marked `optional: true`, `os: ["darwin"]`, and `hasInstallScript: true`.
- No CSI driver runtime state, Kubernetes object state, mount state, secrets, volumes, cache directories, or external service state are persisted here.
- npm may materialize `node_modules` and CLI shims from this lockfile, but this JSON file does not itself perform filesystem mutation.

Because this is generated dependency state, manual edits risk desynchronizing the lockfile from `package.json` and from the package manager's expected tree. The durable contract is "these exact packages are installed for docs validation."

## Dependencies and Integration Points

This chunk integrates with the repository's documentation and CI/tooling lanes, not the CSI driver's Go runtime:

- `markdownlint-cli2` integrates with markdownlint rules and `.markdownlint-cli2` style configuration if present in the repo. Its pinned version requires Node `>=20`, as does `markdownlint@0.40.0` and nested `globby@16.1.0`.
- Custom rules `markdownlint-rule-enhanced-proper-names` and `markdownlint-rule-no-trailing-slash-in-links` integrate into markdownlint's rule loading through `markdownlint-rule-helpers`.
- `remark-cli` integrates with unified's command-line engine and can load remark plugins/configuration for Markdown transforms or checks.
- `remark-validate-links` integrates with the unified/vfile ecosystem to parse Markdown ASTs, visit links, derive headings with `github-slugger`, and report file/message diagnostics.
- `remark-validate-links-heading-id` integrates with Docusaurus utility behavior, which pulls in a large web-docs support subtree: `@docusaurus/logger`, `@svgr/webpack`, `file-loader`, `url-loader`, `webpack`, `gray-matter`, `js-yaml`, `shelljs`, and filesystem/glob utilities.
- Babel, SVGR, webpack, terser, and WebAssembly packages appear as transitive dependencies of Docusaurus/SVGR/webpack support, not because the CSI driver has a frontend runtime in this chunk.
- The lockfile is coupled to npm's package-lock v3 format; other package managers may not preserve this exact tree.

## Risks and Edge Cases

- Node version is a hard compatibility risk. The root allows modern docs tooling, but `markdownlint-cli2@0.21.0`, `markdownlint@0.40.0`, nested `globby@16.1.0`, `string-width@8.1.0`, `unicorn-magic@0.4.0`, and related packages require Node `>=20`. Older CI images will fail before Markdown checks run.
- The registry mix can affect reproducibility in restricted networks. A build environment that allows only npmjs or only npmmirror may fail to fetch part of the pinned graph even though the integrity hashes are present.
- `fsevents` is optional and Darwin-only. Its install script should be skipped or tolerated on Linux CI, but optional dependency handling must remain enabled for cross-platform installs.
- There is a deprecated package marker for `stable@0.1.8`, pulled transitively through `svgo`. It is not direct application risk, but audit/no-deprecation gates may flag it.
- Several packages are old enough to be audit-sensitive in some policy regimes, including transitive parser, glob, schema, loader, Babel, and webpack ecosystem packages. The lockfile pins them exactly, so vulnerability remediation requires coordinated dependency updates and lock regeneration.
- Peer dependencies must remain satisfied by the current tree. Examples include many Babel plugins requiring `@babel/core`, webpack loaders/plugins requiring `webpack`, `ajv-keywords` requiring compatible `ajv`, and `@docusaurus/utils` having optional `@docusaurus/types`.
- Because the file is generated, reviewing diffs by line count alone is weak. A small direct-dependency bump can legitimately rewrite many transitive entries, registries, integrity hashes, and nested package versions.

## Test Signals

Useful validation signals for this chunk are tooling and reproducibility oriented:

- `npm ci` from `sources/control-plane/juicefs-csi-driver` should install exactly the locked package graph without mutating `package-lock.json`.
- `npm exec markdownlint-cli2 -- --version` or the repository's configured markdownlint command should confirm that the `markdownlint-cli2` binary shim is available and running under Node `>=20`.
- Running the repository's Markdown lint task should exercise `markdownlint-cli2`, `markdownlint`, `markdown-it`, and the two custom markdownlint rules.
- Running the repository's remark/link validation task should exercise `remark-cli`, `remark-validate-links`, `remark-validate-links-heading-id`, unified, vfile reporting, Docusaurus heading ID helpers, and filesystem globbing.
- CI should include a Node version check because this chunk contains mixed engine constraints, with the effective floor raised by markdownlint tooling to Node 20 even though many transitive packages support older versions.
- `npm audit` or the project's chosen dependency scanner should be treated as a signal for this lockfile, but findings need triage as documentation-tooling exposure rather than CSI runtime exposure.
- A clean reinstall should not depend on the host platform except for optional `fsevents`; Linux CI should tolerate its Darwin-only optional status.
