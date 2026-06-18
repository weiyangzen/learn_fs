# sources/distributed-fs/ipfs-kubo/core/commands/pubsub.go

## Purpose

`pubsub.go` implements experimental `ipfs pubsub` commands for publishing, subscribing, listing topics, listing peers, and resetting persistent validator sequence-number state. The command is optimized for IPNS-over-PubSub and includes careful multibase URL encoding for binary topic/data values.

## Important APIs, Types, and Functions

`PubsubCmd` registers `pub`, `sub`, `ls`, `peers`, and `reset`. `pubsubMessage` carries multibase data, sender, sequence number, and topic IDs. Helpers include `multibaseDecodedStringListEncoder`, `safeTextListEncoder`, `urlArgsEncoder`, and `urlArgsDecoder`. `pubsubResetResult` reports deleted validator entries.

## Control Flow

`sub` pre-encodes URL args for RPC transport, decodes them server-side, subscribes through `api.PubSub().Subscribe`, flushes HTTP if possible, loops on `sub.Next`, and emits base64url multibase-encoded message fields. Text output decodes and writes message data bytes. Removed `ndpayload` and `lenpayload` encoders return explicit errors. `pub` decodes the topic, reads file/stdin bytes, and publishes them. `ls` gets subscribed topics, encodes them as base64url for structured output, while text output decodes and escapes unsafe characters. `peers` optionally decodes a topic arg, lists peers through CoreAPI, sorts peer IDs, and emits safe text. `reset` directly opens the repo datastore from the live node and deletes validator seqno keys for one decoded peer or all keys under `libp2p.SeqnoStorePrefix`, commits a batch, syncs the datastore prefix, and reports deletion count.

## State and Persistence Behavior

Pub/sub publish, subscribe, ls, and peers use live in-memory/network pubsub state. `reset` mutates persistent datastore validator sequence-number state and can weaken replay protection until state is rebuilt. It does not clear the in-memory seen-message cache.

## Dependencies and Integration Points

Dependencies include CoreAPI PubSub, go-datastore queries/batches, Kubo libp2p seqno prefix, cmdenv, peer IDs, multibase, HTTP flushing, and command encoders. It integrates with config-enabled pubsub and IPNS pubsub router behavior.

## Risks and Test Signals

Risks include binary topic corruption if URL args are not base64url, unbounded subscription lifetimes, reading whole publish payloads into memory, removed encoder compatibility, and destructive reset misuse. Tests should cover URL arg encode/decode, non-base64url rejection, pub/sub binary round trips, text escaping, sorted peers, subscription cancellation, reset one peer/all peers including datastore sync errors, removed encoder errors, and disabled pubsub errors from CoreAPI.
