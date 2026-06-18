<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/stream-conv.yaml -->
# sources/cloud-native/overlaybd/src/example_config/stream-conv.yaml

Purpose: Example YAML config for the stream convertor component.

APIs and control flow: Defines `globalConfig` fields for work dir, Unix socket address, optional HTTP address, HTTP port, reusePort, and log config.

State and persistence: Points work to `/tmp/stream_conv`, UDS to `/var/run/stream_conv.sock`, and logs to `/var/log/overlaybd/stream_convertor.log`.

Dependencies and integration: Parsed by the stream convertor subdirectory when `BUILD_STREAM_CONVERTOR` is enabled.

Risks and test signals: This subset only builds the option through CMake; functional signals belong to stream convertor tests and startup with yaml-cpp.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/example_config/stream-conv.yaml -->
