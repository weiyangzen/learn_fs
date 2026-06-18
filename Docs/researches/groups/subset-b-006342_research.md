# subset-b-006342 Security Keys and Landlock Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/request_key_auth.c -->
# sources/distributed-fs/ceph-client/security/keys/request_key_auth.c

## Purpose

`request_key_auth.c` implements the internal `.request_key_auth` key type used by the Linux key request upcall path. It creates short-lived authorization keys that let `/sbin/request-key` or another user-mode helper instantiate a pending key while preserving the original requester credentials, target key, callout data, and destination keyring. This is not a normal user-facing key type; it is glue between the keyring request path, credentials, and the userspace instantiation helper.

## Important APIs, Types, and Functions

The file defines `key_type_request_key_auth` with `.instantiate`, `.describe`, `.revoke`, `.destroy`, and `.read` operations. `request_key_auth_instantiate()` attaches the `struct request_key_auth` payload prepared by the caller. `request_key_auth_read()` exposes the callout info to the upcall helper. `request_key_auth_new()` allocates a payload, captures the correct servicing credentials and PID, references the target and destination keyring, allocates an authorization key named by the target serial, and instantiates it. `key_get_instantiation_authkey()` searches the current process keyrings for the authorization key matching a target serial.

## Control Flow

Creation starts with `request_key_auth_new()`. It copies callout bytes, records the operation string, and either inherits an existing request-key servicing context from `current_cred()->request_key_auth` or captures current credentials and PID. It then pins the target key and destination keyring, allocates a `.request_key_auth` key with view/read/search/link permissions, and links the `request_key_auth` payload through `key_instantiate_and_link()`. Consumers later call `key_get_instantiation_authkey()`, which builds the hexadecimal target-key description, searches process keyrings under RCU, maps `-EAGAIN` to `-ENOKEY`, and rejects revoked authorization keys.

## State and Persistence Behavior

Authorization state lives in `struct request_key_auth` and is referenced by the key payload under RCU. The payload owns references to the target key, destination keyring, and captured credentials. Revoke and destroy clear the key payload with `rcu_assign_keypointer()` and defer freeing via `call_rcu()`, which protects readers walking key payload state. The key is created outside normal quota accounting with `KEY_ALLOC_NOT_IN_QUOTA`, consistent with its internal authorization role.

## Dependencies and Integration Points

This file depends on keyring internals from `internal.h`, credential lifetime rules, RCU key payload accessors, and `keys/request_key_auth-type.h`. It integrates with the request-key upcall mechanism documented under keyring documentation, `search_process_keyrings_rcu()`, `key_alloc()`, and `key_instantiate_and_link()`.

## Risks and Test Signals

The sensitive risks are stale credential references, authorization keys surviving revoke, and leaking callout information to the wrong helper. RCU ordering and semaphore-guarded revoked checks are central. Useful validation includes keyutils request-key upcall tests, revocation races, nested request-key upcalls, negative key instantiation, and checks that revoked auth keys return `-EKEYREVOKED` or `-ENOKEY` as expected.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/request_key_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/sysctl.c -->
# sources/distributed-fs/ceph-client/security/keys/sysctl.c

## Purpose

`sysctl.c` registers `/proc/sys/kernel/keys` controls for the key management subsystem. It exposes quota and garbage-collection tunables used by normal users, root, and persistent keyrings.

## Important APIs, Types, and Functions

`key_sysctls[]` contains `ctl_table` entries for `maxkeys`, `maxbytes`, `root_maxkeys`, `root_maxbytes`, `gc_delay`, and, under `CONFIG_PERSISTENT_KEYRINGS`, `persistent_keyring_expiry`. Each entry points at global keyring variables declared in key internals and uses `proc_dointvec_minmax` with lower/upper bounds. `init_security_keys_sysctls()` calls `register_sysctl_init("kernel/keys", key_sysctls)` and is registered with `early_initcall()`.

## Control Flow

At early init, the sysctl table is registered once. Runtime reads and writes are handled by the sysctl core, which clamps values through the min/max handler. Most values require at least `1`; delay and persistent expiry allow `0`.

## State and Persistence Behavior

The file does not persist data itself. It exposes mutable kernel globals that affect later key allocations, quota reservations, garbage collection delay, and persistent-keyring expiry. Settings persist only for the running kernel unless user space re-applies sysctl configuration.

## Dependencies and Integration Points

The file integrates with the sysctl framework, the key quota variables in `security/keys/internal.h`, and persistent keyring support when enabled. It is intentionally small because policy is enforced by the key allocation and GC code elsewhere.

## Risks and Test Signals

Bad bounds would let administrators set impossible quotas or negative delays. Useful tests are sysctl read/write smoke tests, boundary writes of `0`, `1`, and `INT_MAX`, and key allocation attempts before and after quota changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/Kconfig -->
# sources/distributed-fs/ceph-client/security/keys/trusted-keys/Kconfig

## Purpose

This Kconfig fragment selects the hardware or firmware trust backends available to the common `trusted` key type. It lets TPM, TEE, CAAM, DCP, and IBM PowerVM PKWM providers contribute sealing/unsealing operations when their platform dependencies are present.

## Important APIs, Types, and Functions

The file defines `HAVE_TRUSTED_KEYS` as a backend availability marker and backend booleans `TRUSTED_KEYS_TPM`, `TRUSTED_KEYS_TEE`, `TRUSTED_KEYS_CAAM`, `TRUSTED_KEYS_DCP`, and `TRUSTED_KEYS_PKWM`. Backend options depend on their provider subsystems being at least as available as `TRUSTED_KEYS`, default to `y` when possible, and select provider-specific prerequisites such as ASN.1/OID helpers for TPM and CAAM blob generation for CAAM.

## Control Flow

During configuration, enabling `TRUSTED_KEYS` allows one or more backend selections. If no backend sets `HAVE_TRUSTED_KEYS`, a warning comment is displayed. The resulting symbols drive which provider objects are linked into `trusted.o`.

## State and Persistence Behavior

There is no runtime state. The persistent effect is build-time: which trusted-key backends exist, which crypto parsers are built, and whether the common trusted key module can initialize a source.

## Dependencies and Integration Points

The options integrate with TPM (`TCG_TPM`), TEE, Freescale/NXP CAAM, MXS DCP, and pSeries PLPKS support. They feed the trusted-key `Makefile` and the `trusted_key_sources[]` array in `trusted_core.c`.

## Risks and Test Signals

Dependency mistakes produce link failures or a `trusted` key type with no usable source. Test signals include allmodconfig/allyesconfig builds, platform-specific boot probes, and keyctl creation of `trusted` keys with each configured source.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/Makefile -->
# sources/distributed-fs/ceph-client/security/keys/trusted-keys/Makefile

## Purpose

The Makefile builds the common trusted-key module object and conditionally includes backend providers and TPM2 ASN.1 parser support.

## Important APIs, Types, and Functions

`obj-$(CONFIG_TRUSTED_KEYS) += trusted.o` creates the aggregate object. `trusted-y` always includes `trusted_core.o`. TPM support adds `trusted_tpm1.o`, `trusted_tpm2.o`, and `tpm2key.asn1.o`, with an explicit dependency from `trusted_tpm2.o` to generated `tpm2key.asn1.h`. Other backend symbols add `trusted_tee.o`, `trusted_caam.o`, `trusted_dcp.o`, and `trusted_pkwm.o`.

## Control Flow

Kbuild composes `trusted.o` from the enabled `trusted-*` fragments. ASN.1 code generation must happen before compiling `trusted_tpm2.o`, because that file includes `tpm2key.asn1.h`.

## State and Persistence Behavior

No runtime state is represented. The file determines the final object contents and therefore which backend operation tables are visible to `trusted_core.c`.

## Dependencies and Integration Points

It integrates with Kbuild, Kconfig backend symbols, and the kernel ASN.1 generator. The naming matches exported backend operation tables such as `trusted_key_tpm_ops` and `trusted_key_tee_ops`.

## Risks and Test Signals

Missing objects lead to unresolved backend references or absent trusted-key features. Test with per-backend build matrices, especially TPM where generated ASN.1 headers are required.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_caam.c -->
# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_caam.c

## Purpose

`trusted_caam.c` implements the trusted-key backend for NXP CAAM blob generation. It seals trusted key payloads into CAAM blobs tied to hardware and can also expose protected-key material for consumers expecting CAAM pkey metadata plus the blob.

## Important APIs, Types, and Functions

`trusted_key_caam_ops` provides `.init`, `.seal`, `.unseal`, and `.exit` callbacks with `.migratable = 0`. `trusted_caam_init()` obtains a CAAM blob generator with `caam_blob_gen_init()` and registers `key_type_trusted`; `trusted_caam_exit()` unregisters and releases the blobifier. `trusted_caam_seal()` calls `caam_encap_blob()`, and `trusted_caam_unseal()` calls `caam_decap_blob()` unless protected-key mode is requested. `get_pkey_options()` parses `key_enc_algo=...`, and `is_key_pkey()` detects a `pk` option in the datablob tail.

## Control Flow

The common trusted core chooses this backend and calls `.init`. For a new key, the core fills `p->key`; CAAM seal builds a `caam_blob_info` with key modifier `SECURE_KEY`, optional protected-key metadata, and output buffer `p->blob`. On success it records `p->blob_len`; in protected-key mode it rewrites `p->key` as `struct caam_pkey_info` followed by the blob. For load, unseal either returns protected-key metadata plus blob without decrypting, or decapsulates the CAAM blob into the payload key.

## State and Persistence Behavior

The backend keeps one global `blobifier` handle. Payload persistence is the sealed CAAM blob stored in `trusted_key_payload.blob`; protected-key mode stores provider metadata in the key payload visible to kernel consumers. Keys are non-migratable because CAAM blobs are tied to the local hardware/key modifier.

## Dependencies and Integration Points

Dependencies include `<soc/fsl/caam-blob.h>`, CAAM blob-gen support, key type registration, and trusted-key core static calls. It is selected by `CONFIG_TRUSTED_KEYS_CAAM`.

## Risks and Test Signals

The protected-key parser currently returns success on option parse failure in two branches, which is behavior worth preserving or reviewing carefully. Other risks are blob size assumptions, hardware binding surprises, and returning blob-backed key material with the wrong length. Test with normal and `pk` datablobs, unsupported `key_enc_algo`, CAAM probe failure, and keyctl load/read cycles across reboot or hardware state changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_caam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_core.c -->
# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_core.c

## Purpose

`trusted_core.c` defines the common `trusted` key type and dispatches sealing, unsealing, and random generation to one selected trust source. It parses user datablobs, manages trusted-key payload lifetime, supports update/reseal for migratable backends, exports sealed blobs, and selects the active backend at module init.

## Important APIs, Types, and Functions

`key_type_trusted` provides `.instantiate`, `.update`, `.destroy`, `.describe`, and `.read`. `trusted_key_sources[]` lists compiled backend operation tables. Static calls `trusted_key_seal`, `trusted_key_unseal`, and `trusted_key_get_random` are updated to the selected provider for fast dispatch. `datablob_parse()` recognizes `new <len>`, `load <hexblob>`, and `update`. `trusted_instantiate()` handles new/load requests; `trusted_update()` reseals an existing migratable key; `trusted_read()` returns the sealed blob as hex. `init_trusted()` selects a source and RNG, calls provider `.init`, updates static calls, and records the provider `.exit` and migratable default.

## Control Flow

Instantiation copies the keyctl payload into a NUL-terminated buffer, allocates a `trusted_key_payload`, parses the command, and either unseals a provided blob or asks the selected RNG to fill a new secret before sealing it. Successful payloads are attached with RCU key payload assignment. Update requires a positive, migratable key, parses only `update`, clones the old key bytes into a new payload, reseals with new options, swaps payloads, and frees the old payload via RCU. Module initialization iterates backend candidates, respecting `trusted.source` and `trusted.rng`, stops on first successful backend or on hard errors, and registers the common key type through the provider.

## State and Persistence Behavior

Per-key persistent state is `struct trusted_key_payload`: clear key bytes while resident, sealed blob bytes, lengths, migratable flag, and provider-specific flags. The external persistence boundary is the hex sealed blob returned by `trusted_read()`. Global state includes selected static-call targets, `trusted_key_exit`, module parameters, and the default migratable value inherited from the backend.

## Dependencies and Integration Points

The core integrates with the keyring subsystem, `keys/trusted-type.h`, user key describe helpers, random bytes, module parameters, and provider headers for TPM, TEE, CAAM, DCP, and PKWM. It relies on provider callbacks to register/unregister `key_type_trusted`.

## Risks and Test Signals

Incorrect datablob parsing or payload length handling can leak secrets, accept malformed blobs, or break compatibility. Static-call targets must only be used after a provider succeeds. Tests should cover `keyctl add trusted ... "new N"`, `load`, `update`, read hex length, unsupported source/RNG parameters, provider probe failure, migratable versus non-migratable update behavior, and memory sanitization on failure paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_dcp.c -->
# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_dcp.c

## Purpose

`trusted_dcp.c` implements trusted-key sealing for NXP Data Co-Processor hardware. DCP only exposes hardware-bound AES operations, so this backend defines its own blob format: a random blob encryption key encrypts the trusted payload with AES-GCM, and DCP encrypts that blob key with an OTP or UNIQUE device key.

## Important APIs, Types, and Functions

`struct dcp_blob_fmt` stores version, encrypted blob key, nonce, payload length, and encrypted payload plus GCM tag. `trusted_dcp_seal()` creates the blob. `trusted_dcp_unseal()` validates and decrypts it. `do_dcp_crypto()` runs `ecb-paes-dcp` for the blob key. `do_aead_crypto()` runs `gcm(aes)` for payload encryption/authentication. `test_for_zero_key()` detects insecure zero/test key state unless `dcp_skip_zk_test` is set. `dcp_trusted_key_ops` registers non-migratable backend callbacks.

## Control Flow

Seal computes the final blob size, allocates a temporary AES-128 blob key, fills the blob version and nonce, AEAD-encrypts `p->key`, encrypts the temporary blob key with DCP, stores payload length, and wipes the temporary key. Unseal checks the version and expected length, decrypts the blob key through DCP, uses it to AEAD-decrypt the payload into `p->key`, and wipes the temporary key. Init optionally logs OTP-key use, runs the zero-key test, and registers the trusted key type.

## State and Persistence Behavior

Persistent key material is stored only in the custom DCP blob in `p->blob`; clear temporary blob keys are explicitly zeroed. Module parameters select OTP versus UNIQUE device key and whether to skip the zero-key test. DCP-backed trusted keys are non-migratable because the encrypted blob key is hardware-bound.

## Dependencies and Integration Points

The backend depends on the Linux crypto API, `ecb-paes-dcp`, `gcm(aes)`, DCP platform support, random bytes, and the trusted-key core. It is selected by `CONFIG_TRUSTED_KEYS_DCP`.

## Risks and Test Signals

Blob version/length validation is critical because malformed blobs drive flexible payload parsing. AEAD tag failure must not expose partial plaintext. The zero-key test is a platform safety gate. Test signals include secure-mode and insecure-mode boot behavior, OTP/UNIQUE modes, malformed blob versions/lengths/tags, crypto allocation failures, and keyctl create/load round trips.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_dcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_pkwm.c -->
# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_pkwm.c

## Purpose

`trusted_pkwm.c` implements a trusted-key backend for IBM PowerVM Key Wrapping Module through pSeries PLPKS hypervisor interfaces. It wraps and unwraps trusted key payloads with a platform-generated wrapping key.

## Important APIs, Types, and Functions

`pkwm_trusted_key_ops` supplies non-migratable `.init`, `.seal`, `.unseal`, and `.exit` callbacks. `trusted_pkwm_init()` checks `plpks_wrapping_is_supported()`, generates a default wrapping key with `plpks_gen_wrapping_key()`, and registers `key_type_trusted`. `trusted_pkwm_seal()` parses `wrap_flags=...`, copies the payload into an aligned buffer, and calls `plpks_wrap_object()`. `trusted_pkwm_unseal()` calls `plpks_unwrap_object()`. `trusted_options_alloc()` allocates shared trusted options plus PKWM-private options.

## Control Flow

Init prepares the PLPKS wrapping environment before trusted keys can be created. Seal allocates option state, parses optional wrapping flags, creates an aligned input buffer from `p->key`, asks PLPKS to wrap it, and copies the returned object into `p->blob`. Unseal copies the sealed blob into an aligned input buffer, unwraps it through PLPKS, and copies returned plaintext into `p->key`.

## State and Persistence Behavior

The sealed object in `p->blob` is the persistent representation. The backend has no long-lived C state beyond the platform wrapping key managed by PLPKS. Temporary input and output buffers are freed after use; option structures are freed with sensitive-free helpers.

## Dependencies and Integration Points

Dependencies include `asm/plpks.h`, pSeries platform firmware, and common trusted-key types. It is selected by `CONFIG_TRUSTED_KEYS_PKWM` and invoked through `trusted_core.c`.

## Risks and Test Signals

Potential risks include output length exceeding `MAX_BLOB_SIZE`, incorrect assumptions about page-aligned buffers, and PLPKS support changing under firmware. Tests should cover unsupported firmware, wrapping-key generation failure, invalid `wrap_flags`, create/load round trips, and large key sizes near trusted-key limits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_pkwm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tee.c -->
# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tee.c

## Purpose

`trusted_tee.c` implements a trusted-key backend backed by an OP-TEE trusted application. It delegates random generation, sealing, and unsealing to a TEE session using shared memory.

## Important APIs, Types, and Functions

`struct trusted_key_tee_private` stores the TEE device, context, session ID, and shared-memory pool pointer. `trusted_tee_seal()`, `trusted_tee_unseal()`, and `trusted_tee_get_random()` invoke TA commands `TA_CMD_SEAL`, `TA_CMD_UNSEAL`, and `TA_CMD_GET_RANDOM`. `optee_ctx_match()` restricts contexts to OP-TEE with registered memory support. `trusted_key_probe()` opens the context/session and registers `key_type_trusted`; `trusted_key_remove()` unregisters and closes them. `trusted_key_tee_ops` exposes the callbacks to the core.

## Control Flow

The TEE client driver binds to a fixed TA UUID. Probe opens an OP-TEE context, opens a kernel-login session to the TA, then registers the trusted key type. Seal and unseal register a kernel buffer spanning `p->key` and `p->blob`, set input/output memrefs at the correct offsets, invoke the TA, and update `blob_len` or `key_len` from the returned memref size. Random generation registers the caller-provided key buffer and invokes the random command.

## State and Persistence Behavior

Backend state is the global `pvt_data` session/context. Per-key persistence is the TA-produced sealed blob. Keys are non-migratable because the TA is expected to use a hardware unique key. Shared-memory registrations are temporary and freed after each invocation.

## Dependencies and Integration Points

The backend depends on TEE client devices, OP-TEE generic capabilities, a TA with the hard-coded UUID, and the trusted-key core. It is selected by `CONFIG_TRUSTED_KEYS_TEE`.

## Risks and Test Signals

The correctness boundary includes TA behavior, memref sizing, and shared buffer layout. Probe must clean up contexts on partial failure. Test signals include TA absence, session open failure, command return codes, short random output, seal/unseal round trips, driver unbind cleanup, and concurrent key operations sharing the global session.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tpm1.c -->
# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tpm1.c

## Purpose

`trusted_tpm1.c` provides the TPM-backed trusted-key provider and contains the TPM 1.2 command construction, HMAC authentication, PCR locking, option parsing, and dispatch glue that also routes TPM 2.0 systems to `trusted_tpm2.c`.

## Important APIs, Types, and Functions

Global state includes the selected `tpm_chip *chip` and PCR-bank `digests`. TPM 1.2 helpers include `TSS_rawhmac()`, `TSS_authhmac()`, `TSS_checkhmac1()`, `TSS_checkhmac2()`, `trusted_tpm_send()`, `osap()`, `oiap()`, `tpm_seal()`, and `tpm_unseal()`. High-level helpers `key_seal()` and `key_unseal()` wrap the TPM 1.2 paths. `getoptions()` parses `keyhandle`, `keyauth`, `blobauth`, `pcrinfo`, `pcrlock`, `migratable`, `hash`, `policydigest`, and `policyhandle`. `trusted_tpm_seal()` and `trusted_tpm_unseal()` dispatch to TPM 2.0 or TPM 1.2. `trusted_key_tpm_ops` exposes the backend.

## Control Flow

Initialization obtains the default TPM chip, allocates digest descriptors for PCR extension, and registers the common trusted key type. Seal parses options and rejects missing TPM 1.2 key handles, then calls `tpm2_seal_trusted()` on TPM 2.0 systems or `key_seal()` on TPM 1.2. TPM 1.2 sealing creates an OSAP session, derives authorization material, builds a `TPM_ORD_SEAL` AUTH1 command, sends it, verifies response HMAC, and copies the returned blob. Unseal creates two OIAP sessions, builds an AUTH2 `TPM_ORD_UNSEAL` command, verifies both response HMACs, copies plaintext, and extracts the embedded migratable flag. Optional `pcrlock` extends a PCR after seal or unseal.

## State and Persistence Behavior

TPM-backed payload persistence is the TPM sealed blob. TPM 1.2 stores the migratable flag at the end of the sealed plaintext; TPM 2.0 stores or infers it through TPM2 attributes in the companion file. Global chip and digest references live until module exit. Authorization data and work buffers are freed with sensitive clearing where appropriate.

## Dependencies and Integration Points

Dependencies include the TPM core, TPM command constants, SHA-1/HMAC helpers, hash metadata, trusted-key core, and TPM2 helper functions from `trusted_tpm2.c`. It integrates with `CAP_SYS_ADMIN` for PCR locking and `tpm_get_random()` for backend RNG.

## Risks and Test Signals

TPM 1.2 packet offsets and HMAC coverage are fragile; endian mistakes or unchecked response sizes can break security. PCR lock is privileged and changes platform state. TPM 2.0 option parsing must reject TPM 1.x-incompatible hash/policy options. Test with TPM 1.2 and TPM 2.0 create/load/update, auth failures, PCR policy mismatch, pcrlock permission checks, malformed hex options, no default TPM, and key length limits.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tpm1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tpm2.c -->
# sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tpm2.c

## Purpose

`trusted_tpm2.c` implements TPM 2.0 sealing and unsealing for trusted keys. It encodes TPM2 private/public blobs into the Linux TPMSealedData ASN.1 format, decodes that format on load, and issues TPM2 `Create`, `Load`, and `Unseal` commands with authorization sessions.

## Important APIs, Types, and Functions

`tpm2_key_encode()` emits the TPMSealedData sequence with OID, optional emptyAuth tag, parent handle, public blob, and private blob. `tpm2_key_decode()` and decoder callbacks `tpm2_key_parent()`, `tpm2_key_type()`, `tpm2_key_pub()`, and `tpm2_key_priv()` parse the ASN.1 representation. `tpm2_buf_append_auth()` appends manual policy/password auth sessions. `tpm2_seal_trusted()` builds and transmits `TPM2_CC_CREATE`. `tpm2_load_cmd()` loads the sealed object and returns a transient handle. `tpm2_unseal_cmd()` executes `TPM2_CC_UNSEAL`. `tpm2_unseal_trusted()` ties load, unseal, flush, and TPM op lifetime together.

## Control Flow

Seal validates the selected hash and parent handle, gets TPM ops, starts an auth session, builds sensitive and public sized buffers, sets object attributes based on policy and migratability, appends optional policy digest, sends `Create`, validates the HMAC response, and encodes the returned private/public blob into `payload->blob`. Unseal first decodes the new ASN.1 format or falls back to old raw format. It validates blob sizes, derives migratable state from public attributes, starts an auth session, loads the object under the parent key, then unseals it. Policy-handle unseal has a special path for external policy sessions and may send a plaintext password because nonce/HMAC material is unavailable.

## State and Persistence Behavior

The persistent representation is the ASN.1 TPMSealedData blob in `payload->blob`, with old raw blob compatibility. Unseal creates a transient TPM object handle and always flushes it after use. `payload->old_format` controls how the migratable flag is recovered. TPM operation references are acquired and released around seal/unseal.

## Dependencies and Integration Points

The file depends on TPM2 buffer/session helpers, ASN.1 encoder/decoder infrastructure, OID registry, unaligned access helpers, and option fields parsed in `trusted_tpm1.c`. It integrates with generated `tpm2key.asn1.h`.

## Risks and Test Signals

ASN.1 size handling, TPM buffer overflow flags, and policy-session authentication are high-risk. The policyhandle FIXME documents a weaker password path for externally created sessions. Tests should cover new and old blob formats, emptyAuth and password auth, policy digest/handle flows, non-migratable attributes, malformed ASN.1, TPM response truncation, and transient handle flushing on failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/trusted-keys/trusted_tpm2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/user_defined.c -->
# sources/distributed-fs/ceph-client/security/keys/user_defined.c

## Purpose

`user_defined.c` implements the generic `user` key type and the non-readable `logon` key type. These key types store arbitrary user-provided payload bytes in keyrings, with `logon` intended for secrets such as credentials that must not be readable back to userspace.

## Important APIs, Types, and Functions

`key_type_user` includes read support through `user_read()`. `key_type_logon` reuses the same payload operations but omits `.read` and adds `logon_vet_description()`. `user_preparse()` validates and copies incoming payloads into `struct user_key_payload`. `user_update()` reserves quota, swaps payloads under RCU, and preserves expiry. `user_revoke()` clears quota and defers payload freeing. `user_destroy()` frees final payload state. `user_describe()` prints description and payload length.

## Control Flow

Instantiation uses `user_preparse()` followed by `generic_key_instantiate()`. Update reserves quota for the new length, installs the new payload, nulls the preparsed pointer so the key core will not free it twice, and queues old payload RCU disposal. Read returns the full payload length and copies as many bytes as the caller buffer allows. Logon key creation first vets that descriptions are qualified with a non-leading colon.

## State and Persistence Behavior

The payload is stored as an RCU-protected `struct user_key_payload` attached to the key. Payload memory is freed with `kfree_sensitive()` on preparse failure, revoke, update, and destroy paths. Quota is reserved according to payload length and released on revoke.

## Dependencies and Integration Points

The file integrates with key type registration elsewhere, the generic key instantiate helper, key quota accounting, RCU payload accessors, and exported user-key APIs used by encrypted/trusted key helpers.

## Risks and Test Signals

The main risks are exposing `logon` payloads through a read path, accepting invalid zero/oversized payloads, and mishandling RCU swaps. Tests should cover payload sizes 0, 1, 32767, and 32768; updates and revoke/read races; logon descriptions without a colon; and sensitive-memory cleanup paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/user_defined.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/Kconfig -->
# sources/distributed-fs/ceph-client/security/landlock/Kconfig

## Purpose

This Kconfig file exposes Landlock LSM support and its KUnit test option. Landlock lets unprivileged processes impose restrictive sandbox policies on themselves and future children.

## Important APIs, Types, and Functions

`SECURITY_LANDLOCK` depends on `SECURITY` and selects `SECURITY_NETWORK` and `SECURITY_PATH`, because Landlock uses network, path, file, credential, and task LSM hooks. `SECURITY_LANDLOCK_KUNIT_TEST` depends on `KUNIT=y` and Landlock and defaults to `KUNIT_ALL_TESTS`.

## Control Flow

When enabled, Kbuild compiles the Landlock object and setup registers it as an LSM. The help text reminds users that Landlock must also appear in `CONFIG_LSM` at boot ordering time.

## State and Persistence Behavior

No runtime state is stored here. Build configuration persists in the kernel image and controls whether syscalls, hooks, and tests exist.

## Dependencies and Integration Points

This integrates with the Linux security framework, path hooks, network hooks, and KUnit. User-visible syscalls are implemented in adjacent Landlock files outside this work item.

## Risks and Test Signals

Configuration mistakes can build Landlock without required hook classes or tests. Build `SECURITY_LANDLOCK=y`, boot with Landlock in `CONFIG_LSM`, run `tools/testing/kunit/kunit.py run --kunitconfig security/landlock`, and run Landlock selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/Makefile -->
# sources/distributed-fs/ceph-client/security/landlock/Makefile

## Purpose

The Landlock Makefile builds the single `landlock.o` LSM object from setup, syscall, object, ruleset, credential, task, filesystem, thread-sync, optional network, and optional audit sources.

## Important APIs, Types, and Functions

`obj-$(CONFIG_SECURITY_LANDLOCK) := landlock.o` declares the aggregate. Core objects include `setup.o`, `syscalls.o`, `object.o`, `ruleset.o`, `cred.o`, `task.o`, `fs.o`, and `tsync.o`. `net.o` is included under `CONFIG_INET`; `id.o`, `audit.o`, and `domain.o` are included under `CONFIG_AUDIT`.

## Control Flow

Kbuild links enabled objects into one LSM unit. Setup then calls per-area hook registration functions at boot.

## State and Persistence Behavior

No runtime state is represented. The build composition determines whether network mediation and audit logging code paths exist.

## Dependencies and Integration Points

The file connects Kconfig symbols to the source files used by `setup.c`. Optional file inclusion must match stub definitions in headers such as `net.h`, `audit.h`, and `id.h`.

## Risks and Test Signals

Missing optional objects can cause unresolved symbols or silently absent features. Test with `CONFIG_INET` on/off and `CONFIG_AUDIT` on/off, plus KUnit/selftest builds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/access.h -->
# sources/distributed-fs/ceph-client/security/landlock/access.h

## Purpose

`access.h` defines Landlock access-mask storage, per-layer access matrices, and helpers shared by filesystem, network, scope, ruleset, and audit code. It is the core representation of which rights are handled, allowed, or still denied in each domain layer.

## Important APIs, Types, and Functions

`access_mask_t` is a `u32` bitmask. `struct access_masks` stores packed `fs`, `net`, and `scope` masks. `union access_masks_all` enables whole-mask comparisons. `struct layer_access_masks` stores one access mask per possible layer. `deny_masks_t` compactly records the layer that denied optional file rights. `_LANDLOCK_ACCESS_FS_INITIALLY_DENIED` contains rights such as `REFER` that are denied when any filesystem access is handled. `_LANDLOCK_ACCESS_FS_OPTIONAL` tracks file rights checked after open, currently truncate and device ioctl. `landlock_upgrade_handled_access_masks()` adds initially denied rights, and `access_mask_subset()` tests bit subset relations.

## Control Flow

Access checks initialize a `layer_access_masks` from a domain and requested access, then path or object rules unmask allowed bits. If every layer mask reaches zero, the request is allowed. Ruleset merging upgrades filesystem handled masks so refer remains initially denied.

## State and Persistence Behavior

This header defines in-memory bit layouts but stores no data itself. The layout is embedded in rulesets, credential/file blobs, and audit requests. Static assertions enforce that UAPI access bits fit and that layer counts align with packed deny-mask encoding.

## Dependencies and Integration Points

It depends on Landlock UAPI constants from `<uapi/linux/landlock.h>` and local limits. It is included by most Landlock source files.

## Risks and Test Signals

Adding new access rights requires updating masks, string tables, static assertions, and optional-deny encoding. Test signals include KUnit coverage for layer masks, deny masks, ruleset merge behavior, and ABI selftests for every UAPI bit.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/audit.c -->
# sources/distributed-fs/ceph-client/security/landlock/audit.c

## Purpose

`audit.c` emits audit records for Landlock domain allocation, access denials, and domain deallocation. It maps denied filesystem/network/scope requests to stable blocker strings and identifies the youngest domain layer responsible for a denial.

## Important APIs, Types, and Functions

`fs_access_strings[]` and `net_access_strings[]` map UAPI bits to audit names. `get_blocker()` and `log_blockers()` format denial causes. `log_domain()` logs domain allocation details once. `get_hierarchy()` maps a layer index to the corresponding hierarchy node. `get_denied_layer()` finds the youngest denying layer from full layer masks. `get_layer_from_deny_masks()` decodes compact optional-access deny masks. `landlock_log_denial()` is the main denial logger, and `landlock_log_drop_domain()` logs deallocation for previously recorded domains. KUnit tests cover hierarchy and layer selection helpers.

## Control Flow

When an enforcement hook denies an action, it builds `struct landlock_request` and calls `landlock_log_denial()`. The function validates the request shape, derives the missing access and youngest denied hierarchy, skips disabled logging, increments denial counters regardless of audit enablement, applies same-exec/new-exec logging policy, emits an `AUDIT_LANDLOCK_ACCESS` record with LSM audit data, then calls `log_domain()` to emit the related `AUDIT_LANDLOCK_DOMAIN` allocation record if needed. When a hierarchy is freed, `landlock_log_drop_domain()` emits a deallocation record only if allocation had been logged.

## State and Persistence Behavior

Audit state is stored in `struct landlock_hierarchy`: `log_status`, `num_denials`, ID, details, and log flags. The file does not persist records itself; audit subsystem storage handles that. Denial counters remain even if audit is disabled.

## Dependencies and Integration Points

Dependencies include Linux audit, LSM audit data, Landlock credentials, domains, rulesets, and access masks. It is compiled only with `CONFIG_AUDIT`.

## Risks and Test Signals

Incorrect layer attribution makes audit records misleading and can break user-space policy debugging. Request validation catches inconsistent caller state. Test with audit enabled/disabled, same-exec and new-exec log flags, optional truncate/ioctl denials, network denials, and KUnit suite `landlock_audit`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/audit.h -->
# sources/distributed-fs/ceph-client/security/landlock/audit.h

## Purpose

`audit.h` defines the compact request structure and logging entry points used by Landlock enforcement code. It also provides no-op stubs when audit support is disabled.

## Important APIs, Types, and Functions

`enum landlock_request_type` classifies ptrace, filesystem topology, filesystem access, network access, abstract Unix socket scope, and signal scope denials. `struct landlock_request` carries mandatory LSM audit data, either a fixed denying layer or access bits, optional layer masks, optional compact deny masks, and optional-access metadata. `landlock_log_denial()` and `landlock_log_drop_domain()` are exported internally.

## Control Flow

Enforcement hooks populate a stack `landlock_request` only when they need to log. With `CONFIG_AUDIT=n`, inline stubs make these calls compile away.

## State and Persistence Behavior

The request is transient stack state. Persistent audit-related state is in domain hierarchy structures declared elsewhere.

## Dependencies and Integration Points

The header depends on Linux audit/LSM audit types and Landlock access and credential types. It is included by filesystem, network, task, domain, and object lifetime code.

## Risks and Test Signals

Callers must set a consistent combination of `layer_plus_one`, `access`, `layer_masks`, and `deny_masks`; `audit.c` warns on invalid combinations. Build-test audit on/off and exercise every request type.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/common.h -->
# sources/distributed-fs/ceph-client/security/landlock/common.h

## Purpose

`common.h` centralizes the Landlock LSM name, printk prefix, and a helper for converting single-bit values to bit indices.

## Important APIs, Types, and Functions

`LANDLOCK_NAME` is `"landlock"`. `pr_fmt` is reset to prefix Landlock log messages. `BIT_INDEX(bit)` uses `HWEIGHT(bit - 1)` to convert a power-of-two UAPI access bit to a zero-based table index.

## Control Flow

The header affects compile-time string formatting and table indexing. There is no runtime control flow.

## State and Persistence Behavior

No runtime state is stored.

## Dependencies and Integration Points

It is included by most Landlock source files and must stay consistent with `setup.c`'s `lsm_id`.

## Risks and Test Signals

`BIT_INDEX()` assumes a single-bit mask. Misuse with multi-bit masks would index string tables incorrectly. Compile warnings and audit string tests are useful signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/cred.c -->
# sources/distributed-fs/ceph-client/security/landlock/cred.c

## Purpose

`cred.c` installs Landlock credential LSM hooks. It copies domain state across credential changes, releases domain references when credentials are freed, and resets audit execution tracking on exec.

## Important APIs, Types, and Functions

`hook_cred_transfer()` copies the Landlock credential blob and increments the domain reference. `hook_cred_prepare()` delegates to transfer during credential preparation. `hook_cred_free()` schedules deferred ruleset release. Under audit, `hook_bprm_creds_for_exec()` clears `domain_exec` for each execution. `landlock_add_cred_hooks()` registers the hook list.

## Control Flow

When credentials are prepared or transferred, Landlock pins the old domain and copies the blob into the new credentials. When credentials are freed, the domain is dropped through deferred freeing to avoid sleeping constraints. During exec credential setup, audit execution-origin bits are reset.

## State and Persistence Behavior

The credential blob persists with each `struct cred`. Domain pointers are reference-counted rulesets. Audit `domain_exec` is per-credential and reset by exec.

## Dependencies and Integration Points

The file integrates with LSM credential hooks, binary execution hooks, ruleset lifetime management, and `setup.c` hook registration.

## Risks and Test Signals

Reference leaks or missed increments can free active domains or leak rulesets. Exec reset affects audit filtering. Test with fork, exec, setuid, thread credential changes, domain dropping after process exit, and audit logs across exec.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/cred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/cred.h -->
# sources/distributed-fs/ceph-client/security/landlock/cred.h

## Purpose

`cred.h` defines Landlock's credential security blob and inline helpers to retrieve the current or target task domain, copy credential Landlock state, and detect whether a subject domain handles a requested mask.

## Important APIs, Types, and Functions

`struct landlock_cred_security` stores the enforced immutable `domain`. With audit, it also stores `domain_exec` and `log_subdomains_off`. `landlock_cred()` indexes the LSM credential blob. `landlock_cred_copy()` drops the destination domain, copies the source blob, and pins the source domain. `landlock_get_current_domain()`, `landlock_get_task_domain()`, and `landlocked()` are accessors. `landlock_get_applicable_subject()` returns a subject only if some domain layer handles the requested fs/net/scope masks and can report the youngest matching layer.

## Control Flow

Enforcement hooks call `landlock_get_applicable_subject()` before doing expensive checks. The function scans domain layers from newest to oldest and returns early when any requested bit is handled. If no domain or no handled bits exist, callers skip enforcement.

## State and Persistence Behavior

The blob is persistent per credential and points to reference-counted immutable rulesets. Audit bits persist until new exec or credential replacement.

## Dependencies and Integration Points

The header depends on ruleset, access, setup, credentials, RCU, and task structures. It is included by filesystem, network, task, audit, and setup code.

## Risks and Test Signals

Layer scanning order affects audit attribution for topology denials. Copy helpers must be used carefully to avoid dropping a live domain. Test nested domains, no-op masks, audit layer reporting, and concurrent task-domain reads under RCU.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/cred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/domain.c -->
# sources/distributed-fs/ceph-client/security/landlock/domain.c

## Purpose

`domain.c` provides audit-specific domain metadata creation and helper logic to encode which domain layers denied optional access rights. It records details about the process that created a domain and assigns unique audit IDs.

## Important APIs, Types, and Functions

Under `CONFIG_AUDIT`, `get_current_exe()` captures the current executable path, `get_current_details()` allocates `struct landlock_details`, and `landlock_init_hierarchy_log()` initializes audit fields in a new hierarchy node. `get_layer_deny_mask()` encodes one optional access/layer pair into `deny_masks_t`. `landlock_get_deny_masks()` walks layer masks from newest to oldest and records the youngest layer denying each optional right. KUnit tests cover encoding and deny-mask extraction.

## Control Flow

When a new domain is created in `ruleset.c`, `landlock_init_hierarchy_log()` captures task PID, UID, command, executable path, assigns an ID with `landlock_get_id_range(1)`, marks logging pending, and initializes denial counters. When file open records optional access denials, `landlock_get_deny_masks()` receives the remaining layer masks and produces compact per-file state for later `ftruncate()` and ioctl audit records.

## State and Persistence Behavior

`struct landlock_details` is allocated once per domain hierarchy node and freed when the hierarchy is released. It pins the creator PID to avoid PID reuse ambiguity. Deny masks are compact transient or file-blob state, not global state.

## Dependencies and Integration Points

Dependencies include audit-enabled domain structures, path formatting through `d_path()`, executable file lookup, PID references, random ID generation, and optional access definitions from `access.h`.

## Risks and Test Signals

Executable path capture must tolerate missing `mm` or executable files. Deny-mask encoding depends on layer count and optional-access bit ordering. Test with `CONFIG_AUDIT=y`, domain creation by kernel threads or processes without exe, long paths, and KUnit suite `landlock_domain`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/domain.h -->
# sources/distributed-fs/ceph-client/security/landlock/domain.h

## Purpose

`domain.h` defines Landlock domain hierarchy metadata, audit log state, domain-origin details, and hierarchy reference helpers.

## Important APIs, Types, and Functions

`enum landlock_log_status` tracks pending, recorded, or disabled domain logging. `struct landlock_details` stores creator PID, UID, command, and executable path. `struct landlock_hierarchy` links a domain to its parent and stores reference count plus audit fields such as ID, denial count, details, and logging flags. `landlock_get_hierarchy()` increments references, and `landlock_put_hierarchy()` walks up parents freeing nodes whose usage drops to zero. Audit stubs are provided when `CONFIG_AUDIT=n`.

## Control Flow

Ruleset creation allocates a hierarchy node; inheritance pins the parent hierarchy; ruleset freeing calls `landlock_put_hierarchy()`, which may log domain deallocation, free details, move to the parent, and continue until a referenced ancestor is reached.

## State and Persistence Behavior

Hierarchy nodes outlive individual ruleset pointers as long as child domains or credentials reference them. Audit details are immutable after creation. Parent references preserve domain ancestry for ptrace/scope checks and audit attribution.

## Dependencies and Integration Points

The header integrates with ruleset lifetime, audit logging, ID generation, and task/scope checks outside this work item.

## Risks and Test Signals

Reference-count mistakes can drop parent hierarchy too early or leak ancestry. The free loop must call audit drop before freeing details. Test nested restrict-self calls, parent process exit before child, audit deallocation records, and scope comparisons.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/domain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/errata.h -->
# sources/distributed-fs/ceph-client/security/landlock/errata.h

## Purpose

`errata.h` builds the list of Landlock ABI errata known to this kernel. Errata let userspace detect semantic fixes that may affect compatibility or feature decisions.

## Important APIs, Types, and Functions

`struct landlock_erratum` stores the ABI number and erratum number. `LANDLOCK_ERRATUM(NUMBER)` emits entries using the currently defined `LANDLOCK_ERRATA_ABI`. `landlock_errata_init[]` conditionally includes `errata/abi-*.h` files using `__has_include` for ABIs 1 through 6 and terminates with an empty entry.

## Control Flow

At compile time, each included ABI errata file expands one or more `LANDLOCK_ERRATUM()` entries. At boot, `setup.c` iterates this table in `compute_errata()` and sets bits in `landlock_errata` for entries whose ABI is not newer than the runtime ABI version.

## State and Persistence Behavior

The table is `__initconst` and only feeds the boot-time bitmask. Runtime state is the integer bitmask in `setup.c`.

## Dependencies and Integration Points

It depends on compiler `__has_include` support and ABI-specific errata headers. The bitmask is visible through Landlock ABI/syscall surfaces outside this file.

## Risks and Test Signals

Missing include lines can hide errata from userspace. New errata must preserve backport rules documented in the header. Test boot warnings for compilers without `__has_include`, verify errata bits through Landlock selftests, and add documentation with each erratum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/errata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/errata/abi-1.h -->
# sources/distributed-fs/ceph-client/security/landlock/errata/abi-1.h

## Purpose

This ABI errata header documents and registers erratum 3 for Landlock ABI 1: disconnected directory handling in rename/link scenarios.

## Important APIs, Types, and Functions

The file expands `LANDLOCK_ERRATUM(3)` under the ABI value supplied by `errata.h`. Its comment documents the issue, fix, and impact.

## Control Flow

When included by `errata.h` with `LANDLOCK_ERRATA_ABI` set to 1, it contributes an entry to `landlock_errata_init[]`. `setup.c` later turns this into the corresponding runtime bit.

## State and Persistence Behavior

No local state exists. Runtime persistence is the global errata bitmask.

## Dependencies and Integration Points

This ties to filesystem refer checks in `fs.c`, especially disconnected directory walks that combine mount-root and filesystem-root restrictions.

## Risks and Test Signals

The behavioral risk is access widening through reparenting disconnected directories on kernels without the fix. Test bind mounts, disconnected dentries, rename/link with `LANDLOCK_ACCESS_FS_REFER`, and ABI errata reporting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/errata/abi-1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/errata/abi-4.h -->
# sources/distributed-fs/ceph-client/security/landlock/errata/abi-4.h

## Purpose

This ABI errata header documents and registers erratum 1 for Landlock ABI 4: TCP socket identification for network access rights.

## Important APIs, Types, and Functions

The file expands `LANDLOCK_ERRATUM(1)` and documents that non-TCP stream protocols should not be restricted by TCP-specific access rights.

## Control Flow

Included by `errata.h` with ABI 4, it contributes an entry consumed by `setup.c` during `compute_errata()`.

## State and Persistence Behavior

No local runtime state exists; the global errata bitmask records the fix.

## Dependencies and Integration Points

This relates directly to `net.c`, where `hook_socket_bind()` and `hook_socket_connect()` call `sk_is_tcp()` before enforcing `LANDLOCK_ACCESS_NET_BIND_TCP` and `LANDLOCK_ACCESS_NET_CONNECT_TCP`.

## Risks and Test Signals

Without the fix, SMC, MPTCP, SCTP, or other stream protocols could be denied by TCP rules. Test non-TCP stream bind/connect under network rules and verify ABI errata reporting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/errata/abi-4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/errata/abi-6.h -->
# sources/distributed-fs/ceph-client/security/landlock/errata/abi-6.h

## Purpose

This ABI errata header documents and registers erratum 2 for Landlock ABI 6: overly restrictive scoped signal handling between threads in the same process.

## Important APIs, Types, and Functions

The file expands `LANDLOCK_ERRATUM(2)` and explains the user-visible effect for multithreaded programs using Landlock thread synchronization.

## Control Flow

Included by `errata.h` with ABI 6, it adds an entry to the boot-time errata table. `setup.c` publishes the corresponding bit when ABI compatibility allows it.

## State and Persistence Behavior

No local runtime state exists. The global errata bitmask records whether the fix is available.

## Dependencies and Integration Points

The fix relates to scoped signal checks in Landlock task/file ownership code, including same-thread-group allowances in `fs.c` and task hooks outside this work item.

## Risks and Test Signals

Without the fix, multithreaded programs that synchronize Landlock policies across existing threads may lose expected intra-process signal behavior. Test `LANDLOCK_SCOPE_SIGNAL`, sibling threads in different domains, `pthread_kill`, async I/O ownership, and ABI errata reporting.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/errata/abi-6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/fs.c -->
# sources/distributed-fs/ceph-client/security/landlock/fs.c

## Purpose

`fs.c` is Landlock's filesystem enforcement core. It manages inode-backed Landlock objects, adds path-beneath rules, walks filesystem hierarchies to evaluate per-layer access, mediates mount namespace changes, path operations, open/truncate/device ioctl, Unix socket path resolution, and file-owner signal scope state.

## Important APIs, Types, and Functions

Object/rule helpers include `release_inode()`, `get_inode_object()`, `landlock_append_fs_rule()`, and `find_rule()`. IOCTL helpers `is_masked_device_ioctl()` and `is_masked_device_ioctl_compat()` define device ioctl commands not restricted by `LANDLOCK_ACCESS_FS_IOCTL_DEV`. Access-check helpers include `may_refer()`, `no_more_access()`, `scope_to_request()`, `is_eacces()`, `is_access_to_paths_allowed()`, `current_check_access_path()`, `collect_domain_accesses()`, and `current_check_refer_path()`. LSM hooks cover inode free, superblock delete, mount/move/umount/remount/pivotroot, path create/remove/link/rename/truncate, Unix socket lookup, file allocation/open/truncate/ioctl/fowner/free, and `landlock_add_fs_hooks()` registers them.

## Control Flow

Adding a filesystem rule validates that non-directories only receive file-applicable rights, upgrades relative rights to absolute rights for unhandled access, obtains or creates an inode object, and inserts a rule into the ruleset tree. Normal access checks first ask whether the current or file credential has a domain handling the requested fs bits. If yes, `landlock_init_layer_masks()` creates per-layer denied masks and `is_access_to_paths_allowed()` walks from the target path up through parents and mount points, unmasking access where rules grant it. If all layers are satisfied, access is allowed; otherwise audit details are filled and `-EACCES` is returned.

Link and rename use `current_check_refer_path()`, which compares source and destination hierarchies to avoid access-right widening. It collects domain access matrices for source and destination parents, considers child access for moved/exchanged dentries, checks whether the destination is at least as restrictive, and prioritizes `-EACCES` for missing create/remove rights over `-EXDEV` for unsafe reparenting. Mount topology hooks deny mount namespace changes by any subject whose domain handles filesystem rights, because topology changes can reveal new paths. Open records the rights available at open time in the file security blob, including optional truncate and device-ioctl rights; later truncate/ioctl hooks enforce those saved rights even if the current task is different.

## State and Persistence Behavior

Inodes have weak RCU pointers to `landlock_object`; rules hold strong object references. `hook_sb_delete()` and `release_inode()` coordinate inode/object disassociation with spinlocks, RCU assignment, `iput()`, and a superblock `inode_refs` wait counter. File blobs persist `allowed_access`, audit deny masks, and fowner subject state. Rulesets/domains are immutable while enforced; access matrices are stack-temporary during checks. Audit state is updated through `landlock_log_denial()`.

## Dependencies and Integration Points

The file depends on VFS dentries, paths, mount walking, LSM hooks, file modes, ioctl command definitions, AF_UNIX socket lookup, Landlock rulesets/objects/credentials/audit, and superblock/inode/file LSM blobs declared in `fs.h`. It integrates with syscalls implemented elsewhere through `landlock_append_fs_rule()`.

## Risks and Test Signals

This file is high risk because small path-walk or lifetime changes can create sandbox escapes, false denials, inode reference leaks, or unmount hangs. Disconnected dentries, bind mounts, mount roots, `RENAME_EXCHANGE`, `O_PATH`, optional rights captured at open, file descriptors passed across domains, and device ioctl allowlists are sensitive. Test Landlock selftests for file hierarchy, refer, truncate, ioctl, Unix socket path resolution, mount operations, open-file transfer, KUnit suite `landlock_fs`, and stress tests with concurrent unmount/rule insertion.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/fs.h -->
# sources/distributed-fs/ceph-client/security/landlock/fs.h

## Purpose

`fs.h` declares Landlock filesystem LSM blob types and public filesystem helpers. It ties inode, file, and superblock objects to Landlock state.

## Important APIs, Types, and Functions

`struct landlock_inode_security` stores an RCU weak pointer to the inode's Landlock object. `struct landlock_file_security` stores `allowed_access`, optional audit `deny_masks` and `fown_layer`, and the `fown_subject` credential snapshot used for signal scope. `struct landlock_superblock_security` tracks pending inode references during unmount cleanup. Accessors `landlock_file()`, `landlock_inode()`, and `landlock_superblock()` index LSM blobs. `landlock_add_fs_hooks()` and `landlock_append_fs_rule()` are exported to setup/syscall code.

## Control Flow

Setup registers filesystem hooks through `landlock_add_fs_hooks()`. Syscall code adds path rules through `landlock_append_fs_rule()`. Enforcement code populates file and inode blobs through hooks in `fs.c`.

## State and Persistence Behavior

Inode object pointers are weak and RCU-protected; rules hold strong references. File security state persists for the lifetime of an open file and is intentionally used for later operations. Superblock state persists until unmount cleanup completes.

## Dependencies and Integration Points

The header depends on Linux fs structures, RCU, Landlock credentials, rulesets, and setup blob sizes. It must match `landlock_blob_sizes` in `setup.c`.

## Risks and Test Signals

Blob layout mismatches corrupt LSM state. File `allowed_access` semantics are user-visible for descriptor passing. Test with open/truncate/ioctl after policy changes, unmount of inodes referenced by rules, and audit-enabled fowner signal scenarios.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/id.c -->
# sources/distributed-fs/ceph-client/security/landlock/id.c

## Purpose

`id.c` implements audit-only unique ID generation for Landlock domains. IDs are 64-bit, boot-randomized, monotonic, and slightly randomized between allocations to reduce predictability.

## Important APIs, Types, and Functions

`next_id` is the global atomic counter. `init_id()` initializes a counter to `2^32 + random_32bits` using `cmpxchg` so initialization happens once. `landlock_init_id()` seeds `next_id`. `get_id_range()` returns the current ID and increments by `number_of_ids + random_4bits`. `landlock_get_id_range()` uses a random low nibble for blurring. KUnit tests cover initialization and step behavior.

## Control Flow

At LSM init, `landlock_init_id()` seeds the counter. Domain creation requests one ID through `landlock_get_id_range(1)`. Atomic fetch-add returns a unique range start and reserves space for future IDs.

## State and Persistence Behavior

State is an in-memory atomic counter for the running boot. IDs are not persisted across reboots, but the randomized high starting range reduces collision and information leakage across logs.

## Dependencies and Integration Points

The file is compiled under `CONFIG_AUDIT` and used by `domain.c`. It depends on random helpers, atomics, and KUnit for tests.

## Risks and Test Signals

Failure to initialize would yield ID 0 warnings. Overflow is theoretically possible but made impractical by a large range and randomized stepping. Test KUnit suite `landlock_id`, boot audit domain creation, and repeated restrict-self ID uniqueness.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/id.h -->
# sources/distributed-fs/ceph-client/security/landlock/id.h

## Purpose

`id.h` declares audit-only Landlock ID initialization and allocation functions, with no-op stubs when audit is disabled.

## Important APIs, Types, and Functions

With `CONFIG_AUDIT`, it declares `landlock_init_id()` and `landlock_get_id_range()`. Without audit, only an inline empty `landlock_init_id()` exists because IDs are unused.

## Control Flow

Setup calls `landlock_init_id()` unconditionally; compilation selects real or stub behavior. Audit domain creation calls `landlock_get_id_range()`.

## State and Persistence Behavior

The header stores no state. It gates access to `id.c`'s counter.

## Dependencies and Integration Points

It integrates `setup.c` and `domain.c` without forcing audit code into non-audit builds.

## Risks and Test Signals

Header/stub mismatch could break non-audit builds. Test `CONFIG_AUDIT=y` and `CONFIG_AUDIT=n` build combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/limits.h -->
# sources/distributed-fs/ceph-client/security/landlock/limits.h

## Purpose

`limits.h` defines Landlock internal limits and masks derived from UAPI access bits.

## Important APIs, Types, and Functions

The file sets `LANDLOCK_MAX_NUM_LAYERS` to 16 and `LANDLOCK_MAX_NUM_RULES` to `U32_MAX`. It derives last, mask, and count constants for filesystem access, network access, scopes, and restrict-self flags: `LANDLOCK_MASK_ACCESS_FS`, `LANDLOCK_NUM_ACCESS_FS`, `LANDLOCK_MASK_ACCESS_NET`, `LANDLOCK_NUM_ACCESS_NET`, `LANDLOCK_MASK_SCOPE`, `LANDLOCK_NUM_SCOPE`, and `LANDLOCK_MASK_RESTRICT_SELF`.

## Control Flow

There is no runtime control flow. Other code uses these constants for validation, static assertions, array sizes, and mask clipping.

## State and Persistence Behavior

No state exists. The constants define ABI-related in-kernel capacity.

## Dependencies and Integration Points

It depends on UAPI Landlock constants. It feeds access masks, ruleset allocation, audit string tables, and syscall validation.

## Risks and Test Signals

When new UAPI bits are added, failing to update `LANDLOCK_LAST_*` constants breaks validation and static assertions. Test new ABI selftests, audit string array sizes, and compile-time checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/limits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/net.c -->
# sources/distributed-fs/ceph-client/security/landlock/net.c

## Purpose

`net.c` implements Landlock TCP port access control. It lets rulesets allow bind/connect rights for specific TCP ports and enforces these rules through socket bind/connect LSM hooks.

## Important APIs, Types, and Functions

`landlock_append_net_rule()` inserts a `LANDLOCK_KEY_NET_PORT` rule keyed by network-order port. `current_check_access_socket()` parses socket addresses, validates family/length consistency, builds audit network data, initializes per-layer masks, checks matching port rules, logs denials, and returns `-EACCES` when needed. `hook_socket_bind()` enforces `LANDLOCK_ACCESS_NET_BIND_TCP` for TCP sockets. `hook_socket_connect()` enforces `LANDLOCK_ACCESS_NET_CONNECT_TCP`. `landlock_add_net_hooks()` registers the socket hooks.

## Control Flow

Syscall code adds port rules with relative access rights upgraded to include unhandled net rights. At bind/connect time, non-TCP sockets are ignored. The checker handles `AF_UNSPEC`, IPv4, and IPv6 address forms, preserving network-stack error semantics for invalid family or length cases where possible. It finds the rule for the port, initializes layer masks for the requested right, unsets allowed layers via `landlock_unmask_layers()`, and denies/logs if any layer remains.

## State and Persistence Behavior

Network rules are stored in the ruleset red-black tree keyed by `htons(port)`. No per-socket Landlock state is stored. Audit data is transient.

## Dependencies and Integration Points

The file depends on `CONFIG_INET`, socket structures, IPv4/IPv6 sockaddr layouts, `sk_is_tcp()`, Landlock rulesets/credentials/audit, and LSM socket hooks. It is omitted with stubs when INET is disabled.

## Risks and Test Signals

Family handling is security and compatibility sensitive, especially `AF_UNSPEC`, IPv6 length checks, and non-TCP stream protocols. Tests should cover TCP bind/connect allow/deny, port byte order, IPv4/IPv6, invalid addrlen, `AF_UNSPEC`, MPTCP/SMC/SCTP non-enforcement, and audit records.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/net.h -->
# sources/distributed-fs/ceph-client/security/landlock/net.h

## Purpose

`net.h` declares Landlock network hook registration and network rule insertion, with stubs for non-INET builds.

## Important APIs, Types, and Functions

When `CONFIG_INET` is enabled, it declares `landlock_add_net_hooks()` and `landlock_append_net_rule()`. Otherwise `landlock_add_net_hooks()` is an empty inline and `landlock_append_net_rule()` returns `-EAFNOSUPPORT`.

## Control Flow

Setup calls hook registration unconditionally through this header. Syscall code can attempt to add network rules and receive a clear unsupported-family error when INET support is absent.

## State and Persistence Behavior

No state is stored in the header.

## Dependencies and Integration Points

It depends on common Landlock declarations, rulesets, and setup state. The real implementation is in `net.c`.

## Risks and Test Signals

Stub behavior must match syscall error expectations. Build and selftest both INET and non-INET configurations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/object.c -->
# sources/distributed-fs/ceph-client/security/landlock/object.c

## Purpose

`object.c` implements generic Landlock object lifetime management for kernel objects referenced by rules, currently primarily inodes. It provides reference counting, locking, underlying-object release callbacks, and RCU freeing.

## Important APIs, Types, and Functions

`landlock_create_object()` allocates and initializes a `struct landlock_object` with usage count, spinlock, underops, and underlying object pointer. `landlock_put_object()` decrements usage and, when it reaches zero, locks the object, calls `underops->release()` with the lock held, and frees the object via `kfree_rcu()`.

## Control Flow

Rules and temporary operations call `landlock_get_object()` to pin objects and `landlock_put_object()` to release them. The final put uses `refcount_dec_and_lock()` so the transition to zero synchronizes with weak-pointer cleanup in filesystem code.

## State and Persistence Behavior

Object state persists while at least one rule or operation references it. The underlying object pointer is cleared by provider-specific release logic. RCU freeing allows lockless readers to observe object metadata safely while references drain.

## Dependencies and Integration Points

The generic object layer depends on provider callbacks declared in `object.h`; `fs.c` supplies inode release operations. It integrates with ruleset rule keys.

## Risks and Test Signals

Final put can sleep because provider release may call `iput()`, so callers must be in sleepable context. Lock ordering with inode locks is critical. Test concurrent rule insertion/removal, unmount cleanup, and KASAN/KCSAN lifetime stress.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/object.h -->
# sources/distributed-fs/ceph-client/security/landlock/object.h

## Purpose

`object.h` defines the generic Landlock object wrapper used to attach rules to underlying kernel objects without depending on the underlying object's lifetime alone.

## Important APIs, Types, and Functions

`struct landlock_object_underops` defines a `release()` callback. `struct landlock_object` contains a `usage` refcount, `lock`, `underobj` pointer, and a union for RCU freeing or underops pointer. `landlock_create_object()`, `landlock_put_object()`, and inline `landlock_get_object()` are the public object lifetime APIs.

## Control Flow

Provider code creates objects for underlying resources. Rules pin them. Final put calls provider release before RCU freeing, allowing weak references from underlying resources to be cleared.

## State and Persistence Behavior

The object persists independently of the underlying object while rules reference it. `underobj` marks whether it is still tied to the underlying kernel structure.

## Dependencies and Integration Points

The header is consumed by ruleset and filesystem code. It relies on refcount, spinlock, and RCU primitives.

## Risks and Test Signals

Lock ordering is documented: inode lock nests inside object lock. Violating this can deadlock. Test with lockdep, unmount/rule races, and object reference leak detection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/object.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/ruleset.c -->
# sources/distributed-fs/ceph-client/security/landlock/ruleset.c

## Purpose

`ruleset.c` implements Landlock ruleset storage, rule insertion, domain creation by merging nested rulesets, ruleset inheritance, lookup, and per-layer mask initialization/unmasking. It is the policy data-structure core of Landlock.

## Important APIs, Types, and Functions

`create_ruleset()` allocates a ruleset with a flexible `access_masks[]` layer array. `landlock_create_ruleset()` creates a one-layer mutable ruleset. `create_rule()`, `insert_rule()`, and `landlock_insert_rule()` manage red-black tree rules for inode objects and network ports. `merge_tree()`, `merge_ruleset()`, `inherit_tree()`, and `inherit_ruleset()` build immutable domains from a parent domain plus a new ruleset. `landlock_merge_ruleset()` creates the new domain and hierarchy. `landlock_find_rule()`, `landlock_unmask_layers()`, and `landlock_init_layer_masks()` are hot-path lookup/check helpers. `landlock_put_ruleset()` and `landlock_put_ruleset_deferred()` free rulesets synchronously or through workqueue.

## Control Flow

Unenforced rulesets have one layer at level 0 and can be extended by adding rules for the same object/port, OR-ing access rights. When `restrict_self` merges a ruleset into a domain, a new ruleset is allocated with parent layers plus one new layer, parent rules are copied, parent hierarchy is referenced, the new ruleset's handled masks are upgraded, and each new rule is inserted as a layer with a real level. Matching existing domain rules are replaced with a new rule whose layer stack is extended. Access checks initialize masks for layers that handle the requested bit and clear them with rule layers until no unfulfilled access remains.

## State and Persistence Behavior

Rulesets are reference-counted. Enforced domains are immutable and carry a hierarchy pointer. Rules are stored in red-black trees keyed by object pointer or raw port data and own references to object keys when applicable. Deferred freeing is used from credential cleanup where sleeping may be unsafe.

## Dependencies and Integration Points

The file depends on object lifetime, domain hierarchy, access masks, red-black trees, workqueues, mutexes, and optional INET support. It is called by syscalls, filesystem/network rule appenders, and enforcement hooks.

## Risks and Test Signals

Layer numbering, OR-versus-AND semantics, and object reference handling are critical. Bugs can grant access in nested domains, leak rules, or fail with use-after-free. Test nested restrict-self composition, duplicate rule insertion, max layer and max rule limits, inode and net-port lookup, deferred freeing, and Landlock KUnit/selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/ruleset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/ruleset.h -->
# sources/distributed-fs/ceph-client/security/landlock/ruleset.h

## Purpose

`ruleset.h` declares the Landlock policy data model: layers, rule keys, rules, rulesets/domains, lifetime helpers, mask accessors, and lookup/check APIs.

## Important APIs, Types, and Functions

`struct landlock_layer` stores a layer level and allowed access bits. `union landlock_key` holds an object pointer or raw data. `enum landlock_key_type` identifies inode and network-port trees. `struct landlock_rule` stores an RB node, key, and flexible layer stack. `struct landlock_ruleset` stores inode and optional network RB roots, hierarchy, refcount/lock/rule count/layer count, and per-layer access masks. Public APIs include `landlock_create_ruleset()`, `landlock_insert_rule()`, `landlock_merge_ruleset()`, `landlock_find_rule()`, `landlock_unmask_layers()`, and `landlock_init_layer_masks()`.

## Control Flow

Callers create a mutable one-layer ruleset, append rules, then merge it with a parent domain to produce a new immutable domain. Enforcement hooks use accessors to build layer masks and find matching rules by object or port key.

## State and Persistence Behavior

Rulesets/domains are reference-counted and may be freed synchronously or deferred. Access masks are immutable after domain creation. Rule layer stacks are persistent until ruleset free.

## Dependencies and Integration Points

The header connects filesystem, network, syscall, credential, and task code. It depends on object wrappers, access masks, mutexes, RB trees, workqueues, and optional INET compilation.

## Risks and Test Signals

Flexible array sizing and layer count limits must stay aligned with `limits.h`. File and network key types must use compatible tree roots. Test compile-time assertions, max layer boundaries, and both `CONFIG_INET` modes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/ruleset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/setup.c -->
# sources/distributed-fs/ceph-client/security/landlock/setup.c

## Purpose

`setup.c` registers Landlock as an LSM, declares its blob sizes, computes runtime errata bits, initializes ID generation, registers hooks, and marks the subsystem initialized.

## Important APIs, Types, and Functions

`landlock_initialized` gates cleanup paths before full init. `landlock_lsmid` names and IDs the LSM. `landlock_blob_sizes` declares credential, file, inode, and superblock blob sizes. `landlock_errata` stores runtime errata bits. `compute_errata()` consumes `landlock_errata_init[]`. `landlock_init()` registers credential, task, filesystem, and network hooks, initializes IDs, and sets initialized state. `DEFINE_LSM(LANDLOCK_NAME)` binds the init function and blob sizes to the LSM framework.

## Control Flow

At LSM initialization, `compute_errata()` validates errata ABI entries and sets the bitmask. Hook registration functions are called in sequence. Audit ID state is initialized through real or stub `landlock_init_id()`. The subsystem is then marked initialized and logs readiness.

## State and Persistence Behavior

Blob sizes become part of LSM-managed object allocation. `landlock_errata` and `landlock_initialized` are `__ro_after_init`. Runtime domains and rules are created later by syscalls.

## Dependencies and Integration Points

The file depends on LSM infrastructure, UAPI LSM ID, Landlock headers for every hook area, errata table, and optional stubs for networking/audit.

## Risks and Test Signals

Blob-size mismatches corrupt credentials/files/inodes/superblocks. Hook registration order should remain consistent with dependencies. Test boot with Landlock enabled in `CONFIG_LSM`, errata bit reporting, audit and non-audit builds, and early unmount paths before initialization.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/setup.h -->
# sources/distributed-fs/ceph-client/security/landlock/setup.h

## Purpose

`setup.h` declares global Landlock setup state shared by hook modules and accessors.

## Important APIs, Types, and Functions

It declares `landlock_abi_version`, `landlock_initialized`, `landlock_errata`, `landlock_blob_sizes`, and `landlock_lsmid`.

## Control Flow

Other files use these declarations to index LSM blobs, guard cleanup before initialization, register hook lists with the correct LSM ID, and expose ABI/errata state.

## State and Persistence Behavior

The variables are defined in `setup.c` or syscall code and persist for the running kernel. Some are read-only after init.

## Dependencies and Integration Points

The header depends on LSM hook definitions and is included by most Landlock modules.

## Risks and Test Signals

Declaration/definition mismatch or wrong blob sizes can break all Landlock hooks. Build with varied optional configs and run boot smoke tests plus Landlock selftests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/landlock/setup.h -->
