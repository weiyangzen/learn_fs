# sources/control-plane/csi-lib-utils/config/config.go

## Purpose
This package builds Kubernetes REST configs for CSI sidecars using either an explicit kubeconfig or in-cluster configuration, then applies standard API QPS/burst settings.

## Important APIs, Types, And Functions
Public API is `BuildConfig(kubeconfig string, opts standardflags.SidecarConfiguration)`. Internal `buildConfig` chooses `clientcmd.BuildConfigFromFlags` or `rest.InClusterConfig`.

## Control Flow
`BuildConfig` obtains a config, returns early on error, then sets `config.QPS` and `config.Burst` from `opts.KubeAPIQPS` and `opts.KubeAPIBurst`.

## State, Persistence, And Dependencies
The code is stateless. Dependencies are `client-go/rest`, `clientcmd`, and csi-lib-utils `standardflags`.

## Integration Points
Sidecars can use this after parsing standard flags to construct clients with consistent throttling.

## Risks And Test Signals
There are no tests in this subset. Risks are that zero QPS/burst values from opts overwrite client-go defaults, so callers must pass initialized standard options. Errors come directly from kubeconfig or in-cluster config loading.
