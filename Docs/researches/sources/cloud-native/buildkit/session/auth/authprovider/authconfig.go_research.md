<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authconfig.go -->
# sources/cloud-native/buildkit/session/auth/authprovider/authconfig.go

Purpose: declares TLS configuration structures used by Docker auth providers when contacting registries.

Important APIs, types, and functions: `AuthTLSConfig` includes `RootCAs []string`, `Insecure bool`, and `KeyPairs []TLSKeyPair`. `TLSKeyPair` records certificate and key file paths.

Control flow and state: data declarations only.

Dependencies and integration: consumed by `authprovider.tlsConfig` to build `tls.Config` for token fetch HTTP clients.

Risks and test signals: path validation happens later when config is loaded. Tests should cover root CA loading, client certificate loading, insecure mode, and missing files through `tlsConfig`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/auth/authprovider/authconfig.go -->
