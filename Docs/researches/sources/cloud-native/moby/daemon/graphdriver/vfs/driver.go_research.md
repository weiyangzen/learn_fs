# sources/cloud-native/moby/daemon/graphdriver/vfs/driver.go

Purpose: portable VFS graphdriver that stores each layer as a plain directory and copies parent contents for layering.

Important APIs and control flow: `Init` parses options, creates the home directory, initializes quota support, rejects configured size when unsupported, and returns a `NaiveDiffDriver` with optional best-effort xattrs. `parseOptions` supports `size` and the explicit unsafe `vfs.xattrs=i_want_broken_containers` opt-in. `CreateReadWrite` applies per-layer size storage options when quota is supported. `Create` rejects storage opts for read-only layers. `create` makes `home/dir/<id>`, optionally applies quota, sets SELinux level label, and if a parent exists copies its directory with `CopyDir`. `Get`, `Put`, `Remove`, `Exists`, and `GetMetadata` are directory operations.

State, dependencies, and risks: persistent state is plain directories under `home/dir`. Dependencies include copy helpers, quota support, SELinux labels, ID mapping, and naive diff. VFS has no copy-on-write, so child creation is slow and space-heavy. Best-effort xattrs is intentionally dangerous and surfaced in status. Tests cover graphtest behavior, quota, and xattr unsupported handling.
