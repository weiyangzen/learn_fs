# subset-b-007845 research

Grouped research for OrangeFS common misc configuration, state-machine, and string utility sources. Each file section is marker-wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/server-config.c -->
# sources/distributed-fs/orangefs/src/common/misc/server-config.c

## Purpose

`server-config.c` is the OrangeFS/PVFS2 configuration parser and runtime accessor implementation for server and client-visible filesystem configuration. It binds dotconf option names to callback handlers, builds `server_configuration_s` and nested `filesystem_configuration_s` objects, validates alias/range/filesystem relationships, exposes lookup helpers used by server startup and request paths, and, when Trove support is compiled, creates or removes on-disk storage spaces from parsed configuration.

The file is stateful in the sense that parsing mutates one caller-provided `server_configuration_s`. It is not a persistent store itself, but it reads and caches the config file contents, keeps parsed strings/lists/ranges in heap-owned structures, and passes storage-space creation/removal requests to `pvfs2_mkspace()` and `pvfs2_rmspace()`.

## Important APIs and functions

- `PINT_parse_config(config_obj, global_config_filename, server_alias_name, server_flag)` zeroes the caller's config object, applies built-in defaults, caches the fs.conf file, creates a dotconf parser with the local `options[]` table, runs the parse loop, resolves the selected server alias to `host_id`, and checks required fields such as storage paths, BMI modules, flow modules, performance settings, and security key/cert paths depending on compile flags.
- `PINT_config_release(config_s)` frees heap allocations owned by a parsed config, including aliases, filesystem lists, cached file data, module strings, export lists, security paths, and trusted-network data.
- `PINT_config_is_valid_configuration()` validates global fields and all configured filesystems, primarily checking that each root handle is in one configured metadata handle range.
- `PINT_config_get_host_addr_ptr()` and `PINT_config_get_host_alias_ptr()` translate between host aliases and BMI address strings. Returned pointers are borrowed from the config object.
- `PINT_config_get_meta_handle_range_str()`, `PINT_config_get_data_handle_range_str()`, and `PINT_config_get_merged_handle_range_str()` return host-specific handle range strings for a filesystem. The merged version allocates a new string for the caller to free.
- `PINT_config_get_meta_handle_extent_array()` copies the current host's metadata handle extent array for a filesystem id into caller-owned memory.
- `PINT_config_find_fs_name()`, `PINT_config_find_fs_id()`, `PINT_config_get_fs_id_by_fs_name()`, and `PINT_config_get_filesystems()` are runtime lookup helpers over the parsed filesystem list.
- `PINT_config_trim_filesystems_except()` replaces the full filesystem list with a deep copy of one selected filesystem, preserving alias pointers and duplicating the selected filesystem's nested fields.
- `PINT_config_get_fs_key()` decodes a filesystem `SecretKey` from base64 with OpenSSL when available. Without OpenSSL it reports `-PVFS_ENOSYS`.
- Trove-gated APIs `PINT_config_pvfs2_mkspace()`, `PINT_config_pvfs2_rmspace()`, `PINT_config_get_trove_sync_meta()`, and `PINT_config_get_trove_sync_data()` integrate parsed configuration with storage creation/removal and storage sync hints.

Most other functions are dotconf callbacks named after config options, for example `get_bmi_module_list`, `get_range_list`, `get_root_squash`, `get_trove_method`, `get_db_max_size`, `get_ldap_search_mode`, and context enter/exit callbacks.

## Control flow

The central control path starts in `PINT_parse_config()`. It initializes defaults on `server_configuration_s`, reads the config file into `fs_config_buf`, creates a `configfile_t` with the local `options[]` array, installs `errorhandler` and `contextchecker`, then runs `PINT_dotconf_command_loop()`. The dotconf table encodes each option's name, argument type, callback, legal context mask, and default. `contextchecker()` rejects options used outside the current context mask.

Context callbacks set `config_s->configuration_context` as dotconf enters and leaves nested sections. `<Defaults>` also triggers dotconf defaults for both security and default contexts. `<FileSystem>` allocates a new zeroed `filesystem_configuration_s`, fills base filesystem defaults, inserts it at the head of `config_s->file_systems`, and applies filesystem defaults. `</FileSystem>` checks that name, collection id, root handle, and both handle-range lists were supplied. `<ServerOptions>` applies defaults and then option callbacks ignore values unless `check_this_server()` matched the configured alias and set `my_server_options`.

Option callbacks mutate either the global `server_configuration_s` or the current filesystem at the head of `file_systems`. List options such as aliases, module lists, export host lists, precreate sizes, and handle ranges allocate new arrays or strings. Handle range parsing validates aliases, validates the textual range characters, either finds an existing mapping or allocates a new mapping, merges repeated ranges with `PINT_merge_handle_range_strs()`, and rebuilds `PVFS_handle_extent_array` with `PINT_parse_handle_ranges()`.

After dotconf completes, `PINT_parse_config()` resolves `server_alias_name` through the alias list and records `host_id` and `host_index`. It then enforces server-side required fields. Later runtime helper calls walk `PINT_llist` lists linearly to retrieve aliases, filesystems, and range mappings.

## State and persistence behavior

The parser stores durable runtime state in heap allocations reachable from `server_configuration_s`. Ownership is mostly clear: `PINT_config_release()` owns strings and lists directly attached to config and filesystem objects. `host_handle_mapping_s.alias_mapping` is intentionally a borrowed pointer into the global alias list and is not freed by mapping cleanup. `PINT_config_get_*_ptr()` helpers return borrowed pointers, while `PINT_config_get_merged_handle_range_str()` and `PINT_config_get_meta_handle_extent_array()` allocate caller-owned results.

The file itself does not write config persistence. It caches the source config file in RAM through `cache_config_files()` so getconfig-style operations can return the original config without rereading the file. With `__PVFS2_TROVE_SUPPORT__`, `PINT_config_pvfs2_mkspace()` and `PINT_config_pvfs2_rmspace()` cause persistent storage side effects under parsed data and metadata paths.

## Dependencies and integration points

Dependencies include dotconf (`PINT_dotconf_create`, defaults, command loop), OrangeFS linked lists (`PINT_llist_*`), gossip logging, PVFS and Trove types, extent utilities (`PINT_create_extent_list`, `PINT_handle_in_extent_list`, `PINT_release_extent_list`), string utilities (`PINT_split_string_list`, `PINT_parse_handle_ranges`, `PINT_merge_handle_range_strs`), mkspace/rmspace storage helpers, and OpenSSL BIO base64 decoding when compiled.

Integration points are broad: server startup uses this parser to load fs.conf and server-specific options, storage initialization uses range and Trove settings, request paths use filesystem and alias lookup helpers, security layers use trusted ports/networks, key paths, cert settings, LDAP options, and filesystem secret keys, and flow/BMI/job layers consume module lists, timeouts, buffer sizes, and retry settings.

## Risks and edge cases

- Several string accumulation callbacks use fixed 512 or 2048 byte buffers with `strncat()` and hand-maintained lengths. They avoid obvious unbounded `strcat`, but the length accounting is inconsistent enough that oversized config values deserve tests.
- Many allocation failures are guarded with `assert()` rather than graceful error returns, especially in deep-copy paths. Release builds built with assertions disabled could continue with null pointers in some paths.
- `PINT_split_string_list()` can return early on empty comma elements without freeing already allocated token storage, so malformed comma lists can leak transient allocations.
- `get_range_list()` assumes alias/range arguments come in pairs and increments `i` inside the loop. Odd argument counts rely on dotconf/list behavior and assertions rather than explicit validation.
- `get_attr_cache_keywords_list()` deduplicates by `strstr(buf, rtok)`, so short key names could match substrings instead of exact comma-delimited tokens if future key names overlap.
- The parser mutates one config object and stores parse context in that object, so it is not reentrant for a shared object.
- `cache_config_files()` uses `PWD` rather than `getcwd()` on non-Windows fallback paths and only retries in unusual stat-error cases, so caller environment can affect diagnostics.
- Some callbacks treat invalid values as warnings and keep defaults, while others fail the parse. This is intentional legacy behavior but makes validation uneven.

## Test signals

Useful tests should parse representative fs.conf files covering Defaults, Security, LDAP, Aliases, ServerOptions, multiple FileSystem sections, StorageHints, ExportOptions, Distribution, and repeated Range entries. Assertions should check server-specific override gating, required-field failures, root-handle-in-meta-range validation, alias duplicate rejection, merged range strings and extent arrays, release after partial parse failure, trusted-network netmask parsing, invalid yes/no options, precreate list length enforcement, DBMaxSize context behavior, and Trove mkspace/rmspace argument selection with root handle only on the responsible metadata server.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/server-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/server-config.h -->
# sources/distributed-fs/orangefs/src/common/misc/server-config.h

## Purpose

`server-config.h` declares the public data structures and accessors for parsed OrangeFS server configuration. It is the contract shared by the config parser, server config manager, server startup code, storage setup, security code, and callers that need filesystem, alias, handle-range, module, timeout, and storage hint settings.

## Important APIs, types, and fields

- Context bit constants `CTX_GLOBAL`, `CTX_DEFAULTS`, `CTX_ALIASES`, `CTX_FILESYSTEM`, `CTX_METAHANDLERANGES`, `CTX_DATAHANDLERANGES`, `CTX_STORAGEHINTS`, `CTX_DISTRIBUTION`, `CTX_SECURITY`, `CTX_EXPORT`, `CTX_SERVER_OPTIONS`, and `CTX_LDAP` define dotconf legality masks and parser state values.
- `phys_server_desc_s` stores a resolved BMI address, address string, and server type.
- `host_alias_s` maps a human server alias to one BMI URL-like address string.
- `host_handle_mapping_s` binds an alias to a textual handle range and its `PVFS_handle_extent_array` representation for wire-level create/mkdir and local range checks.
- `filesystem_configuration_s` stores per-filesystem identity, root handle, metadata and data handle ranges, flow/encoding defaults, storage hints, export policy lists/netmasks, anonymous uid/gid, file stuffing, Direct I/O settings, and LMDB sizing.
- `distribution_param_configuration` and `distribution_configuration` represent configured default distribution name and integer parameters.
- `server_configuration_s` is the top-level parsed configuration: selected server alias and host id, storage paths, cached config file, request/job/retry/perf settings, precreate thresholds, logging, BMI/flow modules, TCP settings, trusted connection settings when enabled, parser context, alias and filesystem lists, distribution defaults, DB/Trove settings, security key/cert/LDAP/timeouts, private parser data, and distributed directory tuning.

The declared functions include `PINT_parse_config`, `PINT_config_release`, optional trusted-port/network accessors, alias lookups, handle range and extent queries, configuration validation, filesystem lookup and trimming helpers, filesystem secret key retrieval, and optional Trove storage setup/removal and sync-mode helpers.

## Control flow and ownership contract

Callers allocate `server_configuration_s`, pass it to `PINT_parse_config()`, use getters and direct struct fields while the object is live, and eventually call `PINT_config_release()`. Most returned strings from getters are borrowed pointers into the config object. The exception called out by the implementation is merged handle ranges, which allocate a new string. `PINT_config_get_meta_handle_extent_array()` allocates an extent array for the caller to free.

`server_configuration_s.private_data` is available to the parser implementation. `configuration_context`, `prev_context`, and `my_server_options` are parser execution state and should not be treated as stable user configuration.

## State and persistence behavior

The header describes in-memory state only. Persistent behavior is exposed indirectly under `__PVFS2_TROVE_SUPPORT__` through `PINT_config_pvfs2_mkspace()` and `PINT_config_pvfs2_rmspace()`, which use parsed paths and filesystem definitions to create or remove Trove storage spaces.

## Dependencies and integration points

The header depends on PVFS core types, `PINT_llist`, gossip logging, and optionally Trove. It is included by `server-config.c`, config manager code, state-machine helper macros through `server-config-mgr.h`, and components that need parsed configuration for networking, storage, security, flow, and filesystem lookup.

## Risks and edge cases

- The structs expose many mutable pointers directly, so callers can accidentally break parser-owned invariants if they modify fields instead of using parser helpers.
- `host_handle_mapping_s.alias_mapping` is a borrowed pointer into `server_configuration_s.host_aliases`; copying or freeing these objects independently requires care.
- Arrays such as export host lists, netmasks, precreate values, and extent arrays depend on companion count fields. Tests and callers must keep counts synchronized.
- Conditional fields under `USE_TRUSTED` and APIs under `__PVFS2_TROVE_SUPPORT__` change struct layout and available functions by build configuration.

## Test signals

Compile coverage should include trusted and non-trusted builds, Trove and non-Trove builds, and security-key/cert combinations. ABI-sensitive tests should verify that parsed configs can be released after partial and full initialization, copied or trimmed through the implementation helpers, and used by callers without taking ownership of borrowed pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/server-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/state-machine-fns.c -->
# sources/distributed-fs/orangefs/src/common/misc/state-machine-fns.c

## Purpose

`state-machine-fns.c` implements the generic OrangeFS state-machine executor declared by `state-machine.h`. It drives current state invocation, transition-table lookup, nested-machine stack handling, parallel child state-machine starts, frame stack management, cancellation/termination flags, and allocation/freeing of `PINT_smcb` control blocks.

## Important APIs and functions

- `PINT_state_machine_halt()` is a stub that returns 0 for shutdown compatibility.
- `PINT_state_machine_terminate(smcb, r)` notifies a parent SMCB when a child finishes, copies the child frame error into the matching parent frame, decrements `children_running`, posts a `job_null()` to resume the parent when the last child exits, and calls the SMCB termination callback.
- `PINT_state_machine_invoke(smcb, r)` validates that the current state is runnable, logs entry/exit, calls the state's action function, interprets `SM_ACTION_*`, marks `op_terminate` on terminate, and starts PJMP child frames after a complete parallel-jump state.
- `PINT_state_machine_start(smcb, r)` marks the operation initially immediate, sets the base frame, invokes the first state, and continues while states complete synchronously.
- `PINT_state_machine_next(smcb, r)` uses the current state's transition table and `r->error_code` to choose the next state, handles `SM_TERM`, `SM_RETURN`, nested `SM_JUMP`, cancellation, and loops while invoked states complete.
- `PINT_state_machine_continue(smcb, r)` advances the machine and calls termination cleanup when the next step returns terminate.
- `PINT_state_machine_locate(smcb)` resolves `smcb->op` through the caller-provided `op_get_state_machine` callback, follows initial nested jumps, and sets `current_state`.
- `PINT_smcb_alloc()` allocates and initializes a control block, optionally allocates an initial zeroed frame, stores operation lookup and terminate callbacks, and locates the initial machine.
- `PINT_smcb_free()` frees all frame entries and only frees frame payloads whose `task_id` is zero; nonzero child/task frames are treated as externally owned.
- `PINT_sm_frame()`, `PINT_sm_push_frame()`, and `PINT_sm_pop_frame()` implement indexed access to a qlist-backed frame stack.
- `PINT_smcb_set_op()`, `PINT_smcb_op()`, `PINT_smcb_set_complete()`, `PINT_smcb_complete()`, `PINT_smcb_set_cancelled()`, `PINT_smcb_cancelled()`, `PINT_smcb_immediate_completion()`, and `PINT_smcb_invalid_op()` expose control flags and op validation.

## Control flow

A caller allocates an SMCB with `PINT_smcb_alloc()` and a machine resolver. `PINT_state_machine_locate()` stores the first runnable state, pushing return states for leading nested jumps. `PINT_state_machine_start()` invokes the first action and then uses `PINT_state_machine_continue()` to process synchronous completions. Each state action writes a result into `job_status_s`, especially `error_code`, and returns `SM_ACTION_DEFERRED`, `SM_ACTION_COMPLETE`, or `SM_ACTION_TERMINATE`.

When a state completes, `PINT_state_machine_next()` searches the transition table for an entry matching `r->error_code`, defaulting to the entry whose `return_value` is `DEFAULT_ERROR`. `SM_RETURN` pops the nested state stack and continues from the saved parent state. `SM_JUMP` pushes the current state and enters a nested machine's first state. `SM_TERM` or `op_terminate` ends the machine. Deferred states stop execution until an external job completion calls continue again.

Parallel jump states (`SM_PJMP`) run their action first. If complete, `PINT_sm_start_child_frames()` counts frames above the current frame, creates child SMCBs for each, maps task ids through the state's PJMP table, starts children, and returns deferred if any children were launched. Child termination updates the parent and schedules a null job to resume the parent after the last child.

## State and persistence behavior

All state is in memory. `PINT_smcb` tracks the current state, nested state stack, frame qlist, base frame index, operation id and flags, parent-child relationships, running child count, job context, termination callback, user pointer, and immediate-completion flag. There is no persistent storage.

Frame ownership is task-id dependent: task id zero frames are freed by `PINT_smcb_free()`, while nonzero task frames are not. Child SMCBs push references to existing frame payloads, so parent and child lifetimes must be coordinated by the state-machine protocol.

## Dependencies and integration points

This file depends on qlist, gossip debug logging, PVFS op constants, job null scheduling, `job_status_s`, and client/server state-machine definitions. It is a common executor reused by client and server generated state tables. The user-provided `PINT_state_machine_complete()` is declared in the header, while termination behavior is supplied per SMCB through a callback.

## Risks and edge cases

- Transition table lookup assumes every table eventually has a `DEFAULT_ERROR` sentinel; a malformed table can walk off the end.
- Nested state depth is limited by `PINT_STATE_STACK_SIZE` and overflow is guarded only by `assert()`.
- `PINT_sm_pop_frame()` unconditionally writes `*task_id` and `*error_code`, so callers must pass non-null pointers.
- PJMP child start logs errors when child start returns negative but does not undo already-started children or decrement `children_running` for that failure path.
- Parent frame error propagation matches child current frame pointer against parent frame payload pointers. Duplicate frame pointers or unexpected frame ownership could propagate errors to the wrong entry.
- The executor is not internally synchronized. Callers must serialize access to each SMCB from the job/event system.

## Test signals

Focused tests should build small synthetic state machines for complete, deferred, terminate, default-error, nested jump/return, cancellation, and PJMP child flows. Tests should assert immediate-completion flag transitions, parent resume after last child, frame indexing around nested base frames, task-id ownership on free, invalid op classification, and failure behavior for missing resolver or malformed operation ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/state-machine-fns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/state-machine.h -->
# sources/distributed-fs/orangefs/src/common/misc/state-machine.h

## Purpose

`state-machine.h` defines the generic state-machine model used by OrangeFS client and server operations. It supplies state codes, transition and parallel-jump table shapes, the `PINT_smcb` control block, frame access constants, executor prototypes, and utility macros for logging and server-to-server message array initialization.

## Important APIs, types, and macros

- `enum PINT_state_code` defines state/table flags: `SM_NONE`, `SM_NEXT`, `SM_RETURN`, `SM_EXTERN`, `SM_NESTED`, `SM_JUMP`, `SM_TERM`, `SM_PJMP`, and `SM_RUN`.
- `PINT_serv_init_msgarray_params(sm_p, __fsid)` initializes server-to-server msgpair parameters from the active server config, falling back to client job timeout/retry defaults when no config is available.
- `PINT_STATE_STACK_SIZE` fixes nested state-machine stack depth at 8.
- `struct PINT_state_stack_s` stores a saved state and previous base frame for nested returns.
- `PINT_smcb` is the per-running-operation control block with execution state, frame qlist, operation lookup callback, operation identifiers and flags, parent-child tracking, job context, terminate callback, user pointer, and immediate-completion marker.
- `struct PINT_state_machine_s` names a machine and points at its first state.
- `struct PINT_state_s` describes one state: name, parent machine, flag, action function or nested machine pointer, parallel-jump table, and transition table.
- `struct PINT_pjmp_tbl_s` maps task return values to child machines for parallel jumps.
- `struct PINT_tran_tbl_s` maps state return values to next states or terminal/return behavior.
- `PINT_sm_action` defines action return values: deferred, complete, terminate, and catastrophic error.
- `SM_ACTION_STRING`, `SM_ACTION_ISERR`, and `SM_ACTION_ISVALID` support validation and diagnostics.
- `JMP_NOT_READY` and `DEFAULT_ERROR` are common transition values. `SM_STATE_RETURN` and `SM_NESTED_STATE` are sentinel-like helpers used by generated tables.
- Prototypes expose state-machine execution, SMCB allocation/free, op and flag helpers, and frame stack functions.

## Control flow contract

State definitions pair action return values with transition tables. The executor calls an action function, then uses `job_status_s.error_code` to choose a transition. `SM_JUMP` enters nested machines while preserving a return state and base-frame location. `SM_RETURN` returns from a nested machine. `SM_PJMP` is for parallel child state-machine launches using pushed frames and a PJMP table. `SM_TERM` and `SM_ACTION_TERMINATE` together mark operation termination.

The `PINT_state_machine_current_machine_name()` macro assumes machine names begin with `pvfs2_` and strips that prefix for diagnostics. State and machine pointers must remain valid for the lifetime of every SMCB using them.

## State and persistence behavior

This header defines only in-memory execution state. It does not persist state-machine progress. Each `PINT_smcb` owns its frame list entries and, depending on task id, may own frame payload memory as implemented in `state-machine-fns.c`.

## Dependencies and integration points

The header depends on `job.h`, `quicklist.h`, `server-config-mgr.h`, and PVFS internal definitions. It is included by common executor code and by generated or handwritten client/server state-machine tables. The server msgarray macro integrates state-machine operations with the active `server_configuration_s` to pick timeouts and retry behavior.

## Risks and edge cases

- The name-stripping macro blindly advances six characters into machine names, so nonconforming names produce misleading diagnostics.
- Stack depth is fixed and enforced in implementation with assertions.
- `PINT_serv_init_msgarray_params()` references `server_job_context` and expects a surrounding server-side compilation context.
- The exposed `PINT_smcb` struct invites direct field mutation by callers, which can bypass invariants maintained by the helper functions.

## Test signals

Compile tests should cover client and server users because the header pulls in server config manager state for msgarray initialization. Runtime tests should exercise machines with nested jumps, returns, PJMP tables, terminal transitions, cancellation, and invalid action returns while checking that current machine/state name macros remain safe for expected naming conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/state-machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/str-utils.c -->
# sources/distributed-fs/orangefs/src/common/misc/str-utils.c

## Purpose

`str-utils.c` implements shared string and path helpers for OrangeFS. It covers path merging and normalization, path segment iteration, base-name and prefix handling, comma-list tokenization, handle-range parsing and merging, fallback libc functions for platforms missing `strnlen` or `strstr`, and key/value string splitting.

## Important APIs and functions

- `PINT_merged_path_len()` computes the required length for joining two paths with one slash and a terminator.
- `PINT_merge_paths()` joins an absolute base path, slash, and relative component into a caller-supplied `PVFS_PATH_MAX + 1` buffer.
- `PINT_is_dot_dir()` detects `"."` and `".."`.
- `PINT_string_rm_extra_slashes()` and `PINT_string_rm_extra_slashes_rts()` collapse repeated slashes in place, optionally removing a trailing slash.
- `PINT_string_count_segments()` counts non-empty path segments using `PINT_string_next_segment()`.
- `PINT_get_base_dir()` returns the parent directory of an absolute path.
- `PINT_string_next_segment()` iterates path segments by temporarily replacing separators with NUL bytes and restoring them on the next call.
- `PINT_parse_handle_ranges()` parses textual handle extents such as `1-10,20-30` into `PVFS_handle_extent` values across repeated calls using an integer status offset.
- `PINT_get_path_element()` copies the Nth path segment into an output buffer.
- `PINT_get_next_path()` allocates a copy of the remainder of a path after a requested number of slash separators.
- `PINT_split_string_list()` splits comma-delimited strings into an allocated token array, and `PINT_free_string_list()` frees it.
- `PINT_remove_base_dir()` copies the last component from an absolute path.
- `PINT_remove_dir_prefix()` validates a qualified/expanded PVFS path, checks an absolute prefix, updates the path object's mount-point flags, and points `pvfs_path` at the suffix inside the input pathname.
- `PINT_merge_handle_range_strs()` allocates `"range1,range2"`.
- Fallback `strnlen()` and `strstr()` are compiled only when platform probes say they are missing.
- `PINT_split_keyvals()` parses comma-separated `key:value` pairs into separate allocated key and value arrays.

## Control flow

Path normalization functions are mostly in-place linear scans. Segment iteration stores state outside the function through `inout_segp` and `opaquep`: the first call starts at `pathname`, later calls restore the slash previously replaced by NUL, skip separators, return the next segment start, and either save the next separator or mark end-of-string with `NULL`.

Handle-range parsing uses the caller's `status` offset as an opaque cursor. Each call parses the next unsigned integer as both first and last, optionally parses a range end after `-`, consumes whitespace and an optional comma, updates `status`, and returns 1 for a found extent, 0 for no more ranges, or -1 for invalid arguments/format.

List and key/value splitters first count expected elements, allocate pointer arrays, then allocate/copy individual strings. `PINT_remove_dir_prefix()` is unusual because it calls `PVFS_path_from_expanded()`, checks path magic and flags, then mutates fields on the returned path object rather than returning the suffix directly.

## State and persistence behavior

These helpers do not persist data. They either mutate caller-owned strings in place, write into caller-provided buffers, or allocate caller-owned arrays/strings. `PINT_string_next_segment()` temporarily mutates the pathname while iteration is active and restores the last slash on the next call. `PINT_remove_dir_prefix()` mutates state inside a `PVFS_path_t` associated with the input path conversion.

## Dependencies and integration points

The file depends on PVFS limits and error codes, `PVFS_handle_extent`, and `pvfs-path.h`. It is used by server config parsing for comma lists, handle ranges, and merged range strings, and by broader path resolution code that needs slash normalization, segment extraction, prefix removal, and key/value option parsing.

## Risks and edge cases

- `PINT_merged_path_len()` returns `short`, which can truncate for long input even though PVFS paths can be much larger than `SHRT_MAX` in principle.
- `PINT_merge_paths()` uses `strcat()` after checking combined length, so the destination must truly be at least `PVFS_PATH_MAX + 1`.
- `PINT_string_count_segments()` mutates and restores the input through `PINT_string_next_segment()`; callers may not expect a counting function to write to its argument.
- `PINT_get_path_element()` copies into `local_pathname[PVFS_NAME_MAX]`, not `PVFS_PATH_MAX`, so long paths are truncated before segment extraction.
- `PINT_split_string_list()` returns early on empty tokens without freeing already allocated token memory and can leave partially initialized arrays.
- `PINT_remove_dir_prefix()` returns error without releasing any object returned by `PVFS_path_from_expanded()` if that API allocates; ownership depends on pvfs-path internals.
- `PINT_split_keyvals()` uses `if (*ptr != ',' || *ptr != '\0')`, which is always true for any single character. The counting loop still advances by commas, but the condition is logically suspect and should be regression-tested.
- Several functions assume non-null output pointer parameters after top-level checks; misuse can crash.

## Test signals

Tests should cover root paths, repeated and trailing slashes, relative path rejection, output-buffer-too-small paths, segment iteration restoration, long path truncation behavior, handle ranges with whitespace, singletons, invalid delimiters, empty comma elements, merged range allocation, prefix boundary cases such as `/mnt/pvfs2fake`, key/value lists with missing colon or extra colon, and fallback builds without libc `strnlen` or `strstr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/str-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/str-utils.h -->
# sources/distributed-fs/orangefs/src/common/misc/str-utils.h

## Purpose

`str-utils.h` declares the shared OrangeFS string, path, handle-range, and tokenization helpers implemented in `str-utils.c`. It is the lightweight public contract consumed by config parsing, path manipulation, and option parsing code.

## Important APIs

The header declares path helpers (`PINT_merged_path_len`, `PINT_merge_paths`, `PINT_is_dot_dir`, slash cleanup, segment count and extraction, base-dir and prefix removal), handle-range helpers (`PINT_parse_handle_ranges`, `PINT_merge_handle_range_strs`), comma-list helpers (`PINT_split_string_list`, `PINT_free_string_list`), fallback libc declarations guarded by `HAVE_STRNLEN` and `HAVE_STRSTR`, and `PINT_split_keyvals` for comma-separated `key:value` strings.

## Control flow and ownership contract

Functions fall into three ownership categories. In-place mutators operate on caller-owned mutable strings. Buffer writers require caller-supplied output buffers and max lengths. Allocators such as `PINT_get_next_path`, `PINT_split_string_list`, `PINT_merge_handle_range_strs`, and `PINT_split_keyvals` return heap memory that callers must free with `free()` or `PINT_free_string_list()` as appropriate.

`PINT_string_next_segment()` has an iterator-style contract: callers initialize `*inout_segp` to NULL and provide persistent `opaquep` storage across calls. It may temporarily alter the input path while iteration proceeds.

## State and persistence behavior

The header exposes no global state and no persistence. State is either caller-provided iterator state, caller-owned buffers, or returned heap allocations.

## Dependencies and integration points

The header depends on `pvfs2-internal.h` and `pvfs2-types.h` for PVFS limits, error codes, and handle extent types. It is included by server config code and other common path handling code.

## Risks and edge cases

- The `inline` declarations for `PINT_merged_path_len` and `PINT_is_dot_dir` rely on compiler/linker behavior matching the definitions in the C file.
- Several APIs require mutable path strings despite accepting names that may look read-only. Passing string literals to in-place or iterator functions is unsafe.
- Allocating APIs use different freeing conventions, so call sites need clear ownership review.

## Test signals

Header-level coverage should compile consumers in configurations with and without `HAVE_STRNLEN` and `HAVE_STRSTR`. API tests should verify ownership expectations, mutable input requirements, and compatibility with PVFS path and handle types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/misc/str-utils.h -->
