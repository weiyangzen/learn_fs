# sources/cloud-native/cri-o/internal/config/nsmgr/nsmgr_freebsd.go

Purpose: implements a minimal FreeBSD namespace manager focused on jail/network namespace placeholders.

Important APIs/types/functions: `NamespaceManager` stores `namespacesDir` and `pinnsPath`; `New`, `Initialize`, `NewPodNamespaces`, `NamespacePathFromProc`, and `NamespaceFromProcEntry`.

Control flow: `Initialize` creates the namespace root directory. `NewPodNamespaces` rejects nil configs, returns an empty slice for no namespaces, and otherwise returns a `namespace` object for each non-host namespace using the namespace type string as the jail name. Host namespaces are skipped. `NamespacePathFromProc` always returns an empty string, and `NamespaceFromProcEntry` reports that proc-entry pinning is unsupported.

State and persistence behavior: creates `namespacesDir` with mode `0755`; namespace objects are in-memory and do not bind mount or persist real namespace files.

Dependencies/integration points: FreeBSD build variant sharing the common `nsmgr` API used by sandbox/container setup.

Risks: functionality is intentionally much thinner than Linux. `pinnsPath` is stored but unused. Host namespace skipping and synthetic jail names may need expansion for richer FreeBSD support.

Test signals: no direct FreeBSD tests in this subset.
