# sources/cloud-native/containerd/cmd/ctr/commands/events/events.go

Purpose: implements `ctr events`, streaming containerd events and printing them with JSON-decoded payloads.

Important APIs/functions: `Command` action; blank import registers gRPC event types for typeurl decoding.

Control flow: creates client/context, subscribes to event service with CLI filter args, then loops selecting from event and error channels. Each event payload is unmarshaled from Any via typeurl, JSON marshaled, and printed with timestamp, namespace, topic, and payload.

State and persistence: read-only event subscription; no local persistence.

Dependencies/integration: containerd event service, typeurl registry, event type blank import, JSON encoding, log.

Risks: if event channel closes and returns nil repeatedly, loop behavior depends on service channel semantics; error channel returns end the command. Events with unknown Any types are skipped with warnings.

Test signals: no local tests.
