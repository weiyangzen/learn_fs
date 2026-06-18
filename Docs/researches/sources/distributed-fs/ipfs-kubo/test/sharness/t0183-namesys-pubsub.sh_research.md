## sources/distributed-fs/ipfs-kubo/test/sharness/t0183-namesys-pubsub.sh

Purpose: validates IPNS over pubsub behavior when enabled by config and when disabled by CLI flag.

Important APIs and helpers: defines `run_ipnspubsub_tests`, uses IPTB, `ipfsi name pubsub state/subs/cancel`, `ipfsi add`, `ipfsi name publish`, `ipfsi name resolve`, `grep`, and config keys for IPNS pubsub.

Control flow and state: initializes an IPTB cluster, checks pubsub state, subscribes nodes to the publisher topic, verifies subscriptions, publishes an IPNS record, waits for propagation, resolves from subscriber nodes, cancels subscriptions, and checks cleanup. It runs enabled configurations, then verifies the command fails when the subsystem is disabled through CLI flag and emits guidance to enable IPNS pubsub.

Dependencies and integration points: covers namesys pubsub topic management, IPNS publication propagation, subscription state, resolver behavior, and feature gating through config/flags.

Risks and test signals: catches pubsub records not flooding, stale subscriptions, disabled feature leakage, and poor error messages. Passing requires successful subscriber resolution and expected disabled-subsystem errors.
