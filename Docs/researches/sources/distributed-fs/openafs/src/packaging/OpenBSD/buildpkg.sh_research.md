<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/OpenBSD/buildpkg.sh -->
# sources/distributed-fs/openafs/src/packaging/OpenBSD/buildpkg.sh

## Purpose
Builds a simple OpenBSD client tarball layout from an in-tree OpenAFS build. The header notes it no longer creates a native package; instead it assembles symlinks and configuration into `openafs-client.tgz`.

## Important APIs, Types, And Functions
The shell script uses `mkdir`, `chmod`, `ln -s`, `echo`, and `tar`. It links client/admin commands (`fs`, `klog`, `pagsh`, `pts`, `tokens`, `unlog`, `vos`, `bos`), `afsd`, `libafs.o`, `postinstall`, and `afs.rc.obsd` from relative source/build locations.

## Control Flow
It removes any existing `usr` staging tree, creates `usr/vice/bin`, `usr/vice/etc`, and `usr/vice/cache`, sets cache permissions to 700, creates symlinks to built artifacts, writes `cacheinfo`, and archives the staged `usr/vice` tree. The old `pkg_create` line is commented out.

## State And Persistence
Outputs are the local `usr` staging tree and `openafs-client.tgz`. The cacheinfo inside the tarball hard-codes `/afs:/usr/vice/cache:96000`.

## Dependencies And Integration Points
This integrates OpenAFS OpenBSD build outputs into a legacy client install payload. It depends on the relative `SRC=../../../../..` layout and on target artifacts already being built.

## Risks And Test Signals
Risks include stale symlinks in the tarball if target build products are missing, no error handling, destructive `rm -rf usr`, and no package metadata. Test signals are tarball contents, symlink targets resolving in the intended build/install environment, and a manual OpenBSD client install smoke test using the generated cacheinfo and rc script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/OpenBSD/buildpkg.sh -->
