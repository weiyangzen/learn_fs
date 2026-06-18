# subset-b-000174 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/create.go -->
# sources/cloud-native/moby/daemon/create.go

## Purpose
Implements the generic container-create path for the daemon. It validates API create input, merges image defaults, allocates daemon metadata, creates the writable image layer, configures security and networking state, creates volumes, registers the container, records metrics, and emits the create event.

## Important APIs, Types, And Functions
- `createOpts` carries `ContainerCreateConfig`, service-managed state, and builder-specific `ignoreImagesArgsEscaped`.
- `CreateManagedContainer`, `ContainerCreate`, and `ContainerCreateIgnoreImagesArgsEscaped` are thin public entrypoints into `containerCreate`.
- `containerCreate` handles OpenTelemetry span setup, default restart policy normalization, settings/network validation, platform mismatch warnings, and warning response shaping.
- `create` performs the irreversible create sequence: image lookup, config merge, `newContainer`, security options, link registration, OS-specific setup, NRI notification, mount registration, layer creation, directory creation, OS volume setup, daemon registration, metrics, and event emission.
- `generateSecurityOpt`, `mergeAndVerifyConfig`, `validateNetworkingConfig`, and `maximumSpec` are key helpers.

## Control Flow
The create path first rejects nil container config, normalizes empty restart policy to `no`, validates host/container settings, optionally warns if the image platform does not match the host, validates endpoint settings, creates an empty host config if absent, and adapts platform defaults. The lower-level `create` resolves image/platform data, preserves Windows `ArgsEscaped` when needed, merges image config, validates logging, constructs the `container.Container`, and installs a deferred cleanup that force-removes the partially created container on later failure. The successful path sets security, registers links, initializes OS-specific defaults, normalizes network mode, informs NRI, registers mounts, creates the RW layer, creates root/checkpoint directories, creates/populates volumes, registers the container, and logs the create event.

## State And Persistence
State created here includes the in-memory `container.Container`, the container root and checkpoint directories, the writable layer from `imageService.CreateLayer`, mount point metadata, volume references, SELinux labels, NRI container state, container store/index registration, metrics, and event history. Failures after `newContainer` attempt cleanup through `cleanupContainer` with `ForceRemove` and `RemoveVolume` to avoid orphaned partial state.

## Dependencies And Integration Points
Integrates with image service lookup/layer creation, container metadata constructors, host-config validators, libnetwork validation, NRI, volume services, SELinux, user namespace identity mapping, metrics, OpenTelemetry, and event logging. The OS-specific hooks are implemented in `create_unix.go` and `create_windows.go`.

## Risks And Edge Cases
Create has many side effects before final registration, so cleanup quality is critical. Image-platform warning logic only runs when no explicit platform is requested. `labelsAsOTelAttributes` is governed by an experimental environment variable and caches the filter once. SELinux label sharing across `--ipc=container` and `--pid=container` requires labels to match. `mergeAndVerifyConfig` rejects containers with no effective command after image/user config merge.

## Test Signals
This file is indirectly covered by daemon create, config merge, networking, delete cleanup, and platform validation tests. Strong regressions show up as invalid warning/error typing, incomplete cleanup on failed create, missing RW layers, bad network endpoint validation, or create events/metrics not being emitted.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/create_unix.go -->
# sources/cloud-native/moby/daemon/create_unix.go

## Purpose
Provides Unix-specific container create behavior: default masked/readonly Linux paths, initial container mount, working-directory setup, anonymous volume creation, SELinux relabeling, and image-to-volume data population.

## Important APIs, Types, And Functions
- `createContainerOSSpecificSettings` applies default Linux masked and readonly paths for non-privileged containers.
- `createContainerVolumesOS` mounts the container rootfs, creates missing anonymous volumes from image `Config.Volumes`, rejects volume-over-file cases, relabels volume paths, and delegates population.
- `populateVolumes` and `populateVolume` copy initial directory contents from the container image into volume mounts that request copy data.

## Control Flow
The create hook sets OCI default masked/readonly paths only when the host config did not already set them and the container is not privileged. Volume setup mounts the container, defers unmount, creates the working directory with daemon identity mapping, iterates declared image volumes, skips destinations already covered by `--volumes-from`, validates the destination path, creates a daemon volume, relabels it, records the mount point, then copies image contents into eligible named/anonymous volumes.

## State And Persistence
This file mutates `ctr.HostConfig`, `ctr.MountPoints`, the container working directory, volume service metadata, volume backing directories, SELinux labels, and volume contents. Population temporarily sets up and later cleans up each volume mount.

## Dependencies And Integration Points
Uses OCI default spec data, daemon `Mount`/`Unmount`, `container.GetResourcePath`, `volumes.Create`, `volumeopts.WithCreateReference`, SELinux `label.Relabel`, id-mapped mount setup, and `CopyImagePathContent`.

## Risks And Edge Cases
Volume setup depends on a successful temporary rootfs mount. Existing files at image volume destinations are rejected because a directory volume cannot be mounted over a file. Copying ignores missing mount sources but surfaces other mount setup errors. Deferred cleanup uses a context that ignores cancellation to avoid leaking mounted volumes.

## Test Signals
Coverage is mainly integration-level: container create with image-declared volumes, copy-data behavior, SELinux relabeling, working-directory creation, and cleanup after create failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/create_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/create_windows.go -->
# sources/cloud-native/moby/daemon/create_windows.go

## Purpose
Provides Windows-specific container create behavior. It applies the daemon default isolation mode when the caller left isolation unset and creates image-declared volumes without Unix-style rootfs content population.

## Important APIs, Types, And Functions
- `createContainerOSSpecificSettings` fills `HostConfig.Isolation` from `daemon.defaultIsolation`.
- `createContainerVolumesOS` parses raw volume specs with the Windows-aware volume parser, skips already-mounted destinations, creates volumes, and records mount points.

## Control Flow
During create, the OS settings hook normalizes default isolation. Volume setup iterates image `Config.Volumes`, parses each destination, skips `--volumes-from`/existing mounts, creates a volume in the configured driver, and adds it to `ctr.MountPoints`. The commented section explains that copying pre-existing container filesystem content into Windows volumes is intentionally deferred because path-following and HCS behavior do not support that flow.

## State And Persistence
Mutates host config isolation and container mount metadata, and creates persistent volume service records/backing storage. Unlike Unix, it does not mount the rootfs or copy initial data from image paths into volumes.

## Dependencies And Integration Points
Depends on `volume/mounts` parsing, volume service creation, daemon default isolation from `daemon_windows.go`, and the generic create pipeline in `create.go`.

## Risks And Edge Cases
Windows containers built with files under a Dockerfile `VOLUME` destination may not get those contents copied to the volume, and HCS may later reject mapped directories with contents. Incorrect default isolation would affect whether later mount/cleanup paths run on the host or inside a utility VM.

## Test Signals
Signals are mostly Windows integration tests for create/start with process and Hyper-V isolation and image-declared volumes; direct unit tests are absent in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/create_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon.go -->
# sources/cloud-native/moby/daemon/daemon.go

## Purpose
Defines the central `Daemon` object and most cross-platform daemon lifecycle orchestration: configuration snapshots, startup initialization, container load/restore, image and storage setup, network setup handoff, shutdown, mount/unmount wrappers, disk/network helpers, root creation, namespace remapping, and backend accessors.

## Important APIs, Types, And Functions
- `configStore` embeds `config.Config` plus resolved runtime configuration.
- `Daemon` owns container stores, image service, config pointer, volume service, events, libnetwork controller, containerd clients, plugin manager/store, NRI, CDI cache, metrics helpers, singleflight disk-usage groups, and shutdown/startup state.
- `loadContainers` reads container metadata directories concurrently and groups containers by storage driver.
- `restore` registers loaded containers, migrates old metadata, restores containerd tasks, handles live-restore, updates state, initializes networking with active sandboxes, restarts eligible containers, removes auto-remove/dead containers, and prepares mount points.
- `NewDaemon` wires registry, runtime, plugins, seccomp/AppArmor, containerd, image service, layer store or snapshotter, NRI, container stores, network restore, metrics, and startup completion.
- `Shutdown`, `Mount`, `Unmount`, `networkOptions`, `deriveULABaseNetwork`, `CreateDaemonRoot`, `RemapContainerdNamespaces`, `RawSysInfo`, and backend accessors expose daemon lifecycle and subsystem entrypoints.

## Control Flow
Startup validates daemon settings, resolves temp/root/user namespace paths, loads runtimes, initializes plugin management before restore, configures logging and volumes, verifies Linux devices cgroup when required, loads persisted containers, initializes NRI, selects graphdriver or containerd snapshotter image service, creates libcontainerd, restores containers for the active driver, closes `startupDone`, emits system warnings and engine metrics, then returns the ready daemon. Restore itself is multi-phase: load/register containers, migrate and checkpoint config, reconcile real containerd task state, initialize network controller with active sandboxes, register legacy links, restart containers with dependencies, auto-remove eligible containers, then prepare mount points.

## State And Persistence
This file manages persistent daemon root layout, `containers/` metadata, image stores under graphdriver or containerd, reference stores, distribution metadata, identity caches, plugin roots, tmp directories, policy verifier state, container checkpoint saves, network state, metrics, and event service lifetime. It also preserves daemon ID through `LoadOrCreateID` and may migrate image metadata from graphdriver to containerd snapshotter.

## Dependencies And Integration Points
It integrates with containerd, graphdriver/layer store, snapshotter service, image service, libcontainerd, libnetwork, plugin manager/executor, volume service, registry service, NRI, CDI, stats, OpenTelemetry/grpc interceptors, BuildKit/distribution backends, policy verifier, sysinfo, SELinux, AppArmor/seccomp platform hooks, and OS-specific helpers from Unix/Linux/Windows files.

## Risks And Edge Cases
Initialization order is delicate: plugins must exist before restore, networking waits for active sandbox discovery, and shutdown must stop containers/layers before plugins. Restore tolerates missing RW layers so users can remove broken containers. Live-restore intentionally preserves running containers and active sandboxes, but network config changes do not apply while active sandboxes exist. Snapshotter migration only occurs under strict no-container/size conditions. `prepareTempDir` asynchronously deletes old temp data. `Mount` treats inconsistent mount paths as fatal except on Windows.

## Test Signals
`daemon_test.go` covers container lookup/name ambiguity, config merge, invalid isolation, invalid port zero, network error typing, deterministic ULA derivation, and symlinked root resolution. Startup and restore are primarily integration-tested because they require containerd, graphdriver, networking, and plugin dependencies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_linux.go -->
# sources/cloud-native/moby/daemon/daemon_linux.go

## Purpose
Implements Linux-only daemon helpers for plugin exec-root selection, stale mount cleanup, `resolv.conf` defaulting, interface address lookup, recursive read-only mount support detection, and rootless network namespace execution.

## Important APIs, Types, And Functions
- `getPluginExecRoot` returns `/run/docker/plugins` to avoid Unix socket path-length issues.
- `cleanupMountsByID`, `cleanupMountsFromReaderByID`, `cleanupMounts`, `getCleanPatterns`, and `shouldUnmountRoot` remove stale container and daemon-root mounts.
- `setupResolvConf` selects the libnetwork-aware resolver path when unset.
- `ifaceAddrs` reads addresses from a named link through libnetwork netlink handles.
- `kernelSupportsRecursivelyReadOnly` and `supportsRecursivelyReadOnly` validate kernel and OCI runtime support for recursive read-only mounts.
- `runInNetNS` executes a function inside RootlessKit's detached network namespace when present.

## Control Flow
Mount cleanup scans `/proc/self/mountinfo`, limits matches to `daemon.root`, matches known container mount patterns or a specific mount ID, and calls an injected unmount function. General cleanup also conditionally unmounts the daemon root if it was made shared by daemon startup and the unmount marker exists. Recursive read-only support probes by mounting a temporary tmpfs and calling `mount_setattr` with `AT_RECURSIVE`, caching the result once.

## State And Persistence
Can unmount container shm/rootfs mounts and the daemon root bind mount, and removes the `unmount-on-shutdown` marker written by Unix root propagation setup. RRO probing creates and unmounts a temporary mount. Resolver setup mutates daemon config.

## Dependencies And Integration Points
Uses `/proc/self/mountinfo`, `moby/sys/mount`, `mountinfo`, libnetwork `resolvconf`, RootlessKit helpers, vishvananda netlink, OCI runtime feature metadata from `configStore.Runtimes`, and Linux `mount_setattr`.

## Risks And Edge Cases
Regex-based cleanup must avoid unmounting unrelated paths, so it checks the daemon root prefix. Root cleanup only unmounts shared root mounts with a marker. RRO support can fail because of older kernels, missing permissions, or runtime feature absence. Rootless netns execution depends on RootlessKit exposing a detached namespace path.

## Test Signals
`daemon_linux_test.go` uses mountinfo fixtures to ensure only expected shm/rootfs mounts are cleaned, validates Linux rejection of Hyper-V isolation, verifies daemon-root unmount marker behavior, and tests `ifaceAddrs` in an isolated network namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_linux_test.go -->
# sources/cloud-native/moby/daemon/daemon_linux_test.go

## Purpose
Tests Linux-specific mount cleanup, root propagation cleanup, interface address discovery, and Linux isolation validation.

## Important APIs, Types, And Functions
- `mountsFixture` and `mountsFixtureOverlay2` simulate `/proc/self/mountinfo` for aufs and overlay2 cases.
- `TestCleanupMounts`, `TestCleanupMountsByID`, and `TestNotCleanupMounts` validate cleanup filtering.
- `TestValidateContainerIsolationLinux` checks Hyper-V isolation rejection on Linux.
- `TestShouldUnmountRoot` exercises root unmount eligibility.
- `TestRootMountCleanup` exercises real mount propagation and cleanup as root.
- `TestIfaceAddrs` and `createBridge` verify netlink address lookup.

## Control Flow
The tests inject fake unmount callbacks into `cleanupMountsFromReaderByID` to count target matches, table-drive `shouldUnmountRoot`, and use temporary mountpoints for root propagation cleanup. Network tests create a bridge in a test OS namespace and compare returned IPv4/IPv6 addresses.

## State And Persistence
Most tests are in-memory fixture driven. Root and netlink tests create temporary directories, mounts, and bridge interfaces, with cleanup deferred by the test harness. Root-only tests skip when not privileged.

## Dependencies And Integration Points
Depends on Linux mount APIs, mountinfo parsing, netlink, test namespace helpers, container isolation validation, and daemon config root/exec-root marker conventions.

## Risks And Edge Cases
Root-required tests may be skipped in unprivileged CI, leaving propagation behavior less covered. Fixture-based cleanup tests are precise for known mount formats but may miss future mount path patterns.

## Test Signals
Failures indicate over-broad or under-broad stale mount cleanup, incorrect daemon-root unmount decisions, Linux accepting unsupported isolation, or broken netlink address enumeration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_test.go -->
# sources/cloud-native/moby/daemon/daemon_test.go

## Purpose
Provides cross-platform unit coverage for daemon helpers: container lookup, valid name patterns, loading old DNS config, image/user config merge, isolation and port validation, network error typing, ULA derivation, and symlinked directory resolution.

## Important APIs, Types, And Functions
- `TestGetContainer` validates lookup precedence between full IDs, partial IDs, full names, ambiguous prefixes, and missing values.
- `initDaemonWithVolumeStore` creates a minimal daemon with a volume service.
- `TestContainerInitDNS` loads old JSON metadata and ensures DNS slices are initialized.
- `TestMerge` verifies image config merge semantics for ports, env, and volumes.
- `TestValidateContainerIsolation`, `TestInvalidContainerPort0`, and `TestFindNetworkErrorType` validate API-facing errors.
- `TestDeriveULABaseNetwork` checks deterministic RFC4193-style ULA prefix derivation.
- Symlink tests validate `resolveSymlinkedDirectory`.

## Control Flow
Tests construct minimal container stores and view DBs, reserve names, call daemon helpers, and assert exact results or error categories. Filesystem tests create temporary config files or symlinks and then invoke loader/path resolution code.

## State And Persistence
Temporary directories hold container metadata and symlink targets. In-memory stores simulate daemon state. Root-required DNS loading test may mutate file ownership and skips without root.

## Dependencies And Integration Points
Exercises container memory store, container view DB, volume service, network/libnetwork errors, config merge logic from image metadata, and host filesystem symlink behavior.

## Risks And Edge Cases
Some tests skip or need porting on Windows. The old JSON fixture covers migration shape for one legacy container but cannot cover all historical metadata variants.

## Test Signals
Failures flag user-visible regressions in `docker inspect`/lookup behavior, name validation, config inheritance, invalid API error typing, network router expectations, or root directory canonicalization.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_unix.go -->
# sources/cloud-native/moby/daemon/daemon_unix.go

## Purpose
Implements Linux/FreeBSD daemon platform behavior: OCI Linux resource translation, security option parsing, resource and daemon setting validation, cgroup driver selection, systemd detection, networking/default bridge setup, user namespace remapping, daemon root permissions/propagation, legacy link registration, seccomp profile loading, cgroup realtime initialization, sysinfo collection, and recursive unmount.

## Important APIs, Types, And Functions
- `getMemoryResources`, `getPidsLimit`, `getCPUResources`, `getBlkioWeightDevices`, and `getBlkioThrottleDevices` translate Docker resources into OCI Linux structures.
- `parseSecurityOpt` handles AppArmor, seccomp, SELinux label options, no-new-privileges, and writable cgroups.
- `adjustParallelLimit` caps startup concurrency based on `RLIMIT_NOFILE`.
- `adaptContainerSettings` fills memory swap, shm, IPC/cgroup namespace defaults, shared namespace IDs, generated SELinux labels, and OOM defaults.
- `verifyPlatformContainerResources`, `verifyPlatformContainerSettings`, and `verifyDaemonSettings` validate kernel capability-dependent settings.
- `cgroupDriver`, `verifyCgroupDriver`, `UsingSystemd`, and `isRunningSystemd` select cgroup integration.
- `initNetworkController`, `configureNetworking`, `initBridgeDriver`, `getDefaultBridgeIPAMConf`, and `selectBIP` initialize libnetwork and default bridge IPAM.
- `parseRemappedRoot`, `setupRemappedRoot`, `setupDaemonRoot`, and `setupDaemonRootPropagation` configure user namespace and root filesystem access.

## Control Flow
Container create/update validation starts by collecting cached sysinfo and then mutates unsupported resource fields into warnings or rejects conflicting/invalid settings. Daemon startup validates bridge/cgroup config, sets thread limits, optionally validates SELinux overlay support, creates libnetwork with active sandbox awareness, creates predefined `none`/`host` networks, deletes stale default bridge state, and builds or removes `docker0` according to config. Default bridge IPAM chooses configured BIP, existing bridge addresses, or fixed CIDR rules while preserving compatibility with older permissive configurations. User namespace setup resolves names/IDs, may create the `dockremap` user for `default`, loads subuid/subgid ranges, and changes daemon root to a remapped subtree.

## State And Persistence
Mutates `HostConfig` resource and namespace fields, daemon config network/root fields, cgroup files for realtime settings, seccomp profile bytes/path, SELinux global state, `/etc/passwd`/group namespace user entries for default remap, daemon root directories and permissions, an `unmount-on-shutdown` marker, libnetwork persistent networks, and legacy link name reservations.

## Dependencies And Integration Points
Uses containerd cgroup mode, sysinfo, SELinux/AppArmor/seccomp support, libnetwork bridge/null/host drivers, netlink, mount propagation helpers, user/group lookup and subid loading, OCI runtime specs, daemon config/runtime store, and container/link stores.

## Risks And Edge Cases
Many validation paths intentionally mutate the input host config by discarding unsupported fields with warnings. Systemd cgroup defaults depend on cgroup v2 and `/run/systemd/system`. User-managed bridge IPAM preserves backward compatibility by logging some IPv4 fixed-CIDR problems instead of failing startup. Root propagation setup writes a marker only when daemon root must be unmounted later. Shared namespace names are converted to IDs only if the target resolves at create time.

## Test Signals
`daemon_unix_test.go` covers namespace name-to-ID adaptation, security option parsing, no-new-privileges override behavior, OOM/memory warnings, and blkio device major/minor extraction. Linux tests cover root propagation and bridge address helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_unix_test.go -->
# sources/cloud-native/moby/daemon/daemon_unix_test.go

## Purpose
Tests Unix-specific validation and translation helpers for shared namespaces, security options, Linux resource warnings, and blkio device conversion.

## Important APIs, Types, And Functions
- `fakeContainerGetter` supports namespace adaptation tests.
- `TestAdjustSharedNamespaceContainerName` verifies `container:name` modes become `container:ID`.
- `TestParseSecurityOptWithDeprecatedColon`, `TestParseSecurityOpt`, and `TestParseNNPSecurityOptions` cover AppArmor, seccomp, labels, no-new-privileges, writable cgroups, deprecated colon syntax, and invalid option errors.
- `TestVerifyPlatformContainerResources` checks OOM/memory warning behavior.
- `deviceTypeMock`, `TestGetBlkioWeightDevices`, and `TestGetBlkioThrottleDevices` validate device major/minor extraction.

## Control Flow
Tests build synthetic host configs and sysinfo structs, call the relevant helper directly, and assert exact error strings, flags, warnings, and generated OCI device structures. Device tests create a character device with a known major/minor when running as root.

## State And Persistence
Most state is in-memory. Device tests create a temporary directory and `mknod` device, then remove it. SELinux-dependent assertions are softened because labels depend on host state.

## Dependencies And Integration Points
Depends on Unix build tags, SELinux package behavior, Linux `mknod` for device tests, sysinfo capability fields, daemon config store, and container security option structs.

## Risks And Edge Cases
Root-required device tests skip in unprivileged environments. Security label assertions are limited when SELinux is enabled, leaving exact label generation to integration coverage.

## Test Signals
Failures identify regressions in user-facing `--security-opt` parsing, daemon default no-new-privileges precedence, warning/discard behavior for unsupported resource controls, and blkio device mapping into OCI specs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_unsupported.go -->
# sources/cloud-native/moby/daemon/daemon_unsupported.go

## Purpose
Provides stub daemon platform hooks for unsupported build targets outside Linux, FreeBSD, and Windows so the package can compile with minimal behavior.

## Important APIs, Types, And Functions
- `checkSystem` returns nil.
- `setupResolvConf` is a no-op.
- `getSysInfo` returns a generic `sysinfo.New()`.
- `runInNetNS` executes the callback directly.

## Control Flow
There is no platform setup logic; each function either returns a neutral value or calls the provided callback.

## State And Persistence
No persistent state is created or mutated.

## Dependencies And Integration Points
Build tags select this file only for unsupported platforms. It satisfies symbols required by generic daemon code.

## Risks And Edge Cases
Returning nil from `checkSystem` can hide missing real platform support if an unsupported target is accidentally built. Generic sysinfo may not describe platform-specific capabilities.

## Test Signals
The main signal is package compilation on unsupported targets; there are no direct unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_windows.go -->
# sources/cloud-native/moby/daemon/daemon_windows.go

## Purpose
Implements Windows daemon platform behavior: startup parallelism, plugin exec-root, resource validation, system requirement checks, Windows network/HNS reconciliation, root ACL setup, Hyper-V/process isolation decisions, and no-op substitutions for Unix-only features.

## Important APIs, Types, And Functions
- `adjustParallelLimit` limits startup parallelism to about 80% of CPUs because Windows containers are process-heavy.
- `verifyPlatformContainerResources` validates Windows-supported CPU/memory/resource fields and discards mutually exclusive CPU controls for process-isolated containers.
- `checkSystem` validates Windows build level, `vmcompute.dll`, and required services.
- `ensureServicesInstalled` verifies named Windows services through the service manager.
- `initNetworkController` reconciles libnetwork state with HNS networks, adopts host networks, recreates missing NAT networks, creates `none`, and initializes the default NAT network.
- `runAsHyperVContainer`, `conditionalMountOnStart`, `conditionalUnmountOnCleanup`, and `setDefaultIsolation` implement isolation-specific behavior.

## Control Flow
Startup validates the OS and services, initializes libnetwork, lists HNS networks, deletes or recreates libnetwork entries missing from HNS, adopts supported HNS networks into Docker with HNS IDs, creates the `none` network, and ensures the default NAT network exists unless bridge networking is disabled. Resource validation rejects Linux-only fields and resolves CPUCount/CPUShares/CPUPercent precedence for process isolation. Default isolation is Hyper-V on client SKUs unless overridden by `exec-opt isolation`, otherwise process.

## State And Persistence
Mutates host config resource fields during validation, daemon `defaultIsolation`, daemon root ACLs, libnetwork persistent state, HNS-backed network records, and container mount state for process-isolated containers. Unix-only features such as SELinux, seccomp, root remapping, mount cleanup, recursive unmount, and network namespace execution are no-ops.

## Dependencies And Integration Points
Uses hcsshim/HNS, Windows OS version APIs, service manager APIs, Windows libnetwork driver options, daemon config, system ACL helpers, container isolation types, and the generic daemon create/start/shutdown paths.

## Risks And Edge Cases
HNS/libnetwork reconciliation must avoid deleting global networks and must preserve labels/options when recreating NAT networks. Adopted HNS networks are marked as host-owned to avoid prune deleting them. Windows resource validation intentionally differs between process and Hyper-V isolation. Service checks require permissions to access the SCM.

## Test Signals
`daemon_windows_test.go` validates service discovery success and first-error behavior. Broader network reconciliation and isolation behavior require Windows integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_windows_test.go -->
# sources/cloud-native/moby/daemon/daemon_windows_test.go

## Purpose
Tests Windows service detection used by daemon system checks.

## Important APIs, Types, And Functions
- `existingService` is the known inbox service `Power`.
- `TestEnsureServicesExist` expects `ensureServicesInstalled` to succeed for the known service.
- `TestEnsureServicesExistErrors` verifies errors for one or more fake service names.

## Control Flow
Each test connects to the Windows service manager, verifies the known service is present, then calls `ensureServicesInstalled` with success and failure inputs. Error tests assert the message names the first missing service encountered.

## State And Persistence
No persistent state is changed; tests only open and close SCM service handles.

## Dependencies And Integration Points
Requires Windows, access to the service manager, and a stable inbox `Power` service. It directly covers `checkSystem`'s service validation helper.

## Risks And Edge Cases
Tests may fail or skip operationally if the process lacks rights to the service manager or if the known service is unavailable on a target image.

## Test Signals
Failures indicate daemon startup may misreport missing Windows container prerequisites or not preserve useful service names in errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/daemon_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/debugtrap_unix.go -->
# sources/cloud-native/moby/daemon/debugtrap_unix.go

## Purpose
Installs a Unix SIGUSR1 trap that writes goroutine stack dumps to the daemon root/exec-root area.

## Important APIs, Types, And Functions
- `setupDumpStackTrap` creates a signal channel, registers `syscall.SIGUSR1`, and starts a goroutine.
- The goroutine calls `stackdump.DumpToFile(root)` for each signal.

## Control Flow
Daemon startup calls this once with the selected stack-dump directory. The goroutine blocks on the signal channel and logs any dump failure.

## State And Persistence
Persists stack dump files in the provided root directory when SIGUSR1 is received. It also installs process-level signal notification.

## Dependencies And Integration Points
Uses Go `os/signal`, Unix `syscall.SIGUSR1`, containerd logging, and Moby stackdump utility. Called from `NewDaemon`.

## Risks And Edge Cases
If the dump directory is unwritable, signal handling remains installed but dumps log errors. Signal behavior is Unix-specific and absent on unsupported targets.

## Test Signals
No direct unit tests; operational signal is successful stack dump creation after SIGUSR1.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/debugtrap_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/debugtrap_unsupported.go -->
# sources/cloud-native/moby/daemon/debugtrap_unsupported.go

## Purpose
Provides a no-op stack dump trap for build targets that are neither Unix-like nor Windows.

## Important APIs, Types, And Functions
- `setupDumpStackTrap` accepts the root path and does nothing.

## Control Flow
No control flow beyond returning immediately.

## State And Persistence
No signal handlers, events, or dump files are created.

## Dependencies And Integration Points
Selected by build tags for unsupported targets to satisfy generic daemon startup symbols.

## Risks And Edge Cases
Operators on unsupported platforms do not get a stack-dump trigger, but this is consistent with the platform support boundary.

## Test Signals
Compilation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/debugtrap_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/debugtrap_windows.go -->
# sources/cloud-native/moby/daemon/debugtrap_windows.go

## Purpose
Installs a Windows global named event listener that writes goroutine stack dumps when signaled.

## Important APIs, Types, And Functions
- `setupDumpStackTrap` builds the `Global\docker-daemon-<pid>` event name, creates the event, sets a finalizer to close the handle, and starts a wait goroutine.
- The goroutine calls `windows.WaitForSingleObject` and `stackdump.DumpToFile(root)`.

## Control Flow
On startup, the daemon creates a global event and waits forever. Each successful wait triggers a stack dump and then continues waiting. Errors creating the event or dumping stacks are logged.

## State And Persistence
Creates a Windows kernel event handle and writes dump files under the provided root when the event is set. The handle is closed by finalizer when the wrapper is collected.

## Dependencies And Integration Points
Uses Windows syscall APIs, process ID naming conventions, containerd logging, and Moby stackdump. The event is meant for external Windows diagnostic tooling to trigger.

## Risks And Edge Cases
Global event creation can fail due to permissions or namespace restrictions. The finalizer-based close is best-effort; the listener goroutine is process-lifetime.

## Test Signals
No direct unit tests; manual/integration validation is creating/signaling the named event and observing a dump file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/debugtrap_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/delete.go -->
# sources/cloud-native/moby/daemon/delete.go

## Purpose
Implements container removal and cleanup, including force handling, link removal, stats stop, graceful stop, RW layer release, filesystem removal, mount/volume cleanup, name release, metrics, and destroy event emission.

## Important APIs, Types, And Functions
- `ContainerRm` is the public entrypoint.
- `containerRm` resolves the container, serializes deletion with `RemovalInProgress`, handles link-only removal, and records delete metrics.
- `rmLink` removes a legacy link name from the parent container and updates networking.
- `cleanupContainer` performs running-container checks, stop/kill, dead-state checkpoint, layer release, root deletion, link index deletion, SELinux release, store removal, mount-point removal, state/metrics cleanup, and destroy event logging.

## Control Flow
Removal first marks `RemovalInProgress` atomically to avoid duplicate deletes. Non-force removal rejects running, paused, or restarting containers with conflict errors. Force removal kills running containers if necessary, stops stats, attempts a short graceful stop, marks the container dead and checkpoints it, releases the RW layer, removes the container root under lock, deletes link/name/store state, removes volumes if requested, and marks the state removed.

## State And Persistence
Mutates container state flags, checkpoint files, layer store references, container root directory, link index, name reservations, SELinux label reservations, in-memory and view DB stores, mount points/volumes, metrics, and event history.

## Dependencies And Integration Points
Depends on container state, daemon kill/stop paths, stats collector, image service layer release, `containerfs.EnsureRemoveAll`, SELinux, mount-point removal, network link update, metrics, and event logging.

## Risks And Edge Cases
The removal lock prevents duplicate deletes but returns conflict while removal is active. If layer release fails, the RW layer reference is restored and the removal error is stored. Windows filesystem deletion requires holding the container lock to avoid open-file races. Link-only removal rejects default link names.

## Test Signals
`delete_test.go` verifies useful conflict messages for paused/restarting/running containers and duplicate removal detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/delete_test.go -->
# sources/cloud-native/moby/daemon/delete_test.go

## Purpose
Tests user-facing container removal conflict behavior and duplicate delete protection.

## Important APIs, Types, And Functions
- `newDaemonWithTmpRoot` builds a minimal daemon with temp root and memory store.
- `newContainerWithState` creates a test container with a given state.
- `TestContainerDelete` table-tests paused, restarting, and running container removal without force.
- `TestContainerDoubleDelete` checks `RemovalInProgress` handling.

## Control Flow
Tests add synthetic containers to a minimal daemon and call `ContainerRm` with force disabled or enabled. They assert conflict error typing and exact useful error-message fragments.

## State And Persistence
Creates temporary daemon roots and in-memory containers only. No real layer store or volume state is required because tests stop at pre-cleanup conflict paths.

## Dependencies And Integration Points
Covers `delete.go`, container state transitions, containerd error classification, and backend removal config.

## Risks And Edge Cases
Because cleanup is not fully exercised, layer release, root deletion, volume removal, and event emission still rely on broader integration coverage.

## Test Signals
Failures indicate degraded CLI/API feedback for common `docker rm` mistakes or a race guard regression for duplicate removal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/dependency.go -->
# sources/cloud-native/moby/daemon/dependency.go

## Purpose
Exposes a small adapter for dependency-aware exec/start logic by binding a named dependency store into the daemon's container store.

## Important APIs, Types, And Functions
- `SetContainerDependencyStore(name string, store exec.DependencyGetter) error` delegates to `daemon.containers.SetDependencyStore`.

## Control Flow
The function performs no validation itself; it forwards the name and store to the underlying container memory store.

## State And Persistence
Mutates in-memory container store dependency tracking. No on-disk persistence is performed here.

## Dependencies And Integration Points
Integrates the daemon package with `daemon/cluster/executor/container` dependency getter interfaces and container store dependency support.

## Risks And Edge Cases
Errors are entirely determined by the store implementation. A nil or incorrectly named store could affect dependent-container ordering if not rejected downstream.

## Test Signals
No direct tests in this subset; integration signals are dependency-aware start/restart behavior and store-level tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/dependency.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices.go -->
# sources/cloud-native/moby/daemon/devices.go

## Purpose
Defines the daemon's pluggable device request registry and generic device selection logic, primarily used for GPU requests.

## Important APIs, Types, And Functions
- `deviceDrivers` is the process-global registry by driver name.
- `deviceDriver` holds a capability set, an OCI spec updater, and optional device listing function.
- `deviceInstance` pairs a Docker `DeviceRequest` with selected capabilities.
- `registerDeviceDriver` inserts a driver.
- `getFirstAvailableVendor` chooses the first known GPU vendor in NVIDIA-then-AMD priority.
- `Daemon.handleDevice` selects a driver by capability match or explicit driver name and invokes its `updateSpec`.

## Control Flow
For requests without an explicit driver, `handleDevice` scans registered drivers for a matching capability set and uses the first match. For explicit drivers, it uses the named driver if registered and logs that capabilities may be ignored. If no suitable driver exists, it returns `incompatibleDeviceRequest`.

## State And Persistence
Device driver registration is global in process memory. `handleDevice` mutates the supplied OCI spec through the selected driver's updater but writes no daemon metadata itself.

## Dependencies And Integration Points
Integrates Docker API device requests, internal capability matching, OCI runtime specs, GPU registration from platform files, and error typing in `errors.go`.

## Risks And Edge Cases
Map iteration order can affect implicit driver selection when multiple registered drivers match the same capability set, though current Linux registration returns after registering one vendor family. Explicit driver requests bypass strict capability validation by design.

## Test Signals
`devices_test.go` covers vendor selection priority and error cases. Device spec mutation is covered by GPU-specific tests/integration outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_amd_linux.go -->
# sources/cloud-native/moby/daemon/devices_amd_linux.go

## Purpose
Implements Linux AMD GPU device request support through CDI when available or the legacy `amd-container-runtime` environment variable path.

## Important APIs, Types, And Functions
- `setAMDGPUs` sets `AMD_VISIBLE_DEVICES` from `DeviceIDs`, `Count`, all devices, or `void`.
- `createAMDCDIUpdater` discovers CDI vendors and injects normalized `amd.com/gpu` CDI device names.
- `getAMDDeviceDrivers` builds a composite updater from CDI and/or `amd-container-runtime`.

## Control Flow
AMD driver setup adds a CDI updater if a CDI cache exists, adds a runtime-env updater if the helper binary is on `PATH`, and returns nil if neither path is available. At runtime, the composite updater tries CDI first, then environment injection. `setAMDGPUs` rejects simultaneous `Count` and `DeviceIDs`.

## State And Persistence
Mutates only the OCI spec process environment or CDI device annotations through the delegated CDI updater. No daemon persistent state is written.

## Dependencies And Integration Points
Uses CDI cache vendor discovery, shared `cdiDeviceInjector` from NVIDIA support, the global device driver registry, and external `amd-container-runtime` discovery through `exec.LookPath`.

## Risks And Edge Cases
CDI vendor discovery must find `amd.com`; otherwise CDI update fails and the composite may fall back to env injection. A request with `Count == 0` produces `AMD_VISIBLE_DEVICES=void`, which is a meaningful legacy-runtime behavior but differs from NVIDIA's no-op for zero.

## Test Signals
Direct tests cover vendor priority through `getFirstAvailableVendor`. Full AMD behavior depends on CDI specs or helper binary integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_amd_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_linux.go -->
# sources/cloud-native/moby/daemon/devices_linux.go

## Purpose
Registers Linux GPU device drivers at daemon startup.

## Important APIs, Types, And Functions
- `RegisterGPUDeviceDrivers(cdiCache *cdi.Cache)` registers NVIDIA drivers if available, otherwise AMD if available.

## Control Flow
The function first calls `getNVIDIADeviceDrivers`; if any NVIDIA path is available it registers all returned NVIDIA drivers and returns. If NVIDIA is unavailable, it calls `getAMDDeviceDrivers` and registers the AMD driver if present.

## State And Persistence
Mutates the global in-memory `deviceDrivers` registry. No on-disk state is written.

## Dependencies And Integration Points
Depends on NVIDIA/AMD helper discovery and optional CDI cache. It is the platform entrypoint used by daemon initialization or device subsystem setup.

## Risks And Edge Cases
NVIDIA registration takes priority over AMD and returns early, so mixed-vendor hosts may not register AMD through this path. This prioritization mirrors `getFirstAvailableVendor` but can be limiting for heterogeneous GPU nodes.

## Test Signals
Vendor priority is indirectly tested in `devices_test.go`; full registration depends on helper binaries/CDI specs in integration environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_nonlinux.go -->
# sources/cloud-native/moby/daemon/devices_nonlinux.go

## Purpose
Provides a no-op GPU device registration function on non-Linux platforms.

## Important APIs, Types, And Functions
- `RegisterGPUDeviceDrivers(_ *cdi.Cache)` intentionally does nothing.

## Control Flow
Returns immediately.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Selected by `!linux` build tag while preserving the same public function name for generic callers.

## Risks And Edge Cases
GPU device requests on non-Linux cannot be satisfied by this registration path and will fall through to incompatible device errors.

## Test Signals
Compilation on non-Linux platforms and API behavior for unsupported device requests are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_nonlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_nvidia_linux.go -->
# sources/cloud-native/moby/daemon/devices_nvidia_linux.go

## Purpose
Implements Linux NVIDIA GPU device request support through the NVIDIA CDI hook and/or legacy `nvidia-container-runtime-hook`.

## Important APIs, Types, And Functions
- `getNVIDIADeviceDrivers` discovers helper binaries and returns driver entries for `nvidia.cdi`, `nvidia.runtime-hook`, and composite `nvidia`.
- `firstSuccessfulUpdater` tries multiple OCI spec updaters and returns on the first success.
- `injectNVIDIARuntimeHook` sets `NVIDIA_VISIBLE_DEVICES`, optional `NVIDIA_DRIVER_CAPABILITIES`, and appends a prestart hook.
- `getRequestedDevicesIDs` converts `DeviceRequest` count/IDs into device names.
- `countToDevices` creates numeric IDs.
- `cdiDeviceInjector.injectDevices` and `normalizeDeviceID` map Docker device IDs into fully qualified CDI names.

## Control Flow
Discovery registers CDI support if `nvidia-cdi-hook` exists and runtime-hook support if `nvidia-container-runtime-hook` exists. The composite `nvidia` driver advertises GPU/NVIDIA capabilities and tries the available updaters in order. Runtime-hook injection rejects `Count` plus `DeviceIDs`, treats negative count as `all`, zero count as no devices, appends environment variables, resolves the hook path, and adds a prestart hook. CDI injection normalizes IDs and delegates to the generic `cdi` device driver.

## State And Persistence
Mutates the OCI spec process environment and hooks, or CDI device requests through the CDI driver. It reads process environment for hook env passthrough but writes no daemon metadata.

## Dependencies And Integration Points
Depends on helper binaries on `PATH`, CDI device driver registration, Docker `DeviceRequest`, OCI runtime specs, internal capabilities, and shared error types. The prestart hook is deprecated in OCI but retained for compatibility.

## Risks And Edge Cases
Using deprecated prestart hooks may need future replacement. If CDI injection is selected but the generic CDI driver is not registered, the request fails. `Count == 0` returns no devices for NVIDIA while AMD's legacy path sets `void`. Simultaneous `Count` and `DeviceIDs` is rejected.

## Test Signals
Direct unit tests are absent here; expected signals are GPU integration tests verifying environment variables, CDI device injection, hook presence, and conflict errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_nvidia_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_test.go -->
# sources/cloud-native/moby/daemon/devices_test.go

## Purpose
Tests GPU vendor selection priority and error handling.

## Important APIs, Types, And Functions
- `TestGetFirstAvailableVendor` table-tests NVIDIA, AMD, nil vendor list, unknown vendors, and mixed vendor input.

## Control Flow
The test calls `getFirstAvailableVendor` for each vendor slice and asserts either the selected vendor or exact error string.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Covers `devices.go` and supports AMD CDI discovery logic that needs a known vendor from a CDI cache.

## Risks And Edge Cases
It does not test global driver registration or OCI spec mutation. Mixed-vendor expected result documents NVIDIA priority.

## Test Signals
Failures indicate changed vendor priority or incompatible error behavior for empty/unknown CDI vendor lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/devices_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/disk_usage.go -->
# sources/cloud-native/moby/daemon/disk_usage.go

## Purpose
Computes daemon disk usage summaries for containers, images, and local volumes, with singleflight de-duplication and parallel aggregation for API callers such as `docker system df`.

## Important APIs, Types, And Functions
- `containerDiskUsage` lists all containers with size and computes total, active, and reclaimable RW size.
- `imageDiskUsage` lists images with shared size, computes total layer usage through `imageService.ImageDiskUsage`, and derives reclaimable image bytes.
- `localVolumesSize` calls the volume service and computes total, active, and reclaimable local volume size.
- `SystemDiskUsage` runs requested categories in an `errgroup`.

## Control Flow
Each category uses a daemon-level `singleflight.Group` keyed by verbosity or unit key so concurrent identical calculations share one result. `SystemDiskUsage` starts goroutines for selected categories, waits for all, and returns the assembled `backend.DiskUsage` or the first error.

## State And Persistence
Does not persist new state. It reads container/image/volume metadata and size data. It strips image manifest descriptors from verbose container results before returning so they are not included in disk usage payloads.

## Dependencies And Integration Points
Uses daemon container listing, image backend list and layer disk usage, volume service `LocalVolumesSize`, filters, backend disk usage API structs, and `errgroup`.

## Risks And Edge Cases
Shared singleflight results must not be mutated by callers; the public comment warns against mutating returned fields. Images with unknown container counts are treated as active to avoid over-reporting reclaimable space. Volume sizes of `-1` are excluded from totals.

## Test Signals
No direct tests in this subset. Integration signals include correct `system df` totals, verbose item inclusion, reclaimable calculations, and no duplicate expensive size scans under concurrent requests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/disk_usage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/errors.go -->
# sources/cloud-native/moby/daemon/errors.go

## Purpose
Centralizes daemon error types and container-start exit-code mapping so API routers and clients receive correct conflict/not-found/invalid/unknown classifications and CLI-compatible exit statuses.

## Important APIs, Types, And Functions
- `containerNotRunningError`, `objNotFoundError`, `nameConflictError`, `invalidIdentifier`, `incompatibleDeviceRequest`, `duplicateMountPointError`, `containerFileNotFound`, and `startInvalidConfigError` implement errdefs marker interfaces.
- `errNotRunning`, `containerNotFound`, `errContainerIsRestarting`, `errExecNotFound`, and `errExecPaused` build common errors.
- `setExitCodeFromError` maps containerd start errors to 126, 127, or 128 and wraps them as invalid config or unknown errors.
- `isInvalidCommand` recognizes common executable-not-found messages.

## Control Flow
Marker methods such as `Conflict`, `NotFound`, and `InvalidParameter` drive errdefs classification. Start error mapping extracts the gRPC status message, checks for permission denied, directory execution, not-a-directory bind issues, command-not-found signatures, and otherwise returns an unknown error after setting a generic exit code.

## State And Persistence
No persistent state. `setExitCodeFromError` mutates container exit code through the provided callback.

## Dependencies And Integration Points
Integrates with `errdefs`, `pkg/errors`, gRPC status conversion, syscall error strings, device request errors, exec/container lifecycle code, and CLI expectations for exit codes.

## Risks And Edge Cases
String matching against runtime/containerd error messages is brittle but necessary for compatibility. The EISDIR path appends permission-denied text to preserve existing CLI behavior. Unknown runtime errors become exit code 128 and errdefs unknown.

## Test Signals
`errors_test.go` verifies `errNotRunning` classification through `isNotRunning`. Broader start-error mapping requires start-path tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/errors_test.go -->
# sources/cloud-native/moby/daemon/errors_test.go

## Purpose
Tests daemon not-running error classification.

## Important APIs, Types, And Functions
- `TestContainerNotRunningError` creates an error with `errNotRunning` and asserts `isNotRunning` recognizes it.

## Control Flow
The test directly exercises the constructor and classifier.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Covers `errors.go` and the internal type-based `errors.As` classification used by delete/kill cleanup paths.

## Risks And Edge Cases
The test is narrow and does not cover errdefs marker behavior or start exit-code mapping.

## Test Signals
Failure would mean force-removal and cleanup paths may stop ignoring already-not-running conditions correctly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/errors_test.go -->
