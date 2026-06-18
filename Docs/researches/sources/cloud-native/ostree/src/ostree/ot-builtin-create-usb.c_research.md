# sources/cloud-native/ostree/src/ostree/ot-builtin-create-usb.c

## Purpose
Implements `ostree create-usb`, which mirrors selected collection-ref pairs from the current repository to a repository located on a mounted removable device. It creates an archive-mode destination repo if needed and prepares it for later discovery by mount-based repo finders.

## Important APIs, Types, And Functions
`ostree_builtin_create_usb()` drives the command. It validates `OstreeCollectionRef` inputs, creates/open the destination with `ostree_repo_create_at()`, pulls with `ostree_repo_pull_with_options()`, regenerates summary metadata with `ostree_repo_regenerate_summary()`, and may create `.ostree/repos.d` symlinks. It uses `glnx_opendirat()`, fd-relative mkdir/symlink calls, `OstreeAsyncProgress`, and `OSTREE_REPO_PULL_FLAGS_MIRROR`.

## Control Flow
The command requires a mount path and at least one complete `COLLECTION-ID REF` pair. `--commit` is allowed only for a single pair. It opens the mount root, records its device, validates refs, creates the destination path under the mount root, creates an archive repo, confirms the destination is on the same device and not the source repo, marks it writable, and applies optional fsync disabling. It builds a `collection-refs` pull option containing collection ID, ref name, and optional commit override, then mirror-pulls from the source repository URI. On pull failure it aborts the destination transaction. After a successful pull, it regenerates summary metadata and creates a symlink under `.ostree/repos.d` for non-standard repo locations if one is not already present.

## State And Persistence
The command writes a destination OSTree repository under the mount, including objects, refs, summary metadata, and optional discovery symlinks. It does not alter source repo content. The destination is archive mode to support filesystems without Unix xattrs and to compress content for removable media.

## Dependencies And Integration Points
It integrates with collection-ref validation, local `file://` pulls, mount repository discovery (`OstreeRepoFinderMount`), summary consumers, and console progress. It depends on `ostree-remote-private.h` data types and libglnx fd-relative filesystem utilities.

## Risks And Edge Cases
The destination must be a descendant of the mount path by device check, which prevents accidentally writing elsewhere but may reject unusual bind-mount layouts. Symlink creation tries 100 generated names and then fails. The success message assumes all requested refs were copied because pull failures abort the operation. Summary regeneration is currently required due to finder assumptions documented in the file.

## Test Signals
Tests should verify argument validation, single-commit override rules, destination-not-source protection, same-device descendant enforcement, archive repo creation, copied collection refs, summary presence, generated symlink behavior for custom repo paths, and operation on non-xattr-capable media.
