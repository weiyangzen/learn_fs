# sources/cloud-native/nydus-snapshotter/pkg/auth/keychain.go

Purpose: defines the basic username/password credential object and orchestrates the ordered registry credential provider chain used by the snapshotter.

Important APIs and functions: `PassKeyChain` holds `Username` and `Password`; `FromBase64` and `ToBase64` encode/decode Docker-style `username:password`; `TokenBase` treats an empty username with non-empty password as a registry token; `renewableProviders` builds the renewal-only provider list; `buildProviders` builds the normal provider list; `GetRegistryKeyChain`, `getRegistryKeyChainFromProviders`, `fetchFromProviders`, `GetKeyChainByRef`, `Resolve`, and `toAuthConfig` expose keychain lookup and go-containerregistry integration.

Control flow: normal lookup checks the global `renewalStore` first. On a miss, it sets `AuthRequest.ValidUntil` to the next renewal tick when renewal is enabled, then iterates providers in priority order: labels, CRI, Docker, kubelet if initialized, and Kubernetes secrets. The first non-nil keychain wins. Renewable providers that return credentials are cached into the renewal store. Errors from failed providers are collected and joined for one warning if no provider succeeds.

State and persistence: provider constructors and `renewalStore` are package-level variables so tests can replace them. Credentials are in-memory only; no file persistence is done here. `PassKeyChain.Resolve` converts to go-containerregistry `authn.Authenticator`.

Dependencies and integration points: integrates with snapshot labels, CRI provider, Docker config, kubelet credential provider plugins, Kubernetes secrets, go-containerregistry authn, and metrics/renewal through `renewal.go`.

Risks: `FromBase64` uses `strings.Split` and therefore rejects passwords containing additional `:` characters; `SplitN` would be more Docker-compatible. Global provider builders and renewal store need careful test restoration. Provider errors are warning-only when no provider succeeds, which avoids hard failing unauthenticated pulls but can mask misconfiguration.

Test signals: label tests cover base64 round trip; renewal tests cover provider ordering, renewable caching, cached lookup, and non-renewable exclusion.
