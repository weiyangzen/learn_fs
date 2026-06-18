# sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_linux.go

Purpose: manages Linux namespace lifecycle for pods by preparing namespace directories, invoking `pinns`, and pinning namespaces from existing process entries.

Important APIs/types/functions: `NamespaceManager` with `namespacesDir` and `pinnsPath`; `New`, `Initialize`, `NewPodNamespaces`, `chownDirToIDPair`, `getMappingsForPinns`, `NamespaceFromProcEntry`, `dirForType`, and `NamespacePathFromProc`.

Control flow: `Initialize` creates the root directory and subdirectories for supported namespace types, replacing files that block directory creation. `NewPodNamespaces` validates config, builds pinns arguments from requested namespace types, host mode, sysctls, and optional ID mappings, precomputes pin paths, optionally chowns pin directories, invokes `pinns`, cleans up mount points on failure, and returns `Namespace` handles from the generated paths. `NamespaceFromProcEntry` creates a pin file, validates `/proc/<pid>/ns/<type>`, bind-mounts it, and returns a namespace wrapper, cleaning up on errors.

State and persistence behavior: persists namespace bind-mount paths under `namespacesDir/<type>ns/<uuid>`. It may chown paths to mapped root IDs. Removal is delegated to namespace objects in `types_linux.go`.

Dependencies/integration points: uses CNI ns package, Google UUID, logrus, storage idtools, unix mount/unmount, CRI-O `utils`, and `cmdrunner`. Integrates with pod sandbox creation and container namespace sharing.

Risks: namespace path checks are inherently racy with infra container PID lifetime. Failure cleanup must unmount partially created paths. Mapping format must match `pinns` expectations. `typeToArg` omits PID namespace creation in this function, so unsupported types fail.

Test signals: no direct tests here; `nsmgr/test/utils.go` supplies spoofed namespace helpers for other tests.
