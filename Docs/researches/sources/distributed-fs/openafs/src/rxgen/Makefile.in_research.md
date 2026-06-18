# sources/distributed-fs/openafs/src/rxgen/Makefile.in

## Purpose
`rxgen/Makefile.in` builds and installs `rxgen`, the OpenAFS RPC/RX code generator, and installs `rxgen_consts.h`.

## Important APIs, Types, and Functions
- Source/object lists cover `rpc_main.c`, `rpc_hout.c`, `rpc_cout.c`, parser/scanner, and utility modules.
- Targets: `all`, `buildtools`, `rxgen`, generated include install, `install`, `dest`, and `clean`.
- `CFLAGS_rpc_main.o` injects `PATH_CPP`.

## Control Flow
The build includes OpenAFS config and LWP make fragments, builds rxgen from its object set plus component version, copies `rxgen_consts.h` into the top include dir, and installs binaries/includes to configured or DEST paths.

## State and Persistence
Build artifacts include `rxgen`, object files, and `AFS_component_version_number.c`. Install targets persist `rxgen` and the public constants header.

## Dependencies and Integration Points
`rxgen` is a build tool used by RX interface make rules throughout OpenAFS, including generator-produced tests. The makefile integrates with `Makefile.version`.

## Risks and Edge Cases
The generator's correctness depends on scanner/parser modules outside this subset. If `PATH_CPP` is wrong, `rpc_main.c` preprocessing fails for normal inputs.

## Test Signals
`make rxgen`, `make buildtools`, installation into staged directories, and generation of a known `.xg` into `.h`, `.xdr.c`, `.cs.c`, and `.ss.c`.
