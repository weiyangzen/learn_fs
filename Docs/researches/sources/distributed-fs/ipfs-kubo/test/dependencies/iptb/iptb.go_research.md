## sources/distributed-fs/ipfs-kubo/test/dependencies/iptb/iptb.go

Purpose: embeds the local iptb plugin into a standalone `iptb` test binary for sharness cluster tests.

Important APIs and control flow: `init` registers a `testbed.IptbPlugin` with local plugin callbacks (`NewNode`, `GetAttrList`, `GetAttrDesc`, `PluginName`) as a built-in plugin. `main` creates `cli.NewCli()`, runs it with `os.Args`, prints errors to the CLI error writer, and exits nonzero on failure.

State and dependencies: state is managed by iptb itself, usually under test-controlled directories. Dependencies include `github.com/ipfs/iptb/cli`, `github.com/ipfs/iptb/testbed`, and `github.com/ipfs/iptb-plugins/local`.

Risks: registration panics on failure, so plugin/API drift breaks the binary at startup. Test signal is that sharness helpers can call `iptb init/start/stop/connect` for multi-node clusters without external plugin discovery.
