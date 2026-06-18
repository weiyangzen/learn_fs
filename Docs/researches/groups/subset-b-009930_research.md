# Research: subset-b-009930

Grouped research for source4 registry, samba3 smbpasswd, and socket helper files. Each section preserves the source path in its title and uses deterministic delimiters for source-tree-aligned split reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/patchfile_preg.c -->
# sources/user-network-fs/samba/source4/lib/registry/patchfile_preg.c

## Purpose

`patchfile_preg.c` implements import and export of Windows Group Policy `Registry.pol` PReg patch files through Samba's registry diff callback interface. It serializes registry diff operations as UTF-16 bracketed records after a `PReg` header and parses those records back into generic add, set, delete-value, delete-all-values, and delete-key callbacks.

## Important APIs, Types, and Functions

`struct preg_data` carries the output file descriptor and talloc context used by save callbacks. `reg_preg_diff_save()` creates the writer callback table. `reg_preg_diff_load()` parses an existing PReg stream. Internal helpers `preg_read_utf16()` and `preg_write_utf16()` convert one UTF-16 code unit or a UTF-8 string to the on-disk encoding. Callback implementations include `reg_preg_diff_set_value()`, `reg_preg_diff_del_key()`, `reg_preg_diff_del_value()`, `reg_preg_diff_del_all_values()`, and `reg_preg_diff_done()`.

## Control Flow

Saving opens the requested file or stdout, writes the `PReg` magic and version 1 header, and returns callbacks consumed by `reg_generate_diff()`. Normal value updates write `[key;value;type;length;raw-data]` with UTF-16 delimiters but raw value bytes. Delete operations are represented with policy marker names such as `**Del.<name>`, `**DelVals.`, and `**DeleteKeys`.

Loading validates the eight-byte header, then loops record by record. It reads an opening `[`, key path, value name, binary type, binary length, binary data, and closing `]`, then translates special marker values into deletion callbacks or emits `add_key` plus `set_value` for ordinary entries. The loader closes the supplied file descriptor and frees its temporary talloc context at exit.

## State and Persistence Behavior

The file persists only the generated PReg patch stream. It does not directly mutate a registry; mutation happens only when the parsed callbacks are an apply callback set. Save-side cleanup closes the writer fd in `done()`. Load-side state is transient except that parsed callbacks may update the caller's registry. Delete-key export currently writes one `**DeleteKeys` value per deletion rather than accumulating multiple deletes as the FIXME notes.

## Dependencies and Integration Points

This file depends on `registry.h` for `struct reg_diff_callbacks`, `WERROR`, and `DATA_BLOB`, on generated winreg type constants, and on Samba byte-order/sys_rw helpers. It is wired into the `registry` library by `wscript_build` and used by `reg_diff_load()`, `reg_diff_apply()`, tests in `tests/diff.c`, and any tool that asks for PReg diff save/load.

## Risks and Edge Cases

Input parsing uses a fixed 1024-byte scratch buffer and does not grow for long key or value names. If `length >= buf_size`, the current data read is skipped but `data_blob_talloc()` still copies from the previous scratch buffer, which is a malformed-input risk. Several delimiter checks combine negation and bounds tests in a fragile way. `reg_preg_diff_del_key()` assumes the key path contains a backslash and repeatedly recomputes `strrchr()`, so top-level delete paths could misbehave. The format writes host memory through helper macros but still relies on correct little-endian handling for type and length.

## Test Signals

`tests/diff.c` creates two LDB-backed registries, saves a PReg diff through `reg_preg_diff_save()`, generates a diff, applies it, and verifies the expected HKLM path exists. Additional useful coverage would include long key/value names, large binary data, missing delimiters, grouped `**DeleteValues` and `**DeleteKeys`, top-level key delete attempts, and round trips against real Windows `Registry.pol` files.

Source-read signal: reviewed complete local file (387 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/patchfile_preg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/pyregistry.c -->
# sources/user-network-fs/samba/source4/lib/registry/pyregistry.c

## Purpose

`pyregistry.c` exposes a small Python module named `samba.registry` for opening Samba registry contexts and hive keys, mounting hives, applying diffs, manipulating hive values, and converting registry type ids to strings.

## Important APIs, Types, and Functions

The file defines Python types `PyRegistry`, `PyRegistryKey`, and `PyHiveKey`, backed by pytalloc-managed `struct registry_context`, `struct registry_key`, and `struct hive_key` pointers. Registry methods include `get_predefined_key_by_name()`, `get_predefined_key()`, `key_del_abs()`, `diff_apply()`, and `mount_hive()`. Hive-key methods include `del()`, `flush()`, `del_value()`, and `set_value()`. Module-level functions include `open_samba()`, `open_ldb()`, `open_hive()`, `str_regtype()`, and `get_predef_name()`.

## Control Flow

Module initialization readies the pytalloc-backed types, creates the module, and publishes HKEY constants. Constructing `Registry()` opens an empty local registry. `open_hive()` and `open_ldb()` convert Python loadparm and credentials objects to Samba C objects, call the matching C open routine, and return a `HiveKey`. `open_samba()` opens the full local Samba registry. Method wrappers parse Python arguments, call the underlying C registry API, translate `WERROR` failures into Python exceptions, and return stolen talloc objects or `None`.

## State and Persistence Behavior

The Python objects own or steal talloc references to C registry objects. Opening a hive may create or mutate backing LDB files depending on the lower backend. `HiveKey.set_value()` treats `None` data as a delete request; non-`None` bytes are passed as a `DATA_BLOB`. `mount_hive()` can alter the in-memory registry context by attaching a hive under a predefined key and optional elements list.

## Dependencies and Integration Points

The binding integrates Python C API compatibility headers, pytalloc, Samba WERROR-to-Python error helpers, loadparm Python conversion, credentials conversion, tevent context creation, and the registry C library. It is built as `samba/registry.so` by `wscript_build`.

## Risks and Edge Cases

Several wrappers accept optional `session_info` but then set `session_info = NULL`, so Python callers cannot currently pass real session state. `py_open_samba()` declares only two keyword names but parses three optional objects, which makes the credentials keyword contract unclear. `py_mount_hive()` allocates the elements array on `NULL` and does not append a NULL sentinel, so it depends on `reg_mount_hive()` using a known list length or tolerating the caller's layout. Python string/bytes handling for `set_value()` uses `z#`, so embedded NULs are accepted but require the caller to pass bytes-like data correctly.

## Test Signals

Build tests must import `samba.registry`, instantiate `Registry`, open LDB and REGF hives through `open_hive()`, set and delete hive values, apply a diff file, mount a hive under an HKEY constant, and check WERROR exception translation on missing keys and invalid type conversions.

Source-read signal: reviewed complete local file (494 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/pyregistry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/regf.c -->
# sources/user-network-fs/samba/source4/lib/registry/regf.c

## Purpose

`regf.c` is Samba's REGF hive backend for Windows NT registry hive files such as `NTUSER.DAT`. It implements `struct hive_operations` over on-disk `regf`, `hbin`, `nk`, `vk`, `sk`, `li`, `lf`, `lh`, and `ri` records generated from `regf.idl`.

## Important APIs, Types, and Functions

`struct regf_data` owns the open file descriptor, parsed header, HBIN array, and throttled write timestamp. `struct regf_key_data` wraps a generic `struct hive_key` with a REGF hive pointer, an HBIN offset, and the parsed `nk_block`. Public entry points are `reg_open_regf_file()` and `reg_create_regf_file()`. Backend operations are implemented by `regf_get_info()`, `regf_get_subkey_by_index()`, `regf_get_subkey_by_name()`, `regf_get_value()`, `regf_get_value_by_name()`, `regf_add_key()`, `regf_del_key()`, `regf_set_value()`, `regf_del_value()`, `regf_get_sec_desc()`, `regf_set_sec_desc()`, and `regf_flush_key()`.

## Control Flow

Opening a REGF file reads the full file, parses and checks the `regf` header, validates the checksum, pulls each HBIN block starting at file offset `0x1000`, and returns the root `nk` as a hive key. Creating a REGF file initializes a header, lazily allocates the first HBIN, writes a root `nk` named `SambaRootKey`, creates a default authenticated-users security descriptor, stores an `sk` block at offset `0x80`, and flushes the file.

Most reads map a logical REGF offset to an HBIN and relative offset with `hbin_by_offset()`, validate the signed cell length in `hbin_get()`, then TDR-pull the typed block. Subkey enumeration and lookup understand direct lists (`li`), first-four-character hash lists (`lf`), base37 hash lists (`lh`), and recursive index lists (`ri`). Value enumeration reads the value-list cell, pulls a `vk_block`, and either returns inline DWORD data from `vk.data_offset` when the high bit is set or returns an HBIN-backed blob.

Writes allocate, resize, or free HBIN cells with `hbin_alloc()`, `hbin_store_resize()`, and `hbin_free()`. Adding a key creates an `nk`, inserts its offset into the parent list in case-insensitive sorted order, updates parent counts, and flushes on the backend's throttle. Deleting a key recursively deletes children and values before removing the key from the parent subkey list. Setting a value updates or creates a `vk`, stores non-DWORD data in an HBIN cell, adjusts the value-list cell, then stores the changed `nk`.

## State and Persistence Behavior

REGF files are held in memory as parsed HBIN blocks and written back wholesale by `regf_save_hbin()`. Saves are throttled to at most once every five seconds unless a flush or destructor requests a forced write. The talloc destructor flushes and closes the file descriptor. Security descriptors are shared through a circular `sk` list with reference counts; `regf_set_sec_desc()` decrements or removes the old descriptor, reuses an equivalent descriptor when found, or appends a new one.

## Dependencies and Integration Points

The backend depends on generated TDR parsers from `regf.idl`, NDR security descriptor push/pull, `winreg` type constants, Samba security helpers, talloc lifetime management, byte-order macros, and low-level file I/O. It plugs into the generic hive API declared in `registry.h`; `tests/hive.c` exercises it alongside the LDB backend, and tools can open REGF files through `reg_open_hive()` or `reg_common_open_file()`.

## Risks and Edge Cases

This backend manipulates a complex binary allocator and several paths have fragile arithmetic. `hbin_store_resize()` compares possible combined free space to `blob.length` rather than the aligned needed size, and the loop starts at the original used cell, so grow-in-place behavior deserves scrutiny. `regf_set_sec_desc()` stores `private_data->nk` using `tdr_push_sk_block` in the final call, which appears inconsistent with the intended NK write. `regf_sl_add_entry()` has a memory check on `lf.hr[lf.key_count].hash` after writing `lf.hr[i].hash`. `ri` list add/delete are explicitly unsupported. Header checksum, dirty/free cell signs, list counts, sorted key order, inline DWORD handling, and security descriptor reference counts are all corruption-sensitive.

## Test Signals

`tests/hive.c` creates REGF hives with minor version 5 and runs add/delete key, recursive delete, value set/get/list/delete, flush, info, and security descriptor round trips. Additional high-value tests should reopen after delayed and forced flush, exercise minor versions 2/3/4/5, add enough subkeys to trigger larger lists, cover `ri` read-only hives, resize values from small to large and back, and validate Windows can load files Samba creates.

Source-read signal: reviewed complete local file (2321 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/regf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/regf.idl -->
# sources/user-network-fs/samba/source4/lib/registry/regf.idl

## Purpose

`regf.idl` defines the TDR-serializable structures for the Windows REGF registry hive format used by `regf.c`. It is the schema source for generated parsers and pushers for REGF headers, HBIN containers, key records, value records, security records, and subkey-list records.

## Important APIs, Types, and Functions

The IDL exports `regf_hdr`, `hbin_block`, `nk_block`, `sk_block`, `lh_block`, `li_block`, `ri_block`, `vk_block`, and `lf_block`. It also defines `regf_version`, `reg_key_type`, `lh_hash`, and `hash_record`, plus `REGF_OFFSET_NONE`. Generated functions such as `tdr_pull_regf_hdr()`, `tdr_push_hbin_block()`, and `tdr_pull_nk_block()` are consumed by `regf.c`.

## Control Flow

There is no runtime control flow in the IDL itself. At build time `wscript_build` runs `SAMBA_PIDL('PIDL_REG', source='regf.idl', options='--header --tdr-parser')`, producing C definitions and TDR functions. At runtime `regf.c` uses those generated routines to parse cells returned by `hbin_get()` and to serialize changed blocks into HBIN storage or the output file descriptor.

## State and Persistence Behavior

The schema captures persisted REGF state: header update counters, modification time, version, root data offset, HBIN sizes, signed cell lengths, key metadata, value metadata, and circular security descriptor lists. Variable-length arrays are tied to count or length fields, so mismatches between record counts and actual cell sizes become parser and corruption risks.

## Dependencies and Integration Points

The IDL depends on Samba PIDL/TDR conventions, NTTIME, DOS and UTF16 charset annotations, and generated C support. It integrates directly with `TDR_REGF` and the private `registry` library. REGF tests indirectly verify the generated types by creating and reading hives.

## Risks and Edge Cases

The schema documents partially understood fields (`uk*`, `unknown_offset`, `unk3`) and assumes DOS-encoded key/value names. `vk_block.data_length` uses its top bit to indicate inline data, so consumers must mask it correctly. REGF minor-version differences determine whether subkey lists are LI, LF, or LH, and the schema also allows RI indirection that write support does not fully implement.

## Test Signals

Build success of `PIDL_REG` and `TDR_REGF` is the primary compile signal. Runtime signals come from opening real REGF hives, creating Samba REGF hives, round-tripping key/value/security changes, and parsing all list record kinds (`li`, `lf`, `lh`, and `ri`).

Source-read signal: reviewed complete local file (167 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/regf.idl -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/registry.h -->
# sources/user-network-fs/samba/source4/lib/registry/registry.h

## Purpose

`registry.h` is the central private/public contract for Samba source4 registry code. It defines both the low-level hive API for one backing store and the higher-level registry API that mounts predefined-key views over one or more hives.

## Important APIs, Types, and Functions

The hive layer centers on `struct hive_key` and `struct hive_operations`, whose methods enumerate, open, add, delete, flush, get/set values, delete values, get/set security descriptors, and query key metadata. The registry layer centers on `struct registry_context`, `struct registry_key`, `struct registry_value`, and `struct registry_operations`, with similar operations plus predefined-key resolution, load/unload, notifications, and hive mounting. The header declares REGF, LDB, directory, Samba-local, remote RPC, and Wine open functions; utility conversion helpers; absolute-path helpers; diff callbacks; and diff load/save/apply entry points.

## Control Flow

Callers open a hive through `reg_open_hive()` or a concrete backend, or open a whole registry through `reg_open_local()`, `reg_open_samba()`, or `reg_open_remote()`. Generic wrappers dispatch through the operation tables. Mounting imports a hive root under a predefined handle and optional path elements. Diff generation compares two registry contexts and emits callback events; diff loading parses a patch file and invokes callbacks that apply changes or save another patch format.

## State and Persistence Behavior

The header does not persist state itself but defines the ownership and mutation boundaries. Hive implementations own backing storage and flush semantics. Registry contexts own mounted predefined keys. `DATA_BLOB` values carry caller-managed talloc memory. Security descriptors and notifications are optional backend features and may return `WERR_NOT_SUPPORTED`.

## Dependencies and Integration Points

This file includes talloc, WERROR, NTSTATUS, security descriptors, time, and data blobs. It is included by REGF, LDB, local, RPC, patchfile, Python binding, tools, and tests. It bridges generated winreg constants and Samba-specific backend implementations.

## Risks and Edge Cases

Operation-table APIs rely on every backend honoring optional output pointer conventions and consistent error codes. Several TODO-style areas are exposed in the contract, including notifications, load/unload support, and security descriptor support. The `access_mask` argument to `reg_key_add_abs()` exists but not all backends use it. Callers must understand that hive keys and registry keys are distinct wrappers even when a local mounted hive makes them look similar.

## Test Signals

`tests/hive.c`, `tests/registry.c`, and `tests/diff.c` exercise the declared surface through LDB, REGF, local registry, and diff paths. Compile coverage across Python bindings and tools catches signature drift. Useful additional tests would verify unsupported-operation behavior for every backend method.

Source-read signal: reviewed complete local file (531 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/registry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/rpc.c -->
# sources/user-network-fs/samba/source4/lib/registry/rpc.c

## Purpose

`rpc.c` implements a remote registry backend by translating generic `struct registry_operations` calls into MS-RRP/winreg DCE/RPC requests. It lets callers use the same registry API against a local `ncalrpc:` winreg endpoint or a remote server.

## Important APIs, Types, and Functions

`struct rpc_registry_context` stores the generic context, DCE/RPC pipe, and binding handle. `struct rpc_key` stores a generic key wrapper, winreg policy handle, binding handle, cached key metadata, and last change time. Public entry point `reg_open_remote()` connects to the winreg pipe. Backend methods include `rpc_get_predefined_key()`, `rpc_open_key()`, `rpc_get_subkey_by_index()`, `rpc_get_value_by_index()`, `rpc_get_value_by_name()`, `rpc_set_value()`, `rpc_del_value()`, `rpc_add_key()`, `rpc_del_key()`, `rpc_query_key()`, and `rpc_get_info()`.

## Control Flow

`reg_open_remote()` initializes DCE/RPC, defaults a missing location to `ncalrpc:`, connects with the caller's credentials/loadparm/event context, and installs `reg_backend_rpc`. Predefined-key opens use generated `winreg_OpenHK*` calls selected from `known_hives[]`. Key opens, enumeration, queries, creates, deletes, and value operations allocate winreg request structures, fill the parent policy handle and buffers, call the `_r` RPC stubs, translate transport NTSTATUS failures, and return server-side WERROR results.

## State and Persistence Behavior

The backend itself caches `QueryInfoKey` results in `struct rpc_key` by using `num_values == -1` or `num_subkeys == -1` as an unqueried marker. Mutations are persisted by the remote registry service, not locally. Open policy handles live as long as their talloc-backed key objects; this file does not explicitly close handles.

## Dependencies and Integration Points

It depends on generated `ndr_winreg_c.h` RPC clients, DCE/RPC pipe connection helpers, Samba credentials/loadparm/tevent context, `registry.h`, and winreg constants. CLI tools call it through `reg_common_open_remote()` and Python uses it indirectly through local/remote registry APIs where exposed.

## Risks and Edge Cases

Fixed `MAX_NAMESIZE` and `MAX_VALSIZE` buffers may be too small for some remote values or names, and the value buffer is declared as one byte but passed with a large size pointer, relying on NDR allocation behavior. Cached key metadata is not invalidated after mutations. Access masks are hard-coded (`SEC_FLAG_MAXIMUM_ALLOWED` or `0x02000000`) rather than caller-specific. Missing explicit handle close can matter for long-running tools. Security descriptor, flush, load/unload, and notification operations are absent from this backend table.

## Test Signals

Coverage should include opening each predefined hive, enumerating keys/values, reading and writing normal and large values, creating and deleting keys, remote access denied cases, local `ncalrpc:` default behavior, and cache behavior after mutations. Existing registry tests mostly exercise the local backend, so RPC-specific integration tests are important.

Source-read signal: reviewed complete local file (578 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/samba.c -->
# sources/user-network-fs/samba/source4/lib/registry/samba.c

## Purpose

`samba.c` opens Samba's local registry view by mounting named private-directory hive files under standard predefined HKEY roots. It is the source4 local-registry composition layer above the generic local registry and concrete hive backends.

## Important APIs, Types, and Functions

`reg_open_samba()` is the public entry point. `mount_samba_hive()` constructs `<private_dir>/<name>.ldb`, opens the hive with `reg_open_hive()`, falls back to `reg_open_ldb_file()` on `WERR_FILE_NOT_FOUND`, and mounts it with `reg_mount_hive()`.

## Control Flow

`reg_open_samba()` first creates an empty local registry context with `reg_open_local()`. It then attempts to mount `hklm.ldb`, `hkcr.ldb`, `hkcu.ldb`, and `hku.ldb` under `HKEY_LOCAL_MACHINE`, `HKEY_CLASSES_ROOT`, `HKEY_CURRENT_USER`, and `HKEY_USERS`. The helper returns an error on mount failure, but the caller currently does not check individual mount results.

## State and Persistence Behavior

The function can create missing LDB hive files in Samba's private directory through the fallback open path. The returned registry context is in-memory, while mounted hives persist through their LDB backend. There is no direct support here for dynamic keys, alias keys, or user-profile NTUSER.DAT loading.

## Dependencies and Integration Points

It depends on loadparm's private directory, registry local/hive mounting APIs, authentication session info, credentials, and tevent. CLI tools use `reg_common_open_local()`, Python exposes `open_samba()`, and tests can mount hives explicitly for isolated local registries.

## Risks and Edge Cases

Ignored `mount_samba_hive()` results mean `reg_open_samba()` can return success with missing predefined roots. FIXME comments document incomplete Windows semantics for HKCR merging, HKCU profile loading, HKCC aliasing, performance data, hardware, and SAM/Security aliases. Callers that assume all standard roots exist need to handle missing-key errors.

## Test Signals

Tests should check that `reg_open_samba()` mounts all intended hives when the private directory is writable, reports or tolerates missing hives consistently, and creates LDB hive files on first run. Tool smoke tests for `regtree`, `regshell`, and `regpatch` without `--remote` cover this path.

Source-read signal: reviewed complete local file (100 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/samba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tests/diff.c -->
# sources/user-network-fs/samba/source4/lib/registry/tests/diff.c

## Purpose

`tests/diff.c` is the torture suite for registry diff generation and application. It verifies both PReg and `.reg` patch save paths against local LDB-backed registries.

## Important APIs, Types, and Functions

`struct diff_tcase_data` stores two registry contexts, diff callbacks, callback data, temp directory, and generated patch filename. `diff_setup_tcase()` builds the source and target registries. `diff_setup_preg_tcase()` and `diff_setup_dotreg_tcase()` select the output format. Tests include `test_generate_diff()`, `test_diff_apply()`, `test_generate_diff_key_add()`, and `test_generate_diff_key_null()`, though the add-key test currently returns before exercising assertions.

## Control Flow

Setup creates two local registry contexts, mounts HKLM and HKCU LDB hives for each, populates r1 with `HKCU\Network\L`, populates r2 with `HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer`, and writes a `NoDrives` DWORD. Format-specific setup initializes callbacks with either `reg_preg_diff_save()` or `reg_dotreg_diff_save()`. The generate test calls `reg_generate_diff()`. The apply test applies the generated patch to r1 and then walks the expected HKLM path.

## State and Persistence Behavior

All registry state is created in a torture temp directory. The patch file is persisted as `test.pol` or `test.reg` and then applied to mutate r1. Test lifetime and cleanup are managed by the torture context.

## Dependencies and Integration Points

The suite uses the registry API, LDB hive backend, PReg and dotreg diff writers, the generic diff engine, winreg constants, loadparm/event context from torture, and Samba torture assertion helpers. It is included in the `torture_registry` subsystem by `wscript_build`.

## Risks and Edge Cases

The suite checks only one high-level creation path and one value, so delete operations, value data comparisons after apply, and error handling remain lightly covered. The early return in `test_generate_diff_key_add()` disables an intended direct callback test. Because apply correctness is inferred by opening a path, a broken value update could pass.

## Test Signals

Passing PReg and dotreg tcase runs signal that diff callbacks can write files, `reg_generate_diff()` emits a usable patch, and `reg_diff_apply()` can create missing nested keys. Stronger signals would assert value content, deletion markers, no-op diffs, and malformed patch rejection.

Source-read signal: reviewed complete local file (291 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tests/diff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tests/generic.c -->
# sources/user-network-fs/samba/source4/lib/registry/tests/generic.c

## Purpose

`tests/generic.c` is the top-level registry torture suite and focused unit coverage for registry value formatting helpers.

## Important APIs, Types, and Functions

It defines tests for `str_regtype()`, `reg_val_data_string()` across DWORD, DWORD_BIG_ENDIAN, QWORD, SZ, binary, and empty data, and `reg_val_description()` with normal and NULL names. `torture_registry()` assembles the generic tests plus the hive, registry, and diff sub-suites.

## Control Flow

Each simple test constructs minimal `DATA_BLOB` inputs, calls the formatting helper, and compares exact strings. The suite then nests `torture_registry_hive()`, `torture_registry_registry()`, and `torture_registry_diff()` so one registry test entry covers utility functions and backend behavior.

## State and Persistence Behavior

The file itself has no persistent state. It uses the torture context for allocations and passes transient blobs to conversion helpers. Nested suites create their own temp hives and registries.

## Dependencies and Integration Points

It depends on `registry.h`, winreg constants, loadparm/torture infrastructure, and generated test prototypes. It validates helper behavior consumed by `regtree`, `regshell`, Python `str_regtype()`, and diff/patch output paths.

## Risks and Edge Cases

The SZ tests convert without a trailing NUL in one case and manually shorten the blob to assert truncation behavior, but REG_MULTI_SZ and unsupported types are not covered. DWORD_BIG_ENDIAN currently expects the same little-endian formatting as DWORD, which documents existing behavior but may not match intuitive big-endian display semantics.

## Test Signals

Exact string comparisons catch accidental display format changes. Additional tests should cover `reg_string_to_val()` parsing, `REG_EXPAND_SZ`, `REG_MULTI_SZ`, invalid data lengths that trigger assertions, and round-trip display/parse behavior.

Source-read signal: reviewed complete local file (179 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tests/generic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tests/hive.c -->
# sources/user-network-fs/samba/source4/lib/registry/tests/hive.c

## Purpose

`tests/hive.c` tests the low-level hive API independently of predefined registry mounting. It runs the same behavioral checks against LDB hives and newly created REGF hives.

## Important APIs, Types, and Functions

Fixture setup functions are `hive_setup_ldb()` and `hive_setup_regf()`. Test helpers cover deletion of nonexistent keys, root key info, subkey/value counts, add/delete key, recursive delete, flush, value set/get/list/delete, and security descriptor get/set. The suite builder is `torture_registry_hive()`.

## Control Flow

Each fixture creates a temporary path, removes the directory placeholder, and opens either an LDB hive or REGF file. Tests operate directly on the root `struct hive_key`: adding subkeys with `hive_key_add_name()`, setting DWORD values, querying info, enumerating by index, deleting values and keys, and verifying WERROR results. The security test creates an authenticated-users descriptor, sets it on a subkey, reads it back, then repeats after setting a fresh equivalent descriptor.

## State and Persistence Behavior

State is persisted in temporary LDB or REGF backing files during a test case. The recursive delete test intentionally runs before the root-info test because it verifies cleanup left no root subkeys. REGF persistence is indirectly covered through backend flush and destructor behavior, but the tests do not reopen the file after mutation.

## Dependencies and Integration Points

The file integrates registry hive APIs, winreg constants, filesystem helpers, loadparm/event torture context, and Samba security descriptor helpers. It is compiled into `torture_registry`.

## Risks and Edge Cases

The same test names run across two backends, which is useful for contract consistency, but tests do not cover large values, default value names in the hive layer, class names, deep subkey list growth, RI list support, or malformed backing stores. Security descriptor comparison checks equality but not reference-count behavior in REGF.

## Test Signals

Passing both LDB and REGF tcase variants signals that backend add/delete/list/value/security operations meet the hive contract. High-value additions would reopen mutated hives, test value resizing, add many sorted subkeys, and verify backend-specific unsupported-operation errors.

Source-read signal: reviewed complete local file (440 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tests/hive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tests/registry.c -->
# sources/user-network-fs/samba/source4/lib/registry/tests/registry.c

## Purpose

`tests/registry.c` tests the higher-level registry API over a local registry context with a mounted HKCR LDB hive. It verifies predefined-key resolution, absolute path helpers, key/value operations, enumeration, flush, metadata, and security descriptors.

## Important APIs, Types, and Functions

`setup_local_registry()` opens a local registry, creates a temp LDB hive, and mounts it as `HKEY_CLASSES_ROOT`. Test functions include `test_get_predefined()`, `test_get_predefined_unknown()`, `test_predef_key_by_name()`, `test_create_subkey()`, `test_create_nested_subkey()`, `test_key_add_abs()`, `test_key_add_abs_top()`, `test_del_key()`, `test_flush_key()`, `test_query_key()`, `test_query_key_nums()`, `test_list_subkeys()`, `test_set_value()`, `test_security()`, `test_get_value()`, `test_del_value()`, and `test_list_values()`.

## Control Flow

Most tests first call `create_test_key()` to open HKCR and create a named subkey. They then dispatch through registry-level wrappers such as `reg_key_add_name()`, `reg_open_key()`, `reg_key_get_info()`, `reg_val_set()`, `reg_key_get_value_by_name()`, `reg_key_get_value_by_index()`, `reg_del_value()`, `reg_key_del()`, `reg_get_sec_desc()`, and `reg_set_sec_desc()`. The suite builder installs all tests in one local tcase.

## State and Persistence Behavior

The mounted HKCR hive is a temp LDB file. Tests mutate it by adding keys and values and deleting selected entries. Some tests rely on independent names to avoid clashes in the shared fixture context. Default unnamed values are explicitly tested with empty value names.

## Dependencies and Integration Points

The file exercises `registry.h` APIs, the local registry backend, LDB hive backend, winreg constants, security descriptor helpers, and torture infrastructure. It complements `tests/hive.c` by testing path parsing and predefined root behavior rather than raw hive calls.

## Risks and Edge Cases

Duplicate test names appear in `tcase_add_tests()` for some cases, which may affect reporting clarity. The suite mounts only HKCR, so multi-hive behavior and other predefined roots are not covered. The tests do not inspect persistence after process teardown, notification/load/unload paths, or RPC-specific behavior.

## Test Signals

Passing this suite signals correct local mounted-registry operation for common CRUD and lookup workflows. Additional signal would come from absolute delete tests, multi-root mounting, case-insensitive predefined names beyond HKCR, path traversal edge cases, and reopened-hive persistence checks.

Source-read signal: reviewed complete local file (645 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tests/registry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/common.c -->
# sources/user-network-fs/samba/source4/lib/registry/tools/common.c

## Purpose

`tools/common.c` provides shared open helpers for source4 registry command-line tools. It hides the choice between remote winreg, local Samba registry, and a single hive file imported into a local registry context.

## Important APIs, Types, and Functions

`reg_common_open_remote()` calls `reg_open_remote()` and prints failures. `reg_common_open_file()` opens a hive with `reg_open_hive()`, creates a local registry context, and imports the hive root as a registry key. `reg_common_open_local()` calls `reg_open_samba()`.

## Control Flow

Each helper attempts one backend open path, checks `WERROR`, reports to stderr on failure, and returns either a registry context or start key. File opens use the supplied event, loadparm, and credentials objects for backend selection and LDB access. The imported file key's context is used by tools that traverse or edit a standalone hive.

## State and Persistence Behavior

Remote opens mutate remote state only when callers later perform operations. Local opens may create or update Samba private LDB hives through `reg_open_samba()`. File opens can return a mutable imported hive root, and changes persist according to the backing hive backend.

## Dependencies and Integration Points

It depends on credentials, tevent, loadparm, and the registry library. `regpatch`, `regshell`, and `regtree` all use these helpers; `regdiff` has its own open-backend helper for two-context diffing.

## Risks and Edge Cases

The helper prints errors but drops detailed ownership and cleanup information. `reg_common_open_file()` returns a key instead of a context, so callers must treat file mode differently. Importing with predef key `-1` relies on local registry import semantics and may not expose normal predefined-key behavior.

## Test Signals

Tool smoke tests should cover `--remote`, local default, and `--file` modes, including failed connection/file paths. Existing registry tests cover underlying APIs but not these stderr/reporting wrappers directly.

Source-read signal: reviewed complete local file (88 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/regdiff.c -->
# sources/user-network-fs/samba/source4/lib/registry/tools/regdiff.c

## Purpose

`regdiff.c` implements the `regdiff` command, which compares two registry backends and writes a `.reg` diff file or stdout output.

## Important APIs, Types, and Functions

The local `enum reg_backend` distinguishes unknown, local Samba, remote winreg, and null/empty registries. `open_backend()` maps parsed options to `reg_open_samba()`, `reg_open_remote()`, or `reg_open_local()`. `main()` handles command-line parsing and diff generation.

## Control Flow

The command accepts two backend selectors in order: `--local`, `--remote HOST`, or `--null`. After Samba command-line initialization and popt parsing, it opens backend 1 and backend 2, initializes dotreg diff callbacks with `reg_dotreg_diff_save()`, then calls `reg_generate_diff(h1, h2, callbacks, callback_data)`. Errors are printed and exit nonzero.

## State and Persistence Behavior

The command does not mutate the compared registries. It persists the generated diff to `--output` when supplied, otherwise through the dotreg writer's default behavior. Remote backends hold RPC connections for command lifetime, and local backends may create missing local Samba hives during open.

## Dependencies and Integration Points

It uses Samba command-line/loadparm/credentials setup, tevent, popt, registry backends, and dotreg diff callbacks. It is built as a `regdiff` binary with manpage wiring in `wscript_build`.

## Risks and Edge Cases

Exactly two backend selectors are required; missing or extra selectors can result in usage output or ignored state depending on parse order. Only dotreg output is supported here despite the library also supporting PReg save. Error reporting does not include which backend failed beyond the generic message from `open_backend()`.

## Test Signals

Smoke tests should compare null-to-local, local-to-null, and remote-to-local when available, verify output file creation, and apply the generated patch with `regpatch` to confirm semantic correctness. The lower diff engine is covered by `tests/diff.c`.

Source-read signal: reviewed complete local file (182 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/regdiff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/regpatch.c -->
# sources/user-network-fs/samba/source4/lib/registry/tools/regpatch.c

## Purpose

`regpatch.c` implements the `regpatch` command, which applies a registry patch file to a local or remote registry.

## Important APIs, Types, and Functions

`main()` is the only function. It parses `--remote HOST` and `--file PATH`, opens either a remote registry with `reg_common_open_remote()` or local Samba registry with `reg_common_open_local()`, fetches the patch path argument, and calls `reg_diff_apply()`.

## Control Flow

After command-line initialization, popt parsing validates options and obtains credentials/loadparm/event context. Remote mode wins when `--remote` is present; otherwise the command opens local Samba registry. The positional patch filename is required. The command burns argv credentials, applies the diff, frees the talloc context, and exits 0 without checking the `reg_diff_apply()` result.

## State and Persistence Behavior

This tool mutates the target registry according to the patch file. Remote mutations persist on the remote winreg server; local mutations persist in Samba private hives. It does not itself store state beyond transient command context.

## Dependencies and Integration Points

It integrates common registry open helpers, diff loading/application, Samba command-line initialization, credentials, loadparm, and tevent. It is built as `regpatch` with a manpage in `wscript_build`.

## Risks and Edge Cases

The parsed `--file` option is stored but unused; patch input is positional. The return value of `reg_diff_apply()` is ignored, so apply failures can still produce exit status 0. Usage/error paths are minimal, and there is no dry-run mode.

## Test Signals

Tool tests should apply valid dotreg and PReg files to temp local registries, verify failure exit status for malformed or missing patch files, and ensure remote apply errors propagate. Existing `tests/diff.c` covers library apply behavior but not this command's exit handling.

Source-read signal: reviewed complete local file (119 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/regpatch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/regshell.c -->
# sources/user-network-fs/samba/source4/lib/registry/tools/regshell.c

## Purpose

`regshell.c` implements an interactive registry shell for browsing and editing local, remote, or file-backed registry trees.

## Important APIs, Types, and Functions

`struct regshell_context` stores the registry context, current relative path, current predefined root name, current key, and root key. Commands include `ck/cd`, `info`, `list/ls`, `print`, `mkkey/mkdir`, `rmval/rm`, `rmkey/rmdir`, `pwd/pwk`, `set/update`, `predef`, `help`, and `exit/quit`. Important helpers are `get_full_path()`, `process_cmd()`, `reg_complete_command()`, `reg_complete_key()`, and `reg_completion()`.

## Control Flow

Startup parses `--file` and `--remote`, opens the selected backend, and chooses an initial key. File mode imports a hive and starts at that root; remote and local modes try predefined keys until one opens. The main loop builds a prompt from predef plus path, installs the current key for readline completion, reads a command line, parses it with `poptParseArgvString()`, dispatches to the command table, and updates the return status based on WERROR success.

## State and Persistence Behavior

The shell holds mutable current key/path state in memory. Commands can persistently set values, create keys, delete values, delete keys, and flush keys through the backend. `set` parses text data through `reg_string_to_val()`. `predef` changes the root to another predefined key. File-backed and local-backed changes persist via their hive backends; remote changes persist on the server.

## Dependencies and Integration Points

It depends on the registry library, common tool open helpers, Samba command-line/credentials/loadparm, tevent, readline abstraction `smb_readline`, NDR debug printing for security descriptors, and value conversion helpers. It is built as `regshell` with `SMBREADLINE` and `registry_common`.

## Risks and Edge Cases

`get_full_path()` mutates the supplied `path` through `strtok(discard_const_p(...))`, so passing immutable argv storage is risky. `process_cmd()` assumes `argv[0]` exists, so an empty parsed line can crash. Completion has off-by-one-looking `samelen` handling and uses a global `current_key` because readline cannot pass private data. `cmd_info()` returns success when security descriptor retrieval fails after printing an error, which may hide backend limitations. Text value parsing supports only selected types.

## Test Signals

Interactive tests should script navigation, path normalization with `.`, `..`, and absolute paths, setting and printing values, deleting keys/values, switching predefined roots, and command completion. Noninteractive smoke can pipe commands through readline-compatible input and inspect resulting registry state.

Source-read signal: reviewed complete local file (708 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/regshell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/regtree.c -->
# sources/user-network-fs/samba/source4/lib/registry/tools/regtree.c

## Purpose

`regtree.c` implements the `regtree` command, which recursively prints registry keys and optionally values from a local, remote, or file-backed registry.

## Important APIs, Types, and Functions

`print_tree()` recursively enumerates subkeys and values, prints key names or full paths, and touches security descriptors. `main()` parses `--file`, `--remote`, `--fullpath`, and `--no-values`, opens the selected backend, and starts traversal.

## Control Flow

In file mode, the command opens one imported hive key and prints it from `""`. In local or remote mode, it opens the registry context and iterates `reg_predefined_keys`, opening each available root and printing it. `print_tree()` prints indentation, enumerates subkeys by index, opens each subkey, recurses, then enumerates values and formats them through `reg_val_description()` unless values are disabled.

## State and Persistence Behavior

The command is read-only from a caller perspective. It allocates temporary talloc contexts for recursion and value/security descriptor retrieval. It does not persist output except to stdout and does not mutate registry data.

## Dependencies and Integration Points

It uses common registry open helpers, Samba command-line/credentials/loadparm setup, tevent, generic registry enumeration APIs, value formatting utilities, and security descriptor retrieval. It is built as `regtree` by `wscript_build`.

## Risks and Edge Cases

Recursive traversal has no cycle detection; unusual backend aliases or symbolic links could loop. Errors opening individual subkeys are silently skipped. Security descriptor retrieval errors are logged at debug level after traversal, and descriptors are not printed. Large registries can produce very large output and deep recursion.

## Test Signals

Smoke tests should run against a temp file hive and local Samba registry with and without `--fullpath` and `--no-values`, then assert key/value output ordering and formatting. Remote tests should verify skipped inaccessible predefined keys report useful stderr messages.

Source-read signal: reviewed complete local file (209 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/tools/regtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/util.c -->
# sources/user-network-fs/samba/source4/lib/registry/util.c

## Purpose

`util.c` provides registry value display/parsing helpers and absolute-path convenience operations over registry contexts.

## Important APIs, Types, and Functions

`reg_val_data_string()` converts typed `DATA_BLOB` values to printable strings. `reg_val_description()` formats `name = type : value`. `reg_string_to_val()` parses command/dotreg-like type and data strings into winreg type ids and blobs. Internal `reg_strhex_to_data_blob()` parses comma-tolerant hex bytes. Path helpers include `reg_open_key_abs()`, `get_abs_parent()`, `reg_key_del_abs()`, and `reg_key_add_abs()`.

## Control Flow

Display helpers switch on winreg type. String values are converted from UTF-16 to Unix charset, DWORD/QWORD values are formatted as hex, binary is upper hex, and unsupported or REG_NONE types may return NULL. Parsing first resolves the type string through `regtype_by_string()` or Windows textual forms (`hex(...)`, `hex`, `dword`), then converts data according to the resulting type. Absolute path helpers split the predefined root from the rest of a backslash-delimited path, open the root, then open/create/delete the final component.

## State and Persistence Behavior

Formatting is read-only and allocates result strings under the caller's talloc context. Parsing allocates blobs under the caller's context. `reg_key_del_abs()` and `reg_key_add_abs()` mutate the target registry context by deleting or creating keys; `reg_open_key_abs()` only returns a key.

## Dependencies and Integration Points

The file depends on `registry.h`, winreg constants, Samba charset conversion, data blob helpers, byte-order macros, and talloc. It is used by CLI tools (`regshell`, `regtree`), Python `str_regtype()` indirectly, diff code, and tests in `tests/generic.c` and `tests/registry.c`.

## Risks and Edge Cases

`REG_MULTI_SZ` formatting is not implemented. `REG_DWORD_BIG_ENDIAN` display and parsing use little-endian `IVAL`/`SIVAL`, so semantic big-endian handling is questionable. `reg_strhex_to_data_blob()` allocation length is approximate and ignores separators by scanning hex pairs; malformed input can truncate silently. Absolute path helpers return generic `WERR_FOOBAR` for missing backslashes and do not use the `access_mask` argument in `reg_key_add_abs()`.

## Test Signals

`tests/generic.c` covers several display paths and `tests/registry.c` covers absolute add and key operations. Missing but valuable tests include `reg_string_to_val()` for all supported type strings, invalid hex, `hex(type)`, QWORD, REG_NONE, REG_MULTI_SZ expectations, and absolute delete.

Source-read signal: reviewed complete local file (302 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/wine.c -->
# sources/user-network-fs/samba/source4/lib/registry/wine.c

## Purpose

`wine.c` is a placeholder for a Wine registry backend. It sketches an adapter for Wine registry files but does not implement usable behavior.

## Important APIs, Types, and Functions

The file declares `wine_open_reg()`, a `REG_OPS reg_backend_wine` table with `.name = "wine"`, `registry_wine_init()`, and `reg_open_wine()`. The functions refer to older-looking `registry_hive`, `REG_OPS`, and `register_backend()` interfaces rather than the `struct registry_operations` contract used by the rest of this directory.

## Control Flow

`registry_wine_init()` would register the backend if built and called. `wine_open_reg()` contains only a FIXME comment and no return. `reg_open_wine()` immediately returns `WERR_NOT_SUPPORTED`.

## State and Persistence Behavior

No state is loaded or persisted. Comments indicate intended future support for opening `~/.wine/system.reg` and related files, likely via mmap, but there is no implementation.

## Dependencies and Integration Points

It includes `lib/registry/common/registry.h` and `windows/registry.h`, which differ from the neighboring source4 registry headers. It is not listed in `wscript_build` for the `registry` library, so it appears stale or disabled.

## Risks and Edge Cases

If accidentally built, `wine_open_reg()` has undefined behavior due to missing return. The API mismatch suggests bitrot. Callers should rely on `reg_open_wine()` reporting not supported rather than expecting Wine registry access.

## Test Signals

The expected test signal is that this file is not part of the active build or that `reg_open_wine()` returns `WERR_NOT_SUPPORTED`. Any future implementation needs compile tests against current registry APIs and file-format tests for Wine registry text files.

Source-read signal: reviewed complete local file (45 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/wine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/wscript_build -->
# sources/user-network-fs/samba/source4/lib/registry/wscript_build

## Purpose

`wscript_build` wires the source4 registry subsystem into Samba's waf build. It generates REGF parsers, builds the private registry library, builds common tooling support, CLI tools, torture tests, and the Python extension module.

## Important APIs, Types, and Functions

Build declarations include `SAMBA_PIDL('PIDL_REG')`, `SAMBA_SUBSYSTEM('TDR_REGF')`, `SAMBA_LIBRARY('registry')`, `SAMBA_SUBSYSTEM('registry_common')`, `SAMBA_BINARY()` entries for `regdiff`, `regpatch`, `regshell`, and `regtree`, `SAMBA_SUBSYSTEM('torture_registry')`, and `SAMBA_PYTHON('py_registry')`.

## Control Flow

At build generation time, PIDL processes `regf.idl` with `--header --tdr-parser`. The registry library compiles interface, utility, Samba-local, patchfile, REGF, hive, local, LDB, and RPC sources. Tool binaries and torture sources depend on that library. Python embedding library names are computed and passed into `py_registry`.

## State and Persistence Behavior

This file affects build artifacts, not runtime registry state. It determines which source files are linked and therefore which backends and tools are available.

## Dependencies and Integration Points

Declared dependencies include `dcerpc`, `samba-util`, `TDR_REGF`, `ldb`, `RPC_NDR_WINREG`, `ldbsamba`, `util_reg`, hostconfig, popt, CMDLINE_S4, SMBREADLINE, torture, pytalloc-util, and pyparam_util. It also declares `registry.h` as a private header.

## Risks and Edge Cases

The active library source list omits `wine.c`, matching that file's placeholder status. Build dependency changes can break Python module linkage or generated REGF parser availability. Because the registry library is private, external consumers should not rely on ABI stability.

## Test Signals

Successful waf build of `registry`, `TDR_REGF`, CLI tools, `torture_registry`, and `samba/registry.so` is the primary signal. Running the torture registry suite verifies the compiled source set coheres.

Source-read signal: reviewed complete local file (69 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/registry/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/samba3/samba3.h -->
# sources/user-network-fs/samba/source4/lib/samba3/samba3.h

## Purpose

`samba3.h` is the small public header for Samba3 compatibility helpers in this directory. It exposes smbpasswd hash conversion routines.

## Important APIs, Types, and Functions

The header declares `smbpasswd_gethexpwd()` to parse a 32-character hex password hash into `struct samr_Password`, and `smbpasswd_sethexpwd()` to format a `struct samr_Password` or placeholder into smbpasswd text.

## Control Flow

There is no runtime control flow. Including translation units get security and SAMR generated types and the two helper prototypes.

## State and Persistence Behavior

The header defines no state. The declared functions allocate talloc-owned return values and are intended for parsing or emitting smbpasswd file fields.

## Dependencies and Integration Points

It includes generated `security.h` and `samr.h` types. `smbpasswd.c` implements the prototypes, and `wscript_build` compiles them into the private `smbpasswdparser` library.

## Risks and Edge Cases

The API exposes only hash-field conversion, not full smbpasswd line parsing. Callers must handle NULL returns for invalid input and own talloc lifetimes correctly.

## Test Signals

Compile coverage with `smbpasswd.c` catches prototype drift. Unit tests should parse valid/invalid 32-hex strings and format real, NULL, and password-not-required values.

Source-read signal: reviewed complete local file (29 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/samba3/samba3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/samba3/smbpasswd.c -->
# sources/user-network-fs/samba/source4/lib/samba3/smbpasswd.c

## Purpose

`smbpasswd.c` implements helpers for converting smbpasswd hash fields between textual 32-character hex and Samba's `struct samr_Password` binary hash representation.

## Important APIs, Types, and Functions

`smbpasswd_gethexpwd()` parses a hash string into a talloc-allocated `struct samr_Password`. `smbpasswd_sethexpwd()` formats a password hash as 32 hex characters or returns smbpasswd placeholder strings for NULL hashes based on account-control flags.

## Control Flow

Parsing rejects NULL input, allocates a password object, and calls `strhex_to_str()` to decode exactly 16 bytes from 32 hex characters. If decoding does not produce 16 bytes, it frees and returns NULL. Formatting calls `hex_encode_talloc()` when a password is present; otherwise it emits `NO PASSWORDXXXXXXXXXXXXXXXXXXXXX` when `ACB_PWNOTREQ` is set, or 32 `X` characters when no hash is stored.

## State and Persistence Behavior

The helpers do not read or write smbpasswd files directly. They allocate converted values under the caller's talloc context. The binary hash data is sensitive credential material and persists in memory until the caller frees it.

## Dependencies and Integration Points

It depends on Samba utility conversion helpers, generated SAMR account-control flags, and `samba3.h`. The private `smbpasswdparser` library exposes these helpers to Samba3 migration/import code.

## Risks and Edge Cases

There is no explicit memory scrubbing before freeing invalid or formatted hashes. Placeholder strings are legacy smbpasswd conventions and must remain exact. The parser accepts whatever `strhex_to_str()` accepts for hex case/format and rejects by decoded length only.

## Test Signals

Tests should cover valid uppercase/lowercase hex, short/long/invalid hex strings, NULL input, formatting NULL with and without `ACB_PWNOTREQ`, and round-tripping a known hash.

Source-read signal: reviewed complete local file (100 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/samba3/smbpasswd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/samba3/wscript_build -->
# sources/user-network-fs/samba/source4/lib/samba3/wscript_build

## Purpose

This `wscript_build` declares the source4 Samba3 smbpasswd parser helper library.

## Important APIs, Types, and Functions

It contains one `SAMBA_LIBRARY('smbpasswdparser')` declaration with `source='smbpasswd.c'`, dependency `samba-util`, and `private_library=True`.

## Control Flow

At waf build time, the declaration compiles `smbpasswd.c` into a private library. There is no runtime control flow.

## State and Persistence Behavior

The build rule has no runtime state. It controls artifact availability for code that needs smbpasswd hash parsing/formatting helpers.

## Dependencies and Integration Points

The only declared build dependency is `samba-util`, which supplies hex conversion and common utility support used by `smbpasswd.c`.

## Risks and Edge Cases

Because the library is private and very small, consumers must be in-tree. Missing generated SAMR include dependencies are satisfied indirectly by source includes rather than explicit build deps here.

## Test Signals

Successful build of `smbpasswdparser` and unit coverage of `smbpasswd_gethexpwd()`/`smbpasswd_sethexpwd()` are the relevant signals.

Source-read signal: reviewed complete local file (9 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/samba3/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/access.c -->
# sources/user-network-fs/samba/source4/lib/socket/access.c

## Purpose

`access.c` checks whether an accepted socket connection should be allowed for a Samba service based on allow and deny lists. It adapts tcp_wrappers-style access matching to Samba socket contexts.

## Important APIs, Types, and Functions

`socket_check_access()` is the exported decision function. Internal `only_ipaddrs_in_list()` determines whether host name lookups can be skipped because allow/deny tokens are IP addresses, network/netmask pairs, or special strings.

## Control Flow

If both allow and deny lists are empty, access is allowed immediately. Otherwise the function allocates a talloc context, fetches the peer address from the socket, optionally resolves the peer name when any list contains non-IP tokens, and calls `allow_access(deny_list, allow_list, name, addr->addr)`. It logs allowed connections at debug level 2 and denied connections at level 0.

## State and Persistence Behavior

The function has no persistent state. It allocates temporary address/name data and frees it before returning. Its only side effect is logging.

## Dependencies and Integration Points

It depends on Samba socket APIs, network system headers, IP address helpers, and `lib/util/access.h` matching logic. Services use it after accepting a socket and before processing service-specific protocols.

## Risks and Edge Cases

When peer address lookup fails, access is denied. Hostname resolution is skipped only if both lists are IP-only, so DNS delays or failures can affect connection setup when names are configured. Network/netmask tokens are treated as IP-only if they contain `/`, even if malformed; actual validation happens later in `allow_access()`.

## Test Signals

Tests should cover empty lists, allow-only, deny-only, deny overriding allow, `ALL`/`EXCEPT`/`FAIL`, IP-only bypass without reverse lookup, hostname-based rules, unknown peer address failure, and IPv4/IPv6 network tokens.

Source-read signal: reviewed complete local file (129 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/connect.c -->
# sources/user-network-fs/samba/source4/lib/socket/connect.c

## Purpose

`connect.c` implements event-aware nonblocking socket connect wrappers for Samba's tevent and composite async frameworks.

## Important APIs, Types, and Functions

`struct connect_state` stores the socket, optional local address, server address, and flags. Public APIs are `socket_connect_send()`, `socket_connect_recv()`, and `socket_connect_ev()`. Internal functions are `socket_send_connect()` and `socket_connect_handler()`.

## Control Flow

`socket_connect_send()` creates a composite context, references the socket and addresses, marks the socket fd nonblocking, and calls `socket_send_connect()`. That function calls low-level `socket_connect()`. Immediate fatal errors complete the composite with an error; `NT_STATUS_MORE_PROCESSING_REQUIRED` or success installs a tevent fd handler watching read/write. The handler calls `socket_connect_complete()` and completes the composite on success. `socket_connect_recv()` waits and frees the composite, while `socket_connect_ev()` provides a synchronous wrapper around the async path.

## State and Persistence Behavior

The connect operation state lives under the composite context and holds talloc references to socket/address inputs. The socket fd is left in nonblocking mode. Successful completion leaves the caller's socket connected; failures leave cleanup to the caller and talloc hierarchy.

## Dependencies and Integration Points

It depends on Samba socket APIs, tevent fd events, and `libcli/composite`. `connect_multi.c` builds racing multi-port connects on top of `socket_connect_send()`.

## Risks and Edge Cases

The fd handler is registered for both read and write, but connect completion usually depends on writability; spurious events rely on `socket_connect_complete()` correctness. There is no timeout in this file. If `socket_connect_send()` returns NULL, `socket_connect_ev()` passes NULL to recv, so callers should check allocation failures in direct async use.

## Test Signals

Tests should cover immediate connect success, EINPROGRESS completion, refused connections, unreachable addresses, local bind address use, nonblocking fd state, and event loop cancellation/freeing before completion.

Source-read signal: reviewed complete local file (158 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/connect_multi.c -->
# sources/user-network-fs/samba/source4/lib/socket/connect_multi.c

## Purpose

`connect_multi.c` races nonblocking connect attempts across all resolved addresses and multiple ports, returning the first successful socket or the last completion error. It can also run an optional post-connect establishment handshake before accepting a connection.

## Important APIs, Types, and Functions

`struct connect_multi_state` tracks resolved addresses, ports, current address/port cursor, sent/received attempt counts, winning socket/port, and optional `socket_connect_multi_ex` hooks. `struct connect_one_state` stores a single attempt's composite, socket, and address. Public APIs include `socket_connect_multi_ex_send()`, `socket_connect_multi_ex_recv()`, `socket_connect_multi_ex()`, `socket_connect_multi_send()`, `socket_connect_multi_recv()`, and `socket_connect_multi()`.

## Control Flow

The send function copies the caller's port list, starts `resolve_name_all_send()` for the server name using the first port, and continues in `continue_resolve_name()`. After resolution, `connect_multi_next_socket()` creates one socket for the current address/port, starts `socket_connect_send()`, advances the cursor, and sets a short timer to launch the next attempt even before the current one finishes. `continue_one()` receives a connect result; without hooks, a successful connect steals the socket and completes the composite, while failure triggers more attempts until all are received. With hooks, successful or failed raw connect completion is followed by `ex->establish_send()` and `continue_one_ex()` uses `establish_recv()` as the acceptance result.

## State and Persistence Behavior

All attempt state is talloc-owned by the composite. Timers are children of individual attempt state, so they vanish when that attempt state is freed. The winning socket is stolen to the caller in recv. Failed sockets and states are freed as attempts complete.

## Dependencies and Integration Points

It depends on name resolution (`resolve_name_all_send/recv`), Samba socket creation/connect wrappers, tevent timers, and composite async control. Higher-level SMB or RPC clients can use it to try NetBIOS/SMB ports or perform transport-specific establishment checks.

## Risks and Edge Cases

`MULTI_PORT_DELAY` is documented as microseconds and set to 2000, but comments say a couple of milliseconds; aggressive racing can create many simultaneous attempts for many addresses/ports. In `continue_one()`, the optional `ex` handshake is invoked regardless of raw connect `status`, so the hook must tolerate failed sockets or this path may be wrong. The final returned error is whichever attempt completes last, not necessarily the most informative. No explicit global timeout is provided here.

## Test Signals

Tests should simulate multiple addresses and ports with controlled success/failure ordering, verify the first successful port is returned, ensure all-fail returns an error after every attempt completes, cover DNS failure, check timer fan-out, and exercise `socket_connect_multi_ex` hooks for both accepted and rejected handshakes.

Source-read signal: reviewed complete local file (392 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/connect_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/interface.c -->
# sources/user-network-fs/samba/source4/lib/socket/interface.c

## Purpose

`interface.c` builds and queries Samba's configured local network interface list. It interprets `interfaces =` configuration entries, probes kernel interfaces, filters duplicates/loopback, and provides helper queries for IP, broadcast, netmask, best local source IP, local-network membership, same-net checks, and wildcard bind addresses.

## Important APIs, Types, and Functions

`struct interface` stores linked-list pointers, name, flags, sockaddr IP/netmask/broadcast, and string copies. Internal helpers are `iface_list_find()`, `add_interface()`, and `interpret_interface()`. Public helpers include `load_interface_list()`, `iface_list_count()`, `iface_list_n_ip()`, `iface_list_first_v4()`, `iface_list_n_is_v4()`, `iface_list_n_bcast()`, `iface_list_n_netmask()`, `iface_list_best_ip()`, `iface_list_is_local()`, `iface_list_same_net()`, and `iface_list_wildcard()`.

## Control Flow

`load_interface_list()` probes kernel interfaces with `get_interfaces()`. If no config list is set, it adds all non-loopback probed interfaces. If config tokens exist, each token is interpreted as an interface-name pattern, DNS/IP address, IP/masklen, IP/mask, network/mask, or broadcast/mask. Matched probed interfaces are added; otherwise explicit IP/mask tokens can create synthetic interface entries. Query helpers then walk the linked list to return indexed properties or match destination addresses against interface networks.

## State and Persistence Behavior

The interface list is allocated under the supplied talloc context and is otherwise in-memory only. String forms are stored to avoid static-buffer lifetime problems from address formatting. No system network configuration is changed.

## Dependencies and Integration Points

It depends on system networking headers, loadparm `lpcfg_interfaces()`, `lib/socket/netif.h`, util_net address helpers, Samba linked-list macros, and robust string-to-number conversion. Other Samba networking code uses the generated list for binding, source address selection, and local-network decisions.

## Risks and Edge Cases

`interpret_interface()` mutates config token strings when stripping `;` extras and splitting `/`, so it relies on writable configuration storage. IPv4 interfaces without broadcast or loopback flags are skipped. If no usable interface remains, only warnings are logged. Synthetic interfaces trust user-provided masks. Ordering is intentionally preserved with `DLIST_ADD_END()` because some tests depend on it, so changes to insertion order can be visible.

## Test Signals

Tests should cover empty config with loopback filtering, wildcard interface-name matches, DNS/IP tokens, CIDR and explicit netmask tokens, broadcast/network address tokens, duplicates, IPv6 behavior, best-source selection, local-network checks, wildcard list generation, and config entries with semicolon metadata.

Source-read signal: reviewed complete local file (530 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/netif.h -->
# sources/user-network-fs/samba/source4/lib/socket/netif.h

## Purpose

`netif.h` is the small include aggregator for the source4 socket network-interface helpers.

## Important APIs, Types, and Functions

It includes system networking declarations, `lib/socket/interfaces.h`, and generated `lib/socket/netif_proto.h`. The actual interface structure and functions are implemented in `interface.c` and exposed through the included prototype header.

## Control Flow

There is no runtime control flow. Translation units include this header to get interface helper declarations and required socket/network types.

## State and Persistence Behavior

The header defines no state. Runtime state is the talloc-owned interface list managed by `interface.c`.

## Dependencies and Integration Points

It bridges system network headers with Samba socket interface/prototype headers. `interface.c` includes it directly, and callers of network interface helpers depend on the prototypes it aggregates.

## Risks and Edge Cases

Because this is an aggregator, stale or missing generated `netif_proto.h` would break compile consumers. Include ordering matters if platform network types are not available before the generated prototypes.

## Test Signals

Compile coverage of `interface.c` and callers validates this header. Runtime behavior is covered by tests for `load_interface_list()` and query helpers.

Source-read signal: reviewed complete local file (24 lines).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/lib/socket/netif.h -->
