# sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox_ttrpc.pb.go

Purpose: generated TTRPC bindings for the sandbox runtime service.

Important APIs/types/functions: `TTRPCSandboxService` declares the nine sandbox RPC methods. `RegisterTTRPCSandboxService` registers a service name `containerd.runtime.sandbox.v1.Sandbox` with a method map that unmarshals requests and calls the service. `NewTTRPCSandboxClient` returns a client implementing the same interface, with each method calling `ttrpc.Client.Call`.

Control flow: server registration stores closures per method; each closure unmarshals into a request struct and invokes the service. Client methods create response structs, perform a TTRPC call with service/method names, and return the response or error.

State/persistence: no persistent state. Client struct holds the TTRPC client pointer.

Dependencies/integration: imports `context` and `github.com/containerd/ttrpc`. This is the lightweight transport path commonly used by shims.

Risks/test signals: method names must stay exactly aligned with the proto service and gRPC bindings. Tests should cover registration, bad unmarshal errors, per-method client call names, and parity with gRPC behavior.
