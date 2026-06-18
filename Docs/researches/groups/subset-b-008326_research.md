# subset-b-008326 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/libecryptfs_wrap.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/libecryptfs_wrap.c

## Purpose
Generated SWIG 1.3.36 Python extension wrapper for a very small libecryptfs API surface. The module is initialized as `init_libecryptfs` and exposes Python-callable bindings for passphrase token blob generation, signature extraction from a blob, and adding a blob to the kernel user keyring.

## Important APIs, types, and functions
- `_wrap_ecryptfs_passphrase_blob(salt, passphrase)` converts Python string-like inputs to `char *`, calls `ecryptfs_passphrase_blob`, and returns the `binary_data` result as a Python string of explicit size.
- `_wrap_ecryptfs_passphrase_sig_from_blob(blob)` returns the password signature embedded in an auth-token blob.
- `_wrap_ecryptfs_add_blob_to_keyring(blob, sig)` forwards a raw blob and expanded-hex signature to libecryptfs and returns an integer status.
- `SWIG_AsCharPtrAndSize`, `SWIG_FromCharPtrAndSize`, and the `PySwigObject`/`PySwigPacked` runtime implement string, pointer, and packed-data conversions.
- `SwigMethods` is the exported Python method table; only the three functions above are bound.

## Control flow
Most of the file is SWIG runtime bootstrap and conversion machinery. Each wrapper parses a Python argument tuple, converts arguments to C buffers, calls the underlying libecryptfs function, converts the return value, releases temporary conversion buffers when SWIG allocated them, and jumps to a shared `fail` path on parse or conversion errors. Module initialization fixes method metadata, creates the Python module, initializes SWIG type information, and installs constants.

## State and persistence behavior
The wrapper itself persists no application state. Its effects are inherited from the called libecryptfs functions: generated auth-token blobs contain key material, and `ecryptfs_add_blob_to_keyring` mutates the caller's Linux user keyring. The returned Python binary strings copy raw C memory into Python objects, but the generated wrapper does not model higher-level ownership or secret zeroization.

## Dependencies and integration points
Depends on the Python 2 C API (`Py_InitModule`, `PyString_*`, `PyCObject_*`) and links against libecryptfs symbols declared near the generated wrapper body. It is normally regenerated from a SWIG interface rather than hand-edited, and it integrates Python callers with `key_management.c`.

## Risks and edge cases
The wrapper is Python 2 era code and will not compile cleanly against modern Python 3 APIs without regeneration or compatibility shims. Binary auth-token blobs may contain NUL bytes, so all call sites must preserve explicit lengths. Sensitive passphrases and token data traverse Python immutable string objects and generated C temporaries without reliable wiping. Error reporting is mostly type-conversion errors plus integer libecryptfs return codes, so Python callers need to interpret negative errno-style values themselves.

## Test signals
Useful tests would import the extension under its target Python version, call `ecryptfs_passphrase_blob` with a known salt/passphrase, extract the signature with `ecryptfs_passphrase_sig_from_blob`, and compare it to libecryptfs C output. Integration tests require a Linux keyring-capable environment to verify `ecryptfs_add_blob_to_keyring`; Python 3 build failure is an expected compatibility signal unless the wrapper is regenerated.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs-swig/libecryptfs_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/Makefile.am

## Purpose
Automake definition for building the shared `libecryptfs.la` library and installing its pkg-config metadata. It lists the C implementation units that form the library and wires crypto/keyutils compiler and linker flags into the build.

## Important APIs, types, and functions
- `lib_LTLIBRARIES = libecryptfs.la` declares the installed libtool library.
- `pkgconfig_DATA = libecryptfs.pc` installs the pkg-config file generated from `libecryptfs.pc.in`.
- `libecryptfs_la_SOURCES` pulls in mount helpers, messaging, key management, decision graph parsing, module manager, stat parser, and the built-in passphrase key module from `src/key_mod`.
- `libecryptfs_la_LDFLAGS` carries libtool version-info and `-no-undefined`.
- `libecryptfs_la_CFLAGS` and `libecryptfs_la_LIBADD` apply `CRYPTO_*` and `KEYUTILS_*` configure results.

## Control flow
There is no runtime control flow. Build flow is source compilation into one libtool library, link with crypto and keyutils dependencies, and optional `splint` static analysis over local C files.

## State and persistence behavior
No application state is handled. The file controls installed artifacts: the shared library and pkg-config metadata.

## Dependencies and integration points
Connects the source files in this subset into the installed library consumed by mount helpers, PAM integration, SWIG bindings, and other eCryptfs utilities. The built-in passphrase module is compiled directly into the library, while dynamic key modules are discovered at runtime by `key_mod.c`.

## Risks and edge cases
Adding a source file without updating this list can silently omit functionality from the library. The direct reference to the passphrase key module couples libecryptfs to source layout under `src/key_mod`. ABI versioning depends on configured `LIBECRYPTFS_LT_*` values being updated when public symbols or struct contracts change.

## Test signals
Build-system validation should run autoreconf/configure plus `make` and confirm `libecryptfs.la` links with no undefined symbols. `pkg-config --libs --cflags libecryptfs` after installation should expose keyutils and include flags as expected.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/cmd_ln_parser.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/cmd_ln_parser.c

## Purpose
Parses eCryptfs mount options and `~/.ecryptfsrc`-style option files into linked lists of `struct ecryptfs_name_val_pair`. It also merges option lists so command-line options can override rc-file defaults while allowing selected duplicate keys.

## Important APIs, types, and functions
- `ecryptfs_parse_options(opts, head)` and `generate_nv_list` tokenize comma and newline separated option strings.
- `process_comma_tok` parses `name=value` pairs and special `key=module:param=value:...` colon sublists.
- `parse_options_file(fd, head)` reads regular files or FIFOs up to bounded sizes and feeds the parser.
- `ecryptfs_parse_rc_file` resolves the current user's home directory and parses `~/.ecryptfsrc`.
- `ecryptfs_nvp_list_union(dst, src, allowed_duplicates)` updates matching destination values or appends source pairs, preserving duplicates for configured option names such as repeated keys.
- `free_name_val_pairs` is implemented in `decision_graph.c` and is the expected cleanup helper for produced lists.

## Control flow
Parsing scans a buffer into tokens on comma or newline boundaries. Each token is rejected if empty, too long, or malformed with a leading `=` or `:`. Normal tokens become one linked-list node. Key-module tokens with colon-delimited suboptions recursively create module and parameter nodes. File parsing uses `fstat`, rejects directories and oversized files, reads into a growable buffer for FIFOs or changing input, then invokes the same tokenizer.

## State and persistence behavior
The parser builds heap-allocated linked-list state only; it does not persist data. It reads user configuration from the passwd database and `~/.ecryptfsrc`. Merge operations mutate destination lists in place and may allocate child nodes for parameter trees.

## Dependencies and integration points
Feeds `decision_graph.c` and `module_mgr.c`, where name/value pairs drive noninteractive mount-option selection. It depends on `struct ecryptfs_name_val_pair` and flags from `ecryptfs.h`, and on syslog for diagnostics.

## Risks and edge cases
`MAX_TOK_LEN` constrains individual options to 128 bytes, which can reject long paths or module parameters. Some allocation paths call `memset` immediately after `malloc` before checking the pointer. The colon-list parser is specialized to `key=` and can be fragile for values that legitimately contain commas or colons. Merge logic is acknowledged in comments as a hack around a weak list/tree representation, so duplicate and child handling need careful regression coverage.

## Test signals
High-value tests should cover plain `name=value`, value-less options, repeated `key=` options, colon suboptions, rc-file plus CLI override precedence, allowed duplicate behavior, malformed leading separators, token length boundaries, directory rejection, FIFO reads, and oversized option files.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/cmd_ln_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/decision_graph.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/decision_graph.c

## Purpose
Generic decision-graph engine used by libecryptfs to turn parsed mount/key-module options into a stack of kernel mount parameters. It can consume pre-supplied name/value pairs, prompt through callbacks, follow transition nodes, and dynamically build linear subgraphs for key modules.

## Important APIs, types, and functions
- Stack helpers `stack_push`, `stack_pop`, and `stack_pop_val` manage `struct val_node` lists containing generated mount options.
- `do_transition` compares a `param_node` value and pending `nvp` entries against transition nodes and invokes transition callbacks.
- `alloc_and_get_val` retrieves node values from options, defaults, implicit successor nodes, or `ctx->get_string` prompts.
- `ecryptfs_eval_decision_graph` and `eval_param_tree` drive repeated value retrieval and transitions from a root node.
- `ecryptfs_set_exit_param_on_graph`, dump helpers, and insertion helpers manage graph topology.
- `ecryptfs_build_linear_subgraph` creates a prompt/transition chain from a key module's parameter metadata and ends by adding the resulting key to the keyring.

## Control flow
Evaluation starts with verbosity detection from the `verbosity` option. For each node, the engine resolves a value, then `do_transition` checks explicit value matches, option-list matches, and finally the `default` transition. Transition callbacks can push mount options, add keys, mutate next-node pointers, or signal `WRONG_VALUE`/`MOUNT_ERROR`. Linear key-module subgraphs enter with a selected module alias, collect parameter values in order, convert them into `key_mod->param_vals`, call `ecryptfs_add_key_module_key_to_keyring`, and push `ecryptfs_sig=<sig>`.

## State and persistence behavior
The engine mutates `param_node->val`, `nvp` processed flags, transition `next_token` pointers, and the mount-parameter stack. It allocates prompt strings, parameter arrays, and transition nodes. Persistent external state appears only through callbacks, especially keyring insertion from generated key-module subgraphs.

## Dependencies and integration points
Used by `module_mgr.c` to implement mount and key-generation flows. It depends on `decision_graph.h`, `ecryptfs.h`, key-module lookup, and keyring insertion in `key_management.c`. Prompt behavior is supplied by `struct ecryptfs_ctx`.

## Risks and edge cases
Some graph mutations are global static-node mutations, so repeated evaluations must reset enough state to avoid stale transitions or suggested values. `set_exit_param_node_for_arr` uses `sizeof` on a function parameter array, which cannot compute the real array length. `do_transition` keeps static repeat tracking and can be surprising across independent evaluations. Memory ownership is mixed: `stack_pop` frees `val`, but some pushed values are string literals in module manager callbacks. Input prompting and verification paths have retry limits but depend on caller-provided callbacks for security properties.

## Test signals
Tests should construct small synthetic graphs for default transitions, explicit transitions, wrong values, implicit transitions, and prompt callbacks. Integration tests should process mount options with one and multiple keys, confirm generated mount option stack contents, and verify no stale graph state leaks between repeated invocations.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/decision_graph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/ecryptfs-stat.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/ecryptfs-stat.c

## Purpose
Parses the fixed front matter of an eCryptfs file header into a user-space crypt-stat structure. It extracts original file size, validates the eCryptfs marker, maps on-disk flags to local flags, records file version, and parses header extent metadata.

## Important APIs, types, and functions
- `ecryptfs_parse_stat(crypt_stat, buf, buf_size)` is the public parser.
- `swab64` and `host_is_big_endian` normalize on-disk integer endianness.
- `ecryptfs_contains_ecryptfs_marker` validates the marker pair using `MAGIC_ECRYPTFS_MARKER`.
- `ecryptfs_process_flags` maps on-disk flags to `ECRYPTFS_ENABLE_HMAC`, `ECRYPTFS_ENCRYPTED`, and `ECRYPTFS_METADATA_IN_XATTR`.
- `ecryptfs_parse_header_metadata` reads extent size and extent count and optionally validates minimum header size.

## Control flow
`ecryptfs_parse_stat` first checks that enough bytes are available for the size, marker, and flags. It zeroes the output structure, reads and byte-swaps the file size as needed, validates the marker, processes flags, then parses header extent metadata with validation enabled. Packet-set parsing is explicitly left commented out.

## State and persistence behavior
The function only fills the caller-provided `struct ecryptfs_crypt_stat_user`; it does not allocate or persist state. It reads from a caller-supplied header buffer and prints diagnostics on malformed input.

## Dependencies and integration points
Depends on constants and output structure definitions in `ecryptfs.h`. It is a library-side companion for utilities that inspect encrypted file headers without mounting them.

## Risks and edge cases
The parser trusts the caller's buffer after the initial minimum check and does not verify all subsequent field availability against `buf_size`. Endianness handling is manual and should be treated carefully on uncommon architectures. Unknown on-disk flags are ignored rather than rejected. Diagnostics go to stdout via `printf`, not syslog or an error object, which can complicate library embedding.

## Test signals
Tests should feed known-good headers for little- and big-endian interpretations, bad marker pairs, too-short buffers, invalid header extents below `ECRYPTFS_MINIMUM_HEADER_EXTENT_SIZE`, and combinations of HMAC/encrypted/xattr flags.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/ecryptfs-stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/key_management.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/key_management.c

## Purpose
Implements passphrase and key-module authentication-token lifecycle operations: generating auth-token payloads, adding/removing keys in the Linux user keyring, wrapping and unwrapping passphrase files, reading salt/signature caches, terminal passphrase prompting, and locating the default wrapped-passphrase file.

## Important APIs, types, and functions
- `ecryptfs_generate_passphrase_auth_tok` combines `generate_passphrase_sig` and `generate_payload` to allocate a password auth token.
- `ecryptfs_add_auth_tok_to_keyring`, `ecryptfs_add_blob_to_keyring`, `ecryptfs_add_passphrase_key_to_keyring`, and `ecryptfs_remove_auth_tok_from_keyring` integrate with keyutils.
- `ecryptfs_wrap_passphrase`, `ecryptfs_wrap_passphrase_file`, and `ecryptfs_unwrap_passphrase` encrypt/decrypt wrapped-passphrase files with NSS AES-ECB using a wrapping key derived from salt/passphrase.
- `ecryptfs_insert_wrapped_passphrase_into_keyring` unwraps a file then inserts both FNEK and normal passphrase keys.
- `ecryptfs_add_key_module_key_to_keyring` builds private-key auth-token payloads from key modules.
- `ecryptfs_read_salt_hex_from_rc`, `ecryptfs_check_sig`, and `ecryptfs_append_sig` handle user config and signature cache files.
- `ecryptfs_get_passphrase` disables terminal echo while reading a passphrase.

## Control flow
Passphrase insertion derives a FEKEK/signature, fills an auth token, searches the user keyring for an existing key, and adds it if absent. Wrapping validates passphrase length, derives a wrapping key, pads to AES block size, encrypts with NSS, writes signature plus ciphertext to a newly created `0600` file, and removes the plaintext source in the file wrapper path. Unwrapping derives the same signature, verifies the file prefix, decrypts the remainder, and leaves the plaintext in the caller buffer. Key-module insertion queries blob size, allocates an auth token with appended blob storage, generates payload/signature, and adds it to the keyring.

## State and persistence behavior
Mutates the Linux user keyring and signature cache files. Wrapped-passphrase operations create, unlink, or replace files in the user's eCryptfs directory. Sensitive buffers are sometimes zeroed before free, but many stack buffers, NSS temporaries, Python-facing blobs, and passphrase strings are not comprehensively wiped.

## Dependencies and integration points
Depends on NSS/PKCS#11 (`NSS_NoDB_Init`, `PK11_*`), keyutils (`add_key`, `keyctl_*`), passwd database, termios, rc-file parsing, and core payload helpers in `main.c`. It is used by mount helpers, PAM support, SWIG bindings, decision-graph key-module subgraphs, and miscdev packet processing.

## Risks and edge cases
AES-ECB for passphrase wrapping is legacy and exposes structure for repeated blocks. Some error paths call `close(fd)` after failed `open`, use positive `errno` conventions inconsistently, or leave allocated data uncleared. `ecryptfs_insert_wrapped_passphrase_into_keyring` writes into the same `auth_tok_sig` buffer for two salts, so callers must know the final signature semantics. `ecryptfs_get_wrapped_passphrase_filename` returns `NULL` if `stat` fails instead of returning the default path for creation.

## Test signals
Integration tests require keyutils and NSS availability. Useful coverage includes deterministic signature generation, keyring add/search/remove idempotence, wrap/unwrap round trips, wrong wrapping passphrase rejection, rc-file salt parsing, signature cache append/check behavior, passphrase length enforcement, and keyring quota failure handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/key_management.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/key_mod.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/key_mod.c

## Purpose
Discovers, registers, and frees eCryptfs key modules. It provides fallback dummy operations for optional module methods, includes the built-in passphrase module, and supports dynamically loaded `.so` modules from the configured key-module directory.

## Important APIs, types, and functions
- `builtin_get_key_mod_ops` currently registers `passphrase_get_key_mod_ops`.
- `ecryptfs_fill_in_dummy_ops` supplies no-op or warning implementations for missing `struct ecryptfs_key_mod_ops` callbacks.
- `ecryptfs_register_key_modules(ctx)` loads dynamic modules with `dlopen`/`dlsym("get_key_mod_ops")`, initializes aliases, then appends built-in modules not shadowed by dynamic modules.
- `ecryptfs_find_key_mod(key_mod, ctx, alias)` searches the registered list.
- `ecryptfs_free_key_mod_list(ctx)` finalizes modules, closes dynamic handles, and frees module records.
- `ecryptfs_generate_sig_from_key_data` is a placeholder for deriving signatures from typed key data; it currently rejects all key types.

## Control flow
Registration opens `ECRYPTFS_DEFAULT_KEY_MOD_DIR`, scans for filenames ending in `.so`, loads each library lazily, resolves its ops factory, fills missing callbacks, calls `init` for the alias, and appends it to `ctx->key_mod_list_head`. It then iterates built-in factories and skips a built-in if a dynamic module with the same alias already exists. Lookup is a linear alias prefix comparison.

## State and persistence behavior
Maintains an in-memory linked list hanging off `struct ecryptfs_ctx`. Dynamic library handles stay open until `ecryptfs_free_key_mod_list`. No persistent files are written; discovery reads the key-module directory.

## Dependencies and integration points
Used by `module_mgr.c` to build key selection graphs, by `packets.c` to locate modules for encrypt/decrypt requests, and by `key_management.c` to generate key-module auth-token payloads. Depends on libdl, directory iteration, and key-module ABI contracts in `ecryptfs.h`.

## Risks and edge cases
Failure to open the dynamic module directory returns `-EPERM`, which can block even built-in module registration. `ecryptfs_find_key_mod` uses `strncmp` with the registered alias length, so prefix matches can accidentally select a module. `ecryptfs_free_key_mod_list` calls `dlclose` even for built-ins with a null handle. Dummy cryptographic operations can mask incomplete modules until runtime behavior fails.

## Test signals
Tests should exercise registration with missing module directory, a fake dynamic module, dynamic-over-built-in alias precedence, missing optional callbacks, lookup prefix collisions, and cleanup of mixed dynamic/built-in lists. Packet and decision-graph integration tests should confirm the passphrase module is always available in normal builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/key_mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/libecryptfs.pc.in -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/libecryptfs.pc.in

## Purpose
Template for the installed `libecryptfs.pc` pkg-config metadata. It lets external programs discover include flags, keyutils flags, library search path, and the package version for libecryptfs.

## Important APIs, types, and functions
- `prefix`, `exec_prefix`, `libdir`, and `includedir` are configure-time substitutions.
- `Name`, `Description`, and `Version` identify the package.
- `Cflags` emits the include directory and `@KEYUTILS_CFLAGS@`.
- `Libs` emits `@KEYUTILS_LIBS@`, `-L${libdir}`, and `-lecryptfs`.

## Control flow
No runtime flow. Configure substitutes variables, installation places the generated file where pkg-config can find it, and downstream builds query it.

## State and persistence behavior
Persists build metadata as an installed text file. It does not represent runtime eCryptfs state.

## Dependencies and integration points
Integrated by `Makefile.am` via `pkgconfig_DATA`. Consumers of libecryptfs use this file instead of hand-coding compiler and linker flags.

## Risks and edge cases
The template exposes keyutils flags but not all crypto/NSS flags visible in the library build; downstream static or unusual link modes may need additional private libs. If include installation layout diverges from `${includedir}`, consumers will compile against missing headers.

## Test signals
After installation, `pkg-config --modversion libecryptfs`, `--cflags`, and `--libs` should return substituted values. A minimal external program including `ecryptfs.h` and linking a libecryptfs symbol is the best end-to-end check.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/libecryptfs.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/main.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/main.c

## Purpose
Core utility routines for libecryptfs: version reporting, hex conversion, NSS hashing, private mount discovery, mount-state checks, passphrase signature and auth-token payload generation, private-key payload generation, and zombie session placeholder tracking with System V IPC.

## Important APIs, types, and functions
- `ecryptfs_get_versions`, `to_hex`, `from_hex`, and `do_hash` provide foundational helpers.
- `ecryptfs_fetch_private_mnt` reads `~/.ecryptfs/Private.mnt` or falls back to `$HOME/Private`.
- `ecryptfs_private_is_mounted` scans `/proc/mounts` for eCryptfs device/mount/signature matches.
- `generate_passphrase_sig` performs salted iterative SHA-512 hashing, yields FEKEK bytes and expanded-hex signature.
- `generate_payload` fills password auth-token fields; `ecryptfs_generate_key_payload` fills private-key auth-token fields from a key module.
- Zombie placeholder functions manage session-id to pid pairs in shared memory guarded by a semaphore.
- `cryptfs_get_ctx_opts` returns a static context-ops structure.

## Control flow
Passphrase signature generation concatenates salt and passphrase, hashes with NSS SHA-512 for `ECRYPTFS_DEFAULT_NUM_HASH_ITERATIONS`, copies the first key bytes as FEKEK, hashes once more, and hex-encodes the signature. Private-key payload generation asks the module for blob and key-data sizes, copies or generates blob data, derives or requests a signature, and fills auth-token metadata. Zombie placeholder setup locks IPC state, appends the current session/pid pair, sleeps, then removes the pair and exits; clear logic finds the pid for the current session, kills it, and removes the entry.

## State and persistence behavior
Reads `/proc/mounts`, user mount config files, and System V shared memory/semaphores keyed by eCryptfs constants. Auth-token helpers mutate caller-provided memory only. Zombie helpers create shared IPC objects and can send `SIGKILL` to tracked processes.

## Dependencies and integration points
Used by `key_management.c`, mount helpers, PAM workflows, and private directory helpers. Depends on NSS hashing, Linux mount table APIs, key-module callbacks, signals, and System V IPC.

## Risks and edge cases
The passphrase KDF is a fixed legacy iterative SHA-512 scheme, not a modern memory-hard KDF. Several mount-path helpers allocate strings with ownership handed to callers but can leak on early errors. `ecryptfs_private_is_mounted` deliberately uses broad matching when mounting and strict matching when unmounting, so callers must pass correct `mounting` intent. Zombie shared-memory code assumes `sizeof(pid_t) == sizeof(uint32_t)` and contains manual byte-order and buffer-shift logic that is easy to break.

## Test signals
Tests should compare known passphrase/salt signature vectors, verify auth-token field layout, mock mount table entries for mount/unmount matching, exercise private mount fallback behavior, and run IPC placeholder add/find/remove operations in an isolated namespace or with cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/messaging.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/messaging.c

## Purpose
Provides shared packet-length encoding/decoding and a small abstraction over eCryptfs kernel messaging backends. The only active backend is the misc device interface; netlink is explicitly unsupported.

## Important APIs, types, and functions
- `ecryptfs_write_packet_length(dest, size, packet_size_length)` encodes OpenPGP-style one- or two-byte packet lengths for sizes below 65536.
- `ecryptfs_parse_packet_length(data, size, length_size)` decodes one- and two-byte lengths and rejects five-byte or invalid encodings.
- `ecryptfs_init_messaging(mctx, type)` initializes a messaging context for `ECRYPTFS_MESSAGING_TYPE_MISCDEV`.
- `ecryptfs_messaging_exit` releases backend resources.
- `ecryptfs_send_message` and `ecryptfs_run_daemon` dispatch to miscdev functions.

## Control flow
Length encoding selects one byte for sizes below 192, two bytes for sizes below 65536, and rejects larger sizes. Messaging initialization switches on requested type and delegates miscdev setup. Send and daemon operations switch on the stored context type and call `miscdev.c`.

## State and persistence behavior
Stores backend type and file descriptor state inside `struct ecryptfs_messaging_ctx`. It does not persist data; actual kernel communication and descriptor lifecycle are delegated to miscdev helpers.

## Dependencies and integration points
Used by `packets.c` and `miscdev.c` for message framing. It depends on shared message constants and structs from `ecryptfs.h`.

## Risks and edge cases
The packet length implementation does not support five-byte lengths, so larger payloads fail. `ecryptfs_parse_packet_length` assumes enough input bytes are available for the indicated encoding; callers must bounds-check the containing buffer. The abstraction still exposes netlink constants even though the path is unsupported, so callers must handle `-EINVAL`.

## Test signals
Unit tests should cover boundary sizes 0, 191, 192, 65535, and 65536; reject first-byte 255 and invalid encodings; and verify miscdev initialization/send/run dispatch returns `-EINVAL` for unsupported types.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/messaging.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/miscdev.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/miscdev.c

## Purpose
Implements the userspace daemon side of the `/dev/ecryptfs` misc-device protocol. It frames messages to/from the kernel, initializes the device handle, runs a request loop, parses key packets, and sends responses.

## Important APIs, types, and functions
- `ecryptfs_send_miscdev` writes type, sequence, optional length, and `struct ecryptfs_message` bytes to the misc-device fd.
- `ecryptfs_recv_miscdev` reads a bounded message, validates framing, returns message type, sequence, and allocated message payload.
- `ecryptfs_init_miscdev` opens `/dev/ecryptfs` or `/dev/misc/ecryptfs`.
- `ecryptfs_release_miscdev` closes the fd.
- `ecryptfs_run_miscdev_daemon` registers key modules and loops over HELO, QUIT, and REQUEST messages.

## Control flow
Sending computes the embedded message size, length-encodes it when present, prepends message type and network-order sequence, and writes one buffer. Receiving reads up to `ECRYPTFS_MSG_MAX_SIZE`, checks minimum type/sequence length, decodes the embedded packet length for request messages, validates that the computed frame size equals bytes read, and copies the payload. The daemon loop tolerates receive errors up to a threshold, ignores HELO, exits on QUIT, and for REQUEST calls `parse_packet`, copies the request index into the reply, and sends an `ECRYPTFS_MSG_RESPONSE`.

## State and persistence behavior
Holds an open misc-device fd and a runtime key-module list in a local `struct ecryptfs_ctx`. It does not write files, but it reads from and writes to the kernel device and may cause key-module cryptographic operations through packet parsing.

## Dependencies and integration points
Depends on `messaging.c` for length encoding, `packets.c` for request interpretation, and `key_mod.c` for module registration/freeing. It is the active backend selected by `messaging.c`.

## Risks and edge cases
`ecryptfs_recv_miscdev` allocates `packet_len` bytes even when packet length is zero for non-request messages, so caller behavior around null/zero allocations matters. The send path does not verify partial writes. The daemon is an infinite loop until QUIT or fatal error and has no signal/shutdown abstraction here. Error logging includes a typo ("miscdevess") and sometimes logs `errno` after functions that already returned logical errors.

## Test signals
Tests can use a pipe or fake fd to validate exact frame bytes, partial or malformed receive frames, sequence byte order, request length validation, HELO/QUIT handling, and REQUEST flow with a stubbed or controlled keyring/key-module environment.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/miscdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/module_mgr.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/module_mgr.c

## Purpose
Builds and processes the eCryptfs mount-option decision graph. It connects key-module selection, existing signatures, cipher/key-size selection, kernel-version-gated features, filename encryption, and repeated key handling into the generic graph engine.

## Important APIs, types, and functions
- Static `param_node` definitions model options such as `sig`, `key`, `ecryptfs_cipher`, `ecryptfs_key_bytes`, passthrough, HMAC, xattr metadata, encrypted view, and FNEK signature.
- Transition callbacks push mount options (`ecryptfs_sig=`, `ecryptfs_cipher=`, `ecryptfs_key_bytes=`, `ecryptfs_hmac`, etc.) or mutate graph edges.
- `init_ecryptfs_cipher_param_node` and `init_ecryptfs_key_bytes_param_node` populate selectable cipher and key-byte transitions.
- `fill_in_decision_graph_based_on_version_support` appends feature nodes based on sysfs version flags.
- `ecryptfs_process_decision_graph` is the main mount option processor.
- `ecryptfs_process_key_gen_decision_graph` drives key-generation subgraphs.

## Control flow
Mount processing registers key modules, allows duplicate `key` options, asks each module for a parameter subgraph or builds a linear one, and attaches those transitions to the key selector. It fills the rest of the graph when all mount options are requested, otherwise routes key-module-only processing to a dummy exit. It parses rc-file and option-string name/value pairs, merges them with CLI precedence and allowed duplicates, stores the merged list in `ctx`, then evaluates from `root_param_node`. Existing `sig=` skips key selection; absent or `NULL` signatures route into key-module selection. The `another_key` node loops back to key selection when unprocessed key options remain, enabling multiple keys.

## State and persistence behavior
Mutates static graph nodes, suggested values, transition counts, and transition next pointers. It allocates allowed-duplicate list entries and graph transition strings. External persistent effects come from key-module subgraphs adding keys to the kernel keyring and from reading `~/.ecryptfsrc`.

## Dependencies and integration points
Integrates option parsing, key-module registration, decision graph evaluation, sysfs feature checks, and keyring insertion. It is called by mount helper flows and depends on `ecryptfs_supports_*` functions from `sysfs.c`.

## Risks and edge cases
Static nodes make repeated calls vulnerable to stale transition counts, suggested values, and next-token mutations. `init_ecryptfs_cipher_param_node` and key-byte initialization append without obvious reset. `tf_ecryptfs_cipher` removes min/max key-byte pseudo-options while iterating a stack and mixes ownership of list values. Feature graph shape depends on kernel version flags, so old kernels skip prompts/options silently. Boolean parsing accepts only lowercase `y/yes/n/no`.

## Test signals
Integration tests should process option strings for existing signature mounts, passphrase key-module mounts, multiple keys, cipher/key-byte min/max constraints, filename encryption suggested FNEK signature, and version masks with and without passthrough/HMAC/xattr/FNEK support. Repeated invocations in one process are especially important.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/module_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/packets.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/packets.c

## Purpose
Parses kernel request packets asking userspace key modules to decrypt or encrypt session keys, then builds tag 65 or tag 67 response packets. It is the cryptographic request handler used by the miscdev daemon.

## Important APIs, types, and functions
- `parse_packet(ctx, emsg, reply)` is the public packet dispatcher.
- `key_mod_decrypt` and `key_mod_encrypt` locate the auth token's key module and perform two-pass size-query then output-buffer operations.
- `write_failure_packet` emits a bad-status response for a target tag.
- `write_tag_65_packet` emits a successful decrypted-key response.
- `write_tag_67_packet` emits a successful encrypted-key response.

## Control flow
`parse_packet` reads packet type, signature length and signature, key length and key bytes from `emsg->data`. It looks up the signature in the user keyring, reads the auth token, and switches on packet type. Tag 64 requests decrypt an encrypted key and return tag 65. Tag 66 requests encrypt a plaintext key and return tag 67. Any parse, lookup, module, or unknown-type failure writes a failure packet, choosing tag 67 for failed tag 66 requests and tag 65 otherwise.

## State and persistence behavior
Reads the Linux user keyring via `request_key` and `keyctl_read_alloc`. It allocates reply messages and temporary key/signature buffers, and wipes auth-token memory before free. It does not add or remove keys.

## Dependencies and integration points
Depends on keyutils, `messaging.c` packet-length helpers, `key_mod.c` lookup, and module `encrypt`/`decrypt` callbacks. Called by `ecryptfs_run_miscdev_daemon` in `miscdev.c`.

## Risks and edge cases
The parser assumes packet fields are present and does not track the outer message `data_len` while advancing offsets, so malformed short packets can lead to out-of-bounds reads. Failure handling can overwrite the original error code with the status-packet write result. `write_tag_67_packet` sets `data_len` to allocated `data_len` rather than the actual index `i`, which currently matches only if length encoding assumptions hold. Key-module callbacks receive raw blob data from auth tokens and must enforce their own cryptographic validity.

## Test signals
Tests should cover valid tag 64 and tag 66 flows with a stub key module, missing key signatures, malformed packet lengths, too-large encrypted/decrypted output sizes, unknown packet types, failure packet tag selection, and response `data_len` correctness.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/packets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/sysfs.c -->
# sources/security-integrity/ecryptfs-utils/src/libecryptfs/sysfs.c

## Purpose
Reads the eCryptfs kernel module feature/version mask from sysfs and exposes helpers that test individual feature bits. This lets userspace tailor mount prompts and options to kernel support.

## Important APIs, types, and functions
- `get_sysfs_mountpoint(mnt, mnt_size)` scans `/etc/mtab` for a `sysfs` mount and falls back to `/sys`.
- `ecryptfs_get_version(version)` reads `<sysfs>/fs/ecryptfs/version`, attempting `/sbin/modprobe ecryptfs` if the file is missing.
- `ecryptfs_version_str_map` maps feature bits to human-readable labels.
- `ecryptfs_supports_passphrase`, `ecryptfs_supports_pubkey`, `ecryptfs_supports_plaintext_passthrough`, `ecryptfs_supports_hmac`, `ecryptfs_supports_filename_encryption`, `ecryptfs_supports_policy`, and `ecryptfs_supports_xattr` return bit-test results.

## Control flow
Version loading first discovers the sysfs mountpoint size, allocates a buffer, reads the mountpoint, builds the eCryptfs version path, opens it, optionally modprobes and retries, reads up to 16 bytes, and parses it with `atoi`. Feature helpers are direct bit masks over the returned integer.

## State and persistence behavior
Reads `/etc/mtab` and sysfs. It may trigger module loading through `/sbin/modprobe ecryptfs`, which changes kernel module state. No user files are written.

## Dependencies and integration points
`module_mgr.c` uses the feature helpers to decide which mount-option nodes to include. Mount helpers use `ecryptfs_get_version` before graph processing.

## Risks and edge cases
Using `/etc/mtab` can be less reliable than `/proc/mounts` on systems where it is stale or absent. `atoi` does not validate trailing garbage or overflow. A failed version read collapses to `-EINVAL`, losing precise errno. The hard-coded modprobe path may fail on distributions where `modprobe` lives elsewhere or when callers lack privileges.

## Test signals
Tests can mock mount-table/sysfs paths only with indirection or filesystem namespace setup. Useful checks include fallback to `/sys`, missing version file with failed modprobe, malformed version contents, and each feature helper against known bit masks.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/libecryptfs/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/Makefile.am -->
# sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/Makefile.am

## Purpose
Automake definition for building and installing the `pam_ecryptfs` PAM module when PAM support is enabled. It links the module against the in-tree libecryptfs and PAM libraries.

## Important APIs, types, and functions
- `if BUILD_PAM` gates `pam_LTLIBRARIES = pam_ecryptfs.la`.
- `install-data-hook` removes installed `.la` and `.a` libtool archive artifacts from the PAM module directory.
- `uninstall-local` removes `pam_ecryptfs.so`.
- `pam_ecryptfs_la_SOURCES = pam_ecryptfs.c` identifies the module implementation.
- `pam_ecryptfs_la_LIBADD` links `src/libecryptfs/libecryptfs.la` and `$(PAM_LIBS)`.
- `pam_ecryptfs_la_LDFLAGS` builds a shared, module-style, avoid-version library.

## Control flow
No runtime control flow. Build flow is conditional on configure's `BUILD_PAM`; installation uses a hook to leave only the PAM shared object where PAM expects loadable modules.

## State and persistence behavior
Controls installed PAM module artifacts under `$(pamdir)`. It does not manage user keyrings or encrypted home state directly; that happens in `pam_ecryptfs.c` and libecryptfs at runtime.

## Dependencies and integration points
Bridges the PAM module with libecryptfs key-management and mount helper functionality. Depends on configure-provided `pamdir`, `PAM_LIBS`, and the built libecryptfs target.

## Risks and edge cases
Incorrect `pamdir` or disabled `BUILD_PAM` means no PAM integration is installed. The install hook assumes libtool archive names and removes them with `rm -f`; packaging scripts should still verify final artifacts. Because it links the in-tree libecryptfs, ABI or symbol changes in the library directly affect PAM authentication/session behavior.

## Test signals
Build tests should configure with and without PAM support, confirm `pam_ecryptfs.so` is produced only when expected, and verify `.la`/`.a` artifacts are removed from the staged PAM directory. Runtime tests belong to the PAM module implementation and should exercise login/session key insertion and unmount flows.
<!-- END_FILE_RESEARCH: sources/security-integrity/ecryptfs-utils/src/pam_ecryptfs/Makefile.am -->
