# Group Research: subset-b-007005

This grouped report covers Coda access-list/protection-database code, ASR resolver/launcher code, and auth2 client/server/token code. Each section is bounded by source-path markers so the reconciliation lane can split it into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/alprocs.c -->
# sources/distributed-fs/coda/coda-src/al/alprocs.c

Purpose: Implements the access-list (AL) library surface used by Coda servers and tools to allocate access lists and CPS sets, convert between internal and external text forms, translate names through the protection database, and compute effective rights.

Important APIs/functions: `AL_NewAlist`, `AL_FreeAlist`, `AL_htonAlist`, `AL_ntohAlist`, `AL_NewExternalAlist`, `AL_Internalize`, `AL_Externalize`, `AL_NewCPS`, `AL_GetInternalCPS`, `AL_GetExternalCPS`, `AL_CheckRights`, `AL_NameToId`, `AL_IdToName`, `AL_IsAMember`, `CmpPlus`, `CmpMinus`, and debug print helpers. The global `AL_MaxExtEntries` bounds external ACL conversion.

Control flow: Allocation routines size flexible-array structs and abort on allocation failure. Byte-order conversion routines no-op when host order already matches network order, otherwise swap header fields and entry arrays in place. `AL_Externalize` emits a counted text form, translating numeric IDs to PDB names when possible. `AL_Internalize` parses counts, resolves names back to IDs, fills an `AL_AccessList`, then sorts plus entries ascending and minus entries with `CmpMinus`. `AL_CheckRights` walks sorted ACL plus/minus entries against the CPS inclusion list, ORs matching positive rights, ORs matching negative rights, and returns `plus & ~minus`.

State and persistence: This file owns only heap-allocated AL/CPS buffers. Persistent identity and membership state is read through `PDB_db_open`, `PDB_readProfile`, `PDB_lookupByName`, and `PDB_lookupById`; `AL_Initialize` asserts that the PDB exists but does not mutate it.

Dependencies and integration: Depends on `prs.h`, `pdb.h`, `al.h`, RPC2/Coda utility logging, byte-order APIs, and the PDB profile array implementation. VICE and tools call this layer for authorization checks and CPS materialization.

Risks and test signals: The external ACL/CPS buffer sizing is an estimate and uses `sprintf`/`strcpy`; malformed or unexpectedly long data could overflow if invariants fail. `AL_Internalize` sorts minus entries using an offset based on `m` rather than `p`, which is suspicious because minus entries start after plus entries. Most failures return errno-style values, but allocation failures abort. `AL_CheckRights` assumes sorted CPS and ACL sections. `altest.c` is the interactive coverage signal for these APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/alprocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/altest.c -->
# sources/distributed-fs/coda/coda-src/al/altest.c

Purpose: Interactive test and diagnostic program for the AL package. It lets an operator exercise name/ID translation, ACL allocation, external/internal conversion, CPS retrieval, byte-order conversion, rights checks, and membership checks.

Important APIs/functions: `ReadConfigFile`, `main`, `Op_1` through `Op_6`, `AskSlot`, `NewSlot`, and `GetInputOutput`. It manipulates four slot vectors for internal ACLs, external ACL strings, internal CPS objects, and external CPS strings.

Control flow: Startup reads `server.conf`, initializes vice paths, parses optional `-x` debug level, calls `AL_Initialize`, then loops over major operation menus. Each operation submenu prompts with `scanf`, allocates a slot, fills or converts structures, calls the relevant AL API, and prints results. `GetInputOutput` can redirect operation input from a file while suppressing prompts to `/dev/null`.

State and persistence: Maintains in-process `Vec[SLOTTYPES][SLOTMAX]` ownership flags and pointers. It does not directly mutate the PDB, but name translation and CPS retrieval read the configured protection database through AL/PDB. Debug level mutates the external `AL_DebugLevel`.

Dependencies and integration: Pulls in `prs.h`, `al.h`, `codaconf`, and `vice_file` for configuration. It is a developer/operator harness rather than production code.

Risks and test signals: The program uses unbounded `%s` into fixed buffers and assumes well-formed interactive input, so it should not be exposed to untrusted streams. The slot model is useful for manual regression testing but is not automated; failures are mostly printed rather than asserted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/altest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdb.c -->
# sources/distributed-fs/coda/coda-src/al/pdb.c

Purpose: High-level protection database mutation and lookup layer. It creates, deletes, renames, clones, and changes IDs for users and groups while keeping membership lists, ownership lists, and CPS arrays consistent.

Important APIs/functions: `PDB_addToGroup`, `PDB_removeFromGroup`, `PDB_changeName`, `PDB_createUser`, `PDB_cloneUser`, `PDB_deleteUser`, `PDB_createGroup`, `PDB_deleteGroup`, `PDB_lookupByName`, `PDB_lookupById`, `PDB_bugfixes`, and `PDB_changeId`.

Control flow: Mutators open the database read/write, read affected profiles, update sorted `pdb_array` fields, write profiles, and close the shared handle. User creation allocates the next positive ID; group creation allocates the next negative ID and adds the owner as a member. Membership changes update both the group's `groups_or_members` and the member's `member_of`, then recompute CPS. Delete and ID-change flows walk all related groups/members to repair back references. `PDB_bugfixes` scans all records twice to repair historical owner/member/CPS inconsistencies.

State and persistence: Persists all changes via `PDB_writeProfile`, `PDB_deleteProfile`, and max-ID updates in `prot_users.cdb`. The logical profile state consists of positive user IDs, negative group IDs, `member_of`, `cps`, and `groups_or_members`.

Dependencies and integration: Depends on `pdb.h`, `prs.h`, `pdbarray`, profile pack/read/write helpers, and `rwcdb` through `pdbdb.c`. AL and auth code consume this database for identity and authorization.

Risks and test signals: Heavy use of `CODA_ASSERT` makes many data errors process-fatal. `PDB_deleteGroup` contains a suspicious `CODA_ASSERT(p.id == 0)` when reading groups that should exist. Recursing CPS updates can be expensive and depends on loop prevention. Name uniqueness is checked before create, but there is no visible transaction boundary across multi-record updates. `pdbtool` and `pdbarray_test` provide the main local exercisers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdb.h -->
# sources/distributed-fs/coda/coda-src/al/pdb.h

Purpose: Public header for Coda's protection database layer. It declares the profile structure, ID classification macros, high-level PDB mutation APIs, profile pack/read/write helpers, and low-level database entry points.

Important APIs/types: `PDB_HANDLE`, `PDB_profile`, `PDB_ISUSER`, `PDB_ISGROUP`, `PDB_MAXID_SET`, `PDB_MAXID_FORCE`, high-level `PDB_*` user/group routines, `pdb_pack`, `pdb_unpack`, profile helpers, and `PDB_db_*` persistence routines.

Control flow and state model: The header defines positive IDs as users and negative IDs as groups. `PDB_profile` stores the name, owner metadata for groups, sorted arrays of parent groups, computed CPS, and owned groups or group members. Callers combine this with `PDB_db_open` modes and profile read/write calls to perform mutations.

Persistence and integration: The opaque `PDB_HANDLE` is implemented by `pdbdb.c`; serialization is implemented by `pdbpack.c`; membership arrays are defined in `pdbarray.h`. This header is included by AL, pdbtool, auth support, and server code.

Risks and test signals: The header exposes many internal helpers, so callers can bypass higher-level consistency routines if used carelessly. The flexible ownership semantics of `groups_or_members` depend on testing `PDB_ISGROUP(id)` at runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbarray.c -->
# sources/distributed-fs/coda/coda-src/al/pdbarray.c

Purpose: Implements a small sorted dynamic array of `int32_t` IDs used by PDB profiles for membership, CPS, and ownership/member lists.

Important APIs/functions: `pdb_array_init`, `pdb_array_free`, `pdb_array_search`, `pdb_array_add`, `pdb_array_del`, `pdb_array_copy`, `pdb_array_merge`, `pdb_array_head`, `pdb_array_next`, `pdb_array_size`, `pdb_array_pack`, `pdb_array_unpack`, `pdb_array_to_array`, and `pdb_array_snprintf`.

Control flow: Insert grows capacity by 16 entries, finds the sorted insertion point, skips duplicates, shifts the tail, and inserts. Delete binary-searches, shifts the tail down, and zeroes the old last slot. Merge allocates a combined sorted buffer and de-duplicates overlaps. Pack/unpack store count followed by network-order entries.

State and persistence: Owns heap memory in `data`, with `size` and `memsize` tracking logical and allocated length. Persistent form is an `int32_t` count plus network-order data, embedded in packed PDB profiles.

Dependencies and integration: Used by `pdb.c`, `pdbprofile.c`, `pdbpack.c`, and tests. Depends on `netinet/in.h` for byte order and `coda_assert`.

Risks and test signals: Allocation return values are not consistently checked after `malloc`/`realloc`. `pdb_array_copy` allocates zero bytes when size is zero and does not special-case NULL, which is usually acceptable but brittle. `pdb_array_snprintf` repeatedly calls `strlen`, making it quadratic for long lists. `pdbarray_test.c` gives simple add/delete/merge coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbarray.h -->
# sources/distributed-fs/coda/coda-src/al/pdbarray.h

Purpose: Declares the `pdb_array` container and operations used throughout the protection database implementation.

Important APIs/types: `pdb_array` with `size`, `memsize`, and `data`; iterator offset typedef `pdb_array_off`; mutators, merge/copy, pack/unpack, iteration, and formatting routines.

Control flow and state model: The API assumes the implementation keeps `data` sorted and duplicate-free. Iteration uses a caller-owned integer offset initialized by `pdb_array_head` and advanced by `pdb_array_next`.

Persistence and integration: Pack/unpack are the bridge between in-memory PDB profile arrays and on-disk serialized profile records. The header is included by `pdb.h` and any caller needing direct list inspection.

Risks and test signals: The API exposes raw `data`, so callers can break sort and uniqueness invariants. No capacity is passed into `pdb_array_to_array`; callers must allocate at least `size` elements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbarray.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbarray_test.c -->
# sources/distributed-fs/coda/coda-src/al/pdbarray_test.c

Purpose: Small standalone smoke test for `pdb_array` behavior.

Important APIs/functions: `print_array` and `main`, which call `pdb_array_init`, `pdb_array_add`, `pdb_array_del`, `pdb_array_merge`, `pdb_array_size`, and `pdb_array_free`.

Control flow: The program creates array `a`, inserts values out of order, prints expected sorted forms, deletes values, merges a second array `b`, and frees both arrays.

State and persistence: All state is in process heap memory. No filesystem or database persistence is touched.

Dependencies and integration: Includes only `pdbarray.h`; it is a direct unit-level sanity check for the sorted-list primitive.

Risks and test signals: The test is print-based and has no assertions, exit-status validation, duplicate insertion case, pack/unpack case, or allocation failure coverage. Still useful as a quick visual regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbarray_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbdb.c -->
# sources/distributed-fs/coda/coda-src/al/pdbdb.c

Purpose: Low-level persistence layer for PDB profiles over an `rwcdb` database at `vice_config_path("db/prot_users.cdb")`.

Important APIs/functions: `PDB_db_open`, `PDB_db_reopen`, `PDB_db_nextkey`, `PDB_db_close`, `PDB_db_release`, `PDB_db_maxids`, `PDB_db_update_maxids`, `PDB_db_write`, `PDB_db_read`, `PDB_db_delete`, `PDB_db_delete_xfer`, `PDB_db_exists`, `PDB_db_compact`, and `PDB_setupdb`.

Control flow: A single static `pdb_handle` is lazily initialized. Read-only opens sync existing state; write opens upgrade the handle when needed and periodically sync every 128 mutations. Records are keyed by network-order numeric ID. Name lookup uses a secondary key composed of `"NAME"` plus the name, whose value is the numeric key. Key iteration filters to four-byte numeric keys.

State and persistence: Persists max UID/GID under a zero-length key and profile blobs under ID keys. Writes insert both ID and name index records, update max IDs, and free the packed blob passed by the caller. `PDB_db_close` is intentionally a no-op; `PDB_db_release` frees the process-global handle.

Dependencies and integration: Depends on `rwcdb`, `vice_file`, byte-order APIs, and `pdb.h`. Higher layers use this as the durable backing store for AL/PDB/auth identity data.

Risks and test signals: The global handle is not thread-safe and `PDB_db_nextkey` uses static iteration state. `PDB_db_close` doing nothing can surprise callers expecting close/flush isolation. `PDB_db_compact` is stubbed. Many error paths exit or assert. Name-key length omits an explicit NUL in the database key length, matching internal convention but needing consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbpack.c -->
# sources/distributed-fs/coda/coda-src/al/pdbpack.c

Purpose: Serializes and deserializes `PDB_profile` records to the binary blob stored by `pdbdb.c`.

Important APIs/functions: `pdb_pack`, `pdb_unpack`, and the local `ALIGN` macro. Fields packed are ID, name length/name bytes, owner ID, owner name length/name bytes, and three packed `pdb_array` lists.

Control flow: `pdb_pack` computes an int32-sized record length, allocates it, writes numeric fields in network order, copies strings without trailing NUL, appends packed arrays, asserts the computed offset, and returns buffer/size. `pdb_unpack` handles zero-size records by setting `id=0`, otherwise allocates NUL-terminated strings, unpacks arrays, asserts bounds, and frees the input blob.

State and persistence: This is the stable on-disk record format for PDB profiles. A comment notes the current `ALIGN(x) (x)` string padding is inefficient but preserved for compatibility.

Dependencies and integration: Called by `PDB_writeProfile`, `PDB_readProfile`, and name-in-use checks. Depends on `pdb_array_pack/unpack` and network byte order.

Risks and test signals: Deserialization trusts blob structure after minimal zero-size handling and can allocate based on corrupt lengths before the final assert. It allocates empty strings even for absent owner names. The `ALIGN` compatibility choice is format-sensitive and should not be changed without migration tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbpack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbprofile.c -->
# sources/distributed-fs/coda/coda-src/al/pdbprofile.c

Purpose: Profile-level lifecycle, read/write/delete, display, and CPS recomputation helpers for PDB records.

Important APIs/functions: `PDB_freeProfile`, `PDB_writeProfile`, `PDB_readProfile`, `PDB_readProfile_byname`, `PDB_deleteProfile`, `PDB_printProfile`, and `PDB_updateCps`.

Control flow: Read/write functions delegate to `PDB_db_read/write` and `pdb_pack/unpack`. Free clears IDs and releases strings and arrays only when the profile ID is nonzero. `PDB_printProfile` emits user/group metadata and array contents. `PDB_updateCps` rebuilds a record's CPS by merging all parent CPS arrays, adding self, writing the record, and recursively updating children when the record is a group.

State and persistence: Persists profiles through the shared PDB handle. `PDB_updateCps` is the main consistency mechanism for derived CPS state across the membership graph.

Dependencies and integration: Used by all high-level PDB operations and AL CPS retrieval. Depends on `pdbpack`, `pdbdb`, `pdbarray`, and `prs.h`.

Risks and test signals: Recursive CPS updates can be costly and require membership loops to be prevented elsewhere. `PDB_freeProfile` does nothing when `id == 0`, so callers must not expect it to sanitize partially unpacked corrupt records. Print buffers are fixed-size for array formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbprofile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbtool.c -->
# sources/distributed-fs/coda/coda-src/al/pdbtool.c

Purpose: Interactive and one-shot command-line administration tool for the protection database.

Important APIs/functions: Command handlers include `tool_byNameOrId`, `tool_list`, `tool_newUser`, `tool_newUser_Id`, `tool_changeName`, `tool_newGroup`, `tool_newDefGroup`, `tool_lookup`, `tool_clone`, `tool_addtoGroup`, `tool_removefromGroup`, `tool_delete`, `tool_update`, `tool_compact`, `tool_get_maxids`, `tool_maxids`, `tool_changeId`, `tool_ldif_export`, `tool_export`, `tool_import`, `tool_source`, and `tool_help`. `pdbcmds` registers these with the parser.

Control flow: Startup reads `server.conf`, initializes `vice_dir`, ensures the database exists, initializes the command parser, and either enters an interactive prompt or concatenates argv into one command line. Handlers parse names/IDs, validate existence, call high-level PDB mutations, and print status. Export paths dump passwd/group-like or LDIF data; import recreates users, then groups, then group memberships in multiple passes.

State and persistence: Mutates `db/prot_users.cdb` via PDB APIs. Import/export also read/write user-specified flat files. `tool_compact` runs historical bug fixups before calling the currently-stubbed compact routine.

Dependencies and integration: Depends on parser utilities, `codaconf`, `vice_file`, `pdb.h`, and the AL/PDB stack. It is the operator-facing bridge for PDB maintenance and migration.

Risks and test signals: The tool uses fixed buffers and `strcat`/`strcpy` in argv command construction and import parsing. `tool_newDefGroup` appears to pass the full `owner:group` string to `PDB_createGroup` but briefly truncates it only for owner lookup. Export mutates `rec.name` in memory when escaping colons. Error handling is mixed between printed failures and assertions in lower layers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/pdbtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/prs.h -->
# sources/distributed-fs/coda/coda-src/al/prs.h

Purpose: Defines Protection Server (PRS) constants, CPS representation, and filesystem rights bit masks shared by AL and auth/server code.

Important APIs/types: `PRS_VERSION`, `PRS_MAXNAMELEN`, well-known group names `PRS_ANYUSERGROUP` and `PRS_ADMINGROUP`, `PRS_InternalCPS`, `PRS_ExternalCPS`, and rights constants `PRSFS_READ` through `PRSFS_ALL`.

Control flow and state model: `PRS_InternalCPS` is a flexible-array style structure where leading `InclEntries` are sorted included IDs and trailing `ExclEntries` are excluded IDs. `PRS_ExternalCPS` is an ASCII string representation starting with a count.

Persistence and integration: The definitions are consumed by AL, auth2, and server authorization code. Rights bits map directly onto directory privileges.

Risks and test signals: The one-element array idiom requires callers to allocate enough memory for all IDs. The header documents exclusion entries, but current `AL_GetInternalCPS` fills only inclusions from PDB CPS arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/prs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/Makefile.am -->
# sources/distributed-fs/coda/coda-src/asr/Makefile.am

Purpose: Automake build recipe for the legacy ASR resolver/parser client program.

Important APIs/build targets: Conditionally builds `parser` when `BUILD_CLIENT` is enabled. Sources include `resolver_parser.y`, `resolver_lexer.l`, `ruletypes.cc`, `ruletypes.h`, `resolver.cc`, `wildmat.c`, `path.c`, and `asr.h`; `resolve.eg` is distributed as extra data.

Control flow: Yacc is invoked with `-d` to generate headers. A custom rule compiles `resolver_parser.c` as C++ into `resolver_parser.o`, matching its C++ semantic actions and `rule_t` usage. Lexer generation depends on `resolver_parser.h`.

State and persistence: Build-only file; it does not define runtime state.

Dependencies and integration: Includes RPC2, base, util, kerndep, vicedep, and vv include paths. Links util, kerndep, and base libraries.

Risks and test signals: Parser generation depends on generated header order and C++ compilation of yacc output. Build coverage of this target is conditional on client builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/asr.h -->
# sources/distributed-fs/coda/coda-src/asr/asr.h

Purpose: Shared small header for the ASR resolver lexer/parser and rule implementation.

Important APIs/types: Defines lexer context constants `FILE_NAME_CTXT`, `DEP_CTXT`, `CMD_CTXT`, and `ARG_CTXT`; declares global `context` and `debug`; defines `DEBUG(a)` conditional logging macro.

Control flow and state model: The lexer changes tokenization based on `context`, and parser actions update that context as they move through object, dependency, command, and argument grammar regions.

Persistence and integration: No persistence. Included by resolver, lexer, parser, ruletypes, and path helper files.

Risks and test signals: Global mutable `context` and `debug` make the lexer/parser non-reentrant. The `DEBUG` macro lacks braces, so callers must use it carefully in control-flow contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/asr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/path.c -->
# sources/distributed-fs/coda/coda-src/asr/path.c

Purpose: Implements a Mach-style `path(3)` splitter for environments that do not provide it, splitting a pathname into directory and final component.

Important APIs/functions: `path(char *pathname, char *direc, char *file)`.

Control flow: Handles empty path, no-slash path, and root path as special cases. For general paths, it copies the path, uses `strtok` to find the last component, copies that to `file`, then truncates the directory copy and strips trailing slashes except root.

State and persistence: Pure string manipulation with caller-provided buffers; no persistent state.

Dependencies and integration: Used by ASR object/dependency/argument parsing and resolver argument handling to normalize rule paths.

Risks and test signals: Uses `strtok`, so it is not reentrant and mutates the temporary copy. It assumes destination buffers are large enough and does not bound `strcpy`. Edge cases around repeated slashes depend on `strtok` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/resolver.cc -->
# sources/distributed-fs/coda/coda-src/asr/resolver.cc

Purpose: Main program for the older application-specific resolver (`parser`) that reads a `RESOLVE` file, matches a rule to an inconsistent object, enables Coda repair mode, executes rule commands, and disables repair mode.

Important APIs/functions: `IsAbsPath`, `FindResolveFile`, `FindRule`, `ParseArgs`, and `main`. Global state includes `cwd` and `olist rules`, populated by yacc parsing.

Control flow: Arguments accept optional `-d` and an inconsistent filename. Relative paths are made absolute from `getcwd`, then split into directory/name. `FindResolveFile` searches upward from the inconsistent directory until `/coda`, looking for `RESOLVE`. `yyparse` populates rule objects. `FindRule` calls each rule's `match` and `expand`. If a rule matches, main enables repair, executes commands sequentially, and disables repair.

State and persistence: Runtime state is in global rule lists and the Coda kernel/Venus repair state manipulated by `pioctl` through `rule_t`. It reads a filesystem `RESOLVE` file but does not write persistent files.

Dependencies and integration: Depends on flex/bison outputs, `ruletypes`, `path`, `wildmat`, Coda ioctl definitions, `olist`, and Coda repair interfaces.

Risks and test signals: Path construction uses fixed buffers and unbounded `strcat`/`strcpy`. `FindResolveFile` assumes `/coda` as root sentinel. Repair disable is best-effort after command execution; failures before disable can leave state dependent on Venus cleanup. Parser behavior is tested only by building/running the client and sample `resolve.eg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/resolver.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/resolver_lexer.l -->
# sources/distributed-fs/coda/coda-src/asr/resolver_lexer.l

Purpose: Flex lexer for the ASR `RESOLVE` rule language.

Important APIs/tokens: Produces tokens such as `COLON`, `SEMI_COLON`, `COMMA`, `BLANK_LINE`, `NEW_LINE`, `INTEGER`, `OBJECT_NAME`, `DEPENDENCY_NAME`, `COMMAND_NAME`, `ARG_NAME`, and `ALL`. Defines `yywrap` and global `context`.

Control flow: Whitespace is mostly skipped. Token classes depend on parser-maintained `context`: object names in file context, dependency names in dependency context, commands in command context, and arguments plus replica selectors in argument context. Brackets are accepted only in argument context. Backslash-newline joins lines, and comment/blank groups can return `BLANK_LINE`.

State and persistence: Maintains global lexer `context` and line numbers; no filesystem writes.

Dependencies and integration: Includes generated `resolver_parser.h` and `asr.h`. Its tokens drive `resolver_parser.y`, which builds `rule_t` objects.

Risks and test signals: Context-sensitive tokenization is fragile after syntax errors. Character classes are restrictive and may reject valid modern paths. The lexer uses older lex compatibility declarations and custom YYERRCODE handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/resolver_lexer.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/resolver_parser.y -->
# sources/distributed-fs/coda/coda-src/asr/resolver_parser.y

Purpose: Yacc grammar and semantic actions for ASR `RESOLVE` files.

Important APIs/grammar objects: Builds global `olist rules` by allocating `rule_t`, `command_t`, object, dependency, argument, and replica-specifier objects. `yyerror` reports line/token/context.

Control flow: A rule is `object_list : dependency_list` followed by a command list, with blank lines separating rules. Parser actions update lexer `context` before dependency, command, and argument regions. Commands collect arguments and optional `[index]` or `[all]` replica specifiers; command terminators append the current command to the current rule.

State and persistence: All parsed state is heap-allocated C++ objects in the global `rules` list. No persistence beyond reading the rule file.

Dependencies and integration: Requires lexer tokens, `asr.h`, `olist`, and `ruletypes.h`. The generated parser is compiled as C++ by the Makefile.

Risks and test signals: Global `crule` and `ccmd` mean parsing is non-reentrant. Error handling reports but returns 0, so callers need to validate parse outcomes. Empty starts allocate rules; ownership is handled later by `rule_t` destructors only if lists are destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/resolver_parser.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/ruletypes.cc -->
# sources/distributed-fs/coda/coda-src/asr/ruletypes.cc

Purpose: Implements ASR rule language runtime objects: object-name matching, dependency records, command argument expansion, command execution, repair-mode interaction, and rule execution.

Important APIs/classes/functions: `objname_t`, `depname_t`, `arg_t`, `command_t`, `rule_t`, and `expandstring`. Key methods include `match`, `GetPrefix`, `expandname`, `expandreplicas`, `execute`, `GetReplicaNames`, `enablerepair`, `disablerepair`, `GetRepInfo`, and print helpers.

Control flow: Object names are split into directory/file and matched with `wildmat`; leading `*` rules derive a prefix for `$*`. Matching a rule records inconsistent directory/name, attempts to identify inconsistent symlink metadata, and exposes replica names by temporarily enabling repair and reading child entries. Rule expansion substitutes `$*`, `$<`, `$>`, `$#`, and replica selectors, expanding `[all]` into multiple arguments. Commands fork and `execv` the configured executable, waiting for completion and stopping on first nonzero status.

State and persistence: Rule objects hold parsed lists, replica names, Coda FID metadata, and conflict path state. Persistent effects are indirect: `pioctl` toggles Venus repair mode and executed commands can mutate the filesystem.

Dependencies and integration: Depends on `olist`, `inconsist`, `venusioctl`, `vcrcommon`, `path`, `wildmat`, and Coda repair ioctls. Invoked by `resolver.cc` after parsing.

Risks and test signals: Many string expansions use fixed `MAXPATHLEN` buffers, `sprintf`, `strcpy`, and `strcat` without robust bounds checks. `command_t::execute` only supports absolute/relative executable paths as parsed; no shell is used here, but rule-controlled commands still execute with resolver privileges. `GetReplicaNames` relies on temporary repair mode and directory listing order. `expandstring` assumes the final string fits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/ruletypes.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/ruletypes.h -->
# sources/distributed-fs/coda/coda-src/asr/ruletypes.h

Purpose: Declares the C++ object model used by the ASR resolver grammar and runtime.

Important APIs/types: Classes `objname_t`, `depname_t`, `arg_t`, `command_t`, and `rule_t`; constants `NOREPLICAID` and `ALLREPLICAS`; exported `expandstring`.

Control flow and state model: `rule_t` owns object, dependency, and command lists plus match-time conflict metadata. `command_t` owns argument objects, and `arg_t` tracks replica selectors. Methods expose matching, expansion, execution, and printing.

Persistence and integration: No direct persistence. Integrates parser actions with resolver execution and Coda repair ioctls implemented in `ruletypes.cc`.

Risks and test signals: The header exposes fixed-size path/name arrays and manual ownership. Replica slots are sized by `VSG_MEMBERS`, while `ALLREPLICAS` is a sentinel value outside normal replica IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/ruletypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/wildmat.c -->
# sources/distributed-fs/coda/coda-src/asr/wildmat.c

Purpose: Shell-style wildcard matcher used by ASR object-name matching.

Important APIs/functions: Public `wildmat(char *text, char *p)` and internal recursive `DoMatch` and `Star`. Supports `?`, `*`, backslash literals, bracket classes, ranges, and `^` negation.

Control flow: `DoMatch` walks pattern and text, returning TRUE, FALSE, or ABORT. `*` delegates to `Star`, which retries the remaining pattern at successive text offsets until match or abort. Bracket classes scan until `]` and check ranges/literals.

State and persistence: Pure computation; no persistent or heap state.

Dependencies and integration: Called by `objname_t::match` in `ruletypes.cc`. Optional `TEST` main provides interactive matching.

Risks and test signals: The file itself notes malformed patterns may segfault. The optional test uses `gets` under `#ifdef TEST`, so it should not be enabled in production builds. Matching is byte-oriented and not locale/UTF aware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asr/wildmat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asrlauncher/Makefile.am -->
# sources/distributed-fs/coda/coda-src/asrlauncher/Makefile.am

Purpose: Automake recipe for the newer `asrlauncher` client-side helper.

Important APIs/build targets: Conditionally builds `sbin_PROGRAMS = asrlauncher` from `asrlauncher.c` when `BUILD_CLIENT` is enabled.

Control flow: This is a minimal build declaration without custom rules.

State and persistence: Build metadata only.

Dependencies and integration: Places `asrlauncher` in sbin for client builds; the source includes Coda configuration headers and standard libc/process APIs.

Risks and test signals: Conditional build means coverage depends on client build configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asrlauncher/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asrlauncher/asrlauncher.c -->
# sources/distributed-fs/coda/coda-src/asrlauncher/asrlauncher.c

Purpose: Launches application-specific resolution commands for Venus conflicts using `.asr` rules files and a local allow-list policy.

Important APIs/functions: `escapeString`, `nameNextRulesFile`, `checkRulesFile`, `replaceEnvVars`, `executeTriggers`, `findRule`, `executeCommands`, and `main`. Global conflict state includes path, parent, basename, volume root, conflict type, policy path, and current rules file positions.

Control flow: Venus passes conflict path, volume root, conflict type, and policy file. Main derives basename/parent, escapes shell metacharacters in conflict paths, and calls `findRule`. Rule discovery walks up from conflict path to volume root, names each `.asr`, checks the local policy allow list, opens allowed rule files, and runs backtick-delimited trigger snippets until one exits 0. The matching rule's following command lines are then expanded and piped into `/bin/sh`, with timeout polling and failure reporting.

State and persistence: Reads local policy and `.asr` files. Does not directly write persistent state, but executed shell commands can mutate Coda-visible files. Global buffers carry conflict and rule-file state.

Dependencies and integration: Invoked by Venus. Depends on Coda compile-time `SYSTYPE`, standard fork/exec/wait/signal APIs, and shell execution. Environment-like variables include `$>`, `$<`, `$@`, `$=`, `$:`, and `$!` forms for conflict metadata.

Risks and test signals: This is security-sensitive. It executes rule-controlled shell snippets, so policy and escaping are critical. `escapeString` has a bug-like write to `str[maxlen - 1]` after copying into `tempstr`, and many `strncpy` calls may not NUL-terminate. `kill(pid * -1, SIGKILL)` intends process-group cleanup but the child is not placed into a new group here. Timeout loops use `select` polling. Allow-list path comparisons require careful normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/asrlauncher/asrlauncher.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/Makefile.am -->
# sources/distributed-fs/coda/coda-src/auth2/Makefile.am

Purpose: Automake recipe for Coda auth2 client tools, server daemon, generated RPC2 stubs, and auth helper libraries.

Important APIs/build targets: Builds `libauser.la` always, client programs `au`, `clog`, `cpasswd`, `ctokens`, `cunlog` when `BUILD_CLIENT`, and server pieces `libauth2.la`, `auth2`, `initpw`, `tokentool` when `BUILD_SERVER`. Includes `auth2.rpc2` via shared RPC2 rules.

Control flow: Declares generated client/server/helper RPC2 sources as nodist library sources. Sets include paths for RPC2, base, kerndep, util, and `coda-src/al`. Configures distinct `LDADD` sets for user tools, auth2 server, token tool, and initpw.

State and persistence: Build metadata only.

Dependencies and integration: Links client auth against `libauser`, util, kerndep, base, and RPC2. Links server auth against `libauth2`, AL, util, rwcdb, base, and RPC2.

Risks and test signals: Conditional targets mean auth code coverage depends on client/server build flags. Duplicate `au` appears in `bin_PROGRAMS`, which may be harmless or an automake warning depending on tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/adduser.c -->
# sources/distributed-fs/coda/coda-src/auth2/adduser.c

Purpose: Legacy batch utility intended to add auth users from a file containing user/password records.

Important APIs/functions: `main`, `AddNewUser`, `MakeString`, `NextField`, and `NextRecord`.

Control flow: Parses `-f filename authuserid authpasswd`, initializes RPC, binds to auth server, reads the whole input file into memory, walks records, splits UID/password fields, looks up each UID's Vice ID, and calls `AuthNewUser` with an encryption key derived from the password.

State and persistence: Reads a batch file and mutates auth server password/user state through RPC. Maintains only an RPC binding and heap buffer locally.

Dependencies and integration: Includes `auth2.h` and uses auth RPC calls, but the binding call signature appears older than current `auser.h` declarations in this subset.

Risks and test signals: Contains serious legacy issues: malformed `#endif __cplusplus` syntax comments, outdated `U_BindToServer` call shape, off-by-one NUL write `area + buff.st_size + 1`, possible NULL dereference when `NextField` fails, missing return in `NextRecord`, fixed 256-byte parsing limits, and unsafe `strcpy`/`strcat`. It likely needs compile verification before use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/adduser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/au.c -->
# sources/distributed-fs/coda/coda-src/auth2/au.c

Purpose: Interactive administrative auth client for changing passwords, changing user records, creating users, and deleting users via the auth2 server.

Important APIs/functions: `main`, `SetGlobals`, and `GetVid`. It calls generated RPC stubs such as `AuthChangePasswd`, `AuthDeleteUser`, `AuthChangeUser`, `AuthNewUser`, and `AuthNameToId`.

Control flow: Parses flags (`-x`, `-h`, `-p`) and one command (`cp`, `cu`, `nu`, `du`), initializes RPC, prompts for administrator Vice name/password, resolves realm/auth servers, binds, then prompts for target user data and invokes the selected RPC.

State and persistence: Local state is input buffers and the RPC binding `AuthCid`. Persistent changes happen on the auth server's password/user database.

Dependencies and integration: Uses `auser` client library, generated `auth2.h`, RPC2, realm parsing, `codaconf`, and PRS naming constants.

Risks and test signals: Password and metadata prompts use fixed-size buffers. `AuthPortal` is parsed but not used in current server resolution path. `strncpy` into RPC key may omit NUL but keys are fixed binary buffers. It relies on server-side authorization for privileged changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/au.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/auser.c -->
# sources/distributed-fs/coda/coda-src/auth2/auser.c

Purpose: Client-side auth library used by Coda user tools to initialize RPC2, discover auth servers, bind with a username/password, obtain tokens, and change passwords.

Important APIs/functions: `U_HostToNetClearToken`, `U_NetToHostClearToken`, `U_Authenticate`, `U_ChangePassword`, `U_InitRPC`, `U_AuthErrorMsg`, `U_GetAuthServers`, `U_BindToServer`, and `U_Error`. Internal helpers include `GetAuthServers` and `TryBinding`.

Control flow: `U_Authenticate` obtains a password from stdin or `getpass`, binds to one auth server with `AUTH_METHOD_CODAUSERNAME`, calls `AuthGetTokens`, then quits/unbinds. `U_ChangePassword` binds as the acting user, resolves target name to ID, and calls `AuthChangePasswd`. Server discovery uses realm SRV/config lookup unless a host override is supplied. `U_BindToServer` iterates server addresses until success or authentication rejection.

State and persistence: Maintains only transient RPC2 bindings and password buffers. Token persistence is handled by callers such as `clog` and `avenus`.

Dependencies and integration: Depends on RPC2/LWP, generated `auth2.h`, `prs.h`, `auth2.common.h`, Coda config, and realm parsing. Used by `clog`, `au`, and other client tools.

Risks and test signals: Password strings remain in stack buffers after use. Non-interactive password reading assumes `strlen(passwd) > 0` before trimming newline. Uses `RPC2_XOR` encryption type, which is legacy. Error reporting preserves RPC2 and auth return domains through `U_Error`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/auser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/auser.h -->
# sources/distributed-fs/coda/coda-src/auth2/auser.h

Purpose: Public header for the auth2 client helper library.

Important APIs/types: Declares token byte-order helpers, `U_Authenticate`, `U_ChangePassword`, `U_InitRPC`, `U_AuthErrorMsg`, `U_GetAuthServers`, `U_BindToServer`, and `U_Error`.

Control flow and state model: The API separates server discovery, binding, token retrieval, and error formatting so command-line tools can compose these operations.

Persistence and integration: No persistence. Integrates auth tools with RPC2-generated auth stubs and token storage helpers.

Risks and test signals: Function signatures expose raw password pointers and lengths; callers are responsible for clearing sensitive data and freeing `RPC2_addrinfo` lists returned by `U_GetAuthServers`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/auser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/auth2.c -->
# sources/distributed-fs/coda/coda-src/auth2/auth2.c

Purpose: Coda auth2 server daemon. It authenticates users against the password database, issues Coda tokens, and exposes RPCs for password/user administration.

Important APIs/functions: Startup helpers `ReadConfigFile`, `InitGlobals`, `ReopenLog`, `InitSignals`, `InitRPC`, `CheckTokenKey`; RPC/auth callbacks `GetKeys`, `LogFailures`; service routines `S_AuthNewConn`, `S_AuthQuit`, `S_AuthGetTokens`, `S_AuthChangePasswd`, `S_AuthNewUser`, `S_AuthDeleteUser`, `S_AuthChangeUser`, `S_AuthNameToId`; helper `GetViceId`.

Control flow: Main reads server config, sets token-key path, changes to auth2 directory, daemonizes unless debugging, initializes logging/signals/RPC/AL/password support, then loops on `RPC2_GetRequest`. It rejects unauthenticated requests, dispatches generated RPC handlers, and handles RPC errors. `GetKeys` accepts only `AUTH_METHOD_CODAUSERNAME` and verifies the identity maps to a Vice ID. Token issuance refreshes the auth2 key when the key file mtime changes and creates a 25-hour token.

State and persistence: Reads `db/auth2.tk`, password files via pwsupport, `/vice/db/scm` and `/vice/hostname` to decide read-only mode, writes `AuthLog` and `pid`, and stores per-connection `UserInfo` in a fixed ring of 10 client slots. Mutating RPCs update password/user database through pwsupport.

Dependencies and integration: Uses RPC2/LWP, generated auth2 RPC stubs, AL/PRS identity lookup, pwsupport, `codatoken`, Coda config and service lookup. Server-side deletion checks administrator status through pwsupport helpers.

Risks and test signals: `readoneline` checks `buf[len] == '\n'` instead of `buf[len - 1]`, so newline stripping is wrong. Client slot eviction unbinds older connections in a ring. `S_AuthNewUser` and `S_AuthChangeUser` do not check `CheckOnly` in this file. Token key reload is mtime-based and fatal if the file is missing. Sensitive keys and passwords are not explicitly wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/auth2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/auth2.common.h -->
# sources/distributed-fs/coda/coda-src/auth2/auth2.common.h

Purpose: Defines per-connection auth server state shared by auth2 implementation and helpers.

Important APIs/types: `struct UserInfo` with `RPC2_Handle handle`, `ViceId`, `HasQuit`, `PRS_InternalCPS *UserCPS`, and `LastUsed`.

Control flow and state model: Auth server allocates one `UserInfo` per accepted connection, attaches it as an RPC2 private pointer, updates `LastUsed`, and honors `HasQuit` in service routines.

Persistence and integration: In-memory only. Integrates auth2 server RPC routines with AL CPS and RPC2 connection lifecycle.

Risks and test signals: `LastUsed` is an `int` despite storing `time_t`. `UserCPS` ownership must be released on unbind/termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/auth2.common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/avenus.c -->
# sources/distributed-fs/coda/coda-src/auth2/avenus.c

Purpose: Client helper library for sending, retrieving, and deleting auth tokens in Venus through Coda pioctls.

Important APIs/functions: `U_SetLocalTokens`, `U_GetLocalTokens`, and `U_DeleteLocalTokens`. Internal `venusbuff` packages clear/secret token sizes, token data, and realm.

Control flow: `U_SetLocalTokens` fills a `venusbuff` and sends `_VICEIOCTL(3)`. `U_GetLocalTokens` passes the realm to `_VICEIOCTL(8)`, validates returned token sizes, and copies tokens out. `U_DeleteLocalTokens` sends the realm to `_VICEIOCTL(9)`.

State and persistence: No local persistence; Venus stores or removes token state. Token file persistence is handled elsewhere (`tokenfile.c`, not in this subset).

Dependencies and integration: Used by `clog` and related client utilities. Depends on Coda kernel/Venus pioctl ABI, `auth2.h`, and config constants.

Risks and test signals: `strncpy(inbuff.realm, realm, MAXHOSTNAMELEN)` may omit NUL on long realm names. Raw numeric ioctl constants are less self-documenting than named constants. Return semantics differ on Cygwin vs Unix for get-token failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/avenus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/avenus.h -->
# sources/distributed-fs/coda/coda-src/auth2/avenus.h

Purpose: Public declarations for Venus token management helpers.

Important APIs/types: Declares `U_DeleteLocalTokens`, `U_GetLocalTokens`, and `U_SetLocalTokens` over `ClearToken`, `EncryptedSecretToken`, and realm strings.

Control flow and state model: Callers set tokens after authentication, optionally fetch them for verification, or delete them for logout.

Persistence and integration: Integrates auth clients with Venus token state via functions implemented in `avenus.c`.

Risks and test signals: Header does not document ioctl side effects or realm length constraints; callers need to handle negative returns and token-size validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/avenus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/avice.c -->
# sources/distributed-fs/coda/coda-src/auth2/avice.c

Purpose: Server-side token validation helper used by Vice file servers to derive RPC2 handshake/session keys from Coda tokens.

Important APIs/functions: `GetKeysFromToken` and `SetServerKeys`. Static state tracks two derived auth2 keys and validity flags.

Control flow: `SetServerKeys` derives auth2 keys from one or two configured server keys. `GetKeysFromToken` allows unauthenticated open-kimono calls when `cIdent` is NULL, validates token length, tries key1 then key2 with `validate_CodaToken`, checks expiry, copies the token handshake key to `hKey`, generates a fresh server secret `sKey`, and overwrites `cIdent->SeqBody` with a host-order `SecretToken` for new-connection handling.

State and persistence: Holds derived keys in static memory only. Persistent key source is supplied by callers from server configuration.

Dependencies and integration: Depends on RPC2, `getsecret`, auth token definitions, and `codatoken`. Intended as the RPC2 authentication callback for file-server request loops.

Risks and test signals: Expires based on `endtimestamp` from token validation, but a log line references fields in `st` before all are set. Static key state is process-global. Sensitive derived keys are not wiped on replacement. Accepting NULL `cIdent` intentionally allows unauthenticated bindings, so callers must enforce operation-level policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/avice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/avice.h -->
# sources/distributed-fs/coda/coda-src/auth2/avice.h

Purpose: Header for Vice-side auth2 token validation helpers.

Important APIs/types: Declares `GetKeysFromToken` RPC2 auth callback and `SetServerKeys` key-configuration routine.

Control flow and state model: File servers configure current/previous server keys, then pass `GetKeysFromToken` to RPC2 request processing to authenticate token-bearing clients.

Persistence and integration: No direct persistence. Integrates Vice file-server authentication with `codatoken` and RPC2.

Risks and test signals: The interface accepts raw `RPC2_EncryptionKey` pointers; ownership and lifetime are external. Callers must decide whether open-kimono bindings are acceptable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/avice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/clog.c -->
# sources/distributed-fs/coda/coda-src/auth2/clog.c

Purpose: User login tool that obtains Coda auth tokens from auth2 or a file, sends them to Venus, and optionally verifies local token round-trip.

Important APIs/functions: `printusage` and `main`. It uses `U_GetAuthServers`, `U_Authenticate`, `U_SetLocalTokens`, `U_GetLocalTokens`, `WriteTokenToFile`, and `ReadTokenFromFile`.

Control flow: Parses flags for quiet/test modes, host override, token input/output files, run-as user, and username/realm. It derives username from effective UID when omitted, reads realm config, initializes RPC, obtains or reads tokens, optionally writes them to a file, sends them to Venus, and in test mode fetches and compares tokens.

State and persistence: Writes optional token files and updates Venus token state. Reads `venus.conf`/`auth2.conf`, realm data, and optional input token file.

Dependencies and integration: Uses `auser`, `avenus`, `tokenfile`, RPC2/LWP, Coda config, and realm parsing. It is the main end-user bridge between auth2 and Venus.

Risks and test signals: `-as` calls `setuid` after `getpwnam` without reporting failure. Token files are sensitive and file-mode handling is in `tokenfile.c` outside this subset. Non-tty stdin disables interactive password prompts. Test mode compares exact token structs and prints byte-order-converted values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/clog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/codatoken.c -->
# sources/distributed-fs/coda/coda-src/auth2/codatoken.c

Purpose: Generates, encrypts, authenticates, and validates Coda authentication tokens.

Important APIs/functions: Public `getauth2key`, `generate_CodaToken`, and `validate_CodaToken`; internal `generate_Secret` and `validate_Secret`.

Control flow: `getauth2key` derives a 48-byte key from a token key using secure PBKDF. Token generation builds a clear token with Vice ID, start time backdated 15 minutes, end time, random handshake key, and encrypted secret token. The secret payload contains magic bytes, key length, identity length, expiry, session key, identity, padding, AES-CBC encryption, and AES-XCBC authentication truncated to 8 bytes. Validation checks token size, MAC, block alignment, decrypts, validates magic/header/padding, extracts key/identity/end time, parses Vice ID, and returns the handshake key.

State and persistence: Stateless except for secure library initialization/randomness. Token blobs are consumed by auth2 and Vice; durable storage is handled by token files or Venus.

Dependencies and integration: Depends on `rpc2/secure.h`, RPC2 token types from `auth2.h`, and server/client code in `auth2.c` and `avice.c`.

Risks and test signals: Some validation error paths return before freeing encryption/auth contexts, causing small leaks. Identity is NUL-terminated inside the decrypted token buffer, relying on unused checksum space. `assert` is used for algorithm availability and context init in generation. Expiration enforcement happens in callers such as `avice.c`, not in `validate_CodaToken`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/codatoken.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/codatoken.h -->
# sources/distributed-fs/coda/coda-src/auth2/codatoken.h

Purpose: Public header for auth2 key derivation and Coda token generation/validation.

Important APIs/types: Defines `AUTH2KEYSIZE` as 48 and declares `getauth2key`, `generate_CodaToken`, and `validate_CodaToken`.

Control flow and state model: Callers derive an auth2 key from configured token material, generate clear/secret tokens for clients, or validate secret tokens to recover Vice ID, end time, and session key.

Persistence and integration: Integrates auth2 server token issuance with Vice server validation. Token storage itself is external.

Risks and test signals: The API assumes fixed-size `EncryptedSecretToken` and `RPC2_EncryptionKey` from `auth2.h`. Callers must check expiry after validation and protect the derived `auth2key`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/auth2/codatoken.h -->
