# sources/cloud-native/cri-o/server/runtime_config.go

Purpose: implements CRI `RuntimeConfig`, currently reporting Linux cgroup driver configuration.

Important APIs and functions: `RuntimeConfig` returns `types.RuntimeConfigResponse` with `Linux.CgroupDriver`. `getCgroupDriver` maps CRI-O's cgroup manager to `SYSTEMD` or `CGROUPFS`.

Control flow: direct projection from config; request content is unused.

State and persistence: read-only over server config.

Dependencies and integration: integrates with Kubernetes CRI runtime configuration API and CRI-O cgroup manager abstraction.

Risks: only cgroup driver is reported; future CRI runtime config fields require extending this response.

Test signals: no direct test in this subset for `RuntimeConfig`; cgroup driver mapping is indirectly related to inspect info tests.
