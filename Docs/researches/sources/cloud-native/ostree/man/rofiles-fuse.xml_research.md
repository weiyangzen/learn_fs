# sources/cloud-native/ostree/man/rofiles-fuse.xml

Purpose: This DocBook refentry documents `rofiles-fuse`, a FUSE helper that exposes a view where directories can be changed but existing files are immutable. It protects hardlink-based OSTree checkouts from accidental in-place file mutation.

Important commands and behavior: The command syntax is `rofiles-fuse SRCDIR MNTPOINT`. The documented workflow mounts a checkout, lets arbitrary tools create, delete, or replace entries through the mount, unmounts with `fusermount -u`, and commits with `ostree commit --link-checkout-speedup`.

Control flow and state: Runtime state is a FUSE mount projecting changes back to the source directory while preventing mutation of existing file content. Persistent state is the changed checkout directory and the subsequent OSTree commit. It is especially intended for package script execution where writes must not corrupt repository hardlinks.

Dependencies and integration points: Depends on FUSE, `fusermount`, OSTree checkout hardlink behavior, and commit acceleration through `--link-checkout-speedup` or equivalent API. It bridges arbitrary filesystem mutating tools with OSTree's immutable object-store assumptions.

Risks: Mount lifecycle is critical; failing to unmount before committing or cleanup can leave confusing state. The helper protects file immutability but still permits directory-level operations, so tests must ensure replacements break hardlinks rather than mutate them. User documentation should make clear this is not a general sandbox.

Test signals: Manual tests should check that writes to new files, directory creation, deletion, and replacement are reflected in `SRCDIR`; direct mutation of original file content must fail or become a safe replacement; and commits with `--link-checkout-speedup` remain valid under `ostree fsck`.
