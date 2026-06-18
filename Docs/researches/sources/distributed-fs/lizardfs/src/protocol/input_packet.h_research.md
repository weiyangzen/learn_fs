# sources/distributed-fs/lizardfs/src/protocol/input_packet.h

Purpose: Provides `InputPacket`, a small state machine used by servers to incrementally read a packet header and payload from a socket while enforcing a maximum payload length.

Important APIs/types/functions: `InputPacketTooLongException`; constructor with `maxPacketSize`; `reset`; `bytesToBeRead`; `pointerToBeReadInto`; `increaseBytesRead`; `hasHeader`; `getHeader`; `hasData`; `getData`.

Control flow: Before the header is complete, callers read into the fixed header buffer. Once `increaseBytesRead` reaches `PacketHeader::kSize`, the header is deserialized, length is checked against `maxPacketSize_`, and `data_` is resized to the payload length. Subsequent reads fill `data_`; `hasData` becomes true when no bytes remain.

State and persistence: Maintains in-memory read state: serialized header bytes, payload buffer, byte count, and max length. It is reset between packets and has no persistence.

Dependencies and integration: Uses `protocol/packet.h`, common exception and assertion infrastructure. It is suitable for event-loop socket readers that need a stable pointer/count pair for `read`.

Risks and test signals: The caller must call `increaseBytesRead` only after successful reads and must handle zero-length reads externally. `getHeader` aborts on impossible deserialization failure. No direct unit test in this subset covers partial-read edge cases or packet-too-long behavior.
