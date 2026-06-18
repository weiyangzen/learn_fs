<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets_grpc.pb.go -->
# sources/cloud-native/buildkit/session/secrets/secrets_grpc.pb.go

Purpose: generated gRPC bindings for the Secrets session service.

Important APIs, types, and functions: defines `SecretsClient`, `GetSecret` client method, `SecretsServer`, `UnimplementedSecretsServer`, `UnsafeSecretsServer`, `RegisterSecretsServer`, service descriptor, and unary handler.

Control flow and state: client invokes `/moby.buildkit.secrets.v1.Secrets/GetSecret`; server handler decodes request, applies optional interceptor, and dispatches to implementation.

Dependencies and integration: used by `secrets.GetSecret` and `secretsprovider.Register`.

Risks and test signals: service path changes would break compatibility. Generated code should be regenerated from proto. Test through session secret retrieval.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets_grpc.pb.go -->
