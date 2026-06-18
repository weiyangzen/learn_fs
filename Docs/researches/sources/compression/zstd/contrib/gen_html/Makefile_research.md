# sources/compression/zstd/contrib/gen_html/Makefile

Purpose: build and run the zstd API manual HTML generator.

Important behavior: compiles `gen_html.cpp` with C++ warning flags, derives library version components from `../../lib/zstd.h` using `sed`, and generates `../../doc/zstd_manual.html` by invoking `./gen_html$(EXT) $(LIBVER) $(ZSTDAPI) $(ZSTDMANUAL)`. `manual` depends on the generator and output; `clean` removes the executable.

State, dependencies, and integration: state is the local `gen_html` binary and generated manual under `doc`. It integrates with top-level `make manual` and release-check workflow.

Risks and test signals: version extraction depends on exact macro formatting in `zstd.h`. Generator output must be deterministic, because release checks compare regenerated manual against committed HTML. Windows extension handling is included but shell tooling remains POSIX-like.
