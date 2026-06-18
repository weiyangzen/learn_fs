# sources/control-plane/mayastor/io-engine/src/subsys/registration/mod.rs

Purpose: defines the SPDK registration subsystem wrapper and default control-plane registration endpoint helpers. It connects SPDK fini with the gRPC registration component so Mayastor deregisters on shutdown.

Important APIs/types/functions: `registration_grpc` submodule contains the gRPC implementation. `default_port`, `default_endpoint_str`, and `default_endpoint` provide the default `https://core:50051` endpoint. `RegistrationSubsystem` wraps a raw `spdk_subsystem`. `init` simply advances SPDK init. `fini` checks `MayastorEnvironment::grpc_endpoint`; if registration was enabled and initialized, it calls `Registration::fini()` before advancing SPDK fini. `register` adds the subsystem.

Control flow: registration subsystem initialization has no async work; real registration is run elsewhere. On shutdown, closing the registration component's fini channel signals its run loop to deregister. SPDK fini proceeds immediately after sending that signal.

State and persistence: no durable state. The subsystem raw pointer is boxed and leaked to SPDK. Runtime registration state lives in `registration_grpc::GRPC_REGISTRATION`.

Dependencies and integration points: integrates with SPDK subsystem registration, Mayastor CLI/environment arguments, `http::Uri`, and the gRPC registration singleton. It is part of lifecycle coordination rather than data-plane I/O.

Risks and edge cases: SPDK fini does not await deregistration completion; it only closes the channel. If the registration run loop is not running, `fini` is a no-op beyond closing. Default endpoint uses HTTPS scheme and will panic only if the constant URI becomes invalid.

Test signals: no direct tests in this subset. Behavior is observable only in startup/shutdown integration tests that enable `grpc_endpoint`.
