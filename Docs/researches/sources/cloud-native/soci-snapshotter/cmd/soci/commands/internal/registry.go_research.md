## sources/cloud-native/soci-snapshotter/cmd/soci/commands/internal/registry.go

Purpose: shared registry transport/auth flags and credential resolution.

Important APIs/types/functions: registry flag constants, `RegistryFlags`, and `ResolveCredentials`.

Control flow: `ResolveCredentials` prefers explicit `--user username[:password]`; otherwise it loads Docker CLI default config and returns matching host credentials, falling back to empty public credentials.

State and persistence: reads Docker config; does not write.

Dependencies and integration: used by push to configure ORAS remote auth and transport options.

Risks and test signals: TLS and tracing flags are declared but not consumed in the push path shown here. Passwordless `--user` returns empty password. No direct tests here.
