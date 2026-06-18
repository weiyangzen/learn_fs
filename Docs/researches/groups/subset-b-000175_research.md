# subset-b-000175 research

This grouped report covers Moby daemon event, exec, export, healthcheck, and graphdriver storage implementation files. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/events.go -->
# sources/cloud-native/moby/daemon/events.go

Purpose: daemon-facing event emission and swarm notification translation. It wraps `EventsService` with typed helpers for containers, plugins, volumes, networks, daemon events, subscriptions, and cluster object watch messages.

Important APIs and control flow: `LogContainerEventWithAttributes` copies container labels into the passed attributes map, adds image/name, and logs a local container event. Network, volume, plugin, and daemon helpers build `events.Actor` attributes. `SubscribeToEvents` and `UnsubscribeFromEvents` expose filtered event streams. `ProcessClusterNotifications` consumes `swarmapi.WatchMessage` until context cancellation or channel close, then `generateClusterEvent` dispatches object types to network/secret/config/node/service handlers. Node and service update handlers add old/new attribute deltas for availability, role, state, reachability, image, replicas, and update status. `logClusterEvent` maps swarm watch actions to Docker event actions and publishes swarm-scoped messages.

State, dependencies, and risks: state is the in-memory event buffer/pubsub owned by `EventsService`; removal events use current time because swarm metadata has no delete timestamp. Dependencies include swarmkit protobuf objects, daemon filters, container/libnetwork models, host naming, and gogo timestamp conversion. The label-copy function mutates the caller-provided attributes map and label keys can overwrite earlier attributes. Test signals in `daemon/events_test.go` cover label copying/override and timestamp action selection, but cluster delta generation is mostly implicit.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/events/events.go -->
# sources/cloud-native/moby/daemon/events/events.go

Purpose: in-process event service for the daemon. It stores a bounded recent event history and broadcasts new `api/types/events.Message` values through `moby/pubsub`.

Important APIs and control flow: `New` allocates a 256-message ring-like slice and a publisher with a 100 ms publish timeout and 1024 channel buffer. `Subscribe` returns a copy of all buffered events, a listener channel, and a cancel closure. `SubscribeTopic` computes a topic predicate from `Filter`, returns buffered events matching since/until/topic, and subscribes either to that topic or all events. `Log` builds local-scope messages with current UTC seconds/nanoseconds. `PublishMessage` increments metrics, appends or evicts the oldest buffered message, unlocks, then publishes. `loadBufferedEvents` walks the buffer backward, stops below `since`, skips after `until`, and prepends matches to preserve chronological order. `Close` closes all subscriber channels.

State, dependencies, and risks: protected state is `events []Message` and the pubsub publisher. Metrics track subscribers and event count. Slow subscribers can miss live events because publish has a timeout. `Evict` decrements metrics unconditionally, so callers must avoid double eviction. Tests cover broadcast, non-blocking publish with unread subscribers, buffer trimming, time filtering, and zero-time behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/events/events.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/events/events_test.go -->
# sources/cloud-native/moby/daemon/events/events_test.go

Purpose: unit tests for the daemon events service in `daemon/events/events.go`.

Important APIs and control flow: `TestEventsLog` subscribes two listeners, logs one container event, and asserts subscriber count, buffered length, action, actor ID, and image attribute from both channels. `TestEventsLogTimeout` leaves a subscriber unread and verifies publishing returns within one second, proving pubsub timeout behavior prevents a blocked listener from stalling logging. `TestLogEvents` writes more than `eventsLimit`, checks that only the most recent 256 remain, subscribes, emits ten more events, and verifies buffered/live ordering. The three `loadBufferedEvents` tests parse CLI-like fixtures with `testutils.Scan` and assert since/until filtering and the historical behavior that no buffered events are returned when both times are zero.

State, dependencies, and risks: tests use real pubsub channels and timeouts, so timing assumptions matter but durations are conservative. Fixtures depend on timestamp parsing and event output scanning. Test signals are strong for buffer size/order and publication liveness, but topic filtering and metrics decrement edge cases are not directly covered here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/events/events_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/events/filter.go -->
# sources/cloud-native/moby/daemon/events/filter.go

Purpose: converts API filter arguments into event-stream predicates for daemon event subscriptions.

Important APIs and control flow: `Filter` wraps `filters.Args`. `Include` composes event action, type, scope, per-object name/ID filters, image matching, and label matching. `matchEvent` preserves compatibility for `health_status`, `exec_create`, and `exec_start` by fuzzily matching action prefixes when users filter without the suffix after the colon. `fuzzyMatchName` matches either actor ID or `Actor.Attributes["name"]` against the event-type-specific filter key. `matchImage` handles both image events (`name` attribute) and container events (`image` attribute), comparing full ID/name and `stripTag` variants. `stripTag` uses distribution reference parsing and falls back to the original string on parse failure.

State, dependencies, and risks: the filter is stateless after construction and depends on `daemon/internal/filters` matching semantics plus distribution reference normalization. Matching is intentionally permissive for historical event strings. Risks include unexpected matches from fuzzy name filters, and `stripTag` returning familiar repository names that may collide across registries. Test coverage is indirect through event subscription behavior; no dedicated filter table tests appear in this group.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/events/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/events/testutils/testutils.go -->
# sources/cloud-native/moby/daemon/events/testutils/testutils.go

Purpose: test helper for parsing human-readable Docker event CLI output into structured `events.Message` fixtures.

Important APIs and control flow: regular-expression constants describe timestamp, event type, action, ID, and optional parenthesized attributes. `eventCliRegexp` is lazily compiled. `ScanMap` returns named capture groups for a line or an empty map on no match. `Scan` validates the line, parses the timestamp with daemon timestamp helpers, splits attributes on `", "`, splits each attribute on the first `=`, and builds an `events.Message` with `Time`, `TimeNano`, `Type`, `Action`, actor ID, and attributes.

State, dependencies, and risks: state is only the lazy regexp. Dependencies include `lazyregexp`, `timestamp.Parse`, and API event types. The parser is deliberately tailored to test fixtures, not a full CLI parser: attributes containing `, ` or `=` in values are lossy, missing attributes can produce an empty-key entry because the split loop still runs, and the regexp only accepts word-like action/type tokens. Test signal comes from event buffer tests that use historical CLI output fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/events/testutils/testutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/events_test.go -->
# sources/cloud-native/moby/daemon/events_test.go

Purpose: daemon-level tests for event attribute handling and swarm event timestamp selection.

Important APIs and control flow: `TestLogContainerEventCopyLabels` subscribes to an event service, emits a container create event, and asserts container labels are not mutated with generated `image`/`name` fields while expected original labels are present. `TestLogContainerEventWithAttributes` passes explicit attributes and verifies container labels override colliding input keys while unrelated input attributes survive. `validateTestAttributes` reads one event with a 10 second timeout and checks expected key/value pairs. `TestEventTimestamp` table-tests create/update/remove/unknown/invalid swarm watch actions against `eventTimestamp`.

State, dependencies, and risks: tests construct minimal `Daemon`, `container.Container`, API config, and swarm metadata values. The label tests observe only selected keys and not the complete attribute map, so they do not assert generated `image` or trimmed `name`. Timestamp checks compare Unix seconds, not nanoseconds, and only assert non-zero for current-time fallbacks. These tests protect the main compatibility behavior around label copy semantics and event time source.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/events_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/exec.go -->
# sources/cloud-native/moby/daemon/exec.go

Purpose: implements Docker exec lifecycle for creating, starting, tracking, attaching, and garbage-collecting exec commands inside running containers.

Important APIs and control flow: `ContainerExecCreate` validates container state, optionally resolves the requested user early, parses detach keys, creates `container.ExecConfig`, merges linked-container and requested environment, defaults user/working directory, registers the exec in both container and daemon stores, and logs `exec_create`. `ContainerExecStart` validates the exec, marks it running once, wires stdin/stdout/stderr, loads the container OCI process spec on non-Windows, overlays args/env/cwd/TTY/console size, applies platform options, attaches stream copying, resolves the running container task, calls `tsk.Exec`, closes `Started`, then waits for context cancellation or attach completion. Cancellation sends KILL. Escape detach logs `exec_detach`; startup errors set exit code 126 when needed. `execCommandGC` periodically removes daemon exec references after they disappear from container command sets.

State, dependencies, and risks: state is split between `daemon.execCommands`, `container.ExecCommands`, `ExecConfig` locks/streams/exit code, and containerd task/process objects. Dependencies include containerd, OCI specs, daemon stream attach code, term detach handling, pools copy, and errdefs. Risks include create/start TOCTOU for users and container state, stream goroutine lifetime, and subtle cleanup differences between startup failure, detach, and process exit. Tests in this subset cover Linux AppArmor platform options; broader exec start behavior is integration-level.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/exec_linux.go -->
# sources/cloud-native/moby/daemon/exec_linux.go

Purpose: Linux-specific exec process option setup for user resolution, capabilities, AppArmor, and rlimits.

Important APIs and control flow: `getUserFromContainerd` loads the containerd container, retrieves info and OCI spec, then applies containerd OCI spec options `WithUser`, `WithAdditionalGIDs`, and appended host-config groups to compute `spec.Process.User`. `execSetPlatformOpt` resolves `ec.User` either through containerd snapshotter metadata or legacy `getUser`; grants all capabilities when the exec is privileged; selects an AppArmor profile based on explicit container profile, privileged container inheritance, or default profile; reloads the default profile if missing; assigns `p.ApparmorProfile`; and finally applies daemon rlimits through `withRlimits`.

State, dependencies, and risks: it mutates the `specs.Process` passed from `ContainerExecStart`. Dependencies include containerd OCI helpers, daemon config, container security options, capability listing, AppArmor feature/profiles, and rlimit setup. Risks include behavior differences between snapshotter and non-snapshotter user lookup, inherited AppArmor semantics where `docker exec --privileged` does not itself unconfine AppArmor, and runtime failure if AppArmor profile reload fails. Test coverage focuses on AppArmor selection across host support and container privilege/profile combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/exec_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/exec_linux_test.go -->
# sources/cloud-native/moby/daemon/exec_linux_test.go

Purpose: Linux unit test for AppArmor profile selection during exec process setup.

Important APIs and control flow: `TestExecSetPlatformOptAppArmor` captures whether AppArmor is supported, creates a daemon config store, and table-tests default, custom profile, privileged container, and privileged container with custom profile. It runs each case for both regular exec and `exec --privileged`, then calls `execSetPlatformOpt` with a minimal container and `specs.Process`, asserting the resulting `ApparmorProfile`.

State, dependencies, and risks: the test depends on host AppArmor support detection, so expected profile is blank when unsupported. It documents a known behavior/possible bug: custom container profiles take precedence over privileged-container unconfined behavior, and exec privileged does not change AppArmor selection. The test exercises only the AppArmor branch; user lookup, capabilities, and rlimit behavior are not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/exec_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/exec_windows.go -->
# sources/cloud-native/moby/daemon/exec_windows.go

Purpose: Windows-specific exec process option setup.

Important APIs and control flow: `execSetPlatformOpt` checks the target container image platform and, for Windows containers, assigns `p.User.Username = ec.User`. It returns nil without applying Linux-specific capabilities, AppArmor, or rlimit logic.

State, dependencies, and risks: it mutates only the OCI `specs.Process` user field and depends on the daemon container `ImagePlatform.OS`. The file intentionally keeps behavior minimal because Windows user handling is passed through as a username rather than resolved to Linux UID/GID and supplementary groups. Risks are mostly integration-level: non-Windows containers running on a Windows daemon path receive no user mapping here, and invalid usernames are left to lower layers. No tests for this file are included in this group.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/exec_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/export.go -->
# sources/cloud-native/moby/daemon/export.go

Purpose: implements container filesystem export to a tar stream.

Important APIs and control flow: `ContainerExport` resolves the container, rejects Windows container export from unsupported daemons, rejects dead or removal-in-progress containers with conflict errors, delegates to `containerExport`, wraps errors with the requested name, and logs an export event on success. `containerExport` validates `RWLayer`, checks context cancellation, mounts the RW layer with the container mount label, defers unmount with warning-only logging, creates an uncompressed chroot tar with daemon ID mapping, closes the archive when context is cancelled, copies the archive to the output writer, maps cancellation during copy to `errdefs.Cancelled`, and logs `ActionExport`.

State, dependencies, and risks: state is the mounted RW layer and streamed tar reader. Dependencies include `chrootarchive.Tar`, archive compression options, ID mappings, container RWLayer, and daemon events. Export is a volatile snapshot: writes during copy can appear inconsistently. Risks include unmount failures, cancellation races while streaming, and unsupported Windows-container path. No direct tests appear here; behavior is covered through API/integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/btrfs/btrfs.go -->
# sources/cloud-native/moby/daemon/graphdriver/btrfs/btrfs.go

Purpose: Linux/cgo Btrfs graphdriver implementation using Btrfs subvolumes, snapshots, qgroups, and the generic naive diff wrapper.

Important APIs and control flow: `Init` verifies the backing filesystem is Btrfs, creates/chowns driver home, parses `btrfs.min_space`, bind-mounts the home directory to improve propagation behavior, optionally enables quota, and returns `NewNaiveDiffDriver`. Cgo helpers open directories and issue Btrfs ioctls for subvolume create/snapshot/delete, quota enable/rescan, qgroup status/lookup/limit. `Create` creates a new subvolume or snapshot of the parent, applies per-layer `size` quota if requested, persists quota size under `quotas/<id>`, adjusts remapped root ownership, and relabels. `Remove` removes quota metadata, updates quota status, recursively deletes nested subvolumes, falls back to `EnsureRemoveAll`, and rescans quota. `Get` validates the subvolume and reapplies persisted quota; `Put` is a no-op.

State, dependencies, and risks: persistent state lives under `subvolumes/` and `quotas/`, plus Btrfs qgroups. Dependencies include Linux Btrfs headers >=4.12, ioctls, mount helper, SELinux labels, user namespaces, fstype detection, and quota support. Risks include cgo/platform build constraints, privilege requirements, recursive subvolume deletion failures, and quota cleanup warnings not being fatal. Tests use `graphtest` plus nested subvolume deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/btrfs/btrfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/btrfs/btrfs_test.go -->
# sources/cloud-native/moby/daemon/graphdriver/btrfs/btrfs_test.go

Purpose: Btrfs graphdriver conformance tests.

Important APIs and control flow: `TestBtrfsSetup` acquires a shared `graphtest` driver. `TestBtrfsCreateEmpty`, `TestBtrfsCreateBase`, and `TestBtrfsCreateSnap` run generic layer creation and snapshot validation. `TestBtrfsSubvolDelete` creates a writable layer, creates a nested Btrfs subvolume inside its mounted filesystem, removes the layer, and asserts the nested subvolume path no longer exists. `TestBtrfsTeardown` releases the shared driver.

State, dependencies, and risks: tests require Linux, cgo, a Btrfs-backed temp driver root, and privileges/capabilities sufficient for Btrfs ioctls. The shared driver pattern means setup/teardown ordering matters, and a failed intermediate test can leave cleanup work to `PutDriver`. The strongest signal is recursive subvolume deletion, which protects against leaked child subvolumes that regular directory removal cannot handle.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/btrfs/btrfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/btrfs/dummy_unsupported.go -->
# sources/cloud-native/moby/daemon/graphdriver/btrfs/dummy_unsupported.go

Purpose: unsupported-platform package stub for the Btrfs graphdriver.

Important APIs and control flow: the file has build tags `!linux || !cgo` and declares package `btrfs` without registering a driver or defining runtime behavior. This lets imports/builds of the package succeed on non-Linux or non-cgo builds while excluding the ioctl-backed implementation.

State, dependencies, and risks: there is no runtime state. The integration point is build selection: without Linux+cgo, `graphdriver.Register("btrfs", Init)` never runs, so automatic graphdriver selection cannot pick Btrfs. This is intentional, but tests or docs expecting Btrfs availability must account for build tags. No direct tests are needed beyond cross-platform build success.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/btrfs/dummy_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/copy/copy.go -->
# sources/cloud-native/moby/daemon/graphdriver/copy/copy.go

Purpose: Linux directory-copy helper for graphdrivers, preserving file content, hardlink relationships, metadata, selected xattrs, and special file types.

Important APIs and control flow: `Mode` selects content copy or hardlinking. `copyRegular` creates a destination exclusively, tries `FICLONE`, falls back to `copy_file_range`, disables unsupported cross-device paths, then uses buffered copy. `DirCopy` walks `srcDir`, rebases each path under `dstDir`, handles regular files, directories, symlinks, FIFOs/sockets, and devices, tracks source `(dev, ino)` to preserve hardlinks in content-copy mode, copies ownership, `security.capability`, optionally `trusted.overlay.opaque`, modes, and timestamps. Directory mtimes are deferred and restored after children. Device creation is skipped inside user namespaces. `doCopyXattrs` currently copies only overlay opaque metadata.

State, dependencies, and risks: state is temporary maps and deferred directory timestamp list. Dependencies include Linux syscalls, xattr helpers, user namespace detection, pools copy, and filesystem support for clone/range/xattrs/mknod. Risks include fallback complexity, skipped devices in user namespaces, copied xattrs failing on unsupported filesystems, and walk-time races if source changes. Tests cover regular copy, metadata preservation, and hardlink preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/copy/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/copy/copy_test.go -->
# sources/cloud-native/moby/daemon/graphdriver/copy/copy_test.go

Purpose: Linux tests for the graphdriver directory-copy helper.

Important APIs and control flow: `TestCopy` and `TestCopyWithoutRange` copy a deterministic random buffer through `copyRegular` with fast-copy paths enabled or disabled. `TestCopyDir` recursively populates a source tree with random modes and mtimes, copies it, and walks the source comparing destination type/mode/uid/gid/mtime while asserting copied files are not the same inode when on the same device. `populateSrcDir` builds nested directories and files with varied metadata. `TestCopyHardlink` creates two source hardlinks, runs content copy, and asserts destination hardlink inodes match.

State, dependencies, and risks: tests rely on Linux stat fields, local filesystem mtime precision, and permission to set modes/times. They do not test symlinks, devices, sockets, FIFOs, xattrs, clone/range fallback errors, or Hardlink mode directly. The main signal is preserving core metadata and hardlink topology for VFS and other users of `DirCopy`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/copy/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver.go -->
# sources/cloud-native/moby/daemon/graphdriver/driver.go

Purpose: central graphdriver interfaces, registration, selection, and prior-driver detection.

Important APIs and control flow: `CreateOpts`, `InitFunc`, `ProtoDriver`, `DiffDriver`, `Driver`, `DiffGetterDriver`, and `FileGetCloser` define the storage-driver contract. `Register` stores init functions by name and rejects duplicates; `IsRegistered` queries the registry. `New` either initializes an explicitly requested driver after checking removed names, or scans existing non-empty driver directories, picks a prior driver in platform priority order, errors if multiple prior drivers exist, otherwise tries priority drivers and then all registered drivers skipping `ErrUnSupported` errors. `scanPriorDrivers` ignores `vfs`, and `isEmptyDir` treats open/read errors as non-empty. `checkRemoved` rejects removed `aufs`, `devicemapper`, and legacy `overlay`.

State, dependencies, and risks: state is the package-global driver registry and platform `priority`. Persistent detection is based on directories under the graph root. Dependencies include filesystem stat/read, logging, and user ID mappings passed to drivers. Risks include ambiguous prior state blocking daemon startup, map iteration fallback order being nondeterministic, and support errors needing to implement `NotSupported`. Tests cover only `isEmptyDir`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_freebsd.go -->
# sources/cloud-native/moby/daemon/graphdriver/driver_freebsd.go

Purpose: FreeBSD graphdriver priority declaration.

Important APIs and control flow: defines package variable `priority = "zfs"`, which `graphdriver.New` splits and uses for prior-driver preference and automatic selection.

State, dependencies, and risks: there is no runtime logic beyond influencing driver selection. On FreeBSD, automatic graphdriver choice prefers ZFS and there is no fallback list in this file. The behavior depends on the ZFS driver being registered and supported at runtime; if not, `New` falls through to any registered drivers via map iteration. Test signal is platform build/driver initialization rather than direct unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_linux.go -->
# sources/cloud-native/moby/daemon/graphdriver/driver_linux.go

Purpose: Linux graphdriver priority declaration.

Important APIs and control flow: defines `priority = "overlay2,fuse-overlayfs,btrfs,zfs,vfs"`. `graphdriver.New` uses this ordered list to prefer existing prior state and to auto-select the first supported driver on a new root.

State, dependencies, and risks: there is no direct runtime state. The order encodes Linux storage policy: native overlay2 first, rootless-friendly fuse-overlayfs second, then Btrfs, ZFS, and VFS fallback. Driver init functions still perform feature detection and may return not-supported errors. Tests are indirect through graphdriver initialization and per-driver suites.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_test.go -->
# sources/cloud-native/moby/daemon/graphdriver/driver_test.go

Purpose: unit test for graphdriver prior-state directory emptiness detection.

Important APIs and control flow: `TestIsEmptyDir` creates a temp root, then checks `isEmptyDir` for an empty directory, a directory containing a subdirectory, and a directory containing an empty file.

State, dependencies, and risks: the test uses only local filesystem operations and `gotest.tools` assertions. It protects `scanPriorDrivers` from treating empty driver directories as prior state while recognizing any real child entry as non-empty. It does not cover read errors, nonexistent directories, duplicate drivers, removed-driver errors, or priority selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_unsupported.go -->
# sources/cloud-native/moby/daemon/graphdriver/driver_unsupported.go

Purpose: priority declaration for platforms that are not Linux, Windows, or FreeBSD.

Important APIs and control flow: under build tag `!linux && !windows && !freebsd`, defines `priority = "unsupported"`. `graphdriver.New` will try a driver named `unsupported` first, then fall back to any registered drivers if present.

State, dependencies, and risks: no state is managed here. The integration point is compile-time platform selection, ensuring the package has a `priority` variable everywhere. Unsupported platforms typically lack concrete driver registrations, so selection should fail with "no supported storage driver found." Build coverage is the primary test signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_windows.go -->
# sources/cloud-native/moby/daemon/graphdriver/driver_windows.go

Purpose: Windows graphdriver priority declaration.

Important APIs and control flow: defines `priority = "windowsfilter"`, causing automatic graphdriver selection on Windows to prefer the HCS-backed Windows filter driver.

State, dependencies, and risks: there is no direct runtime state. Correct behavior depends on the Windows filter package registering `windowsfilter` and `InitFilter` succeeding on a supported filesystem. Test signal is Windows build and driver integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/driver_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/errors.go -->
# sources/cloud-native/moby/daemon/graphdriver/errors.go

Purpose: shared unsupported/prerequisite error taxonomy for graphdriver selection.

Important APIs and control flow: constants `ErrNotSupported`, `ErrPrerequisites`, and `ErrIncompatibleFS` are `NotSupportedError` values. `ErrUnSupported` is an interface with marker method `NotSupported`. `NotSupportedError` implements `Error` and `NotSupported`. `IsDriverNotSupported` returns true when the direct error value implements `ErrUnSupported`.

State, dependencies, and risks: no state or external dependencies. The integration point is `graphdriver.New`, which skips drivers whose init error is recognized as unsupported but returns other errors. A risk is that `IsDriverNotSupported` uses a direct type switch and does not unwrap wrapped errors, so drivers must return marker errors directly or risk aborting selection. No direct tests in this group cover wrapping behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/fsdiff.go -->
# sources/cloud-native/moby/daemon/graphdriver/fsdiff.go

Purpose: generic diff implementation that wraps a `ProtoDriver` to satisfy full `graphdriver.Driver` when the backend exposes mounted directories but not native diffs.

Important APIs and control flow: `NewNaiveDiffDriver` returns a `NaiveDiffDriver` with ID mapping. `Diff` mounts the target layer, and for base layers tars the whole filesystem; otherwise it mounts parent, computes `archive.ChangesDirs`, exports changes with ID mapping, and wraps the tar reader so close releases mounts. It sleeps until the next second after close to avoid mtime precision races. `Changes` mounts layer and optional parent and delegates to `archive.ChangesDirs`. `ApplyDiff` mounts the target, applies an uncompressed layer through `ApplyUncompressedLayer` with ID mapping and best-effort xattr option, and logs timing. `DiffSize` computes changes then sums changed sizes.

State, dependencies, and risks: state is backend mounts and `BestEffortXattrs`. Dependencies include `go-archive`, chrootarchive, compression, logging, and user mappings. Risks include expensive full-tree comparisons, mtime second-granularity workaround slowing builds, and subtle behavior when xattrs cannot be restored. Concrete drivers use this as fallback or primary diff implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/fsdiff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs.go -->
# sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs.go

Purpose: Linux graphdriver using the external `fuse-overlayfs` mount program, primarily for rootless or overlayfs-incompatible environments.

Important APIs and control flow: `Init` requires the binary and kernel >=4.18, creates driver home and short-link directory, and returns a driver with naive diff. Layer layout mirrors overlay2: per-layer `diff`, optional `work`, `merged`, `lower`, `link`, and root `l/` symlinks. `Create` rejects storage options, creates diff/link metadata, marks parents committed, and writes lower chains up to 128 layers. `Get` returns `diff` for base layers or invokes `fuse-overlayfs -o <lower/upper/work,label> <merged>` for layered mounts with refcounting. `Put` unmounts via `fusermount3`/`fusermount`, falling back to `syncfs` plus `unix.Unmount`. `ApplyDiff` writes directly to the upper diff path for direct parents using AUFS whiteouts; `Diff`, `DiffSize`, and `Changes` use naive diff.

State, dependencies, and risks: persistent state is overlay-like layer directories and link files; runtime state is FUSE mounts tracked by `mountref.Counter` and per-layer locks. Dependencies include the external binary, kernel, FUSE mount utilities, SELinux labels, user namespace detection, and archive helpers. Risks include binary availability, FUSE unmount failures, no storage-opt support, and whiteout-format differences from kernel overlay2. Tests use shared graphtest and benchmarks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs_test.go -->
# sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs_test.go

Purpose: conformance and benchmark coverage for the fuse-overlayfs graphdriver.

Important APIs and control flow: `init` swaps chrooted untar/apply functions for direct archive helpers to speed tests and make failures easier to debug. Tests acquire a shared driver, validate empty/base/snapshot layer creation, read through 128 layers, and release the driver. Benchmarks measure `Exists`, `Get` on empty layers, diff workloads with different lower/upper file counts, diff/apply, deep-layer diff, and deep-layer read.

State, dependencies, and risks: tests require Linux, the `fuse-overlayfs` binary, FUSE support, and sufficient mount permissions. They do not include native diff tests because this driver relies on naive diff. The strongest signals are layer-chain visibility and generic graphdriver correctness; performance benchmarks expose FUSE and naive diff overhead.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs_unsupported.go -->
# sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs_unsupported.go

Purpose: unsupported-platform package stub for fuse-overlayfs.

Important APIs and control flow: under build tag `!linux`, it only declares package `fuseoverlayfs`, so the Linux implementation and driver registration are absent.

State, dependencies, and risks: no runtime state or dependencies. The integration effect is that `fuse-overlayfs` is unavailable to `graphdriver.New` outside Linux. Build success on unsupported platforms is the test signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/fuse-overlayfs/fuseoverlayfs_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/graphbench_unix.go -->
# sources/cloud-native/moby/daemon/graphdriver/graphtest/graphbench_unix.go

Purpose: reusable Unix benchmarks for graphdriver implementations.

Important APIs and control flow: benchmark helpers create a temp driver with `GetDriver`, build layers with deterministic helper functions, reset timers around setup, and measure hot operations. They cover `Exists`, `Get`/`Put` on empty layers, base-layer diff streaming, diff on configurable lower/upper file counts, diff/apply loops, deep-layer diff, and deep-layer file reads. Each diff benchmark drains archives to `io.Discard` so backend archive generation work is included.

State, dependencies, and risks: state is the shared graphtest driver and temporary layer trees. Dependencies include test helpers, `stringid`, file IO, and graphdriver APIs. Benchmarks sometimes pass `parent=""` to diff paths, exercising full or fallback diff behavior rather than strictly direct-parent native diff. The diff/apply size comparison is intentionally not enforced, leaving a documented TODO. Signals are comparative performance and basic correctness during benchmark setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/graphbench_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/graphtest_unix.go -->
# sources/cloud-native/moby/daemon/graphdriver/graphtest/graphtest_unix.go

Purpose: reusable Unix conformance tests for graphdriver implementations.

Important APIs and control flow: `GetDriver` lazily creates a shared temp-root driver by name and increments a refcount; `PutDriver` decrements and cleans up. `DriverTestCreateEmpty` verifies a new empty layer exists, mounts, has expected directory metadata, and contains no entries except filtered `lost+found`. `DriverTestCreateBase` and `DriverTestCreateSnap` validate base creation and parent snapshot content. `DriverTestDeepLayerRead` builds many layers and checks top-layer and lower-file visibility. `DriverTestDiffApply` builds a base and upper, removes entries, diffs upper, applies into a sibling layer, compares size, content, and deletions. `DriverTestChanges` compares reported change lists. `DriverTestSetQuota` writes below and above a requested quota and expects `EDQUOT` or `ENOSPC`.

State, dependencies, and risks: shared driver state makes setup/teardown order important. Tests require Unix filesystem semantics, mount privileges depending on driver, and quota support for quota tests. These are the primary cross-driver behavioral signals for create/get/put/remove/diff/apply/quota.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/graphtest_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/graphtest_windows.go -->
# sources/cloud-native/moby/daemon/graphdriver/graphtest/graphtest_windows.go

Purpose: Windows package placeholder for `graphtest`.

Important APIs and control flow: the file only declares package `graphtest`, preventing Unix-specific test helper files from being compiled on Windows while allowing package references to resolve.

State, dependencies, and risks: no runtime state, APIs, or tests are defined here. Windows graphdriver coverage must come from Windows-specific tests elsewhere; the Unix graphtest conformance suite is not available on Windows through this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/graphtest_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/testutil.go -->
# sources/cloud-native/moby/daemon/graphdriver/graphtest/testutil.go

Purpose: shared graphdriver test helpers for deterministic file content, layer mutations, and assertions.

Important APIs and control flow: `randomContent` creates deterministic pseudo-random bytes from a seed. Helpers mount layers with `Get`, defer `Put`, and create/check/remove files and directories. `addManyFiles`, `changeManyFiles`, and `checkManyFiles` build grouped directory/file workloads and expected `archive.Change` entries. `checkChanges` sorts expected and actual changes before comparing. `addManyLayers` chains random layer IDs and writes per-layer marker files; `checkManyLayers` verifies the top layer and parent chain markers. `readDir` hides `lost+found` to normalize ext filesystems.

State, dependencies, and risks: helpers mutate real graphdriver layers through mounted paths, so correctness depends on driver `Get`/`Put` and filesystem behavior. Paths are joined with OS filepath, while some expected change paths include leading slash-style archive paths. Risks include hidden assumptions about permissions, deterministic random content size, and change-kind semantics. The helpers underpin nearly all graphtest conformance and benchmark signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/testutil_unix.go -->
# sources/cloud-native/moby/daemon/graphdriver/graphtest/testutil_unix.go

Purpose: Unix-specific graphdriver test helpers for metadata verification and base layer creation.

Important APIs and control flow: `verifyFile` stats a path and checks file type, permissions, sticky/setuid/setgid bits, and UID/GID from `syscall.Stat_t`. `createBase` temporarily clears umask, creates a writable layer, mounts it, creates a sticky directory owned by UID 1/GID 2 and a setuid write-only file, then unmounts. `verifyBase` mounts a layer and asserts that the directory, file, ownership, permissions, and entry count match expectations.

State, dependencies, and risks: tests depend on Unix mode bits, ability to chown, and driver preservation of metadata through copy/snapshot paths. Clearing umask is scoped with defer. These helpers provide strong signals that graphdrivers preserve POSIX metadata, but they are not compiled on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/graphtest/testutil_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/check.go -->
# sources/cloud-native/moby/daemon/graphdriver/overlay2/check.go

Purpose: runtime probes for overlay2 native diff safety and metacopy status.

Important APIs and control flow: `doesSupportNativeDiff` optionally requires userxattr inside user namespaces, creates layered test dirs, marks a middle-layer directory opaque, mounts overlay, forces copy-up, verifies the opaque xattr was not copied to upper, then renames a lower directory to detect redirect_dir. It returns errors that cause overlay2 to fall back to naive diff. `usingMetacopy` mounts a small overlay, performs metadata-only chmod, and checks for the `metacopy` xattr to report whether kernel metacopy behavior is active.

State, dependencies, and risks: state is temporary dirs and short-lived overlay mounts. Dependencies include overlay xattrs, kernel mount behavior, user namespace detection, containerd mount helpers, and `overlayutils.NeedsUserXAttr`. Risks include probe failures from insufficient mount privileges, xattr support variation, userns kernel differences, and accidental stale mounts if cleanup fails. Test signal is indirect through overlay2 initialization/status and native-diff tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/mount.go -->
# sources/cloud-native/moby/daemon/graphdriver/overlay2/mount.go

Purpose: helper for overlay2 mounts whose option strings must be made relative to the driver home to fit the kernel page-size mount-data limit.

Important APIs and control flow: `mountFrom` starts a goroutine, locks it to an OS thread, unshares `CLONE_FS` so cwd changes do not leak to other threads, changes to the requested directory, and performs `unix.Mount`. The thread is deliberately not unlocked because its filesystem state cannot be restored safely.

State, dependencies, and risks: runtime state is a throwaway locked OS thread with isolated filesystem context. Dependencies are Linux `unshare`, `chdir`, and mount syscalls. It is called by `overlay2.Get` only when absolute mount data is too large and relative layer links are needed. Risks include thread leakage by design, syscall failure in restricted environments, and mount behavior depending on cwd isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay.go -->
# sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay.go

Purpose: Linux kernel overlayfs graphdriver with native diff fast paths, short lowerdir links, project quota support, and mount refcounting.

Important APIs and control flow: `Init` parses `overlay2.size`, verifies overlay support and d_type, detects backing filesystem/metacopy/index/userxattr, creates `home` and `l/`, initializes mount counters/locks, and configures XFS project quota when available. `CreateReadWrite` merges default quota and enforces quota support; `Create` rejects size on read-only layers; `create` writes layer directories, random link ID, `link`, optional `work`, parent `committed`, and `lower` chain. `Get` returns `diff` for base layers; otherwise it builds read-only or read-write overlay options, shortens mount data with relative paths when needed, mounts, and chowns `work/work` for userns. `Put` refcount-unmounts and removes `merged`. `ApplyDiff`, `Diff`, and `DiffSize` use native upperdir operations only when native diff is safe and parent is direct; otherwise they delegate to naive diff.

State, dependencies, and risks: persistent state is per-layer `diff/work/merged/lower/link/committed` plus root `l/` symlinks and optional quotas. Runtime state is `mountref.Counter`, per-ID locks, and package-level feature flags. Dependencies include overlayfs kernel support, xattrs, SELinux labels, fstype/d_type detection, quotas, user namespaces, and archive whiteout handling. Risks include max-depth enforcement, page-size mount limits, stale mounts, global feature-detection caching, and quota-only-on-XFS behavior. Tests and benchmarks use graphtest.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay_test.go -->
# sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay_test.go

Purpose: conformance and benchmark coverage for the overlay2 graphdriver.

Important APIs and control flow: `init` replaces chrooted archive functions with direct archive helpers for faster and more debuggable tests. `skipIfNaive` creates a temp dir and skips native-diff-specific tests when `useNaiveDiff` says the host is unsafe. Tests acquire a shared overlay2 driver, validate empty/base/snapshot creation, read through 128 layers, run diff/apply when native diff is available, skip `Changes` because naive change algorithm is not used there, and release the driver. Benchmarks cover common driver operations and deep-layer workloads.

State, dependencies, and risks: tests require Linux overlayfs support and sufficient mount privileges. Because native-diff capability is host-dependent, some tests skip on kernels/filesystems that force naive diff. The suite strongly signals graphdriver contract behavior but leaves some overlay2-specific storage-option and mount-shortening paths untested.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay_unsupported.go -->
# sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay_unsupported.go

Purpose: unsupported-platform package stub for overlay2.

Important APIs and control flow: under build tag `!linux`, it only declares package `overlay2`; no driver registration or implementation is compiled.

State, dependencies, and risks: no runtime state. The integration point is platform build selection: overlay2 is Linux-only, so non-Linux graphdriver priority lists cannot select it. Build success is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlay2/overlay_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlayutils/overlayutils.go -->
# sources/cloud-native/moby/daemon/graphdriver/overlayutils/overlayutils.go

Purpose: shared overlay filesystem support checks and xattr naming helpers.

Important APIs and control flow: `ErrDTypeNotSupported` creates a `NotSupportedError` with driver/backing filesystem-specific remediation text for XFS and ext filesystems. `SupportsOverlay` rejects rootless SELinux via `_DOCKERD_ROOTLESS_SELINUX`, creates temporary lower/upper/work/merged dirs, attempts an actual overlay mount with one or two lowerdirs depending on `checkMultipleLowers`, unmounts, and returns mount errors wrapped. `GetOverlayXattr` chooses `trusted.overlay.<name>` in the initial user namespace and `user.overlay.<name>` in user namespaces.

State, dependencies, and risks: state is temporary mount test directories. Dependencies include Linux overlayfs, xattr namespace rules, user namespace detection, and graphdriver unsupported errors. Risks include probe false negatives in restricted environments, cleanup warnings leaving temporary dirs, and env-based SELinux rootless detection. These helpers gate overlay2 and native diff behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlayutils/overlayutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlayutils/randomid.go -->
# sources/cloud-native/moby/daemon/graphdriver/overlayutils/randomid.go

Purpose: random short-link ID generation for overlay-style graphdrivers.

Important APIs and control flow: `GenerateID` computes the needed random byte count for the requested base32 length, reads from `crypto/rand.Reader`, retries partial/retryable failures with incremental 10 ms backoff up to nine retries, logs retryable errors, base32-encodes the bytes, and truncates to the requested length. `retryOnError` unwraps `os.PathError` and treats `EPERM` as retryable for entropy-pool-related conditions.

State, dependencies, and risks: no persistent state; temporary state is the random byte buffer and retry counters. Dependencies are cryptographic randomness, base32 encoding, logging, and Unix errno. On unrecoverable random-source failure it panics, which is acceptable because unique layer link IDs are required. There is no collision check here; callers rely on random entropy and symlink creation failure if a collision occurs. Test coverage is indirect through overlay2/fuse-overlayfs layer creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlayutils/randomid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlayutils/userxattr.go -->
# sources/cloud-native/moby/daemon/graphdriver/overlayutils/userxattr.go

Purpose: detects whether rootless overlayfs mounts need the `userxattr` option.

Important APIs and control flow: `NeedsUserXAttr` returns false outside a user namespace. Inside a user namespace it fast-paths to true for kernel >=5.11, because upstream rootless overlayfs uses `user.overlay.*` xattrs. For older kernels, it creates a temporary overlay mount with `userxattr`; if mounting fails, it assumes an Ubuntu/Debian-style backport that does not need the option and returns false; if mounting succeeds, it unmounts and returns true.

State, dependencies, and risks: state is a temporary `userxattr-check` directory under the driver home. Dependencies include kernel version parsing, user namespace detection, containerd mount helpers, and overlay mount behavior. Risks include distro backports making version checks imperfect, mount permission failures being interpreted as no userxattr needed, and cleanup/unmount warnings. It directly influences overlay2 native-diff checks and mount options.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/overlayutils/userxattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_btrfs.go -->
# sources/cloud-native/moby/daemon/graphdriver/register/register_btrfs.go

Purpose: blank-import registration hook for the Btrfs graphdriver.

Important APIs and control flow: imports `github.com/moby/moby/v2/daemon/graphdriver/btrfs` for side effects under Linux when the `exclude_graphdriver_btrfs` build tag is not set. The imported package `init` registers `"btrfs"` with the central graphdriver registry.

State, dependencies, and risks: no direct runtime state. Build tags control whether Btrfs registration is compiled in. The file is part of the daemon's graphdriver plugin registration mechanism; omitting it or setting the exclusion tag makes Btrfs unavailable even on suitable filesystems. Build/initialization coverage is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_btrfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_fuseoverlayfs.go -->
# sources/cloud-native/moby/daemon/graphdriver/register/register_fuseoverlayfs.go

Purpose: blank-import registration hook for the fuse-overlayfs graphdriver.

Important APIs and control flow: imports the `fuse-overlayfs` graphdriver package for side effects on Linux unless `exclude_graphdriver_fuseoverlayfs` is set. Its `init` registers `"fuse-overlayfs"` in the graphdriver registry.

State, dependencies, and risks: no direct runtime state. Build tags decide availability; runtime initialization still checks binary and kernel support. This hook is needed for Linux priority selection to consider fuse-overlayfs after overlay2. Test signal is successful build and driver selection/registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_fuseoverlayfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_overlay2.go -->
# sources/cloud-native/moby/daemon/graphdriver/register/register_overlay2.go

Purpose: blank-import registration hook for the overlay2 graphdriver.

Important APIs and control flow: imports `overlay2` for side effects on Linux unless `exclude_graphdriver_overlay2` is set. The overlay2 package `init` registers the `"overlay2"` driver.

State, dependencies, and risks: no direct state. This file connects the default Linux priority list to the actual driver implementation. Excluding it or breaking its import would make automatic selection skip overlay2 and fall back to later drivers. Build and initialization are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_overlay2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_vfs.go -->
# sources/cloud-native/moby/daemon/graphdriver/register/register_vfs.go

Purpose: blank-import registration hook for the VFS graphdriver.

Important APIs and control flow: imports `github.com/moby/moby/v2/daemon/graphdriver/vfs` for side effects, causing its `init` to register `"vfs"` on all supported builds.

State, dependencies, and risks: no direct state. VFS is the portable fallback driver in Linux priority and is useful in test or unsupported filesystem environments. Registration is unconditional in this file; runtime behavior still depends on VFS init and quota options. Build coverage is the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_vfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_windows.go -->
# sources/cloud-native/moby/daemon/graphdriver/register/register_windows.go

Purpose: blank-import registration hook for the Windows graphdriver.

Important APIs and control flow: under Windows builds, imports the `windows` graphdriver package for side effects so it registers `"windowsfilter"`.

State, dependencies, and risks: no direct runtime state. This is the bridge between the Windows priority list and the HCS-backed implementation. Correctness depends on Windows-only build selection and successful `InitFilter` at runtime. Build and Windows integration tests are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_zfs.go -->
# sources/cloud-native/moby/daemon/graphdriver/register/register_zfs.go

Purpose: blank-import registration hook for the ZFS graphdriver.

Important APIs and control flow: imports the ZFS graphdriver for side effects on Linux or FreeBSD unless `exclude_graphdriver_zfs` is set. The imported package registers `"zfs"`.

State, dependencies, and risks: no direct state. Build tags control whether ZFS is included in driver selection. Runtime initialization still requires the `zfs` command, `/dev/zfs`, and a valid dataset. The signal is successful platform build and graphdriver registration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/register/register_zfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/utils.go -->
# sources/cloud-native/moby/daemon/graphdriver/utils.go

Purpose: shared parser for graphdriver storage option strings.

Important APIs and control flow: `ParseStorageOptKeyValue` splits an option on the first `=`, returns an error when no separator exists, and trims surrounding whitespace from key and value while preserving additional `=` characters in the value.

State, dependencies, and risks: no state and only standard library dependencies. It is used by multiple drivers to parse daemon/global and per-layer storage options. It does not reject empty keys or values after trimming, so caller-specific validation must handle those. Tests cover missing separators, whitespace trimming, and values containing additional equals signs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/utils_test.go -->
# sources/cloud-native/moby/daemon/graphdriver/utils_test.go

Purpose: unit tests for storage-option key/value parsing.

Important APIs and control flow: `TestParseKeyValueOpt` checks invalid inputs `""` and `"key"` return exact error strings, then checks valid inputs with whitespace and additional `=` characters return the expected trimmed key/value pairs.

State, dependencies, and risks: no external state. The tests assert exact error text, which protects CLI/API compatibility but can make wording changes test-breaking. They do not cover empty key/value cases such as `"=value"` or `"key="`, leaving that validation to driver-specific parsers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/copy_linux.go -->
# sources/cloud-native/moby/daemon/graphdriver/vfs/copy_linux.go

Purpose: Linux VFS driver directory-copy implementation binding.

Important APIs and control flow: `dirCopy` delegates to `copy.DirCopy(srcDir, dstDir, copy.Content, false)`, using the graphdriver copy helper in content-copy mode and not copying overlay opaque xattrs.

State, dependencies, and risks: no direct state. The VFS driver depends on this when creating a child layer from a parent, so layer creation performs a full recursive copy while preserving Linux metadata handled by `copy.DirCopy`. Risks inherit from the copy helper: expensive full copies, filesystem metadata/xattr differences, and special-file handling limitations in user namespaces. Tests are indirect through VFS create/snapshot tests and copy helper tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/copy_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/copy_unsupported.go -->
# sources/cloud-native/moby/daemon/graphdriver/vfs/copy_unsupported.go

Purpose: non-Linux VFS directory-copy implementation binding.

Important APIs and control flow: under build tag `!linux`, `dirCopy` uses `chrootarchive.NewArchiver(user.IdentityMapping{}).CopyWithTar(srcDir, dstDir)`, copying parent layer contents through tar rather than Linux-specific filesystem walking.

State, dependencies, and risks: no direct state. Dependencies are chrootarchive and an empty identity mapping. The tar copy path is more portable but may not preserve every platform-specific metadata detail the Linux copy helper handles. It is used whenever VFS creates a child layer on non-Linux platforms. Test signal is cross-platform VFS behavior/builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/copy_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/driver.go -->
# sources/cloud-native/moby/daemon/graphdriver/vfs/driver.go

Purpose: portable VFS graphdriver that stores each layer as a plain directory and copies parent contents for layering.

Important APIs and control flow: `Init` parses options, creates the home directory, initializes quota support, rejects configured size when unsupported, and returns a `NaiveDiffDriver` with optional best-effort xattrs. `parseOptions` supports `size` and the explicit unsafe `vfs.xattrs=i_want_broken_containers` opt-in. `CreateReadWrite` applies per-layer size storage options when quota is supported. `Create` rejects storage opts for read-only layers. `create` makes `home/dir/<id>`, optionally applies quota, sets SELinux level label, and if a parent exists copies its directory with `CopyDir`. `Get`, `Put`, `Remove`, `Exists`, and `GetMetadata` are directory operations.

State, dependencies, and risks: persistent state is plain directories under `home/dir`. Dependencies include copy helpers, quota support, SELinux labels, ID mapping, and naive diff. VFS has no copy-on-write, so child creation is slow and space-heavy. Best-effort xattrs is intentionally dangerous and surfaced in status. Tests cover graphtest behavior, quota, and xattr unsupported handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/quota_linux.go -->
# sources/cloud-native/moby/daemon/graphdriver/vfs/quota_linux.go

Purpose: Linux quota support adapter for the VFS driver.

Important APIs and control flow: `driverQuota` stores a `quota.Control` and desired `quota.Quota`. `setupDriverQuota` attempts `quota.NewControl(driver.home)` and stores it, logging non-not-supported setup errors. `setQuotaOpt`, `getQuotaOpt`, `setupQuota`, and `quotaSupported` manage the configured size and apply quotas to layer directories through `quotaCtl.SetQuota`.

State, dependencies, and risks: state is per-driver quota control and option size. Dependencies include daemon internal quota support and logging. Risks include quota setup silently unavailable when unsupported, later size options returning quota errors, and filesystem-specific quota behavior. `vfs_test.go` uses `DriverTestSetQuota` with quota not required, so unsupported environments skip rather than fail.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/quota_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/quota_unsupported.go -->
# sources/cloud-native/moby/daemon/graphdriver/vfs/quota_unsupported.go

Purpose: non-Linux quota adapter for VFS that reports quota unsupported.

Important APIs and control flow: `driverQuota` is empty. `setupDriverQuota` is a no-op, `setQuotaOpt` and `setupQuota` return `quota.ErrQuotaNotSupported`, `getQuotaOpt` returns zero, and `quotaSupported` returns false.

State, dependencies, and risks: no state. It ensures VFS builds on non-Linux without quota primitives while giving callers deterministic unsupported errors for size options. A minor integration oddity is the no-op `setupDriverQuota` signature differs from the Linux helper but callers ignore its return value. Build and driver option tests provide the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/quota_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/vfs_test.go -->
# sources/cloud-native/moby/daemon/graphdriver/vfs/vfs_test.go

Purpose: Linux VFS graphdriver conformance, quota, and xattr behavior tests.

Important APIs and control flow: setup/create/base/snapshot/quota/teardown tests use `graphtest`. `TestXattrUnsupportedByBackingFS` mounts a ramfs, builds a tar layer containing a `SCHILY.xattr.user.test` PAX record, and runs two subtests: default VFS expects `EOPNOTSUPP` when applying the layer, while `vfs.xattrs=i_want_broken_containers` allows apply to succeed and then verifies file content exists.

State, dependencies, and risks: tests require Linux and, for the xattr test, permission to mount ramfs; otherwise it skips on `EPERM`. The xattr test directly validates the intentionally unsafe best-effort option. Generic graphtest coverage checks VFS copy-based layering and optional quota support.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/vfs/vfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/windows/windows.go -->
# sources/cloud-native/moby/daemon/graphdriver/windows/windows.go

Purpose: Windows `windowsfilter` graphdriver backed by HCSShim layers, sandbox VHDs, Windows backup streams, and reexec for layer import.

Important APIs and control flow: `InitFilter` rejects ReFS, creates home, parses default sandbox size and options, and initializes HCS driver info, mount refcounter, cache, and defaults. `Create`/`CreateReadWrite` resolve parent IDs, build parent layer chains, call `CreateLayer` or `CreateSandboxLayer`, expand sandbox size, validate parent directory, and persist `layerchain.json`. `Remove` terminates template VMs using the layer, retries transient HCS enumeration errors on old Windows, renames the layer to `-removing`, detaches stale VHDs on permission failure, and destroys it. `Get` activates/prepares layers and caches mount paths; `Put` unprepares/deactivates on final ref. `Diff`, `Changes`, `ApplyDiff`, and `DiffSize` use HCS layer readers/writers, backup privileges, tar whiteouts, backup stream conversion, and reexec `docker-windows-write-layer` unless disabled. `DiffGetter` opens files with backup privilege and handles files mutated during import.

State, dependencies, and risks: persistent state includes HCS layer directories, `layerchain.json`, optional `layerID` metadata, sandbox VHDs, and saved mutated boot files. Runtime state includes refcounts and a mount-path cache. Dependencies include HCSShim, winio, backup privileges, osversion quirks, longpath, vhd detach, and reexec. Risks are Windows-version-specific HCS races, typo-like `layerID`/`layerId` mismatch paths, privilege requirements, mutated-file backup correctness, and cleanup of `-removing` folders. Tests are external to this group.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/windows/windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs.go -->
# sources/cloud-native/moby/daemon/graphdriver/zfs/zfs.go

Purpose: Linux/FreeBSD ZFS graphdriver implementation using datasets, snapshots/clones, legacy mounts, and naive diff.

Important APIs and control flow: `Init` requires the `zfs` command and `/dev/zfs`, parses `zfs.fsname`, verifies or discovers the root dataset, builds a filesystem cache from recursive ZFS listing, creates/chowns the mount path, and returns `NewNaiveDiffDriver`. `Status` reports pool/dataset usage, quota, and compression. `Create` calls `create`, and if dataset-already-exists indicates an aborted build, destroys recursively and retries. Base layers create filesystems with `mountpoint=legacy`; child layers snapshot the parent and clone. `parseStorageOpt` supports per-layer `size` as ZFS quota. `Get` refcount-mounts the dataset at `mountPath/graph/<mountpoint>`, applies SELinux mount labels, and chowns for remapped root. `Put` lazy-unmounts and removes mountpoint. `Remove` destroys datasets recursively and updates the cache.

State, dependencies, and risks: persistent state is ZFS datasets, snapshots/clones, mountpoints, and driver filesystem cache. Dependencies include go-zfs, system `zfs`, `/dev/zfs`, mountinfo, SELinux labels, user mappings, and platform-specific root filesystem checks. Risks include external command availability, dataset discovery failures, snapshot-name nanosecond collisions, quota string validation deferred to ZFS, and mount refcount cleanup. Linux tests use graphtest including quota-required behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_freebsd.go -->
# sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_freebsd.go

Purpose: FreeBSD-specific ZFS graphdriver helpers.

Important APIs and control flow: `checkRootdirFs` uses `unix.Statfs` and checks `Fstypename` bytes for `"zfs"`; otherwise it logs and returns `graphdriver.ErrPrerequisites`. `getMountpoint` shortens layer IDs to at most 12 characters before an optional suffix separated by `-`, preserving a suffix when present.

State, dependencies, and risks: no persistent state. Dependencies include FreeBSD `Statfs_t`, logging, graphdriver errors, and string splitting. Risks include `id[:maxlen]` panicking if an ID shorter than 12 characters reaches this helper, though graphdriver layer IDs are normally long. The shortened mountpoint avoids FreeBSD mount/path constraints but can collide if truncated IDs share prefixes. Build and FreeBSD integration tests are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_linux.go -->
# sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_linux.go

Purpose: Linux-specific ZFS graphdriver helpers.

Important APIs and control flow: `checkRootdirFs` reads filesystem magic for the root directory, maps it to a human-readable backing filesystem name, and returns `ErrPrerequisites` with an error log if it is not ZFS. `getMountpoint` returns the full layer ID unchanged.

State, dependencies, and risks: no persistent state. Dependencies include daemon fstype detection and graphdriver errors. The helper is used when `zfs.fsname` is not explicitly configured, so incorrect rootdir filesystem detection prevents ZFS auto-discovery. Tests for ZFS initialization and graphtest behavior indirectly exercise this on suitable hosts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_test.go -->
# sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_test.go

Purpose: Linux ZFS graphdriver conformance tests.

Important APIs and control flow: setup/teardown tests acquire and release a shared ZFS driver. Generic graphtest functions validate empty/base/snapshot layer behavior. `TestZfsSetQuota` runs `DriverTestSetQuota` with quota marked required, so an unsupported quota path is a failure rather than a skip.

State, dependencies, and risks: tests require Linux with a functional ZFS setup, `zfs` command, `/dev/zfs`, a ZFS-backed test root or configured dataset, and privileges to create/destroy datasets and mount them. The suite gives strong signals for dataset lifecycle and quota enforcement but is environment-sensitive.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_unsupported.go -->
# sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_unsupported.go

Purpose: fallback ZFS helper definitions for platforms outside Linux and FreeBSD.

Important APIs and control flow: under build tag `!linux && !freebsd`, `checkRootdirFs` returns nil and `getMountpoint` returns the ID unchanged. Because the main ZFS implementation is itself built only for Linux or FreeBSD, these helpers primarily satisfy package completeness when needed by build constraints.

State, dependencies, and risks: no state. The file does not register or implement ZFS by itself. Build coverage is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/graphdriver/zfs/zfs_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/health.go -->
# sources/cloud-native/moby/daemon/health.go

Purpose: container healthcheck execution, monitoring, result state transitions, event emission, and bounded output buffering.

Important APIs and control flow: `cmdProbe.run` builds an exec config from `Healthcheck.Test`, optionally prepends shell, registers/logs exec create, starts `ContainerExecStart` in a goroutine with combined stdout/stderr buffer, separates a 30 second exec-start timeout from the configured probe timeout, cancels/awaits long probes, reads exit code from exec config, and returns a `HealthcheckResult`. `handleProbeResult` locks the container, ignores results after monitor stop, caps log entries at five, applies retries and start-period logic to transition starting/healthy/unhealthy, commits health state to the in-memory container replica, and emits `health_status` events on status changes. `monitor` schedules probes using `Interval`, `StartInterval`, and `StartPeriod`, ensures stop waits for active probes, and records metrics. `getProbe`, `updateHealthMonitor`, `initHealthMonitor`, and `stopHealthchecks` manage monitor lifecycle. `limitedBuffer` stores at most 4096 bytes and appends `...` on truncation.

State, dependencies, and risks: state spans container `State.Health`, monitor stop channels, exec commands, log ring, metrics, and replica DB. Dependencies include daemon exec, event logging, linked env setup, container health config, and API health result types. Risks include long exec startup, cancellation races, in-memory commit failures, start-period edge cases, and goroutine lifecycle. Tests cover NONE config, state transitions/retries/start period, and empty command errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/health.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/health_test.go -->
# sources/cloud-native/moby/daemon/health_test.go

Purpose: unit tests for healthcheck state machine and probe validation.

Important APIs and control flow: `reset` installs a fresh starting health state. `TestNoneHealthcheck` verifies `initHealthMonitor` leaves `State.Health` nil when healthcheck type is `NONE`. `TestHealthStates` creates an event service and container replica DB, then drives `handleProbeResult` directly through starting, unhealthy, healthy, retries, and start-period scenarios while asserting emitted `health_status` events and failing streak values. `TestCmdProbeEmptyCommand` calls `cmdProbe.run` with `Test: []string{"CMD"}` and expects a "has no command" error before any daemon dependency is needed.

State, dependencies, and risks: tests avoid real exec by directly invoking result handling except for the empty-command validation. They depend on event channel timing and a temporary container view DB. Coverage is strong for transition rules and event emission but does not exercise monitor timers, exec startup/timeout behavior, limited output truncation, or in-memory commit failure handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/health_test.go -->
