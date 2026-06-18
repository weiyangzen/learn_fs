## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin.sh

Purpose: exercises dynamic Go plugin loading, plugin failure handling, disable/re-enable config, plugin-specific config injection, and `--enable-plugins=false` command behavior.

Important commands and control flow: gated by `PLUGIN` prereq. It initializes a repo, confirms `ipfs id` works, writes an executable invalid `.so` and expects `ipfs id` to fail, removes it, builds `t0280-plugin-data/example.go` with `-buildmode=plugin`, and runs `test_plugin` to inspect stderr output. The helper validates whether plugin output is absent or matches expected repo/config lines. The script toggles `Plugins.Plugins.test-plugin.Disabled`, writes plugin config, and checks `--enable-plugins=false` suppresses loading.

State and persistence: modifies `$IPFS_PATH/plugins`, plugin config under `Plugins.Plugins.test-plugin`, and command stderr. The built plugin observes but does not mutate repo state.

Dependencies and integration points: depends on Go plugin support, build flags, plugin loader, Kubo config schema, `ipfs id`, sharness prereqs, and the fixture plugin's stderr contract.

Risks and test signals: strong signal for plugin ABI/load errors, bad plugin isolation, config-disable behavior, and CLI no-plugin flags. It is platform-sensitive because Go plugins are unavailable on some systems.
