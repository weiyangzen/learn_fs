## sources/cloud-native/buildkit/util/network/cniprovider/cni_nolinux.go

Purpose: non-Linux stubs for sampling and detached netns handling.

Important functions: `(*cniNS).sample` always returns nil sample and nil error. `withDetachedNetNSIfAny` simply invokes the callback.

State/persistence: none. Dependencies: resource sample type and context.

Integration points: lets shared `cni.go` compile on non-Linux platforms. Risks: no network metrics on non-Linux. Test signals: no local non-Linux tests.
