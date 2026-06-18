# subset-b-007798 Research

Grouped research report for the OpenAFS RX test, XDR, rxdebug, and rxgen sources in work item `subset-b-007798`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/generator.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/generator.h -->
# sources/distributed-fs/openafs/src/rx/test/generator.h

## Purpose
`generator.h` defines the constants, utility macros, and data structures shared by `generator.c` for RX generated-test creation.

## Important APIs, Types, and Functions
- `arg_tuple` describes one RPC argument: direction, type, optional attributes, generated input/output value strings, and array bounds.
- `rpcArgs` wraps an argument count and a dynamically allocated `arg_tuple` vector.
- Constants such as `TESTS_PER_FILE`, `IDL_STR_MAX`, `IDL_FIX_ARRAY_SIZE`, `MAX_SERV_NAME`, and string-length limits drive both parser assumptions and generated code shape.
- `MEM_CHK`, `FATAL`, `PrintShortUsage`, and `PrintLongUsage` centralize fail-fast behavior and CLI help text.

## Control Flow
This header has no runtime control flow, but its constants control `generator.c` batching, allocation sizes, and generated IDL dimensions.

## State and Persistence
The header defines only compile-time state. The value pointer arrays in `arg_tuple` imply ownership by `generator.c`, which allocates and frees generated strings per signature.

## Dependencies and Integration Points
Included directly by `generator.c`; its schema must match `tableGen.c` output vocabulary (`IN`, `OUT`, `INOUT`, scalar and array type names) and generated rxgen type names.

## Risks and Edge Cases
Many field sizes are hard-coded. New direction/type strings must fit `MAX_DIR_STR` and `MAX_TYP_STR`; otherwise `fscanf("%s")` in `generator.c` can overflow. `IDL_FIX_ARRAY_SIZE` and array value pointer counts must remain aligned.

## Test Signals
Compile success of `generator.c` and successful generation/parsing of all table signatures are the main signals. Mismatched constants show up as malformed generated `.xg` or C output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/kctest.c -->
# sources/distributed-fs/openafs/src/rx/test/kctest.c

## Purpose
`kctest.c` is a simple RX client benchmark/regression tool. It connects to an RX test server, sends a single XDR-encoded long value, decodes the response, and measures average call latency.

## Important APIs, Types, and Functions
- `ParseCmd()` handles `-port`, `-host`, `-count`, `-security`, `-log`, and `-stats`.
- `SigInt()` prints RX stats, finalizes RX, and exits.
- `nowms()` provides coarse millisecond timing.
- `main()` initializes RX, creates an rxnull security object, creates a connection, loops over `count` calls, and uses `xdrrx_create()` plus `xdr_long()`.

## Control Flow
Defaults target localhost port 10000 with one unauthenticated call. After parsing, the client initializes RX with an ephemeral local port, creates an rxnull client security class, and constructs a connection to service id `1`. Each iteration creates a call, encodes `1988`, switches the same `XDR` object to decode mode, reads the returned value, expects `1989`, ends the call, and finally prints timing.

## State and Persistence
State is held in static globals for host, port, count, security level, and stats mode. Optional persistent output is `kctest.log` assigned to `rx_debugFile`.

## Dependencies and Integration Points
Depends on RX core, RX globals, rxnull, and XDR-over-RX (`xdrrx_create`). It pairs with `kstest.c`, whose server increments the decoded long value.

## Risks and Edge Cases
Only security level 0 is accepted. `count` is a `short`, so large counts truncate. The code calls `SigInt(0)` at normal completion, which exits with status 1 after finalization. Host and port are stored in network order after parsing; defaults are already network-ordered.

## Test Signals
Expected signal is `wrong value returned` never appearing and a printed average milliseconds-per-call line. RX debug/stat output on interrupt or completion provides transport diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/kctest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/kstest.c -->
# sources/distributed-fs/openafs/src/rx/test/kstest.c

## Purpose
`kstest.c` is the matching simple RX server for `kctest.c`. It decodes one long value from each call, increments it, encodes it back, and runs as a donated-thread RX server.

## Important APIs, Types, and Functions
- `ParseCmd()` handles `-port`, `-log`, and `-stats`.
- `rxk_erproc()` is the request handler; it wraps the call in an `XDR` stream, decodes a long, increments it, and encodes the result.
- `main()` initializes RX, creates an rxnull server security object, registers service id `1`, and calls `rx_StartServer(1)`.

## Control Flow
The server defaults to UDP port 10000, parses options, initializes RX, installs a SIGINT handler, creates rxnull security, registers the service, and donates the main thread to the RX server loop.

## State and Persistence
The only mutable static state is the listening port and `stats` flag. Optional persistent output is `kstest.log` through `rx_debugFile`.

## Dependencies and Integration Points
Integrates with RX server APIs, rxnull, RX debug stats, and XDR-over-RX. It is a direct protocol counterpart to `kctest.c`.

## Risks and Edge Cases
The handler does not check `xdr_long()` return values, so malformed or truncated calls may be treated as zero/undefined local state. `SigInt()` exits without `rx_Finalize()`, unlike the client. The service security array is sized for three but only index 0 is used.

## Test Signals
Normal startup prints initialization and service creation messages. A `kctest` client should receive `1989` after sending `1988`; interrupt-time stats indicate transport behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/kstest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/tableGen.c -->
# sources/distributed-fs/openafs/src/rx/test/tableGen.c

## Purpose
`tableGen.c` generates RPC signature tables for `generator.c`. It creates deterministic combinations of argument directions and types, plus additional randomized multi-argument signatures.

## Important APIs, Types, and Functions
- Global `dir`/`typ` arrays are populated from command-line lists or defaults.
- `drand32()` mirrors the deterministic RNG used by `generator.c`.
- `SingleArg()`, `DoubleArg()`, and `BunchArg()` emit one-line signatures.
- `ProcessCmdLine()` handles optional append input, output file, and direction/type overrides.

## Control Flow
The program parses arguments, opens the output file, optionally copies an append file into it, emits one single-argument signature per type, emits every two-type combination, then emits 100 randomized signatures of up to `MAX_ARGS` arguments.

## State and Persistence
Persistent state is the generated output table. Runtime state is the selected direction/type arrays and deterministic RNG seed. With identical options and append file, output is deterministic.

## Dependencies and Integration Points
The output format is explicitly coupled to `generator.c`: `argCount ( DIR TYPE ) ...`. Default types include scalar, string, and array names recognized by the generator.

## Risks and Edge Cases
Changing emitted format breaks `generator.c`. Command parsing manually walks argv and assumes value lists stop at the next `-` argument. It avoids `INOUT varString` because the generator cannot handle reference string pointers for those cases.

## Test Signals
A useful signal is that `generator.c -f <table>` can parse all emitted lines and produce rxgen-compatible output. Deterministic output diffs are also meaningful because the RNG seed is fixed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/tableGen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/testclient.c -->
# sources/distributed-fs/openafs/src/rx/test/testclient.c

## Purpose
`testclient.c` is a manual RX throughput and behavior test client. It sends either a byte stream of configured size or a file to a test server and reports throughput and RX peer stats.

## Important APIs, Types, and Functions
- `main()` parses many transport-tuning options, initializes RX, creates an rxnull connection to service id `3` on port 2500, and performs calls.
- `SendFile()` streams a file over a single RX call and reads the server reply.
- `Abort()`, `Quit()`, `intSignal()`, and `quitSignal()` print RX stats and exit.
- `OpenFD()` opens `/dev/null` descriptors until a target fd number is reached, for fd-number stress testing.

## Control Flow
The client parses packet/window/drop/log/timing/file options, resolves the target host, optionally opens filler descriptors, initializes RX, creates a connection, and either runs `SendFile()` or loops over `nCalls` synthetic payload calls. For synthetic calls it writes until `nBytes` are sent, reads all response bytes, ends the call, reports throughput, optionally sleeps for compute/wait timing, and prints peer stats.

## State and Persistence
Global knobs include `print`, `eventlog`, `rxlog`, `fillPackets`, `timeout`, `waitTime`, `computeTime`, and `timeReadvs`. Optional persistent debug output is `rx_ctest.db`; file mode reads the named file but does not persist new local data.

## Dependencies and Integration Points
Uses RX core, RX globals, rxnull, RX clocks, `hostutil_GetHostByName`, and OpenAFS utility allocation. It pairs with `testserver.c`, especially the file-transfer mode and remote status `79` check.

## Risks and Edge Cases
`Abort()` passes a `va_list` to `printf` instead of `vprintf`, so formatted abort messages are unreliable. In `SendFile()`, `rx_Read(call, buf, sizeof(buf))` uses the size of the pointer, not the allocated block size. Large `nBytes` use a 4 MB buffer without initialization, so payload contents are arbitrary. Many transport globals are changed directly and depend on RXDEBUG or platform guards.

## Test Signals
Expected signals are throughput lines, response byte counts, and printed RX peer stats. File mode additionally detects remote status `79`, prints server response text, and reports file-send throughput.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/testclient.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/testserver.c -->
# sources/distributed-fs/openafs/src/rx/test/testserver.c

## Purpose
`testserver.c` is the companion RX throughput/file-transfer test server. It receives synthetic byte streams or writes incoming call data to a file, sends a fixed response string, and exposes many RX tuning/debug switches.

## Important APIs, Types, and Functions
- `main()` parses server options, initializes RX on port 2500, creates an rxnull service id `3`, configures process counts and reachability checks, and starts the server.
- `SimpleRequest()` drains a call into a static 2 MB buffer, optionally simulates compute/wait delay, and writes a fixed response.
- `FileRequest()` receives call data into `rcvFile`, sets RX local status `79`, writes a fixed response, and prints peer stats.
- `Abort()`, `Quit()`, and `OpenFD()` mirror the client-side helpers.

## Control Flow
Command-line parsing sets debug, packet/window, delay, file, drop, jumbo, and fd options. After RX initialization, the registered execute function is `FileRequest` when `-file` is present, otherwise `SimpleRequest`. RX then owns execution via `rx_StartServer(1)`.

## State and Persistence
Persistent effects include optional `rx_stest.db` logs, optional trace file configuration, and file output in `FileRequest()`. Global mutable state controls error return, print mode, debug logging, delays, and receive-file path.

## Dependencies and Integration Points
Uses RX core, rxnull, RX clocks, RX globals, OpenAFS abort helpers, and optional RXDEBUG trace/drop variables. It is designed for `testclient.c`.

## Risks and Edge Cases
`Abort()` has the same `printf`/`va_list` misuse as the client. `FileRequest()` allocates `buffer` but never frees it. `error` is parsed but not returned by `SimpleRequest()` or `FileRequest()`. Direct manipulation of RX globals makes the tool sensitive to RX build configuration.

## Test Signals
Startup prints packet-buffer count. Runtime signals include received-byte logs in verbose mode, fixed response text observed by the client, file creation in `-file` mode, and RX peer/stat output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/testserver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr.c -->
# sources/distributed-fs/openafs/src/rx/xdr.c

## Purpose
`xdr.c` implements generic Sun RPC XDR primitives for OpenAFS RX: scalar integers/chars/bools/enums, opaque byte sequences, counted bytes, discriminated unions, strings, wrapping/free helpers, and allocator hooks.

## Important APIs, Types, and Functions
- Scalar routines: `xdr_int`, `xdr_u_int`, `xdr_long`, `xdr_u_long`, `xdr_char`, `xdr_u_char`, `xdr_short`, `xdr_u_short`, `xdr_bool`, `xdr_enum`, and `xdr_afs_time64`.
- Buffer routines: `xdr_opaque`, `xdr_bytes`, and `xdr_string`.
- Higher-level routines: `xdr_union`, `xdr_wrapstring`, `xdrfree_string`, `xdr_alloc`, and `xdr_free`.
- Uses the `XDR` ops table from `xdr.h` for stream-specific reads/writes.

## Control Flow
Most routines switch on `xdrs->x_op`. Encode writes canonical 32-bit network-order units through `XDR_PUTINT32`/`XDR_PUTBYTES`; decode reads through `XDR_GETINT32`/`XDR_GETBYTES`; free releases allocations created by decode. Composite routines first marshal lengths/discriminants, validate maxima, then dispatch to element or arm routines.

## State and Persistence
No module-level mutable state. Allocation and deallocation go through `osi_alloc`/`osi_free`, so decoded objects persist until an XDR_FREE pass or explicit helper frees them.

## Dependencies and Integration Points
This is the generic type layer used by rxgen-generated code and by hand-written RX tests. It depends on `xdr.h` macros and concrete stream implementations such as memory, RX call, stdio, record, and length-counting XDR.

## Risks and Edge Cases
The file contains notable safety checks: preallocated `xdr_bytes` decode refuses sizes larger than caller-provided capacity; `xdr_string` refuses preallocated decode buffers, caps huge `maxsize`, rejects embedded NUL bytes, and poisons failed strings so later free size is calculable. Scalar casts can truncate platform `long`/`int` values to XDR's 32-bit representation. `xdr_union` relies on a sentinel `NULL_xdrproc_t` in the choices table.

## Test Signals
Round-trip encode/decode tests over `xdrmem_create` are direct signals for scalars, strings, bytes, and unions. Fuzz/negative tests should assert rejection for oversized byte counts, embedded-NUL strings, and too-small preallocated byte arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr.h -->
# sources/distributed-fs/openafs/src/rx/xdr.h

## Purpose
`xdr.h` declares the OpenAFS XDR public interface, core data types, operation enum, stream handle layout, ops macros, inline encode/decode macros, and namespace-remapping macros.

## Important APIs, Types, and Functions
- `enum xdr_op` defines `XDR_ENCODE`, `XDR_DECODE`, and `XDR_FREE`.
- `XDR` contains `x_op`, an `xdr_ops` vector, public/private pointers, base pointer, and `x_handy` scratch integer.
- `xdrproc_t` adapts to platforms needing fixed parameters instead of variadic calls.
- `struct xdr_discrim` describes discriminated-union arms.
- `XDR_GETINT32`, `XDR_PUTINT32`, `XDR_GETBYTES`, `XDR_PUTBYTES`, `XDR_GETPOS`, `XDR_SETPOS`, `XDR_INLINE`, and `XDR_DESTROY` dispatch into the active backend.
- `IXDR_*` macros optimize inline network-order 32-bit primitive access.

## Control Flow
The header defines dispatch macros rather than runtime logic. All XDR implementation files install an `xdr_ops` vector, and generic marshalling routines call back through this vector.

## State and Persistence
`XDR` instances own backend-specific stream state through `x_private`, `x_base`, and `x_handy`; ownership and persistence depend on the backend. The header also maps common `xdr_*` names to `afs_xdr_*` for non-NT builds to avoid namespace collisions.

## Dependencies and Integration Points
Included by RX, rxgen-generated code, tests, and all XDR backends. It bridges platform headers, kernel/user allocation hooks, OpenAFS integer types, and `xdr_prototypes.h`.

## Risks and Edge Cases
Backend implementations must fully populate ops entries used by callers; some backends intentionally set unsupported operations to `NULL`, so generic callers must avoid unsupported operations. Inline macros assume alignment and network-order 32-bit units. The `xdrproc_t` signature variations are sensitive to ABI/calling-convention mismatches.

## Test Signals
Compile coverage across kernel/user and platform targets is important. Runtime signals include successful generic type round-trips over every backend and safe failure when unsupported operations are not invoked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_afsuuid.c -->
# sources/distributed-fs/openafs/src/rx/xdr_afsuuid.c

## Purpose
`xdr_afsuuid.c` provides the XDR routine for the built-in `afsUUID` type.

## Important APIs, Types, and Functions
- `xdr_afsUUID(XDR *xdrs, afsUUID *objp)` serializes fields in UUID order: `time_low`, `time_mid`, `time_hi_and_version`, two clock sequence bytes, and six node bytes.

## Control Flow
The function is a straight-line sequence of primitive XDR calls. It returns `FALSE` on the first failed field conversion and `TRUE` only after the node vector succeeds.

## State and Persistence
No local persistent state. For `XDR_FREE`, behavior delegates to primitive routines and `xdr_vector`; no dynamic UUID storage is allocated here.

## Dependencies and Integration Points
Depends on `xdr_afs_uint32`, `xdr_u_short`, `xdr_char`, and `xdr_vector`. Used wherever OpenAFS RPC interfaces expose `afsUUID`.

## Risks and Edge Cases
The cast to `xdrproc_t` for `xdr_char` reflects the legacy function pointer signature mismatch. A field-order change would break wire compatibility.

## Test Signals
Round-trip an `afsUUID` through memory XDR and compare every field. Negative stream tests should fail when any primitive field read/write is truncated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_afsuuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_array.c -->
# sources/distributed-fs/openafs/src/rx/xdr_array.c

## Purpose
`xdr_array.c` implements generic counted variable-length array marshalling for user and kernel XDR callers.

## Important APIs, Types, and Functions
- `xdr_array(XDR *xdrs, caddr_t *addrp, u_int *sizep, u_int maxsize, u_int elsize, xdrproc_t elproc)` handles array count, optional allocation, per-element conversion, and freeing.

## Control Flow
The routine caps `maxsize` to avoid `c * elsize` overflow, marshals or reads the element count, validates count against maximum and preallocated capacity, allocates and zeroes storage on decode when `*addrp` is `NULL`, iterates each element through `elproc`, and frees allocated storage during `XDR_FREE`.

## State and Persistence
Decoded arrays may be allocated with `osi_alloc` and persist via `*addrp` until `XDR_FREE`. `*sizep` is updated to the decoded count.

## Dependencies and Integration Points
Used by rxgen-generated `xdr_*` routines for variable arrays. Relies on `xdr_u_int`, `osi_alloc`, `osi_free`, and caller-provided element XDR functions.

## Risks and Edge Cases
`elsize` must be nonzero; the overflow guard divides by `elsize`. Preallocated decode requires `*sizep` to represent capacity on entry. Element conversion failures can leave partially decoded arrays that the caller must clean up with `XDR_FREE`.

## Test Signals
Test zero-length arrays, max-size rejection, preallocated too-small rejection, allocation-on-decode, element failure propagation, and freeing resets `*addrp` to `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_arrayn.c -->
# sources/distributed-fs/openafs/src/rx/xdr_arrayn.c

## Purpose
`xdr_arrayn.c` provides `xdr_arrayN`, a kernel-only variant of counted array marshalling.

## Important APIs, Types, and Functions
- `xdr_arrayN()` mirrors `xdr_array()` but is compiled under `#ifdef KERNEL`.

## Control Flow
It follows the same count-read/write, maximum validation, optional decode allocation, per-element loop, and free behavior as `xdr_array.c`.

## State and Persistence
Decoded storage is allocated via `osi_alloc` and freed through `osi_free`. `*sizep` is updated to the wire count after successful capacity validation.

## Dependencies and Integration Points
Integrated into kernel XDR consumers and declared in `xdr_prototypes.h`. Includes kernel-specific headers and OpenBSD allocation compatibility glue.

## Risks and Edge Cases
The implementation is largely duplicated from `xdr_array`; divergence between the two can create user/kernel behavior differences. Like `xdr_array`, `elsize == 0` would be invalid.

## Test Signals
Kernel build coverage and array round-trip tests should match `xdr_array` semantics, including oversized and preallocated-buffer rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_arrayn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_float.c -->
# sources/distributed-fs/openafs/src/rx/xdr_float.c

## Purpose
`xdr_float.c` implements floating-point XDR primitives for non-Windows platforms.

## Important APIs, Types, and Functions
- `xdr_float()` serializes a `float` by treating its bits as one 32-bit unit.
- `xdr_double()` serializes a `double` as two 32-bit units with word ordering chosen for the supported non-NT environments.

## Control Flow
Each function switches on `x_op`: encode writes raw integer words, decode reads them, free succeeds without action. On `AFS_NT40_ENV`, both return `FALSE`.

## State and Persistence
No persistent state or allocation.

## Dependencies and Integration Points
Used by generated XDR routines for IDL `float` and `double` types. Depends on backend `XDR_GETINT32` and `XDR_PUTINT32`.

## Risks and Edge Cases
The file explicitly warns the implementation is non-portable. It assumes local floating-point representation and word ordering compatible with the chosen XDR layout; Windows is unsupported here.

## Test Signals
Round-trip representative floats/doubles on supported platforms and compile-time exclusion or expected failure on NT builds. Cross-endian interoperability is the key risk signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_float.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_int32.c -->
# sources/distributed-fs/openafs/src/rx/xdr_int32.c

## Purpose
`xdr_int32.c` provides OpenAFS-specific 32-bit signed and unsigned integer XDR routines.

## Important APIs, Types, and Functions
- `xdr_afs_int32()` directly gets/puts an `afs_int32`.
- `xdr_afs_uint32()` directly gets/puts an `afs_uint32` through casts to the 32-bit backend API.

## Control Flow
Each routine checks `x_op`: decode calls `XDR_GETINT32`, encode calls `XDR_PUTINT32`, free returns `TRUE`, and unknown operations return `FALSE`.

## State and Persistence
No persistent state and no allocation.

## Dependencies and Integration Points
These routines are foundational for rxgen-generated code and other XDR primitives, including UUID and 64-bit values.

## Risks and Edge Cases
Unsigned support relies on casting to `afs_int32 *` for the backend. Correctness depends on backend network-byte-order conversion and OpenAFS integer type widths.

## Test Signals
Round-trip boundary values: `0`, `-1`, `INT32_MIN`, `INT32_MAX`, and `UINT32_MAX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_int32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_int64.c -->
# sources/distributed-fs/openafs/src/rx/xdr_int64.c

## Purpose
`xdr_int64.c` implements signed and unsigned 64-bit integer XDR routines for OpenAFS.

## Important APIs, Types, and Functions
- `xdr_int64()` delegates to `xdr_afs_int64()`.
- `xdr_afs_int64()` marshals high signed 32 bits followed by low unsigned 32 bits.
- `xdr_uint64()` delegates to `xdr_afs_uint64()`.
- `xdr_afs_uint64()` marshals high and low unsigned 32-bit halves.

## Control Flow
Decode reads high then low words and reconstructs by shifting high left 32 and adding low. Encode splits the local 64-bit value into high and low words and writes both. Free succeeds without action.

## State and Persistence
No allocation or persistent state.

## Dependencies and Integration Points
Used by `xdr_afs_time64()` and any rxgen interface using 64-bit OpenAFS integer types. Depends on backend 32-bit XDR ops.

## Risks and Edge Cases
Signed right-shift behavior and reconstruction must preserve negative values on supported compilers. The low mask uses `0xFFFFFFFFL`, whose width depends on platform `long`, though cast targets are fixed OpenAFS types.

## Test Signals
Round-trip `0`, `1`, `-1`, signed min/max, and values crossing the 32-bit boundary. Wire-order tests should confirm high word precedes low word.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_int64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_len.c -->
# sources/distributed-fs/openafs/src/rx/xdr_len.c

## Purpose
`xdr_len.c` implements an XDR backend that measures the number of bytes an encode would produce without writing data.

## Important APIs, Types, and Functions
- `xdrlen_create(XDR *xdrs)` initializes an encode-only stream with `x_handy = 0`.
- `xdrlen_putint32()` and `xdrlen_putbytes()` increment `x_handy`.
- `xdrlen_getpos()` returns the accumulated length; `xdrlen_setpos()` sets it.

## Control Flow
Generic XDR encode routines call this backend as if writing to a stream. Integer and byte writes accumulate byte counts; reads and inline access return failure/NULL.

## State and Persistence
State is only `x_handy`, the current calculated encoded length. No buffers are allocated or persisted.

## Dependencies and Integration Points
Used by callers that need to size a memory buffer before a later `xdrmem_create` encode pass.

## Risks and Edge Cases
It does not enforce overflow on `x_handy`, which is an `int` in `XDR`. Decode operations are unsupported and should not be used. Length calculation depends on generic routines calling backend write operations for all bytes including padding.

## Test Signals
For a representative object, length from `xdrlen_create` should equal the final position after encoding the same object with `xdrmem_create`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_len.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_mem.c -->
# sources/distributed-fs/openafs/src/rx/xdr_mem.c

## Purpose
`xdr_mem.c` implements an XDR backend over a caller-provided memory buffer.

## Important APIs, Types, and Functions
- `xdrmem_create()` initializes the stream with buffer base, current pointer, size, and operation.
- `xdrmem_getint32()`/`xdrmem_putint32()` read/write network-order 32-bit units.
- `xdrmem_getbytes()`/`xdrmem_putbytes()` copy raw bytes.
- `xdrmem_getpos()`/`xdrmem_setpos()` support buffer-relative seeking.
- `xdrmem_inline()` returns a direct pointer to contiguous buffer space when available.

## Control Flow
Every read/write verifies `x_handy` has enough remaining bytes, updates remaining capacity, copies or converts data, and advances `x_private`. `setpos` recomputes remaining capacity relative to the original buffer and current end.

## State and Persistence
The backend persists no ownership; it mutates the caller-provided buffer and stores cursor/capacity state in the `XDR` handle. `destroy` is a no-op.

## Dependencies and Integration Points
This is the primary backend for unit tests and in-memory encode/decode of rxgen data structures.

## Risks and Edge Cases
The code casts buffer pointers to `afs_int32 *`, so alignment matters. `x_handy` is capped at `INT_MAX`, limiting very large buffers. `setpos` compares against the current original end, not a separately stored total length.

## Test Signals
Round-trip primitives and composites, verify failures on short buffers, verify `getpos`/`setpos`, and confirm inline access advances position.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_prototypes.h -->
# sources/distributed-fs/openafs/src/rx/xdr_prototypes.h

## Purpose
`xdr_prototypes.h` declares OpenAFS XDR functions after `XDR` and related types are defined by `xdr.h`.

## Important APIs, Types, and Functions
It declares UUID, int32, int64, RX-call backend creation, generic XDR primitives, array/reference/pointer/vector helpers, memory and length backends, record-stream APIs, and allocation hooks.

## Control Flow
No runtime control flow.

## State and Persistence
No runtime state. The `XDR_AFS_DECLS_ONLY` guard allows a reduced declaration set for contexts needing only AFS-specific declarations.

## Dependencies and Integration Points
Included at the end of `xdr.h`; forward-declares `struct rx_call` for `xdrrx_create`. Keeps generated and hand-written code from relying on implicit declarations.

## Risks and Edge Cases
Prototype mismatch with implementation files would surface as ABI/calling bugs, especially around `xdrproc_t` casts and platform-specific declarations. It declares `osi_alloc`/`osi_free` fallbacks when macros are absent.

## Test Signals
Compile with strict prototypes across user/kernel targets and generated rxgen output. Link tests should catch missing implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_rec.c -->
# sources/distributed-fs/openafs/src/rx/xdr_rec.c

## Purpose
`xdr_rec.c` implements record-marked XDR streams over a TCP-like read/write handle. It supports Sun RPC record fragments with a high-bit last-fragment marker and 31-bit fragment length.

## Important APIs, Types, and Functions
- `RECSTREAM` stores input/output buffers, fragment state, callbacks, and sizes.
- `xdrrec_create()` allocates buffers and initializes backend ops.
- Backend ops implement int32/byte read-write, position, inline, and destroy behavior.
- Exported record controls: `xdrrec_skiprecord()`, `xdrrec_eof()`, and `xdrrec_endofrecord()`.
- Internal helpers: `flush_out()`, `fill_input_buf()`, `get_input_bytes()`, `set_input_fragment()`, `skip_input_bytes()`, and `fix_buf_size()`.

## Control Flow
Writes buffer data behind a fragment header; `xdrrec_endofrecord()` either flushes with `LAST_FRAG` or starts another in-buffer fragment. Reads consume fragment bytes, reading new fragment headers when needed. `skiprecord` discards remaining fragments until record alignment is restored.

## State and Persistence
The `XDR` handle owns a heap-allocated `RECSTREAM` plus input/output buffers until `XDR_DESTROY`. Fragment counters (`fbtbc`, `last_frag`, `frag_sent`) persist across calls and define the current record boundary.

## Dependencies and Integration Points
Used for RPC-over-stream transports that need record marking. It depends on caller-provided `readit` and `writeit` callbacks and generic XDR routines dispatch through its ops vector.

## Risks and Edge Cases
`xdrrec_create()` returns `void` and silently leaves partially allocated state on allocation failure. Several pointer differences are cast through 32-bit integer types, which is risky on 64-bit systems. The position functions assume `tcp_handle` can be cast to an fd for `lseek`, which is not valid for every opaque handle.

## Test Signals
Round-trip records with single and multiple fragments, verify `skiprecord` alignment, test EOF lookahead, force small send/receive buffers, and simulate short read/write callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_rec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_refernce.c -->
# sources/distributed-fs/openafs/src/rx/xdr_refernce.c

## Purpose
`xdr_refernce.c` implements `xdr_reference`, the XDR helper for a non-null referenced object. The filename contains the historical misspelling `refernce`.

## Important APIs, Types, and Functions
- `xdr_reference(XDR *xdrs, caddr_t *pp, u_int size, xdrproc_t proc)` allocates storage for decode if needed, invokes the referenced object's XDR procedure, and frees storage on `XDR_FREE`.

## Control Flow
If `*pp` is `NULL`, decode allocates and zeroes `size` bytes, free returns success, and encode proceeds without allocation. The routine then calls `proc`; in free mode it frees the object and clears `*pp`.

## State and Persistence
Decoded referenced storage persists through `*pp` until an XDR_FREE pass. There is no module global state.

## Dependencies and Integration Points
Used by `xdr_pointer()` and generated XDR routines for recursive or indirect structures. Depends on caller-provided object XDR procedures and `osi_alloc`/`osi_free`.

## Risks and Edge Cases
Encode with `*pp == NULL` still calls the object procedure with a null pointer, so callers should use `xdr_pointer()` when nullability is part of the wire format. Partial decode failure can leave allocated storage that callers must free.

## Test Signals
Decode with null pointer should allocate and zero storage; free should clear it. A nested object procedure failure should propagate `FALSE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_refernce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_rx.c -->
# sources/distributed-fs/openafs/src/rx/xdr_rx.c

## Purpose
`xdr_rx.c` implements an XDR backend over an RX call stream.

## Important APIs, Types, and Functions
- `xdrrx_create(XDR *xdrs, struct rx_call *call, enum xdr_op op)` binds an XDR handle to an RX call.
- `xdrrx_getint32()`/`xdrrx_putint32()` use `rx_Read32`/`rx_Write32` and network-order conversion.
- `xdrrx_getbytes()`/`xdrrx_putbytes()` use `rx_Read`/`rx_Write`.
- `xdrrx_inline()` intentionally returns `NULL`.

## Control Flow
Generic XDR routines dispatch to RX reads and writes. Each operation returns success only when RX reads/writes exactly the requested byte count. AIX kernel builds pin stack pages around RX calls to avoid paging under network interrupt constraints.

## State and Persistence
The `XDR` handle stores only a borrowed `struct rx_call *` in `x_private`; it does not own or destroy the call.

## Dependencies and Integration Points
This is the backend used by rxgen client/server stubs and hand-written RX tests such as `kctest.c`/`kstest.c`.

## Risks and Edge Cases
Position operations are not supported and are set to `NULL`. Exact-length RX read/write semantics mean partial stream errors fail the XDR operation. The AIX stack-pinning path tracks failures but continues.

## Test Signals
Client/server RPC round trips through rxgen stubs and direct `xdrrx_create` tests. Short read/write simulation should force `FALSE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_stdio.c -->
# sources/distributed-fs/openafs/src/rx/xdr_stdio.c

## Purpose
`xdr_stdio.c` implements an XDR backend over a standard `FILE *` stream.

## Important APIs, Types, and Functions
- `xdrstdio_create()` initializes the backend.
- `xdrstdio_getint32()`/`xdrstdio_putint32()` use `fread`/`fwrite` with network-order conversion except on `mc68000`.
- `xdrstdio_getbytes()`/`xdrstdio_putbytes()` transfer raw bytes.
- `xdrstdio_getpos()`/`xdrstdio_setpos()` use `ftell`/`fseek`.
- `xdrstdio_destroy()` flushes the file; it does not close it.

## Control Flow
Each backend operation directly invokes stdio and returns `FALSE` if the expected item count is not transferred. Inline access is unsupported and returns `NULL`.

## State and Persistence
The `XDR` handle borrows the `FILE *`. The file content is persistent according to the caller's stream; this backend only flushes on destroy.

## Dependencies and Integration Points
Useful for file-based XDR serialization and legacy Sun RPC compatibility paths. Generic XDR routines use this through the ops vector.

## Risks and Edge Cases
The function uses old K&R declarations, which can hide prototype issues. It does not close the stream. `fread(addr, len, 1)` reports failure unless the whole byte block is read.

## Test Signals
Encode to a temporary file, rewind, decode, and compare values. Test `getpos`/`setpos` and flush behavior after destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_stdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_update.c -->
# sources/distributed-fs/openafs/src/rx/xdr_update.c

## Purpose
`xdr_update.c` adds later Sun RPC helper routines needed by rpcgen/rxgen: nullable pointers and fixed-length vectors.

## Important APIs, Types, and Functions
- `xdr_pointer()` serializes a nullable pointer as a boolean presence flag followed by referenced object data.
- `xdr_vector()` serializes a fixed number of elements in static storage.

## Control Flow
`xdr_pointer()` computes `more_data` from `*objpp`, marshals it with `xdr_bool`, clears `*objpp` when absent, and otherwise delegates to `xdr_reference`. `xdr_vector()` loops `nelem` times and calls the element XDR routine for each fixed-size element.

## State and Persistence
Pointer decode can allocate storage via `xdr_reference`; vector handling does not allocate because storage is caller-owned.

## Dependencies and Integration Points
Used by generated XDR routines for recursive pointers and fixed arrays. Depends on `xdr_bool`, `xdr_reference`, and caller-provided element/object XDR functions.

## Risks and Edge Cases
During decode, the initial `more_data = (*objpp != NULL)` value is overwritten by the wire boolean, so callers must rely on output state after success. Recursive data structures can allocate deeply and need a later XDR_FREE traversal.

## Test Signals
Round-trip null and non-null pointers, ensure absent pointers decode to `NULL`, and verify fixed-vector element counts and failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/xdr_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxdebug/Makefile.in -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxdebug/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxdebug/rxdebug.c -->
# sources/distributed-fs/openafs/src/rxdebug/rxdebug.c

## Purpose
`rxdebug.c` implements the `rxdebug` command-line utility, which probes a remote RX server over UDP and prints server stats, RX stats, connection state, security stats, peer metrics, and server version.

## Important APIs, Types, and Functions
- `PortNumber()` parses numeric ports and returns network byte order.
- `PortName()` resolves service names with `getservbyname`.
- `MainCommand()` performs argument interpretation, socket setup, debug RPCs, filtering, and reporting.
- `main()` registers command syntax through the OpenAFS `cmd` package and dispatches.

## Control Flow
The command resolves the target host and port, opens/binds a UDP socket, optionally fetches server version and exits, then calls `rx_GetServerDebug()` to learn stats and supported feature flags. Depending on flags it fetches RX stats, iterates connections with `rx_GetServerConnections()`, filters by dally state, host, port, client/server type, and auth level, prints per-call state, and optionally iterates peers with `rx_GetServerPeers()`.

## State and Persistence
The utility persists no files. Runtime state is local to `MainCommand`: next-connection/peer cursors, supported-feature bitmasks, filters, and display options.

## Dependencies and Integration Points
Depends on RX user debug APIs, RX data structure constants, host utilities, command parser, RX statistics printer, and optional rxgk security stats. It is installed by `rxdebug/Makefile.in`.

## Risks and Edge Cases
Output depends heavily on server-supported debug flags; unsupported features downgrade with warnings. Auth filtering assumes rxkad and rxgk levels use matching numeric constants. The fixed 64-byte version buffer truncates longer version strings. Remote debug calls can fail with negative codes and terminate the utility.

## Test Signals
Probe a local fileserver/default port, `-version`, `-rxstats`, `-noconns`, filtered connection modes, and peer output. Backward-compatibility tests should cover servers lacking newer debug flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxdebug/rxdebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/Makefile.in -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_cout.c -->
# sources/distributed-fs/openafs/src/rxgen/rpc_cout.c

## Purpose
`rpc_cout.c` emits C XDR routines for rxgen/rpcgen definitions and also builds per-parameter marshalling snippets used by RX client/server stub generation.

## Important APIs, Types, and Functions
- `emit()` dispatches by definition kind and writes `xdr_<type>` plus `xdrfree_<type>`.
- `print_ifstat()` is the central relation-aware emitter for pointers, vectors, arrays, aliases, strings, and opaque bytes.
- `emit_enum()`, `emit_union()`, `emit_struct()`, and `emit_typedef()` generate body code per data definition.
- `print_param()` builds `Proc_list->code` and `Proc_list->scode` marshalling expressions for procedure parameters.

## Control Flow
For normal data definitions, `emit()` prints a function header, emits per-field/per-arm XDR calls, then prints a success trailer. `print_ifstat()` selects the correct helper (`xdr_pointer`, `xdr_vector`, `xdr_array`, `xdr_string`, `xdr_bytes`, or direct alias call) and emits failure checks. Procedure-parameter generation mutates `Proc_list` metadata as it encounters arrays, strings, and indirect parameters.

## State and Persistence
The module writes generated C to global `fout` and mutates global rxgen structures such as `Proc_list`, `PerProcCounter`, `typedef_defined`, and `defined`. There is no standalone persistent state beyond generated files.

## Dependencies and Integration Points
Depends on parsed `definition`/`declaration` trees from `rpc_parse.h`, symbol lists from `rpc_util.h`, and global flags such as `brief_flag`, `hflag`, and `cflag`. Called from `rpc_main.c` output passes.

## Risks and Edge Cases
Generated code correctness depends on relation/type classification. Fixed local buffers for code snippets and type names assume generated strings fit. `print_param()` has special cases for strings and arrays that mutate parameter type/name, making ordering and global state important.

## Test Signals
Generate XDR code for structs, enums, unions with defaults, typedef arrays, fixed vectors, opaque arrays, and string parameters; compile generated output with strict warnings and run round-trip XDR tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_cout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_errors.h -->
# sources/distributed-fs/openafs/src/rxgen/rpc_errors.h

## Purpose
`rpc_errors.h` defines error constants used by rxgen-generated client/server marshalling and unmarshalling paths.

## Important APIs, Types, and Functions
- `RXGEN_CC_MARSHAL`, `RXGEN_CC_UNMARSHAL`, `RXGEN_SS_MARSHAL`, and `RXGEN_SS_UNMARSHAL` are negative generated-stub error codes.
- `VICETOKENDEAD` is a positive legacy error code noted as needing relocation.

## Control Flow
No runtime control flow.

## State and Persistence
No state; compile-time constants only.

## Dependencies and Integration Points
Included by generated or generator support code that needs stable marshalling error values.

## Risks and Edge Cases
Constants must not collide with other OpenAFS/RX error spaces. The comment indicates `VICETOKENDEAD` is misplaced here, which can confuse ownership of error-code definitions.

## Test Signals
Compile generated stubs that reference these constants and verify callers can distinguish client/server marshal and unmarshal failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_errors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_hout.c -->
# sources/distributed-fs/openafs/src/rxgen/rpc_hout.c

## Purpose
`rpc_hout.c` emits C header declarations for rxgen/rpcgen data definitions and procedure prototypes.

## Important APIs, Types, and Functions
- `print_datadef()` dispatches definition emission and emits `xdr_`/`xdrfree_` prototypes for non-rxgen data definitions.
- `pstructdef()`, `puniondef()`, `penumdef()`, `ptypedef()`, and `pconstdef()` emit C type/constant declarations.
- `psprocdef()` and `psproc1()` emit client, split, multi, ubik, and server-prefixed procedure prototypes.
- `pdeclaration()` emits one declaration with relation-specific syntax.
- `undefined2()` decides whether to prefix forward references with `struct`.

## Control Flow
For every parsed definition, `print_datadef()` optionally suppresses scanner echo for server generation, dispatches to the right emitter, then writes XDR prototypes. Procedure definitions may emit Start/End split prototypes, normal client prototypes, ubik wrappers, and server-manager prototypes depending on global flags and definition metadata.

## State and Persistence
The module writes to global `fout` and records type metadata into global lists such as `uniondef_defined` and `typedef_defined`. It reads global flags including `Sflag`, `uflag`, `kflag`, `brief_flag`, and `ServerPrefix`.

## Dependencies and Integration Points
Called by `rpc_main.c` during header and server-stub passes. It depends on parser data structures and utility functions from rxgen.

## Risks and Edge Cases
Prototype generation is sensitive to parameter direction flags and `OUT_STRING` handling. Fixed-size local `prefix` buffers assume only small prefixes like `struct `. Brief-mode array layouts differ from normal mode, so generated C and XDR emitters must agree.

## Test Signals
Generate headers for structs, recursive unions, typedef arrays, strings, split/multi procedures, ubik mode, and server prefixes; compile both generated header and generated C stubs together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_hout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_main.c -->
# sources/distributed-fs/openafs/src/rxgen/rpc_main.c

## Purpose
`rpc_main.c` is the top-level driver for `rxgen`, the OpenAFS RX protocol compiler. It parses command-line flags, preprocesses `.xg` input, and orchestrates generation of XDR, header, client stub, and server stub outputs.

## Important APIs, Types, and Functions
- `struct commandline` captures parsed flags and input/output paths.
- Global flags (`cflag`, `hflag`, `Cflag`, `Sflag`, `kflag`, `uflag`, `xflag`, `yflag`, `zflag`, `brief_flag`, etc.) drive scanner/parser and output modules.
- `main()` selects generation mode and invokes output passes.
- `extendfile()` computes output filenames.
- `open_input()` runs the C preprocessor with defines such as `-DRPC_XDR`, `-DRPC_HDR`, `-DRPC_CLIENT`, or `-DRPC_SERVER`.
- `c_output()`, `h_output()`, `C_output()`, and `S_output()` generate `.xdr.c`, `.h`, `.cs.c`, and `.ss.c` content.
- `parseargs()` validates flag combinations.

## Control Flow
`main()` allows `RXGEN_CPPCMD` to override the preprocessor, initializes parser state, parses flags, and either runs a single requested output pass or the default sequence. The default sequence regenerates parser state between passes and emits XDR, header, client, and server files; `-r` emits only client and server stubs. Each output pass opens preprocessed input, opens the target file, emits headers/includes, iterates `get_definition()`, and delegates to generation functions in other rxgen modules.

## State and Persistence
Persistent outputs are generated files and installed build-tool artifacts. Runtime state is broad and global: output file name buffers, include-dir list, parser state, package/function statistics, and output-mode flags. `record_open()` tracks files for cleanup on crash via utility code outside this subset.

## Dependencies and Integration Points
Depends on the C preprocessor, scanner/parser/util modules, `rpc_cout.c`, `rpc_hout.c`, and procedure-code generation functions from other rxgen files. Build integration comes from `rxgen/Makefile.in`, which injects `PATH_CPP`.

## Risks and Edge Cases
`open_input()` builds a shell command line for `popen`, so input/include paths with shell metacharacters are risky. Several filename buffers are fixed at 256 or 1024 bytes. `uppercase()` uses a static 100-byte buffer, so long include guards can overflow. Output would overwrite input is checked only for exact string equality after output filename selection.

## Test Signals
Run `rxgen` in each mode (`-c`, `-h`, `-C`, `-S`, `-r`, default) on representative `.xg` inputs; verify generated files compile and that cpp include handling, `RXGEN_CPPCMD`, `-I`, `-P`, `-o`, kernel mode, ubik mode, stats mode, and brief mode behave as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxgen/rpc_main.c -->
