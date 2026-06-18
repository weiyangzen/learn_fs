# sources/distributed-fs/beegfs/client_module/source/components/DatagramListener.h

## Purpose
Declares the UDP datagram listener component and send helpers.

## Important APIs and types
`DatagramListener` embeds `Thread` and stores app, receive buffer, local node, net filter, UDP socket/port, send buffer, and send mutex. Inline lifecycle helpers initialize the thread, socket, filter pointers, and mutex; destructors close the socket and free buffers. Inline `DatagramListener_sendto_kernel` serializes send access with `sendMutex`, and `sendtoIP_kernel` builds a sockaddr from IP/port.

## State, dependencies, integration
The component references app-owned local node and net filter and owns its socket and buffers. It is used by `InternodeSyncer` and message processing paths.

## Risks and test signals
Buffers are allocated in the run method, so send paths should not use `sendBuf` before the thread initializes it unless message send allocates its own buffer. Tests should cover initialization error paths and destruction when socket or buffers are null.
