# subset-b-005213 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_ep11.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_ep11.c

Purpose: implements the s390 pkey handler for EP11 secure key material. It recognizes EP11 non-CCA AES/ECC tokens, discovers suitable APQNs, generates EP11 AES secure keys, imports clear AES material into EP11 blobs, converts EP11 blobs into protected keys, verifies tokens, and registers those operations with the pkey core.

Important APIs and functions: `is_ep11_key()` and `is_ep11_keytype()` are pkey handler predicates. `ep11_apqns4key()` and `ep11_apqns4type()` call `ep11_findcard2()` after `zcrypt_wait_api_operational()` to find cards/domains matching EP11 API level, wrapping key verification pattern, and WKVP. `ep11_key2protkey()` validates token layout using `ep11_check_aes_key*()`/`ep11_check_ecc_key_with_hdr()` and calls `ep11_kblob2protkey()` over explicit or discovered APQNs. `ep11_gen_key()` and `ep11_clr2key()` generate secure blobs through `ep11_genaeskey()` and `ep11_clr2keyblob()`. `ep11_verifykey()` reports key subtype, bitsize, matching APQN, and current-MKVP flag. `ep11_slowpath_key2protkey()` turns clear AES tokens into temporary EP11 keys before converting to protected keys.

Control flow: callers enter through the `pkey_handler` table registered at module init. Most paths first reject malformed token headers, unsupported key types, incompatible subtypes, or invalid clear-key lengths. If APQNs are unspecified or wildcarded, the handler discovers candidate EP11 queues; then it iterates candidates until one hardware operation succeeds or all fail.

State and persistence: this file keeps no persistent key state. It uses stack buffers for APQN lists and temporary EP11 blobs. Module lifetime state is only the registered `ep11_handler`; AP hardware state and key wrapping keys live outside this file.

Dependencies and integration: depends on `pkey_base.h`, CCA/EP11 zcrypt helpers, AP bus card types, and secure-execution detection via `ap_is_se_guest()`. It integrates as an optional pkey provider and exposes AP modaliases for CEX4 through CEX8 when built as a module.

Risks: token length and header interpretation are critical because hardware helpers consume binary blobs. Clear-key slow path must honor `PKEY_XFLAG_NOCLEARKEY`; failures would expose policy bypass. APQN discovery is constrained to CEX7/API v4 or v6 for PKEY-extractable blobs, so regressions could silently reduce availability.

Test signals: exercise EP11 AES legacy and with-header tokens, ECC with-header verification, wildcard APQN conversion, explicit APQN fallback, extractable/non-extractable blobs, secure-execution API selection, invalid subtype/keybitsize paths, and clear-key slow path with and without `NOCLEARKEY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_ep11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_pckmo.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_pckmo.c

Purpose: implements the pkey handler backed by the s390 CPACF PCKMO instruction. It supports protected-key tokens and clear-key tokens for AES, AES-XTS, HMAC, and ECC protected-key types where the architecture exposes the needed PCKMO subfunction.

Important APIs and functions: `is_pckmo_key()` accepts non-CCA clear-key and protected-key token versions. `pckmo_clr2protkey()` maps pkey key types to CPACF PCKMO function codes, checks key and output sizes, queries/caches the PCKMO function mask, calls `cpacf_pckmo()`, and returns protected material plus WKVP. `pckmo_verify_protkey()` creates a dummy AES-128 protected key and compares WKVPs to reject keys wrapped under a different wrapping key. `pckmo_key2protkey()` copies existing protected tokens or converts clear tokens, respecting `PKEY_XFLAG_NOCLEARKEY`. `pckmo_gen_protkey()` creates random protected-key material by generating a dummy protected token and replacing the key bytes with random bytes while preserving a valid WKVP. Wrapper callbacks populate `pckmo_handler`.

Control flow: pkey core dispatches into the handler. Conversion validates the token header, token version, key type, embedded length, and output buffer before touching CPACF. Generation validates subtype `PKEY_TYPE_PROTKEY`, supported key type, randomizes clear input, calls PCKMO, then randomizes the protected key portion.

State and persistence: the only retained state is the static `cpacf_mask_t pckmo_functions`, lazily filled by `cpacf_query()`. No key material persists beyond caller buffers and local stack arrays, which are zeroed where temporary protected-key verification material is used.

Dependencies and integration: depends on `asm/cpacf.h`, Linux random APIs, AES WKVP size constants, token formats from zcrypt CCA misc, and pkey handler registration gated by `S390_CPU_FEATURE_MSA`.

Risks: PCKMO function-code mapping must remain exact for all key types. The protected-key verification method trusts WKVP comparison, so tests must catch wrapping-key mismatch handling. Generated protected keys intentionally replace the key bytes after PCKMO, so accidental replacement of the WKVP would make outputs unusable.

Test signals: cover all supported AES, XTS, HMAC, and ECC key types; unsupported subtype/type rejection; short clear key and short output buffer errors; unavailable CPACF subfunction; protected-token WKVP mismatch; `NOCLEARKEY`; and module init on CPUs without PCKMO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_pckmo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_sysfs.c

Purpose: defines the pkey module's read-only binary sysfs attributes for generating fresh protected keys and secure-key blobs. Attributes are grouped into `protkey`, `ccadata`, `ccacipher`, and `ep11`, each returning a fixed-size binary token or padded blob.

Important APIs and functions: `sys_pkey_handler_gen_key()` wraps `pkey_handler_gen_key()` and requests handler modules on `-ENODEV` before retrying. `pkey_protkey_aes_attr_read()`, `pkey_protkey_aes_xts_attr_read()`, and `pkey_protkey_hmac_attr_read()` build protected-key tokens. `pkey_ccadata_aes_attr_read()` generates CCA data key tokens. `pkey_ccacipher_aes_attr_read()` generates CCA cipher key tokens sized by `CCACIPHERTOKENSIZE`. `pkey_ep11_aes_attr_read()` generates EP11 AES blobs padded to `MAXEP11AESKEYBLOBSIZE`. `pkey_attr_groups` exports all attribute groups to the pkey device.

Control flow: sysfs invokes a concrete `*_read()` function for each binary attribute. Each reader rejects partial reads with `off != 0` or too-small `count` because every read generates new random key material. XTS attributes generate two independent tokens/blobs and concatenate them.

State and persistence: no generated key is persisted by this file. State is transient in the sysfs output buffer and local structs. The only durable surface is the attribute table that the pkey core attaches to sysfs.

Dependencies and integration: depends on pkey core generation APIs, CCA/EP11 token constants, `BIN_ATTR_RO`, and Linux sysfs binary attribute semantics. It integrates with handler modules indirectly, causing module-load requests when no handler is available.

Risks: callers must read the full binary object in one read. Size constants are ABI-sensitive because userspace consumes exact token lengths. Any mismatch between attribute size and actual generated length can truncate or expose stale zero padding. XTS handling must avoid returning two copies of the same generated key.

Test signals: read each attribute with exact count, short count, and nonzero offset; verify XTS returns two token-sized outputs; force first `pkey_handler_gen_key()` to return `-ENODEV` and confirm retry after module request; validate fixed sizes for protected, CCA data, CCA cipher, and EP11 outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_uv.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_uv.c

Purpose: provides a pkey handler for Ultravisor secret tokens in protected-virtualization guests. It maps UV secret IDs to retrievable protected-key material and verifies that referenced UV secrets exist with the expected secret type.

Important APIs and functions: `struct uvsecrettoken` defines the non-CCA token layout with version `TOKVER_UV_SECRET`, secret type, length, and UV secret ID. `is_uv_key()` validates token type/version and supported UV secret types. `get_secret_metadata()` serializes access to the preallocated `uv_secret_list` and calls `uv_find_secret()`. `retrieve_secret()` fetches metadata, checks caller buffer length, and calls `uv_retrieve_secret()`. `uv_get_size_and_type()` maps UV secret type to protected-key byte size and pkey key type. `uv_key2protkey()` retrieves the secret and fills pkey output. `uv_verifykey()` checks metadata and reports pkey type, bit size, and underlying pkey type in `flags`.

Control flow: module init only succeeds in protected-virtualization guests with UV retrieve-secret support. Handler calls validate the token, compute expected size/type, retrieve metadata, then retrieve or verify the secret ID. Exit unregisters the handler and frees the preallocated list under the mutex.

State and persistence: `uv_list` is a module-lifetime scratch buffer shared by `uv_find_secret()` and protected by `uv_list_mutex`. Actual secrets persist in UV-managed storage, not in this driver. Retrieved protected key bytes are returned to the caller buffer only.

Dependencies and integration: depends on `asm/uv.h`, CPU feature `S390_CPU_FEATURE_UV`, `is_prot_virt_guest()`, `uv_info.inst_calls_list`, and the pkey handler interface. It integrates UV secret retrieval with the normal pkey protected-key conversion API.

Risks: `uv_key2protkey()` assumes callers passed a valid token; incorrect dispatch could read fields before full validation. The shared `uv_list` must remain serialized to avoid metadata races. Size/type mapping is security-relevant because it controls output buffer requirements and algorithm identification.

Test signals: run init gating for non-PV guests, PV guests without retrieve-secret, and allocation failure; verify every supported UV secret type maps to expected protected-key size/type; test missing secret ID, mismatched metadata type, short output buffer, and concurrent verify/retrieve calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/pkey_uv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_debug.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_debug.h

Purpose: supplies the VFIO AP driver's s390 debug feature levels and convenience macros. It centralizes calls to `debug_sprintf_event()` so driver code can emit structured debug records through the shared `vfio_ap_dbf_info` handle.

Important APIs and functions: defines debug levels `DBF_ERR`, `DBF_WARN`, `DBF_INFO`, and `DBF_DEBUG`, plus `DBF_MAX_SPRINTF_ARGS`. Macros `VFIO_AP_DBF`, `VFIO_AP_DBF_ERR`, `VFIO_AP_DBF_WARN`, `VFIO_AP_DBF_INFO`, and `VFIO_AP_DBF_DBG` wrap `debug_sprintf_event()` with fixed levels. The header declares external `debug_info_t *vfio_ap_dbf_info`.

Control flow: no executable control flow beyond macro expansion. Runtime behavior depends on `vfio_ap_drv.c` registering the debug area before VFIO AP operations call the macros.

State and persistence: this header owns no state. The debug area pointer is allocated, configured, and unregistered by the driver module.

Dependencies and integration: includes `asm/debug.h` and is consumed by VFIO AP driver and operations files. It integrates kernel debug feature logging with mdev, queue, interrupt, and configuration paths.

Risks: macros assume `vfio_ap_dbf_info` is valid. Calls before debug initialization or after unregister would be unsafe, so module init/exit ordering matters. `DBF_MAX_SPRINTF_ARGS` must stay aligned with registered debug entry size.

Test signals: build coverage for all macro users, module init failure paths that avoid later macro use, and dynamic debug level checks through s390 debugfs/sprintf view.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_drv.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_drv.c

Purpose: module-level driver setup for VFIO AP matrix passthrough. It creates the root `vfio_ap` device, `matrix` bus/device, AP queue driver for CEX4 and newer queues, debug feature area, and mediated-device registration.

Important APIs and functions: global `matrix_dev` holds the matrix device. `features_show()` advertises `guest_matrix hotplug ap_config`. `vfio_ap_drv` binds AP queues and delegates probe/remove/resource/config callbacks to `vfio_ap_ops.c`. `vfio_ap_matrix_dev_create()` registers the root device and custom matrix bus, allocates `matrix_dev`, fills AP config via `ap_qci()` when facility 12 exists, initializes locks/lists, registers the matrix device and driver. `vfio_ap_dbf_info_init()` creates the s390 debug area. `vfio_ap_init()` orders debug, AP instruction check, matrix creation, AP driver registration, and mdev registration. `vfio_ap_exit()` reverses that order.

Control flow: module init fails early if debug setup, AP instruction availability, matrix setup, AP driver registration, or mdev registration fails. Error paths unregister only objects created earlier. AP bus callbacks flow from `ap_driver_register()` into VFIO AP operations.

State and persistence: persistent module state includes `matrix_dev`, matrix device sysfs attributes, `matrix_dev->info`, mdev list/locks, AP driver registration, and debug feature registration. No guest assignment is stored here; that state lives in mdev objects managed by `vfio_ap_ops.c`.

Dependencies and integration: depends on AP bus/device model, VFIO/mdev parent registration, s390 facility/AP QCI support, and the VFIO AP private ABI. It exposes AP queue IDs for CEX4-CEX8 queue types.

Risks: init error unwinding must avoid leaking root devices, buses, or debug areas. `ap_qci()` failure during matrix allocation jumps through shared cleanup labels, so release order is important. The global `matrix_dev` is central to every operation and must not be used after destruction.

Test signals: module load/unload, no-AP-instruction systems, `ap_qci()` failure injection, each registration failure path, sysfs `features` content, AP queue driver matching for CEX4-CEX8, and debug feature registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_ops.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_ops.c

Purpose: implements VFIO AP mediated-device behavior: matrix assignment sysfs, queue ownership, KVM guest APCB updates, PQAP(AQIC) interception, interrupt resource pinning, queue reset/hotplug, VFIO ioctls, AP queue probe/remove, and host AP configuration change handling.

Important APIs and functions: lock helpers enforce `guests_lock`, `kvm->lock`, then `mdevs_lock`. `vfio_ap_irq_enable()` validates/pins guest NIB pages, handles PV shared-page checks, registers GISC, and issues `ap_aqic()`. `handle_pqap()` handles guest AQIC interception through the KVM crypto hook. Assignment sysfs handlers update AP adapter/domain/control-domain bitmaps, validate no sharing/default-driver conflict, link queues, filter guest shadow APCB, and reset filtered queues. `ap_config_store()` atomically parses three hex masks and applies bulk add/remove. VFIO callbacks implement open/close, reset, IRQ eventfd setup, request signaling, DMA unmap cleanup, and device info. Queue probe/remove creates per-queue status sysfs, links APQNs to matching mdevs, filters guest exposure, and resets on removal. Config callbacks track added resources until scan completion and hot-unplug removed resources.

Control flow: userspace creates an mdev, writes matrix sysfs masks, opens the VFIO device with a KVM, then the driver installs a PQAP hook and writes filtered masks into the guest CRYCB/APCB. AP bus probe/remove and config-change callbacks dynamically link/unlink queues and update guests.

State and persistence: each `ap_matrix_mdev` stores assigned matrix masks, filtered `shadow_apcb`, KVM pointer, APQN queue hash, eventfds, and pending add bitmaps. Each `vfio_ap_queue` stores APQN, owning mdev, saved NIB IOVA/ISC, reset status, and reset work. State is in kernel memory and sysfs; it is not persisted across module unload.

Dependencies and integration: depends on AP bus queue objects, KVM s390 crypto masks and GISA/GISC interfaces, VFIO/mdev/iommufd APIs, eventfd, AP instructions (`TAPQ`, `ZAPQ`, `AQIC`), AP permissions, and s390 UV shared-page handling for protected guests.

Risks: lock ordering is critical to avoid deadlocks across AP bus, sysfs, VFIO, and KVM callbacks. Queue filtering at adapter granularity can remove more guest APQNs than a single missing queue. Interrupt setup must cleanly unpin NIB pages and unregister GISC on all AQIC failures. Some bitmap calls use AP device/domain widths and require careful bounds testing.

Test signals: concurrent sysfs assignment/unassignment, APQN sharing rejection, default-driver ownership rejection, VFIO open with duplicate KVM use, AQIC enable/disable for normal and PV guests, DMA unmap of saved NIB, queue reset response codes, AP queue hotplug/remove, config add/remove plus scan-complete, eventfd request/config notifications, and VFIO ioctl validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_private.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_private.h

Purpose: defines private VFIO AP data structures and cross-file function prototypes. It is the shared contract between driver setup and operations for matrix devices, mdev assignment state, and queue ownership.

Important APIs and types: `struct ap_matrix_dev` wraps the root matrix `device`, current `ap_config_info`, mdev list, `mdevs_lock`, `guests_lock`, AP driver pointer, and mdev parent/type data. `struct ap_matrix` carries adapter (`apm`), queue/domain (`aqm`), and control-domain (`adm`) bitmaps plus max IDs. `struct ap_queue_table` contains a hash table of assigned queues. `struct ap_matrix_mdev` embeds `vfio_device`, list node, desired matrix, filtered `shadow_apcb`, KVM pointer, PQAP hook, mdev pointer, queue table, request/config eventfds, and pending add masks. `struct vfio_ap_queue` records APQN, owning mdev, saved AQIC NIB/ISC, hash/list nodes, reset status, and reset work.

Control flow: this header has no executable flow. It enables `vfio_ap_drv.c` to create global matrix state and `vfio_ap_ops.c` to mutate it through declared mdev/AP bus callbacks.

State and persistence: all structs describe in-memory kernel state. Assignment state is visible through sysfs while the mdev exists, but it is not written to stable storage. Queue interrupt state persists only while a queue is linked and a guest has configured AQIC.

Dependencies and integration: includes Linux mdev, eventfd, mutex, KVM, VFIO, hashtable, and `ap_bus.h`. External callbacks connect to AP bus registration, mdev registration, resource-in-use checks, and AP config notifications.

Risks: because this header defines lock ownership and shared state, field semantics must stay synchronized with operations code. Misinterpreting `matrix` versus `shadow_apcb` can expose unavailable queues to guests. `VFIO_AP_ISC_INVALID` must be honored before unregistering interrupt subclasses.

Test signals: compile-time structure use across driver files, mdev create/remove lifecycle, queue link/unlink hash behavior, saved IOVA/ISC cleanup, and configuration-change callbacks updating pending add masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/vfio_ap_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_api.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_api.c

Purpose: central zcrypt user and kernel API implementation. It manages zcrypt device nodes, permission masks, message-type registration, queue/card selection, RSA/CCA/EP11 request dispatch, status ioctls, hwrng integration, AP-bus readiness waits, and module init/exit.

Important APIs and functions: `zcrypt_msgtype_register()`/`zcrypt_msgtype()` maintain crypto message operation providers. zcdn helpers create named char devices with per-node AP/ioctl masks. `zcrypt_open()` selects global or per-device permissions. `zcrypt_rsa_modexpo()` and `zcrypt_rsa_crt()` choose accelerator/CCA queues using card/queue load, request size, speed rating, permissions, and retry penalties. `_zcrypt_send_cprb()` and `_zcrypt_send_ep11_cprb()` prepare CCA/EP11 AP messages, enforce admin/usage-domain permissions, select eligible queues, and call provider ops. Exported `zcrypt_send_cprb()` and `zcrypt_send_ep11_cprb()` add retry and AP bus rescan behavior. Status helpers build masks and counters. `zcrypt_rng()` and hwrng callbacks fill a page buffer from CCA RNG requests. `zcrypt_wait_api_operational()` waits once for APQN bindings.

Control flow: ioctl dispatch first checks the node ioctl mask, then copies user structures, runs request-specific retry loops, optionally triggers AP bus rescan on `-ENODEV`, and copies results back. Queue selection is done under `zcrypt_list_lock`; selected card/queue/module/device refs are held during operation and dropped afterward.

State and persistence: module state includes card list, ops list, open count, zcdn device class/char-device minors, debug feature handle, RNG buffer/count, and one-shot API readiness state. It does not persist state across unload.

Dependencies and integration: depends on AP bus, zcrypt message type 6/50 providers, CCA/EP11 misc preparation helpers, tracepoints, misc/cdev device models, sysfs class attributes, hwrng, and AP permission masks.

Risks: queue-selection reference counting and lock boundaries are subtle. Per-node permission checks must distinguish admin control domains from usage domains. Retry and rescan behavior can mask transient AP binding races but must not livelock. User/kernel buffer handling depends on `ZCRYPT_XFLAG_USERSPACE`.

Test signals: ioctls with denied masks, per-zcdn AP/AQ/AD masks, RSA size bounds, CCA and EP11 target selection, `-EAGAIN` retry limit to `-EIO`, `-ENODEV` rescan retry, status mask compatibility ioctls, RNG register/read/remove, zcdn create/destroy conflicts, and init failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_api.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_api.h

Purpose: declares the private zcrypt API shared by zcrypt card/queue/message-type drivers and pkey/EP11/CCA helpers. It defines device type constants, request operation identifiers, queue/card state objects, provider callbacks, retry tracking, flags, globals, and exported function prototypes.

Important APIs and types: `enum crypto_ops` indexes speed ratings for RSA, CRT, hwrng, and secure-key operations. `struct zcrypt_track` stores retry count, last qid, and last return code for penalized reselection. `ZCRYPT_XFLAG_USERSPACE` and `ZCRYPT_XFLAG_NOMEMALLOC` control buffer interpretation and AP message allocation. `struct zcrypt_ops` is the provider vtable for RSA modexpo, RSA CRT, CCA CPRB, EP11 CPRB, and RNG operations. `struct zcrypt_card` stores card list membership, queues, AP card pointer, online flag, userspace type/name, size limits, speed ratings, load, and request count. `struct zcrypt_queue` stores queue list membership, provider ops, AP queue pointer, online/load/request state, and reply message.

Control flow: the header contributes inline copy helpers `z_copy_from_user()` and `z_copy_to_user()` that switch between userspace copy functions and kernel `memcpy()` depending on flags. Iteration macros walk the global card list and per-card queues.

State and persistence: declares global list/lock state and mempool threshold, but owns no storage itself. Struct fields describe runtime AP card/queue registration state and current load, not persistent configuration.

Dependencies and integration: includes AP bus, s390 zcrypt ABI, and debug support. The prototypes connect card, queue, rng, message-type, and exported CCA/EP11 send paths across the crypto driver directory.

Risks: this header is an internal ABI; changing struct fields or callback signatures affects multiple drivers. Copy-helper misuse can turn a userspace pointer into an unchecked kernel pointer or vice versa. Load/request counters must be updated consistently by API users.

Test signals: build all zcrypt message providers, validate userspace and kernel-call send paths, verify retry tracking updates, exercise queue/card register/unregister paths, and confirm mempool threshold handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_card.c -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_card.c

Purpose: implements common zcrypt AP card device helpers: sysfs attributes, online/offline propagation, reference counting, allocation/free, and registration/unregistration in the global zcrypt card list.

Important APIs and functions: `type_show()` exposes the card type string. `online_show()` reports online only when the AP card is configured, not checkstopped, and zcrypt online is set. `online_store()` validates requested state, rejects online for unavailable cards, updates `zc->online`, emits AP uevents, and force-updates child queues. It collects queue references under `zcrypt_list_lock` and sends queue uevents after releasing the spinlock. `load_show()` reports `atomic_t load`. `zcrypt_card_alloc()` initializes list heads and kref. `zcrypt_card_get()`/`zcrypt_card_put()` manage lifetime. `zcrypt_card_register()` adds to `zcrypt_card_list`, marks online, and creates sysfs attributes. `zcrypt_card_unregister()` removes sysfs/list membership and drops the final reference.

Control flow: AP card-specific drivers allocate and populate `struct zcrypt_card`, then call register. Userspace writes `online`; queue online state is forced accordingly and events are sent. Unregister removes visibility before releasing object references.

State and persistence: persistent runtime state includes global card-list membership, `zc->online`, load, request count, and child queue list. The online flag is not stored across driver reloads.

Dependencies and integration: depends on zcrypt global list/lock, AP card device state, queue helpers, sysfs, krefs, and AP online uevents. It is used by zcrypt message-type card drivers rather than by userspace directly.

Risks: online propagation crosses spinlock and sleepable uevent contexts, so reference collection must be correct. Register error paths must remove list entries if sysfs creation fails. Online state combines AP hardware state and zcrypt user state; tests should avoid treating `zc->online` alone as availability.

Test signals: card allocation/free kref balance, sysfs attribute creation failure, online write validation, checkstopped/configured transitions, child queue force-online propagation, uevent emission, list removal, and concurrent status reads during unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cca_key.h -->
# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cca_key.h

Purpose: defines CCA RSA key token structures and inline builders that translate userspace RSA key parameters into type-6 AP message key blocks for modular exponentiation and CRT operations.

Important APIs and types: `struct t6_keyblock_hdr`, `struct cca_token_hdr`, `struct cca_public_sec`, and `struct cca_pvt_ext_crt_sec` model packed CCA key-token sections. Constants identify extended token headers, private CRT sections, clear private format, and usage flags. `zcrypt_type6_mex_key_en()` builds a public-section key block from exponent and modulus pointers in `ica_rsa_modexpo`. `zcrypt_type6_crt_key()` builds a private CRT token from p, q, dp, dq, u, padding, synthetic public section, and exponent 65537.

Control flow: both builders first enforce a defensive `inputdatalength <= 512` check, clear the output area, populate static header/section fields, copy key parts from userspace, compute token/section lengths, and return the number of bytes written or a negative errno.

State and persistence: no state persists. Static header templates are immutable. Generated key blocks live in caller-provided AP message buffers.

Dependencies and integration: depends on s390 zcrypt userspace ABI structures `ica_rsa_modexpo` and `ica_rsa_modexpo_crt`, `copy_from_user()`, and message type 6 request builders that include this header.

Risks: packed binary layout and length arithmetic are hardware ABI-sensitive. The inline functions trust the caller to provide a sufficiently large destination buffer; the 512-byte plausibility checks guard against known dispatch limits but do not size the destination. All user copies must be checked to avoid partially built messages.

Test signals: build MEX keys for 1K/2K/4K RSA sizes, CRT keys with odd/even input lengths, invalid lengths above 512, fault-injected `copy_from_user()`, expected section lengths/padding, and hardware/message-type parser acceptance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_cca_key.h -->
