<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix.go

Purpose: Unix sandbox `/etc/hosts`, `/etc/resolv.conf`, and embedded DNS resolver setup.

Important APIs/functions: `AddHostsEntry`, `UpdateHostsEntry`, `rebuildHostsFile`, `startResolver`, `setupResolutionFiles`, `buildHostsFile`, `makeHostsRecs`, `addHostsEntries`, `deleteHostsEntries`, path restore helpers, `setExternalResolvers`, `loadResolvConf`, `setupDNS`, `updateDNS`, `rebuildDNS`, `createBasePath`, and `copyFile`.

Control flow: sandbox creation creates hosts and resolv.conf paths under `/var/lib/docker/network/files/<sandbox>`. Host-mode with no extra hosts copies the origin hosts file. DNS setup loads host resolv.conf, applies user overrides, and writes a hash. On endpoint join, `updateDNS` rewrites non-user-modified files for legacy networks. When embedded DNS starts, `rebuildDNS` swaps nameservers to `127.0.0.11`, stores external resolvers, and preserves/sets `ndots`.

State and persistence: files on disk, hash files for user-modification detection, `sb.extDNS`, and `sb.ndotsSet`.

Dependencies and integration points: internal `resolvconf`, `etchosts`, resolver, sandbox IPv6 probing, and container mount setup.

Risks and test signals: user-edited resolv.conf must not be overwritten; hash behavior in `rebuildDNS` is intentionally legacy. Tests cover DNS option precedence and invalid ndots handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix.go -->
