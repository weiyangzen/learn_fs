# sources/cloud-native/cri-o/internal/criocli/version.go

Purpose: implements `crio version` output.

Important APIs/types/functions: constants `fullVersionTemplate` and `versionTemplate`; `VersionCommand` with `--json` flag.

Control flow: action gets version information from `version.Get()`. With `--json`, it JSON-encodes the version struct to stdout. Otherwise it applies either full or short text templates depending on `c.App.Version`, printing app version plus git/build details.

State and persistence behavior: writes version text/JSON to stdout; no persistent state.

Dependencies/integration points: urfave/cli, goccy JSON, text/template, and CRI-O internal version package.

Risks: template execution errors are returned. Short template omits git/build details when app version is populated.

Test signals: no direct tests.
