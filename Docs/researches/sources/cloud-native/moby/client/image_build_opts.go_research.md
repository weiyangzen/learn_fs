<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_build_opts.go -->
# sources/cloud-native/moby/client/image_build_opts.go

Purpose: declares the public build option/result structures.

Important APIs/types: `ImageBuildOptions`, `ImageBuildOutput`, and `ImageBuildResult`.

Control flow and dependencies: no runtime flow. The options type references build, container, registry, and OCI platform types plus `io.Reader` for build context.

State and integration behavior: no persistence. The struct is a large public encoding contract for `ImageBuild`, including auth configs, resource limits, BuildKit session/output settings, and build args where `*string` distinguishes empty value from absent value.

Risks and test signals: compatibility risk is high because fields map directly to daemon API query/header/body behavior. `image_build_test.go` and downstream compile-time use are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_build_opts.go -->
