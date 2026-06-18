# sources/cloud-native/ostree/src/libostree/ostree-repo-finder-mount.c

Purpose: implements the removable-volume `OstreeRepoFinder` backend, scanning mounted volumes for OSTree repositories and resolving requested collection refs to local `file://` remotes.

Important APIs/types/functions: defines final `OstreeRepoFinderMount` with construct-only `monitor` property and exports `ostree_repo_finder_mount_new`. Core helpers include `scan_repo`, `scan_and_add_repo`, `RepoAndRefs`, `UriAndKeyring`, and `ostree_repo_finder_mount_resolve_async/finish`.

Control flow: resolution enumerates mounts from a `GVolumeMonitor`, skips shadowed/system mounts, opens mount roots, and records the mount device. It scans `.ostree/repos.d` in lexical order, then well-known fallback paths `.ostree/repo`, `ostree/repo`, and `var/lib/flatpak/repo`. Each candidate is opened with `ostree_repo_open_at`, rejected if it resolves outside the mounted filesystem or equals the parent repo, and queried for local collection refs. For each requested ref, the first matching repo on a mount is grouped by canonical `file://` URI plus keyring remote, then emitted as a dynamic remote result with priority `50`.

State and persistence: instance state is only the owned `GVolumeMonitor`. Resolution opens repositories and builds temporary result maps; it does not alter repository configuration. Dynamic remotes carry URL, keyring, `gpg-verify=true`, and `gpg-verify-summary=false`.

Dependencies/integration: depends on GIO volume/mount APIs, GLib Unix mount filtering, libglnx fd helpers, OSTree repo open/list refs APIs, remote keyring resolution, and the shared finder interface. `ostree-repo-pull.c` creates it for the configured `mount` finder, and `tests/test-create-usb.sh` exercises mount-discovery behavior.

Risks: symlinks are followed, so the same-device check is critical to prevent repos outside the removable volume from being used. Canonicalization uses `realpath`; missing paths or permission errors simply skip candidates. System mount filtering depends on GLib availability/version. The “first repo per ref per mount” rule trades completeness for avoiding redundant parallel pulls.

Test signals: integration is referenced by `tests/test-create-usb.sh`; broader finder behavior is also exercised through pull/find-remotes tests. Unit coverage for mount edge cases is limited because it depends on system mount state.
