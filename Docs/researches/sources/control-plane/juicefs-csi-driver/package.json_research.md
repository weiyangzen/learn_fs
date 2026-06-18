# sources/control-plane/juicefs-csi-driver/package.json

Purpose: documentation tooling manifest for the JuiceFS CSI driver. It is not part of the Go runtime; it defines npm scripts for Markdown linting, link validation, autocorrect checks, and a combined `lint` workflow over `./docs/`.

Important APIs and dependencies: scripts call `markdownlint-cli2`, `remark --quiet --frail`, and `autocorrect`. `remarkConfig` enables heading-id and link validation plugins. Dependencies are documentation-only lint/link tools.

Control flow, state, and integration: execution state is npm dependency installation plus the docs tree being scanned. The manifest integrates with local/CI quality gates, not Kubernetes or CSI code.

Risks: scripts target lowercase `./docs/`, so generated `Docs/researches/` artifacts are outside its normal scope. `autocorrect` is referenced but not declared as an npm dependency. Version ranges may change lint behavior over time.

Test signals: no Go tests apply. The signal is whether `npm run lint` succeeds in an environment with npm dependencies and `autocorrect` available.
