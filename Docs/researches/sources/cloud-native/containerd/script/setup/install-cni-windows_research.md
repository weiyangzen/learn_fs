<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-cni-windows -->
# sources/cloud-native/containerd/script/setup/install-cni-windows

- Purpose: Builds Microsoft Windows CNI binaries and generates a NAT CNI config for Windows containerd testing.
- Important functions: `split_ip` decomposes IPv4 addresses; `calculate_subnet` builds a subnet from gateway and prefix length.
- Control flow: Clone `windows-container-networking`, checkout a pinned commit, run `make all`, install `nat.exe`, `sdnbridge.exe`, and `sdnoverlay.exe`, query PowerShell for the NAT adapter gateway/prefix, then write `0-containerd-nat.conf`.
- State and persistence: Writes binaries under `DESTDIR/cni/bin` and CNI config under `DESTDIR/cni/conf`.
- Dependencies and integration: Requires Go/GOPATH style source layout, Windows PowerShell, Microsoft HCN-compatible networking, and make.
- Risks: Uses `eval` in `split_ip`, assumes `vEthernet (nat)` exists, and has a likely prefix-length inversion in the emitted CIDR suffix (`32 - prefix_len`).
- Test signals: Windows CRI integration pod networking and presence of installed `.exe` plugins.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/install-cni-windows -->
