# sources/cloud-native/ostree/man/ostree-create-usb.xml

Purpose: documents `ostree create-usb`, which creates a repository on removable media and pulls selected collection/ref pairs for offline or peer-to-peer distribution.

Important APIs/types: required `MOUNT-PATH` and one or more `COLLECTION-ID REF` pairs; options include destination repository placement and repo mode/collection-id behavior described in the page.

Control flow: initializes or uses a repository on the mount path, pulls requested refs into it, creates standard discovery symlinks when needed, and regenerates the destination summary.

State and persistence: writes repository objects, refs, summary metadata, and possible `.ostree/repos.d` symlinks on the external drive.

Dependencies and integration: integrates P2P collection IDs, `ostree-find-remotes`, local/remote pull machinery, repository modes, and mounted filesystem discovery paths.

Risks and test signals: risks include globally unique collection-id requirements, stale summaries, symlink discovery mismatch, and removable media permissions. Signals are USB repo discovery tests, summary validation, and pulling from the created media.
