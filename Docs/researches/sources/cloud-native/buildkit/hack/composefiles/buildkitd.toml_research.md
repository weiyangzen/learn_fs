<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/buildkitd.toml -->
# sources/cloud-native/buildkit/hack/composefiles/buildkitd.toml

Purpose: minimal development BuildKit daemon configuration used by the compose environment.

Important APIs, types, and functions: sets `[log].level = "debug"` and `[grpc].debugAddress = "0.0.0.0:6060"`.

Control flow and state: declarative config only. It affects daemon logging verbosity and exposes the debug endpoint inside the compose network and mapped localhost port.

Dependencies and integration: mounted into the `buildkit` service as `/etc/buildkit/buildkitd.toml` by `compose.yaml`.

Risks and test signals: debug logging and `0.0.0.0` binding are intended for local development and should not be reused unreviewed in production. Test with `buildkitd --config` through the compose service and debug endpoint reachability.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/composefiles/buildkitd.toml -->
