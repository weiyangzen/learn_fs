# Research: subset-b-005214

This grouped report covers the exact source files assigned to `subset-b-005214`. Each section is bounded by reconciliation markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ccamisc.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ccamisc.c

## Purpose
`zcrypt_ccamisc.c` implements exported helper routines for CCA secure-key handling used by the s390 zcrypt core and pkey consumers. It builds CCA CPRBX request/reply buffers, sends them through `zcrypt_send_cprb()`, validates CCA AES DATA, AES CIPHER, and ECC token formats, derives protected keys, queries CCA facility state, and scans AP queues for CCA-capable APQNs matching master-key constraints.

## Important APIs, Types, And Functions
The externally visible functions are `cca_check_secaeskeytoken()`, `cca_check_secaescipherkey()`, `cca_check_sececckeytoken()`, `cca_genseckey()`, `cca_clr2seckey()`, `cca_sec2protkey()`, `cca_gencipherkey()`, `cca_clr2cipherkey()`, `cca_cipher2protkey()`, `cca_ecc2protkey()`, `cca_query_crypto_facility()`, `cca_get_info()`, `cca_findcard2()`, `zcrypt_ccamisc_init()`, and `zcrypt_ccamisc_exit()`. Internal helpers include `alloc_and_prep_cprbmem()`, `free_cprbmem()`, `prep_xcrb()`, and `_ip_cprb_helper()`. The file relies heavily on token layouts from `zcrypt_ccamisc.h`, AP queue status from `zcrypt_api.h`, and type-6 CPRB dispatch from `zcrypt_msgtype6.h`.

## Control Flow
Most operations allocate one contiguous buffer for request CPRB, request parameter block, reply CPRB, and reply parameter block. The request CPRB is initialized as a T2 CPRBX, `prep_xcrb()` wraps it in an `ica_xcRB`, `zcrypt_send_cprb()` submits it, and reply code/reason code checks gate parsing of the returned parameter block. Key-generation/import functions build different CCA service requests: `KG` for random AES DATA keys, `CM` for clear AES DATA import, `US` for secure-to-protected unwrap, `GK` for AES CIPHER generation, multi-step `IP` for AES CIPHER import, `AU` for AES CIPHER/ECC protected-key export, and `FQ` for facility queries. `cca_get_info()` issues `STATICSA` and `STATICSB` facility queries, while `cca_findcard2()` iterates the preallocated device-status table and filters queues by online state, CCA function bit, card/domain, hardware type, and master-key verification patterns.

## State And Persistence
The file owns two module-lifetime resources: `cprb_mempool` for no-allocation or short-term CPRB buffers, and `dev_status_mem` for serialized APQN scans. Sensitive request buffers are scrubbed before freeing when clear key material or derived protected key material may be present. No persistent on-disk state exists; observable state is AP queue status and adapter master-key state returned by firmware.

## Dependencies And Integration Points
This code integrates with the AP bus through `zcrypt_send_cprb()`, with pkey through exported secure/protected key helpers, with debug via `ZCRYPT_DBF_*`, and with zcrypt status calls through `zcrypt_device_status_ext()` and `zcrypt_device_status_mask_ext()`. It assumes CCA CPRB formats and CCA service function semantics.

## Risks And Test Signals
Primary risks are structure packing/length mismatches, unchecked firmware reply shape beyond local plausibility tests, endian/alignment sensitivity in embedded CCA fields, buffer-size mismatches in caller-supplied key buffers, and serialization bottlenecks around `dev_status_mem_mutex`. Good test signals include invalid token rejection, correct `-EINVAL`/`-EIO`/`-EBUSY` mapping, CPRB mempool operation under `ZCRYPT_XFLAG_NOMEMALLOC`, successful key generation/import/unwrap on CCA APQNs, master-key filtering in `cca_findcard2()`, and memory-scrub paths for clear-key operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ccamisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ccamisc.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ccamisc.h

## Purpose
`zcrypt_ccamisc.h` is the public local interface for CCA helper logic. It defines CCA token type/version constants, packed views of CCA AES DATA, AES CIPHER, and ECC private key tokens, CCA AES CIPHER export-control bits, the `cca_info` facility-state structure, and prototypes for the helper functions implemented in `zcrypt_ccamisc.c`.

## Important APIs, Types, And Functions
Important types are `struct keytoken_header`, `struct secaeskeytoken`, `struct cipherkeytoken`, `struct eccprivkeytoken`, and `struct cca_info`. Important constants include `TOKTYPE_NON_CCA`, `TOKTYPE_CCA_INTERNAL`, `TOKTYPE_CCA_INTERNAL_PKA`, `TOKVER_CCA_AES`, `TOKVER_CCA_VLSC`, `MAXCCAVLSCTOKENSIZE`, and the `KMF1_XPRT_*` bit definitions. Function prototypes expose token validation, CCA key generation/import, secure-to-protected conversion, crypto-facility query, APQN selection, and module init/exit routines.

## Control Flow
The header has no executable control flow, but it defines the contract used by pkey and zcrypt call sites. Callers validate token buffers with the check helpers before extracting fields, then use the generate/import/unwrap/query APIs with card/domain selectors and optional `ZCRYPT_XFLAG_*` flags. `cca_findcard2()` communicates APQN matches by updating an input/output count and filling a caller-provided `u32` array.

## State And Persistence
The header declares `struct cca_info`, which is a transient in-memory snapshot of hardware type, master-key states, master-key verification patterns, and adapter serial number. It does not define persistent storage.

## Dependencies And Integration Points
It includes `asm/zcrypt.h`, `asm/pkey.h`, and `zcrypt_api.h`, making it a bridge between architecture zcrypt ioctls, pkey key types, and the zcrypt internal queue/device model. Packed token layouts are ABI-sensitive because they are cast over opaque firmware-generated key blobs.

## Risks And Test Signals
Risks are accidental layout drift, token-version confusion, and callers using these structs on undersized buffers. Test signals include compile-time structure consumers, token validation against known CCA samples, key-size mapping checks for AES 128/192/256, and APQN discovery tests that inspect the `cca_info` fields populated by `cca_get_info()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ccamisc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2a.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2a.c

## Purpose
This source file is zero bytes in the researched snapshot. It does not implement a CEX2A driver in this tree.

## Important APIs, Types, And Functions
No APIs, types, functions, macros, or module metadata are present.

## Control Flow
There is no executable control flow.

## State And Persistence
There is no state, allocation, registration, or persistence behavior in this file.

## Dependencies And Integration Points
There are no includes or direct integration points. Historical or upstream CEX2A support, if any, is not represented by this local file; active accelerator handling in this subset is implemented by `zcrypt_cex4.c` plus message type 50.

## Risks And Test Signals
The main risk is build-system or documentation assumptions that expect this file to contain legacy CEX2A logic. Test signals are simple: the file contributes no object code, and any required CEX2A behavior must be verified elsewhere in the tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2a.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2a.h

## Purpose
This header is zero bytes in the researched snapshot. It declares no CEX2A interface.

## Important APIs, Types, And Functions
No declarations, include guards, constants, structs, or prototypes are present.

## Control Flow
Headers have no runtime control flow, and this one has no preprocessor behavior either.

## State And Persistence
No state or persistence contract is defined.

## Dependencies And Integration Points
There are no includes and no direct compile-time integration points. Code that requires accelerator support in this subset uses `zcrypt_msgtype50.h` and the CEX4+ registration path instead.

## Risks And Test Signals
The notable risk is stale include references from older code. A clean build or `rg "zcrypt_cex2a.h"` can confirm whether this empty header is unused or a placeholder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2c.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2c.c

## Purpose
This source file is zero bytes in the researched snapshot. It contains no CEX2C coprocessor implementation.

## Important APIs, Types, And Functions
No symbols are defined or exported.

## Control Flow
There is no executable control flow.

## State And Persistence
No state, allocations, registration paths, or persistent behavior exist in this file.

## Dependencies And Integration Points
There are no includes or direct dependencies. CCA coprocessor request handling in this subset is represented by `zcrypt_msgtype6.c`, `zcrypt_ccamisc.c`, and the CEX4+ queue registration path rather than this placeholder file.

## Risks And Test Signals
The main risk is assuming legacy CEX2C behavior lives here. Build and symbol-reference checks should verify that no object depends on content from this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2c.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2c.h

## Purpose
This header is zero bytes in the researched snapshot. It declares no CEX2C interface.

## Important APIs, Types, And Functions
No declarations are present.

## Control Flow
There is no preprocessor or runtime flow.

## State And Persistence
The file defines no state contract.

## Dependencies And Integration Points
There are no includes. Any active CCA/coprocessor integration in this subset is through message type 6 and CEX4+ registration headers.

## Risks And Test Signals
Risk is limited to stale assumptions or dead includes. Test with build coverage and reference search.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex4.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex4.c

## Purpose
`zcrypt_cex4.c` registers AP bus card and queue drivers for CEX4 through CEX8 crypto hardware. It normalizes device metadata for accelerator, CCA coprocessor, and EP11 personality modes, attaches zcrypt card/queue objects, selects the right message type implementation, and exposes CCA/EP11 sysfs attributes.

## Important APIs, Types, And Functions
The module exports init/exit through `zcrypt_cex4_init()` and `zcrypt_cex4_exit()`. Internal probes are `zcrypt_cex4_card_probe()` and `zcrypt_cex4_queue_probe()`, with matching remove functions. Sysfs show routines include CCA serial and MKVP views plus EP11 API ordinal, firmware version, serial number, operational modes, wrapping-key verification patterns, and queue op modes. AP device ID tables match CEX4, CEX5, CEX6, CEX7, and CEX8 card and queue devices.

## Control Flow
On module init, the card driver is registered first; the queue driver is registered second, and card registration is unwound on queue-driver failure. Card probe allocates a `zcrypt_card`, stores it as driver data, classifies hardware via `ac->hwinfo.accel`, `cca`, or `ep11`, assigns type strings, user-space compatibility type, speed-rating tables, and RSA modulus limits, then calls `zcrypt_card_register()`. Depending on personality, it creates a CCA or EP11 card sysfs group. Queue probe allocates a `zcrypt_queue`, selects message type 50 for accelerators, type 6 default for CCA, or type 6 EP11 variant for EP11, initializes AP queue state/reply buffer and timeout, registers the queue, and adds matching queue sysfs attributes.

## State And Persistence
State is kernel-resident device state: `zcrypt_card`, `zcrypt_queue`, sysfs attributes, AP queue timeout, online flag, load counter, and speed tables. No on-disk persistence exists. Remove paths unregister sysfs groups and zcrypt objects.

## Dependencies And Integration Points
This file integrates the AP bus with zcrypt core (`zcrypt_card_*`, `zcrypt_queue_*`), message handlers (`zcrypt_msgtype50`, `zcrypt_msgtype6`), CCA info helpers, EP11 info helpers, and sysfs. Compatibility mappings intentionally report newer CEX7/CEX8 and CCA cards as older user-space types for legacy ioctl behavior.

## Risks And Test Signals
Risks include incorrect hardware-personality classification, sysfs group leaks on partial failure, stale speed ratings, and compatibility type regressions. Test signals include AP hotplug probe/remove, sysfs attribute reads on CCA and EP11 devices, queue operation routing by hardware mode, failure injection around `sysfs_create_group()`, and module init unwind when queue driver registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex4.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex4.h

## Purpose
`zcrypt_cex4.h` is the small local header for the CEX4+ AP driver module. It exposes module lifecycle functions to the rest of the zcrypt build.

## Important APIs, Types, And Functions
The header declares `zcrypt_cex4_init()` and `zcrypt_cex4_exit()`. It has a conventional include guard and no data structures.

## Control Flow
There is no runtime control flow. The declarations correspond to driver registration and unregistration in `zcrypt_cex4.c`.

## State And Persistence
No state is defined in the header. Module state is owned by the source file and zcrypt/AP subsystems.

## Dependencies And Integration Points
Consumers can include this header to call CEX4+ initialization or teardown from aggregate zcrypt initialization paths. In this snapshot, the source also uses `module_init()`/`module_exit()`.

## Risks And Test Signals
Risk is limited to declaration/signature drift relative to `zcrypt_cex4.c`. Build coverage catches mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cex4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_debug.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_debug.h

## Purpose
`zcrypt_debug.h` centralizes zcrypt debug-facility levels, convenience macros, the global debug handle declaration, and debug subsystem lifecycle prototypes.

## Important APIs, Types, And Functions
It defines `DBF_ERR`, `DBF_WARN`, `DBF_INFO`, `DBF_DEBUG`, helper mappings `RC2ERR()` and `RC2WARN()`, maximum sprintf argument metadata, and wrappers `ZCRYPT_DBF()`, `ZCRYPT_DBF_ERR()`, `ZCRYPT_DBF_WARN()`, and `ZCRYPT_DBF_INFO()`. It declares `extern debug_info_t *zcrypt_dbf_info`, `zcrypt_debug_init()`, and `zcrypt_debug_exit()`.

## Control Flow
The macros directly invoke `debug_sprintf_event()` against `zcrypt_dbf_info`; callers control when and at which level events are emitted. There is no branching logic except the `RC2*` level selection helpers.

## State And Persistence
The global debug handle is external state managed by the zcrypt debug implementation. Debug records are kernel debug-facility records, not persistent repository state.

## Dependencies And Integration Points
The header depends on `asm/debug.h` and is included broadly by zcrypt helpers, message handlers, error conversion, and queue management. It standardizes log severity across this driver family.

## Risks And Test Signals
Risks include using debug macros before initialization, format/argument mismatches, and overly noisy logs at high-frequency paths. Build-time format checking is limited because these are macros; runtime signals include debugfs/debug facility output and clean init/exit of the global debug area.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ep11misc.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ep11misc.c

## Purpose
`zcrypt_ep11misc.c` implements EP11 helper services used by zcrypt and pkey. It validates EP11 AES/ECC key blobs, queries EP11 card/domain information, generates AES key blobs, imports clear AES keys through a temporary KEK and unwrap operation, derives protected keys from EP11 AES/ECC blobs, and scans APQNs for EP11 capability and wrapping-key matches.

## Important APIs, Types, And Functions
Exported APIs are `ep11_kb_wkvp()`, `ep11_check_aes_key_with_hdr()`, `ep11_check_ecc_key_with_hdr()`, `ep11_check_aes_key()`, `ep11_get_card_info()`, `ep11_get_domain_info()`, `ep11_genaeskey()`, `ep11_clr2keyblob()`, `ep11_kblob2protkey()`, `ep11_findcard2()`, plus init/exit. Internal helpers split/decode key blobs (`ep11_kb_split()`, `ep11_kb_decode()`), allocate EP11 CPRBs, write short ASN.1-like tags, prepare payload/URB headers, validate reply CPRB/payloads, perform generic info queries, single encrypt/decrypt operations, key unwrap, and key wrap.

## Control Flow
EP11 requests are built as `struct ep11_cprb` plus payload. `prep_head()` writes the outer sequence and function/domain fields; `prep_urb()` wraps request and reply CPRBs for `zcrypt_send_ep11_cprb()`. Reply handling first checks CPRB `ret_code`, then validates the payload sequence, function/domain fields, and embedded return value. Key generation chooses API ordinal V4 by default for extractable protected-key-capable blobs, V1 when flags do not request newer behavior, and V6 with an empty pinblob in secure-execution guests. Clear-key import generates a temporary AES-256 KEK, encrypts the clear key using CBC padding and a fixed IV, then unwraps the encrypted key into the requested EP11 blob. Protected-key derivation calls EP11 wrap with `CKM_IBM_CPACF_WRAP` and parses the returned protected-key info.

## State And Persistence
The file owns an EP11 CPRB mempool and a serialized device-status buffer for `ep11_findcard2()`. Sensitive request, reply, temporary KEK, encrypted key, and wrapped-key buffers are scrubbed where relevant before freeing. No disk persistence exists; durable cryptographic state remains on AP hardware.

## Dependencies And Integration Points
It depends on AP/zcrypt dispatch through `zcrypt_send_ep11_cprb()`, pkey constants for protected key types, token constants shared with CCA helpers, `ap_is_se_guest()` for secure-execution behavior, and AES block sizing. `zcrypt_cex4.c` uses the card/domain info APIs for sysfs.

## Risks And Test Signals
Risks include ASN.1 length handling limited to two-byte lengths, firmware reply parsing assumptions, fixed IV use for the internal KEK wrapping sequence, accidental mutation of old-style EP11 header overlay in `ep11_kblob2protkey()`, and mempool pressure under no-allocation callers. Test signals include validation of old/new AES and ECC blob headers, EP11 query parsing, API ordinal selection in secure-execution guests, clear-key import round trips, protected-key export for AES and ECC, and APQN filtering by API ordinal and WKVNP/WKVP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ep11misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ep11misc.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ep11misc.h

## Purpose
`zcrypt_ep11misc.h` defines the local public interface for EP11 helper functionality. It exposes API ordinal constants, EP11 key-blob version constants, key-blob layouts, card/domain info structs, validation routines, key generation/import/conversion functions, APQN discovery, and lifecycle hooks.

## Important APIs, Types, And Functions
Important constants are `EP11_API_V1`, `EP11_API_V4`, `EP11_API_V6`, `EP11_STRUCT_MAGIC`, `EP11_BLOB_PKEY_EXTRACTABLE`, `TOKVER_EP11_AES`, `TOKVER_EP11_AES_WITH_HEADER`, and `TOKVER_EP11_ECC_WITH_HEADER`. `struct ep11keyblob` describes the firmware key blob payload with a union for old-style session/header overlay, WKVNP/WKVP, attributes, mode, magic, IV, encrypted key data, and MAC. `struct ep11_card_info` and `struct ep11_domain_info` are query result contracts.

## Control Flow
The inline `is_ep11_keyblob()` checks the magic value and is used by decode logic in the implementation. Other declarations form call paths for checking blobs, querying cards/domains, generating AES blobs, importing clear keys, finding matching APQNs, and deriving protected keys.

## State And Persistence
The header defines transient in-memory views of EP11 key blobs and hardware info. It does not own storage or persistent state.

## Dependencies And Integration Points
It includes `asm/zcrypt.h` and `asm/pkey.h`, connecting EP11 helpers to zcrypt request types and pkey protected-key typing. CEX4 sysfs and pkey code are natural consumers.

## Risks And Test Signals
Risks include packed-layout drift, old-style header overlay confusion, and callers treating `is_ep11_keyblob()` as sufficient validation without length checks. Tests should cover all accepted token versions, extractability-flag enforcement, and query result formatting in CEX4 sysfs attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ep11misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_error.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_error.h

## Purpose
`zcrypt_error.h` defines common AP error reply structures and maps firmware reply codes from type 82/type 88/type 86 contexts into Linux errno values for zcrypt message handlers.

## Important APIs, Types, And Functions
The central type is `struct error_hdr`, containing response type and reply code. The file defines response-type constants `TYPE82_RSP_CODE` and `TYPE88_RSP_CODE`, many `REP82_*` and `REP88_*` reply-code constants, and the inline `convert_error()` helper.

## Control Flow
`convert_error()` reads the error header from `reply->msg`, obtains card and queue numbers for diagnostics, and switches on `reply_code`. Request formatting, operand, malformed-message, invalid-domain-pending, hypervisor-filtered, and similar client-side errors map to `-EINVAL`. Machine failure, message-type mismatch, transport failure, and unknown retry-worthy errors map to `-EAGAIN`. Type 86 transport/filter cases include AP final status in debug output when available.

## State And Persistence
The header mutates no state directly. It emits debug events and returns errno values that may cause higher layers to retry, rescan, or mark queues offline depending on caller logic.

## Dependencies And Integration Points
It includes `zcrypt_debug.h`, `zcrypt_api.h`, and `zcrypt_msgtype6.h`. It is used by message type 50 and type 6 response conversion paths to keep error mapping consistent.

## Risks And Test Signals
Risks include firmware reply-code changes not reflected in the mapping, over-broad `-EAGAIN` causing retries for permanent failures, and incorrect type 86 overlay assumptions when logging APFS. Test signals include synthetic type 82/88 replies through both message handlers, debug output for hypervisor filtering and transport failures, and retry behavior at the zcrypt dispatcher.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype50.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype50.c

## Purpose
`zcrypt_msgtype50.c` implements zcrypt operations for accelerator-style CEXxA message type 50 RSA modular exponentiation and CRT requests. It converts user ICA request structures into fixed type-50 AP messages, waits for AP completion, converts type-80 replies back to user buffers, and registers a `zcrypt_ops` implementation.

## Important APIs, Types, And Functions
Important internal wire types include `type50_hdr`, `type50_meb[1-3]_msg`, `type50_crb[1-3]_msg`, and `type80_hdr`. Exported helper functions `get_rsa_modex_fc()` and `get_rsa_crt_fc()` classify request sizes into dispatcher function codes. Main operation callbacks are `zcrypt_msgtype50_modexpo()` and `zcrypt_msgtype50_modexpo_crt()`. Lifecycle functions register/unregister `zcrypt_msgtype50_ops`.

## Control Flow
For modexpo, `ICAMEX_msg_to_type50MEX_msg()` chooses 128, 256, or 512 byte operand slots based on `inputdatalength`, right-aligns modulus, exponent, and message, and copies user buffers into the AP message. For CRT, `ICACRT_msg_to_type50CRT_msg()` similarly chooses CRB format, derives half-size CRT fields, uses the documented adjustment offset for selected operands, and enforces 4K CRT only when the zcrypt card says it supports 512-byte modulus. Send callbacks set the receive function, generate a PSMID from current PID and an atomic sequence, queue the AP message, wait interruptibly, cancel on signal, and convert the reply. Response conversion dispatches type 82/88 to `convert_error()` and type 80 to `convert_type80()`.

## State And Persistence
The file keeps only the static registered ops object and an atomic PSMID sequence. Queue online state can be changed to offline on impossible short or unknown replies. No persistent storage exists.

## Dependencies And Integration Points
It integrates with AP queueing (`ap_queue_message()`, `ap_cancel_message()`), zcrypt queue/card metadata, user-copy helpers, common error conversion, and zcrypt message-type registration. CEX4+ queue probe selects this ops variant for accelerator hardware.

## Risks And Test Signals
Risks include user pointer copy failures, operand length boundary errors, response length mismatches, queue-offline side effects on malformed replies, and compatibility behavior for 4K CRT support. Tests should cover 0/129/257/513-byte boundaries, CRT short length calculation, type 80 copyback, type 82/88 mapping, interrupt cancellation, and registration lookup by name/variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype50.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype50.h

## Purpose
`zcrypt_msgtype50.h` declares the public local contract for the message type 50 accelerator operations.

## Important APIs, Types, And Functions
It defines `MSGTYPE50_NAME`, `MSGTYPE50_VARIANT_DEFAULT`, `MSGTYPE50_CRB3_MAX_MSG_SIZE`, and `MSGTYPE_ADJUSTMENT`. It declares `get_rsa_modex_fc()`, `get_rsa_crt_fc()`, `zcrypt_msgtype50_init()`, and `zcrypt_msgtype50_exit()`.

## Control Flow
No runtime control flow is present. The constants guide buffer sizing, operation lookup, and user-request classification performed by `zcrypt_msgtype50.c` and the broader dispatcher.

## State And Persistence
No state is defined.

## Dependencies And Integration Points
The prototypes depend on `struct ica_rsa_modexpo` and `struct ica_rsa_modexpo_crt` from architecture zcrypt headers included by consumers. CEX4 accelerator queues use the name and variant to select these operations.

## Risks And Test Signals
Risks are signature drift and incorrect maximum message size if wire structures change. Build coverage and boundary tests around 4K CRB3 requests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype6.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype6.c

## Purpose
`zcrypt_msgtype6.c` implements message type 6 operations for CEXxC CCA coprocessors and CEXxP EP11 adapters. It handles RSA modexpo/CRT through CCA CPRBX frames, generic CCA `send_cprb`, EP11 `send_ep11_cprb`, hardware RNG requests, reply conversion, speed-index classification, and registration of default and EP11 zcrypt ops variants.

## Important APIs, Types, And Functions
Visible helper APIs are `speed_idx_cca()`, `speed_idx_ep11()`, `prep_cca_ap_msg()`, `prep_ep11_ap_msg()`, `prep_rng_ap_msg()`, `zcrypt_msgtype6_init()`, and `zcrypt_msgtype6_exit()`. Key internal functions convert ICA MEX/CRT to type 6, convert generic XCRB and EP11 URB requests to AP messages, convert type 86 replies for ICA/XCRB/EP11/RNG, receive tasklet callbacks, and send queued requests. Important wire views include `type86x_reply`, `type86_ep11_reply`, and embedded CPRBX/EP11 CPRB payload overlays.

## Control Flow
RSA paths build type 6 CCA messages using static headers, static CPRBX values, and function/rule blocks (`PK`/`MRP` for modexpo, `PD`/`ZERO-PAD` for CRT), copy input data from user space, append encoded keys, queue the AP message, and copy response data back after type 86 conversion. Generic CCA XCRB preparation aligns control/data lengths, checks overflow, copies request CPRB/data from user or kernel address space, extracts function code/domain, and sets AP message flags for usage/admin/special handling. EP11 preparation validates CPRB/payload length formats, extracts the EP11 function ID, marks admin/usage, and later rewrites non-management target domain fields to the queue domain before sending. RNG preparation builds an `RL`/`RANDOM` CPRB and returns copied random data from type 86 count2.

## State And Persistence
The file keeps static registered ops and an atomic PSMID sequence. It can mark queues offline and emit uevents on unknown or firmware-failure replies. It also dynamically lowers `zcard->max_exp_bit_length` on a specific CCA error for large-exponent requests, influencing future dispatch behavior. No on-disk persistence exists.

## Dependencies And Integration Points
It depends on AP queueing, zcrypt queue/card structures, common error conversion, CCA key encoding helpers from `zcrypt_cca_key.h`, architecture zcrypt request structs, and EP11/CCA callers that use `zcrypt_send_cprb()` and `zcrypt_send_ep11_cprb()` through the zcrypt API. CEX4 queue probe selects the default or EP11 variant based on hardware personality.

## Risks And Test Signals
Risks include alignment and integer overflow errors in XCRB sizing, incorrect user/kernel copy mode, reply length/count trust, domain rewrite mistakes for EP11 management vs usage commands, retry semantics for administrative requests, and queue-offline side effects on unexpected responses. Tests should cover CCA and EP11 prepared-message extraction, AP message flags, oversize request rejection, interrupted waits and cancellation, type 82/86/87/88 response mapping, RNG count handling, and speed-index classification for known function codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype6.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype6.h

## Purpose
`zcrypt_msgtype6.h` defines the local public interface and wire headers for zcrypt message type 6 CCA/EP11 handling.

## Important APIs, Types, And Functions
It defines message type names and variants (`MSGTYPE06_NAME`, default, no-RNG, EP11), `struct type6_hdr`, `struct type86_hdr`, `struct type86_fmt2_ext`, response constants `TYPE86_RSP_CODE`, `TYPE87_RSP_CODE`, `TYPE86_FMT2`, speed classes `LOW`, `MEDIUM`, `HIGH`, and prototypes for CCA, EP11, and RNG AP message preparation, speed indexing, and lifecycle registration.

## Control Flow
No executable logic exists in the header, but the wire structs define how the implementation interprets AP request/reply offsets, lengths, function codes, AP final status, and payload counts. Callers prepare AP messages through the declared helpers before dispatching through selected `zcrypt_ops`.

## State And Persistence
No state is owned by the header.

## Dependencies And Integration Points
It includes `asm/zcrypt.h` for CPRB/URB request types. The header is shared by error conversion, CCA/EP11 misc helpers, and queue/message dispatch code.

## Risks And Test Signals
Risks are packed-wire-layout drift and response constant misuse. Compile-time consumers plus integration tests with real or synthetic type 6/type 86 frames are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_msgtype6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_queue.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_queue.c

## Purpose
`zcrypt_queue.c` implements shared zcrypt queue-device lifetime, common queue sysfs attributes, online/offline behavior, load reporting, registration into the zcrypt card queue list, and cleanup.

## Important APIs, Types, And Functions
Externally visible functions are `zcrypt_queue_force_online()`, `zcrypt_queue_alloc()`, `zcrypt_queue_free()`, `zcrypt_queue_get()`, `zcrypt_queue_put()`, `zcrypt_queue_register()`, and `zcrypt_queue_unregister()`. Sysfs handlers implement `online` read/write and `load` read. Internal release is handled by `zcrypt_queue_release()`.

## Control Flow
Allocation zeroes a `zcrypt_queue`, allocates a reply buffer sized by the card/driver caller, initializes the list and refcount, and returns the queue. Registration takes the global zcrypt list lock, finds the parent `zcrypt_card` from AP card driver data, increments the card refcount, links the queue into the card queue list, creates the sysfs group, and adds the hardware RNG device when the selected ops provide `.rng`. Unregistration removes the queue from the list, removes RNG support and sysfs, drops the parent card, and releases the queue ref. The `online` store path validates requested values and underlying AP/card config/checkstop state, refuses online if parent zcrypt card is offline, updates `zq->online`, emits an AP online uevent, and flushes queued AP messages when transitioning offline.

## State And Persistence
The file manages in-memory queue state: reply buffer, list node, refcount, online flag, load counter, parent card pointer, and sysfs attributes. No persistent storage exists.

## Dependencies And Integration Points
It depends on zcrypt global list locking and card refcounting, AP queue/card state, AP uevents and flushing, sysfs, and optional zcrypt RNG device registration. CEX card/queue probe paths call these routines.

## Risks And Test Signals
Risks include refcount/list imbalance on registration failure, sysfs lifecycle mismatches, racing online changes with AP queue operations, and failure to flush when offline. Test signals include allocation failure injection, register/unregister cycles, sysfs online validation, uevent emission, AP flush on offline, and RNG add/remove symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/s390/net/Kconfig

## Purpose
This Kconfig file defines the s390 network-device driver menu and configuration symbols for CTCM, VM special-message IUCV support, qeth Ethernet/HiperSockets support, CCWGROUP aggregation, and ISM vPCI adapter support.

## Important APIs, Types, And Functions
Important symbols are `CTCM`, `SMSGIUCV`, `SMSGIUCV_EVENT`, `QETH`, `QETH_L2`, `QETH_L3`, `QETH_OSX`, `CCWGROUP`, and `ISM`. The menu depends on `NETDEVICES && S390`; individual options add dependencies such as `CCW`, `IUCV`, `IP_MULTICAST`, `QDIO`, `ETHERNET`, `BRIDGE`, `PCI`, and `DIBS`.

## Control Flow
Kconfig evaluation controls which drivers are built in, built as modules, or omitted. `CTCM`, `SMSGIUCV`, `QETH`, `QETH_L2`, and `QETH_L3` default to module or built-in values as specified. `QETH_OSX` defaults based on `!HAVE_MARCH_Z15_FEATURES`. `CCWGROUP` is selected by default when CTCM, QETH, or SMC are enabled.

## State And Persistence
The file contributes kernel build configuration state, persisted in `.config`, but has no runtime state itself.

## Dependencies And Integration Points
The companion Makefile consumes these symbols via `obj-$(CONFIG_*)`. Driver help text maps symbols to module names such as `ctcm`, `smsgiucv_app`, `qeth`, `qeth_l2`, `qeth_l3`, and `ism`.

## Risks And Test Signals
Risks include dependency mistakes that expose drivers without required bus/protocol support, default changes that alter s390 kernel footprint, and `CCWGROUP` not matching dependent drivers. Test signals include Kconfig dependency resolution, allyesconfig/allmodconfig builds for s390, and module presence matching selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/Makefile -->
# sources/distributed-fs/ceph-client/drivers/s390/net/Makefile

## Purpose
This Makefile maps s390 network Kconfig symbols to composite objects and modules.

## Important APIs, Types, And Functions
Composite objects include `ctcm-y`, `qeth-y`, `qeth_l2-y`, `qeth_l3-y`, and `ism-y`. Conditional object entries use `obj-$(CONFIG_CTCM)`, `obj-$(CONFIG_SMSGIUCV)`, `obj-$(CONFIG_SMSGIUCV_EVENT)`, `obj-$(CONFIG_QETH)`, `obj-$(CONFIG_QETH_L2)`, `obj-$(CONFIG_QETH_L3)`, and `obj-$(CONFIG_ISM)`.

## Control Flow
During the kernel build, enabled config symbols determine which module or built-in objects are included. `ctcm.o` is built from main, FSM, MPC, sysfs, and debug components plus `fsm.o`; qeth core and layer modules are split into core, L2, and L3 composites; ISM builds from `ism_drv.o`.

## State And Persistence
The file has no runtime state. It affects build artifacts.

## Dependencies And Integration Points
It consumes symbols defined in the same folder's Kconfig and references source/object names under `drivers/s390/net`. `ctcm_dbug.o` is included in `ctcm-y`, linking the debug facility helpers from this subset into the CTCM driver.

## Risks And Test Signals
Risks include object list drift when sources are renamed, missing dependencies when symbols change, and stale composite membership. Test signals are s390 builds across built-in and module configurations and link checks for CTCM/qeth/ISM modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_dbug.c -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_dbug.c

## Purpose
`ctcm_dbug.c` implements debug-facility registration and formatted text logging for the s390 CTCM network driver.

## Important APIs, Types, And Functions
It defines the global `ctcm_dbf` array with six debug areas: setup, error, trace, MPC setup, MPC error, and MPC trace. Public functions are `ctcm_register_dbf_views()`, `ctcm_unregister_dbf_views()`, and `ctcm_dbf_longtext()`.

## Control Flow
Registration iterates all debug areas, calls `debug_register()` with configured name/pages/areas/record length, unwinds all previously registered areas on failure, registers the hex+ASCII view, and sets the configured debug level. Unregistration iterates all areas, calls `debug_unregister()`, and clears IDs. `ctcm_dbf_longtext()` checks whether a level is enabled, formats a variable-argument string into a fixed 64-byte buffer using `vscnprintf()`, and records it with `debug_text_event()`.

## State And Persistence
State is the process-wide `ctcm_dbf` array and debug-facility IDs. Debug records live in the kernel debug facility; there is no source-tree persistence.

## Dependencies And Integration Points
The file includes `ctcm_dbug.h` and Linux debugfs/debug headers. It is linked into the `ctcm` composite module by the s390 net Makefile and provides macros in the header with actual backing debug areas.

## Risks And Test Signals
Risks include partial registration leaks, using macros before successful registration, truncation of long formatted messages to 63 characters plus terminator, and missing error handling for `debug_register_view()`. Test signals include module init/exit under allocation failure, debug area visibility, level filtering, and formatted logging from CTCM and MPC call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_dbug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_dbug.h -->
# sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_dbug.h

## Purpose
`ctcm_dbug.h` defines the CTCM debug-facility interface, debug levels, debug area IDs, metadata structure, function prototypes, and convenience macros used by the CTCM and MPC network driver code.

## Important APIs, Types, And Functions
It defines compile-time flags `do_debug`, `do_debug_ccw`, and `do_debug_data` from `DEBUG`, `DEBUGCCW`, and `DEBUGDATA`. Debug levels mirror kernel severity levels from `CTC_DBF_ALWAYS` through `CTC_DBF_DEBUG`. `enum ctcm_dbf_names` names six debug areas and `struct ctcm_dbf_info` describes each area. Prototypes expose registration, unregistration, and printf-style long text logging. Macros include `CTCM_DBF_TEXT`, `CTCM_DBF_HEX`, `CTCM_DBF_TEXT_`, `CTCM_DBF_DEV_NAME`, `MPC_DBF_DEV_NAME`, `CTCMY_DBF_DEV_NAME`, `CTCM_DBF_DEV`, `MPC_DBF_DEV`, and `CTCMY_DBF_DEV`.

## Control Flow
The macros dispatch directly to debug-facility calls or `ctcm_dbf_longtext()`. `CTCMY_*` macros branch on `IS_MPCDEV(dev)` to choose MPC or non-MPC debug areas. `strtail()` shortens function names for compact logs.

## State And Persistence
The header declares the external `ctcm_dbf` array populated by `ctcm_dbug.c`. It defines no persistent state.

## Dependencies And Integration Points
It depends on `asm/debug.h` and on external CTCM driver context for `IS_MPCDEV()` and valid `net_device` names/pointers in macros. It is the logging surface used throughout the CTCM driver.

## Risks And Test Signals
Risks include macro arguments with side effects, use before debug areas are registered, dependency on `IS_MPCDEV()` being visible at expansion sites, and fixed-size function-name/log formatting. Test signals include compile coverage across debug flag combinations, CTCM and MPC logging call sites, and debug output routing to the expected area.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/net/ctcm_dbug.h -->
