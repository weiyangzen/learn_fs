# Group Research:

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ioctl.h

User/kernel ioctl ABI for `/dev/crypto`. It defines command numbers, request payload structures, and 32-bit compatibility structures for PKCS#11-like cryptographic operations exposed through the illumos kernel cryptographic framework.

Key elements:
- Defines the `CRYPTO(x)` ioctl namespace, `CRYPTO_MAX_ATTRIBUTE_COUNT`, `CRYPTO_IOFLAGS_RW_SESSION`, `CRYPTO_INPLACE_OPERATION`, selected PKCS#11 mechanism constants, and threshold metadata used by provider capability reporting.
- `crypto_function_list_t` describes provider-supported function groups plus hash/HMAC limits and per-mechanism thresholds.
- General ioctls expose provider function lists and mechanism-name to internal-number translation.
- Session and login ioctls cover open, close, close-all, login, and logout, with user PIN buffers passed by address/length.
- Cryptographic operation structs cover encrypt, decrypt, digest, MAC, sign, verify, recover variants, multipart init/update/final flows, and combined update operations such as digest-encrypt and decrypt-verify.
- Random-number ioctls expose seed and generate operations.
- Object-management ioctls cover create, copy, destroy, get/set attributes, get size, and find init/update/final.
- Key ioctls cover stored-object key generation, key-pair generation, wrap, unwrap, derive, plus no-store key-generation/derivation variants that return key material through attributes instead of provider object handles.
- Provider and mechanism ioctls expose provider lists, token/provider metadata, provider mechanisms, mechanism info, token/PIN initialization, global mechanism list, all-mechanism info, and provider-by-mechanism selection.
- `_KERNEL && _SYSCALL32` sections mirror pointer- and size-bearing structs with `caddr32_t`, `size32_t`, and packed layout where long-long alignment differs.

Dependencies:
- Uses core crypto ABI types from `sys/crypto/api.h`, `sys/crypto/spi.h`, and `sys/crypto/common.h`, including sessions, providers, mechanisms, keys, objects, attributes, and mechanism-info structures.
- Consumed by the `/dev/crypto` ioctl implementation and by userland libraries/tools that marshal these structures.

Research notes:
- This is an ABI header; field order, sizes, command numbers, and 32-bit translations are compatibility-sensitive.
- Several structs use trailing one-element arrays for variable-length lists, so callers must allocate enough space for count-dependent payloads.
- Many payloads carry raw user pointers and lengths; kernel handlers must copy in/out defensively and translate embedded crypto mechanism/key structures for 32-bit callers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ioctladmin.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ioctladmin.h

Administrative ioctl ABI for `/dev/cryptoadm`. It defines control payloads for cryptographic provider inventory, disabled-mechanism configuration, software module management, pool control, door registration, and FIPS 140 mode state.

Key elements:
- Defines `ADMIN_IOCTL_DEVICE` as `/dev/cryptoadm` and the `CRYPTOADMIN(x)` command-number namespace.
- List/info structs expose hardware provider entries, software provider names, per-device/per-software mechanism lists, and disabled mechanism lists.
- Software-management payloads support unloading a software provider and loading software configuration.
- `crypto_load_door_t` carries a door id for userland administration integration.
- `crypto_fips140_t` carries a FIPS operation and resulting status.
- FIPS operation enum supports status query, enable, and disable.
- FIPS status enum distinguishes unset, validating, shutdown, enabled, and disabled modes.
- Defines admin command numbers for version, lists, provider info, disabled config, software unload/config, pool create/wait/run, door loading, and FIPS status/set.

Dependencies:
- Uses public crypto common types such as `crypto_dev_list_entry_t` and `crypto_mech_name_t`.
- Includes a 32-bit compatibility structure for `crypto_get_soft_list_t`, the payload with embedded pointer/size fields.

Research notes:
- Like `ioctl.h`, this is ABI-sensitive and uses trailing one-element arrays for variable-length mechanism/provider lists.
- The FIPS mode enum models both requested mode and framework validation/shutdown states, so consumers should not treat it as a simple boolean.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ioctladmin.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ops_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ops_impl.h

Internal request-parameter packaging layer for the kernel cryptographic framework scheduler. It defines compact per-operation parameter bundles, operation group/type enums, and macros that marshal KCF API/ioctl arguments into a single `kcf_req_params_t` passed to providers.

Key elements:
- Defines operation-parameter structs for digest, MAC, encrypt, decrypt, sign, verify, encrypt+MAC, MAC+decrypt, random, session, object, key, provider-management, and no-store key operations.
- `kcf_op_type_t` enumerates init/single/update/final/atomic operation phases plus digest-key, MAC-verify, dual cipher/MAC, recover, random, session, object, key, key-check, and provider-management operations.
- `kcf_op_group_t` groups request payload unions by provider function families, including operations without mechanisms such as sessions and objects.
- `IS_INIT_OP`, `IS_SINGLE_OP`, `IS_UPDATE_OP`, `IS_FINAL_OP`, and `IS_ATOMIC_OP` classify operation types used by KCF dispatch logic.
- `kcf_req_params_t` stores the group, operation type, and a union of the corresponding parameter bundle.
- `KCF_WRAP_*_OPS_PARAMS` macros fill request bundles in-place and preserve the framework mechanism type before provider mechanism-number translation.
- Session and provider-management wrappers carry an explicit provider descriptor for cases where a logical provider supplies the handle but another provider supplies the ops vector.
- Key wrappers handle stored-object and no-store variants, including public/private key-pair templates and output templates.
- `KCF_SET_PROVIDER_MECHNUM` translates a framework mechanism number into a provider-local mechanism number before SPI invocation.

Dependencies:
- Depends on KCF provider descriptors and mechanism translation from `sys/crypto/impl.h`, provider SPI types from `spi.h`, and public crypto data/key/mechanism types from `api.h` and `common.h`.
- Used by ioctl and kernel crypto API front ends before submission through scheduler routines declared in `sched_impl.h`.

Research notes:
- The wrapper macros intentionally copy `crypto_mechanism_t` by value but store data/key/template pointers; caller lifetimes still matter for synchronous versus asynchronous paths.
- Some struct fields are generic to keep the union small; comments identify reused fields for wrap/unwrap and key-pair public/private variants.
- Mechanism translation is split from initial wrapping so KCF can retain both framework and provider mechanism identities.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/ops_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/sched_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/sched_impl.h

Internal scheduler structures for the kernel cryptographic framework. It defines synchronous/asynchronous request nodes, context lifetime tracking, software-provider queueing, request-id hashing, provider retry lists, bufcall/notify lists, and scheduler entry points.

Key elements:
- Defines request states `REQ_ALLOCATED`, `REQ_WAITING`, `REQ_INPROGRESS`, `REQ_DONE`, and `REQ_CANCELED`, plus synchronous/asynchronous call types.
- Fast-path macros distinguish direct software-provider execution from queued execution and derive allocation flags from request context.
- `kcf_prov_tried_t` tracks providers already attempted during failover/retry provider selection.
- Recovery macros classify retryable provider errors such as busy, device failure, memory, buffer-too-big, key-size range, and permission failures.
- `kcf_sreq_node_t` represents a synchronous request with CV/lock completion state, return value, parameter pointer, context, provider, and per-provider CPU mapping.
- `kcf_areq_node_t` represents an asynchronous request with saved parameters, callback request argument, context request chain links, turn-taking state, global software queue links, provider, tried-provider list, request-id hash links, completion CV, and reference count.
- Reference macros release async requests and KCF contexts when atomic counts reach zero.
- `kcf_dual_req_t` stores framework-generated chained requests for dual operations, including saved offset/length for continuation.
- Request IDs are partitioned across 16 tables and 512 hash buckets, with high-bit/counter layout designed to avoid wraparound collision checks.
- `kcf_context_t` embeds the provider-visible `crypto_ctx_t`, tracks references, in-use locking, async request chains, provider descriptors, mechanism entry, and second context for dual operations.
- `kcf_ctx_template_t` records provider handle, generation, allocation size, and provider template pointer for software context templates.
- Defines global software queue, software worker pool, crypto bufcall elements, notify-list elements, taskq sizing constants, and exported global queue/list locks.
- Declares scheduler/provider-selection routines including provider lookup, dual-provider lookup, request submission, common SPI submission, context allocation/free, notification walks, dual request allocation, and chained request callbacks.

Dependencies:
- Uses crypto API/SPI/internal provider descriptors and request parameters from `api.h`, `spi.h`, `impl.h`, `common.h`, and `ops_impl.h`.
- Integrates with kernel synchronization primitives, task queues, doors, atomics, condition variables, and provider CPU mapping.

Research notes:
- Context release is conditional: queued, busy, and buffer-too-small results keep contexts alive for provider completion or client retry.
- Async requests must copy request parameters because caller stack storage can disappear; synchronous requests can point at caller-owned parameters.
- `CHECK_FASTPATH` and special software-provider request handles control whether provider callbacks see `KM_SLEEP` or `KM_NOSLEEP` semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/sched_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/spi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/spi.h

Cryptographic Service Provider Interface header. It defines provider registration structures, provider operation vectors, request/context handles, mechanism capability masks, provider status, and callbacks exported by the kernel cryptographic framework to providers.

Key elements:
- Defines SPI interface versions 1 through 4 and provider-private, context-template, and request-handle opaque types.
- `crypto_ctx_t` is the provider-facing operation context with provider/session handles, provider-private and framework-private slots, flags, and operation state.
- Extended token/provider flag constants mirror PKCS#11 token-info state such as RNG, write protection, login requirement, token initialized, and PIN warning/lock states.
- Operation-vector structs cover control, context/template management, digest, cipher, MAC, sign, verify, old dual operations, dual cipher/MAC operations, random, session, object, key, provider management, mechanism copyin/copyout/free, no-store key, and FIPS 140 POST hooks.
- Versioned `crypto_ops_v1` through `crypto_ops_v4` extend the provider ops vector by adding mechanism ops, no-store key ops, and FIPS 140 ops.
- `crypto_provider_dev_t` identifies software providers by module linkage and hardware/logical providers by `dev_info_t`.
- `crypto_func_group_t` masks describe which function groups each provider mechanism supports, including atomic and dual-operation capabilities.
- Defines simple and dual function-group masks for internal KCF checks.
- `crypto_mech_info_t` describes a provider mechanism name, provider mechanism number, supported function groups, key-size range, and mechanism flags.
- `crypto_provider_info_t` describes provider registration state: interface version, description, type, device, provider handle, ops vector, mechanism list, logical-provider membership, and provider flags.
- Provider flags hide providers behind logical providers, indicate hash/HMAC update limitations, and mark synchronous providers.
- Exports provider lifecycle/completion functions: `crypto_register_provider`, `crypto_unregister_provider`, `crypto_provider_notification`, `crypto_op_notification`, and `crypto_kmflag`.

Dependencies:
- Kernel-only portions depend on DDI device types, memory allocation flags, module linkage, and public crypto common structures.
- Included by provider drivers/modules and by KCF internals that dispatch through provider operation vectors.

Research notes:
- The versioned ops union is append-style ABI evolution; accessor macros flatten the current view but providers must set the matching interface version.
- Provider mechanism numbers are provider-local; KCF maps framework mechanism IDs before invoking SPI callbacks.
- Request handles are how asynchronous providers report completion back to KCF; software fast-path requests use special handles to communicate allocation constraints.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/crypto/spi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/csiioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/csiioctl.h

Small ioctl-number header for codeset-independent communication between `stty(1)` and the `ldterm(4M)` line discipline.

Key elements:
- Defines the `CSI_IOC` command prefix.
- `CSDATA_SET` asks `ldterm` to accept an `ldterm_cs_data_t` definition and switch locale/codeset methods when valid.
- `CSDATA_GET` asks `ldterm` to return the currently active codeset data.

Dependencies:
- The comments reference `ldterm_cs_data_t`, defined elsewhere in the terminal/line-discipline headers.
- Used by terminal control paths that configure multibyte or locale-specific character-width behavior.

Research notes:
- This header only defines ioctl command values and explanatory comments; payload validation and codeset switching are implemented in `ldterm`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/csiioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctf.h

On-disk/in-memory format definition for Compact ANSI-C Type Format data. It describes the CTF section layout, header, type records, labels, string references, type kind encoding, integer/float encodings, arrays, members, large members, and enums.

Key elements:
- Opening comment documents the CTF file layout: header, labels, object types, function info, data types, and string table.
- Defines maximum type ID, name offset, variable-length member count, integer offset/bits, normal type size, large-size sentinel, and maximum large size.
- `ctf_preamble_t` and `ctf_header_t` encode magic/version/flags and section offsets relative to the end of the header.
- Optional `CTF_OLD_VERSIONS` block defines the older v1 header and v1 info packing macros.
- Defines CTF magic, supported/current versions, and compression flag.
- `ctf_lblent_t` maps a label string reference to the last type ID covered by that label.
- `ctf_stype_t` is the compact type record for normal-size types; `ctf_type_t` extends it with 64-bit size split into high/low words.
- Macros pack and unpack `ctt_info` kind/root/vlen fields and `ctt_name` string-table/id offsets.
- Parent/child type-id macros split type IDs around `CTF_CHILD_START` and convert between IDs and indexes.
- Defines string table IDs 0 and 1, large-size helpers, and large-member offset helpers.
- Enumerates CTF type kinds: unknown, integer, float, pointer, array, function, struct, union, enum, forward, typedef, volatile, const, and restrict.
- Defines integer and floating-point encoding macros and flags, including signed/char/bool/varargs and many float encodings.
- Defines `ctf_array_t`, `ctf_member_t`, `ctf_lmember_t`, and `ctf_enum_t`.

Dependencies:
- Uses fixed-width and system integer types from `sys/types.h`.
- Consumed by libctf, kernel CTF support, debuggers, CTF tools, and code that reads `.SUNW_ctf` ELF sections.

Research notes:
- The format is data-model independent and designed for mmap-friendly parsing; structures avoid native pointer-sized fields.
- Struct/union member encoding switches to `ctf_lmember_t` when the containing type size reaches `CTF_LSTRUCT_THRESH`.
- String references deliberately support both internal CTF strings and the external ELF string table to avoid duplication.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctf_api.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctf_api.h

Private libctf and kernel CTF module API. It exposes opaque CTF container/type handles, libctf-specific error codes, section descriptors, type metadata structs, iteration callback signatures, open/query/update/write routines, and dynamic type construction APIs.

Key elements:
- Explicitly warns that the interface is not public and may change between releases.
- Defines opaque `ctf_file_t` and `ctf_id_t`, plus `CTF_ERR` for failed ID/status returns.
- Enumerates libctf error codes starting at `ECTF_BASE`, covering format, ELF/CTF version, endian, symbol/string table, corruption, missing data, parent/model mismatch, mmap/zlib/decompression, bad names/IDs, wrong type kind, missing labels/members/enums, read-only/full/dynamic conflicts, merge/label conflicts, and conversion backend errors.
- `ctf_sect_t` describes raw CTF, symbol, and string table buffers for `ctf_bufopen()`.
- Defines public query structs for encodings, member info, array info, function info, and label info.
- Defines CTF data-model constants and `CTF_MODEL_NATIVE`.
- Defines dynamic-container add flags for root and non-root type visibility.
- Callback typedefs support visits over type graphs, members, enums, types, labels, functions, objects, and strings.
- Opening APIs support buffers, file descriptors, paths, dynamic creation, fd-backed creation, duplication, close, parent metadata, import, data-model get/set, and per-container private data.
- Query APIs cover errors, flags, version, max type id, symbol count, function info/args, lookup by name or symbol, symbol name, type resolution/naming/size/alignment/kind/reference/pointer/encoding/visit/compare/compatibility, member/array/enum/label info, and iterators.
- Dynamic update APIs add arrays, qualifiers, enums, floats, forwards, function pointers, integers, pointers, imported types, typedefs, structs/unions, enumerators, members, function/object/label records, set array/root/size, delete types, update/discard/write, and expose raw data pointers.
- Kernel-only API includes `ctf_modopen()` for opening CTF data from a loaded module.

Dependencies:
- Includes `sys/elf.h` and `sys/ctf.h`, and uses ELF section constants and CTF format/type definitions.
- Shared by userland libctf consumers and kernel CTF support, with kernel-specific declarations guarded by `_KERNEL`.

Research notes:
- The API intentionally separates immutable container inspection from dynamic container mutation and requires `ctf_update()`/`ctf_discard()` to commit or abandon edits.
- Many callbacks return `int`, implying iteration can be stopped or failed by the callback implementation.
- Type IDs are opaque at the API level even though `ctf.h` documents their on-disk encoding.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctf_api.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctfs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctfs.h

Public control-code header for the contract filesystem mounted at `/system/contract`. It defines ioctl/message command values for template, control, status, and event endpoints.

Key elements:
- Defines `CTFS_ROOT` as `/system/contract`.
- Defines the `CTFS_PREFIX` and `CTFS_IOC(x, y)` encoding used for command values.
- Template-file commands activate, clear, create from, set, and get contract templates.
- Control-file commands abandon, acknowledge, request more negotiation quantum, adopt, create a new contract, and negative-acknowledge negotiation.
- Status-file command obtains contract status.
- Event-endpoint commands reset queue position, receive normal or critical events, skip current event, and request reliable receipt.

Dependencies:
- Includes `sys/contract.h` for contract subsystem types and constants used by CTFS clients.
- Consumed by contract filesystem vnode operations and user/kernel CTFS clients.

Research notes:
- This header is command-number only; CTFS object layouts and vnode state live in `ctfs_impl.h`.
- Commands are grouped by virtual file role, reflecting CTFS's file-oriented control model.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctfs_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctfs_impl.h

Private implementation header for the contract filesystem. It defines CTFS synthetic inode encodings, per-vnode private data structures, endpoint listener state, VFS state, vnode creation helpers, common access/open/close helpers, and vnodeops templates.

Key elements:
- Encodes root inode as zero, contract-specific files with the high bit set plus file number and contract id, and type-specific files with type/file fields.
- Provides macros for contract directory, `all` symlink, contract special files, type directories, and type special files.
- Defines `CTFS_NAME_MAX` and endpoint flags for setup and nonblocking mode.
- `ctfs_endpoint_t` combines a mutex, contract listener, and endpoint flags.
- Root, `all`, type-directory, and latest nodes are represented using `gfs_dir_t`.
- `ctfs_symnode_t` stores a GFS file, target contract, symlink target string, and string length.
- `ctfs_cdirnode_t` stores contract-directory contents, target contract, and contract vnode-list linkage.
- Template, ctl/status, events, and bundle/pbundle node structs store the GFS file plus the relevant contract/template/event queue/listener state.
- `ctfs_vfs_t` stores the root vnode for the mounted CTFS instance.
- Declares vnode factory functions for type dirs, templates, latest, bundles, ctl/status, events, `all`, contract dirs, and symlinks.
- Declares shared getattr, close, access, and open helpers.
- Exposes vnodeops vectors for each CTFS virtual file type.

Dependencies:
- Depends on the contract subsystem and generic filesystem (`gfs`) support.
- Uses vnode/vattr/cred/caller context types from the kernel VFS layer through included contract/GFS headers.

Research notes:
- The inode encoding is part of CTFS's stable synthetic namespace; changing it would affect vnode identity and filesystem behavior.
- Endpoint nodes embed listener state directly, so open/read/ioctl paths must coordinate endpoint setup and blocking flags under `ctfs_endpt_lock`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctfs_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctype.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctype.h

Kernel/simple ASCII character classification header. It defines macro predicates and inline boolean functions for digit, hex digit, lower/upper alpha, alphanumeric, printable, and whitespace tests.

Key elements:
- Macro predicates operate directly on ASCII character ranges and avoid locale dependence.
- `ISSPACE` recognizes space, tab, carriage return, and newline.
- Inline functions `isdigit`, `isxdigit`, `islower`, `isupper`, `isalpha`, `isalnum`, `isprint`, and `isspace` wrap the macros and return `boolean_t`.

Dependencies:
- Includes `sys/types.h` for `boolean_t` and `__GNU_INLINE`.
- Intended for kernel or system code that cannot or should not depend on libc locale-aware ctype behavior.

Research notes:
- The functions accept `char`, not `int`, and are ASCII-only; they are not drop-in locale-aware libc replacements.
- Macro arguments may be evaluated more than once in composed predicates such as `ISXDIGIT`, `ISALPHA`, and `ISALNUM`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cyclic.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cyclic.h

Public kernel interface for the cyclic subsystem, illumos's high-resolution cyclic timer/callback facility. It defines cyclic levels, IDs, handler/time descriptors, omni-cyclic handlers, and lifecycle/CPU-migration APIs.

Key elements:
- Defines three execution levels: low, lock, and high, with two software interrupt levels.
- Defines cyclic ID/index/cookie/level types, handler function type, backend argument type, and `CYCLIC_NONE`.
- `cyc_handler_t` stores callback function, argument, and desired cyclic level.
- `cyc_time_t` stores absolute first-fire time and interval.
- `cyc_omni_handler_t` describes callbacks used to create/remove per-CPU cyclics as CPUs come online/offline.
- `CY_INFINITY` represents an unbounded time value.
- Kernel/fake-kernel APIs add/remove cyclics, add omni-cyclics, bind/reprogram/move cyclics, get timer resolution, handle CPU online/offline/juggle/move events, suspend/resume, and dispatch high/soft cyclic interrupts.

Dependencies:
- Includes time, CPU, and CPU partition definitions for non-assembly consumers.
- Implemented by the cyclic subsystem and platform-specific cyclic backend.

Research notes:
- The level model is central: callbacks may run at high interrupt, lock-level soft interrupt, or low-level soft interrupt context.
- Omni-cyclics abstract per-CPU timer setup and teardown across CPU hotplug.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cyclic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cyclic_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cyclic_impl.h

Private cyclic subsystem implementation header. It documents the platform backend contract in detail and defines backend ops, cyclic subsystem initialization, per-CPU cyclic state, tracing/coverage support, omni-cyclic bookkeeping, xcall arguments, and heap helpers.

Key elements:
- Large design comment specifies backend-supplied operations and call contexts for configure, unconfigure, enable, disable, reprogram, soft interrupt generation, interrupt-level set/restore, cross-call, suspend, and resume.
- `cyc_backend_t` is the platform callback vector and backend argument storage.
- Declares `cyclic_init()` and `cyclic_mp_init()` for backend registration and multiprocessor initialization.
- Debug builds enable `CYCLIC_TRACE`.
- `cyc_state_t` tracks per-CPU cyclic state: online, offline, expanding, removing, and suspended.
- `cyclic_t` records expiration time, interval, handler, argument, pending count, binding flags, and execution level.
- Producer/consumer and soft-buffer structs queue pending cyclic indexes between hard and soft interrupt contexts.
- Trace and coverage structs store diagnostic records when enabled.
- `cyc_cpu_t` stores per-CPU heap, cyclic array, soft buffers, backend, semaphores/modify levels, pending reprogram state, and optional trace buffers.
- `cyc_omni_cpu_t` and `cyc_id_t` maintain omni-cyclic per-CPU instances and globally visible cyclic IDs protected by an rwlock.
- `cyc_xcallarg_t` packages cyclic add/remove/move state for cross-call execution on target CPUs.
- Defines default per-CPU allocation, passive level, wait modes, and binary-heap parent/child index macros.

Dependencies:
- Depends on `cyclic.h` public types and kernel rwlocks, semaphores, CPU structures, and high-resolution time.
- Backend implementations are architecture/platform-specific and must call back into `cyclic_fire()`/`cyclic_softint()` as required.

Research notes:
- The backend contract is strict about CPU affinity, interrupt level, blocking behavior, and exactly-once cross-call semantics; violations can corrupt cyclic state.
- Per-CPU cyclics are organized in a heap by expiration time, with pending handoff through fixed producer/consumer buffers for soft levels.
- Suspend/unconfigure paths assume cyclic subsystem suspension and disabled interrupts for safe CPU dynamic reconfiguration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cyclic_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dacf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dacf.h

Public Device Autoconfiguration Framework interface. It defines DACF module/opset descriptors, operation IDs, client information handles, client helper accessors, and success/failure return codes.

Key elements:
- Defines DACF interface revision `DACF_MODREV_1`.
- Opaque handles `dacf_arghdl_t` and `dacf_infohdl_t` represent operation arguments and device/minor information.
- Operation IDs include post-attach and pre-detach hooks, plus error/end sentinels.
- `dacf_op_t` maps an operation ID to a callback function.
- `dacf_opset_t` groups a named, null-terminated set of operations.
- `struct dacfsw` is the module-visible DACF switch with revision and opsets; `kmod_dacfsw` is the kernel-provided module symbol.
- Client helper functions retrieve minor name/number, dev_t, driver name, devinfo node, named arguments, stored per-info data, and vnode creation.
- Defines `DACF_SUCCESS` and `DACF_FAILURE`.

Dependencies:
- Uses DDI device/minor types through included `sys/types.h` and externally visible `dev_info_t`/`vnode` declarations.
- Implemented by DACF core and consumed by DACF modules that register post-attach/pre-detach actions.

Research notes:
- Operation arrays and opset arrays are null/sentinel terminated, so module definitions must include `DACF_OPID_END`.
- The framework lets callbacks store/retrieve per-info private state, which is important for pairing post-attach setup with pre-detach teardown.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dacf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dacf_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dacf_impl.h

Private implementation header for the Device Autoconfiguration Framework. It defines DACF module/rule/argument/reservation state, hash sizes, parsing helpers, rule matching/reference management, reservation processing, operation invocation, debugging flags, and DDI hook entry points.

Key elements:
- `dacf_module_t` tracks a DACF module name, lock, loaded state, and opset table.
- Defines small hash-table sizes for rules, modules, and info handles.
- Reservation-processing flags distinguish invoke and release passes.
- Device specifier enum supports matching by minor node type, driver minor name, or device path.
- `dacf_arg_t` is a linked list of named operation arguments.
- `dacf_rule_t` stores match data, module/opset/opid target, options, reference count, and operation arguments.
- `dacf_rsrvlist_t` records reserved rules to invoke later, their info handle, last result, and next pointer.
- Kernel-only declarations cover global DACF lock, module register/unregister, argument insertion/deletion, initialization, binding-file reading, rule clearing, string-to-enum parsing, option parsing, rule insertion/hold/release, reservation creation/processing/clearing, rule matching, and operation invocation.
- Defines detailed invocation failure codes for missing module, missing opset, missing op, and failed op.
- Debug flags distinguish generic messages and devinfo diagnostics.
- DACF client support hooks match minor creation and invoke post-attach/pre-detach processing.

Dependencies:
- Includes public `dacf.h`; relies on kernel locks, DDI minor data, devinfo nodes, and configuration-file parsing implemented elsewhere.
- Tied to DDI attach/detach and minor-node creation hooks.

Research notes:
- Rules are reference-counted and may be reserved for delayed processing, so attach/detach paths must handle lifetimes across module loading and invocation.
- Matching is data-driven from DACF binding files and can target different device identifiers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dacf_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/damap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/damap.h

Public Delta Address Map API. It provides stabilized string-address sets for device/bus discovery, supporting per-address reports, full-set reports, delayed stabilization, activation/release callbacks, configure/unconfigure callouts, lookup, and reference management.

Key elements:
- Opening comment explains per-address reporting, full-set reporting, stabilization timers, activation/release, and stable-address lookup.
- Defines opaque `damap_t`, `damap_id_t`, and unused `damap_id_list_t`; `NODAM` is the null ID.
- Deactivation reasons distinguish gone, configuration failure, and unstable report.
- Provider callbacks handle address activation and deactivation with provider-private state.
- Class callbacks handle configuration and unconfiguration of stabilized addresses.
- Report modes are per-address and full-set.
- Map options distinguish serialized configuration and multithreaded configuration.
- `damap_create()` wires map name, report mode, stabilization/config parameters, callback arguments, callbacks, and returned map handle.
- Basic APIs destroy maps, query name/size/empty state, and synchronize with pending operations.
- Per-address APIs add/delete by string or ID.
- Full-set APIs begin/add/end, flush, and reset address sets; `DAMAP_END_RESET` and `DAMAP_END_ABORT` modify end behavior.
- Lookup/reference APIs iterate IDs, map ID to address/nvlist/private data, hold/release/ref IDs, set/get private data, lookup one address, and lookup all stable addresses.
- Return codes include success, exists, map full, invalid, generic failure, and `DAM_SHAME`.

Dependencies:
- Uses `nvlist_t` payloads and kernel callback patterns; concrete structures are private in `damap_impl.h`.
- Intended for bus/device discovery layers that need debounce/stabilization before configuring devices.

Research notes:
- Full-set reporting frees providers from issuing explicit deletes for disappeared addresses; stabilization applies to the entire reported set.
- IDs require explicit hold/release in lookup paths to avoid use-after-release while configuration/unconfiguration proceeds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/damap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/damap_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/damap_impl.h

Private implementation header for Delta Address Map. It defines the concrete map structure, per-address soft state, state flags, bitset membership tests, report types, and kstat counters used to implement stabilized address reporting.

Key elements:
- Includes DDI, time, devctl, nvpair, sysevent, bitset, and SDT headers needed by the implementation.
- Defines internal callback typedefs corresponding to the public activation/deactivation and configure/unconfigure callbacks.
- `struct dam` stores map name, flags, options, report mode, stabilization ticks, map size/highest ID, timeout ID, activation/config callback arguments and function pointers, address-to-ID hash, active/stable/report bitsets, per-address soft state, update/stable timestamps, stabilization counters, sync CV/lock, kstats, and sync timeout count.
- Map flags track stable-pending, destroy-pending, and full-set-add pending state.
- `dam_da_t` stores per-address flags, jitter/rereport count, reference count, provider/config private pointers, stable and reported nvlists, stabilization deadline, timestamps/counters, and address string pointer for debugging.
- Per-address flags track initialized, failed configuration, and released addresses.
- Report types distinguish address add and delete reports.
- Macros test whether an ID is in the report set or active/stable set.
- `dam_kstats` exposes cycles, overrun, jitter, and active-address counters.

Dependencies:
- Includes public `damap.h` indirectly through callback types and deactivation reasons, plus DDI string-ID hashing and bitsets.
- Used only by DAMAP implementation code and debugging/observability paths.

Research notes:
- The implementation maintains separate active, stable, and reported sets, which is what enables debounce and full-set reconciliation.
- Address soft state carries both current stable nvlist and newly reported nvlist, allowing configuration only after a report stabilizes.
- Timeout-driven stabilization and sync waiting are coordinated through `dam_lock`, `dam_sync_cv`, and timeout IDs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/damap_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dc_ki.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dc_ki.h

Kernel interface header for Sun Cluster bootstrap integration. It declares hooks used by drivers/modules loaded before the root filesystem is mounted.

Key elements:
- Includes types, DDI, and module-control definitions.
- Declares `cluster()` plus `clboot_modload()`, `clboot_loadrootmodules()`, `clboot_rootconf()`, and `clboot_mountroot()`.
- Comments state the routines are implemented in the `misc/cl_bootstrap` module from the SunCluster consolidation.

Dependencies:
- Depends on `struct modctl`, DDI declarations, and early boot/root-mount code that calls these hooks.

Research notes:
- This is a narrow external integration point; the header contains declarations only and no local state.
- The functions sit on the boot path before root is mounted, so callers cannot assume normal filesystem/module availability.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dc_ki.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcam/dcam1394_io.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcam/dcam1394_io.h

Ioctl and data-structure header for DCAM IEEE 1394 camera control. It defines camera parameter IDs, subparameters, value constants, ioctl commands, status flags, parameter-list helpers, frame records, and register read/write payloads.

Key elements:
- Parameter-list macros initialize, add/remove/test entries, and access value/error fields in a two-dimensional parameter list.
- Defines 30 parameters and 24 subparameters.
- Parameter IDs cover power, video-mode capabilities, frame-rate capabilities per video mode, current video mode/frame rate, ring-buffer capacity/ready count/read-pointer increment, frame byte size, status, and image controls such as brightness, exposure, sharpness, white balance, hue, saturation, gamma, shutter, gain, iris, focus, zoom, pan, and tilt.
- Subparameters cover video modes, frame rates, feature presence/capabilities, min/max/current values, on/off, control mode, white-balance U/V values, and none.
- Value aliases define video modes, frame rates, automatic/manual control, and power on/off.
- Ioctl commands support register read/write, camera reset, parameter get/set, frame receive start/stop, ring-buffer flush, and frame sequence counter reset.
- Status flags report frame receive completion, lost frame, parameter changes, sequence counter overflow, and camera unplug.
- `dcam1394_param_list_entry_t` stores a requested flag, error, and value; `dcam1394_param_list_t` is the fixed parameter/subparameter matrix.
- `dcam1394_frame_t` describes video mode, sequence number, timestamp, and frame buffer pointer.
- `dcam1394_reg_io_t` carries register offset/value for register access.

Dependencies:
- Includes `sys/time.h` for `hrtime_t`.
- Consumed by the DCAM 1394 driver and userland code issuing camera-control ioctls.

Research notes:
- Parameter and subparameter values intentionally alias generic indices and descriptive names, so consumers can use either naming style.
- The frame structure includes a raw buffer pointer, making ioctl handlers responsible for user/kernel pointer handling and data-size validation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcam/dcam1394_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcopy.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcopy.h

Private DMA copy API for IP stack use. It defines the upper-layer client interface for discovering DMA copy engines, allocating channels and commands, posting physical-address copy commands, and polling or blocking for completion.

Key elements:
- Warns that the interface is private to the IP stack.
- Declares `uioa_dcopy_enable()` and `uioa_dcopy_disable()` to toggle dcopy KAPI integration in `uioa`.
- Defines common return statuses: failure, success, no resources, pending, and completed.
- `dcopy_query_t` reports the number of DMA channels in the system.
- `dcopy_handle_t` is an opaque channel handle.
- Allocation flags distinguish sleeping and non-sleeping allocation.
- `dcopy_alloc()` allocates a channel with in-order command completion; `dcopy_free()` releases it.
- `dcopy_query_channel_t` reports DCA support, device id/capabilities, channel size, and device-local channel number.
- Command version and command type currently define physical-address copy.
- Command flags support queuing without notify, no status, DCA target, completion interrupt, no-wait resource handling, source/destination snoop disabling, loop descriptors, and internal sync.
- `dcopy_cmd_copy_t` carries source physical address, destination physical address, and size.
- `dcopy_cmd_t` is a pointer to `struct dcopy_cmd_s`, which stores version, flags, command selector, command union, DCA id, and private command state.
- `DCOPY_ALLOC_LINK` allows command-allocation chaining for bulk free through the last command.
- Command lifecycle APIs allocate/free, post, and poll commands; blocking poll is only allowed in base context and requires interrupt generation.

Dependencies:
- Uses core kernel types from `sys/types.h`; provider-side details are in `dcopy_device.h`.
- Tied to DMA engines that understand physical copy commands and optional DCA/cache-snoop capabilities.

Research notes:
- Commands cannot be reused or freed until polling reports failure or completion.
- `DCOPY_CMD_NOSTAT` prevents later completion polling for that command, so callers must structure batches carefully.
- Channel allocation does not grant exclusive engine access; it guarantees ordering for commands posted through that channel.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcopy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcopy_device.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcopy_device.h

Provider-side registration interface for DMA copy devices. It defines private command state managed by dcopy, callback vectors implemented by DMA drivers, device info registration payloads, and notification/unregistration APIs.

Key elements:
- `dcopy_cmd_priv_s` is allocated during driver command allocation and attached to `dcopy_cmd_t.dp_private`; DMA drivers may only use `pr_device_cmd_private` directly.
- Private command state includes blocking-poll initialization, list node, wait flag, mutex/CV, backpointer to command, channel pointer, and device-private pointer.
- `dcopy_device_cb_t` version 0 contains callbacks for channel allocate/free, command allocate/free, command post/poll, and asynchronous unregister completion.
- Channel allocation callback receives device private state, dcopy channel handle, flags, requested size, query info output, and channel-private storage.
- `dcopy_device_info_t` registers devinfo node, static callback vector, DMA engine count, max transfer, capabilities, and device id.
- `dcopy_device_handle_t` is the opaque registered-device handle.
- `dcopy_device_register()` and `dcopy_device_unregister()` manage DMA device registration; unregister may return pending until channels drain.
- `dcopy_device_channel_notify()` reports channel events such as command completion to the dcopy framework.

Dependencies:
- Includes public `dcopy.h` and kernel device/list/synchronization types through related headers.
- Implemented by DMA engine drivers and consumed by the dcopy framework.

Research notes:
- The split private state prevents DMA drivers from corrupting framework polling/lifetime fields while still allowing driver-owned command metadata.
- Unregister is asynchronous when clients still hold channels; drivers must wait for `cb_unregister_complete()` before detach is safe.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dcopy_device.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi.h

DDI-conforming driver helper header. It undefines selected kernel macros and replaces them with driver-callable functions or DDI-safe macros for parameters, device numbers, page/block conversions, STREAMS helpers, buffers, and privileges.

Key elements:
- Comments warn drivers to include `sys/ddi.h` after headers that may define macros being undefined here.
- Redefines `min` and `max` as unsigned-expression macros so drivers avoid signed-only kernel functions.
- Defines `drv_getparm()` parameter selectors such as time, process, process group, lbolt, syscall counters, parent/session IDs, and credentials.
- Declares DDI driver utility functions for get/set parameter, microsecond waits, hz/usec conversion, delay, timed waits, major-number conversion, and privilege checking.
- Undefines device-number macros from `sysmacros.h` and declares function forms for external/internal major/minor extraction, device construction, compression, and expansion.
- Undefines block/page conversion macros and declares function forms for `btop`, `btopr`, and `ptob`.
- Undefines STREAMS queue/data macros and declares function forms for `OTHERQ`, `RD`, `WR`, `SAMESTR`, and `datamsg`.
- Declares buffer-header allocation/free helpers `getrbuf()` and `freerbuf()`.
- Kernel-only portion defines `NOPAGE`, typedefs `ppid_t`, and declares `kvtoppid()` and `qassociate()`.

Dependencies:
- Includes system types, map, buffer, uio, and STREAMS headers.
- Consumed broadly by DDI-compliant drivers to get stable function interfaces instead of private macros.

Research notes:
- This header deliberately changes macro/function binding depending on include order; incorrect ordering can alter compilation.
- It is compatibility glue between old macro-heavy kernel headers and the DDI driver ABI.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_hp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_hp.h

Public DDI hotplug support definitions. It defines hotplug connection states, connection types, connection metadata, dependency numbering, property buffer payloads, and 32-bit property compatibility structure.

Key elements:
- Hotplug connection state enum covers empty, present, powered, enabled, virtual-port empty/present, offline, attached, maintenance, and online states.
- Connection type enum distinguishes virtual ports, PCI slots, and PCI Express slots.
- Defines the type string for virtual ports and `DDI_HP_CN_NUM_NONE` for no same-parent dependency.
- `ddi_hp_cn_info_t` describes a connector or port: name, number, dependency number, type, type string, optional child device for ports, current state, and last-change time.
- `ddi_hp_property_t` carries an nvlist buffer pointer and size for hotplug property get/set operations.
- `_SYSCALL32` block defines `ddi_hp_property32_t` with 32-bit pointer and size fields.

Dependencies:
- Uses `dev_info_t`, `time32_t`, and 32-bit syscall types from surrounding kernel/DDI headers.
- Implemented by DDI hotplug core and bus nexus drivers.

Research notes:
- The state enum uses spaced hex values, making states easy to classify by range and stable for external reporting.
- A connection can be a connector or a port; `cn_child` being non-null identifies the child device only for ports.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_hp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_hp_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_hp_impl.h

Private DDI hotplug implementation header. It defines sync/async request flags, registered connection handles, async event entries, bus hotplug operation commands, connector/port dispatch macros, sysevent subclasses, list helpers, and internal helper prototypes.

Key elements:
- Request flags distinguish synchronous and asynchronous hotplug requests.
- `DDI_HP_IS_VIRTUAL_PORT()` tests whether a connection handle represents a virtual port.
- `ddi_hp_cn_handle_t` links a devinfo node to its `ddi_hp_cn_info_t` and to the next registered connector/port.
- `ddi_hp_cn_async_event_entry_t` stores async event target dip, connection name, and requested target state.
- `ddi_hp_op_t` enumerates bus hotplug operations: get/change state, probe/unprobe, get/set property, create port, and remove port.
- `DDIHP_CN_OPS()` dispatches operations to port or connector handlers based on connection type.
- `NEXUS_HAS_HP_OP()` checks whether a nexus driver has a bus ops vector new enough to provide `bus_hp_op`.
- Sysevent subclasses distinguish state-change events and hotplug requests.
- `DDIHP_LIST_APPEND` and `DDIHP_LIST_REMOVE` manipulate simple singly linked handle lists.
- Declares internal functions for modctl entry, connection-name lookup, state retrieval, port/connector ops, sysevent generation, and connection unregister.

Dependencies:
- Depends on public `ddi_hp.h`, DDI devinfo internals through `DEVI()`, bus ops revisions, and sysevent infrastructure.
- Used only in kernel hotplug implementation code.

Research notes:
- Dispatch splits virtual-port behavior from physical connector behavior while presenting a shared operation enum.
- The list macros are unguarded by locking; callers must provide synchronization around connection handle lists.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_hp_impl.h -->