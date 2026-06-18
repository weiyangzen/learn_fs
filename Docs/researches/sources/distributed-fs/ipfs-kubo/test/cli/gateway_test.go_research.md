# sources/distributed-fs/ipfs-kubo/test/cli/gateway_test.go

Purpose: integration coverage for Kubo HTTP gateway, API HTTP edge cases, pprof controls, gateway config flags, IPNS resolution through the gateway, and streaming logs. It exercises a real test daemon through `harness.NewT`, `Node.Init`, `StartDaemon`, `GatewayClient`, and `APIClient`.

Important APIs/functions: `TestGateway` is a large parallel subtest tree; `TestLogs` separately verifies `/logs` streaming with `GOLOG_LOG_LEVEL=info`. Test data is created through `IPFSAddStr`, recursive `ipfs add`, raw `block put`, `name publish`, and direct config mutation through `UpdateConfig`.

Control flow: the main node starts offline for deterministic local gateway tests, then nested subtests request `/ipfs`, `/ipns`, `/webui`, `/api/v0/version`, `/debug/pprof-*`, and content-negotiated trustless gateway paths. Other subtests create fresh nodes for pprof, content-type, fixed gateway-address, `NoFetch`, `DeserializedResponses`, and `DisableHTMLErrors` scenarios.

State and persistence: writes temporary files, imports blocks into the repo, publishes IPNS records, mutates gateway/API config, and checks generated `gateway` repo file contents. Daemons are stopped via cleanup.

Dependencies/integration: uses Kubo config structs, libp2p peer CIDs, multibase base36, multiaddr conversion, HTTP clients, and testify assertions. It directly validates gateway behavior exposed by the CLI daemon and gateway server.

Risks: heavy `t.Parallel` sharing around one gateway client can expose redirect-client mutation hazards; fixed port `32563` may collide; output parsing of daemon stdout and CID list ordering is brittle. Test signals are status codes, headers, body bytes, JSON version fields, pprof methods, file contents, and streamed log lines.
