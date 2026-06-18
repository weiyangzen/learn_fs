## sources/cloud-native/moby/daemon/builder/dockerfile/copy_windows.go

**Purpose:** Provides Windows-specific ADD/COPY permissions, destination normalization, wildcard detection, and restrictions on copying from sensitive system paths.

**Important APIs:** `pathDenyList`, `fixPermissions`, `fixPermissionsReexec`, `fixPermissionsWindows`, `normalizeDest`, `containsWildcards`, and `validateCopySourcePath`. Permission changes run via a reexec helper and Windows security descriptors/SIDs.

**Control flow:** `fixPermissions` runs `windows-fix-permissions` when a SID is present. `normalizeDest` rejects non-`C:` destinations, strips drive letters, resolves relative paths under system-drive WORKDIR, and preserves trailing separators. `validateCopySourcePath` denies `c:\` and `c:\windows` when copying from image sources.

**State and persistence:** Mutates ACL/owner metadata on copied destination paths. Registers a reexec command at init time.

**Dependencies and integration:** Uses go-winio privileges, Windows syscalls, reexec, system SDDL constants, and common copy logic.

**Risks:** Windows ACL handling requires elevated privileges and correct SID mapping. Destination drive rules are compatibility-sensitive. Deny-list normalization must catch drive-relative oddities such as `c:.`.

**Test signals:** `internals_windows_test.go` covers `normalizeDest`; broader ACL and deny-list behavior likely needs Windows integration tests.
