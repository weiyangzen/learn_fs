# sources/cloud-native/moby/integration/plugin/common/plugin_test.go

## Purpose
Common plugin API integration coverage: invalid JSON handling for plugin endpoints, plugin install from registries with/without auth/digest/insecure registry, plugins with configured runtimes, and backward-compatible Docker schema2 plugin media types.

## Important APIs, Types, And Functions
Uses raw `request.Post`, plugin fixture helpers (`plugin.Create`, `CreateInRegistry`), test registry helpers, `PluginInstall`, `PluginPush`, `PluginRemove`, `PluginInspect`, `PluginEnable`, `jsonmessage.DisplayStream`, containerd/docker resolver, and OCI manifest decoding. It also writes a temporary runtime wrapper script and daemon config JSON.

## Control Flow
`TestPluginInvalidJSON` posts bad content type, invalid JSON, trailing JSON content, and empty bodies to plugin endpoints and validates HTTP errors are 4xx rather than 5xx. `TestPluginInstall` creates plugin images in local registries and installs them through unauthenticated, digest, htpasswd-authenticated, and insecure registry paths. `TestPluginsWithRuntimes` enables a plugin, configures custom runtimes, restarts the daemon with each default runtime, and checks wrapper side-effect files. `TestPluginBackCompatMediaTypes` pushes a plugin, resolves it with a Docker schema2 accept header, and validates manifest/layer media types.

## State And Persistence Behavior
Tests mutate daemon plugin store, local registry content, runtime config files, and temporary filesystem markers. Plugin install/remove and daemon restart persistence are part of the behavior under test.

## Dependencies And Integration Points
Depends on local daemon, registry test server, containerd image media types, Docker resolver, plugin fixture builder, daemon runtime configuration, and non-Windows plugin support.

## Risks
Registry and network binding assumptions can make install tests flaky. The insecure registry test needs a non-loopback interface. Runtime wrapper tests depend on `runc` being in PATH and rootless is skipped due daemon restart setup issues.

## Test Signals
Signals include HTTP status/error body text for JSON validation, successful plugin inspect after install, extracted push digest, wrapper-created `success` files, and manifest media type/layer count equality.
