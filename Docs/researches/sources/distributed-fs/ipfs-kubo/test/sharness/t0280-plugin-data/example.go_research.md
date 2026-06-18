## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-data/example.go

Purpose: provides a minimal Go plugin fixture for Kubo sharness plugin-loading tests. It exports `Plugins`, containing one implementation of `plugin.Plugin`, so `go build -buildmode=plugin` can produce a loadable `.so`.

Important APIs/types/functions: `Plugins` is the symbol Kubo's plugin loader discovers. `testPlugin.Name` returns `test-plugin`; `Version` returns `0.1.0`; `Init` receives `*plugin.Environment` and prints the repo path and config value to stderr with a `testplugin` prefix consumed by the shell test.

State and persistence: the plugin does not mutate Kubo state. It observes environment data and writes diagnostic output to stderr during initialization.

Dependencies and integration points: imports `github.com/ipfs/kubo/plugin`, `fmt`, and `os`. It integrates with the Kubo plugin loader's expected exported symbol and environment contract.

Risks and test signals: any change to plugin discovery, `plugin.Environment`, or Go plugin ABI can break this fixture. Its stderr format is part of `t0280-plugin.sh` assertions and should remain stable.
