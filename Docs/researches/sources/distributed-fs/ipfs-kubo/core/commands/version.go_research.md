# sources/distributed-fs/ipfs-kubo/core/commands/version.go

Purpose: implements `ipfs version`, dependency reporting, and swarm-based version-check heuristics.

Important APIs/types/functions: `VersionCmd`, `depsVersionCommand`, `checkVersionCommand`, output structs `Dependency` and `VersionCheckOutput`, and `DetectNewKuboVersion`.

Control flow: root version command emits `version.GetVersionInfo()` and text-encodes number/commit/repo/all variants. `deps` reads embedded Go build info and emits main plus dependencies, including replacements. `version check` requires online mode, reads a percentage threshold, and calls `DetectNewKuboVersion`. Detection parses local version, samples peerstore `AgentVersion` values from accelerated fullrt client or dual DHT WAN/LAN tables, ignores non-Kubo and pre/dev versions, counts peers running greater stable versions, and returns whether the fraction meets threshold.

State and persistence behavior: read-only. It reads build metadata, repo version info, DHT routing tables, and peerstore metadata.

Dependencies and integration points: integrates with Kubo version/config defaults, libp2p peerstore and fullrt DHT, `IpfsNode.HasActiveDHTClient`, and `hashicorp/go-version`.

Risks: type assertion `v.(string)` in `processPeerstoreEntry` can panic if peerstore stores non-string `AgentVersion`; other files guard this assertion. Sampling depends on DHT availability and may miss connected peers not in DHT tables. Threshold option name says min-percent but help mentions min-fraction in text.

Test signals: no direct tests in this file. `core_test.go` protects DHT client activity detection used by version checking.
