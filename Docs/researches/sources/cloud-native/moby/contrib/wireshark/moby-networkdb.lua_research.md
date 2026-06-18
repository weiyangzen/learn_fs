# sources/cloud-native/moby/contrib/wireshark/moby-networkdb.lua

## Purpose
Adds Wireshark protobuf decode helpers for Moby NetworkDB gossip payloads.

## APIs, Types, And Functions
The script uses the protobuf dissector, `Field.new` accessors for gossip message type/data and table event names, `last_fieldinfo`, `gossip_proto.dissector`, and `tableevent_proto.dissector`. It registers decode hooks in the `protobuf_field` dissector table.

## Control Flow, State, And Integration
The gossip dissector first decodes a generic `networkdb.GossipMessage`, reads the last parsed type/data fields, chooses a concrete protobuf message type from a map, and recursively decodes the data field. Table events similarly decode values based on table name such as overlay peer or endpoint records.

## Risks And Test Signals
Risks include protobuf field-name drift, missing generated protobuf descriptors in Wireshark, recursive decode failures, and malformed field offsets. Integration is with the memberlist user-data dissector path and Moby overlay/networkdb debugging.
