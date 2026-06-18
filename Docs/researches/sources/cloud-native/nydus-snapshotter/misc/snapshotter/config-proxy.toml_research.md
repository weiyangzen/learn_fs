# sources/cloud-native/nydus-snapshotter/misc/snapshotter/config-proxy.toml

Purpose: snapshotter config for proxy fs driver mode.

Flow/state: sets daemon mode `none`, fs driver `proxy`, and enables Kata volume option injection.

Integration points: used by `nydus-snapshotter.service` and deployment paths that relay layer download/mount management to another agent.

Risks/tests: relies on downstream runtime/agent understanding the extra mount information. No direct unit test validates this file; config schema coverage is indirect.
