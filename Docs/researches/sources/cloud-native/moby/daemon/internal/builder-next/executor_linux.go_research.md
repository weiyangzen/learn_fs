<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_linux.go -->
# sources/cloud-native/moby/daemon/internal/builder-next/executor_linux.go

Purpose: constructs the Linux BuildKit runc executor and network/proxy providers.

Important APIs and control flow: `newExecutor` sets up bridge/host/none network providers, removes stale network state, normalizes empty identity mappings to nil, creates a resource monitor, honors `DOCKER_BUILDKIT_RUNC_COMMAND`, optionally creates a proxy provider with host/filtered egress, and constructs `runcexecutor.New` with cgroup, rootless, DNS, AppArmor, CDI, proxy, and network settings. `newExecutorGD` delegates to `newExecutor`. `loopbackFilteredProvider` blocks proxy egress to loopback addresses. `lnInterface.Set` installs a prestart hook invoking `libnetwork-setkey` through the current executable.

State and persistence: writes executor/proxy/network state under the BuildKit root and deletes old network state on startup. It may own and close a proxy provider on failures.

Dependencies and integration: Linux-only integration between BuildKit runcexecutor, resource monitor, proxy provider, libnetwork bridge provider, daemon identity mappings, CDI, and OCI runtime specs.

Risks: loopback filtering requires DNS resolution and may allow hosts that resolve differently later. Environment-based runc override is a testing escape hatch. Prestart hook correctness depends on libnetwork controller IDs and daemon reexec support.

Test signals: no direct tests in this subset; Linux BuildKit build/network/proxy tests cover behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/builder-next/executor_linux.go -->
