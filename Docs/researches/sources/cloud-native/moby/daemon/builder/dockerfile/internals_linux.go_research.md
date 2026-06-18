## sources/cloud-native/moby/daemon/builder/dockerfile/internals_linux.go

**Purpose:** Implements Linux/Unix `--chown` parsing for ADD/COPY.

**Important APIs:** `parseChownFlag`, `lookupUser`, and `lookupGroup`. The parser accepts `user`, `user:group`, numeric IDs, and names looked up in container `/etc/passwd` and `/etc/group`, then maps IDs through user namespace identity mapping.

**Control flow:** `parseChownFlag` splits on colon, defaults group to user when omitted, resolves passwd/group paths with symlink scope inside container rootfs, resolves IDs/names, then converts to host UID/GID.

**State and persistence:** No persistent state; returns an `identity` used by copy code to chown files in the RW layer.

**Dependencies and integration:** Uses `moby/sys/user`, symlink scope checks, and user namespace mapping from builder.

**Risks:** Path resolution for `/etc/passwd` and `/etc/group` is security-sensitive. Missing user/group produces user-facing build errors. Namespace mapping errors must not be ignored.

**Test signals:** `internals_linux_test.go` covers chown parsing behavior and lookup combinations.
