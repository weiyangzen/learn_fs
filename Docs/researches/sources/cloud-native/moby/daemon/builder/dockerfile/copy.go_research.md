## sources/cloud-native/moby/daemon/builder/dockerfile/copy.go

**Purpose:** Implements shared ADD/COPY source resolution, hashing, URL download, wildcard expansion, and filesystem copy/decompression logic for the classic builder.

**Important APIs/types:** `copyInfo`, `copyInstruction`, `copier`, `copierFromDispatchRequest`, `createCopyInstruction`, `calcCopyInfo`, `copyWithWildcards`, `copyInfoForFile`, `walkSource`, `sourceDownloader`, `downloadSource`, `identity`, `copyFileOptions`, `performCopyForInfo`, `copyDirectory`, `copyFile`, and `isExistingDirectory`.

**Control flow:** A dispatcher builds a `copier`, source paths become `copyInfo` records from context, image mount, or downloaded URL. Wildcards walk the source tree. File sources hash with `source.Hash`; directories hash sorted child hashes. Copy execution resolves source/destination through symlink scope, copies directories or files with tar helpers, and optionally untars local archives for ADD.

**State and persistence:** Per-build path cache stores image-source hashes by image ID plus path. URL downloads create temporary directories cleaned by `Cleanup`. Copy writes to an RW layer that is later committed by `performCopy`.

**Dependencies and integration:** Uses remotecontext, URL utilities, progress output, longpath temp dirs, go-archive archiver, symlink scope helpers, user chown helpers, and platform-specific `normalizeDest`/`fixPermissions`.

**Risks:** This is security-sensitive for path traversal, symlinks, remote downloads, archive decompression, permission ownership, and cache correctness. Missing `Cleanup` leaks temp dirs/RW layers. Directory hash order must remain deterministic.

**Test signals:** `copy_test.go` covers directory existence and download filename inference; platform files add path behavior. Full ADD/COPY behavior needs integration coverage for .dockerignore, wildcard matching, remote URLs, archive extraction, and COPY --from.
