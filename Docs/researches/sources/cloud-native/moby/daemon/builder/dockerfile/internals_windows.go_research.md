## sources/cloud-native/moby/daemon/builder/dockerfile/internals_windows.go

**Purpose:** Implements Windows-specific `--chown` handling by mapping account names or SIDs to Windows SIDs for ADD/COPY.

**Important APIs:** Constants for `SeTakeOwnershipPrivilege`, `ContainerAdministrator`, and `ContainerUser` SIDs; `parseChownFlag`, `getAccountIdentity`, and `lookupNTAccount`.

**Control flow:** For Windows target platform, chown is interpreted as an account/SID. Direct SID strings are validated, built-in aliases/well-known groups use host lookup results, container-specific names are mapped to constants, and remaining names are resolved by running `containerutility.exe getaccountsid` inside a temporary container with a bind mount.

**State and persistence:** Returns an `identity` with SID for later ACL application. Creates/runs a temporary helper container for dynamic account lookup.

**Dependencies and integration:** Uses Windows syscalls, platform parsing, container manager, bind mounts, JSON stream errors, and copy permission code.

**Risks:** Helper-container lookup depends on `containerutility.exe` path and container runtime behavior. Host vs container account resolution must not confuse identities. Non-Windows platform option returns root UID/GID instead.

**Test signals:** Adjacent Windows tests cover destination normalization, not SID lookup. Integration tests are needed for built-in and container-local account chown.
