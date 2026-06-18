# subset-b-007771 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tcudbprocs.c -->
## sources/distributed-fs/openafs/src/butc/tcudbprocs.c

Purpose: implements tape-coordinator backup database save and restore operations. It creates BUDB dump/tape records for `SaveDb`, writes the BUDB server's serialized database stream to `butm`, reads that stream back during `RestoreDb`, restores configuration text blocks, and updates BUDB metadata for the tapes used.

Important APIs and state: public entry points include `saveDbToTape`, `restoreDbFromTape`, `CreateDBDump`, `GetDBTape`, `readDbTape`, `getTapeData`, `restoreDbHeader`, `restoreDbDump`, `restoreText`, and `saveTextFile`. `struct rstTapeInfo` tracks task id, tape sequence, and dump id across multi-volume restore. The file uses global tape-entry list state (`listEntryHead`, `listEntryPtr`, `lastDump`) to defer BUDB tape updates until the tape operation reaches a consistent point.

Control flow: save creates a database dump entry, obtains and labels the first tape, deletes overwritten old dump metadata where needed, streams `ubik_Call_SingleServer_BUDB_DumpDB` chunks into 16 KiB tape blocks, starts `KeepAlive` after the first BUDB stream call, writes filemarks/EOD at tape boundaries, prompts for more tapes when remaining space falls below an end margin, then finishes tape and dump records. Restore mounts the first expected database tape, reads a file stream of `structDumpHeader` records, dispatches database header, dump/tape/volume trees, and text sections, and moves to later tapes on `BUTM_ENDVOLUME`.

Persistence and integration: all durable state is external: BUDB records through `bcdb_*`, UBik BUDB RPCs, tape labels/data through `butm_*`, and temporary text files under `gettmpdir()`. It integrates with butc task status, device queue locking, prompt/log helpers, abort checks, DB watcher threading, and network byte-order conversion helpers from BUDB structures.

Risks: state is process-global and not safe for concurrent DB tape tasks. `writeDbDump` overwrites `code` during the final `UF_END_SINGLESERVER` cleanup, which can mask an earlier error. Several fixed buffers rely on OpenAFS tape-name limits. Restore trusts tape dump structure ordering and uses `ERROR_EXIT(-1)` for some malformed records. Test signals come indirectly from `test_budb.c`, `test_ftm.c`, and operational SaveDb/RestoreDb workflows; no isolated unit test covers multi-tape BUDB restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tcudbprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tdump.c -->
## sources/distributed-fs/openafs/src/butc/tdump.c

Purpose: small diagnostic utility for inspecting raw backup tape/file blocks. It opens the path supplied as `argv[1]`, repeatedly reads a fixed block size of `4096 + 24`, and prints the first sixteen 32-bit words in hexadecimal for each block, emitting `***EOF***` on zero-byte reads.

Important APIs: `glong` copies an `afs_int32` from a byte buffer at a 32-bit index; `main` performs the open/read/print loop. On AIX it installs full-core signal behavior for `SIGABRT` and `SIGSEGV`.

Control flow and state: there is no persistent state beyond the input file descriptor and local read buffer. The tool exits on open failure, short read, or negative read. It does not parse the `butm` structures semantically; it only exposes raw words useful when debugging the tape module format.

Dependencies and integration: uses roken/OpenAFS configuration headers and `AFS_component_version_number.c`. It is a debugging companion for butc/butm tape formats and assumes a legacy backup tape block size distinct from `BUTM_BLOCKSIZE`.

Risks and tests: there is no argument count validation before `argv[1]`, so invoking without an argument dereferences invalid memory. The fixed block size may not match all current tape-module writes. Test signal is manual use against known tape images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/tdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/test_budb.c -->
## sources/distributed-fs/openafs/src/butc/test_budb.c

Purpose: live integration stress test for BUDB database operations used by backup tape workflows. It connects to the backup database server, creates dump/tape/volume hierarchies, finishes them, verifies database consistency, and deletes selected dumps across repeated passes.

Important APIs: `connect_buserver` initializes RX, calls `udbClientInit`, and checks `BUDB_T_GetVersion`. `verifyDb` wraps `BUDB_DbVerify`. `deleteDump` calls `bcdb_deleteDump`. `main` constructs `budb_dumpEntry`, `budb_tapeEntry`, and `budb_volumeEntry` records and exercises `bcdb_CreateDump`, `bcdb_UseTape`, `bcdb_AddVolume`, `bcdb_FinishTape`, and `bcdb_FinishDump`.

Control flow and state: `NPASS` loops create `NDUMPS` dumps, each with `NTAPES` tapes and `NVOLUMES` volumes, varying volume names and sizes. Dump 1 can reference dump 0 as its initial dump. After each pass it deletes one non-appended dump and verifies the DB. Persistence is entirely in the live BUDB service.

Dependencies and integration: depends on RX, UBik BUDB client globals, and backup database client wrappers. It is not hermetic and requires a running backup database service for the selected cell.

Risks and tests: the test mutates real BUDB state and uses old-style C declarations. One bug checks `code` after `bcdb_UseTape` without assigning its return value, so a tape-use failure may be missed. It is valuable as an integration signal for BUDB metadata paths, but risky to run outside a disposable test cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butc/test_budb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/Makefile.in -->
## sources/distributed-fs/openafs/src/butm/Makefile.in

Purpose: builds and installs the backup tape module library and its local test programs. The primary artifact is `libbutm.a`, built from `file_tm.o` and `AFS_component_version_number.o`, then copied to `${TOP_LIBDIR}`.

Important targets: `all` builds `libbutm.a`, installs `butm_prototypes.h` into the top include tree, and builds `test_ftm` and `butm_test`. `test_ftm` and `butm_test` link against `libbutm.a`, `libbubasics.a`, LWP, USD, com_err, util, opr, roken, and platform libraries. `install` and `dest` place the static library in AFS lib directories.

Control flow and dependencies: includes common config and LWP make fragments. Object dependencies ensure `file_tm.c` and tests rebuild when public butm/com_err headers or component version source change.

Risks and tests: `test` only prints a usage hint for manual execution instead of running assertions. The library is static-only here, and tests require device configuration or tape hardware/file simulation. Duplicate `libafscom_err.a` in `LIBS` is harmless but noisy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/butm_prototypes.h -->
## sources/distributed-fs/openafs/src/butm/butm_prototypes.h

Purpose: private/provided prototypes for the file tape module implementation. It exposes helpers used by butm tests and callers that need direct instantiation of the file-backed tape module.

Important APIs: declares `incSize`, `SeekFile`, `butm_file_Instantiate`, and `NextFile`. `butm_file_Instantiate` is the key factory that fills a `struct butm_tapeInfo` operation table from a `struct tapeConfig`.

Control flow and state: no executable logic. The declarations imply external code can manipulate tape position/accounting helpers, so the implementation cannot treat those as fully private.

Dependencies and integration: requires prior visibility of `struct butm_tapeInfo`, `struct tapeConfig`, and `afs_uint32`, normally through `<afs/butm.h>` and OpenAFS standard headers.

Risks and tests: exposing low-level helpers increases coupling to `file_tm.c` internals. Build coverage comes from the butm Makefile installing this header and compiling `butm_test`/`test_ftm`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/butm_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/butm_test.c -->
## sources/distributed-fs/openafs/src/butm/butm_test.c

Purpose: simple behavioral test harness for `file_tm.c` error handling and sequencing. It instantiates a `butm_tapeInfo`, initializes LWP/IOMGR, and checks expected return codes for invalid and basic tape operations.

Important APIs: uses `butm_file_Instantiate` and direct `tapeInfo.ops.*` calls for mount, dismount, read/write file begin/end/data. Macros `PASS` and `PASSq` compare returned `code` against expected values and print results.

Control flow and state: first verifies operations fail with `BUTM_NOMOUNT` before mounting, checks bad file-end sequencing, writes then reads an empty file stream, then tests bad `writeFileData`/`readFileData` arguments and call order. Global `isafile` and `debugLevel` configure file tape behavior.

Dependencies and integration: depends on LWP, com_err, `butm.h`, and `butm_prototypes.h`; initializes the BUTM error table for readable diagnostics. The hard-coded device is `/dev/rmt0`, so the test targets real tape defaults unless the environment changes globals elsewhere.

Risks and tests: `PASS` prints failures but does not force process failure, so automated consumers may see exit 0 despite failed expectations. The calls to `writeFileData` pass argument positions that reflect the operation signature and can be easy to misread. It is useful smoke coverage for state-machine errors, not data integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/butm_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/config -->
## sources/distributed-fs/openafs/src/butm/config

Purpose: sample tape configuration line for butm tests or manual tape module setup.

Content and format: contains `10000000 /dev/rst0`, representing a capacity and device path in the older minimal format. `test_ftm.c` documents a richer format of capacity, device name, port number, and `isafile`; this file may be a legacy example rather than directly accepted by current `test_ftm` parsing.

State and integration: no executable behavior. It points tests toward a rewind/no-rewind tape device path and therefore can drive real hardware if used unmodified.

Risks and tests: using `/dev/rst0` on a developer system can fail or touch real tape hardware. The mismatch with `test_ftm`'s four-field parser is a compatibility risk for manual testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/error_macros.h -->
## sources/distributed-fs/openafs/src/butm/error_macros.h

Purpose: tiny local error-exit helper header used by tape module code and tests to centralize `code = value; goto label` patterns.

Important APIs: `ERROR_EXIT(evalue)` sets local variable `code` and jumps to `error_exit`; `ABORT_EXIT(evalue)` sets `code` and jumps to `abort_exit`.

Control flow and dependencies: these macros require a local `code` variable and the corresponding label to exist in the including function. They are intentionally statement-like via `do { ... } while (0)`.

Risks and tests: macro use hides non-local control flow and can overwrite prior error values during cleanup if used carelessly. Compile coverage comes from `file_tm.c`, `test_ftm.c`, and butc code that include similarly named local headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/error_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/file_tm.c -->
## sources/distributed-fs/openafs/src/butm/file_tm.c

Purpose: implements the backup tape module vtable for a real tape device or file-backed simulated tape. It defines the on-media format: tape labels, software file begin/end/EOD marks, hardware EOF marks, and 16 KiB data blocks with block marks.

Important APIs and types: `butm_file_Instantiate` fills `struct butm_tapeInfo.ops` with mount/dismount/create/readLabel/seek/read/write methods. Helpers include `ForkIoctl`, `ForkOpen`, `ForkClose`, `ForwardSpace`, `BackwardSpace`, `WriteEOF`, `Rewind`, `incSize`, `incPosition`, `readData`, `SeekFile`, `NextFile`, `WriteTapeBlock`, and `ReadTapeBlock`. `struct progress` in `tmRock` tracks `usd_handle_t`, mount id, and read/write sequencing. Static `config` stores device, tape size, filemark size, and port offset.

Control flow: mount opens the configured device with USD, sets read-only fallback, initializes counters, and stores progress state. Create/write-label rewinds or appends, writes a network-order label block, and emits EOF. File writes require `WriteFileBegin`, one or more `WriteFileData` calls, then `WriteFileEnd`; EOD writes a special filemark. Reads validate label/filemark/data block types and return `BUTM_ENDVOLUME`, `BUTM_EOF`, `BUTM_EOD`, or `BUTM_BADBLOCK` according to stream markers.

Persistence and dependencies: durable bytes are on the configured tape device or file. It depends on USD, LWP/IOMGR polling, com_err for config errors, roken, and platform tape ioctls. It uses child processes on non-pthread Unix to avoid blocking the whole process on tape open/ioctl/close.

Risks and tests: static globals (`config`, `tapeBlock`, `TapeBlockSize`) and the external `isafile` make concurrent independent tape instances unsafe. Several fixed 64-byte path buffers can truncate or overflow if upstream config permits long device strings. The read/write state machine is strict and callers must preserve operation order. `butm_test.c` covers bad-operation paths; `test_ftm.c` covers write/readback and append behavior with configured media.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/file_tm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/test_ftm.c -->
## sources/distributed-fs/openafs/src/butm/test_ftm.c

Purpose: end-to-end tape module data integrity test. It writes one or more regular files to a configured tape/file target using `butm`, writes EOD, remounts, reads the data back, and compares labels and file contents.

Important APIs and types: `GetDeviceInfo` parses test configuration into `struct tapeConfig`. `PerformDumpTest` performs the write/readback workflow using `butm_file_Instantiate`, `butm_Mount`, `butm_Create`, `butm_WriteFileBegin/Data/End`, `butm_WriteEOT`, `butm_ReadLabel`, `butm_ReadFileBegin/Data/End`, and `butm_SeekEODump` for append testing. `TestInfo` carries tape name, config, file list, and append flag.

Control flow and state: `main` parses `-configuration`, `-tapename`, and file arguments, filters readable regular files, initializes LWP/IOMGR, runs a normal dump test thread, and runs an appended test when target is a real tape. `PerformDumpTest` writes metadata labels, streams source files block by block, then validates label fields and content bytes on readback.

Dependencies and integration: uses LWP process creation/signaling, com_err, USD-backed `file_tm`, and filesystem input files. It reads a config format of capacity, device name, port, and `isafile`.

Risks and tests: the content comparison only checks one advancing byte per block (`tbuffer[tprogress++]`), not every byte, weakening integrity coverage. It uses global `bufferBlock` and `isafile`, and can touch real tape devices. Still, it is the strongest local signal for label, filemark, EOD, and append integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/butm/test_ftm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/Makefile.in -->
## sources/distributed-fs/openafs/src/cmd/Makefile.in

Purpose: builds the OpenAFS command parsing library, its PIC/shared variants, generated command error table files, and tests.

Important targets: `generated` creates `cmd.h` and `cmd_errors.c` from `cmd_errors.et` using `compile_et`. `all` installs `libcmd.a`, `libcmd_pic.a`, `cmd.h`, and `liboafs_cmd.la`. `all64` additionally builds 64-bit object/library variants. `config_file.lo` compiles Heimdal `config_file.c` against `krb5_locl.h` to provide raw config parsing APIs.

Dependencies and integration: depends on com_err (`liboafs_comerr.la`), roken, libtool fragments, pthread make config, and generated `AFS_component_version_number.c`. It exports `<afs/cmd.h>` to the top include directory for consumers.

Risks and tests: generated headers are central to many tools, so `compile_et` behavior affects this build. The clean target removes generated files and local test binaries. Test coverage is delegated to `src/cmd/test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/cmd.c -->
## sources/distributed-fs/openafs/src/cmd/cmd.c

Purpose: command-line parsing framework for OpenAFS tools. It supports registering subcommands, aliases, parameter descriptors, hidden/implicit commands, help/apropos/version built-ins, abbreviated matching, positional parsing, quoted interactive-line parsing, and option lookup from config files.

Important APIs and types: public APIs include `cmd_CreateSyntax`, `cmd_CreateAlias`, `cmd_AddParm`, `cmd_AddParmAtOffset`, `cmd_AddParmAlias`, `cmd_Dispatch`, `cmd_Parse`, `cmd_FreeOptions`, `cmd_ParseLine`, `cmd_FreeArgv`, `cmd_DisablePositionalCommands`, `cmd_DisableAbbreviations`, `cmd_SetBeforeProc`, `cmd_SetAfterProc`, `cmd_OptionAsInt/Uint/String/List/Flag`, `cmd_OptionPresent`, `cmd_OpenConfigFile`, and raw config accessors. Global parser state includes `allSyntax`, `noOpcodes`, hook callbacks, abbreviation/positional toggles, `globalConfig`, and `commandName`.

Control flow: syntaxes are sorted alphabetically and receive an implicit `-help` parameter. On first parse, built-ins are registered. `cmd_Parse` resolves opcode or implicit `initcmd`, parses switches with optional `-x=value`, fills `cmd_item` lists, enforces required params, and returns a selected syntax. `cmd_Dispatch` handles built-ins before hooks, runs before/proc/after callbacks, and resets per-invocation option items. Config option helpers prefer command-line values, then `[command_subcommand]`, `[command]`, and `[defaults]`.

State and integration: parser definitions persist globally for process lifetime; parsed options are transient and freed after dispatch. Config parsing is supplied by the Heimdal-derived raw config layer compiled in the same library. Error returns are generated from `cmd_errors.et`.

Risks and tests: many allocations use `assert`, so allocation failure aborts instead of returning errors. Globals make independent parser contexts impossible. `cmd_ParseLine` has a fixed 256-byte token buffer and strips quotes without escape handling. Test programs cover opcode/no-opcode/interactive modes but not config fallback deeply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/cmd.p.h -->
## sources/distributed-fs/openafs/src/cmd/cmd.p.h

Purpose: prolog header included into generated `cmd.h` by `compile_et`. It defines the public command parser types, constants, and function prototypes.

Important APIs and types: defines parameter types (`CMD_FLAG`, `CMD_SINGLE`, `CMD_LIST`, `CMD_SINGLE_OR_FLAG`), syntax flags (`CMD_ALIAS`, `CMD_HIDDEN`, `CMD_IMPLICIT`), parameter flags (`CMD_OPTIONAL`, `CMD_EXPANDS`, `CMD_HIDE`, `CMD_NOABBRV`), `CMD_MAXPARMS`, `struct cmd_item`, `struct cmd_parmdesc`, `struct cmd_syndesc`, config binding structures, parser functions, option conversion functions, and raw config accessors.

Control flow and state: no executable logic. The layout of `cmd_syndesc` and `cmd_parmdesc` is a binary/source contract with `cmd.c` and all command-line tools.

Dependencies and integration: generated `cmd.h` appends error-table definitions after this prolog, so consumers get both parser declarations and `CMD_*` error code definitions.

Risks and tests: changing constants or structure layout can break ABI/source compatibility across OpenAFS tools. Coverage comes from all consumers and `src/cmd/test` binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/cmd.p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/krb5_locl.h -->
## sources/distributed-fs/openafs/src/cmd/krb5_locl.h

Purpose: compatibility shim that lets Heimdal's `config_file.c` compile as OpenAFS `cmd` raw config parsing code without exposing a real Kerberos dependency.

Important APIs and types: maps `krb5_config_binding/section` to `cmd_config_binding/section`, defines minimal `krb5_context`, error, boolean, and deltat types, stubs Kerberos error-message helpers, and wraps Heimdal functions as `cmd_RawConfigParseFile*`, `cmd_RawConfigFileFree`, `cmd_RawConfigGetString/Bool/Int/List`. Under `EXPAND_PATH_HEADER`, it provides Windows path-expansion indirection and a dummy `SHGetFolderPath`.

Control flow and state: wrapper functions pass `NULL` Kerberos context into static Heimdal routines. `cmd_RawConfigGet*` use variadic path arguments to traverse config sections. No persistent state exists here beyond what Heimdal's parser allocates and returns.

Dependencies and integration: included only while compiling external Heimdal `config_file.c` in the cmd library. It depends on `cmd.h`, roken, and platform Windows headers when path expansion is built.

Risks and tests: the shim intentionally stubs Kerberos behavior, so future Heimdal changes may require new compatibility definitions. `krb5_abortx` aborts on fatal parser errors. Config behavior is indirectly tested through cmd option/config consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/krb5_locl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/test/Makefile.in -->
## sources/distributed-fs/openafs/src/cmd/test/Makefile.in

Purpose: builds three small command parser test binaries: `ctest`, `dtest`, and `itest`.

Important targets: `test`/`tests` depend on all three binaries. Each binary links its object with `-lcmd`, `libafscom_err.a`, `-lafsutil`, roken, and platform libraries. `clean` removes objects, binaries, archives, and core files.

Dependencies and integration: includes common config and LWP make fragments, and expects `libcmd` and generated `<afs/cmd.h>` to be available from the parent build.

Risks and tests: there is no scripted expected-output validation; the target only builds runnable examples. `install` and `dest` are empty, keeping these as build-tree tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/test/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/test/ctest.c -->
## sources/distributed-fs/openafs/src/cmd/test/ctest.c

Purpose: sample/test program for subcommand mode in the `cmd` library. It registers two commands and aliases, then dispatches command-line arguments.

Important APIs: uses `cmd_CreateSyntax`, `cmd_CreateAlias`, `cmd_AddParm`, `cmd_Seek`, and `cmd_Dispatch`. `apple` has no arguments; `pear` demonstrates required list, optional flag, expanding list, sparse parameter offset, and optional single string.

Control flow and state: callbacks print parsed option values from `as->parms`. Parser definitions persist globally until process exit; parsed `cmd_item` lists are reset by `cmd_Dispatch`.

Dependencies and integration: includes `<afs/cmd.h>` and therefore uses the generated command error table header. It is built by the cmd test Makefile.

Risks and tests: callbacks assume required items exist and do no defensive checks. It is primarily a manual parser behavior example for aliases, positional/list parsing, and help generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/test/ctest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/test/dtest.c -->
## sources/distributed-fs/openafs/src/cmd/test/dtest.c

Purpose: sample/test program for no-opcode mode in the `cmd` library. It creates a syntax with `name == NULL`, so arguments are parsed directly as options for one command.

Important APIs: uses `cmd_CreateSyntax(NULL, ...)`, `cmd_AddParm`, and `cmd_Dispatch`. Parameters cover required single `-num`, optional `-noauth` flag, and optional `-spotpos` list.

Control flow and state: dispatch parses from `argv[1]` because there is no subcommand token. The callback prints parsed values.

Dependencies and integration: built against `libcmd` by the cmd test Makefile.

Risks and tests: assumes `-num` is present and valid. Useful signal for `noOpcodes`, required parameter checks, and optional flag/list parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/test/dtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/test/itest.c -->
## sources/distributed-fs/openafs/src/cmd/test/itest.c

Purpose: interactive command parser test shell. It registers `apple`, `pear`, alias, and `quit`, then reads lines, tokenizes them with `cmd_ParseLine`, dispatches, and frees argument vectors.

Important APIs: exercises `initialize_CMD_error_table`, `cmd_CreateSyntax`, `cmd_AddParm`, `cmd_Seek`, `cmd_CreateAlias`, `cmd_ParseLine`, `cmd_Dispatch`, `cmd_FreeArgv`, and `afs_error_message`.

Control flow and state: loops on `gets(tline)`, prints a prompt, parses into a local `tv` array, dispatches, and reports parse/dispatch errors. `quit` exits the process.

Dependencies and integration: uses com_err to report generated cmd error messages and is built as a cmd test binary.

Risks and tests: uses unsafe `gets`, making it unsuitable for production or fuzzing without replacement. It tests quoted-line tokenization and repeated dispatch cleanup better than the one-shot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/cmd/test/itest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/Makefile.in -->
## sources/distributed-fs/openafs/src/comerr/Makefile.in

Purpose: builds the OpenAFS com_err runtime library and the `compile_et` build tool used to generate error table source/header files.

Important targets: `all` builds `compile_et`, installs public headers, builds `libafscom_err.a`, `liboafs_comerr.la`, and `libcomerr_pic.la`. `et_lex.lex.c` is generated from `et_lex.lex.l`; `compile_et` links `compile_et.o` and yacc output `error_table.o`, with platform-specific lex library handling. Install targets place `afs_compile_et`, headers, and library artifacts.

Dependencies and integration: includes config/LWP/lwptool fragments and links against `opr` and roken. Many OpenAFS components depend on `compile_et` during generated-header phases and on `libafscom_err` at runtime.

Risks and tests: generated parser/lexer files must be available and compatible with local lex/yacc. Platform case logic is hand-maintained. `test` delegates to a subdirectory not covered by this work item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/com_err.c -->
## sources/distributed-fs/openafs/src/comerr/com_err.c

Purpose: implements the formatted error reporting front end for OpenAFS com_err.

Important APIs: `afs_com_err` formats variadic messages, `afs_com_err_va` calls the current hook, `afs_set_com_err_hook` replaces the hook and returns the old hook, and `afs_reset_com_err_hook` restores the default. The default hook prints optional subsystem name, decoded error message from `afs_error_message`, optional formatted text, newline, carriage return, and flushes stderr.

Control flow and state: a static function pointer `com_err_hook` holds reporting behavior. No persistent external storage is touched.

Dependencies and integration: depends on `error_msg.c` for code-to-message lookup and `com_err.h` for API. Used broadly by command-line tools and tests.

Risks and tests: the hook pointer is global and not protected by a mutex, so concurrent hook changes are racy. The default writes an extra carriage return for historical terminal behavior. Coverage is broad through users such as butm tests and command tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/com_err.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/com_err.h -->
## sources/distributed-fs/openafs/src/comerr/com_err.h

Purpose: public header for the OpenAFS common error reporting and lookup library.

Important APIs: declares `afs_com_err`, `afs_com_err_va`, `afs_error_table_name`, `afs_error_message`, `afs_error_message_localize`, and hook setters/resetters with printf-format attributes. Under `AFS_OLD_COM_ERR`, maps legacy names such as `com_err` and `error_message` to the AFS-prefixed APIs.

Control flow and state: no executable logic. It defines the public ABI contract consumed by OpenAFS tools and libraries.

Dependencies and integration: requires `afs_int32`, `size_t`, and OpenAFS attributes from included upstream headers. Installed by the comerr Makefile.

Risks and tests: function pointer declaration syntax is hard to read and easy to break. Compatibility macros may shadow non-AFS com_err symbols when `AFS_OLD_COM_ERR` is defined.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/com_err.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/compile_et.c -->
## sources/distributed-fs/openafs/src/comerr/compile_et.c

Purpose: command-line compiler for `.et` error table definitions. It generates C source, header, or message catalog output consumed by OpenAFS builds.

Important APIs and state: `main` parses flags (`-debug`, `-language`, `-h`, `-p`, `-v`, `-emit`), derives input/output paths, opens `yyin`, optionally includes a `.p.h` prolog into the header, writes C/MSF prologs, calls `yyparse`, and emits trailer definitions such as `initialize_<table>_error_table`, `ERROR_TABLE_BASE_*`, and compatibility macros. Globals include `hfile`, `cfile`, `msfile`, `table_name`, `version`, `use_msf`, and emit flags. `xmalloc` exits on allocation failure; `yyerror` reports line and token context.

Control flow and persistence: generated files are written in the current working directory; input is resolved as `prefix/filename(.et)`. Parser actions in `error_table.y` write error strings and macro definitions as the grammar is reduced.

Dependencies and integration: depends on yacc/lex globals, `compiler.h`, `internal.h`, roken, opr, and generated component version source. It is invoked by Makefiles such as `src/cmd/Makefile.in`.

Risks and tests: argument parsing is manual and exits on many errors. It writes output files directly rather than atomically. Table names are truncated by parser code for compatibility, which can surprise callers. Test signal comes from generated headers/sources in normal builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/compile_et.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/compiler.h -->
## sources/distributed-fs/openafs/src/comerr/compiler.h

Purpose: shared declarations for the error table compiler and parser sources.

Important APIs and state: defines `enum lang` values `lang_C`, `lang_KRC`, and unfinished `lang_CPP`; declares global parser/compiler state `debug`, `filename`, `language`, and `whoami`; declares `yyparse`.

Control flow and dependencies: no executable logic. It couples `compile_et.c` and yacc/lex generated code through global variables.

Risks and tests: global state makes the compiler non-reentrant. C++ support is represented in the enum but rejected by `compile_et.c`. Build coverage comes from compiling `compile_et`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_msg.c -->
## sources/distributed-fs/openafs/src/comerr/error_msg.c

Purpose: runtime error-code decoder and error-table registry for com_err.

Important APIs and state: `afs_error_message`, `afs_error_message_localize`, `afs_com_right`, `afs_com_right_r`, and `afs_add_to_error_table`. Static `_et_list` stores registered generated tables. In pthread builds, `LOCK_ET_LIST` lazily initializes and uses a mutex via `pthread_once`.

Control flow: negative codes map to selected RX/RPC messages; table number zero maps through `strerror` or legacy volume messages; nonzero table codes split into table base and offset using `ERRCODE_RANGE`, then scan `_et_list` for a matching base. Unknown codes are formatted into a static buffer with table-name text and numeric offset. Localization uses CoreFoundation on Darwin, gettext when available, or plain copy.

Persistence and integration: registry state persists for process lifetime after generated `initialize_*_error_table` functions call `afs_add_to_error_table`. It integrates with `com_err.c`, generated error tables, platform localization, and `et_name` for table names.

Risks and tests: unknown-code and negative-code messages use static buffers, so returned pointers are not thread-safe despite registry locking. `afs_add_to_error_table` prevents duplicate bases but does not validate table contents. Coverage is broad through every generated error-table user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_table.h -->
## sources/distributed-fs/openafs/src/comerr/error_table.h

Purpose: public data structures and constants for generated com_err tables.

Important APIs and types: defines `struct error_table` with message vector, base, and count; `struct et_list` for registered table linked lists; constants `ERRCODE_RANGE` and `BITS_PER_CHAR`; declarations for `afs_error_table_name`, `afs_add_to_error_table`, `afs_com_right`, and `afs_com_right_r`.

Control flow and state: no executable logic. Generated `.c` files instantiate `error_table` and `et_list` objects matching this layout.

Dependencies and integration: includes system types and errno. Installed with comerr headers and used by generated code from `compile_et`.

Risks and tests: `base` is an `int` while generated code may format as long constants; this is legacy-compatible but should be treated carefully on unusual platforms. Any layout change breaks generated object compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_table.y -->
## sources/distributed-fs/openafs/src/comerr/error_table.y

Purpose: yacc grammar and semantic actions for parsing `.et` error table files.

Important APIs and state: grammar accepts `error_table`/`et`, optional table function, table id, one or more `error_code`/`ec` entries, and `end`. Semantic helpers include `add_ec`, `add_ec_val`, `put_ecs`, `set_table_num`, `set_table_fun`, `set_table_1num`, `char_to_num`, and `char_to_1num`. Globals include `table_number`, `current`, `error_codes`, and external output files.

Control flow: parser computes the table base from encoded table name and optional function, writes string entries to C or MSF output as entries are parsed, fills gaps with `NULL` for explicit numeric values, records symbolic names, then writes header `#define`s for each error code.

Persistence and integration: output is streamed into files opened by `compile_et.c`. The lexer is included at the end as generated `et_lex.lex.c` or NT variant. Generated tables later register with `afs_add_to_error_table`.

Risks and tests: parser uses process globals and exits on invalid table names. `add_ec_val` only prints when codes are out of order and returns, which may allow generation to continue in a degraded state. Table-name truncation is intentional legacy behavior but can collide. Build generation is the main test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_table.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_table_nt.c -->
## sources/distributed-fs/openafs/src/comerr/error_table_nt.c

Purpose: checked-in Bison-generated C parser for Windows/NT builds of the `.et` grammar, including copied semantic actions from `error_table.y`.

Important APIs and state: defines token constants, `YYSTYPE`, parser tables, `yyparse`, and the same helper functions as the grammar source: `add_ec`, `add_ec_val`, `put_ecs`, `set_table_num`, `set_table_fun`, `set_table_1num`, `char_to_num`, and `char_to_1num`. It includes `et_lex.lex_nt.c` on NT or `et_lex.lex.c` otherwise.

Control flow: Bison table-driven parser shifts/reduces `.et` syntax into semantic actions that compute table bases and write generated output. Error recovery is the old Bison skeleton behavior.

Persistence and integration: exists to avoid requiring yacc/Bison on some NT build paths. It shares globals and output-file contracts with `compile_et.c`.

Risks and tests: generated code is large, old, non-reentrant, and can drift from `error_table.y` if regenerated inconsistently. Manual edits should target the grammar instead. Build coverage on Windows is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_table_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_table_nt.h -->
## sources/distributed-fs/openafs/src/comerr/error_table_nt.h

Purpose: checked-in generated parser header for NT builds of the error table compiler.

Important APIs: defines `YYSTYPE` with `char *dynstr`, token values for `ERROR_TABLE`, `ERROR_CODE_ENTRY`, `END`, `STRING`, and `QUOTED_STRING`, and declares external `yylval`.

Control flow and integration: no executable logic. It is consumed by NT lexer/parser build paths so lexer tokens match the generated parser.

Risks and tests: must stay synchronized with `error_table_nt.c` and `error_table.y` token definitions. Build failures in NT compile_et paths are the main detection mechanism.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/error_table_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/et_lex.lex.l -->
## sources/distributed-fs/openafs/src/comerr/et_lex.lex.l

Purpose: lex scanner for `.et` error table files.

Important tokens: recognizes `error_table`/`et`, `error_code`/`ec`, `end`, quoted strings, alphanumeric/underscore strings, comments starting with `#`, whitespace, and single-character punctuation such as comma and equals.

Control flow and state: quoted strings are duplicated without surrounding quotes into `yylval.dynstr`; identifiers are duplicated as `STRING`; comments and whitespace are skipped; unknown single characters are returned literally. `yywrap` returns 1 to signal end of input.

Dependencies and integration: generated into `et_lex.lex.c` by the comerr Makefile and included by `error_table.y` output or NT parser variants. It depends on yacc token definitions and `yylval`.

Risks and tests: quoted strings do not support escapes and the identifier rule `{AN}*` can match empty input in some lex implementations, though surrounding rules usually consume progress. Build-time parsing of `.et` files is the main test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/comerr/et_lex.lex.l -->
