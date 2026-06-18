# sources/cloud-native/soci-snapshotter/internal/archive/compression/doc.go

Purpose: package documentation for the internal configurable decompression package.

Important APIs/types/functions: declares package `compression` with import path `github.com/awslabs/soci-snapshotter/internal/archive/compression` and documents that it defines mechanisms for configuring decompression streams used to unpack image layer tarballs.

Control flow: no runtime behavior.

State and persistence: no state.

Dependencies/integration points: documents that the package was copied and modified from containerd archive compression. The actual implementation in `compression.go` depends on containerd archive compression contracts.

Risks: documentation must stay aligned with supported algorithms and configuration behavior.

Test signals: no direct tests; package behavior is covered by `compression_test.go`.
