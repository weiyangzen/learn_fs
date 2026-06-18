# Research: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nft_cgo_linux.go

Purpose: provides the cgo/libnftables backend for applying nftables command buffers. It is built when cgo, dynamic build, and libnftables are available. Important APIs are `preflight`, `nftCtx.Apply`, `newNftCtx`, and `nftCtx.Close`.

Control flow: `preflight` succeeds because cgo linkage is the capability check. `newNftCtx` allocates a libnftables context, enables output and error buffers, and frees the context on setup failure. `Apply` starts an OTEL span, converts command bytes to a C string, runs `nft_run_cmd_from_buffer`, reads buffered stdout/stderr, returns a formatted error on nonzero status, and logs successful output. `Close` frees the C context.

State/dependencies: state is the libnftables context held by `Table` under an apply lock. Dependencies include cgo, `libnftables`, unsafe pointers, logging, and OTEL. Risks include C string conversion of command bytes, libnftables availability at build/runtime, and memory lifetime across C calls. Tests for nftables behavior exercise this backend when built with cgo/libnftables.
