## sources/cloud-native/moby/daemon/builder/remotecontext/git/gitutils_test.go

**Purpose:** Tests Git remote context parsing, fetch arguments, checkout behavior, submodule handling, transport detection, and ref validation.

**Important APIs:** `TestParseRemoteURL`, shallow clone argument tests, `TestCheckoutGit`, `TestValidGitTransport`, and `TestGitInvalidRef`.

**Control flow:** Tests use HTTP test servers and `git http-backend` to create smart/dumb Git scenarios, initialize repos/submodules, exercise refs and subdirs, and assert checked-out Dockerfile contents or failures.

**State and persistence:** Creates temporary Git repositories, commits, branches, submodules, and server state under test temp dirs.

**Dependencies and integration:** Requires a working `git` binary. It validates security controls around refspec parsing and path scoping.

**Risks:** Some symlink cases are skipped on Windows. Network behavior is local test-server based and may not cover all real Git hosting quirks.

**Test signals:** Strong integration-level signal for the Git context utility, including submodule and smart HTTP behavior.
