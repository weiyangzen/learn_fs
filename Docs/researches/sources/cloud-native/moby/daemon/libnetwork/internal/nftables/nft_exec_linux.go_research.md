# Research: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nft_exec_linux.go

Purpose: provides the external `nft` command backend when cgo/libnftables is unavailable or disabled. Important APIs are `preflight`, `newNftCtx`, `nftCtx.Apply`, and `Close`, plus cached `lookPathNft`/`lookPathNSEnter`.

Control flow: preflight and context creation require `nft` in PATH. `Apply` starts an OTEL span, builds `nft -f -`, detects rootless detached netns and wraps the command in `nsenter` when needed, starts the command, writes the nft command buffer to stdin, closes stdin, drains stdout/stderr, waits, and returns stderr-enhanced errors. Successful runs log stdout/stderr. `Close` is a no-op because no persistent process exists.

State/dependencies: state is limited to cached executable lookups. Dependencies include `exec`, rootless netns helpers, logging, and OTEL. Integration point is the same `Table.nftApply` path as cgo. Risks include command deadlocks if stdout/stderr handling changes, missing `nsenter` in rootless detached mode, and external command syntax/version differences. Tests use this backend in non-cgo/static/no-libnftables builds.
