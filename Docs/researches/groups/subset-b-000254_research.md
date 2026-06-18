# Research Group subset-b-000254

This grouped report covers OSTree libotutil variant/JSON/base32 helpers and the `ostree` CLI/admin command entry points in this subset. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-builder.c -->
# sources/cloud-native/ostree/src/libotutil/ot-variant-builder.c

## Purpose
Implements `OtVariantBuilder`, a streaming serializer for container `GVariant` values into an existing file descriptor. It exists for cases where OSTree needs to construct serialized variants without first materializing the whole value in memory, while staying byte-compatible with GLib's GVariant layout.

## Important APIs and Types
The public functions are `ot_variant_builder_new`, `ot_variant_builder_ref`, `ot_variant_builder_unref`, `ot_variant_builder_open`, `ot_variant_builder_close`, `ot_variant_builder_end`, `ot_variant_builder_add_from_fd`, `ot_variant_builder_add_value`, and `ot_variant_builder_add`. Internal types include copied GLib-style `GVariantTypeInfo`, `ArrayInfo`, `TupleInfo`, `GVariantMemberInfo`, `OtVariantBuilderInfo`, and `OtVariantBuilder`. The helper code computes fixed sizes, alignments, tuple member offset formulas, and serialized offset-table widths.

## Control Flow
Construction creates a top-level `OtVariantBuilderInfo` for a container type and links it as `builder->head`. Adding a value validates child count and type constraints, writes alignment padding to the target fd, copies child bytes from a `GVariant` or source fd, then updates offsets and offset-table bookkeeping. Opening a nested container pushes a new info frame; closing finalizes the child, posts it into the parent, and pops the stack. `ot_variant_builder_end` writes offset tables for tuples, dict entries, and variable-size arrays.

## State and Persistence
Persistent output is the serialized GVariant byte stream written to `builder->fd`. In-memory state tracks nested containers, child end offsets, expected type progression, previous item type for homogeneous containers, and min/max child counts. Global cached `GVariantTypeInfo` data is shared through a recursive mutex and hash table with manual refcounts.

## Dependencies and Integration Points
Depends on GLib/GIO `GVariant`, `GVariantType`, `GArray`, atomics, slices, and libglnx helpers such as `glnx_loop_write`, `glnx_regfile_copy_bytes`, and `glnx_throw_errno`. It integrates with OSTree metadata and summary-writing code that needs deterministic serialized variants.

## Risks
The highest risk is layout compatibility with GLib: padding, offset-table order, offset width calculation, variant type suffixes, and tuple fixed-size rules must match exactly. Assertions guard many type-state errors, so invalid caller sequencing can abort rather than return a `GError`. Large offsets depend on correct `gsize`/`guint64` handling. The type-info cache is global and must remain refcount-safe under concurrent builders.

## Test Signals
Useful signals are byte-for-byte comparisons against `g_variant_get_data()` for nested arrays, tuples, dict entries, maybes, variants, empty containers, and large offset tables; fd-copy tests for `ot_variant_builder_add_from_fd`; malformed sequence tests for open/close/end; and sanitizer or valgrind runs for type-info cache lifetimes.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-builder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-builder.h -->
# sources/cloud-native/ostree/src/libotutil/ot-variant-builder.h

## Purpose
Declares the public `OtVariantBuilder` streaming GVariant builder interface used by libotutil clients.

## Important APIs and Types
The header forward-declares `struct _OtVariantBuilder` and exposes constructors, ref/unref, `end`, nested `open`/`close`, value addition from an fd or `GVariant`, varargs addition, and a parsed-add declaration. It also registers `G_DEFINE_AUTOPTR_CLEANUP_FUNC` for automatic cleanup.

## Control Flow
The header defines no executable logic, but its API implies the required sequence: create a builder for a container type, add values or open/close nested containers, end the active container, and unref the builder.

## State and Persistence
State is opaque to callers. Persistence occurs through the fd supplied to `ot_variant_builder_new`; callers own opening and eventual closing of that fd.

## Dependencies and Integration Points
Includes `gio/gio.h` and `libglnx.h`; consumed through `otutil.h` and direct includes by code writing serialized GVariant metadata.

## Risks
The declaration of `ot_variant_builder_add_parsed` has no implementation in the paired source in this subset, so build coverage must verify whether it is implemented elsewhere or stale. Callers must pass container types and manage fd lifetime correctly.

## Test Signals
Compile/link tests are important for the full declared API. API-level tests should use autoptr cleanup and nested builder sequencing from external translation units.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-utils.c -->
# sources/cloud-native/ostree/src/libotutil/ot-variant-utils.c

## Purpose
Provides small GLib `GVariant` convenience helpers for byte arrays, empty string-to-variant dictionaries, fd-backed variant reads, mutable-builder creation from immutable variants, sorted-array lookup, and safe data access.

## Important APIs and Types
Exports `ot_gvariant_new_empty_string_dict`, `ot_gvariant_new_bytearray`, `ot_gvariant_new_ay_bytes`, `ot_variant_read_fd`, `ot_util_variant_builder_from_variant`, `ot_variant_bsearch_str`, and `ot_variant_get_data`.

## Control Flow
The constructors wrap GLib builders or `g_variant_new_from_data`. `ot_variant_read_fd` reads or mmaps an fd from a given offset via `ot_fd_readall_or_mmap`, then creates a `GVariant` from the resulting bytes. The builder-copy helper iterates children and adds each to a new `GVariantBuilder`. The binary search performs index comparisons against the first string child of each array element.

## State and Persistence
No durable state is stored here. The functions create refcounted GLib objects, sometimes sharing immutable backing storage with `GBytes`. `ot_variant_read_fd` maps persisted serialized data into process memory.

## Dependencies and Integration Points
Uses GLib/GIO, `otutil.h`, and lower-level fd utilities. Callers include OSTree metadata, summary, commit, and config code that frequently stores dictionaries and byte arrays in `GVariant` form.

## Risks
`ot_variant_bsearch_str` assumes the array is sorted and each child starts with a string; violating that contract can produce wrong lookup results or GLib warnings. `ot_gvariant_new_ay_bytes` trusts immutable `GBytes` lifetime. `ot_variant_get_data` turns GLib's nullable data result into a hard error and should be used where corrupted serialized variants are possible.

## Test Signals
Round-trip byte-array tests, fd/mmap read tests for trusted and untrusted variants, binary-search hit/miss/bounds tests, and corrupted-variant tests for `ot_variant_get_data` are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-utils.h -->
# sources/cloud-native/ostree/src/libotutil/ot-variant-utils.h

## Purpose
Declares libotutil helpers for creating, reading, copying, searching, and safely accessing `GVariant` data.

## Important APIs and Types
The header exposes byte-array constructors, empty `a{sv}` creation, `ot_variant_read_fd`, `ot_util_variant_builder_from_variant`, `ot_variant_bsearch_str`, and `ot_variant_get_data`.

## Control Flow
No control flow is implemented. The declarations define a utility API that returns newly allocated/refcounted GLib objects or boolean success with `GError`.

## State and Persistence
The API works with serialized variant data from file descriptors and refcounted memory buffers, but the header stores no state.

## Dependencies and Integration Points
Includes `gio/gio.h` and is pulled into the broad `otutil.h` umbrella. It is part of the internal utility surface shared by command and library code.

## Risks
Callers must respect transfer ownership and the sorted-array precondition for `ot_variant_bsearch_str`. Mismatched trusted flags in `ot_variant_read_fd` can shift validation responsibility to callers.

## Test Signals
Compile-time API consumers, ownership/leak tests, and negative tests for corrupt serialized data exercise the contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ot-variant-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/otutil.h -->
# sources/cloud-native/ostree/src/libotutil/otutil.h

## Purpose
Acts as the umbrella include for OSTree utility helpers and common inline macros used across command and library code.

## Important APIs and Types
Defines `OT_VARIANT_BUILDER_INITIALIZER` compatibility for older GLib, `ot_booltostr`, `ot_gobject_refz`, `ot_transfer_out_value`, journald wrapper macros, and `GMainContextPopDefault` autoptr cleanup helpers. It includes checksum, fd, filesystem, keyfile, option, tool, Unix, variant-builder, and variant-utils headers, plus GPG helpers when enabled.

## Control Flow
Inline logic is limited to simple conversions, nullable ref, output-value transfer, journald no-op wrappers, and thread-default main-context push/pop helpers.

## State and Persistence
No durable state is stored. `_ostree_main_context_new_default` creates a new `GMainContext` and makes it thread-default until autoptr cleanup pops and unrefs it.

## Dependencies and Integration Points
Depends on GLib/GIO, libglnx, syslog, optional systemd journal APIs, and many local libotutil headers. Most CLI and helper sources include this file to get a consistent internal utility environment.

## Risks
Because it is an umbrella header, changes can have broad rebuild and namespace effects. The GLib-version initializer must remain aligned with GLib's struct shape. Journald macros intentionally compile to no-ops without systemd, so callers must not rely on side effects in arguments.

## Test Signals
Full-tree compilation across GLib/systemd/GPG feature combinations and small tests for thread-default main-context cleanup are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/otutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.c -->
# sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.c

## Purpose
Implements a compact JSON writer adapted from util-linux for OSTree status output and other simple structured CLI output.

## Important APIs and Types
The core functions are `ul_jsonwrt_init`, `ul_jsonwrt_is_ready`, `ul_jsonwrt_indent`, `ul_jsonwrt_open`, `ul_jsonwrt_empty`, `ul_jsonwrt_close`, `ul_jsonwrt_flush`, and typed value writers for raw strings, JSON strings, sized strings, `uint64`, doubles, and booleans. `fputs_quoted_case_json` handles string escaping and optional case conversion.

## Control Flow
Open/empty/value calls print commas and indentation based on `after_close`, then emit object, array, or value syntax. Close calls decrement indentation and writes closing delimiters. String writers wrap values in quotes and escape control characters, double quotes, and backslashes.

## State and Persistence
State is just `FILE *out`, current indentation level, and `after_close`. Persistence is bytes written to the target stream; there is no buffering beyond stdio.

## Dependencies and Integration Points
Uses stdio, integer format macros, GLib ASCII case helpers, and assertions. `ot-admin-builtin-status.c` uses it for `ostree admin status --json`.

## Risks
The writer is stateful and does not maintain a stack of object/array types, so callers must close in the same order they open. `ul_jsonwrt_value_raw` can emit invalid JSON if passed unsafe data. Non-ASCII case conversion falls back to locale-sensitive `toupper`/`tolower`.

## Test Signals
Tests should parse emitted JSON for nested objects/arrays, strings with control characters and backslashes, null handling, status JSON output, and bad call ordering assertions in debug builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.h -->
# sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.h

## Purpose
Declares the lightweight util-linux JSON writer API and convenience macros.

## Important APIs and Types
Defines `UL_JSON_OBJECT`, `UL_JSON_ARRAY`, `UL_JSON_VALUE`, `struct ul_jsonwrt`, open/close/empty/flush functions, root/array/object/value macros, and typed value writers.

## Control Flow
The header has no runtime logic beyond macro aliases that specialize `ul_jsonwrt_open`, `ul_jsonwrt_close`, and `ul_jsonwrt_empty` by JSON element type.

## State and Persistence
The writer state consists of a target `FILE`, indentation integer, and `after_close` bit. Output persists to the stream chosen by the caller.

## Dependencies and Integration Points
Includes stdio and stdint. Used by command code that needs JSON without pulling in a heavier JSON library.

## Risks
The API is procedural and trusts callers to maintain valid nesting. Raw-value output is intentionally unsafe for untrusted strings.

## Test Signals
Compile tests plus CLI JSON parse tests from consumers such as admin status cover this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/zbase32.c -->
# sources/cloud-native/ostree/src/libotutil/zbase32.c

## Purpose
Implements z-base-32 encoding for binary buffers using Zooko Wilcox-O'Hearn's alphabet.

## Important APIs and Types
The exported function is `zbase32_encode`. Internal `zstr` and `czstr` pair a length with mutable or const byte buffers. Helpers include `new_z`, `divceil`, `b2a_l_extra_Duffy`, `b2a_l`, and `b2a`.

## Control Flow
`zbase32_encode` wraps input data in `czstr`, calls `b2a`, and returns the allocated output buffer. The encoder allocates the maximum needed quintet string, walks input from the end using Duff's device over 5-byte groups, maps 5-bit values through the z-base-32 alphabet, then truncates unused trailing quintets for non-byte-aligned bit lengths.

## State and Persistence
No global mutable state exists. The returned string is heap allocated with `malloc` and must be freed by the caller with a compatible allocator.

## Dependencies and Integration Points
Uses libc allocation/string headers and `zbase32.h`. OSTree may use this for compact human-friendly encodings where z-base-32 compatibility matters.

## Risks
The implementation is old and pointer-arithmetic heavy; boundary conditions around zero-length input, allocation failure, and partial groups need coverage. It returns `malloc` memory rather than GLib `g_malloc`, so ownership conventions must be clear.

## Test Signals
Known-vector tests for z-base-32, empty and one-to-five byte inputs, large inputs, allocation-failure handling where injectable, and leak checks for caller ownership are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/zbase32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/zbase32.h -->
# sources/cloud-native/ostree/src/libotutil/zbase32.h

## Purpose
Declares the z-base-32 encoder and preserves version metadata from the imported implementation.

## Important APIs and Types
The only callable API is `char *zbase32_encode(const unsigned char *data, size_t length)`. Static version constants describe upstream base32 version 0.9.12.

## Control Flow
No executable control flow exists in the header.

## State and Persistence
No state is stored. The API promises an allocated encoded string for the provided buffer.

## Dependencies and Integration Points
Includes `assert.h` and `stddef.h`. Consumers integrate with the C implementation and must free returned memory according to its allocation strategy.

## Risks
The header-level static version variables appear in every including translation unit; they are harmless but can trigger unused warnings depending on flags. The allocator convention is not GLib-specific.

## Test Signals
Compile/link checks and ownership tests around `zbase32_encode` cover the public contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/zbase32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/main.c -->
# sources/cloud-native/ostree/src/ostree/main.c

## Purpose
Defines the main entry point for the `ostree` command-line tool and registers the top-level built-in command table.

## Important APIs and Types
The static `commands[]` array maps command names to `OstreeCommand` entries, flags, function pointers, and descriptions. `main` calls `ostree_command_lookup_external`, `ostree_command_exec_external`, or `ostree_main`.

## Control Flow
Startup asserts an argv is present, checks whether the requested command should dispatch to an external executable, and otherwise invokes the internal command dispatcher with the built-in table.

## State and Persistence
No persistent state is modified directly. The selected built-in may open repositories, mutate sysroots, or access remotes.

## Dependencies and Integration Points
Includes `ot-builtins.h` and integrates all top-level OSTree CLI commands including `admin`, `checkout`, `pull`, `remote`, `summary`, and more. Conditional compilation hides GPG and network pull commands when features are disabled.

## Risks
Command table flags determine whether repository context is required and must match each command's parser. External command lookup changes `argv[0]` before exec, so compatibility depends on `ot-main` behavior.

## Test Signals
CLI smoke tests for command discovery, help output, external command dispatch, feature-conditional commands, and no-repo commands are appropriate.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ostree-trivial-httpd.c -->
# sources/cloud-native/ostree/src/ostree/ostree-trivial-httpd.c

## Purpose
Implements `ostree-trivial-httpd`, a small libsoup-based static file server used primarily for OSTree tests and local repository serving.

## Important APIs and Types
Options support daemonization, auto-exit, port/port-file, log-file, forced range behavior, random 500/408 fault injection with caps, expected cookies, expected headers, and fixed test basic auth. `OtTrivialHttpd` stores root dir fd, running flag, and log stream. Key functions include `httpd_log`, `get_directory_listing`, `is_safe_to_access`, `calculate_etag`, `_server_cookies_from_request`, `do_get`, `httpd_callback`, `basic_auth_callback`, `on_dir_changed`, `run`, and `main`.

## Control Flow
`main` sets locale/prgname and calls `run`. `run` parses options, opens the root directory, optionally forks with parent/child readiness pipe, configures logging and libsoup server, writes the selected port, installs auth and request handlers, optionally monitors the root for deletion, then iterates the main context until stopped. Requests route through `httpd_callback` to `do_get` for GET/HEAD. `do_get` validates expected cookies/headers, rejects traversal, injects configured random failures, stats relative to the root fd, serves directory listings or index files, mmaps regular files, emits cache headers/ETags, handles range checks, and supports forced short responses for range retry tests.

## State and Persistence
Persistent effects include optional log-file creation, optional port-file writing, and serving file bytes from the opened root. Daemon mode changes process/session state and redirects stdio. Auto-exit monitors filesystem deletion events. Fault-injection counters are process-global.

## Dependencies and Integration Points
Depends on libsoup 2/3 compatibility shims, GIO Unix streams, libglnx fd helpers, signals, sockets, prctl, and OSTree utility formatting. It integrates with OSTree tests that exercise pull, cache validation, auth, retry, range, and HTTP error paths.

## Risks
Although permission checks require world-readable files and world-executable directories, this is still a simple server and not a hardened production daemon. Path traversal filtering only checks `"../"` before stripping leading slashes. Forced range behavior deliberately lies about content length and closes sockets. Daemon readiness relies on pipe status correctness. Cookie parsing assumes `KEY=VALUE` strings and uses assertions for malformed expected headers.

## Test Signals
Tests should cover GET/HEAD, directory redirects/listings/index.html, forbidden permissions, traversal attempts, ETag and If-None-Match/If-Modified-Since, range errors, forced ranges on objects, random 500/408 caps, expected cookie/header failures, basic auth, daemon port-file readiness, and auto-exit on root deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ostree-trivial-httpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-boot-complete.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-boot-complete.c

## Purpose
Implements the hidden `ostree admin boot-complete` command run by systemd after booting an OSTree deployment.

## Important APIs and Types
Exports `ot_admin_builtin_boot_complete`. It uses `OSTREE_PATH_BOOTED` as a sanity check and calls `ostree_cmd__private__()->ostree_boot_complete`.

## Control Flow
If the system is not booted into OSTree, it exits successfully. Otherwise it asserts systemd provided `INVOCATION_ID`, parses admin options requiring superuser sysroot access, and invokes the private library boot-complete operation.

## State and Persistence
The command delegates persistent boot-completion state changes to the private OSTree library operation, likely marking deployments as successfully booted and clearing pending state.

## Dependencies and Integration Points
Uses `ostree-cmd-private.h`, admin option parsing, sysroot loading, and systemd service invocation context.

## Risks
The `INVOCATION_ID` assertion can abort if manually invoked inside an OSTree boot. Correct behavior depends on private API semantics and systemd mount namespace setup.

## Test Signals
Service-level tests for boot-complete on booted and non-booted systems, plus private API tests for deployment state updates, are key.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-boot-complete.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-cleanup.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-cleanup.c

## Purpose
Implements `ostree admin cleanup`, which prunes untagged deployments and repository objects through the sysroot cleanup API.

## Important APIs and Types
Exports `ot_admin_builtin_cleanup`; its only option table is empty.

## Control Flow
The command parses admin context with superuser requirements, obtains an `OstreeSysroot`, then calls `ostree_sysroot_cleanup`.

## State and Persistence
Persistent mutations are delegated to sysroot cleanup: deployment directories, bootloader state, and repo object garbage collection may be affected.

## Dependencies and Integration Points
Depends on admin option parsing and `OstreeSysroot`. It is registered under `ostree admin cleanup`.

## Risks
Cleanup is destructive by design. Safety depends on sysroot APIs preserving booted, default, rollback, pending, staged, and pinned deployments correctly.

## Test Signals
Integration tests should verify cleanup retains required deployments and removes only eligible leftovers after deploy/undeploy/failure scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-cleanup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-deploy.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-deploy.c

## Purpose
Implements `ostree admin deploy`, creating a new deployment from a ref/revision with optional staging, finalization locking, origin override, kernel argument control, initrd overlays, and retention policy.

## Important APIs and Types
Exports `ot_admin_builtin_deploy`. Options include `--os/--stateroot`, `--origin-file`, `--no-prune`, `--no-merge`, `--retain*`, `--stage`, `--lock-finalization`, `--not-as-default`, kernel argument replace/append/delete/proc/none flags, and `--overlay-initrd`. It uses `OstreeKernelArgs`, `OstreeSysrootDeployTreeOpts`, `OstreeDeployment`, and sysroot deploy/stage/write APIs.

## Control Flow
After parsing and validating incompatible options, locking implies staging. The command resolves the requested ref, determines a merge deployment unless disabled, performs initial cleanup, builds optional kernel args, stages overlay initrds and records checksums, then either stages the tree or deploys immediately. Non-staged deployments are written into the deployment list with retention/default flags. It finishes with prepare cleanup for staged/no-prune cases or full sysroot cleanup otherwise.

## State and Persistence
Mutates sysroot deployments, origin files, kernel argument bootconfig, overlay initrd staging data, staged-finalization lock state, bootloader deployment order, and repository cleanup state. With `--lock-finalization`, it also writes a legacy runstate lockfile for compatibility.

## Dependencies and Integration Points
Uses `ostree-sysroot-private.h`, repo rev resolution, sysroot deploy/stage APIs, kernel arg helpers, libglnx fd helpers, and admin shared functions. It is central to admin workflows and interacts with bootloader and shutdown finalization services.

## Risks
Option interaction is complex: staged deployments reject some retention/default flags, `--no-merge` and karg deletion conflict, and karg defaults depend on merge state. Partial failures can leave staging data, so cleanup ordering is important. Overlay initrd checksums must remain aligned with staged/deployed metadata. Finalization locks require compatibility between new deployment metadata and legacy lockfile behavior.

## Test Signals
Coverage should include immediate deploy, staged deploy, locked staged deploy, origin-file input, all kernel-arg modes and conflicts, overlay initrd staging, retain/pending/rollback flags, no-prune cleanup behavior, and recovery from partial deploy failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-deploy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-diff.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-diff.c

## Purpose
Implements `ostree admin config-diff`, comparing a deployment's mutable `/etc` against the default `/usr/etc`.

## Important APIs and Types
Exports `ot_admin_builtin_diff`. It accepts `--os` to target a stateroot and uses `ostree_diff_dirs` and `ostree_diff_print`.

## Control Flow
The command parses admin context, requires either a booted deployment or explicit OS name, selects the merge or booted deployment, resolves deployment directory paths for `usr/etc` and `etc`, computes modified/removed/added lists ignoring xattrs, and prints the diff.

## State and Persistence
No persistent state is changed; it reads deployment filesystem state.

## Dependencies and Integration Points
Uses admin sysroot loading, `OstreeDeployment`, GFile path resolution, and OSTree diff APIs.

## Risks
The diff intentionally ignores xattrs, so SELinux or capability changes are not reported. With `--os`, absence of a merge deployment is a hard not-found error.

## Test Signals
Tests should create deployment etc changes and verify added, removed, modified output, booted-vs-os selection, and xattr-ignore behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-finalize-staged.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-finalize-staged.c

## Purpose
Implements the hidden `ostree admin finalize-staged` command used by `ostree-finalize-staged.service` to finish staged deployments at shutdown.

## Important APIs and Types
Exports `ot_admin_builtin_finalize_staged`. Option `--hold` keeps `/boot` open until SIGTERM. It delegates finalization to `ostree_cmd__private__()->ostree_finalize_staged`.

## Control Flow
If not booted into OSTree, it exits successfully. It first parses without loading the sysroot. With `--hold`, it loads the sysroot unlocked, relies on the sysroot keeping `/boot` open, and blocks in `pause()`. Without `--hold`, it loads normally with superuser access and invokes private staged-finalization.

## State and Persistence
Finalization mutates staged deployment and bootloader state through the private API. Hold mode keeps file descriptors and process state alive but does not itself write deployment data.

## Dependencies and Integration Points
Integrates with systemd shutdown units, sysroot loading flags, private command APIs, signal behavior, and mount namespace expectations.

## Risks
Hold mode intentionally blocks until a signal. Loading flags are subtle: unlocked loading avoids a separate namespace so `/boot` remains held correctly. Manual invocation outside the service path can be surprising.

## Test Signals
Systemd integration tests for staged deployment finalization, lock/hold behavior, non-booted no-op behavior, and bootloader updates are needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-finalize-staged.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-impl-prepare-soft-reboot.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-impl-prepare-soft-reboot.c

## Purpose
Implements a hidden internal command that delegates soft-reboot preparation to the private OSTree command API.

## Important APIs and Types
Exports `ot_admin_builtin_impl_prepare_soft_reboot` and calls `ostree_cmd__private__()->ostree_prepare_soft_reboot`.

## Control Flow
There is no option parsing in this wrapper. It invokes the private preparation function and returns its boolean result.

## State and Persistence
Any state changes, such as preparing runtime files for a soft reboot, are performed by the private library function.

## Dependencies and Integration Points
Depends on `ostree-cmd-private.h` and is registered conditionally by the admin command table when soft reboot support is enabled.

## Risks
The wrapper has minimal validation and relies entirely on private API preconditions and service-level invocation.

## Test Signals
Private soft-reboot preparation tests and hidden command invocation smoke tests cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-impl-prepare-soft-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-init-fs.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-init-fs.c

## Purpose
Implements `ostree admin init-fs`, initializing a filesystem root for OSTree use with legacy or modern top-level directory layouts.

## Important APIs and Types
Exports `ot_admin_builtin_init_fs`. Options are `--modern` and `--epoch`; it uses libglnx directory creation and `ostree_sysroot_ensure_initialized`.

## Control Flow
The command parses without an existing sysroot, opens the target path, always ensures `boot`, validates epoch, maps `--modern` to epoch 1, creates legacy top-level directories for epoch 0, creates private `ostree` for epoch 2, then constructs an `OstreeSysroot` and ensures initialization.

## State and Persistence
Creates directories such as `boot`, `ostree`, and legacy `dev/home/proc/run/sys/root/tmp`, with specific modes. It initializes the sysroot on disk.

## Dependencies and Integration Points
Uses admin parser flags for superuser/unlocked/no-sysroot operation, libglnx mkdir helpers, GFile, and sysroot initialization APIs.

## Risks
Directory mode choices are compatibility-sensitive. Epoch handling accepts epoch 1 by doing only boot plus normal sysroot initialization, while epoch 2 changes `ostree` permissions to 0700. Negative epoch is rejected, but values above 2 currently skip the explicit layout branches.

## Test Signals
Filesystem layout tests for default, `--modern`, epoch 1, epoch 2, invalid negative epoch, permissions on `tmp` and `ostree`, and idempotent reinitialization are relevant.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-init-fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-instutil.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-instutil.c

## Purpose
Implements the hidden/deprecated `ostree admin instutil` subcommand dispatcher for installer-oriented utilities.

## Important APIs and Types
Static `admin_instutil_subcommands[]` registers `selinux-ensure-labeled` when SELinux is enabled, `set-kargs`, and `grub2-generate`. `ot_admin_builtin_instutil` dispatches to selected subcommands.

## Control Flow
The dispatcher removes the first non-option argument as the subcommand, searches the subcommand table, prints generated help and errors for missing/unknown names, updates `g_prgname`, then invokes the target function with a fresh `OstreeCommandInvocation`.

## State and Persistence
This file only rewrites argv in memory and changes process program name. Persistence belongs to the selected subcommand.

## Dependencies and Integration Points
Uses `OstreeCommand`, admin option parsing, and the instutil builtins header. It is registered under `ostree admin instutil`.

## Risks
In-place argv compaction must preserve options after `--` correctly. Hidden/deprecated commands still affect bootloader, SELinux labels, or kargs through their handlers.

## Test Signals
Dispatcher tests should cover help, unknown subcommands, option passing, `--` behavior, and feature-conditional SELinux command visibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-instutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-kargs.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-kargs.c

## Purpose
Implements the `ostree admin kargs` dispatcher for kernel-argument subcommands.

## Important APIs and Types
Registers hidden `edit-in-place` through `admin_kargs_subcommands[]` and exports `ot_admin_builtin_kargs`.

## Control Flow
Mirrors the instutil dispatcher: extracts the first non-option subcommand, searches the table, generates help/errors for missing or unknown commands, sets program name, and calls the selected subcommand.

## State and Persistence
This file only mutates argv layout and process prgname. Deployment bootconfig mutations are performed by the selected kargs subcommand.

## Dependencies and Integration Points
Depends on `ot-admin-kargs-builtins.h`, admin option parsing, and the `OstreeCommand` dispatch model. Registered under `ostree admin kargs`.

## Risks
The only current subcommand is hidden, so user-facing help may be sparse. Option forwarding and `--` handling must remain consistent with other dispatchers.

## Test Signals
Dispatcher tests for missing command, unknown command, hidden command invocation, and option passthrough are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-kargs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-lock-finalization.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-lock-finalization.c

## Purpose
Implements `ostree admin lock-finalization`, toggling whether a staged deployment is automatically finalized at shutdown.

## Important APIs and Types
Exports `ot_admin_builtin_lock_finalization`. Option `--unlock` reverses the lock. It uses `ostree_sysroot_get_staged_deployment`, `ostree_deployment_is_finalization_locked`, and `ostree_sysroot_change_finalization`.

## Control Flow
After superuser sysroot parsing, it requires a staged deployment, checks current lock state, prints idempotent messages when no change is needed, otherwise toggles finalization and prints the resulting state.

## State and Persistence
Mutates staged deployment metadata/state through `ostree_sysroot_change_finalization`.

## Dependencies and Integration Points
Uses private sysroot headers and admin parser. It complements `deploy --lock-finalization` and shutdown finalization services.

## Risks
The command assumes exactly the current staged deployment is the target. Correctness depends on `change_finalization` toggling the intended persistent metadata and any legacy runstate compatibility.

## Test Signals
Tests should cover no staged deployment, lock, unlock, idempotent lock/unlock, and later finalize-staged behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-lock-finalization.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-os-init.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-os-init.c

## Purpose
Implements `ostree admin os-init` and the `stateroot-init` alias, initializing an empty deployment stateroot.

## Important APIs and Types
Exports `ot_admin_builtin_os_init`; uses `ostree_sysroot_ensure_initialized` and `ostree_sysroot_init_osname`.

## Control Flow
The command parses superuser admin context, ensures the sysroot exists, requires a `STATEROOT` argument, initializes that OS/stateroot name, and prints confirmation.

## State and Persistence
Creates or updates `ostree/deploy/<osname>` stateroot metadata on disk.

## Dependencies and Integration Points
Depends on admin option parsing and sysroot initialization. It is part of provisioning workflows before deployments are added.

## Risks
Input validation of stateroot names is delegated to sysroot APIs. Re-running against existing state must be handled idempotently by the library.

## Test Signals
Provisioning tests for new stateroot creation, missing argument, invalid names, and repeated initialization are useful.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-os-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-pin.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-pin.c

## Purpose
Implements `ostree admin pin`, setting or clearing the pinned state of deployments so cleanup does or does not prune them.

## Important APIs and Types
Exports `ot_admin_builtin_pin`. Option `--unpin` clears pins. Helpers `get_deployment_index_for_type` and `do_pinning` resolve symbolic indices and apply `ostree_sysroot_deployment_set_pinned`.

## Control Flow
After parsing superuser context, each argument is parsed as `booted`, `pending`, `rollback`, or a numeric deployment index. The command resolves the deployment, compares current and desired pin state, prints idempotent status or applies the change.

## State and Persistence
Mutates deployment pin metadata in the sysroot.

## Dependencies and Integration Points
Uses deployment list queries, booted/pending/rollback identification, `ot_admin_get_indexed_deployment`, and sysroot pin APIs. Cleanup behavior consumes the pin state.

## Risks
Symbolic resolution depends on a booted deployment to identify pending/rollback. Numeric parsing checks invalid characters and range errors, but selected deployments can change if deployment order changes between commands.

## Test Signals
Tests should cover numeric and symbolic indices, missing type, invalid index, already pinned/unpinned idempotence, multiple indices, and cleanup retaining pinned deployments.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-pin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-post-copy.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-post-copy.c

## Purpose
Implements `ostree admin post-copy`, updating repo and deployment metadata after a sysroot copy.

## Important APIs and Types
Exports `ot_admin_builtin_post_copy` and calls `ostree_sysroot_update_post_copy`.

## Control Flow
The command parses superuser admin context, obtains the sysroot, and delegates all work to the sysroot post-copy update API.

## State and Persistence
Persistent changes are delegated and likely include copied repository/deployment fixups needed after image or filesystem duplication.

## Dependencies and Integration Points
Uses private sysroot headers, admin parsing, and sysroot update APIs. It is intended for image-copy or install workflows.

## Risks
The wrapper exposes a broad operation with no extra validation. Safety depends on the library correctly detecting and updating copied state.

## Test Signals
Image-copy integration tests should verify post-copy updates required metadata and remains idempotent.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-post-copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-prepare-soft-reboot.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-prepare-soft-reboot.c

## Purpose
Implements `ostree admin prepare-soft-reboot`, selecting a non-booted deployment as the soft-reboot target or clearing queued soft-reboot state.

## Important APIs and Types
Exports `ot_admin_builtin_prepare_soft_reboot`. Options are `--reboot` to execute `systemctl soft-reboot` after success and `--reset` to clear state.

## Control Flow
After superuser parsing, `--reset` immediately calls `ostree_sysroot_clear_soft_reboot`. Otherwise the command requires an index, parses it, resolves the deployment, rejects the currently booted deployment, marks the target with `ostree_sysroot_deployment_set_soft_reboot`, and optionally `execlp`s `systemctl soft-reboot`.

## State and Persistence
Mutates soft-reboot target state in deployment/sysroot metadata. With `--reboot`, the process image is replaced by systemctl.

## Dependencies and Integration Points
Uses shared indexed deployment helper, sysroot soft-reboot APIs, and systemd soft-reboot support.

## Risks
Index parsing does not check `ERANGE` explicitly. Preparing the booted deployment is rejected. The final `execlp` has no return on success, so callers must account for process replacement.

## Test Signals
Tests should cover reset, missing index, invalid index, booted deployment rejection, target marking, and systemctl exec failure paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-prepare-soft-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-default.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-default.c

## Purpose
Implements `ostree admin set-default`, reordering deployments so a selected deployment becomes default.

## Important APIs and Types
Exports `ot_admin_builtin_set_default`; uses `ot_admin_get_indexed_deployment`, `ostree_sysroot_write_deployments`, and `ostree_sysroot_cleanup`.

## Control Flow
The command parses superuser context, requires an index, fetches current deployments, resolves the target deployment, removes it from its current position, inserts it at index 0, writes deployments, and runs cleanup.

## State and Persistence
Persists deployment order and bootloader state through sysroot write and cleanup operations.

## Dependencies and Integration Points
Uses shared admin helper and sysroot deployment APIs. Deployment order affects boot default and status output.

## Risks
The index is parsed with `atoi`, so invalid strings become 0 rather than explicit errors. Removing/inserting assumes the deployment list has not changed after resolving the target.

## Test Signals
Tests should cover valid reordering, invalid and out-of-range input, preserving booted/rollback entries, and cleanup side effects.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-default.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-origin.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-origin.c

## Purpose
Implements `ostree admin set-origin`, configuring a remote and writing a new origin refspec for a deployment.

## Important APIs and Types
Exports `ot_admin_builtin_set_origin`. Options include `--set KEY=VALUE` for remote options and `--index` to target a non-booted deployment. It uses `ostree_repo_remote_change`, `ostree_parse_refspec`, `ostree_sysroot_origin_new_from_refspec`, and `ostree_sysroot_write_origin_file`.

## Control Flow
The command parses superuser context, requires remote and URL, opens the sysroot repo, selects the booted deployment or indexed deployment, converts `--set` pairs into an `a{sv}` remote-options variant, adds the remote if needed, derives the branch from an explicit argument or old origin, builds a new refspec, and writes the deployment origin file.

## State and Persistence
Mutates repository remote configuration and deployment origin metadata. It does not deploy new content by itself.

## Dependencies and Integration Points
Integrates repo remote management, deployment origin files, and later upgrade/switch behavior that reads origins.

## Risks
If the old origin lacks a refspec and no branch is provided, the command fails. Remote options are accepted as strings only. Changing the origin of a non-booted deployment depends on index stability.

## Test Signals
Tests should cover adding a new remote, updating booted and indexed deployments, branch inheritance, explicit branch override, remote option parsing, missing refspec failure, and later upgrade using the new origin.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-set-origin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-state-overlay.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-state-overlay.c

## Purpose
Implements hidden `ostree admin state-overlay`, called by `ostree-state-overlay@.service` to mount persistent overlayfs state over a deployment path and prune stale upperdir data when the lower deployment changes.

## Important APIs and Types
Defines overlay directory names under `/var/ostree/state-overlays`, xattr `user.ostree.deploymentcsum`, and overlayfs opaque xattr `trusted.overlay.opaque`. Helpers include `ensure_overlay_dirs`, `lgetxattrat_allow_nodata`, `is_opaque_dir`, `prune_upperdir_recurse`, `prune_upperdir`, `mount_overlay`, `get_overlay_deployment_checksum`, and `set_overlay_deployment_checksum`.

## Control Flow
The command parses unlocked superuser context, requires `NAME MOUNTPATH`, verifies a booted deployment, creates/open overlay `upper` and `work` dirs, reads the stored deployment checksum, and if it differs from the booted deployment checksum, prunes upper entries that now shadow lower entries and stores the new checksum. It then mounts overlayfs with the mount path as lowerdir and the named upper/work dirs.

## State and Persistence
Creates and mutates `/var/ostree/state-overlays/<name>`, including upper/work directories and a deployment checksum xattr on the upper dir. It removes obsolete upperdir files/directories during pruning and creates a live overlayfs mount.

## Dependencies and Integration Points
Uses Linux overlayfs, xattrs, mount syscall, libglnx fd/xattr/shutil helpers, sysroot booted deployment state, and systemd state-overlay units.

## Risks
Pruning is destructive and must correctly distinguish real state files from entries shadowing lowerdir content. Opaque directories and whiteouts require correct xattr/d_type handling. The xattr helper intentionally handles ENODATA races, but relies on `/proc/self/fd`. Mount options are stringified paths and require correct permissions and kernel overlayfs behavior.

## Test Signals
Integration tests need overlay creation, checksum change pruning, opaque directory behavior, whiteout pruning, ENODATA/ERANGE xattr races, mount failure errors, and preservation of upper-only state files.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-state-overlay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-status.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-status.c

## Purpose
Implements `ostree admin status`, listing deployments in text, JSON, verification, or default-state forms.

## Important APIs and Types
Exports `ot_admin_builtin_status`. Options are `--verify`, `--json`, `--skip-signatures`, and `--is-default`. Helpers `deployment_print_status` and `deployment_write_json` read deployment metadata, origin refspec, commit metadata, signature state, unlocked/pinned/staged/finalization/soft-reboot flags, and pending/rollback classification.

## Control Flow
The command loads the sysroot and repo, obtains deployments and booted/pending/rollback references, then either emits a JSON object with a `deployments` array, prints `default`/`not-default`, prints `No deployments.`, or iterates deployments in text form. Text mode loads commit metadata best-effort, prints version/origin/unlocked/pinned/status markers, optionally prints GPG signatures, and optionally verifies signatures. JSON mode requires commit load for each deployment and writes fields through `ul_jsonwrt`.

## State and Persistence
No persistent state is modified. It reads deployment files, origin keyfiles, commit objects, detached metadata, and remote GPG configuration.

## Dependencies and Integration Points
Depends on libglnx, OSTree repo/sysroot/deployment APIs, optional GPGME/signature verification, and `ul-jsonwrt` for JSON output. Status output is often consumed by automation.

## Risks
Text mode tolerates commit load failure for display, but JSON mode treats commit load as fatal. Signature output depends on origin remote and remote GPG config. JSON field names are a compatibility surface for scripts. `--is-default` reports error when not in a booted OSTree system.

## Test Signals
Tests should cover empty deployments, booted/pending/rollback/staged/locked/soft-reboot/pinned/unlocked flags, JSON parse and schema fields, signature display and skip/verify modes, originless deployments, and default detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-switch.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-switch.c

## Purpose
Implements `ostree admin switch`, changing the tracked origin refspec to a new remote/ref, pulling it, deploying it, and deleting the old ref.

## Important APIs and Types
Exports `ot_admin_builtin_switch`. Options are `--reboot`, `--kexec`, and `--os`. Uses `OstreeSysrootUpgrader`, origin keyfiles, refspec parsing, pull/deploy APIs, repo transactions, and `ot_admin_execve_reboot`.

## Control Flow
The command parses superuser context, creates an upgrader with `IGNORE_UNCONFIGURED` and optional kexec, reads the old origin refspec, parses the requested new refspec or remote-only syntax ending in `:`, builds the final refspec, rejects no-op switches, writes the upgrader origin, pulls allowing older commits, deploys, starts a repo transaction to delete the old remote ref, commits it, and optionally reboots.

## State and Persistence
Mutates deployment origin, downloads content, creates a new deployment, deletes the old repo ref, and may replace the process with `systemctl reboot`.

## Dependencies and Integration Points
Integrates remote/ref tracking with the sysroot upgrader and repo transaction APIs. It shares progress display behavior with upgrade.

## Risks
Deleting the old ref after deploy can surprise users if the old ref is still desired. Remote-only syntax must preserve the old branch correctly. Pull allows older commits intentionally, so downgrade-like switches are possible.

## Test Signals
Tests should cover remote-only switches, full refspec switches, equal-ref rejection, pull/deploy success, old ref deletion transaction, kexec flag propagation, and reboot exec failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-undeploy.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-undeploy.c

## Purpose
Implements `ostree admin undeploy`, deleting a non-booted deployment by index.

## Important APIs and Types
Exports `ot_admin_builtin_undeploy`; uses `ot_admin_get_indexed_deployment`, `ostree_sysroot_write_deployments`, and `ostree_sysroot_cleanup`.

## Control Flow
After superuser parsing, it requires an index, parses it with `g_ascii_strtoull`, resolves the target, rejects the currently booted deployment, removes it from the deployment array, writes the new array, prints the deleted checksum/serial, and performs cleanup.

## State and Persistence
Persists deployment list changes and removes eligible deployment/repo data during cleanup.

## Dependencies and Integration Points
Uses shared admin helpers and sysroot deployment APIs. It interacts with cleanup, pinning, and bootloader state.

## Risks
Index parsing checks invalid trailing characters but not `ERANGE`. Removing deployments can affect rollback/default ordering. Booted deployment protection is essential.

## Test Signals
Tests should cover missing/invalid/out-of-range index, booted rejection, deletion of pending/rollback entries, cleanup side effects, and status output after undeploy.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-undeploy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-unlock.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-unlock.c

## Purpose
Implements `ostree admin unlock`, making the booted deployment mutable through development, hotfix, or transient overlay modes.

## Important APIs and Types
Exports `ot_admin_builtin_unlock`. Options `--hotfix` and `--transient` select `OstreeDeploymentUnlockedState`; default is development.

## Control Flow
The command parses superuser context, rejects extra args, requires a booted deployment, rejects simultaneous hotfix and transient, calls `ostree_sysroot_deployment_unlock`, and prints mode-specific instructions.

## State and Persistence
Mutates booted deployment unlocked state and mounts/prepares overlayfs behavior through sysroot APIs. Hotfix mode creates a non-hotfixed rollback target.

## Dependencies and Integration Points
Integrates with deployment metadata, overlayfs/unlocked deployment handling, and status display of unlocked state.

## Risks
Unlocking intentionally weakens immutability. Hotfix state persists differently from development/transient modes. Correct rollback creation is delegated to sysroot APIs.

## Test Signals
Tests should cover all modes, conflict validation, no booted deployment, status output after unlock, reboot persistence/discard behavior, and rollback creation in hotfix mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-unlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-upgrade.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-upgrade.c

## Purpose
Implements `ostree admin upgrade`, pulling from the current origin and deploying a new tree when available.

## Important APIs and Types
Exports `ot_admin_builtin_upgrade`. Options include `--reboot`, `--kexec`, `--allow-downgrade`, `--override-commit`, `--pull-only`, `--deploy-only`, `--stage`, and `--os`. It uses `OstreeSysrootUpgrader`, pull flags, progress reporting, origin mutation, and optional reboot exec.

## Control Flow
The command validates incompatible options, constructs upgrader flags for staging/kexec, creates an upgrader for the selected OS, duplicates and sanitizes origin transient state, applies override commit if provided, configures pull flags including synthetic deploy-only and allow older, runs pull with console progress, cleans up on failed pull-only, deploys unless pull-only, prints no-update status if unchanged, and reboots if requested.

## State and Persistence
Pulling mutates repository objects and refs. Deploying mutates sysroot deployment state. Override commit is applied to the upgrader origin for this operation. Optional cleanup runs after failed pull-only. Optional reboot replaces the process.

## Dependencies and Integration Points
Uses sysroot upgrader APIs, repo pull progress callbacks, console locking, origin keyfiles, and shared reboot helper.

## Risks
Pull-only and deploy-only modes alter normal sequencing and must not be combined. Allow-downgrade intentionally accepts older commits. Override commit affects pull/deploy selection and must not persist unintended transient state. Progress handling is TTY-dependent.

## Test Signals
Tests should cover no update, successful pull/deploy, staged upgrade, kexec flag, pull-only cleanup on failure, deploy-only synthetic mode, allow-downgrade, override commit, option conflicts, and reboot exec path.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-upgrade.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtins.h -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtins.h

## Purpose
Declares the function prototypes for `ostree admin` built-in command handlers.

## Important APIs and Types
Defines `BUILTINPROTO` to declare handlers with the standard `(argc, argv, invocation, cancellable, error)` signature. It declares cleanup, config diff, deploy, finalize, boot-complete, soft-reboot commands, unlock, status, origin, upgrade, kargs, state-overlay, and more. `switch` is declared manually because it is a C keyword.

## Control Flow
No runtime control flow exists. The declarations let command tables reference handlers consistently.

## State and Persistence
No state is stored. Each declared handler may mutate sysroot state.

## Dependencies and Integration Points
Includes `ot-main.h` for `OstreeCommandInvocation` and command types. Consumed by `ot-builtin-admin.c` and individual admin source files.

## Risks
Prototype drift breaks command registration at compile time. Conditional implementations must remain aligned with command table feature guards.

## Test Signals
Full compilation with all feature combinations and command-table link checks are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtins.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-functions.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-functions.c

## Purpose
Provides shared helper functions for admin commands: booted deployment checks, commit version extraction, deployment lookup by index, sysroot lock waiting, and guarded reboot exec.

## Important APIs and Types
Exports `ot_admin_require_booted_deployment_or_osname`, `ot_admin_checksum_version`, `ot_admin_get_indexed_deployment`, `ot_admin_sysroot_lock`, and `ot_admin_execve_reboot`. Internal `ContextState` supports async lock waiting.

## Control Flow
The booted check returns an error only when neither a booted deployment nor explicit OS name exists. Version extraction reads commit metadata child 0. Indexed lookup validates bounds against current deployment array. Sysroot lock first tries nonblocking lock, then if needed attaches a 3-second repeating timeout that prints waiting messages, starts async lock acquisition, and iterates a private main context until acquired. Reboot only execs systemctl when the sysroot is actually booted.

## State and Persistence
No persistent state is directly changed except that lock acquisition changes sysroot lock ownership and reboot exec changes process state. The helper reads deployment arrays and commit metadata.

## Dependencies and Integration Points
Uses libglnx errors, GLib main contexts/sources, `OstreeSysroot` locking APIs, and systemctl exec. Many admin builtins depend on these helpers.

## Risks
The async lock callback does not inspect the async result in this file, relying on the lock API's behavior to wake after acquisition. `ot_admin_execve_reboot` intentionally no-ops on non-booted sysroots to avoid accidental build-host reboot. Index lookup operates on current order.

## Test Signals
Tests should cover no booted/no os error, indexed lookup bounds, version metadata presence/absence, lock wait messaging/acquisition, and reboot helper no-op vs exec failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-functions.h -->
# sources/cloud-native/ostree/src/ostree/ot-admin-functions.h

## Purpose
Declares shared admin helper APIs used by multiple command implementations.

## Important APIs and Types
Exposes booted-or-os validation, checksum version extraction, indexed deployment lookup, sysroot locking, and guarded reboot exec.

## Control Flow
No implementation is present; functions follow standard GLib boolean/error or returned-object conventions.

## State and Persistence
The header stores no state. Declared functions may read deployment metadata, acquire locks, or exec reboot.

## Dependencies and Integration Points
Includes `ot-main.h` for OSTree/GLib command context types. Used across admin builtins.

## Risks
Callers must respect ownership of returned strings and deployment refs. Functions that may exec or block on locks should be used only in command paths where that behavior is expected.

## Test Signals
Compile/link tests and the implementation tests for each declared helper cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-functions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-grub2-generate.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-grub2-generate.c

## Purpose
Implements `ostree admin instutil grub2-generate`, generating GRUB2 configuration for a selected bootversion.

## Important APIs and Types
Exports `ot_admin_instutil_builtin_grub2_generate`; calls `ostree_cmd__private__()->ostree_generate_grub2_config`.

## Control Flow
The command parses superuser/unlocked admin context, accepts an optional bootversion argument or reads `_OSTREE_GRUB2_BOOTVERSION` or current sysroot bootversion, validates it is 0 or 1, and delegates config generation with deployment count limit 1.

## State and Persistence
Writes GRUB2 boot configuration through the private command API.

## Dependencies and Integration Points
Depends on sysroot bootversion state, environment override, and private bootloader generation code. Used by installer/bootloader workflows.

## Risks
Invalid environment values are not explicitly rejected before the final assertion path if not 0/1. Bootversion determines which boot tree is generated, so mismatches can affect bootability.

## Test Signals
Tests should cover explicit bootversion 0/1, invalid values, environment override, default sysroot bootversion, and generated GRUB output.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-grub2-generate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-selinux-ensure-labeled.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-selinux-ensure-labeled.c

## Purpose
Implements `ostree admin instutil selinux-ensure-labeled`, recursively applying SELinux labels to all or part of the first deployment when a policy is present.

## Important APIs and Types
Helpers include `ptrarray_path_join`, `relabel_one_path`, `relabel_recursively`, and `selinux_relabel_dir`. The exported command is `ot_admin_instutil_builtin_selinux_ensure_labeled`.

## Control Flow
After superuser/unlocked parsing, the command selects the first deployment, derives the deployment path, accepts optional subpath and prefix, creates an `OstreeSePolicy`, and if a policy name exists, recursively enumerates files and calls `ostree_sepolicy_restorecon` with allow-nolabel and keep-existing flags. Paths are tracked as an array to produce SELinux relative paths.

## State and Persistence
Mutates SELinux xattrs/labels on deployment files when policy rules assign a label. It prints label changes.

## Dependencies and Integration Points
Depends on GFile enumeration, `OstreeSePolicy`, deployment directories, and SELinux feature availability. Registered only when SELinux support is compiled.

## Risks
The optional-argument handling checks `argc >= 2` but then reads `argv[2]`, so callers should provide both subpath and prefix. Recursive relabeling can be expensive and error-prone on large trees. KEEP_EXISTING changes semantics versus force relabeling.

## Test Signals
SELinux-enabled tests should cover no deployment, no policy, full deployment relabel, subpath/prefix relabel, missing prefix argument, recursive traversal, and unchanged existing labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-selinux-ensure-labeled.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-set-kargs.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-set-kargs.c

## Purpose
Implements deprecated installer utility `ostree admin instutil set-kargs`, setting kernel command-line arguments on the first deployment.

## Important APIs and Types
Options include `--import-proc-cmdline`, `--merge`, `--replace`, and `--append`. Uses `OstreeKernelArgs` and `ostree_sysroot_deployment_set_kargs`.

## Control Flow
The command parses superuser/unlocked context, requires at least one deployment, creates a fresh kargs object, optionally imports `/proc/cmdline` or merges previous deployment options, applies replacement and append arrays, appends positional args, converts to string vector, and writes kargs to the first deployment.

## State and Persistence
Mutates bootconfig kernel arguments for the first deployment in the sysroot.

## Dependencies and Integration Points
Uses sysroot deployment list, bootconfig parser, kernel arg helpers, and installer command dispatch.

## Risks
The command targets only the first deployment. `--import-proc-cmdline` overrides merge behavior by design. Deprecated status means newer karg paths may differ.

## Test Signals
Tests should cover merge vs proc import, replace and append precedence, positional args, no deployment error, and resulting bootconfig options.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-set-kargs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtins.h -->
# sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtins.h

## Purpose
Declares installer utility subcommand handlers for `ostree admin instutil`.

## Important APIs and Types
Declares SELinux relabel, set-kargs, and grub2-generate handlers with the standard `OstreeCommandInvocation` signature.

## Control Flow
No runtime logic is implemented.

## State and Persistence
No state is stored in the header; declared commands may mutate labels, bootloader config, and deployment kargs.

## Dependencies and Integration Points
Includes `ot-main.h` and is consumed by the instutil dispatcher and implementation files.

## Risks
Feature guards in the dispatcher must stay aligned with available declarations/definitions, especially SELinux.

## Test Signals
Feature-matrix compilation and dispatcher link tests cover this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtins.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtin-edit-in-place.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtin-edit-in-place.c

## Purpose
Implements hidden `ostree admin kargs edit-in-place`, updating kernel arguments across all deployments without creating new deployments.

## Important APIs and Types
Exports `ot_admin_kargs_builtin_edit_in_place`. Option `--append-if-missing` supplies kernel args to add only when absent.

## Control Flow
The command parses superuser context, requires at least one deployment, iterates every deployment, builds `OstreeKernelArgs` from current bootconfig options, applies each append-if-missing argument, converts the result to a string, and calls `ostree_sysroot_deployment_set_kargs_in_place`.

## State and Persistence
Mutates bootconfig options in place for all deployments in the sysroot.

## Dependencies and Integration Points
Uses sysroot deployment APIs, bootconfig parser, kernel arg helpers, and the kargs dispatcher.

## Risks
This command changes every deployment and is hidden, so it is likely intended for controlled automation. In-place mutation bypasses deploy-based rollback semantics.

## Test Signals
Tests should cover multiple deployments, idempotent append-if-missing, no deployment error, and status/bootloader visibility of changed kargs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtin-edit-in-place.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtins.h -->
# sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtins.h

## Purpose
Declares admin kargs subcommand handlers.

## Important APIs and Types
Defines `BUILTINPROTO` for `ot_admin_kargs_builtin_edit_in_place` using the standard command signature.

## Control Flow
No implementation logic exists.

## State and Persistence
No state is stored in the header. The declared handler mutates deployment kargs.

## Dependencies and Integration Points
Includes `ot-main.h`; consumed by the kargs dispatcher and edit-in-place implementation.

## Risks
Prototype and dispatcher table must remain aligned.

## Test Signals
Compile/link tests and kargs dispatcher tests cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtins.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-admin.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-admin.c

## Purpose
Implements the top-level `ostree admin` dispatcher and registers admin subcommands.

## Important APIs and Types
Static `admin_subcommands[]` maps names such as `cleanup`, `deploy`, `status`, `switch`, `upgrade`, `unlock`, `pin`, `kargs`, and hidden service commands to their handlers and flags. `ostree_admin_option_context_new_with_commands` creates help text, and `ostree_builtin_admin` dispatches.

## Control Flow
The dispatcher strips the first non-option command from argv, looks it up, prints generated help with missing/unknown errors when needed, sets the process program name to include the subcommand, creates a sub-invocation, and calls the handler. Some commands are conditionally included for soft reboot support.

## State and Persistence
This file mutates only process argv layout and program name. Persistent sysroot changes are performed by subcommands.

## Dependencies and Integration Points
Uses `OstreeCommand`, admin builtins, generic builtins, and admin option parsing. It is registered as top-level `admin` in `main.c`.

## Risks
Command flags determine repository/sysroot parsing behavior and must match handler expectations. Hidden commands are service-facing and should remain available to units even if omitted from help.

## Test Signals
CLI tests for help, missing/unknown subcommand errors, option passthrough, hidden command invocation, command flags, and feature-conditional entries are important.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-admin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-cat.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-cat.c

## Purpose
Implements `ostree cat`, concatenating file contents from a commit to stdout.

## Important APIs and Types
Exports `ostree_builtin_cat`; helper `cat_one_file` reads a `GFile` and splices it to a Unix stdout output stream.

## Control Flow
The command parses repository context, requires a commit and at least one path, reads the commit root as `GFile`, creates a stdout stream, resolves each requested path relative to the commit root, and splices each file sequentially.

## State and Persistence
No persistent state is changed. It reads repository commit contents and writes bytes to stdout.

## Dependencies and Integration Points
Uses `ostree_repo_read_commit`, GIO file/input/output streams, and Unix output stream integration. It is a simple content inspection command.

## Risks
Errors on any file stop the whole command after any previous files may already have been written. It does not insert separators between multiple files, matching `cat` behavior.

## Test Signals
Tests should cover one and multiple files, missing path, directory path errors, binary content, and commit resolution failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-cat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-checkout.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-checkout.c

## Purpose
Implements `ostree checkout`, materializing a commit or subpath into a filesystem tree, with modes for union checkout, whiteouts, SELinux labeling, hardlink/copy policy, composefs output, skip lists, and batch checkout input.

## Important APIs and Types
Exports `ostree_builtin_checkout`. Helpers include `parse_fsync_cb`, `handle_skiplist_line`, `checkout_filter`, `process_one_checkout`, and `process_many_checkouts`. Options configure user mode, cache, subpath, union modes, whiteout processing, allow-noent, stdin/file batch input, fsync policy, hardlink/copy behavior, bareuseronly dirs, skip-list, SELinux policy/prefix, and composefs/composefs-noverity.

## Control Flow
The command parses repo context and fsync policy, then either processes many null-delimited checkout records from stdin/file or resolves a single commit and destination. `process_one_checkout` chooses composefs if requested, otherwise uses the newer `ostree_repo_checkout_at` path when advanced options are set, or the older `ostree_repo_checkout_tree` path for coverage when simple options suffice. It validates incompatible modes, loads SELinux policy, builds optional skip-list filter, sets checkout flags, and executes checkout.

## State and Persistence
Writes the destination filesystem tree or composefs blob. It may update/use repo uncompressed object cache unless disabled, set xattrs/labels, create whiteout devices, hardlink/reflink/copy files, and alter fsync behavior on the repo.

## Dependencies and Integration Points
Uses repository checkout APIs, GIO input streams, Unix stdin streams, SELinux policy APIs, libglnx parsing helpers, and OSTree file abstractions. It is a major bridge from content-addressed commits to mutable filesystems.

## Risks
Option interaction is broad: union modes are mutually exclusive, union-identical requires hardlinks, SELinux prefix requires policy, composefs rejects many checkout options, and require-hardlinks conflicts with force-copy. Batch input is null-delimited and easy for callers to format incorrectly. Checkout affects real filesystem paths and can overwrite data depending on mode.

## Test Signals
Tests should cover simple checkout, subpath, allow-noent, each union mode and conflicts, whiteouts and passthrough whiteouts, hardlink/copy/fallback modes, zero-size copy, bareuseronly dirs, skip-list filtering, SELinux labeling/prefix, composefs and noverity options, fsync parsing, and batch stdin/file checkouts.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-checkout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-checksum.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-checksum.c

## Purpose
Implements `ostree checksum`, computing the OSTree file-object checksum for a filesystem path.

## Important APIs and Types
Exports `ostree_builtin_checksum`. Option `--ignore-xattrs` switches to a synchronous checksum path with `OSTREE_CHECKSUM_FLAGS_IGNORE_XATTRS`. `AsyncChecksumData` carries async completion state for the default path.

## Control Flow
After option parsing and path validation, the default path creates a `GFile`, starts `ostree_checksum_file_async`, runs a main loop until `on_checksum_received`, converts returned checksum bytes to hex, and prints them. With `--ignore-xattrs`, it calls `ostree_checksum_file_at` synchronously and prints the returned checksum.

## State and Persistence
No persistent state is changed. It reads the target file/directory metadata and content, including xattrs unless ignored, and writes the checksum to stdout.

## Dependencies and Integration Points
Uses OSTree checksum APIs, GLib main loop, GFile, and command parsing. It doubles as coverage for both async and sync checksum APIs.

## Risks
Default async behavior depends on correct main-loop completion and callback error propagation. Ignoring xattrs changes object identity semantics. Output is only printed after successful checksum completion.

## Test Signals
Tests should cover regular files, directories, xattr-sensitive differences, `--ignore-xattrs`, missing path, async error propagation, and checksum compatibility with repository object checksums.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-checksum.c -->
