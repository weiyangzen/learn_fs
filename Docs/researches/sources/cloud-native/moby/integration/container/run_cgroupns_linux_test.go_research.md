# sources/cloud-native/moby/integration/container/run_cgroupns_linux_test.go

Purpose: Linux cgroup namespace tests for daemon defaults, privileged behavior, explicit host/private modes, invalid modes, and old API clients.

Important APIs and flow: `testRunWithCgroupNs` starts a child daemon with a default cgroup namespace mode, runs a container, and compares daemon and container namespace links. `testCreateFailureWithCgroupNs` expects create errors. Tests cover private default, privileged exceptions on cgroup v1, host default, explicit `host`, explicit `private`, privileged plus private, invalid mode, and API v1.39 compatibility with `DOCKER_MIN_API_VERSION=1.39`.

State and dependencies: Starts isolated dockerd instances with `daemon.WithDefaultCgroupNamespaceMode`, reads namespace identifiers, and requires `requirement.CgroupNamespacesEnabled`. Skips remote/non-Linux and cgroup-version-specific cases.

Risks and signals: It guards namespace isolation defaults and backwards compatibility. Failures can mean containers receive the wrong cgroup namespace, invalid values pass validation, or older clients lose expected host-mode behavior.
