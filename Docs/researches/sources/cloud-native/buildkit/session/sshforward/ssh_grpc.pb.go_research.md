## sources/cloud-native/buildkit/session/sshforward/ssh_grpc.pb.go

Purpose: generated gRPC client and server bindings for the SSH session service.

Important APIs/types/functions: `SSHClient` exposes `CheckAgent` and `ForwardAgent`. `NewSSHClient` wraps a `grpc.ClientConnInterface`. `SSHServer` requires both service methods and should embed `UnimplementedSSHServer` for forward compatibility. `RegisterSSHServer` registers the service. `_SSH_CheckAgent_Handler` and `_SSH_ForwardAgent_Handler` adapt incoming gRPC calls to the server implementation. `SSH_ServiceDesc` names the service and declares unary and stream descriptors.

Control flow: client methods invoke `cc.Invoke` or create a new stream using static method names. Server handlers decode requests or wrap stream objects, then call the implementation.

State and persistence: no persistent state; generated stubs only hold a client connection pointer.

Dependencies and integration points: consumed by `sshforward.CheckSSHID`, `sshforward.server.run`, and `sshprovider.socketProvider.Register`. Depends on gRPC-Go generics for `grpc.BidiStreamingClient[BytesMessage, BytesMessage]` and server aliases.

Risks and test signals: generated code requires gRPC-Go v1.64.0 or newer. Manual edits would be overwritten. Compatibility risk is service/method name stability because session metadata advertises method URLs. Provider tests exercise both unary and streaming generated methods through an in-memory listener.
