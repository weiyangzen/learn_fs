## sources/distributed-fs/ipfs-kubo/test/sharness/t0321-pubsub-gossipsub.sh

Purpose: verifies pubsub behavior when all nodes use the `gossipsub` router.

Important commands and control flow: creates a five-node testbed, sets `Pubsub.Router gossipsub` on every node, starts with `--enable-pubsub-experiment`, captures peer IDs, starts long-running JSON subscribers in the background, checks `pubsub peers`, publishes payloads from file and stdin, and compares subscriber output to base64url-encoded expected values.

State and persistence: runtime-only state covers topic subscriptions, peer IDs, FIFOs, output files, and daemon pubsub state. Config persists router selection in each repo.

Dependencies and integration points: depends on gossipsub configuration, `iptb`, `jq`, multibase encoding, shell FIFOs, and pubsub CLI JSON format.

Risks and test signals: catches router-specific discovery/delivery regressions and JSON encoding changes. Readiness sleeps are a flake risk when cluster startup or subscription propagation slows.
