## sources/cloud-native/moby/daemon/builder/remotecontext/git/gitutils.go

**Purpose:** Implements Git URL parsing, secure clone/fetch/checkout, shallow-clone detection, submodule update, and subdirectory selection for remote build contexts.

**Important APIs/types:** `gitRepo`, `CloneOption`, `WithIsolatedConfig`, `Clone`, `clone`, `parseRemoteURL`, `getRefAndSubdir`, `fetchArgs`, `supportsShallowClone`, `checkout`, `gitWithinDir`, `isGitTransport`, and `getScheme`.

**Control flow:** `Clone` parses URL/fragments, applies options, initializes a temp repo, adds origin, fetches selected ref with optional depth, checks out branch or `FETCH_HEAD`, updates submodules, and returns either root or scoped subdirectory. HTTP shallow support is probed via smart-HTTP service discovery.

**State and persistence:** Creates a temporary `docker-build-git` directory and deletes it on error. Successful clone root is later archived and removed by caller.

**Dependencies and integration:** Uses external `git`, HTTP probing, URL parsing, symlink scope for subdir, and environment controls `GIT_PROTOCOL_FROM_USER=0`, `GIT_CONFIG_NOSYSTEM=1`, `HOME=/dev/null`.

**Risks:** Remote URL/ref handling is command-injection-sensitive; refs starting with `-` are rejected and fetch uses `--`. File protocol is disabled for submodules. HTTP probing performs network requests. Subdir symlinks must stay within repo root.

**Test signals:** `gitutils_test.go` covers URL parsing, shallow args, checkout/subdir/submodule behavior, transport detection, and invalid refspecs.
