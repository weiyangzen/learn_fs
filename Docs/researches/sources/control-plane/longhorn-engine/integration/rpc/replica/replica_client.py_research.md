# sources/control-plane/longhorn-engine/integration/rpc/replica/replica_client.py

Purpose: hand-written convenience client for `ptypes.ReplicaService`, used by tests to manage a replica over gRPC.

Important APIs/types/functions: `ReplicaClient.__init__` creates an insecure channel, wraps it with `IdentityValidationInterceptor`, records `url` as `tcp://<address>`, and creates `ReplicaServiceStub`. Methods wrap create/delete/get/open/close/reload/snapshot/expand, disk remove/prepare/mark, rebuild flag setting, and unmap mark-disk-chain-removed setting. Most methods unwrap response `.replica`.

Control flow: each method is a synchronous unary RPC wrapper. Identity validation is enabled only when volume and instance names are provided to the interceptor; defaults disable it.

State and persistence behavior: local state is limited to address/channel/url/stub. Replica disk/snapshot/rebuild state is remote and reflected in returned `Replica` messages.

Dependencies and integration points: depends on `grpc`, `empty_pb2`, `ptypes.replica_pb2`, `ptypes.replica_pb2_grpc`, and `common.interceptor.IdentityValidationInterceptor`. Integrates with identity-aware Longhorn RPC servers.

Risks: `replica_snapshot` uses mutable default `labels={}`. Insecure channel is intended for local integration tests. Wrapper coverage is partial compared with the full generated service; for example disk replace, revision counter, and snapshot max setters are not exposed here.

Test signals: fake-stub unit tests for request construction and response unwrapping; interceptor tests for metadata when volume/instance names are supplied; integration tests against a replica service for create/open/snapshot/remove workflows.
