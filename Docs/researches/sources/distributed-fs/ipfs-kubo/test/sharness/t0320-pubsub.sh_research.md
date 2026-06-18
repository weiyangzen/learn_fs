## sources/distributed-fs/ipfs-kubo/test/sharness/t0320-pubsub.sh

Purpose: integration-tests experimental pubsub command behavior across a five-node `iptb` cluster, including config-enabled mode, daemon-flag-enabled mode, unsigned-message filtering, and CLI flag precedence.

Important commands and control flow: initializes a testbed, disables DHT, defines helpers using `ipfsi` to publish, subscribe, list topics, list peers, and verify JSON/base64url payloads. It runs normal pubsub tests after enabling `Pubsub.Enabled`, then again with `--enable-pubsub-experiment`. It disables signing on nodes 1-3 and confirms a subscriber receives no unsigned messages. Finally it sets config enabled but launches daemon with `--enable-pubsub-experiment=false`, expecting pubsub commands to fail with the disabled-feature error.

State and persistence: state includes multi-node configs, daemon flags, FIFOs used to synchronize long-running subscribers, and pubsub topic membership. No durable content is required beyond repo config.

Dependencies and integration points: depends on `iptb`, pubsub router, command JSON encoding, multibase base64url output, shell FIFOs, `jq`, daemon flags, and config precedence.

Risks and test signals: highly timing-sensitive around subscriber readiness and peer discovery. Strongly signals regressions in pubsub enablement, message encoding, signing policy, and config-vs-CLI precedence.
