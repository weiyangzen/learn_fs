# sources/distributed-fs/lizardfs/src/protocol/packet.cc

Purpose: Implements `receivePacket`, a blocking helper that reads a full LizardFS/MooseFS packet from a TCP socket into a header and data buffer.

Important APIs/types/functions: `receivePacket(PacketHeader&, std::vector<uint8_t>&, int sock, uint32_t timeout_ms)`; `tcptoread`; `tcpclose`; `deserializePacketHeader`; `kMaxDeserializedBytesCount`.

Control flow: The function asserts the output data buffer is empty, reads exactly the serialized header size, deserializes it, rejects oversized payload lengths, resizes the buffer to the payload length, and reads exactly that payload. On short reads it closes the socket and throws `Exception`.

State and persistence: No persistence. It mutates caller-provided `header` and `data`, and it may close the socket on read failure.

Dependencies and integration: Depends on common socket helpers and `packet.h`. It is a synchronous receive utility for protocol clients/servers that want one complete packet before dispatch.

Risks and test signals: It casts payload length to `int32_t` after bounds check; size limits depend on `kMaxDeserializedBytesCount`. Closing the socket inside the helper is a side effect callers must expect. No direct behavior tests in this subset beyond header-size validation in `packet_unittest.cc`.
