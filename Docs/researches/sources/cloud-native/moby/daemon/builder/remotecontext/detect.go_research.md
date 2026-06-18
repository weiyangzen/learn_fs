## sources/cloud-native/moby/daemon/builder/remotecontext/detect.go

**Purpose:** Detects and constructs the build context and Dockerfile parser result from local archive, Git URL, remote URL, or unsupported client-session source.

**Important APIs:** `ClientSessionRemote`, `Detect`, `newArchiveRemote`, `withDockerfileFromContext`, `newGitRemote`, `newURLRemote`, `removeDockerfile`, `readAndParseDockerfile`, `openAt`, `StatAt`, and `FullPath`.

**Control flow:** `Detect` switches on `RemoteContext`. Archive/git/archive-URL paths create a modifiable context, open/parse Dockerfile, and remove Dockerfile/.dockerignore if ignored. Plain-text URL content is parsed as Dockerfile without a build context. Missing default `Dockerfile` falls back to lowercase.

**State and persistence:** May mutate the extracted build context by removing `.dockerignore` and Dockerfile entries before build. Temporary context lifecycle belongs to returned source.

**Dependencies and integration:** Uses BuildKit parser, URL utilities, Git remote context, ignorefile/patternmatcher, symlink scope, and buildbackend config/progress reader.

**Risks:** Dockerfile path handling must prevent escape from context. Removal semantics depend on .dockerignore matching. Client session is explicitly rejected for v1 builder. Plain text remote Dockerfiles have no build context, so COPY should fail.

**Test signals:** `detect_test.go` covers removeDockerfile behavior. Internals tests cover missing/empty/symlink/outside Dockerfile handling.
