# sources/distributed-fs/ipfs-kubo/test/cli/content_blocking_test.go

Purpose: end-to-end denylist/content-blocking coverage across CLI, HTTP gateway, NoFetch gateway, subdomain/IPNS gateway paths, CAR output filtering, and Gateway-over-libp2p.

Important APIs/functions: `TestContentBlocking`, denylist file creation under `$IPFS_PATH/denylists`, `IPFS_NS_MAP`, `carstore.NewReadOnly`, libp2p host/client setup, and many CLI commands (`block`, `dag`, `cat`, `ls`, `get`, `refs`).

Control flow: the test creates allowed and blocked content, writes explicit and double-hash denylist rules, primes namesys mappings, enables GatewayOverLibp2p, starts a daemon, validates allowed reads, then iterates blocked paths across CLI and gateway entry points expecting HTTP 410 or stderr containing the blocked message.

State/persistence: mutates repo denylists, blockstore contents, environment variables, gateway config, daemon restarts for NoFetch, and libp2p streams.

Dependencies/integration: denylist loader/matcher, namesys, gateway path handling, CAR traversal/filtering, CLI content fetchers, NoFetch blockservice swapping, and libp2p HTTP gateway transport.

Risks/test signals: broad regression gate but globally mutates `IPFS_NS_MAP`, so it intentionally avoids top-level parallelism. Duplicate CAR subtest names and path `/subdir` versus `blocked-subdir` should be watched for intent drift.
