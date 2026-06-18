# sources/cloud-native/cri-o/server/server.go

Purpose: defines the central CRI-O `Server` type, streaming service adapter, startup/shutdown lifecycle, restore/wipe behavior, sandbox/container store wrappers, exit monitoring, evented PLEG generation, registry reload watching, and artifact-store access.

Important APIs and functions: `Server`, `StreamService`, pull operation structs, `StopStreamServer`, streaming request helpers, `restore`, `Shutdown`, `getIDMappings`, `New`, `startReloadWatcher`, `useDefaultUmask`, `wipeIfAppropriate`, sandbox/container add/get/remove wrappers, `getPodSandboxFromRequest`, monitor functions, status helper functions, `generateCRIEvent`, `isNotFound`, mirror registry watcher functions, and `ArtifactStore`.

Control flow: `New` validates config, sets system context, prepares dirs, creates the container server, restores IRQ balance config, configures hostport and ID mappings, adjusts rootless env, builds artifact store and `Server`, configures max threads, redirects stdin to `/dev/null`, restores existing pods/containers, optionally wipes stale resources/images, starts streaming server, reload watchers, metrics server, seccomp notifier, NRI, and systemd watchdog. `restore` scans storage metadata, separates pods/containers, loads recoverable objects, deletes broken pods/containers and releases names, runs CNI GC, retries deleted-pod network cleanup asynchronously, and restores sandbox IPs.

State and persistence: owns runtime server state, config copy, stream server, hostport manager, monitors channel, ID mappings, event channel, pull synchronization map, resource store, seccomp notifiers, NRI API, hooks retriever, and artifact store. It mutates storage, indexes, names, network state, image store, clean-shutdown file, fsnotify watchers, metrics server, and event channel. `Shutdown` syncs graph root and optionally writes/syncs clean shutdown marker after storage shutdown.

Dependencies and integration: CRI image/runtime service interfaces, container server library, storage, CNI, hostport, streaming, TLS cert reload, fsnotify, metrics, seccomp, NRI, watchdog, runtime handler hooks, artifact storage, Kubernetes CRI types, system signals, and version wipe logic.

Risks: startup is complex and side-effect heavy; partial failures can delete storage containers or images. `restore` launches asynchronous network cleanup after startup. `generateCRIEvent` has a possible nil-status logging hazard if `getSandboxStatuses` returns error with nil status and the log references `sandboxStatuses.GetMetadata()`. Mirror registry watcher uses debounced events and a buffered channel that could block if reload processing stalls.

Test signals: this subset does not include `server_test.go`; related tests in this subset indirectly use server setup and wrappers. Many startup, restore, watcher, and shutdown paths require broader integration tests.
