<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/lib.sh -->
## sources/cloud-native/nydus-snapshotter/tests/helpers/lib.sh

Purpose: generic bash utility library for e2e scripts, covering logging, required-tool checks, host installation, temp directories, tar extraction, HTTP downloads/healthchecks/checksums, and GitHub API helpers.

Important functions/state: log level constants/styles, `log::init`, `log::*`, `host::require`, `host::install`, `fs::mktemp`, `tar::expand`, `_http::get`, `http::get`, `http::healthcheck`, `http::checksum`, `github::settoken`, `github::request`, `github::tags::latest`, and `github::releases::latest`.

Control flow and state: strict bash options are enabled. `_http::get` wraps curl with retry/optional basic auth/TLS restrictions/header injection. GitHub helpers optionally use `GITHUB_TOKEN`; placeholder GitHub Actions expressions are ignored when not on GitHub. At load time it initializes logging and requires `jq`, `tar`, `curl`, and `shasum`.

Dependencies/integration: sourced by project helper scripts. Provides the primitives used by `helpers.sh` and `kind.sh`.

Risks and test signals: `http::checksum` appears to call `http::get -o ...`, but `http::get` expects output then URL, so that helper may be broken if used. Sourcing the library immediately exits if required tools are missing due to strict mode. No shell tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tests/helpers/lib.sh -->
