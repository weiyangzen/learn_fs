# Group Research: group_1323_nvme_cli_sources_virtualization_nvme_cli_libnvme_src_nvme_accessors_eb8da80b59ba

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors-fabrics.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors-fabrics.h

Auto-generated public declarations for NVMe-oF accessor functions over opaque internal structs: `libnvmf_context`, `libnvmf_discovery_args`, and `libnvmf_uri`.

Main API surface:
- `libnvmf_context_get_*` exposes borrowed strings for transport, target address, host address/interface, service ID, subsystem NQN, host identity, DH-CHAP/TLS/keyring strings, and device.
- `libnvmf_context_set/get_*` covers fabrics connection tunables: queue counts, queue size, reconnect policy, timeout policy, `tos`, key IDs, TLS booleans, digest booleans, duplicate connect, SQ flow disable, persistent, and defaults.
- `libnvmf_discovery_args_new/free/init_defaults` manages the opaque discovery argument object, with setters/getters for `max_retries` and log specific parameter `lsp`.
- `libnvmf_uri_set/get_*` exposes URI fields: scheme, protocol, userinfo, host, port, path segments, query, and fragment.

Dependencies and integration:
- Includes `<nvme/types.h>` and `<nvme/nvme-types.h>` for libnvme/NVMe scalar types such as `__u8`.
- The implementation is in the corresponding generated fabrics accessor source, not in this file.
- Used by higher-level discovery/connect code to keep the actual fabrics structs opaque to API consumers.

Ownership contract:
- Getter return values are borrowed and must not be freed by callers.
- URI string setters document copy-on-set semantics.
- `path_segments` is declared as a deep-copied NULL-terminated string array.

Risks and notes:
- This is generated code; manual edits are likely to be overwritten by `update-accessors`.
- The header intentionally exposes no validation policy. Callers can set invalid combinations; validation is performed later by fabrics connect/discovery code.
- ABI stability depends on keeping these declarations synchronized with generated implementations and the hidden internal struct fields.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors-fabrics.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors.c

Generated implementation for public accessors over libnvme topology and fabrics option structs.

Main behavior:
- Exports functions with `__libnvme_public`.
- Implements setters/getters for `libnvme_path`, `libnvme_ns`, `libnvme_ctrl`, `libnvme_subsystem`, `libnvme_host`, and `libnvme_fabric_options`.
- String setters free the old field and assign `strdup(new_value)` or `NULL`.
- Primitive setters assign directly.
- Getters return primitive values, borrowed string pointers, or borrowed array pointers.

Key object coverage:
- `libnvme_path`: name, sysfs directory, group ID.
- `libnvme_ns`: NSID, names, sysfs directory, LBA geometry/utilization, EUI64, NGUID, CSI.
- `libnvme_ctrl`: identity/sysfs strings, fabrics address fields, DH-CHAP keys, keyring/TLS fields, discovery state flags, persistence, and embedded `cfg` connection parameters.
- `libnvme_subsystem`: name/sysfs/NQN/model/serial/firmware/subsystem type and application ownership string.
- `libnvme_host`: host NQN/ID, DH-CHAP host key, symbolic host name.
- `libnvme_fabric_options`: booleans indicating which kernel fabrics options are supported.

Dependencies and integration:
- Includes `accessors.h`, `private.h`, and `compiler-attributes.h`.
- Reads and writes fields of private libnvme structs, providing controlled public access while keeping struct definitions opaque.
- Used broadly by tree, fabrics, JSON config, and discovery code.

Ownership and lifetime:
- Returned strings are internal borrowed pointers.
- Setters that use `strdup` do not report allocation failure; on allocation failure after freeing the previous value, the stored field becomes `NULL`.
- No NULL-object checks are performed; callers must pass valid object pointers.

Risks and tests:
- Since this is generated code, tests should focus on generator correctness and representative accessor behavior rather than hand-editing individual functions.
- Important cases: setter clears on NULL, string setters replace old values without leaks, and fabric option flags match `/dev/nvme-fabrics` option parsing.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors.h

Generated public declaration header for libnvme topology and fabrics option accessors.

Main API surface:
- Forward-declares opaque structs: `libnvme_path`, `libnvme_ns`, `libnvme_ctrl`, `libnvme_subsystem`, `libnvme_host`, and `libnvme_fabric_options`.
- Declares path accessors for device/sysfs names and group ID.
- Declares namespace accessors for NSID, names, sysfs directory, LBA sizes/counts, EUI64, NGUID, and command set identifier.
- Declares controller accessors for sysfs/identity fields, address/transport fields, DH-CHAP/TLS/keyring fields, discovery flags, persistence, and connection config fields.
- Declares subsystem and host accessors for static identity plus mutable application/crypto/symbolic fields.
- Declares per-option booleans in `libnvme_fabric_options`.

Dependencies and integration:
- Includes standard bool/int headers and `<nvme/types.h>`, `<nvme/nvme-types.h>`.
- Matched by generated implementations in `accessors.c`.
- Allows external callers to inspect libnvme tree objects without depending on private struct layouts.

Ownership contract:
- Documentation distinguishes copied string setters from borrowed-pointer getters.
- EUI64 and NGUID getters return pointers to fixed internal arrays.
- Fabric option setters/getters are simple boolean controls.

Risks and notes:
- The generated API has no runtime validation or allocation-error reporting in the setter signatures.
- Callers must treat returned pointers as valid only while the owning libnvme object is alive and unchanged.
- Any new private field that should be public must be added through the accessor generator, not by manually editing this file.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/accessors.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/base64.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/base64.c

Small RFC4648-style Base64 encoder/decoder used by NVMe TLS key import/export.

Functions:
- `base64_encode(src, srclen, dst)`: emits Base64 characters and `=` padding, returns encoded byte count, and does not NUL-terminate.
- `base64_decode(src, srclen, dst)`: decodes Base64 input, returns decoded byte count, `-EINVAL` for invalid characters, and `-EAGAIN` for trailing non-zero leftover bits.

Dependencies:
- Uses `strchr` against a static Base64 alphabet.
- Error codes come from `<errno.h>`.

Important behavior:
- Caller must provide sufficiently large output buffers.
- Decoder accepts `=` padding by shifting zero bits into the accumulator.
- Embedded NUL in input is rejected because `!src[i]` triggers `-EINVAL`.

Risks and tests:
- No output capacity argument exists; all safety depends on callers sizing buffers correctly.
- Header comment says the alphabet is `[A-Za-z0-9+,]`, but the implementation uses standard `+/`.
- Test vectors should include empty input, 1/2/3-byte inputs, padding, invalid characters, embedded NUL, and malformed leftover bits.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/base64.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/base64.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/base64.h

Tiny internal declaration header for Base64 helpers.

Exports:
- `int base64_encode(const unsigned char *src, int len, char *dst);`
- `int base64_decode(const char *src, int len, unsigned char *dst);`

Integration:
- Used by `crypto.c` for PSK digest and TLS key interchange encoding.
- No public libnvme visibility macro is applied, so this is an internal utility API.

Contract:
- Buffer sizing and NUL termination are caller responsibilities.
- Return values are byte counts or negative errno-style errors for decode.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/base64.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/cleanup-linux.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/cleanup-linux.h

Linux-specific cleanup helpers built on GCC/Clang `__attribute__((cleanup))`.

Exports/macros:
- `__cleanup_file`: closes `FILE *` with `fclose`.
- `__cleanup_dir`: closes `DIR *` with `closedir`.
- `__cleanup_fd`: closes an `int` file descriptor when it is `>= 0`.

Dependencies:
- Includes `<dirent.h>`, `<stdio.h>`, `<unistd.h>`, and `cleanup.h`.

Integration:
- Used in `crypto.c` and `fabrics.c` to make early returns close files/directories/fds.
- Complements generic pointer cleanup in `cleanup.h`.

Risks:
- Assumes GCC-compatible cleanup attributes.
- `cleanup_fd` requires variables to be initialized to `-1` before use.
- Cleanup functions ignore close errors, which is acceptable for most read/scan paths but not for durability-sensitive write paths.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/cleanup-linux.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/cleanup.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/cleanup.h

Generic cleanup-attribute helper header.

Macros/functions:
- `__cleanup(fn)` wraps `__attribute__((cleanup(fn)))`.
- `DECLARE_CLEANUP_FUNC` and `DEFINE_CLEANUP_FUNC` create typed cleanup wrappers.
- `freep()` backs `__cleanup_free` for normal `free`.
- `libnvme_freep()` backs `__cleanup_libnvme_free` for memory allocated with `libnvme_alloc`.

Dependencies:
- Includes `<stdlib.h>` and `<nvme/mem.h>`.

Integration:
- Used across crypto, fabrics, ioctl, and discovery paths for structured cleanup on error returns.
- Helps keep complex functions from accumulating manual unwind labels.

Risks:
- Compiler-specific feature; portability depends on supported toolchain.
- Ownership transfer must explicitly NULL out cleanup-managed pointers, as seen in code that assigns output pointers after allocation.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/cleanup.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/compiler-attributes.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/compiler-attributes.h

Central header for compiler visibility and annotation attributes.

Macros:
- `__libnvme_public`: marks a symbol with default visibility for shared library ABI export.
- `__libnvme_weak`: declares weak symbols for optional overrides/platform hooks.
- `__libnvme_unused`: suppresses unused warnings for intentionally unused symbols or parameters.

Integration:
- Used by generated accessors, filters, ioctl wrappers, fabrics, and crypto public APIs.
- Supports builds with `-fvisibility=hidden` by making exported symbols explicit.

Risks:
- GCC/Clang attribute syntax is assumed.
- Public ABI depends on consistent use of `__libnvme_public`; omitting it can hide intended API symbols.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/compiler-attributes.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/crc32.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/crc32.c

CRC-32 implementation derived from Gary S. Brown’s public-domain style code and FreeBSD libkern lineage.

Contents:
- `crc32_tab[]`: 256-entry lookup table for polynomial `0xedb88320`.
- `crc32(crc, buf, size)`: inverts the starting CRC, updates over bytes with the table, and returns inverted result.

Integration:
- Used by `crypto.c` to append and verify CRC values in NVMe TLS key interchange strings.

Behavior:
- Supports incremental CRC by accepting an initial CRC.
- `crc32(0, NULL, 0)` is safe because the loop does not dereference the buffer for zero size.
- The function treats input as raw bytes.

Risks and tests:
- Correctness should be verified against standard CRC-32 vectors and the TLS key import/export round trip.
- The global table is not declared `static`, so it is externally visible unless hidden by build visibility settings.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/crc32.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/crc32.h

Internal declaration header for CRC-32.

Exports:
- `uint32_t crc32(uint32_t crc, const void *buf, size_t len);`

Dependencies:
- Includes `<stddef.h>` and `<stdint.h>`.

Integration:
- Included by `crypto.c` for TLS PSK interchange format integrity checks.
- Not marked as a public libnvme API symbol.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/crypto.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/crypto.c

Implements libnvme cryptographic support for DH-HMAC-CHAP, NVMe/TCP TLS PSKs, Linux keyrings, host ID generation, and host NQN/ID configuration file reads.

Major feature gates:
- Without `CONFIG_OPENSSL`, HMAC/TLS derivation functions either pass through `LIBNVME_HMAC_ALG_NONE` secrets or return `-ENOTSUP` with log messages.
- With `CONFIG_OPENSSL`, HMAC and HKDF are implemented using OpenSSL EVP APIs.
- Without `CONFIG_KEYUTILS`, keyring functions return `-ENOTSUP`, while config import returns zero IDs.

OpenSSL-backed crypto:
- `default_hmac()` maps key length 32/48/64 to SHA-256/SHA-384/SHA-512 defaults, though TLS key derivation mostly accepts SHA-256 and SHA-384.
- `select_hmac()` maps libnvme HMAC IDs to OpenSSL digests and digest lengths.
- `libnvme_gen_dhchap_key()` derives DH-HMAC-CHAP keys using HMAC over host NQN and `"NVMe-over-Fabrics"`.
- `derive_retained_key()` and `_compat()` derive retained PSKs from configured PSKs with HKDF.
- `derive_tls_key()` and `_compat()` derive TLS PSKs from retained PSKs and identities.
- `derive_psk_digest()` builds a Base64 HMAC digest for NVMe TLS identity version 1.

TLS key lifecycle:
- `libnvme_create_raw_secret()` accepts generated random secret, `pin:` deterministic secret, or hex secret, enforcing key lengths of 32/48/64 bytes.
- `libnvme_generate_tls_key_identity()` and `_compat()` derive keys and return an identity string.
- `libnvme_export_tls_key_versioned()` creates `NVMeTLSkey-<v>:<hmac>:<base64(raw+crc)>:` strings.
- `libnvme_import_tls_key_versioned()` validates version, HMAC, encoded length, Base64, decoded length, and CRC before returning key bytes.
- Compatibility wrappers preserve older import/export APIs.

Linux keyutils integration:
- Looks up or links keyrings, reads keys, searches keys, updates/revokes existing keys, scans TLS keys, and imports keys from controller config.
- Default keyring is `.nvme`.
- `__libnvme_import_keys_from_config()` ties controller TLS config into keyring IDs and key IDs used by fabrics connect option construction.

Host identity:
- Reads host NQN/ID from `LIBNVME_HOSTNQN` and `LIBNVME_HOSTID` environment variables or `/etc/nvme/hostnqn` and `/etc/nvme/hostid`.
- Generates host ID from DMI product UUID, DMI raw entries, IBM device-tree UUID, or random UUID fallback.
- Generates host NQN as `nqn.2014-08.org.nvmexpress:uuid:<hostid>`.

Dependencies:
- OpenSSL EVP/HMAC/KDF/core names when enabled.
- Linux keyutils when enabled.
- `base64.c`, `crc32.c`, cleanup helpers, private libnvme logging/path helpers, and UUID helpers.

Risks and notes:
- `getswordfish()` declares `counter` inside the loop, so multi-block deterministic output repeats the same SHA-256 block; for 48/64-byte outputs this weakens the derived secret pattern.
- Several identity strings are assembled with `sprintf` into buffers sized by estimates; current callers allocate expected sizes, but this is fragile against formula changes.
- `libnvme_import_tls_key_versioned()` only accepts version 1.
- `base64_encode()` does not NUL-terminate; callers rely on zeroed buffers or append terminators.
- Key material is generally freed but not explicitly zeroized before free.
- Tests should cover OpenSSL/no-OpenSSL, keyutils/no-keyutils, TLS key import/export round trips, CRC mismatch, hex secret parsing, `pin:` derivation, env/config host identity, and DMI fallback behavior.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/endian.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/endian.h

Portability header for endian conversion helpers.

Behavior:
- On Windows, defines `htobe16/32/64`, `htole16/32/64`, and `le16/32/64toh` using `__BYTE_ORDER__` and builtin byte swaps.
- On non-Windows, includes system `<endian.h>`.

Integration:
- Provides consistent endian macros for code that must build on Windows and Unix-like platforms.

Risks:
- Windows branch assumes compiler support for `__BYTE_ORDER__`, `__ORDER_BIG_ENDIAN__`, and `__builtin_bswap*`.
- Big-endian Windows is handled, but likely lightly tested.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/endian.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/fabrics.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/fabrics.c

Core NVMe-over-Fabrics implementation for libnvme: context setup, kernel connect/disconnect, discovery log handling, discovery-controller recursion, DIM registration, URI parsing, JSON/config-file discovery, and NBFT boot discovery.

Major responsibilities:
- Defines `/dev/nvme-fabrics` path and writes kernel connect option strings to it.
- Provides string decoders for fabrics enum fields: transport, address family, subtype, TREQ, EFLAGS, SECTYPE, RDMA provider/QP/CMS.
- Creates/frees `libnvmf_context` and installs discovery parser/callback hooks.
- Sets connection, host identity, crypto, device, queue, and reconnect policy fields on the context.
- Builds controller connect option strings from host/controller state and kernel-supported options.
- Connects, initializes, disconnects, and retries controllers.
- Fetches discovery log pages atomically using generation counter validation.
- Parses NVMe-oF boot URIs.
- Performs Discovery Information Management registration for supported discovery controllers.
- Reads NBFT files and connects boot/discovery entries.

Kernel option flow:
- `__nvmf_supported_options()` reads `/dev/nvme-fabrics` to learn supported option names, falling back to a conservative default option set on older `EINVAL` behavior.
- `build_options()` validates transport/address requirements, TLS/concat conflicts, DH-CHAP concat secret requirements, imports TLS keys, and appends supported options.
- `__nvmf_add_ctrl()` opens `/dev/nvme-fabrics`, writes the option string, maps errno values to libnvme connect errors, then parses `instance=<n>` from the kernel response.

Discovery flow:
- `libnvmf_discovery()` locates or creates a discovery controller, optionally reuses a requested device, performs `_nvmf_discovery()`, and disconnects transient controllers.
- `_nvmf_discovery()` fetches discovery logs, invokes hooks, and optionally connects discovered NVMe or discovery subsystems.
- Discovery entries are sanitized by trimming padded fields and fixing FC comma separators.
- TCP discovery entries can set TLS or concat automatically from `treq` and `sectype`.

Registration:
- `libnvmf_is_registration_supported()` checks dctype/cntrltype, falling back to Identify if sysfs fields are unavailable.
- `libnvmf_register_ctrl()` builds and sends a DIM command for TCP discovery controller registration/update/deregistration.

URI and NBFT:
- `libnvmf_uri_parse()` parses `nvme+tcp://...` style URIs into scheme, protocol, userinfo, host, port, path segments, query, and fragment, percent-decoding components.
- NBFT support scans `NBFT*` files, maps HFI MAC/VLAN to Linux interface names, connects SSNS records, and follows discovery descriptors.
- DHCP-related fallbacks retry TCP connects without firmware-provided `host_traddr` when the OS has a different local address.

Dependencies:
- Linux networking headers, sysfs/tree helpers, private fabrics structs, key/TLS helpers from `crypto.c`, NVMe passthrough command builders, and NBFT parser/free helpers.
- Uses cleanup attributes heavily for fd, directory, URI, and heap cleanup.

Risks and notable behaviors:
- Many context setters store borrowed pointers, except TLS `pin:` handling creates an owned exported key string; callers must keep borrowed source strings alive.
- `libnvmf_add_ctrl()` has a likely field typo in its config lookup context: `host_iface` is initialized from `libnvme_ctrl_get_trsvcid(c)`.
- `_nvmf_discovery()` has suspicious child/discover branching: recursive discovery is attempted only under `!child`, which can pass a NULL controller, while successful discovery-controller children are not recursed in that branch.
- URI parsing and unescaping allocate several pieces but does not check every allocation result from `unescape_uri()` or `calloc()` for path segments.
- Option strings are built with repeated `asprintf`, so large untrusted fields are memory-bounded by allocation but still passed to the kernel as-is.
- Tests should cover supported-option parsing, option-string generation, hostname vs literal address behavior, discovery log genctr retry, TLS/concat TREQ decisions, URI parsing, NBFT DHCP fallback, duplicate connect handling, and DIM registration data layout.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/fabrics.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/fabrics.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/fabrics.h

Public header for NVMe-over-Fabrics definitions and APIs.

Exports:
- Default controller loss timeout `NVMF_DEF_CTRL_LOSS_TMO`.
- Opaque `struct libnvmf_context`, `struct libnvmf_discovery_args`, and `struct libnvmf_uri`.
- Enum-to-string helpers for discovery log transport/address/subtype/TREQ/EFLAGS/SECTYPE/RDMA fields.
- Controller connect/disconnect APIs: `libnvmf_add_ctrl`, `libnvmf_connect_ctrl`, `libnvmf_connect`, `libnvmf_connect_config_json`, `libnvmf_disconnect_ctrl`.
- Discovery APIs: `libnvmf_get_discovery_log`, `libnvmf_discovery`, `libnvmf_discovery_config_json`, `libnvmf_discovery_config_file`, `libnvmf_discovery_nbft`.
- Registration API: `libnvmf_is_registration_supported`, `libnvmf_register_ctrl`.
- URI API: `libnvmf_uri_parse`, `libnvmf_uri_free`.
- Context creation, hook installation, connection/host/crypto/device/queue/reconnect setters.
- NBFT read/free APIs.

Integration:
- Includes `<nvme/tree.h>` for topology types like `libnvme_ctrl_t` and `libnvme_host_t`.
- Implemented by `fabrics.c` and accessor-generated files.
- Consumers use this API to perform connect-all, discovery, persistent discovery controller handling, and boot-table discovery without private struct access.

Contract notes:
- Hooks provide retry, connected, already-connected, discovery-log, and parser callbacks.
- `libnvmf_get_default_trsvcid()` returns constant default service strings, despite documentation saying allocated string.
- Context setters return errno-style status but often only assign fields.

Risks:
- Documentation has minor typos and a few ownership inaccuracies.
- Because context internals are opaque, accessors must remain synchronized with this header for users needing fine-grained field control.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/fabrics.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/filters.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/filters.c

Implements sysfs directory filters and scan helpers for NVMe topology discovery.

Filters:
- `libnvme_filter_namespace()`: matches `nvme<id>n<nsid>`.
- `libnvme_filter_paths()`: matches multipath-style `nvme<id>c<ctrl>n<nsid>`.
- `libnvme_filter_ctrls()`: matches controller names `nvme<id>` while excluding namespace/path names.
- `libnvme_filter_subsys()`: matches `nvme-subsys<id>`.

Scanners:
- `libnvme_scan_subsystems()` scans the subsystem sysfs directory.
- `libnvme_scan_subsystem_namespaces()` scans namespaces below a subsystem.
- `libnvme_scan_ctrls()` scans controller sysfs directory.
- `libnvme_scan_ctrl_namespace_paths()` scans path entries below a controller.
- `libnvme_scan_ctrl_namespaces()` scans namespace entries below a controller.
- `libnvme_scan_ns_head_paths()` scans path entries below a namespace head.

Dependencies:
- Uses `scandir` with `alphasort`, private sysfs directory helpers, and accessor getters for sysfs paths.

Risks and tests:
- Filters use `strstr(..., "nvme")` before `sscanf`, so unexpected names containing `nvme` are still parsed but must match the strict format.
- Returned `struct dirent **` arrays are caller-owned and must be freed.
- Tests should feed synthetic dirent names for hidden files, controllers, namespaces, paths, subsystem names, and invalid near-matches.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/filters.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/filters.h -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/filters.h

Public declarations for NVMe sysfs filters and scan helpers.

Exports:
- Four `dirent` predicate filters for namespaces, paths, controllers, and subsystems.
- Six scan helpers returning a count or negative errno-style error.

Integration:
- Includes `<dirent.h>` and `<nvme/tree.h>`.
- Implemented by `filters.c`.
- Used by libnvme topology scanning code to enumerate controllers, namespaces, paths, namespace heads, and subsystems.

Contract:
- On success, scan helpers return the number of entries in the caller-provided `struct dirent ***`.
- On failure, they return negative errno.
- Caller owns the `scandir` results.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/filters.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl-linux.c -->
# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl-linux.c

Linux ioctl transport implementation for direct NVMe admin/I/O passthrough and controller management operations.

Controller/block operations:
- `nvme_verify_chr()` ensures a transport fd is a character device.
- `libnvme_reset_subsystem()`, `libnvme_reset_ctrl()`, and `libnvme_rescan_ns()` issue libnvme reset/rescan ioctls after character-device verification.
- `libnvme_get_nsid()` reads namespace ID with `LIBNVME_IOCTL_ID`.
- `libnvme_update_block_size()` applies `BLKBSZSET` and triggers `BLKRRPART`.

Passthrough submission:
- `libnvme_submit_passthru32()` adapts `libnvme_passthru_cmd` into the legacy 32-bit-result ioctl structure.
- `libnvme_submit_passthru64()` sends the command directly through the 64-bit-result ioctl.
- I/O path probes 64-bit ioctl first unless probing is disabled, caches success/fallback state, and falls back to 32-bit on `-ENOTTY`.
- Admin path follows the same 64/32 probing, but rejects fabrics admin commands on the 32-bit fallback with `-ENOTSUP`.
- Submit hooks `submit_entry`, `submit_exit`, and `decide_retry` are invoked around ioctl attempts.

Synchronous exec:
- `libnvme_exec_admin_passthru()` and `libnvme_exec_io_passthru()` prefer io_uring async submission/reap when available, falling back to ioctl submission on `-ENOTSUP` or unavailable io_uring.
- Both return completion status for async execution, or ioctl error/status from direct submission.

Dependencies:
- Linux ioctl constants, block ioctls, CCAN helpers, libnvme private transport handle state, and async passthrough functions from the uring layer.

Risks and tests:
- `libnvme_get_nsid()` uses `errno` after ioctl return rather than checking a negative return directly; tests should cover ioctl returning `-1` and unusual valid IDs.
- Passthrough probing mutates cached state in the transport handle, so concurrent use of one handle needs external safety if required.
- Dry-run mode still invokes submit hooks but skips ioctl.
- Tests should cover 64-bit ioctl success, `ENOTTY` fallback, retry callback behavior, timeout defaulting, dry-run, MI admin passthrough routing, and io_uring fallback.
<!-- END FILE RESEARCH: sources/virtualization/nvme-cli/libnvme/src/nvme/ioctl-linux.c -->