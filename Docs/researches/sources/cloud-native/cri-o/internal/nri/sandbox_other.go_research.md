# sources/cloud-native/cri-o/internal/nri/sandbox_other.go

Purpose: non-Linux NRI pod sandbox conversion fallback. `podSandboxToNRI` returns the common pod fields without Linux details. There is no state mutation or persistence. Dependencies are containerd NRI adaptation types. Integration allows NRI code to compile on non-Linux platforms while exposing only portable pod fields. Risks include plugins expecting Linux resources/namespaces and behavior divergence from Linux. Test signals are compile-time build tag coverage.
