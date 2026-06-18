# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-mount.h

Purpose: declares the public final `OstreeRepoFinderMount` type for repository discovery on mounted removable volumes.

Important APIs/types/functions: exposes `OSTREE_TYPE_REPO_FINDER_MOUNT`, `G_DECLARE_FINAL_TYPE`, and `ostree_repo_finder_mount_new(GVolumeMonitor *monitor)`.

Control flow: callers optionally inject a volume monitor for tests or specialized environments, then resolve through the generic `OstreeRepoFinder` methods. The implementation fills in the default system monitor during construction when `NULL` is passed.

State and persistence: no public state; the private object stores only the volume monitor and builds results on each resolve. No repo configuration is persisted.

Dependencies/integration: includes GIO/GObject and finder/type headers. Used by default pull remote discovery when `mount` is included in the repo-finders configuration.

Risks: the header exposes only construction, so monitor lifetime and mount filtering details are implementation concerns. Consumers must handle zero results on systems without suitable mounts.

Test signals: behavior is integration-tested through USB/mount scenarios rather than this header directly.
