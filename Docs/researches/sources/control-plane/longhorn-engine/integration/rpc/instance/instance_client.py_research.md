# sources/control-plane/longhorn-engine/integration/rpc/instance/instance_client.py

Purpose: hand-written convenience client for the generated instance-manager RPC API. It wraps `imrpc.instance_pb2_grpc.InstanceServiceStub` and builds protobuf request messages for integration tests or helper scripts.

Important APIs/types/functions: `InstanceClient.__init__` creates an insecure channel and an `InstanceServiceStub`. `version_get` sends `Empty`. `instance_create` builds `ProcessInstanceSpec`, `SpdkInstanceSpec`, and `InstanceSpec`, then calls `InstanceCreate`. `instance_get`, `instance_list`, and `instance_delete` wrap corresponding RPCs. `instance_replace` first calls `InstanceCreate` to obtain an instance spec/value, then passes it to `InstanceReplace` with a terminate signal.

Control flow: methods are synchronous pass-through RPC invocations. `instance_create` always constructs both process and SPDK spec submessages, even when only one backend type may be relevant. `instance_replace` has a two-step flow: create replacement spec via the service, then invoke replace.

State and persistence behavior: the client stores `address`, `channel`, and `stub`. Durable instance state is remote, owned by the instance-manager service, not by this client.

Dependencies and integration points: depends on `grpc`, `google.protobuf.empty_pb2`, `imrpc.instance_pb2`, and `imrpc.instance_pb2_grpc`. Integrates with instance-manager services that understand process-backed and SPDK-backed instance specs.

Risks: default mutable arguments (`port_args=[]`, `args=[]`, `replica_address_map={}`) can leak caller mutation across invocations if modified. The channel is insecure, appropriate for local integration tests but not for untrusted networks. Parameter name `type` shadows the Python built-in. There is little client-side validation, so malformed requests mostly fail remotely.

Test signals: use a fake stub to assert exact protobuf request construction, especially defaults and SPDK/process fields. Integration tests should cover create/get/list/delete/replace against a real or in-process service and confirm replace uses the requested terminate signal.
