# sources/compression/zstd/contrib/largeNbDicts/Makefile

Purpose: build recipe for the `largeNbDicts` benchmark tool, including shared program utility objects.

Important behavior: includes zstd lib/common/dictBuilder and programs headers, uses GNU99 with broad warning flags, builds `largeNbDicts` from local C plus `util.o`, `timefn.o`, `benchfn.o`, `datagen.o`, `xxhash.o`, and `libzstd.a`. Utility objects are compiled from `../../programs`, xxhash from `../../lib/common`, and libzstd via delegated make. `clean` removes local objects, cleans the lib directory, and deletes the executable.

State, dependencies, and integration: local objects/executable and `../../lib/libzstd.a` are build state. It integrates benchmark helper APIs, dictionary builder APIs, and static zstd.

Risks and test signals: cleaning the shared lib can disrupt parallel builds. Build coverage through top-level `contrib` catches compile drift; benchmark correctness is mostly manual/runtime.
