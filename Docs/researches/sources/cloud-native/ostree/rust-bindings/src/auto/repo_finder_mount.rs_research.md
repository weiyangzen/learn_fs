# sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_mount.rs

## sources/cloud-native/ostree/rust-bindings/src/auto/repo_finder_mount.rs

Generated object wrapper for `OstreeRepoFinderMount`, a concrete `RepoFinder` implementation for locating OSTree repositories on mounted media. It exposes `new(mount_root: Option<&gio::File>)`.

Control flow only converts the optional `gio::File` mount root and calls `ostree_repo_finder_mount_new`. Discovery, mount traversal, and result creation live in libostree. State is object configuration plus external mounted filesystems; this file does not persist anything.

Dependencies include `gio::File`, `RepoFinder`, and GLib translation traits. Risks are environmental: mount visibility, permissions, removable media layout, and object lifetime. No local tests are present.
