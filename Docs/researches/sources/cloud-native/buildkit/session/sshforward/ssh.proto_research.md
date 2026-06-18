## sources/cloud-native/buildkit/session/sshforward/ssh.proto

Purpose: declares the wire contract for BuildKit SSH agent forwarding over a session.

Important APIs/types/functions: package `moby.sshforward.v1`, Go package `github.com/moby/buildkit/session/sshforward`. Service `SSH` has `CheckAgent(CheckAgentRequest) returns (CheckAgentResponse)` and `ForwardAgent(stream BytesMessage) returns (stream BytesMessage)`. `BytesMessage` carries raw bytes in field 1. `CheckAgentRequest` carries an agent ID in field 1. `CheckAgentResponse` is empty and acts as existence/permission acknowledgement.

Control flow: the proto itself has no execution, but it drives two runtime flows: checking if an SSH id is available before mounting, and tunneling arbitrary SSH-agent protocol bytes through a bidirectional stream.

State and persistence: no stored state. The stream is session-scoped and transient.

Dependencies and integration points: compiled into `ssh.pb.go`, `ssh_grpc.pb.go`, and `ssh_vtproto.pb.go`; used by `sshforward.MountSSHSocket`, `sshforward.CheckSSHID`, and `sshprovider.socketProvider`.

Risks and test signals: schema is intentionally small. Backward compatibility depends on not renumbering existing fields or changing stream direction. Tests around `raw_provider` validate the stream can tunnel framed JSON payloads, standing in for SSH-agent byte streams.
