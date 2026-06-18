# sources/distributed-fs/ipfs-kubo/test/cli/p2p_test.go

Purpose: tests foreground `ipfs p2p listen` and `ipfs p2p forward` behavior when libp2p stream mounting is enabled. It verifies listener/forwarder registration, cleanup on signals, cleanup when closed through `ipfs p2p close`, data-plane tunnel behavior, and command termination when the daemon exits.

Important APIs and helpers: `waitForListenerCount` and `waitForListenerProtocol` poll `ipfs p2p ls --enc=json` and unmarshal `commands.P2PLsOutput` to check listener count and protocol names. The tests use `harness.Node.Runner.Run` with `RunFunc: (*exec.Cmd).Start` for long-running foreground commands, `syscall.SIGTERM` for interrupt simulation, `harness.NewRandPort` for local TCP endpoints, and ordinary `node.IPFS` calls for non-foreground command setup and cleanup.

Control flow: `TestP2PForeground` is a parallel top-level suite with subtests for listen and forward. Each test starts one or two nodes, sets `Experimental.Libp2pStreamMounting=true`, starts daemons, launches foreground p2p commands asynchronously, waits until the daemon reports the listener, then either signals the child process, closes it with `p2p close`, or stops the daemon. Tunnel tests create a local HTTP server, bind a p2p listener on one node and a forwarder on another, and confirm HTTP body bytes cross the p2p tunnel before teardown.

State and persistence: p2p listener state lives in the daemon and is observed through the RPC command. Foreground mode is expected to bind command lifetime to daemon listener lifetime; non-foreground mode is expected to return immediately and leave daemon state until an explicit close. No on-disk persistence is asserted.

Dependencies and integration points: integrates CLI, daemon RPC streaming, libp2p p2p stream mounting, OS process signals, local TCP listeners, and JSON command encoding. It depends on command text such as `waiting for interrupt` and cleanup messages.

Risks and test signals: the tests are timing-sensitive and depend on process signal semantics, available local ports, and RPC stream behavior. They deliberately distinguish SIGTERM output, where cleanup messages may be hidden by stream closure, from `p2p close` output, where both wait and cleanup messages should be visible. Failure signals include leaked listeners, hung foreground commands, missing text output, or broken tunnel data.
