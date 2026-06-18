# sources/distributed-fs/openafs/src/rxdebug/Makefile.in

## Purpose
`rxdebug/Makefile.in` builds and installs the RX diagnostic utilities `rxdebug` and `rxdumptrace`.

## Important APIs, Types, and Functions
- Build targets: `all`, `rxdebug`, `rxdumptrace`, `install`, `dest`, and `clean`.
- `LT_deps` links command, util, and RX libtool libraries.
- `rxdumptrace.o` is compiled from `../rx/rx_trace.c` with `-DDUMPTRACE`.

## Control Flow
The build includes OpenAFS config and pthread make fragments, compiles objects, links static utilities with roken and thread libs, installs `rxdebug` to system bindirs or DEST staging, and cleans generated objects/binaries/version files.

## State and Persistence
Build outputs are `rxdebug`, `rxdumptrace`, objects, and generated component-version files. Install targets persist `rxdebug` under `${sbindir}` or `${DEST}/etc`.

## Dependencies and Integration Points
Integrates with top-level OpenAFS Autoconf substitutions, libtool rules, RX libraries, and `Makefile.version`.

## Risks and Edge Cases
Only `rxdebug` is installed; `rxdumptrace` is built by `all` but not installed by these targets. Static link dependencies must match the RX library ABI and thread model.

## Test Signals
`make rxdebug rxdumptrace`, `make install DESTDIR=...`, and `make clean` are the primary build signals.
