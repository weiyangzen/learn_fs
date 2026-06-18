# sources/control-plane/longhorn-engine/pkg/interceptor/interceptor.go

Purpose: provides gRPC unary interceptors that attach and validate Longhorn volume and instance identity metadata on controller/replica RPCs.

Important APIs/types/functions: `WithIdentityValidationControllerServerInterceptor` and `WithIdentityValidationReplicaServerInterceptor` return server options with the server type in error messages. `identityValidationServerInterceptor` checks incoming `volume-name` and `instance-name` metadata when exactly one value is present and both sides have non-empty values. `WithIdentityValidationClientInterceptor` returns a dial option. `identityValidationClientInterceptor` appends outgoing metadata keys.

Control flow: server validation is permissive unless both client and server specify a value. Multiple metadata values are ignored rather than rejected. Mismatches return `codes.FailedPrecondition`; matches trace-log and call the underlying handler.

State and persistence: no state beyond closure-captured expected names.

Dependencies and integration points: used by replica and sync gRPC client/server constructors. Depends on gRPC metadata, status codes, and logrus.

Risks: validation is unary-only; streaming RPCs are not covered. Multiple metadata values bypass validation. Empty expected names disable enforcement, which is intentional for compatibility but weakens identity guarantees. Metadata is not cryptographic authentication.

Test signals: no direct tests here. Server/client interceptor tests should cover match, mismatch, empty fields, multiple values, and streaming exclusion.
