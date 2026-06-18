## sources/cloud-native/buildkit/util/network/proxyprovider/provider_unsupported.go

Purpose: non-Linux proxy provider stub.

Important APIs: same `Opt` shape as Linux, `Supported() bool` returns false, `New` returns an unsupported error.

State/persistence: none. Integration: `netproviders` checks `Supported` before constructing proxy provider. Risks: proxy capture/source-policy network proxy features are Linux-only. Test signals: no local tests.
