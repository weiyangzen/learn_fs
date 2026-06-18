# sources/cloud-native/nydus-snapshotter/pkg/auth/cri.go

Purpose: implements a CRI-backed registry credential provider that captures image pull credentials by installing a proxy ImageService in front of the real CRI image service. It is used as one provider in the registry keychain path.

Important APIs and functions: `DefaultImageServiceAddress` defaults to `/run/containerd/containerd.sock`; package global `credentials []resolver.Credential` stores credential lookup callbacks returned by stargz-snapshotter's CRI keychain; `CRIProvider` implements `AuthProvider` with `String` and `GetCredentials`; `newCRIConn` builds an insecure gRPC client over containerd's dialer with containerd default message sizes and a short max backoff; `AddImageProxy` registers a CRI ImageService proxy on the supplied gRPC server and appends the CRI credential resolver to the global list.

Control flow: `GetCredentials` rejects missing parsers and empty refs, parses the image reference via `parseReference`, then calls each captured CRI credential resolver with `(host, refSpec)`. The first non-empty username or secret is returned as `PassKeyChain`; otherwise the provider reports no credentials for the host. `AddImageProxy` chooses either the configured image service address or the default socket, creates `cri.NewCRIKeychain`, registers its ImageService server into the snapshotter RPC server, and stores the returned resolver callback for later credential reads.

State and persistence: credentials are in-memory only and package-global. There is no persistence and no synchronization around appending or iterating `credentials`; the file comments note it should be embedded in `CRIProvider` and made concurrency safe.

Dependencies and integration points: integrates with containerd CRI over gRPC, containerd dialer defaults, Kubernetes CRI API types, and `github.com/containerd/stargz-snapshotter/service/keychain/cri`. It depends on `parseReference` from `provider.go` and returns `PassKeyChain` from `keychain.go`.

Risks: the global slice can race if `AddImageProxy` and credential lookup run concurrently. Because CRI is pull-time credential capture, restarts lose captured credentials and renewal intentionally excludes CRI. A resolver returning an error aborts the whole provider chain for CRI instead of trying later captured resolvers.

Test signals: `cri_test.go` exercises the no-proxy case, proxy registration, credential capture through `PullImage`, ref mismatches, alternate registries, and digest refs.
