# sources/cloud-native/moby/daemon/libnetwork/networkdb/message.go

## Purpose
Encoding/decoding helpers for NetworkDB protobuf gossip messages, including compound messages.

## Important APIs, Types, And Functions
Constants `compoundHeaderOverhead` and `compoundOverhead` estimate packet budget. `encodeRawMessage`, `encodeMessage`, `decodeMessage`, `makeCompoundMessage`, and `decodeCompoundMessage` wrap and unwrap `GossipMessage` and `CompoundMessage`.

## Control Flow
`encodeMessage` marshals a concrete `proto.Message`, wraps it with a `MessageType`, and marshals the envelope. Compound creation wraps each already-encoded message as a simple payload and then envelopes the compound. Decoding unmarshals the envelope, returns type/data, or splits compound payloads in order.

## State And Persistence
No state. The wire format is transient but compatibility-sensitive across cluster nodes.

## Dependencies And Integration Points
Used by broadcast senders, delegate handlers, bulk sync, gossip, and push/pull state exchange. Depends on gogo/protobuf generated NetworkDB message types.

## Risks
`encodeMessage` type-asserts `msg.(proto.Message)`, so wrong callers panic. `makeCompoundMessage` returns nil on marshal error rather than an error, relying on protobuf marshaling not to fail for expected message shapes. Wire format changes affect rolling upgrades.

## Test Signals
No direct tests in this subset; exercised indirectly by NetworkDB cluster behavior.
