# sources/distributed-fs/ipfs-kubo/.github/workflows/gateway-conformance.yml

## Purpose
This workflow validates Kubo's HTTP gateway behavior against `ipfs/gateway-conformance` fixtures on pushes to `master`, pull requests except Markdown-only changes, and manual dispatch. It has two jobs: a regular gateway conformance run over TCP port 8080 and an experimental trustless gateway-over-libp2p run exposed through a local HTTP-over-libp2p proxy.

## Important APIs, Types, And Functions
The workflow uses reusable actions from `ipfs/gateway-conformance`, `actions/checkout`, `actions/setup-go`, and `actions/upload-artifact`. It configures `Gateway.PublicGateways`, runs `make build`, initializes `cmd/ipfs/ipfs`, imports CAR/IPNS/DNSLink fixtures, starts `ipfs daemon`, and invokes the conformance test action with JSON, XML, HTML, and Markdown outputs.

## Control Flow
Both jobs fetch fixtures, build Kubo, initialize a repo, load fixture data, start the daemon, run conformance tests, and always upload summaries/artifacts. The libp2p job also enables `Experimental.GatewayOverLibp2p` and `Experimental.Libp2pStreamMounting`, starts a second proxy node, connects it to the gateway node, and forwards `/http/1.1` over libp2p.

## State And Persistence Behavior
State is temporary GitHub runner state: Kubo repos under checkout directories, imported blocks, IPNS/DNSLink fixtures, daemon processes, `$GITHUB_ENV` DNS map, and generated conformance reports. No repository source is modified.

## Dependencies And Integration Points
It integrates Kubo's gateway config, DAG import, routing put, daemon startup, libp2p p2p forwarding, DNSLink fixture environment, and external gateway-conformance specs. `jq` is assumed in startup readiness checks.

## Risks And Test Signals
Risks include conformance action version drift, daemon readiness races, skipped CAR content-length coverage, port conflicts, and libp2p forwarding instability. Test signals are conformance action status plus uploaded JSON/HTML/Markdown reports and GitHub step summary output.
