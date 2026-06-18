<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/util -->
# sources/cloud-native/buildkit/hack/util

Purpose: shared shell utility library for BuildKit hack scripts, especially Docker/buildx command wrapping and build context/cache flag preparation.

Important APIs, types, and functions: initializes defaults for `BUILDX_CMD`, `BUILDX_BUILDER`, GitHub Actions metadata, `CONTEXT`, `CACHE_FROM`, and `CACHE_TO`. `dockerCmd` traces and runs `docker`. `buildxCmd` traces and runs the configured buildx command with `BUILDX_NO_DEFAULT_LOAD=true`. `buildAttestFlags` emits SBOM/provenance attest flags when supported and adds a GitHub Actions builder id. The tail logic switches CI builds for `moby/buildkit` to a Git URL context and augments GHA cache specs with repository/token values.

Control flow and state: sourced by other scripts rather than executed directly. Its state is shell variables/functions in the caller process.

Dependencies and integration: used by `hack/compose`, `hack/test`, and other build/test scripts to avoid duplicating Docker/buildx invocation and CI cache handling.

Risks and test signals: because it is sourced, variable names and shell options can affect callers. Cache flag string concatenation is shell-sensitive. Tests are indirect: build/test scripts that source it should still produce expected Docker/buildx commands in local and GitHub Actions environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/util -->
