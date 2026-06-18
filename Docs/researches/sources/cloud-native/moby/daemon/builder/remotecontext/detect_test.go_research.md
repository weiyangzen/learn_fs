## sources/cloud-native/moby/daemon/builder/remotecontext/detect_test.go

**Purpose:** Tests `.dockerignore`-driven removal of Dockerfile and `.dockerignore` from modifiable build contexts.

**Important APIs:** Helpers inspect directories and invoke `removeDockerfile` using a `stubRemote` implementing source/remove methods.

**Control flow:** Tests create context directories, write ignore files, execute removal, and compare remaining filenames.

**State and persistence:** Temporary filesystem state only.

**Dependencies and integration:** Protects `withDockerfileFromContext` cleanup behavior used after parsing Dockerfile.

**Risks:** Does not cover remote URL/Git detection, Dockerfile parsing errors, or symlink-scoped `FullPath`.

**Test signals:** Direct signal for whether ignored Dockerfile/.dockerignore files are removed from the context before build instructions can copy them.
