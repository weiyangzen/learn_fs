# subset-b-000098 research

Grouped research for the requested CRI-O, fuse-overlayfs-snapshotter, and fuse-overlayfs files. Each section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/runtime.go -->
# sources/cloud-native/cri-o/test/nri/runtime.go

Purpose: test-only CRI runtime helper for NRI integration tests. It connects to CRI-O over the `-crio-socket` gRPC endpoint, exposes typed helpers for image pulling, pod/container lifecycle, resource updates, listing, and synchronous exec, and tracks created pod/container IDs so tests can address objects by either UID or runtime ID.

Important APIs and flow: `ConnectRuntime` builds runtime and image service clients with insecure local gRPC credentials and blocking dial timeout. `PullImages`/`PullImage` cache and pull the Fedora CRI-O CI image. `CreatePod` builds a `PodSandboxConfig` with DNS, cgroup parent selection from `-cgroup-manager`, SELinux fields, labels, annotations, and pod option hooks. `CreateContainer` builds a default long-running shell container, applies container option hooks, and calls `CreateContainer`; `StartContainer`, `StopContainer`, `RemoveContainer`, `UpdatePod`, and `ExecSync` wrap corresponding CRI calls.

State and persistence: in-memory maps store pod configs, UID-to-ID aliases, container aliases, and pulled image refs; the actual persistent state is in CRI-O/container storage. A mutex protects map mutation, but reads before RPCs are mostly unsynchronized, which is acceptable for serial test usage but not a general concurrent client.

Dependencies and integration points: depends on Kubernetes CRI API, gRPC, local CRI-O socket flags, CRI-O image availability, and NRI test flags. Risks include stale aliases after failed cleanup, missing `PullImages` before `CreateContainer`, long image-pull timeout behavior, and use of deprecated gRPC dial options retained for blocking semantics. Test signal is indirect: NRI tests exercise this helper against a live CRI-O daemon rather than unit tests in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/runtime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/utils.go -->
# sources/cloud-native/cri-o/test/nri/utils.go

Purpose: support utilities for NRI tests. It discovers available CPU and NUMA memory node sets from sysfs, derives a test namespace from the Go call stack, and waits for files produced asynchronously by tests.

Important APIs and flow: `getAvailableCpuset` and `getAvailableMemset` lazily cache parsed values from `/sys/devices/system/cpu/online` and `/sys/devices/system/node/has_normal_memory`. `getXxxset` expands comma-separated ranges such as `0-3,8` into string slices. `getTestNamespace` scans callers for a function name prefixed with `Test`. `waitForFileAndRead` polls up to five seconds, sleeps a short slack period after existence, then reads the file.

State and persistence: package globals cache parsed sysfs data for the process lifetime. The helpers read host sysfs and arbitrary paths but write nothing. Risks include nil sets on hosts without the expected sysfs files, no synchronization around lazy globals, and a fixed wait timeout that can be flaky on slow environments. Test signal is its direct use by NRI integration tests that need host topology and file-event synchronization.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/policy-signature.json -->
# sources/cloud-native/cri-o/test/policy-signature.json

Purpose: containers/image signature policy fixture for CRI-O tests that require a restrictive default and explicit sigstore trust for a signed CRI-O image.

Important structure: `default` rejects all images. Under `transports.docker`, `quay.io/crio/signed` is accepted only with `sigstoreSigned`, repository identity matching, a Fulcio issuer/email constraint, embedded CA data, and embedded Rekor public key data. `quay.io/crio/fedora-crio-ci` is explicitly allowed with `insecureAcceptAnything` so test infrastructure images can still pull.

State and integration: this is static policy input consumed by containers/image through CRI-O image pull verification paths. It persists no state. Risks are fixture drift as sigstore identities, embedded certificates, or test image names change; because the default is reject, missing transport entries will turn into pull failures. Test signal comes from image signature policy tests that copy or reference this policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/policy-signature.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/policy.json -->
# sources/cloud-native/cri-o/test/policy.json

Purpose: unrestrictive image policy fixture with targeted exceptions for CRI-O image policy tests.

Important structure: `default` accepts anything. The `docker-daemon` transport rejects `quay.io/crio/hello-world` and requires Red Hat GPG signatures for `registry.access.redhat.com` using embedded public key data. This lets tests cover both successful permissive pulls and transport-specific denial/signature paths.

State and integration: consumed by containers/image policy evaluation through CRI-O or test helpers. No runtime state is stored. Risks include the large embedded key material becoming stale or malformed and transport mismatch: entries under `docker-daemon` will not affect `docker://` pulls. Test signal is fixture-based; correctness is proven by higher-level pull/signature tests rather than a parser test here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/policy.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/redhat_sigstore.yaml -->
# sources/cloud-native/cri-o/test/redhat_sigstore.yaml

Purpose: short sigstore registry configuration fixture for Red Hat registry signature tests.

Important structure: maps `docker.registry.access.redhat.com` to the Red Hat hosted sigstore URL. It provides the external signature source that containers/image can use when checking Red Hat images.

State and integration: static YAML read by image-signature policy tooling. It has no local persistence. Risks are external URL availability and schema compatibility with the containers/image version under test. Test signal comes from policy/signature integration paths that load this file alongside policy fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/redhat_sigstore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/registries.conf -->
# sources/cloud-native/cri-o/test/registries.conf

Purpose: registries configuration fixture for CRI-O tests that need deterministic unqualified image search and alias resolution.

Important structure: `unqualified-search-registries` is ordered as `quay.io`, `registry.access.redhat.com`, and `docker.io`. The `aliases` table maps `image-for-testing` to `registry.crio.test.com/repo`.

State and integration: read by containers/image/containers-common registry resolution when tests point CRI-O at this file. It stores no state. Risks include tests accidentally depending on network-accessible default registries or alias names colliding with newer defaults. Test signal is higher-level image resolution behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/registries.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/test_runner.sh -->
# sources/cloud-native/cri-o/test/test_runner.sh

Purpose: Bats test entrypoint for CRI-O integration tests.

Important flow: enables Go coverage output directory if `GOCOVERDIR` is set, changes into the test directory, optionally exports user namespace UID/GID mappings when `TEST_USERNS=1`, raises `/proc/sys/user/max_user_namespaces` when writable, preloads images via `common.sh get_images`, chooses test arguments or `critest.bats` when `RUN_CRITEST=1`, sets parallel `JOBS`, enables one Bats retry, and runs non-serial tests in parallel followed by serial-tagged tests.

State and integration: mutates process environment and may write a sysctl in privileged CI. It depends on Bats, common CRI-O test helpers, image preloading, and tag discipline. Risks include `set -xe` leaking command details, host sysctl side effects, and test flakes hidden by one retry. Test signal is the top-level integration test orchestration itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/test_runner.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/50-runc-default.conf -->
# sources/cloud-native/cri-o/test/testdata/50-runc-default.conf

Purpose: minimal CRI-O drop-in config fixture that sets `runc` as the default runtime and declares the `runc` runtime path.

Important structure: under `[crio.runtime]`, `default_runtime = "runc"`; under `[crio.runtime.runtimes.runc]`, `runtime_path="/usr/bin/runc"`.

State and integration: static TOML fragment merged into CRI-O config in tests. It does not persist state. Risks are path assumptions on hosts where `runc` is elsewhere and accidental masking of runtime defaults. Test signal is config-loading behavior in runtime selection tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/50-runc-default.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/50-runc.conf -->
# sources/cloud-native/cri-o/test/testdata/50-runc.conf

Purpose: minimal CRI-O runtime definition fixture that declares `runc` without setting it as `default_runtime`.

Important structure: contains only the runtime tables and `runtime_path="/usr/bin/runc"`. It is useful for testing runtime table merging or default selection from other config sources.

State and integration: static TOML drop-in consumed by CRI-O config loading tests. It stores no state. Risks are host path assumptions and ambiguity when combined with other runtime fragments. Test signal comes from config merge/runtime selection tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/50-runc.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/Dockerfile -->
# sources/cloud-native/cri-o/test/testdata/Dockerfile

Purpose: builds the Fedora-based CRI-O CI image used by many runtime tests.

Important flow: starts from `quay.io/fedora/fedora-minimal:38`, installs basic tools, compiler, networking utilities, OpenSSL headers, process tools, and wget; creates a test user/group and adjusts `/etc` permissions; builds and installs `su-exec`; downloads and verifies Redis 6.0.18, builds it with TLS, installs it, and sets a Redis-style entrypoint, data volume, exposed port, and default command. It also declares `/imagevolume` for image-volume tests.

State and integration: produces `quay.io/crio/fedora-crio-ci:latest` variants used in CRI request fixtures and NRI runtime helpers. Risks include external download availability, Fedora package drift, Redis checksum/version updates, and architecture-specific build behavior. Test signal is image-dependent integration behavior rather than Dockerfile unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/artifact.sh -->
# sources/cloud-native/cri-o/test/testdata/artifacts/artifact.sh

Purpose: tiny executable OCI artifact payload fixture.

Important behavior: shell script prints a fixed greeting. It is pushed by the artifact helper as an executable-like test artifact, letting tests verify artifact retrieval and execution/payload handling separate from image layers.

State and integration: static file consumed by `push-oci-artifacts` and registry artifact tests. It persists no state. Risks are only file mode/content drift if tests expect exact output. Test signal is artifact pull/use behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/artifact.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/push-oci-artifacts -->
# sources/cloud-native/cri-o/test/testdata/artifacts/push-oci-artifacts

Purpose: helper script to publish OCI artifact test fixtures to `quay.io/crio/artifact`.

Important flow: requires `oras`, changes into `test/testdata/artifacts`, and pushes tags for a single file, executable script, multiple files, and subpath entries with `application/x.test.test.test.v1` artifact type.

State and integration: writes remote registry artifacts; it assumes credentials and network access when used manually or in maintenance. Risks include wrong working directory if invoked outside repository layout, registry tag mutation, and missing `oras`. Test signal is indirect: CRI-O tests consume the pushed artifact tags.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/push-oci-artifacts -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/subpath/2 -->
# sources/cloud-native/cri-o/test/testdata/artifacts/subpath/2

Purpose: small text payload used as a subpath OCI artifact fixture.

Important behavior: contains the text value `2`, pushed by `push-oci-artifacts` as `subpath/2:text/plain`. It lets tests verify that artifact entries preserve subpath names and simple content.

State and integration: static payload, no persistence. Risks are exact-content expectations and registry artifact drift after publishing. Test signal is artifact extraction/path validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/subpath/2 -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/subpath/3 -->
# sources/cloud-native/cri-o/test/testdata/artifacts/subpath/3

Purpose: companion text payload for subpath OCI artifact tests.

Important behavior: contains the text value `3`, pushed as `subpath/3:text/plain`. Together with `subpath/2`, it verifies multi-entry subpath handling.

State and integration: static payload, no persistence. Risks are exact-content dependencies and stale remote artifacts. Test signal is artifact pull/extract behavior that checks multiple named payloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/subpath/3 -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/build-and-push-image.sh -->
# sources/cloud-native/cri-o/test/testdata/build-and-push-image.sh

Purpose: maintenance script for building and publishing the multi-architecture CRI-O CI image.

Important flow: configures QEMU binfmt through `multiarch/qemu-user-static`, creates a Docker buildx builder, builds and loads architecture-specific images for `amd64` and `arm64`, pushes each arch tag, then creates, annotates, and pushes the multi-arch manifest for `quay.io/crio/fedora-crio-ci:latest`. Cleanup removes the buildx builder.

State and integration: writes Docker builder state and remote registry tags/manifests. Risks include privileged Docker requirement, QEMU image/version drift, registry credential requirements, and the script mutating `latest`. Test signal is external: CRI-O test fixtures depend on the resulting image.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/build-and-push-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/clone-ns.c -->
# sources/cloud-native/cri-o/test/testdata/clone-ns.c

Purpose: C helper fixture for namespace/clone behavior tests.

Important flow: expects one argument, either `with_flags` or `without_flags`. It allocates a 1 MiB stack and calls `clone` with `CLONE_NEWUSER|CLONE_NEWNET` for the flagged mode or zero flags otherwise. The child entry executes `id`.

State and integration: creates a process and potentially new namespaces; no files are persisted. Risks include weak error handling after invalid arguments, pointer arithmetic on `void *` relying on compiler extensions, leaked allocated stack at process exit, and required kernel/userns privileges. Test signal is integration output/exit behavior under CRI-O namespace policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/clone-ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/config/config-v1.17.0.toml -->
# sources/cloud-native/cri-o/test/testdata/config/config-v1.17.0.toml

Purpose: historical CRI-O v1.17-style full configuration fixture for config migration, parsing, and default compatibility tests.

Important structure: covers `[crio]`, API socket and stream server settings, runtime defaults, conmon/cgroup/SELinux/seccomp/AppArmor/runtime handler settings, image transport/pause/signature policy options, CNI network paths, and metrics. Most storage values are comments, while active defaults include `log_dir`, `version_file`, `listen`, `default_runtime = "runc"`, `cgroup_manager = "cgroupfs"`, default capabilities, runtime root, pause image, and CNI plugin dirs.

State and integration: static TOML input that represents old config shape and comments. It persists no runtime state, but tests may copy it into temporary CRI-O config paths. Risks include deprecated fields (`default_mounts`, old namespace lifecycle names) and old Kubernetes pause image/runtime defaults. Test signal is parser/migration acceptance of legacy config.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/config/config-v1.17.0.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_config.json -->
# sources/cloud-native/cri-o/test/testdata/container_config.json

Purpose: baseline CRI `ContainerConfig` fixture for creating a small Fedora CI container.

Important structure: metadata names `container1`, image is `quay.io/crio/fedora-crio-ci:latest`, command is `/bin/ls`, environment includes PATH, TERM, GLIBC tunable disabling rseq, and test directory/file values. Labels and annotations identify test type and ownership. Linux resources set CPU quota/period/shares, OOM score, memory limit, root user, pod PID namespace, SELinux label, and added `setuid`/`setgid` capabilities.

State and integration: consumed by `crictl`/CRI-O integration tests as JSON request input. It stores no state itself. Risks include image availability, resource defaults conflicting with host cgroup mode, and exact JSON field compatibility with CRI API versions. Test signal is successful container create/start and metadata/resource assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_config_ping.json -->
# sources/cloud-native/cri-o/test/testdata/container_config_ping.json

Purpose: privileged long-running container config fixture for network-oriented tests.

Important structure: same Fedora CI image and common env/labels as the baseline config, but command is `/bin/sleep` with `+Inf`, `privileged` is set, and the Linux resource/security fields mirror the baseline root container. The name remains `container1`.

State and integration: static CRI request body for tests that need a persistent privileged container, commonly to exec networking commands. Risks include CRI schema compatibility for the top-level `privileged` field, host policy rejecting privileged containers, and infinite sleep behavior depending on coreutils. Test signal is higher-level ping/network tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_config_ping.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_redis.json -->
# sources/cloud-native/cri-o/test/testdata/container_redis.json

Purpose: CRI container config fixture for launching Redis from the CI image.

Important structure: metadata `podsandbox1-redis`, Fedora CI image, args `docker-entrypoint.sh redis-server`, working directory `/data`, Redis version/download environment, backend label, and pod annotation. Linux resources include memory/CPU/OOM plus `cpuset_cpus` and `cpuset_mems` fixed to `0`; security context uses pod PID namespace, writable rootfs, and adds `sys_admin`.

State and integration: used by CRI-O tests that verify service containers, ports, resources, or entrypoint behavior. It persists no local state, but Redis writes to container data paths. Risks include requiring CPU and memory node `0`, capability policy, image Redis version drift, and working directory/entrypoint assumptions. Test signal is successful Redis start and runtime behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_redis.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_sleep.json -->
# sources/cloud-native/cri-o/test/testdata/container_sleep.json

Purpose: simple long-running CRI container fixture for lifecycle tests.

Important structure: metadata `podsandbox-sleep`, Fedora CI image, command `/bin/sleep 6000` and args `6000`, minimal PATH/GLIBC tunable environment, pod annotation, pod PID namespace, writable rootfs, and basic CPU/memory/OOM resource settings.

State and integration: static request body for creating a container that remains available for stop, exec, inspect, and resource tests. Risks include duplicated sleep duration in command and args, image availability, and resource compatibility across cgroup versions. Test signal is lifecycle stability.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_sleep.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/docker-entrypoint.sh -->
# sources/cloud-native/cri-o/test/testdata/docker-entrypoint.sh

Purpose: Redis-compatible entrypoint included in the CRI-O CI image.

Important flow: if the first argument looks like an option or `.conf`, prepends `redis-server`. If running `redis-server` as root, it chowns the current directory to the Redis user and re-execs through `su-exec`; otherwise it executes the provided command.

State and integration: mutates ownership of the working directory inside the container and then replaces the shell process. Risks include recursive re-exec assumptions, dependency on `su-exec`, and ownership changes on mounted volumes. Test signal comes from Redis container fixture startup.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/docker-entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/log_cni_plugin.sh -->
# sources/cloud-native/cri-o/test/testdata/log_cni_plugin.sh

Purpose: minimal CNI plugin fixture that logs ADD input and returns simple CNI responses.

Important flow: reads stdin JSON, switches on `CNI_COMMAND`, and for `ADD` extracts `.config.log_path` using `jq`; if present, appends the full config to that log and emits a `cniVersion` result. `VERSION` emits supported versions, while `DEL` and `GET` are no-ops; unknown commands fail.

State and integration: writes to the configured log path and participates in CRI-O CNI setup during tests. Dependencies include bash and `jq`. Risks include no validation of log path, silent no-op for DEL/GET, and minimal CNI result fields that may not satisfy consumers outside tests. Test signal is captured log content and CNI command behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/log_cni_plugin.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/policies/restrictive.json -->
# sources/cloud-native/cri-o/test/testdata/policies/restrictive.json

Purpose: restrictive policy fixture under testdata mirroring the top-level signature policy.

Important structure: default reject; Docker transport allows `quay.io/crio/signed` through sigstore verification with Fulcio issuer/email and Rekor key data; allows `quay.io/crio/fedora-crio-ci` insecurely for test infrastructure.

State and integration: static input for tests that need policy files in a `testdata/policies` tree. It persists no state. Risks are duplicate-fixture drift versus the top-level `policy-signature.json`, embedded key/certificate expiry or identity changes, and strict default rejection causing unrelated image pulls to fail. Test signal is image policy acceptance/rejection behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/policies/restrictive.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/policies/unrestrictive.json -->
# sources/cloud-native/cri-o/test/testdata/policies/unrestrictive.json

Purpose: unrestrictive policy fixture under `testdata/policies`, duplicating the top-level permissive policy shape for tests that load policy directories.

Important structure: default accepts anything, but `docker-daemon` rejects `quay.io/crio/hello-world` and requires Red Hat GPG signature material for `registry.access.redhat.com`.

State and integration: static containers/image policy file. It has no persistence. Risks include duplicate drift with `test/policy.json`, large embedded key data, and transport-specific behavior surprising tests that use `docker` rather than `docker-daemon`. Test signal is targeted pull/signature-policy tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/policies/unrestrictive.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/sandbox_config.json -->
# sources/cloud-native/cri-o/test/testdata/sandbox_config.json

Purpose: baseline CRI `PodSandboxConfig` fixture for CRI-O integration tests.

Important structure: metadata identifies pod name, UID, namespace, and attempt; hostname is `crictl_host`; DNS server is `8.8.8.8`; resource requests/limits are present for CPU and memory; labels/annotations include seccomp unconfined and a custom annotation. Linux config sets `cgroup_parent` to a systemd-like slice and uses pod namespace options plus SELinux label fields.

State and integration: static JSON request body for `RunPodSandbox`. It stores no state directly; CRI-O creates pod sandbox resources. Risks include seccomp annotation compatibility, cgroup parent format mismatch with cgroup manager, and CRI API field drift. Test signal is sandbox creation and metadata/resource propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/sandbox_config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/usehugetlb.c -->
# sources/cloud-native/cri-o/test/testdata/usehugetlb.c

Purpose: C helper for tests that need a process holding a huge page.

Important flow: registers a SIGTERM handler, mmaps one 2 MiB anonymous private huge page with `MAP_HUGETLB`, sleeps for 100 seconds, then unmaps during cleanup. On mmap or unmap failure it prints an error and exits nonzero.

State and integration: consumes host huge page resources while running and releases them on normal termination/SIGTERM. Risks include requiring configured huge pages and privileges/cgroup allowances, simplistic signal handling, and `NULL` fd argument style for `mmap`. Test signal is resource accounting or hugetlb cgroup behavior while the process is alive.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/usehugetlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/updateunified/updateunified.go -->
# sources/cloud-native/cri-o/test/updateunified/updateunified.go

Purpose: small command-line helper to update cgroup v2 unified resource keys for a container through the CRI `UpdateContainerResources` RPC.

Important flow: validates arguments as `<socket> <container-id> <key=value>...`, parses remaining arguments into a `map[string]string`, creates an insecure Unix gRPC client to the CRI-O socket, constructs a 30-second context, and sends `UpdateContainerResourcesRequest` with `Linux.Unified` set to the parsed map.

State and integration: writes container resource state through CRI-O; no local persistence. Dependencies are CRI API and local Unix socket access. Risks include no validation of unified keys/values beyond `key=value`, no blocking dial, and updates being kernel/cgroup-manager dependent. Test signal is used by cgroup unified integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/updateunified/updateunified.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner.go -->
# sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner.go

Purpose: package-level command execution abstraction for CRI-O code that needs globally configurable command wrapping, commonly for tests or running commands under another tool.

Important APIs and flow: `CommandRunner` defines `Command`, `CommandContext`, and `CombinedOutput`. The package-level `commandRunner` singleton defaults to `os/exec`. `PrependCommandsWith` installs a `prependableCommandRunner`; its `Command` and `CommandContext` replace the executable with `prependCmd` and prepend configured args plus the original command and args. `GetPrependedCmd` and `ResetPrependedCmd` expose state for tests.

State and persistence: singleton process state, no disk persistence. Risks include global mutable state with no synchronization, `prependArgs` slice aliasing and append mutation, and cross-test contamination without reset. Integration points are all code paths importing this package instead of `exec` directly. Test signal is `cmdrunner_test.go`, plus `cmdrunner_test_inject.go` for build-tagged mock injection.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test.go -->
# sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test.go

Purpose: Ginkgo/Gomega specs for the command runner singleton and prepend behavior.

Important coverage: verifies prepend state can be reset, default `CombinedOutput` matches `exec.Command`, configured `PrependCommandsWith("which")` changes command output and reports the prepended command, and configuring only prepend args with an empty command does not wrap execution.

State and integration: mutates the package singleton and explicitly resets it in test bodies. It depends on host `ls` and `which` commands. Risks include PATH/environment-specific output and no coverage for `CommandContext`, concurrent access, or prepend argument slice mutation. Test signal is direct unit coverage of the main public behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test_inject.go -->
# sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test_inject.go

Purpose: test-build-only injection hook for replacing the command runner singleton with a generated mock.

Important API: under build tag `test`, `SetMocked` accepts `*MockCommandRunner` from `test/mocks/cmdrunner` and assigns it to the package-level `commandRunner`.

State and integration: mutates process-global command runner state during tests. No persistence. Risks include tests forgetting to reset the mock and the hook being unavailable unless the `test` build tag is used. Test signal is indirect: packages that need mocked command execution can use this hook.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/cmdrunner_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/suite_test.go -->
# sources/cloud-native/cri-o/utils/cmdrunner/suite_test.go

Purpose: Ginkgo suite bootstrap for `utils/cmdrunner`.

Important flow: `TestCommandRunner` registers Gomega's fail handler and calls CRI-O's `RunFrameworkSpecs`. `BeforeSuite` creates a `TestFramework` with no-op setup/teardown callbacks and calls `Setup`; `AfterSuite` tears it down.

State and integration: initializes shared CRI-O test framework state for this package. Risks are hidden framework side effects and suite-level state shared across specs. Test signal is that cmdrunner specs run under the same framework conventions as broader CRI-O tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/cmdrunner/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/consts.go -->
# sources/cloud-native/cri-o/utils/consts.go

Purpose: tiny shared constants package fragment.

Important API: exports `PodCgroupName = "pod"`, a common prefix/name used by CRI-O cgroup code when constructing or recognizing pod cgroup names.

State and integration: compile-time constant only, no persistence. Risks are broad ripple effects if changed because cgroup paths and tests may assume this exact token. Test signal is indirect through cgroup-related tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/consts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/errdefs/errors.go -->
# sources/cloud-native/cri-o/utils/errdefs/errors.go

Purpose: local copy/adaptation of containerd-style error classes for CRI-O utility code.

Important APIs: exported sentinel errors `ErrInvalidArgument`, `ErrNotFound`, `ErrAlreadyExists`, `ErrFailedPrecondition`, `ErrUnavailable`, and `ErrNotImplemented`, plus predicate functions using `errors.Is`. `ErrUnknown` is used internally for unmapped conversions.

State and integration: no runtime state; callers wrap these sentinels to communicate error class across package and gRPC boundaries. Risks include diverging from upstream containerd semantics and losing class information if callers format errors without wrapping. Test signal is mostly through gRPC conversion behavior in `grpc.go` consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/errdefs/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/errdefs/grpc.go -->
# sources/cloud-native/cri-o/utils/errdefs/grpc.go

Purpose: converts local error classes to and from gRPC status errors.

Important APIs and flow: `ToGRPC` maps known sentinel classes to corresponding gRPC codes, preserves errors that are already gRPC statuses, and returns unmapped errors unchanged. `ToGRPCf` wraps an existing class with formatted context before mapping. `FromGRPC` maps status codes back to sentinel classes and rebases duplicate messages with `rebaseMessage`; unknown codes become `ErrUnknown`.

State and integration: stateless conversion layer between server-side CRI-O errors and gRPC clients. Risks include `status.FromError` treating non-status errors as unknown in helper paths, `FromGRPC` converting every unknown into `ErrUnknown`, and message rebasing relying on string suffixes. Test signal is indirect unless higher-level API tests check status codes.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/errdefs/grpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/filesystem.go -->
# sources/cloud-native/cri-o/utils/filesystem.go

Purpose: filesystem utility functions for disk usage and directory validation.

Important APIs: `GetDiskUsageStats` walks a path without following symlinks and sums `FileInfo.Size()` plus one inode count per visited entry. `IsDirectory` follows symlinks with `os.Stat` and returns a `PathError` with `ENOTDIR` for existing non-directories, matching `os.Stat`-style errors.

State and integration: reads filesystem metadata only. Risks include expensive recursive walks on large trees, size values not matching block usage, no context/cancellation, and symlink-follow behavior differing between the two functions. Test signal is `filesystem_test.go`, which covers current directory, missing paths, directory success, file failure, and missing path failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/filesystem_test.go -->
# sources/cloud-native/cri-o/utils/filesystem_test.go

Purpose: unit specs for filesystem helpers.

Important coverage: `GetDiskUsageStats(".")` must return positive byte and inode counts, while a missing path returns an error and zero values. `IsDirectory` succeeds on `.`, fails on the test binary path, and fails on a missing path.

State and integration: reads the test process filesystem and package working directory. Risks include assumptions about current directory contents and using `os.Args[0]` as a regular file. It does not cover symlink behavior, permission errors, or very large trees. Test signal is direct focused coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/filesystem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/suite_test.go -->
# sources/cloud-native/cri-o/utils/suite_test.go

Purpose: Ginkgo suite bootstrap for the `utils` package tests.

Important flow: `TestUtils` registers fail handling and runs framework specs. Suite setup constructs a CRI-O `TestFramework` with no-op callbacks, calls `Setup`, and tears it down after all specs.

State and integration: suite-level test framework lifecycle; no production behavior. Risks are shared package-global state across specs and hidden framework setup assumptions. Test signal is enabling all `utils` Ginkgo specs under the CRI-O test framework.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils.go -->
# sources/cloud-native/cri-o/utils/utils.go

Purpose: broad CRI-O utility collection for process status, detachable IO, diagnostics, identity file handling, SELinux labels, sync helpers, terminal resize handling, and duration parsing.

Important APIs and flow: `CopyDetachable` copies from reader to writer while detecting detach key sequences, returning `DetachError`. `WriteGoroutineStacksToFile` and `WriteGoroutineStacksTo` dump goroutine stacks. `GenerateID` returns 32 random bytes hex encoded. `GetUserInfo`, `GetUser`, and `GetGroup` safely read container `/etc/passwd` and `/etc/group` using secure joins. `GeneratePasswd` and `GenerateGroup` create runtime-specific passwd/group files only when IDs are absent and permissions allow safe modification. `EnsureSaneLogPath` removes broken symlinks. `GetLabelOptions`, `SyncParent`, `Sync`, `HandleResizing`, and `ParseDuration` provide smaller shared behaviors.

State and persistence: reads container rootfs files, may create/chown passwd/group files in a run directory, remove broken log-path symlinks, sync file descriptors, and spawn a resize goroutine. Risks include subtle detach sequence buffering, secure file permission skip rules, chown requirements, unbounded resize goroutine lifetime until channel close, and negative durations being made positive. Test signal is broad `utils_test.go` coverage for IDs, copy/detach errors, user/group generation, and duration parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_linux.go -->
# sources/cloud-native/cri-o/utils/utils_linux.go

Purpose: Linux-specific utility implementations for systemd scope placement and filesystem sync.

Important APIs and flow: `RunUnderSystemdScope` validates a DBus manager, builds default transient unit properties (`PIDs`, `Delegate`, `DefaultDependencies`), optionally adds a slice, starts a systemd transient unit via `RetryOnDisconnect`, and waits up to six minutes for the job channel to report `done`. `Syncfs` opens a path and invokes the Linux `syncfs` syscall on its file descriptor.

State and integration: mutates systemd state by moving a PID into a scope; syncs filesystem state to disk. Dependencies include systemd DBus, CRI-O internal dbus manager, and Linux syscalls. Risks include long timeout, DBus job channel behavior, pid/slice validity, and `syncfs` requiring open path permissions. Test signal is mostly integration-level because systemd behavior is host-dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_test.go -->
# sources/cloud-native/cri-o/utils/utils_test.go

Purpose: Ginkgo specs for the general `utils` package.

Important coverage: tests `StatusToExitCode`, `CopyDetachable` success, custom keys, nil reader/writer, reader/writer errors, and detach sequence; goroutine stack writing success and invalid path failure; `GetUserInfo` with missing/empty/existing user data; `GeneratePasswd` and `GenerateGroup` for existing/non-existing users and groups; and `ParseDuration` for unit-suffixed, integer seconds, negative values, zero, floating unit values, invalid float seconds, invalid text, and empty input.

State and integration: creates temporary etc/passwd and etc/group fixtures via helper functions and writes generated files in temporary directories. Risks include not covering `EnsureSaneLogPath`, label options, sync, terminal resizing, secure join symlink attacks, or Linux systemd helpers. Test signal is strong for identity and duration utilities.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_unix.go -->
# sources/cloud-native/cri-o/utils/utils_unix.go

Purpose: non-Linux Unix fallback for `Syncfs`.

Important API: under build tag `!linux`, `Syncfs(path string)` ignores the path and calls `unix.Sync()` because Linux `syncfs` is unavailable.

State and integration: syncs all filesystems, not a specific mount. Risks include broader performance impact and path argument being unused, but it preserves API portability. Test signal is build-platform coverage rather than direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/dependabot.yml -->
# sources/cloud-native/fuse-overlayfs-snapshotter/.github/dependabot.yml

Purpose: Dependabot configuration for the snapshotter repository.

Important structure: enables daily updates for Go modules at repository root and GitHub Actions workflows at repository root.

State and integration: affects GitHub-hosted dependency update PR creation, not runtime behavior. Risks include daily update churn and no grouping/ignore rules for noisy ecosystems. Test signal is repository maintenance automation rather than code tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/main.yml -->
# sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/main.yml

Purpose: primary CI workflow for the containerd fuse-overlayfs snapshotter.

Important jobs: project checks run containerd project checks with Go 1.24; linters run golangci-lint; test builds and runs `make test` against matrixed fuse-overlayfs versions `v1.0.0`, `v1.13`, and `main`; cross builds release artifacts through `make artifacts`.

State and integration: runs on GitHub Actions for pushes, PRs, and manual dispatch. It uses Docker/buildx and rootless/FUSE test containers via the Makefile. Risks include dependence on building external fuse-overlayfs commits, Docker-in-CI capabilities, and version matrix drift. Test signal is strong CI coverage for project hygiene, linting, snapshotter test suite, and cross compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/release.yml -->
# sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/release.yml

Purpose: tag-triggered release automation for snapshotter binaries.

Important flow: on `v*` or test release tags, sets up Go 1.24, checks out source, runs `make artifacts`, generates `_output/SHA256SUMS`, records its own checksum, creates a release note, attests build provenance, and creates a draft GitHub release with artifacts.

State and integration: writes GitHub release drafts and provenance attestations. Requires contents, id-token, and attestations permissions. Risks include draft release creation with placeholder notes, reliance on `gh` CLI availability, and artifact naming from Makefile version logic. Test signal is release pipeline execution rather than source tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.golangci.yml -->
# sources/cloud-native/fuse-overlayfs-snapshotter/.golangci.yml

Purpose: golangci-lint v2 configuration for the snapshotter project.

Important structure: enables `copyloopvar`, `depguard`, `gosec`, `misspell`, `nolintlint`, and `unconvert`; disables `errcheck` and `revive`; denies `io/ioutil`; uses common exclusion presets and generated/third_party/builtin/examples path exclusions. Formatter config enables `gofmt`.

State and integration: controls CI lint behavior. Risks include disabled `errcheck` hiding unchecked cleanup errors and broad exclusion presets suppressing findings. Test signal is lint job in `main.yml`.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/Dockerfile -->
# sources/cloud-native/fuse-overlayfs-snapshotter/Dockerfile

Purpose: multi-stage test image for running snapshotter tests under rootlesskit with a built fuse-overlayfs binary.

Important flow: builds Go test binary with CGO disabled; clones and statically builds `containers/fuse-overlayfs` at configurable commit; clones and builds rootlesskit at configurable commit; final Alpine image installs FUSE/user namespace dependencies, grants `newuidmap` and `newgidmap` capabilities, creates a test user and subuid/subgid ranges, and runs the compiled Go test under rootlesskit.

State and integration: used by `make test` and CI. It downloads external source repositories and packages, builds binaries, and requires runtime flags for `/dev/fuse` plus relaxed seccomp/AppArmor. Risks include unpinned default `main` for fuse-overlayfs, privileged build/run assumptions, and package version drift. Test signal is the containerized snapshotter suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/Makefile -->
# sources/cloud-native/fuse-overlayfs-snapshotter/Makefile

Purpose: build, install, test, clean, and release artifact automation for `containerd-fuse-overlayfs-grpc`.

Important targets: builds the gRPC binary with version/revision ldflags and CGO disabled; `install` copies it to `$(BINDIR)`; `test` builds the Docker test image, checks `fuse-overlayfs -V`, runs tests with `/dev/fuse` and relaxed security options, then removes the image; `_test` runs Go tests via rootlesskit; `artifacts` cross-builds Linux archives for amd64, arm64, armv7, ppc64le, s390x, and riscv64.

State and integration: writes `bin/` and `_output/`, uses Docker, Go, tar, git, and rootlesskit. Risks include duplicate `binaries` target declarations, mutable version from dirty git state, Docker cleanup failures, and cross-build assumptions. Test signal is Makefile-driven CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/check.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/check.go

Purpose: Linux support checks for using fuse-overlayfs as a snapshotter backend.

Important APIs and flow: `supportsReadonlyMultipleLowerDir` creates temporary lower and merged directories, attempts a read-only `fuse3.fuse-overlayfs` mount with two lowerdirs, unmounts it, and reports failure with context. `Supported` verifies `fuse-overlayfs` is in PATH, ensures the root directory exists, and calls the mount probe with an error hint about kernel support.

State and integration: creates/removes temporary directories, performs a real FUSE mount, and checks executable lookup. Risks include needing `/dev/fuse`, permissions, kernel features, and cleanup after mount/unmount failures. Test signal is used by the snapshotter test suite to skip unsupported environments and by the gRPC server before serving.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/main.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/main.go

Purpose: standalone containerd proxy snapshotter gRPC server.

Important flow: logs version/revision, validates CLI args as `<unix addr> <root>`, creates the socket directory, removes any existing socket path, runs `fuseoverlayfs.Supported(root)`, creates a snapshotter, wraps it with containerd `snapshotservice.FromSnapshotter`, registers the snapshots API on a gRPC server, listens on the Unix socket, sends systemd readiness/stopping notifications when `NOTIFY_SOCKET` is set, and serves.

State and integration: creates/removes Unix socket path, initializes snapshotter metadata/root directories, and serves containerd's snapshot gRPC API. Risks include `os.RemoveAll(address)` deleting non-socket paths if misconfigured, no graceful signal shutdown in this file, and support probe requiring mount privileges at startup. Test signal is integration with containerd proxy plugin configs.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/version/version.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/version/version.go

Purpose: build-time version metadata holder for the snapshotter gRPC binary.

Important API: exports mutable package variables `Version` and `Revision`, defaulting to `<unknown>`. The Makefile sets them through `-ldflags -X`.

State and integration: compile-time/link-time metadata only. Risks are missing ldflags producing unknown version logs and mutable globals being theoretically changeable at runtime. Test signal is release/build output inspection.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs.go

Purpose: Linux containerd `snapshots.Snapshotter` implementation backed by `fuse-overlayfs`.

Important APIs and flow: `NewSnapshotter` creates root, metadata DB, and snapshots directory. `Stat`, `Update`, `Walk`, and `Close` delegate to containerd metadata storage. `Usage` returns stored committed usage or scans active upperdir disk usage. `Prepare`/`View` call `createSnapshot`, which creates a temp snapshot directory, registers metadata, inherits parent ownership, renames into place, commits metadata, and returns mounts. `Commit` records disk usage and commits active snapshots. `Remove` removes metadata and either defers cleanup or computes unreferenced directories for deletion. `Cleanup` deletes abandoned snapshot directories.

State and persistence: persistent state is `root/metadata.db` plus `root/snapshots/<id>/fs` and optional `work`. Mount generation uses bind mounts for single-layer cases and `fuse3.fuse-overlayfs` with `lowerdir`, `upperdir`, `workdir`, and converted UID/GID mapping labels for layered cases. Risks include untested async remove, cleanup races if directories are externally touched, reliance on parent ID order, no direct fsync of metadata/directories, and `convertIDMappingOption` blindly replacing commas with colons. Test signal is containerd's `SnapshotterSuite` in `fuseoverlayfs_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs_test.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs_test.go

Purpose: containerd snapshotter conformance test wiring for the fuse-overlayfs snapshotter.

Important flow: `newSnapshotter` creates a snapshotter rooted at the test directory and returns its `Close` cleanup. `TestFUSEOverlayFS` requires root, creates a temp dir, skips if `Supported` fails, then runs containerd `testsuite.SnapshotterSuite`.

State and integration: performs real filesystem, FUSE, and metadata operations in a temp directory. Requires root and functional fuse-overlayfs. Risks include environment-dependent skips, no dedicated assertions for async remove or ID mapping labels, and relying on upstream testsuite coverage. Test signal is strong behavioral conformance for standard snapshotter operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/plugin/plugin.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/plugin/plugin.go

Purpose: in-process containerd snapshot plugin registration for fuse-overlayfs.

Important flow: registers a plugin with type `plugins.SnapshotPlugin` and ID `fuse-overlayfs`. `Config` supports optional `root_path`; init appends default platform metadata, validates config type, chooses root from containerd property or config override, exports the root, and returns `fuseoverlayfs.NewSnapshotter(root)`.

State and integration: participates in containerd plugin registry and creates snapshotter state under the selected root. Unlike the standalone gRPC server, it does not call `Supported` during init. Risks include delayed runtime failures if `fuse-overlayfs` is unavailable, root path misconfiguration, and Linux build-tag limitation. Test signal is containerd plugin initialization in deployments rather than direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/.github/workflows/rust-test.yaml -->
# sources/cloud-native/fuse-overlayfs/.github/workflows/rust-test.yaml

Purpose: CI workflow for the Rust fuse-overlayfs implementation.

Important jobs: `build` installs stable Rust with clippy/rustfmt, caches Cargo state, checks formatting, runs clippy with warnings as errors, builds and tests release mode, and uploads the x86_64 binary. `integration-test` installs the binary and dependencies, builds containers/storage tests, runs project test scripts, unionmount tests, containers/storage tests, and unprivileged tests with and without overlay whiteouts. `cross-build` uses `cross` for multiple Linux architectures. `release` packages downloaded artifacts, writes `SOURCE_DATE_EPOCH`, creates SHA256 sums, and creates draft releases on version tags.

State and integration: extensive GitHub Actions automation using FUSE, root privileges, Podman/storage tests, and external repositories. Risks include external dependency drift, privileged kernel settings, long integration runtime, and tag-only release behavior. Test signal is strong across unit, integration, compatibility, and cross-arch builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/.github/workflows/rust-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/Cargo.toml -->
# sources/cloud-native/fuse-overlayfs/Cargo.toml

Purpose: Rust crate manifest for the fuse-overlayfs binary.

Important structure: package `fuse-overlayfs` version `2.0.0`, edition 2024, Rust 1.85 minimum, GPL-2.0-or-later metadata, and excludes CI/tests/containerfiles from packaging. Dependencies include `fuser` with ABI 7.40, `rustix`, `libc`, `signal-hook`, `parking_lot`, `log`, `env_logger`, `thiserror`, and `rustc-hash`; dev dependency is `tempfile`. Release profile enables LTO and stripping.

State and integration: controls build graph and published crate metadata. Risks include requiring recent Rust, FUSE ABI compatibility, and release builds optimized/stripped making debugging harder. Test signal is Cargo unit/build jobs in CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/Makefile -->
# sources/cloud-native/fuse-overlayfs/Makefile

Purpose: local build, test, install, and cleanup automation for the Rust fuse-overlayfs binary.

Important targets: `build` runs Cargo release build; `unit-test` runs release-mode Cargo tests; `integration-test` requires root, then runs a fixed list of shell integration tests with the built binary on PATH; `test-single` runs one integration script; `test` combines unit and integration; `install` installs the release binary; `clean` runs Cargo clean.

State and integration: writes Cargo target artifacts, installs to `$(DESTDIR)$(BINDIR)` when requested, and runs root/FUSE integration scripts. Risks include integration tests requiring root and host FUSE setup, release-mode tests taking longer, and `CARGO_HOME` defaulting to a repo-local `.cargo`. Test signal is explicit unit and integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/config.rs -->
# sources/cloud-native/fuse-overlayfs/src/config.rs

Purpose: command-line and `-o` option parser for the Rust fuse-overlayfs implementation.

Important APIs and flow: `OverlayConfig` stores paths, UID/GID mapping strings and parsed mappings, timeouts, xattr/NFS modes, squash options, booleans, FUSE pass-through options, and effective UID. `parse_args` injects default FUSE options based on root/non-root, handles `-f`, `-d`, help/version, `-o` separated and concatenated forms, records mountpoint, parses mappings, and makes `volatile` disable fsync. `split_options`, `unescape_path`, `parse_single_option`, `parse_lowerdir`, and `parse_plugin_path` handle comma/colon escaping, plugin lowerdir syntax, and known C-compatible options.

State and persistence: builds in-memory config only. Integration points are `main.rs`, `mapping.rs`, and `layer.rs`. Risks include unknown arguments being warnings rather than hard failures, partial plugin support, quoting/escape edge cases, and C compatibility expectations for option behavior. Test signal covers lowerdir parsing, plugin path parsing, option splitting, basic parse, xino, volatile, and multiple `-o`.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/copyup.rs -->
# sources/cloud-native/fuse-overlayfs/src/copyup.rs

Purpose: copy-up implementation that materializes lower-layer files/directories into the writable upper layer before modifications.

Important APIs and flow: `copy_xattr` copies extended attributes while skipping overlay-internal prefixes and tolerating unsupported/permission errors. `copy_data` tries `FICLONE`, then `sendfile`, then read/write fallback. `create_node_directory` recursively ensures parent directories are copied into upper, preserving ownership, timestamps, and xattrs via workdir temp names and safe renames. `copyup` handles directories, symlinks, special files, and regular files, creating objects in workdir then renaming into upper and updating node layer state.

State and persistence: writes temp files/directories in workdir and final objects in upperdir; removes related whiteouts where appropriate. Dependencies include `OvlLayer`, `NodeArena`, safe `openat2`, sys fs/io/xattr wrappers, and whiteout helpers. Risks include xattr buffer limits, partial cleanup on rename failures, file mode/ownership failures being ignored in places, and copy-up races with concurrent operations. Test signal should come from integration tests for copyup, xattr, special files, symlinks, and directory operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/copyup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/datasource.rs -->
# sources/cloud-native/fuse-overlayfs/src/datasource.rs

Purpose: trait abstraction for accessing overlay layer data sources.

Important APIs: constants define stat override xattrs; `StatOverrideMode` records none/user/privileged/containers modes; `DirIterator` and `DirEntry` abstract directory scanning; `DataSource` defines initialization, existence/stat/open/readlink/xattr operations, NFS file handle hashing, root fd/device reporting, stat override reporting, and NFS handle support reporting.

State and integration: trait has no state itself; implementations such as `DirectAccess` hold file descriptors and device metadata. It is consumed by layers, overlay operations, and copy-up code. Risks include every implementation needing safe path resolution internally, trait object overhead, and mode/xattr semantics needing to match the C implementation. Test signal is through direct datasource behavior and overlay integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/datasource.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/direct.rs -->
# sources/cloud-native/fuse-overlayfs/src/direct.rs

Purpose: direct filesystem-backed `DataSource` implementation.

Important flow: `load_data_source` resolves the layer path, opens it as a trusted directory, records device ID, probes NFS file handle support, and detects stat override mode through xattrs. File operations use `openat2::safe_openat` or safe parent opening to keep resolution inside the layer root. `statat` and `fstat` prefer `statx` with fallback to `fstatat`/`fstat`; xattr operations use proc-fd paths for l* xattr calls; `get_nfs_filehandle` hashes kernel file handles when available.

State and persistence: holds an owned root fd, resolved path, device ID, stat override mode, NFS support state, and file handle size. It reads filesystem metadata/xattrs and opens files but does not write. Risks include proc-fd xattr path assumptions, NFS probe error handling, xattr detection ordering, and reliance on openat2 support wrappers. Test signal is integration coverage for path safety, xattrs, inode stability, and layer loading.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/direct.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/error.rs -->
# sources/cloud-native/fuse-overlayfs/src/error.rs

Purpose: small errno-based error type for filesystem operations.

Important APIs: `FsError` wraps a `libc::c_int`, provides `last`, implements `Display` through `io::Error::from_raw_os_error`, implements `std::error::Error`, converts from `rustix::io::Errno` and `std::io::Error`, and defines `FsResult<T>`. `cstr` and `cstr_bytes` convert paths to `CString`, returning `EINVAL` on embedded nulls.

State and integration: stateless error glue used throughout sys, direct, copy-up, and overlay layers. Risks include losing richer IO context, defaulting unknown IO errors to `EIO`, and callers comparing raw errno values. Test signal is indirect through error paths in unit/integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/layer.rs -->
# sources/cloud-native/fuse-overlayfs/src/layer.rs

Purpose: overlay layer initialization and metadata wrapper.

Important APIs and flow: `OvlLayer` stores a boxed `DataSource` and whether it is a lower layer. `init_layers` parses lowerdir entries, initializes optional upper first, applies `xattr_permissions` override when no xattr mode was detected, enforces `xino=on` NFS file handle support, skips unimplemented plugin lowerdirs with warnings, initializes direct lower layers, and errors if no layers are specified. `all_same_device` checks whether every layer has the same device ID.

State and integration: opens layer root file descriptors through `DirectAccess`; no writes except any side effects of opening/probing. Risks include skipped plugin layers silently changing layer stack, strict xino support failures, and upper being index 0 as an important invariant for copy-up and overlay operations. Test signal comes from config/layer and integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/layer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/main.rs -->
# sources/cloud-native/fuse-overlayfs/src/main.rs

Purpose: binary entrypoint that parses configuration, initializes layers and FUSE, daemonizes if requested, and runs the filesystem session.

Important flow: parses args, initializes logging from `FUSE_OVERLAYFS_DEBUG_LOG` or env/default level, validates `lowerdir` and mountpoint, rejects redirect modes other than `off`, raises `RLIMIT_NOFILE`, warns on read-only `/proc`, opens workdir, initializes layers, builds fuser mount options and ACL from parsed options, creates `OverlayFs`, creates a `fuser::Session`, sets notifier for cache invalidation, daemonizes unless foreground, installs SIGUSR1 reporting, spawns and joins the FUSE session.

State and persistence: opens workdir/layer fds, mounts FUSE at mountpoint, may daemonize, writes logs, and SIGUSR1 reports node/inode stats. Dependencies include config/layer/overlay/sys modules and fuser. Risks include startup exits on missing options, workdir fd `-1` in read-only mode assumptions, daemonization timing, and signal logging fd lifetime. Test signal is integration tests that run the binary under mount scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/mapping.rs -->
# sources/cloud-native/fuse-overlayfs/src/mapping.rs

Purpose: UID/GID mapping and overflow ID utilities.

Important APIs: `IdMapping` represents a `host:to:len` range. `OverflowIds::read` reads kernel overflow UID/GID with fallback to `65534`. `parse_mappings` parses colon-separated triples and tolerates empty segments. `find_mapping` maps host-to-container for direct reads or container-to-host for writes, with direct-mode `squash_to_uid/gid` taking precedence over `squash_to_root`, and returns overflow ID for unmapped IDs when mappings are configured.

State and integration: reads `/proc/sys/kernel/overflowuid` and `overflowgid`; otherwise stateless. Used by config parsing and overlay ownership presentation/mutation. Risks include no overlap validation, empty segment filtering accepting unusual strings, and overflow behavior surprising callers when mappings are partial. Test signal covers parse success/failure, leading colon, direct/reverse mapping, squash-to-root, and squash-to-id precedence.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/mapping.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/node.rs -->
# sources/cloud-native/fuse-overlayfs/src/node.rs

Purpose: node arena, directory state, inode table, path computation, and statistics for the overlay filesystem.

Important APIs and flow: `DirState` separates non-directories from directories with child and whiteout maps plus loaded state. `NodeArena` owns `OvlNode` values behind opaque `NodeId`s and updates global node counters. `OvlNode` stores parent, layer indexes, underlying inode/device, name, hidden deletion state, link count, mode, and child/whiteout helpers. `Drop` cleans hidden files/dirs from workdir. `compute_fuse_ino` uses raw inode when layers share a device or hashes inode/device otherwise. `InodeTable` maps `(ino,dev)` to `OvlIno`, tracks hardlinks and lookup counts, resolves collisions with fallback inode numbers, leaves tombstones for recycled inodes, and handles FUSE forget.

State and persistence: all primary state is in-memory; hidden node cleanup can unlink workdir paths on drop. Integration points are overlay lookup/readdir/forget/copy-up paths and SIGUSR1 stats in `main.rs`. Risks include stale tombstones until forget, path computation cost via parent walks, concurrent consistency depending on outer locks, hidden cleanup best-effort behavior, and inode collision/recycling edge cases. Unit tests cover node creation, child maps, arena insert/remove, inode registration, forget, path computation, hashing, collision behavior, and related primitives.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/node.rs -->
