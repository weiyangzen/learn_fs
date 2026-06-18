# sources/cloud-native/containerd/internal/cri/config/config.go

## Purpose

`config.go` defines the main CRI image, runtime, CNI, registry, decryption, server, and containerd configuration model plus validation/default-selection helpers.

## Important APIs, Types, and Functions

- Data types include `Runtime`, `ContainerdConfig`, `CniConfig`, `Mirror`, `AuthConfig`, `Registry`, `RegistryConfig`, `ImageDecryption`, `ImagePlatform`, `ImageConfig`, `RuntimeConfig`, `X509KeyPairStreaming`, `Config`, and `ServerConfig`.
- Constants define sandbox controller modes, default pause image, IO modes, implicit runtime names, and key model names.
- `ValidateImageConfig` handles registry deprecations, `config_path` conflicts, auth migration to configs, and image pull timeout parsing.
- `CheckLocalImagePullConfigs` enables local image pull when configured options are incompatible with transfer service.
- `ValidateRuntimeConfig` validates default runtime, CNI bin dir conflicts/migration, runtime cgroup/device/sandboxer/io-type settings, timeout strings, unprivileged kernel support, and CDI deprecation.
- `ValidateServerConfig` validates stream idle timeout.
- `GetSandboxRuntime`, `untrustedWorkload`, and `hostAccessingSandbox` select runtimes and enforce untrusted workload restrictions.
- `GenerateRuntimeOptions` and `getRuntimeOptionsType` marshal generic runtime option maps into runc, runhcs, or generic runtime option structs.
- `DefaultServerConfig` returns CRI server defaults.

## Control Flow

Validation functions both check and normalize config. Runtime validation ensures a default runtime exists, migrates deprecated single CNI bin dir when possible, fills missing `Sandboxer` with `podsandbox`, defaults empty IO type to `fifo`, parses configured durations, and delegates platform-specific unprivileged validation. Image validation warns on deprecated registry fields and maps legacy `auths` into `configs`.

Runtime selection first handles the untrusted workload annotation, rejects explicit conflicting runtime handlers and host namespace access, falls back to default runtime when the handler is empty, and returns the configured runtime by name. Runtime option generation round-trips the map through TOML so typed shim option structs can be populated.

## State and Persistence Behavior

The file defines TOML/JSON-serializable configuration structures. Validation mutates config in memory by filling defaults and migrating deprecated fields; persistence is handled by containerd config loading outside this file.

## Dependencies and Integration Points

It integrates with CRI API types, containerd plugin runtime identifiers, runc/runhcs/runtime option protobuf structs, deprecation warnings, CRI annotations, OCI option helpers, TOML encoding, streaming defaults, and platform-specific defaults/validation files.

## Risks and Edge Cases

Because validation mutates input, callers and tests must compare post-validation state. Deprecated registry settings interact with transfer service fallback and config path conflicts. The IO type error says `named_pipe` even though the accepted constant is `fifo`, which may confuse users. Untrusted workload rules depend on Linux sandbox security context fields and must be kept compatible with Windows handling.

## Test Signals

`config_test.go`, `config_kernel_linux_test.go`, and `streaming_test.go` cover validation errors, warnings, mutation, host-access detection, local-pull fallback, kernel-gated unprivileged settings, and streaming TLS mode selection.
