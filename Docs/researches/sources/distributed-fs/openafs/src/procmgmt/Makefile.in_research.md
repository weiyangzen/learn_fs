# sources/distributed-fs/openafs/src/procmgmt/Makefile.in

## Purpose
Builds and installs the OpenAFS process-management library and public process/signal compatibility headers.

## Important APIs, Types, And Functions
Targets build `${TOP_LIBDIR}/libprocmgmt.a`, install `${TOP_INCDIR}/afs/procmgmt.h`, and install `${TOP_INCDIR}/afs/procmgmt_softsig.h`. `libprocmgmt.a` is assembled from `procmgmt_unix.o` and `AFS_component_version_number.o` in this Unix build path. `buildtools` exposes only the public header.

## Control Flow
`all` ensures the library and headers are available in top-level build output. `install` stages the library under `${libdir}/afs` and headers under `${includedir}/afs`; `dest` mirrors that into `${DEST}/lib/afs` and `${DEST}/include/afs`. `clean` removes local archive/object/version artifacts.

## State And Persistence
Build artifacts are `libprocmgmt.a`, object files, and generated component version source. Install/dest persist a static library and public headers for other OpenAFS components.

## Dependencies And Integration Points
Includes OpenAFS config and LWP make fragments. The Unix archive exposes spawn wrappers used by portable OpenAFS code, while NT-specific sources are present for Windows builds outside this Unix make path.

## Risks And Test Signals
Risks include platform divergence between Unix and NT implementations and consumers expecting NT-only APIs from a Unix archive. Test signals are archive creation, header installation, and successful consumers using `spawnprocve`/`spawnprocv`.
