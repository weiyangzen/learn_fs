<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/info.go -->
# sources/cloud-native/moby/daemon/info.go

Purpose: builds daemon `/info` and `/version` responses from host, daemon, storage, registry, runtime, and configuration state.

Important APIs and control flow: `SystemInfo` gathers raw sysinfo, config, image counts, host/kernel/OS/memory values, registry config, proxy config with masked credentials, NRI/CDI/device info, and then delegates to fill helpers for containers, debug, containerd, API warnings, platform info, driver info, plugins, security options, licensing, address pools, firewall, and devices. `SystemVersion` builds engine component details and delegates platform component population. Utility functions handle tracing, module version caching, host/kernel/memory/OS lookup, env fallback, nil-slice promotion, and device driver enumeration.

State and persistence: reads many daemon fields and host files/proc data; does not mutate daemon state except metrics timers and logs. `moduleVersion` is cached with `sync.OnceValue`.

Dependencies and integration: central to API system endpoints and integrates config, metrics, tracing, registry, platform, sysinfo, logger plugins, SELinux/seccomp/userns/rootless state, containerd, libnetwork, and device drivers.

Risks: most helper errors are logged and suppressed by design, while context cancellation/deadline is intended to propagate through platform helpers. API security warnings depend on normalized daemon hosts. Device driver enumeration can append warnings but should not fail the whole info response.

Test signals: no direct tests in this file; platform parser helpers are tested in `info_unix_test.go`, and system API integration tests cover assembled responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/info.go -->
