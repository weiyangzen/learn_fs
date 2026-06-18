## sources/cloud-native/buildkit/util/network/netproviders/network_unix.go

Purpose: non-Windows host-provider and fallback selection.

Important functions: `getHostProvider` returns `network.NewHostProvider`; `getFallback` logs a warning and returns host provider with resolved mode `"host"`.

State/persistence: none beyond logging. Integration: default network mode on Unix when CNI config is absent. Risks: host fallback may be less isolated than users expect; warning is the only signal. Test signals: no local test.
