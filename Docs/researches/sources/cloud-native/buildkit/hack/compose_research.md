<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/compose -->
# sources/cloud-native/buildkit/hack/compose

Purpose: thin development wrapper for running BuildKit's Docker Compose environment from the repository root.

Important APIs, types, and functions: bash script sources `hack/util`, enables `set -eu -o pipefail`, builds `args=(compose -f "$filesDir/compose.yaml")`, and invokes `dockerCmd "${args[@]}" "$@"`.

Control flow and state: no persistent state beyond Docker/Compose side effects. The script resolves `composefiles` relative to itself and forwards all user arguments.

Dependencies and integration: depends on `hack/util` for Docker CLI discovery and on `hack/composefiles/compose.yaml` plus profile-specific configs. Used by developers to start tracing/metrics/dev BuildKit services.

Risks and test signals: `$(dirname $0)` is unquoted, so paths with spaces are fragile. Compose behavior depends on Docker CLI availability. Test signal is successful `hack/compose config` or `hack/compose up` in a developer environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/compose -->
