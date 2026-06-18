# sources/cloud-native/moby/integration/daemon/nri/nri_test.go

Purpose: integration tests for Docker daemon NRI support, including container-create adjustments, unsupported adjustments, injected mounts, and daemon/plugin reload behavior.

Important APIs and helpers: `TestNRIContainerCreateEnvVarMod`, `TestNRIContainerCreateUnsupportedAdj`, `TestNRIContainerCreateAddMount`, and `TestNRIReload`. They use `startBuiltinPlugin`, `builtinPluginConfig`, NRI `api.ContainerAdjustment`, daemon `--nri-opts`, container helpers, and a compiled test plugin.

Control flow: the first three tests start a sub-daemon with NRI enabled on a temp socket, start an in-process plugin, then create containers. Env tests assert plugin-provided or modified environment variables are visible in inspect. Unsupported adjustment tests return hooks, CDI devices, or CPU resource changes and expect daemon create errors. Mount tests prepare a host directory and Docker volume, inject bind/volume mounts with read-only or read-write options, and exec `cat`/`touch` to validate access. Reload test builds `testdata/test_plugin.go`, updates daemon and plugin config files, reloads the daemon, and checks whether new containers receive the configured environment variable.

State and persistence: state spans NRI socket connections, plugin synchronization, daemon JSON config, plugin config files, container config/env, volume data, and reloadable daemon NRI settings.

Dependencies and integration: depends on rootful local Linux daemons, containerd NRI API/stub, Go toolchain for building the external plugin, Docker volumes, mounts, and daemon config reload.

Risks: skipped for remote, Windows, or rootless environments. The tests rely on plugin synchronization before container creation and on reload timing. Build-path assumptions for `./testdata/test_plugin.go` matter.

Test signals: verifies supported NRI env and mount adjustments, rejects unsupported adjustment families, and proves NRI can be enabled, reconfigured, and disabled through daemon reload.
