
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/health/net.go

- Purpose: implements `health network` alias `net` for local BeeGFS client connections.
- Important APIs: `netCfg`, `newNetCmd`, `runNetCmd`, and `printBeeGFSNet`.
- Control flow/state: loads local clients from procfs, optionally filters by configured management service, can force storage connections through df, then prints management, metadata, and storage node connection lines.
- Dependencies/integration: uses `procfs.GetBeeGFSClients`, mount filtering config, timeout flags, and shared health header utilities.
- Risks/tests: health meaning is nuanced because idle clients can show no connections; force-connections can block on unreachable storage nodes. No direct tests observed.
