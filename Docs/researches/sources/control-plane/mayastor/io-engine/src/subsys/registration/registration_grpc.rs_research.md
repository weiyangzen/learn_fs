# sources/control-plane/mayastor/io-engine/src/subsys/registration/registration_grpc.rs

Purpose: implements Mayastor node registration/deregistration and heartbeat-like periodic register messages to a control-plane registration service over tonic gRPC.

Important APIs/types/functions: `ApiVersion` parses `v0`/`v1` and converts to protobuf enum. `Configuration` stores node ID, optional host NQN, advertised gRPC endpoint, heartbeat interval/timeout, supported API versions, and process `instance_uuid`. `Registration` holds config, tonic registration client, receive channel, and fini sender. `GRPC_REGISTRATION` is the global singleton. `init`, `new`, `get`, `instance_uuid`, `fini`, `register`, `deregister`, `run`, and `run_loop` are the main API.

Control flow: `init` creates the singleton lazily. `new` reads heartbeat overrides from `MAYASTOR_HB_INTERVAL_SEC` and `MAYASTOR_HB_TIMEOUT_SEC`, creates a lazy tonic channel with connect/request timeouts and HTTP/2 keepalive settings, and stores an unbounded channel pair. `run` clones the singleton and enters `run_loop`. The loop sends `register` immediately and then either sleeps until the next heartbeat or breaks when the channel closes. On exit it attempts one `deregister`.

State and persistence: registration state is in memory. `instance_uuid` is generated per process start to distinguish restarts. `register` includes node ID, endpoint, instance UUID, API versions, host NQN, feature bits, bugfix bits, and raw version string. No local durable storage is used.

Dependencies and integration points: depends on generated `io_engine_api::v1::registration` client/protos, tonic, futures `select`, async-channel, Mayastor feature/bugfix providers, environment variables, and `version_info`. Called from registration subsystem shutdown and from startup registration wiring elsewhere.

Risks and edge cases: register errors are rate-limited in logs by `show_error`, which avoids log spam but may hide repeated failures. `fini` closes the channel but does not itself await deregistration. `connect_lazy` defers connection errors to RPC time. Invalid heartbeat environment values silently fall back to defaults. The unbounded channel currently carries no implemented messages other than closure.

Test signals: no direct tests in this subset. Integration risk is mainly covered by full control-plane deployments rather than local unit tests.
