# sources/cloud-native/cri-o/pinns/Makefile

Purpose: builds the `pinns` helper binary from C sources and installs it under `../bin/pinns`.

Important APIs/types/functions: derives `src` and `obj` from `src/*.c`, sets `STRIP`, `LIBS`, and default `CFLAGS`, defines `all`, binary link, object compile, `../bin` creation, and `clean` targets.

Control flow: object files compile from C sources, the binary target links them with configured flags, strips symbols, and creates `../bin` as needed.

State and persistence: produces `.o` files beside sources and `../bin/pinns`; `clean` removes those artifacts.

Dependencies/integration: requires a C compiler and `strip`. CRI-O runtime config validates `pinns` on Linux and namespace management uses the resulting executable.

Risks: default `CFLAGS` include `-static`, `-Werror`, and `-O3`, so portability depends on static libc/toolchain support and warning cleanliness. `HEADERS` is referenced but not defined, so header dependencies may not trigger rebuilds unless supplied by the caller.

Test signals: build success of `../bin/pinns` is the primary signal; there are no unit tests in this subset for the C helper.
