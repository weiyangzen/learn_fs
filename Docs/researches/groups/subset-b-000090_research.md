# Research: subset-b-000090

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/restore.go -->
# sources/cloud-native/cri-o/internal/lib/restore.go

Purpose: implements CRI-O checkpoint restore for an existing container. Important APIs are `ContainerServer.ContainerRestore` and `restoreFileSystemChanges`. Control flow looks up the target container, rejects running containers, reloads and rewrites `config.json`, mounts the rootfs, imports checkpoint payloads from either an archive or checkpoint image, reapplies rootfs diffs/deletions, recreates external bind-mount sources, rewires OCI namespaces to the destination sandbox, updates sandbox/name annotations, calls `runtime.RestoreContainer`, persists state, and optionally deletes checkpoint artifacts. State touches storage mounts, checkpoint files, restored logs, OCI specs in both container dir and bundle, and container state on disk. Dependencies include checkpointctl metadata, CRIU stats names, runtime-tools/generate, containers/storage archive helpers, CRI-O annotations, sandbox lookup, and OCI runtime restore. Risks are partial cleanup, rootfs mount/image unmount leaks on earlier errors, bind mount file-vs-directory mismatch, assuming Linux namespace/spec shapes are initialized, and log path overwrite. Test signals come from `restore_test.go`, which covers bad IDs, running containers, invalid configs, archive/image restore setup, bind-mount recreation, and runtime restore failure paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/restore_test.go -->
# sources/cloud-native/cri-o/internal/lib/restore_test.go

Purpose: Ginkgo coverage for `ContainerRestore`. Important helpers include `setupInfraContainerWithPid`, `createDummyConfig`, and suite fixtures from `internal/lib/suite_test.go`. The tests initialize mocked storage/runtime state, skip when required CRIU support is unavailable, and assert restore behavior for invalid container IDs, attempts to restore running containers, invalid specs, runtime restore failures, archive imports, and OCI checkpoint image imports. State is mostly temporary `config.json`, checkpoint directories, tar archives, fake runtime files, and mocked container/sandbox records. Dependencies include gomock storage expectations, containers/storage archive generation, CRIU probing, runtime-tools/generate, and CRI-O storage reference parsing. Risks are environment sensitivity around CRIU/root privileges and broad failure assertions that only check substrings after setup. Test signals are strongest for negative paths, checkpoint file staging, and bind-mount recreation setup; successful end-to-end restore remains outside this unit suite.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/restore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/builder.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/builder.go

Purpose: defines the pod sandbox builder interface and default `sandboxBuilder`. Important APIs include `NewBuilder`, `SetConfig`, `GenerateNameAndID`, all sandbox field setters, `SetCRISandbox`, `Validate`, and `GetSandbox`. Control flow uses a `sandboxValidations` bitmask; required setter calls mark fields and `GetSandbox` refuses incomplete sandboxes before returning the built `Sandbox` and clearing builder references. `SetConfig` normalizes nil Linux security context subfields, while `GenerateNameAndID` creates the Kubernetes-style sandbox name and non-crypto ID. State lives only in builder memory until a `Sandbox` is returned; `SetCRISandbox` also creates/updates the CRI API `PodSandbox` object. Dependencies include CRI runtime API types, hostport mappings, memorystore, OCI containers, storage ID mappings, and config. Risks are setter order sensitivity, map iteration making missing-validation error order nondeterministic, and setting validation flags before later validation errors in some methods. Tests cover config validation, generated IDs/names, duplicate config rejection, and successful construction.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/fixtures/expanded_resolv.conf -->
# sources/cloud-native/cri-o/internal/lib/sandbox/fixtures/expanded_resolv.conf

Purpose: expected resolver output fixture for `ParseDNSOptions` when many search domains are provided. It contains one `search` line with seven search entries, two `nameserver` lines, and one `options` line. There are no APIs or runtime control flow; it is static test data. State and persistence are limited to the repository fixture and temporary comparison files created by tests. It integrates with `infra_test.go` to verify that CRI-O writes DNS config without truncating expanded Kubernetes search lists. Risks are fixture drift if resolver rendering rules change. Test signal is direct byte equality against generated `fixtures/resolv_test.conf`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/fixtures/expanded_resolv.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/fixtures/resolv.conf -->
# sources/cloud-native/cri-o/internal/lib/sandbox/fixtures/resolv.conf

Purpose: expected resolver output fixture for normal DNS server/search/option rendering. It contains a two-entry `search` line, two nameservers, and retry/timeout options. There are no functions or state transitions; the file is static data. It integrates with `ParseDNSOptions` tests as the canonical output for explicit DNS configuration. State is only fixture content plus temporary generated output. Risks are false failures if formatting intentionally changes, such as line ordering or option spacing. Test signal is byte-for-byte comparison in `infra_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/fixtures/resolv.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/infra.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/infra.go

Purpose: initializes the infra container spec and pod `resolv.conf`. Important APIs are `InitInfraContainer`, `Spec`, `PauseCommand`, `ParseDNSOptions`, and helpers `createResolvConf`/`copyFile`. Control flow creates a factory container, resolves the pause command from config or image entrypoint/cmd, configures OCI generator defaults/rlimits/capabilities, writes DNS config or copies `/etc/resolv.conf`, relabels/chowns it, and adds a read-only bind mount to `/etc/resolv.conf`. State includes builder infra generator, sandbox `resolvPath`, DNS config defaulting, and the generated resolv file. Dependencies include image-spec, runtime-tools/generate, SELinux labels, idtools mappings, storage container info, CRI API DNS config, and podman storage utilities. Risks include cleanup masking original errors, copying host resolver config verbatim, SELinux/chown failures, and nil config/image cases. Tests cover DNS rendering, pause command selection, and error cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/infra.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/infra_linux.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/infra_linux.go

Purpose: Linux implementation of pod shared-memory setup. The main API is `SetupShm`, which validates `shmSize`, creates `<podSandboxRunDir>/shm`, and mounts a `tmpfs` with noexec/nosuid/nodev, mode 1777, requested size, and SELinux mount label formatting. State is a host directory plus a mounted tmpfs that later sandbox code unmounts. Dependencies are `unix.Mount`, SELinux label formatting, and filesystem creation. Risks include requiring mount privileges, leaving a directory behind if mount fails, mount-label errors, and no cleanup in this function. Tests cover invalid sizes, empty label behavior through mount failure, and pre-existing directory errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/infra_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/infra_test.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/infra_test.go

Purpose: validates sandbox infrastructure helper behavior. It exercises `ParseDNSOptions`, `PauseCommand`, and `SetupShm`. Control flow writes a temporary resolver file and compares it with either `/etc/resolv.conf` or repository fixtures, builds default CRI-O config to test pause command fallback and image command handling, and calls Linux shm setup for invalid parameters. State is temporary files under `fixtures/resolv_test.conf` and temp directories. Dependencies are Ginkgo/Gomega, image-spec `v1.Image`, CRI-O config defaults, and sandbox helpers. Risks include comparing against host `/etc/resolv.conf`, mount-privilege sensitivity for shm cases, and limited positive coverage of successful mounts. Test signals verify DNS line formatting, default/custom pause command behavior, nil config/image errors, and shm validation failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/infra_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/namespaces.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/namespaces.go

Purpose: manages sandbox namespace references and exposes namespace paths. Important APIs are `AddManagedNamespaces`, `NamespacePaths`, `RemoveManagedNamespaces`, `NetNsPath`/`Join`, `IpcNsPath`/`Join`, `UtsNsPath`/`Join`, `UserNsPath`/`Join`, `PidNsPath`, and helpers `nsJoin`, `infraPid`, `nsPathGivenInfraPid`. Control flow stores pinned namespace objects by type, returns pinned paths when available or falls back to `/proc/<infra-pid>/ns/<type>`, aggregates removal errors, and rejects joining a second namespace of the same type unless stopped paths suppress some errors. State is held on `Sandbox` fields for ipc/net/uts/user namespaces; PID namespace is derived from infra container pid. Dependencies include CRI-O namespace manager, managed namespace wrappers, OCI container pid/state, and logrus. Risks include panicking on unknown namespace types, stale `/proc` paths, silently ignoring expected `ErrNotInitialized`, and stopped-sandbox join semantics that can hide invalid paths. Tests cover nil/empty namespaces, spoofed namespaces, invalid panic, join errors, path fallback, and infra pid cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/namespaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/namespaces_test.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/namespaces_test.go

Purpose: Ginkgo coverage for sandbox managed namespace behavior. It tests adding managed namespaces, removing them, joining existing namespace paths, rejecting invalid or duplicate joins, and path reporting with or without an infra container. State is a test sandbox plus spoofed namespace objects and temporary references to `/proc/self/ns/*`. Dependencies include `nsmgr` types, `nsmgr/test` helpers, os pid lookup, and suite setup. Risks are platform assumptions around namespace files and max PID values, plus duplicate test names for non-namespace cases. Test signals verify four managed namespace paths, panic on invalid namespace type, remove success, error reporting for missing/non-namespace paths, and `/proc` fallback when an infra pid is running.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/namespaces_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/sandbox.go

Purpose: core in-memory representation of a CRI-O pod sandbox. Important APIs include getters for CRI metadata, labels, namespace, logging, cgroups, resource hints, resolver/hostname paths, `AddContainer`/`GetContainer`/`RemoveContainer`, infra container setters, state transitions `SetCreated`, `SetStopped`, `SetNetworkStopped`, `RestoreStopped`, `Ready`, `State`, and `.containerenv` creation. Control flow keeps mutable lifecycle state behind `stateMutex`, protects stop flows with `stopMutex`, clones the CRI protobuf when returned state changes, and persists stopped/network-stopped marker files in the infra container dir for restore after daemon restart. State includes CRI `PodSandbox`, container store, namespace handles, ip cache, security labels, runtime handler, resource pointers, and marker files. Dependencies include CRI API types, protobuf clone, hostport, memorystore, OCI containers, log spans, and Kubernetes field sets. Risks include nil infra/container dereferences in file helpers, marker file best-effort behavior, direct exposure of maps/slices, and state correctness relying on callers taking transitions in order. Tests cover field construction, getters, state changes, DNS config, infra/container management, `.containerenv`, and `NeedsInfra`.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_builder_test.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_builder_test.go

Purpose: validates `sandboxBuilder` construction and config behavior. It pre-populates required validation fields in `BeforeEach`, then tests `SetConfig`, `GenerateNameAndID`, duplicate config protection, and validation compatibility with nil or rejected configs. State is a fresh builder per test, CRI pod metadata, and generated sandbox ID/name values. Dependencies include Ginkgo/Gomega, CRI runtime API types, hostport mappings, and sandbox builder methods. Risks are that many required fields are pre-set to empty strings, so tests validate presence rather than semantic content; generated IDs are checked only by length. Test signals confirm default Linux security context creation paths indirectly, required metadata name/namespace/uid checks, and that `GetSandbox` succeeds once validation flags are satisfied.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_builder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_freebsd.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_freebsd.go

Purpose: FreeBSD-specific sandbox stubs and policy. It defines a noop `NetNs` type with unsupported initialization/get functions, no-op symlink/close/remove methods, `hostNetNsPath` returning unsupported, `UnmountShm` as no-op, and `NeedsInfra` based on whether server drops infra and network namespace mode is POD. State is intentionally absent for network namespace operations. Dependencies are CRI namespace mode types and context. Risks are feature gaps hidden by no-op methods, callers assuming Linux netns behavior, and broad unsupported errors. Tests in generic sandbox tests exercise `NeedsInfra` on supported builds; FreeBSD-specific netns behavior relies mainly on compile-time separation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_linux.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_linux.go

Purpose: Linux-specific sandbox shared-memory cleanup and infra requirement policy. Important APIs are `UnmountShm` and `NeedsInfra`. `UnmountShm` returns early for `/dev/shm`, otherwise performs lazy unmount and ignores `EINVAL`/`ENOENT` to tolerate already-unmounted paths. `NeedsInfra` returns true unless the server manages namespace lifecycles and the pod PID mode is not POD. State affected is the host shm mount; no in-memory fields are changed. Dependencies include `unix.Unmount`, CRI namespace mode, and tracing logs. Risks include nil `nsOpts` callers if not initialized, lazy unmount hiding busy mounts, and platform-specific behavior. Tests cover `NeedsInfra` cases and invalid shm setup in infra tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_test.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_test.go

Purpose: broad Ginkgo tests for `Sandbox` getters, lifecycle state, container membership, and infra policy. It constructs sandboxes through the builder and asserts IDs, labels, annotations, labels, cgroup/runtime/hostname/resolv fields, stop mutex, container store, and creation time. Control flow then mutates seccomp path, IPs, stopped/network-stopped/created flags, DNS config, hostname path, namespace options, and container/infra attachment. State includes test containers, memorystore entries, and `.containerenv` paths. Dependencies include CRI API types, storage references, OCI container creation, hostport, memorystore, and suite fixtures. Risks are mostly getter-level coverage with limited marker-file persistence assertions and one misleading test title around `NeedsInfra`. Test signals verify ready/not-ready transitions, duplicate infra rejection, nil infra rejection, and `NeedsInfra` behavior for PID namespace modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_test_inject.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_test_inject.go

Purpose: test-only injection helper for sandbox port mappings. Build tag `test` limits it to test builds. The single API `(*Sandbox).SetPortMappings` directly assigns the private `portMappings` field so tests can alter sandbox state without broad production setters. There is no persistence or external control flow. Dependencies are CRI-O hostport types and the sandbox package. Risks are accidental reliance on this helper outside test builds and bypassing validation or defensive copying. Test signal is indirect: sandbox tests can set or assert port mappings through controlled fixture setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_unsupported.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_unsupported.go

Purpose: non-Linux, non-FreeBSD fallback implementation for sandbox platform hooks. It provides no-op `UnmountShm` and `NeedsInfra` returning false. There are no data structures or persistence. Integration is purely via Go build tags so unsupported platforms compile without Linux mount or FreeBSD jail/netns behavior. Dependencies are only `context`. Risks are semantic under-reporting: callers on unsupported platforms will not require infra containers and shm cleanup is skipped, which may be acceptable only because those runtime features are unavailable. Test signals are compile-time coverage for unsupported platforms rather than runtime tests in this repository slice.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/sandbox_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/suite_test.go -->
# sources/cloud-native/cri-o/internal/lib/sandbox/suite_test.go

Purpose: Ginkgo suite bootstrap and shared fixture creation for sandbox tests. It registers `TestSandbox`, initializes a `TestFramework`, suppresses logrus noise, and defines `beforeEach` to build a valid baseline sandbox and a fresh builder. State includes package globals `t`, `testSandbox`, and `builder`. Dependencies include CRI API metadata, hostport, memorystore, OCI containers, sandbox builder, and CRI-O test framework. Risks include shared globals requiring strict test isolation and fixture defaults that set many required fields to empty values while satisfying validation flags. Test signals are enabling infrastructure for all sandbox Ginkgo specs and confirming builder construction is viable in repeated setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/sandbox/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/cgroup_stats_linux.go -->
# sources/cloud-native/cri-o/internal/lib/stats/cgroup_stats_linux.go

Purpose: defines Linux cgroup statistics shape consumed by CRI-O stats and metrics code. `CgroupStats` embeds `cgroups.Stats` and adds `ProcessStats` plus `SystemNano`; `ProcessStats` carries pids, file descriptor, socket, thread, thread limit, and soft ulimit counters. There is no control flow or persistence here; it is a data contract returned by runtime/cgroup managers. Dependencies are opencontainers/cgroups. Integration points include statsserver conversion functions, process metrics, OOM/disk IO/CPU/memory metrics, and CRI summary stats. Risks are field population consistency across cgroup v1/v2 and assuming `SystemNano` is the collection timestamp. Test signals are indirect through statsserver metric cardinality and runtime stats consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/cgroup_stats_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/cgroup_stats_unsupported.go -->
# sources/cloud-native/cri-o/internal/lib/stats/cgroup_stats_unsupported.go

Purpose: non-Linux placeholder for cgroup statistics. It defines an empty `CgroupStats` type so packages compile where opencontainers cgroup stats are unavailable. There are no functions, state, or persistence. Integration is selected by `!linux` build tag and paired with unsupported statsserver behavior. Risks are callers expecting populated fields on unsupported platforms, so platform-specific code must avoid Linux-only conversions. Test signals are compile-time platform coverage rather than runtime assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/cgroup_stats_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/disk_stats_freebsd.go -->
# sources/cloud-native/cri-o/internal/lib/stats/disk_stats_freebsd.go

Purpose: FreeBSD disk usage collection for container filesystem metrics. Important types are `DiskStats` and `FilesystemStats`; `GetDiskUsageForPath` gathers used bytes through CRI-O utilities and filesystem capacity/inodes through `syscall.Statfs`. State is sampled from the host filesystem and returned as JSON-tagged values; nothing is persisted. Dependencies include `utils.GetDiskUsageStats` and FreeBSD `Statfs_t`. Integration feeds statsserver disk metrics and CRI writable-layer style reporting. Risks include syscall type differences, permission/path errors, and total capacity reflecting the filesystem containing the path rather than container quota. Test signals are indirect via consumers; unsupported and Linux implementations share the same public shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/disk_stats_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/disk_stats_linux.go -->
# sources/cloud-native/cri-o/internal/lib/stats/disk_stats_linux.go

Purpose: Linux disk usage collection for container filesystem metrics. Important APIs are `DiskStats`, `FilesystemStats`, and `GetDiskUsageForPath`. Control flow gets path usage via `utils.GetDiskUsageStats`, then calls `syscall.Statfs` for total blocks and inode totals/free counts. State is a point-in-time filesystem sample; no persistence. Dependencies include CRI-O utils and Linux `syscall.Statfs_t`. Integration points are runtime disk stats, statsserver CRI filesystem stats, and Prometheus-like disk metrics. Risks include path errors, filesystem-wide limits instead of overlay/quota-specific limits, integer casts from `Bsize`, and expensive disk walks in `GetDiskUsageStats`. Test signals are indirect through statsserver conversions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/disk_stats_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/disk_stats_unsupported.go -->
# sources/cloud-native/cri-o/internal/lib/stats/disk_stats_unsupported.go

Purpose: fallback disk stats API for platforms other than Linux and FreeBSD. It preserves `DiskStats`, `FilesystemStats`, and `GetDiskUsageForPath` signatures but always returns an unsupported error. There is no runtime state beyond the returned error. Integration allows callers to compile while platform-specific statsserver paths avoid real disk collection. Risks are callers treating unsupported as fatal in generic code and missing filesystem metrics on these platforms. Test signals are compile-time and any platform tests that expect the explicit "disk usage statistics not supported" error.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/stats/disk_stats_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/cpu_metrics_linux.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/cpu_metrics_linux.go

Purpose: converts cgroup CPU stats into CRI metrics. The main API is `generateContainerCPUMetrics`, which emits user/system/total usage seconds plus CFS period, throttled period, and throttled seconds counters. Control flow handles nil CPU stats, reports a `total` CPU label if no per-CPU values exist, otherwise emits nonzero per-CPU values as `cpu%02d`. State is computed per call with current timestamps supplied by `computeContainerMetrics`. Dependencies include opencontainers/cgroups, CRI metric types, OCI container labels, and metric descriptors. Risks include integer truncation from nanoseconds to seconds, omitting zero per-CPU entries, and label cardinality changes. Tests cover metric label cardinality and non-empty metric generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/cpu_metrics_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/descriptors.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/descriptors.go

Purpose: defines all CRI metric descriptors exported by statsserver. It groups descriptors for CPU, disk, disk IO, hugeTLB, memory, network, OOM, process, last-seen, spec, and pressure metrics. There is no executable control flow; the important state is descriptor names, help text, and `LabelKeys`, most based on `baseLabelKeys` with metric-specific labels. Dependencies are CRI runtime metric descriptor types and config keys consumed in `metrics.go`. Integration determines what kubelet/prometheus clients accept and what `availableMetricDescriptors` exposes. Risks are label-key/value cardinality drift, descriptor name compatibility changes, and `append(baseLabelKeys, ...)` sharing/capacity surprises if base labels were mutated. Tests in `metrics_test.go` build descriptor label counts and verify every generated metric has matching label values.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/descriptors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/disk_metrics_linux.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/disk_metrics_linux.go

Purpose: converts filesystem and blkio stats into container metrics. APIs are `generateContainerDiskMetrics` and `generateContainerDiskIOMetrics`. Filesystem metrics emit inode free/total, limit bytes, and usage bytes gauges. Disk IO metrics iterate cgroup blkio service counts/bytes, label devices as `major:minor`, emit read/write counters, and add `container_blkio_device_usage_total` with device, major, minor, and lowercase operation labels. State is per-call metric values only. Dependencies include cgroups blkio structures, CRI metric types, CRI-O stats filesystem stats, and OCI container labels. Risks include closure capture over range variables if Go semantics change, unknown operation names only producing generic blkio usage, unresolved device names, nil handling, and label cardinality. Tests cover cardinality for read/write sample stats.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/disk_metrics_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/hugetlb_metrics_linux.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/hugetlb_metrics_linux.go

Purpose: converts cgroup hugeTLB stats into CRI metrics. `generateContainerHugetlbMetrics` emits usage and max-usage gauges per page size label. Control flow iterates the `map[string]cgroups.HugetlbStats` separately for each descriptor and delegates label/base construction to `computeContainerMetrics`. State is per-call only and map iteration order is not stable. Dependencies are cgroups hugeTLB stats, CRI metric types, descriptors, and OCI container identity. Risks include nondeterministic metric order, nil maps producing zero metrics but non-nil result, and label cardinality if descriptor labels change. Test signals verify generated sample metrics match descriptor label counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/hugetlb_metrics_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/memory_metrics_linux.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/memory_metrics_linux.go

Purpose: converts cgroup memory stats into CRI metrics and OOM metrics. Important APIs are `generateContainerMemoryMetrics`, `computeMemoryMetricValues`, `computeSwapUsageForMetrics`, `computeFileMapped`, and exported `GenerateContainerOOMMetrics`. Control flow derives working set by subtracting inactive file, selects cgroup v1/v2 stat names, computes actual swap differently for v2, emits cache/rss/kernel/mapped/swap/failcnt/usage/max/working-set gauges or counters, and emits page fault metrics for container and hierarchy scopes. State is sampled cgroup data only. Dependencies include cgroups, CRI metric types, CRI-O node cgroup mode detection, and OCI container labels. Risks include missing stat keys yielding zeros, duplicate page fault values for container/hierarchy, integer-only metrics, and v1/v2 semantic drift. Tests cover non-empty memory/OOM metrics and label cardinality.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/memory_metrics_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/metrics.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/metrics.go

Purpose: shared metric descriptor selection and metric assembly. Important types are `metricValue`, `metricValues`, `containerMetric`, and `SandboxMetrics`; important APIs are `NewSandboxMetrics`, `GetMetric`, `PopulateMetricDescriptors`, `computeSandboxMetrics`, `computeContainerMetrics`, and `computeMetrics`. Control flow maps config metric keys to descriptors, always includes `container_last_seen`, builds base labels for pods (`id`, `POD`, empty image) and containers (`id`, name, image), appends extra labels, and stamps every metric with current time. State includes descriptor maps and metric slices in `SandboxMetrics`. Dependencies include CRI API metrics, sandbox/OCI identities, and config metric keys. Risks include no validation of included config keys, timestamp per metric rather than per scrape, possible aliasing when no extra labels, and cardinality mismatches. Tests focus on descriptor label counts versus generated metric labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/metrics_test.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/metrics_test.go

Purpose: verifies generated metrics have label value counts matching their descriptors, preventing kubelet/prometheus rejection. It constructs a test OCI container with resources, sample cgroup CPU/memory/blkio/pids/process/disk/hugeTLB stats, synthetic network metrics, and invokes every generator. State is all in-memory test data plus container resource spec. Dependencies include Go testing, cgroups types, runtime-spec resources, CRI API types, stats structs, and OCI container creation. Risks are cardinality-only coverage: values, timestamps, cgroup v2 behavior, nil cases, and order are not fully asserted. Test signals are strong for descriptor/generator compatibility across CPU, disk, disk IO, hugeTLB, memory, network, OOM, process, spec, and pressure metric families.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/network_metrics_linux.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/network_metrics_linux.go

Purpose: generates pod-level network metrics from netlink link statistics. APIs are `StatsServer.GenerateNetworkMetrics` and `generateSandboxNetworkMetrics`. Control flow lists links in the current network namespace, logs and returns nil on list errors or empty lists, skips links with nil attrs, and emits receive/transmit bytes, packets, drops, and errors counters labeled by interface name. State is sampled host/network-namespace link stats only. Dependencies include vishvananda/netlink, CRI metric types, sandbox base labels, and CRI-O logging. Integration is called by Linux statsserver when network metrics are enabled. Risks include relying on caller to enter the right netns in some paths, returning nil on empty lists, including loopback depending on namespace, and label cardinality. Tests use synthetic metrics for cardinality rather than real netlink.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/network_metrics_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/pressure_metrics_linux.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/pressure_metrics_linux.go

Purpose: converts cgroup PSI totals into pressure stall metrics. APIs are `microSecondsToSeconds` and `generateContainerPressureMetrics`. Control flow checks CPU, memory, and blkio stats independently for non-nil PSI data, then emits full/stalled and some/waiting counters converted from microseconds to whole seconds. State is sampled cgroup PSI data only. Dependencies include cgroups PSI structures, CRI metric types, descriptors, and OCI container labels. Risks include truncating sub-second pressure, silently omitting unavailable PSI sources, and terminology differences between kernel/cAdvisor/CRI metric names. Tests cover sample pressure metrics for cardinality and non-empty output.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/pressure_metrics_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/process_metrics_linux.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/process_metrics_linux.go

Purpose: converts pids and CRI-O process-side stats into container process metrics. The main API is `generateContainerProcessMetrics`, which emits file descriptors, process count, sockets, thread count, thread max, and soft max-open-files ulimit metrics. Control flow returns no metrics if pids or process stats are nil and otherwise builds gauges through `computeContainerMetrics`. State is per-call sampled process/cgroup data. Dependencies include cgroups `PidsStats`, CRI-O `stats.ProcessStats`, CRI metric descriptors, and OCI container labels. Risks include only exposing one ulimit label, inconsistent collection of process stats versus cgroup pids, and nil stats dropping all process metrics. Tests verify cardinality for sample values.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/process_metrics_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/spec_metrics_linux.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/spec_metrics_linux.go

Purpose: emits metrics derived from the container resource spec rather than live cgroup stats. Important APIs are `generateContainerSpecMetrics` and `specMemoryValue`. Control flow reads Linux resources from the OCI container, reports memory limit/swap limit, CPU shares/period, start time, optional positive CPU quota, and memory reservation from unified `memory.min`. It parses `memory.min`, logging parse errors, and maps negative or effectively unlimited memory values to zero. State is container resource spec and creation time. Dependencies include CRI API types, CRI-O logging, OCI container resources, and metric descriptors. Risks include nil resources producing no metrics, only cgroup v2 unified `memory.min` used for reservation, parse failures silently omitting reservation, and integer semantics for unlimited values. Tests validate sample spec metric cardinality.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/spec_metrics_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/stats_server.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/stats_server.go

Purpose: platform-neutral statsserver orchestration, caching, and public API. Important types/APIs are `StatsServer`, `parentServerIface`, `New`, `updateLoop`, `update`, `StatsForSandbox`, `StatsForSandboxes`, `StatsForContainer`, `StatsForContainers`, remove methods, `Shutdown`, `MetricsForPodSandbox`, and `MetricsForPodSandboxList`. Control flow starts a background update loop when `CollectionPeriod` is nonzero; otherwise requests collect on demand. A mutex guards maps for sandbox stats, container stats, and sandbox metrics. It computes `UsageNanoCores` from old/current CPU samples and populates writable-layer usage through containers/storage graph driver. State persists only in memory caches until removal or shutdown. Dependencies include parent server runtime/store/config/sandbox listing, containers/storage, CRI stats types, sandbox and OCI packages. Risks include `time.After` allocation loop, unlocked `alreadyShutdown`, stale cache entries without remove calls, writable-layer errors only logged, and divide-by-zero/underflow risk if CPU timestamps or counters regress. Tests are mostly indirect through platform conversions and suite consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/stats_server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/stats_server_linux.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/stats_server_linux.go

Purpose: Linux implementation of sandbox/container stats and metrics collection. Important APIs include `updateSandbox`, `updateContainerStats`, `populateNetworkUsage`, `metricsForPodSandbox`, `updatePodSandboxMetrics`, `GenerateSandboxContainerMetrics`, `containerMetricsFromContainerStats`, CRI conversion helpers, `linkToInterface`, `computeMemoryStats`, `computeSwapUsage`, and `isMemoryUnlimited`. Control flow collects sandbox cgroup stats, pod network usage inside the sandbox netns, runtime cgroup/disk stats per non-stopped container, writable-layer usage, CPU nano-core deltas, and config-enabled CRI metrics. State updates the statsserver maps for sandbox stats, container stats, and sandbox metrics. Dependencies include CNI ns execution, netlink, cgroups, CRI-O cgroup manager, runtime stats interfaces, stats structs, config metric keys, sandbox namespace paths, and logging. Risks include dereferencing `ctrStats` after runtime errors in `updateSandbox`, nil `diskStats` passed to metric conversion for disk metrics, network namespace failures, stopped-container filtering, cgroup v1/v2 memory differences, and metric update serialization under one mutex. Tests mainly cover metric cardinality; broader behavior depends on integration tests/mocks elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/stats_server_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/stats_server_unsupported.go -->
# sources/cloud-native/cri-o/internal/lib/statsserver/stats_server_unsupported.go

Purpose: non-Linux statsserver fallback. It provides stub implementations for `updateSandbox`, `updateContainerStats`, and `metricsForPodSandbox`, each returning empty CRI stats/metrics structures. There is no real control flow, persistence, or external collection. Dependencies are sandbox, OCI, and CRI API types so generic statsserver code compiles. Risks include callers receiving empty-but-non-nil stats and assuming data was collected, and no remove/cache behavior in the platform functions. Test signals are compile-time platform coverage rather than runtime validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/statsserver/stats_server_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/suite_test.go -->
# sources/cloud-native/cri-o/internal/lib/suite_test.go

Purpose: shared Ginkgo suite setup for `internal/lib` tests. It registers `TestLib`, creates a test framework, initializes common mocks for storage, lib interface, and OCI runtime, builds a large sample OCI manifest annotation payload, and defines helpers for clean state/config files, container/sandbox fixture setup, runtime command mocking, and storage directory expectations. State is held in package globals such as `sut`, `config`, mocks, `mySandbox`, `myContainer`, and temp paths. Dependencies include gomock, CRI API types, CRI-O config/lib/sandbox/memorystore/OCI packages, storage mocks, and test framework. Risks are global mock lifecycle coupling, root-ish temp paths such as `/tmp/fake-runtime`, and broad shared fixture assumptions across tests. Test signals are enabling restore and other lib tests with controlled mocked runtime/storage behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/lib/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/linklogs/link_logs.go -->
# sources/cloud-native/cri-o/internal/linklogs/link_logs.go

Purpose: supports Kubernetes linked log volumes by mounting pod logs into an emptyDir and symlinking container log files. Important APIs are `MountPodLogs`, `UnmountPodLogs`, `LinkContainerLogs`, and helper `podEmptyDirPath`. Control flow validates emptyDir volume names as DNS-1123 labels, securely joins kubelet pod/volume paths, checks the emptyDir exists, constructs `/var/log/pods/<namespace>_<name>_<uid>`, bind mounts it read-only through platform helpers, applies SELinux label, unmounts if the emptyDir still exists, and creates relative symlinks like `<container>/<attempt>.log`. State is host mount state and symlinks under kubelet-managed directories. Dependencies include `filepath-securejoin`, SELinux label APIs, Kubernetes validation, CRI container metadata, platform mount helpers, and CRI-O logging. Risks include requiring host mount privileges, SELinux failures, kubelet path layout assumptions, not validating pod UID/namespace/name as strongly as volume name, and symlink collisions. Test signals are not present in this subset; behavior should be integration-tested with kubelet volume layouts.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/linklogs/link_logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/linklogs/utils_freebsd.go -->
# sources/cloud-native/cri-o/internal/linklogs/utils_freebsd.go

Purpose: FreeBSD implementation of linked-log platform helpers. `mountLogPath` and `unmountLogPath` both return explicit unsupported errors. There is no state mutation or persistence because no mount operation is attempted. Integration is selected by `freebsd` build tag and used by `MountPodLogs`/`UnmountPodLogs`. Risks are feature unavailability on FreeBSD and callers surfacing unsupported errors when linked logs are configured. Test signals are compile-time separation and any platform-specific error handling tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/linklogs/utils_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/linklogs/utils_linux.go -->
# sources/cloud-native/cri-o/internal/linklogs/utils_linux.go

Purpose: Linux mount helpers for linked pod logs. `mountLogPath` performs a read-only bind mount from kubelet pod logs into the emptyDir target; `unmountLogPath` performs a lazy detach. State is host mount table changes. Dependencies are `golang.org/x/sys/unix`. Integration is called by `link_logs.go` after path validation and before SELinux relabeling. Risks include requiring privileges, read-only bind semantics varying by kernel, lazy unmount hiding busy users, and no direct path validation in this layer. Test signals are likely integration-level; no direct unit tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/linklogs/utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook.go -->
# sources/cloud-native/cri-o/internal/log/hook.go

Purpose: removes logrus hooks by concrete type name. The single API `RemoveHook(logger, name)` rebuilds a `logrus.LevelHooks` map, retaining hooks whose `fmt.Sprintf("%T", hook)` is not `*log.<name>`, then replaces the logger hooks. State mutation is limited to the passed logger. Dependencies are logrus and fmt. Integration supports toggling CRI-O custom hooks such as `FilterHook` and `FileNameHook`. Risks include matching by stringified type name, package path assumptions, removing all hooks of that type across all levels, and not handling nil logger. Tests cover removing `FilterHook` while preserving `FileNameHook` and replacing hooks.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_filename.go -->
# sources/cloud-native/cri-o/internal/log/hook_filename.go

Purpose: logrus hook/formatter wrapper that adds caller file information to debug logs. Important types are `FileNameHook` and `wrapper`; APIs include `NewFilenameHook`, `Levels`, `Fire`, `Format`, `findCaller`, `caller`, and `shouldSkipPrefix`. Control flow installs a formatter wrapper on first fire or when the logger formatter changes, finds a caller by skipping known log/logrus stack frames, shortens file paths to the last two components, and writes a configured field, default `file`, before delegating to the old formatter. State is cached formatter and hook settings. Dependencies include runtime caller frames, strings, fmt, and logrus. Risks include mutating `entry.Logger.Formatter` during logging, fragile skip counts, caller misidentification across wrappers, and concurrency concerns. Tests cover creation, debug level activation, fire success, and default formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_filename.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_filename_test.go -->
# sources/cloud-native/cri-o/internal/log/hook_filename_test.go

Purpose: unit coverage for the file-name log hook. It verifies `NewFilenameHook` returns a hook, `Levels` is debug-only, `Fire` succeeds against a JSON formatter, and the default `Formatter` renders `file:line`. State is a temporary logrus entry/logger. Dependencies include Ginkgo/Gomega, logrus, and CRI-O log package. Risks are limited coverage of actual caller discovery, formatter wrapping behavior under concurrent logging, skip-prefix behavior, and emitted fields in formatted output. Test signals catch basic construction/API regressions but not full integration with standard logger output.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_filename_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_filter.go -->
# sources/cloud-native/cri-o/internal/log/hook_filter.go

Purpose: logrus hook for custom message filtering and debug redaction. Important APIs are `NewFilterHook`, `Levels`, and `Fire`. Control flow compiles an optional custom regexp; on log events, if a custom filter exists and the message does not match, it replaces the entry with a discard logger/JSON formatter. For debug logs it also redacts predefined bracketed numeric/slice-looking content with `[FILTERED]`. State is the compiled custom and predefined regexps. Dependencies are regexp, io.Discard, fmt, and logrus. Risks include replacing the entire entry instead of just suppressing output, regexp cost, false positives in predefined filtering, and custom filter semantics as allow-list rather than deny-list. Tests cover creation, invalid regex, all-level activation, filtering, and byte-slice-style redaction.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_filter_test.go -->
# sources/cloud-native/cri-o/internal/log/hook_filter_test.go

Purpose: validates filter hook construction and behavior. Tests assert empty filters succeed, invalid regex fails, `Levels` covers all logrus levels, nonmatching messages are filtered by entry replacement, and debug messages containing byte-slice-like numeric brackets are redacted. State is local logrus entries and compiled hook instances. Dependencies are Ginkgo/Gomega, fmt, logrus, and CRI-O log package. Risks are tests checking entry message emptiness after full entry replacement rather than output behavior, and only one predefined redaction pattern. Test signals protect regex compilation error handling and broad custom/predefined filtering semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_filter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_test.go -->
# sources/cloud-native/cri-o/internal/log/hook_test.go

Purpose: tests hook removal behavior. It creates a fresh logrus logger, adds `FilterHook` and `FileNameHook`, removes by type name, and checks hook map length; it also verifies a remove-then-add scenario. State is a local logger and hook instances. Dependencies are Ginkgo/Gomega, logrus, and CRI-O log hooks. Risks are assertions based on logrus level-hook map lengths, which can be brittle because hooks register across levels differently. Test signals confirm `RemoveHook` filters by concrete CRI-O hook name and that replacement does not corrupt logrus hook registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/hook_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/interceptors/interceptors.go -->
# sources/cloud-native/cri-o/internal/log/interceptors/interceptors.go

Purpose: gRPC interceptors for request-scoped logging, tracing, and operation metrics. Important APIs are `ServerStream`, `NewServerStream`, `StreamInterceptor`, `UnaryInterceptor`, `AddRequestNameAndID`, and helpers for request ID/name context values. Control flow wraps stream contexts with a UUID and method name, logs stream errors, starts an OpenTelemetry span for unary calls, logs request/response using compact formatting for `List*` operations, invokes the handler, records operation count/latency/error metrics, and ends the span. State is context values and metrics side effects; `ServerStream` stores a replacement context. Dependencies include gRPC, uuid, CRI-O log package, opentelemetry tracer, and server metrics. Risks include large non-list payload logging, debug logging sensitive request data, span not ended if panic occurs, and metrics singleton coupling. Test signals are not in this subset; integration tests should verify context propagation and metric increments.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/interceptors/interceptors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/klog.go -->
# sources/cloud-native/cri-o/internal/log/klog.go

Purpose: bridges Kubernetes `klog`/`logr` output into logrus. `InitKlogShim` disables stderr logging and installs `logSink`. `logSink.Info` writes klog info as logrus debug; `Error` writes logrus error with optional error text; `writeKeysAndValues` formats key/value pairs, quotes strings/errors/Stringers/bytes, and fills odd missing values with `[MISSING]`. State is global klog logger configuration only. Dependencies include logr, klog, logrus, fmt, and strings. Risks include global side effects, all verbosity levels enabled, formatting differences from structured logging, and possible sensitive value inclusion. Tests cover info-to-debug conversion, key/value formatting, and missing values.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/klog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/klog_test.go -->
# sources/cloud-native/cri-o/internal/log/klog_test.go

Purpose: verifies klog shim output through the standard logrus logger. Tests initialize debug logging, call `InitKlogShim`, emit `klog.InfoS` messages with no keys, paired keys, and a missing value, then assert output contains the message, debug level, and expected formatted key/value text. State is the shared buffer/standard logger from suite setup and global klog logger configuration. Dependencies include Ginkgo/Gomega, logrus, klog, and CRI-O log package. Risks include global klog state affecting other tests and assertions relying on logrus text formatting. Test signals cover core bridge behavior and missing-value handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/klog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/log.go -->
# sources/cloud-native/cri-o/internal/log/log.go

Purpose: provides CRI-O logging helpers with request context fields and trace span creation. Important APIs are `Tracef`, `Debugf`, `Infof`, `Warnf`, `Errorf`, `Fatalf`, `WithFields`, `StartSpan`, and context key types `ID`/`Name`. Control flow builds a logrus entry from the standard logger; when context contains both ID and Name strings it attaches `id` and `name` fields, otherwise it logs with context only. `StartSpan` names spans from the caller function via `runtime.Caller`. State is not persisted, but output depends on global logrus configuration and context values. Dependencies include logrus, OpenTelemetry trace, runtime, and context. Risks include untyped context keys being package structs, nil context support bypassing fields, global logger reliance, and span name fragility. Tests cover level filtering and context field inclusion for debug/info/warn/error/fatal thresholds.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/log_test.go -->
# sources/cloud-native/cri-o/internal/log/log_test.go

Purpose: verifies CRI-O logging helper functions honor log levels and context fields. It builds contexts with `log.ID{}` and `log.Name{}`, emits messages at multiple logrus levels, and checks buffer content for message/id/name or absence under stricter levels. State is the standard logrus logger redirected to an in-memory buffer per test. Dependencies include context, Ginkgo/Gomega, logrus, and CRI-O log package. Risks include global logger mutation across tests and no assertions for `Tracef`, `WithFields`, or `StartSpan`. Test signals protect basic field attachment, nil/empty context behavior, and logrus level filtering for debug/info/warn/error/fatal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/log_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/suite_test.go -->
# sources/cloud-native/cri-o/internal/log/suite_test.go

Purpose: Ginkgo suite setup for internal log package tests. It registers `TestLog`, creates a CRI-O `TestFramework`, and provides `beforeEach` to reset the standard logrus logger level/output to a fresh buffer. State is package globals `t`, `sut`, and `buf`, with `sut` referencing the standard logger. Dependencies include bytes, testing, Ginkgo/Gomega, logrus, and the CRI-O test framework. Risks include shared global logger side effects between specs and packages. Test signal is foundational for all log tests, ensuring consistent in-memory capture for assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/log/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/history.go -->
# sources/cloud-native/cri-o/internal/memorystore/history.go

Purpose: sortable history slice for objects with creation timestamps. The generic `History[T AnyCreated[T]]` implements `Len`, `Less`, `Swap`, and private `sort`. Control flow delegates to `sort.Sort`; `Less` orders newer `CreatedAt` values before older ones, producing descending creation order. State is the underlying slice being sorted in place. Dependencies are Go `sort` and the package's `AnyCreated` interface. Integration is used by `memoryStore.List` to return stable newest-first lists of sandboxes/containers. Risks include in-place mutation, equal timestamps preserving only sort.Sort's unstable behavior, and relying on `CreatedAt` semantics of stored objects. Tests cover length, less comparisons, and swap behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/history.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/history_test.go -->
# sources/cloud-native/cri-o/internal/memorystore/history_test.go

Purpose: tests the generic `History` sorter with sandbox objects. It creates two sandboxes with distinct creation times through the builder, builds a `History[*sandbox.Sandbox]`, and asserts `Len`, `Less`, and `Swap` behavior. State is in-memory test sandboxes and the mutable history slice. Dependencies include time, Ginkgo/Gomega, CRI API types, hostport, sandbox builder, and memorystore. Risks are timing sensitivity from `time.Now()` and using full sandbox fixtures for a small sorter. Test signals confirm descending creation ordering and slice swap semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/history_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/memory_store.go -->
# sources/cloud-native/cri-o/internal/memorystore/memory_store.go

Purpose: generic concurrent in-memory store for CRI-O objects with `CreatedAt`. Important APIs are `New`, `Add`, `Get`, `Delete`, `List`, `First`, `ApplyAll`, and private `all`; interfaces include `Storer`, `AnyCreated`, `StoreFilter`, and `StoreReducer`. Control flow stores values in `sync.Map`, type-asserts on reads/ranges, lists by collecting all values and sorting via `History`, returns the first matching filter or zero value, and applies reducers concurrently with a wait group. State is process-local only; there is no persistence. Dependencies are sync and time. Risks include nondeterministic `First` order because `sync.Map` range order is undefined, concurrent reducer side effects in `ApplyAll`, silent ignoring of non-typed values, and overwriting IDs on add. Tests cover add/get/delete/list/first/apply behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/memory_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/memory_store_test.go -->
# sources/cloud-native/cri-o/internal/memorystore/memory_store_test.go

Purpose: unit tests for the generic memory store using sandbox values. Tests verify adding and retrieving by ID, missing lookup returning nil, deletion, listing one value, `First` with matching and nonmatching filters, and `ApplyAll` invoking a reducer. State is a fresh store per test plus sandbox fixture from the suite. Dependencies include Ginkgo/Gomega, sandbox type, and memorystore. Risks include single-item cases not testing sort order, duplicate IDs, concurrent access, nil reducers, or reducer race behavior. Test signals protect the core API contract and zero-value missing results.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/memory_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/suite_test.go -->
# sources/cloud-native/cri-o/internal/memorystore/suite_test.go

Purpose: Ginkgo suite setup for memorystore tests. It registers `TestMemoryStore`, initializes a CRI-O `TestFramework`, suppresses logrus output, and defines `beforeEach` to build a valid sandbox fixture through the sandbox builder. State includes package globals `t` and `testSandbox`. Dependencies include testing, time, Ginkgo/Gomega, logrus, CRI API types, hostport, sandbox builder, and test framework. Risks include shared globals and builder fixture verbosity masking store-specific failures. Test signals are indirect: every memorystore test starts with a valid `CreatedAt`-capable sandbox object.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/memorystore/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/mockutils/mockutils.go -->
# sources/cloud-native/cri-o/internal/mockutils/mockutils.go

Purpose: helper for composing nested gomock call order sequences. Important type/API: `MockSequence` stores first/last calls, and `InOrder(calls ...any)` accepts `*gomock.Call` or nested `MockSequence` values. Control flow flattens the input, links each non-empty sequence's first call after the previous last call, fails the current Ginkgo test for invalid argument types, and returns the combined first/last sequence. State is gomock call ordering metadata; no persistence. Dependencies are gomock and Ginkgo failure reporting. Integration lets tests express ordered groups without deeply manual `.After` wiring. Risks include runtime type checking, Ginkgo coupling, nil/empty sequence behavior, and no direct tests in this subset. Test signals are expected through downstream gomock-heavy tests that use nested ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/mockutils/mockutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/container.go -->
# sources/cloud-native/cri-o/internal/nri/container.go

Purpose: CRI-O-side container abstraction and conversion into containerd NRI API objects. Important types are `ContainerStatus`, `Container`, and `LinuxContainer`; functions are `containerToNRI` and `containersToNRI`. Control flow pulls identity, sandbox ID, status, labels, annotations, args/env, mounts, hooks, Linux data, user, rlimits, pid, timestamps, and exit code from the interface and builds `nri.Container` slices. State is not mutated; it is a snapshot conversion. Dependencies include containerd NRI adaptation types and OCI runtime spec. Integration is used by NRI lifecycle requests and plugin sync. Risks include nil status or Linux container implementations causing panics on Linux conversion, loss of `Reason`/`Message` fields because they are not copied, and direct map/slice pointer sharing. Tests are not present in this subset; behavior is integration-tested through NRI lifecycle paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/container_linux.go -->
# sources/cloud-native/cri-o/internal/nri/container_linux.go

Purpose: Linux conversion of CRI-O container Linux details to NRI `LinuxContainer`. The single function `linuxContainerToNRI` reads namespaces, devices, resources, OOM score, cgroups path, IO priority, scheduler, net devices, and RDT info from the `LinuxContainer` interface. State is not changed; returned pointers/slices reference provider data. Dependencies are containerd NRI adaptation types. Integration fills the Linux field in `containerToNRI` for plugin requests. Risks include nil `GetLinuxContainer()` results causing panics, pointer aliasing, and Linux-only fields being unavailable on other platforms. Test signals are absent here; plugin integration should validate conversion completeness.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/container_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/container_other.go -->
# sources/cloud-native/cri-o/internal/nri/container_other.go

Purpose: non-Linux container conversion fallback for NRI. `linuxContainerToNRI` returns nil so `nri.Container.Linux` is unset on non-Linux builds. There is no state, persistence, or external control flow. Dependencies are only NRI adaptation types for the return signature. Risks are plugins expecting Linux data on non-Linux platforms and reduced feature parity. Test signals are compile-time build tag coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/container_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/domain.go -->
# sources/cloud-native/cri-o/internal/nri/domain.go

Purpose: domain bridge between generic NRI adapter code and CRI-O's pod/container implementation. Important APIs are `Domain`, `SetDomain`, `domainTable` methods for listing pods/containers and applying updates/evictions. Control flow stores one registered domain under a mutex, delegates list calls, applies plugin `ContainerUpdate` values while collecting failures unless `IgnoreFailure` is true, and applies evictions collecting all failures. State is global `domains.domain`. Dependencies include NRI adaptation types, logrus, CRI-O contextual logging, and context. Risks include nil domain panic if used before registration, single-domain global replacement, holding the domainTable lock while invoking domain list methods, and partial update failure semantics. Tests are not present here; integration with server domain registration and NRI plugin callbacks is the main signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/domain.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/nri.go -->
# sources/cloud-native/cri-o/internal/nri/nri.go

Purpose: local implementation of CRI-O's NRI API and lifecycle adapter. Important APIs are `New`, `Start`, `Stop`, pod lifecycle methods, container lifecycle/update methods, `syncPlugin`, `updateFromPlugin`, `applyUpdates`, `evictContainers`, and state helpers. Control flow initializes containerd NRI adaptation when enabled, serializes plugin calls under a mutex, builds NRI request objects from CRI-O interfaces, applies plugin-provided updates/evictions through the registered domain, tracks container state (`Created`, `Running`, `Stopped`, `Removed`) to avoid duplicate stop/remove calls, and syncs plugin state from current domains. State includes config, NRI adaptation pointer, and in-memory container state map. Dependencies include CRI-O NRI config, version discovery, containerd NRI adaptation, domain table, log/logrus, and context. Risks include `IsEnabled` only checking config enabled even after `Stop` nils `l.nri`, map state loss across daemon restart, plugin update failures blocking lifecycle, locking during external plugin/domain callbacks, and special handling of the last update in `UpdateContainer` as return resources. No direct tests in this subset; integration tests should cover disabled mode, plugin sync, update/evict failure handling, and duplicate stop/remove suppression.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/nri.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/sandbox.go -->
# sources/cloud-native/cri-o/internal/nri/sandbox.go

Purpose: CRI-O-side pod sandbox abstraction and common conversion to NRI. Important types are `PodSandbox` and `LinuxPodSandbox`; functions are `commonPodSandboxToNRI` and `podSandboxesToNRI`. Control flow snapshots pod ID, name, UID, namespace, labels, annotations, runtime handler, pid, and IPs, while platform-specific files add Linux details. State is not mutated, and maps/slices are passed through as returned by the interface. Dependencies include containerd NRI adaptation types. Integration is used for pod lifecycle requests and plugin synchronization. Risks include nil interface methods or mutable map/slice aliasing, and non-Linux conversion omitting Linux fields. Tests are not present in this subset; lifecycle integration exercises it.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/sandbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/sandbox_linux.go -->
# sources/cloud-native/cri-o/internal/nri/sandbox_linux.go

Purpose: Linux-specific NRI pod sandbox conversion. `podSandboxToNRI` calls `commonPodSandboxToNRI`, reads the pod's `LinuxPodSandbox`, and fills Linux namespaces, pod overhead/resources, cgroup parent, cgroups path, and current resources. It does not mutate state; it returns a snapshot with provider-owned pointers/slices. Dependencies are containerd NRI adaptation types. Integration feeds pod lifecycle and sync requests sent to plugins on Linux. Risks include nil `GetLinuxPodSandbox()` panic, aliasing mutable resource pointers, and plugin compatibility if fields are incomplete. Test signals are integration-level rather than unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/sandbox_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/sandbox_other.go -->
# sources/cloud-native/cri-o/internal/nri/sandbox_other.go

Purpose: non-Linux NRI pod sandbox conversion fallback. `podSandboxToNRI` returns the common pod fields without Linux details. There is no state mutation or persistence. Dependencies are containerd NRI adaptation types. Integration allows NRI code to compile on non-Linux platforms while exposing only portable pod fields. Risks include plugins expecting Linux resources/namespaces and behavior divergence from Linux. Test signals are compile-time build tag coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/nri/sandbox_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/attach.go -->
# sources/cloud-native/cri-o/internal/oci/attach.go

Purpose: demultiplexes conmon attach stream data into stdout and stderr writers. Important constants `AttachPipeStdin`, `AttachPipeStdout`, and `AttachPipeStderr` must stay synchronized with conmon's `stdpipe_t`; the main helper is `redirectResponseToOutputStreams`. Control flow reads chunks into a `conmon.BufSize+1` buffer, uses the first byte as stream selector, writes payload bytes to output or error stream, reports short writes, logs unknown stream types, and exits cleanly on EOF. State is transient buffer and first encountered error. Dependencies include conmon runner config, logrus, and io abstractions. Risks include ignoring stdin selector/unknown types, assuming each read begins with a selector byte for the whole payload, not closing writers, and partial writer behavior. Tests are not in this subset; attach integration should validate stdout/stderr framing, EOF, short writes, and malformed stream tags.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/internal/oci/attach.go -->
