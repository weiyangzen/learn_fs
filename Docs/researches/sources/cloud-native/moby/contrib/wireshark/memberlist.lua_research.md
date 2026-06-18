# sources/cloud-native/moby/contrib/wireshark/memberlist.lua

## Purpose
Implements a Wireshark Lua dissector for HashiCorp memberlist protocol traffic used by Moby networking components.

## APIs, Types, And Functions
The script defines `memberlist_protocol`, protocol fields for message type, CRC, label, encryption, compression, compound parts, and user data, preferences for ports, keylog path, and user-data dissector, plus functions such as `dissect_userdata`, `try_decrypt`, and `memberlist_protocol.dissector`. It also inlines msgpack, LZW, and CRC32 helper code.

## Control Flow, State, And Integration
The dissector registers TCP/UDP ports, optionally decrypts AES-GCM messages using keys from a preference file, validates CRC wrappers, decodes labels, compound messages, push/pull msgpack payloads, compression wrappers, and delegates user payloads to another dissector when configured. State is Wireshark preference state and keylog file contents.

## Risks And Test Signals
Risks include malformed packet handling, keylog file trust, crypto API availability, recursive dissector bugs, and protocol drift. Integration is with Wireshark Lua APIs, protobuf/msgpack dissectors, and Moby network gossip analysis.
