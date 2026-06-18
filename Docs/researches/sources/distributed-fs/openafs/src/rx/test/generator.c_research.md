# sources/distributed-fs/openafs/src/rx/test/generator.c

## Purpose
`generator.c` is phase 2 of an RX stress-test generator. It reads signature descriptions, normally produced by `tableGen.c`, and emits a batch of `.xg` rxgen interface files, generated client/server C files, per-batch makefiles, and a top-level Makefile. The generated programs make deterministic random RPC calls and verify parameter marshalling for pthread or LWP RX builds.

## Important APIs, Types, and Functions
- Uses `rpcArgs` and `arg_tuple` from `generator.h` as the in-memory model for one RPC signature.
- `drand32()` is a deterministic 32-bit linear-congruential RNG, intentionally stable across platforms.
- `ProcessCmdLine()` accepts `-f`, `-s`, `-o`, `-p`, `-l`, and help flags; `-p NT` selects Windows make/include fragments, other values select Unix fragments.
- `GenParamValues()` fills every argument descriptor with stringified input/output test values for scalar, string, and fixed-size array types.
- `WriteXG*()`, `WriteServ*()`, `WriteClt*()`, and `WriteMake()` emit the generated source and build files.
- `main()` reads each signature, rotates output files every `TESTS_PER_FILE`, writes matching RPC/interface/client/server fragments, frees generated strings, and writes a top-level Makefile.

## Control Flow
Startup parses the command line, opens the input table, creates the first output file set, and emits headers. The read loop parses an argument count followed by `( direction type )` pairs, allocates an `arg_tuple` array, initializes all value pointers to `NULL`, calls `GenParamValues()`, and emits one normal RPC plus one struct-wrapper RPC. When the signature count reaches `TESTS_PER_FILE`, it closes the current generated files with trailers, opens a new numbered set, and continues. The final path writes trailers, closes everything, and emits a driver Makefile that invokes each numbered makefile.

## State and Persistence
Persistent output is entirely file based: generated `.xg`, `Clt.c`, `Srv.c`, `.mak`, and `Makefile` artifacts. Runtime state is process-local: global platform symbol tables, global `threadModel`, and global deterministic `randVal`. The deterministic RNG means the same input signatures produce the same generated values and checks if file ordering and platform selection are unchanged.

## Dependencies and Integration Points
The generator targets OpenAFS RX and rxgen conventions. Generated clients use RX, rxnull, rxkad, cmd parsing, optional pthread/LWP threading, and fixed test service id `4`. Generated servers create RX services with rxnull and rxkad security classes. The emitted makefiles depend on platform-specific OpenAFS library names and on `$(RXGEN)`.

## Risks and Edge Cases
The code uses large format strings and manual string allocation; several buffers are fixed size by constants in `generator.h`. `ProcessCmdLine()` mutates `serverName` in place to truncate it, which assumes argv storage is writable. Some generated code casts thread arguments through `int`, which is pointer-width fragile. The generated `CHECKfloat`/`CHECKdouble` macros compare ratios and can misbehave around zero, although generated random values are positive. `GetRandP()` has a char quoting path where `ret` is not populated for backslash/single-quote cases, leaving behavior dependent on `ret2` users.

## Test Signals
The test signal is the generated client/server pair itself: servers validate incoming `IN` and `INOUT` values and set `OUT` values; clients validate returned values across both normal argument lists and struct wrapper calls. Build signals come from successful rxgen output and generated makefiles for pthread/LWP and Unix/NT variants.
