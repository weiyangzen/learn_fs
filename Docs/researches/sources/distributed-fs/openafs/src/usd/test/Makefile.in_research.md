
# sources/distributed-fs/openafs/src/usd/test/Makefile.in

This makefile builds the `usd_test` executable against the top-level `libusd.a`. It includes OpenAFS config and LWP make settings, sets include paths for the destination include tree and parent directory, and defines `test`/`tests` as aliases depending on the binary.

The main build rule links `usd_test.o` with `LIBUSD` and platform libraries. `clean` removes objects, executable, core files, and component version output.

Risks are mostly dependency freshness: `usd_test` depends on installed/copied `afs/usd.h` and `libusd.a`, so partial builds can fail if the parent library was not built first. Test signals are successful compile/link and manual execution against a tape-capable device.
