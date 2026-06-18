# sources/distributed-fs/openafs/src/rx/rx_packet.h

## Purpose
Defines the RX packet wire format, packet buffer sizing constants, packet type/flag constants, `struct rx_header`, jumbo-header metadata, `struct rx_packet`, and packet data access macros used throughout RX.

## Important APIs, Types, And Functions
Important constants include `RX_HEADER_SIZE`, `RX_MIN_PACKET_SIZE`, `RX_MAX_PACKET_SIZE`, `RX_MAX_PACKET_DATA_SIZE`, `RX_PACKET_TYPE_*`, `RX_CLIENT_INITIATED`, `RX_REQUEST_ACK`, `RX_LAST_PACKET`, `RX_MORE_PACKETS`, `RX_SLOW_START_OK`, `RX_JUMBO_PACKET`, `RX_PKTFLAG_*`, `RX_JUMBOBUFFERSIZE`, `RX_JUMBOHEADERSIZE`, `RX_FIRSTBUFFERSIZE`, `RX_CBUFFERSIZE`, and `RX_EXTRABUFFERSIZE`. `struct rx_packet` embeds queue linkage, timing, header, iovec array, local header/data/extradata buffers, length/flags, and optional debug identity. Macros include `RX_CBUF_TO_PACKET`, `rx_DataOf`, `rx_GetDataSize`, `rx_SetDataSize`, checksum accessors, `rx_GetInt32`, `rx_PutInt32`, `rx_packetwrite`, `rx_packetread`, `rx_computelen`, and `rx_Contiguous`.

## Control Flow
This header does not execute by itself; it defines invariants that `rx_packet.c`, `rx_rdwr.c`, and security code rely on. The first iovec is always the RX header, the second is the first data buffer, and later iovecs point at continuation packet buffers. Fast macros operate when data lies in `wirevec[1]`; otherwise they call slow functions that walk iovec entries.

## State And Persistence
The packet structure is the state carrier for all in-flight RX datagrams. It stores host-order header fields, wire buffers, data length, local packet flags, send timing, retransmission serials, and debug metadata. There is no disk persistence.

## Dependencies And Integration Points
The header includes platform iovec definitions or the Windows shim and relies on `RX_MAXWVECS` from configuration. It is included by packet allocation, call read/write, connection, security, listener, and platform networking code. NT, jumbo datagram, and Linux paths rely on `wirehead`, `localdata`, and `extradata` being physically adjacent.

## Risks And Test Signals
Changing sizes or structure layout can break wire compatibility, security padding, Windows sendmsg/recvmsg assumptions, jumbo split logic, and kernel network paths. Test signals include compile coverage across Unix/Windows/kernel variants, max MTU/jumbo interoperability, packet checksum/security tests, and sanitizer or debug checks for out-of-bounds iovec access.
