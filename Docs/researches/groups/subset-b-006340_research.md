# subset-b-006340 Research

Grouped research for the requested source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_policy.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_policy.c

Purpose: Implements IMA policy construction, parsing, matching, readback, and activation. It owns the built-in TCB, appraisal, secure-boot, and critical-data rule arrays and converts boot arguments, architecture policy strings, and runtime policy writes into `struct ima_rule_entry` lists.

Important APIs/types/functions: `struct ima_rule_entry` captures action, match flags, hook, mask, fs identity, uid/gid/file-owner comparisons, PCR, allowed xattr hash algorithms, LSM conditions, keyring/label lists, and template override. Public entry points include `ima_init_policy()`, `ima_match_policy()`, `ima_update_policy_flags()`, `ima_parse_add_rule()`, `ima_check_policy()`, `ima_update_policy()`, `ima_delete_rules()`, policy seq-file helpers under `CONFIG_IMA_READ_POLICY`, `ima_lsm_policy_change()`, and `ima_appraise_signature()`.

Control flow: Boot setup handlers parse `ima_tcb`, `ima_policy=`, and `ima_appraise_tcb`, then `ima_init_policy()` populates default/custom lists in priority order: default exclusions, measurement policy, architecture rules, secure boot/build appraisal, appraisal TCB, and critical-data rules. Runtime writes go through `ima_parse_add_rule()`, which allocates an entry, tokenizes a line with `match_token()`, validates hook/action/flag compatibility, then links it to `ima_temp_rules`. `ima_update_policy()` splices temporary rules into `ima_policy_rules`, switches the active RCU pointer from defaults to custom rules, refreshes global flags, frees architecture entries, and processes queued keys.

State and persistence: Active policy is an RCU pointer to either `ima_default_rules` or `ima_policy_rules`; updates append or replace list heads but do not remove active rules while readers run. `ima_policy_flag`, `temp_ima_appraise`, `build_ima_appraise`, and `ima_setxattr_allowed_hash_algorithms` cache derived policy state. LSM rule data can be rebuilt after LSM policy reloads via notifier-driven RCU replacement.

Dependencies and integration: Integrates with LSM label APIs, audit logging, securityfs policy writes/readback, IMA template descriptors, hash algorithm availability, architecture policy providers, key measurement queue flushing, and kernel lockdown checks. Rule matching is called from IMA hook paths with inode, idmap, credentials, LSM properties, hook, mask, optional keyring/label data, and optional algorithm allowlist.

Risks and test signals: High-risk areas are parser token ordering, accepted flag combinations per hook, RCU lifetime of shallow-copied LSM/template/keyring fields, fallback handling for stale LSM rules, and single-active `SETXATTR_CHECK` hash allowlist semantics. Tests should cover malformed policies, duplicate fields, unsupported algorithms, fsuuid/fsname/subtype rules, uid/gid comparison operators, `KEY_CHECK` and `CRITICAL_DATA` list matching, read-policy output round-trips, and policy replacement under concurrent matchers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_queue.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_queue.c

Purpose: Maintains the append-only IMA measurement list, duplicate-detection hash table, PCR extension path, kexec serialization sizing, reboot suspension, and violation digest initialization.

Important APIs/types/functions: Exports `ima_measurements`, `ima_htable`, `ima_add_template_entry()`, `ima_restore_measurement_entry()`, `ima_get_binary_runtime_size()`, `ima_init_reboot_notifier()`, and `ima_init_digests()`. Internals include `ima_lookup_digest_entry()`, `ima_add_digest_entry()`, `ima_pcr_extend()`, and the reboot notifier.

Control flow: `ima_add_template_entry()` locks `ima_extend_list_mutex`, refuses additions after measurements are suspended, checks the hash table for existing non-violation digests unless disabled, links a queue entry to `ima_measurements`, optionally indexes it by digest, extends the selected TPM PCR, and audits the result. Violations use a preallocated all-0xff digest bank array to invalidate PCRs. Kexec restore uses `ima_restore_measurement_entry()` to relink entries without PCR extension.

State and persistence: Measurements are never removed during a boot cycle. `binary_runtime_size` tracks serialized list size for kexec handoff. `ima_measurements_suspended` prevents late logging once reboot/kexec has started. The hash table stores digest/PCR pairs for duplicate suppression.

Dependencies and integration: Depends on TPM PCR APIs, IMA template entries, audit helpers, RCU list traversal, and reboot notifiers. It is consumed by measurement display, kexec restore/save code, and all IMA measurement producers.

Risks and test signals: Watch for hash-table duplicate false positives across PCRs, memory accounting overflow, lock ordering around TPM calls, reboot-time races, and correct audit causes for `hash_exists`, suspended measurements, ENOMEM, and TPM errors. Tests should exercise duplicate measurement suppression, violation extension, TPM absent behavior, and kexec restore sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_queue_keys.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_queue_keys.c

Purpose: Defers asymmetric key measurements until a custom IMA policy is loaded or a timeout proves none will be loaded.

Important APIs/types/functions: Provides `ima_init_key_queue()`, `ima_queue_key()`, `ima_process_queued_keys()`, and `ima_should_queue_key()`. Uses `struct ima_key_entry` from IMA headers, `ima_keys_lock`, `ima_keys`, delayed work `ima_keys_delayed_work`, and `timer_expired`.

Control flow: At init, a delayed worker is scheduled for five minutes. `ima_queue_key()` copies the key payload and keyring description, then enqueues the entry only while `ima_process_keys` is false. `ima_update_policy()` later calls `ima_process_queued_keys()`, which atomically flips processing mode, cancels the timeout if it has not fired, measures queued keys with `process_buffer_measurement(... KEY_CHECK ...)`, then frees all entries. If the timer fires first, queued keys are discarded without measurement.

State and persistence: Queued keys live only in memory. Once `ima_process_keys` becomes true, it never returns to queueing mode, so future keys are measured immediately by the normal key measurement path.

Dependencies and integration: Integrated with IMA policy loading, keyring notifications, asymmetric key payloads, workqueues, user namespace idmaps, and integrity audit for allocation failures.

Risks and test signals: Main risks are missed measurements when policy loads close to timeout, allocation failure audit correctness, list lifetime during concurrent queue/process calls, and copying untrusted payload lengths. Tests should simulate policy load before and after timeout, concurrent key arrivals, and OOM cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_queue_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_template.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_template.c

Purpose: Defines supported IMA template descriptors and fields, handles boot-time template selection/custom formats, initializes template field arrays, and restores template metadata from kexec-carried measurement lists.

Important APIs/types/functions: Built-in templates include `ima`, `ima-ng`, `ima-sig`, `ima-ngv2`, `ima-sigv2`, `ima-buf`, `ima-modsig`, and `evm-sig`. Public helpers include `ima_template_has_modsig()`, `lookup_template_desc()`, `template_desc_init_fields()`, `ima_init_template_list()`, `ima_template_desc_current()`, `ima_template_desc_buf()`, `ima_init_template()`, and `ima_restore_measurement_list()`.

Control flow: `ima_template=` selects an existing descriptor after validating SHA1/MD5 constraints for legacy `ima`; `ima_template_fmt=` validates a custom field string and binds it to the placeholder descriptor. `ima_init_template()` initializes the current template and the buffer template. Kexec restore parses a serialized header, rejects incompatible versions and legacy `ima`, resolves or creates template descriptors, initializes fields, parses field data, recalculates digests when needed, and restores queue entries without extending PCRs.

State and persistence: Template descriptors are held in the RCU-protected `defined_templates` list. Field arrays are allocated once per descriptor and reused. Restored custom descriptors are dynamically allocated and appended to the descriptor list.

Dependencies and integration: Uses field initializers/show functions from `ima_template_lib.c`, measurement queue restore, TPM bank sizing, canonical endian mode, and boot parameter parsing.

Risks and test signals: Risks include template format validation holes, maximum field/name length checks, kexec buffer bounds enforcement, endian conversion mistakes, and memory leaks for partially restored entries. Tests should include custom format validation, modsig template detection, kexec restore with truncated buffers, unknown restored formats, and unsupported legacy template restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_template.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_template_lib.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_template_lib.c

Purpose: Implements serialization, display, parsing, and field initialization helpers for all supported IMA measurement template fields.

Important APIs/types/functions: Provides show functions for digest/string/signature/buffer/uint fields, `ima_parse_buf()`, digest initializers (`ima_eventdigest_init`, `_ng_init`, `_ngv2_init`, `_modsig_init`), event name initializers, signature/buffer/modsig/EVM signature field initializers, inode DAC fields, and protected xattr field initializers.

Control flow: Field initializers populate `struct ima_field_data` with allocated buffers using `ima_write_template_field_data()`, which NUL-terminates string data and replaces spaces with underscores for ASCII measurement parsing. Digest initialization chooses legacy, algorithm-prefixed, or type+algorithm-prefixed formats; violation events reserve zero/empty digest-sized fields. Display helpers render either ASCII or binary, respecting canonical endian format for integer field lengths and values. `ima_parse_buf()` walks serialized length-prefixed fields with optional fixed-length masks and strict end/field enforcement.

State and persistence: It allocates per-entry template field data but owns no global state. It depends on `ima_canonical_fmt`, `ima_hash_algo`, event data, and file xattrs at initialization time.

Dependencies and integration: Integrates with fs-verity digest type signaling, modsig helpers, EVM protected xattr readers, file hash calculation, boot aggregate calculation, seq_file output, and kexec restore parsing.

Risks and test signals: Important risks are bounds arithmetic in `ima_parse_buf()`, digest format compatibility, silent zero-length fields for missing optional data, xattr allocation failures returning success with empty fields, and canonical endian handling. Tests should cover ASCII/binary rendering, filenames with spaces, violation records, modsig digest/raw signature fields, EVM portable signatures, protected xattr lists, and malformed serialized buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_template_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_template_lib.h -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_template_lib.h

Purpose: Declares the IMA template field library interface shared by template descriptor management and measurement rendering/restoration code.

Important APIs/types/functions: Defines `ENFORCE_FIELDS` and `ENFORCE_BUFEND` parse flags and prototypes for field show functions, `ima_parse_buf()`, and all event field initializers for digests, names, signatures, buffers, inode uid/gid/mode, and protected xattr names/lengths/values.

Control flow: The header has no runtime flow but establishes the function table contract used by `supported_fields[]` in `ima_template.c`; each field descriptor maps a field id to an initializer and a display function declared here.

State and persistence: No persistent state. The declared functions allocate or display per-measurement field data owned by template entries.

Dependencies and integration: Includes `ima.h` and `linux/seq_file.h`, exposing APIs to IMA template core while hiding implementation details in `ima_template_lib.c`.

Risks and test signals: Interface risks are prototype drift against `supported_fields[]` and parse flag misuse by restore code. Build tests catch signature mismatch; runtime tests should validate field ids and parsing behavior through template initialization and kexec restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_template_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/integrity.h -->
# sources/distributed-fs/ceph-client/security/integrity/integrity.h

Purpose: Central internal header for Linux integrity subsystems, defining xattr/signature data formats, keyring ids, certificate/signature loading APIs, asymmetric verification hooks, IMA/EVM X.509 loaders, audit helpers, and platform/machine keyring entry points.

Important APIs/types/functions: Defines `enum evm_ima_xattr_type`, `struct evm_ima_xattr_data`, `struct evm_xattr`, `struct ima_digest_data`, `struct ima_max_digest_data`, `struct signature_v2_hdr`, and `struct ima_file_id`. Declares `integrity_kernel_read()`, integrityfs init/fini, `integrity_digsig_verify()`, `integrity_modsig_verify()`, `integrity_init_keyring()`, `integrity_load_x509()`, `integrity_load_cert()`, `asymmetric_verify*()`, `ima_modsig_verify()`, `integrity_audit_*()`, and platform/machine keyring loaders with stubs for disabled configs.

Control flow: Header-only configuration selects real functions or no-op/-EOPNOTSUPP stubs based on build options, allowing IMA, EVM, and platform cert code to compile under many feature combinations.

State and persistence: Defines keyring numeric ids for EVM, IMA, platform, and machine keyrings. Data structures describe persistent xattr and signature wire formats.

Dependencies and integration: Bridges integrity, audit, keyrings, asymmetric crypto, secure boot, IMA appraisal, EVM, and platform certificate import.

Risks and test signals: Risks are ABI/layout drift in packed xattr/signature structures, stale stubs masking missing functionality, and keyring id mismatches. Tests should include structure offset/static assertions, disabled-config builds, signature verification, and xattr compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/integrity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/integrity_audit.c -->
# sources/distributed-fs/ceph-client/security/integrity/integrity_audit.c

Purpose: Provides common audit logging for integrity subsystem events such as IMA PCR updates, policy parsing, and data collection failures.

Important APIs/types/functions: `integrity_audit_setup()` handles the `integrity_audit=` boot parameter. `integrity_audit_msg()` is a convenience wrapper, and `integrity_audit_message()` builds the full audit record including pid, uid, auid, session, LSM context, operation, cause, command, optional file name, optional inode device/inode, result, and errno.

Control flow: Informational records are skipped unless global `integrity_audit_info` is enabled or the caller marks the record non-informational. Otherwise an audit buffer is allocated, populated, and ended.

State and persistence: Only persistent state is the boot-parameter-controlled `integrity_audit_info` flag.

Dependencies and integration: Used by IMA queue, policy, key queue, and template code; depends on audit context, current task credentials, inode metadata, and untrusted string audit helpers.

Risks and test signals: Risks include incorrect suppression of important events, missing errno propagation, unsafe string formatting, and NULL audit buffer handling. Tests should verify boot parameter behavior and representative records for success, failure, inode, and non-inode cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/integrity_audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/efi_parser.c -->
# sources/distributed-fs/ceph-client/security/integrity/platform_certs/efi_parser.c

Purpose: Parses EFI signature lists and dispatches certificate/hash elements to caller-selected handlers.

Important APIs/types/functions: Exports `parse_efi_signature_list(source, data, size, get_handler_for_guid)`, where the callback maps each `signature_type` GUID to an `efi_element_handler_t` or NULL.

Control flow: The parser iterates through sublists, copies each `efi_signature_list_t` header, validates total size, header size, element size, and divisibility, asks for a handler, skips uninterested lists, and invokes the handler for each element’s `signature_data` excluding the owner GUID header.

State and persistence: Stateless parser. Persistence depends on handlers adding certificates or hashes to keyrings/blacklists.

Dependencies and integration: Used by UEFI, powerpc secure variable, and other platform certificate loaders. Integrates with EFI GUID definitions and platform keyring/blacklist handlers.

Risks and test signals: Bounds validation is critical because firmware blobs are untrusted. Tests should include truncated list headers, overruns, zero/too-small element sizes, header padding, uninterested GUID skipping, mixed-list blobs, and exact-size termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/efi_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/keyring_handler.c -->
# sources/distributed-fs/ceph-client/security/integrity/platform_certs/keyring_handler.c

Purpose: Maps EFI signature-list GUIDs to handlers that load certificates into platform/machine/secondary keyrings or blacklist/revoke hashes and certificates.

Important APIs/types/functions: Provides `get_handler_for_db()`, `get_handler_for_mok()`, `get_handler_for_ca_keys()`, `get_handler_for_code_signing_keys()`, and `get_handler_for_dbx()`. Internal handlers call `mark_hash_blacklisted()`, `add_key_to_revocation_list()`, `add_to_platform_keyring()`, `add_to_machine_keyring()`, and `add_to_secondary_keyring()`.

Control flow: DB accepts X.509 certs into the platform keyring. MOK accepts X.509 certs into machine keyring when configured and `imputed_trust_enabled()` is true, otherwise platform keyring. CA and code-signing key databases route X.509 certs to machine and secondary keyrings respectively. DBX maps X.509 TBS hashes, executable hashes, and X.509 certs to blacklist/revocation handlers.

State and persistence: No local state beyond initdata GUID constants. Handlers persist data in global keyrings/blacklists.

Dependencies and integration: Invoked by EFI signature parser from UEFI and powerpc loaders. Depends on system keyring, blacklist, integrity keyring, and machine/platform keyring config.

Risks and test signals: Risks include trust-domain confusion for MOK, unsupported GUID silently skipped, and config-dependent handler changes. Tests should validate GUID-to-handler mapping for all supported GUIDs and machine-keyring fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/keyring_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/keyring_handler.h -->
# sources/distributed-fs/ceph-client/security/integrity/platform_certs/keyring_handler.h

Purpose: Internal platform certificate handler declarations and DMI quirk macro support for EFI/platform certificate loaders.

Important APIs/types/functions: Declares blacklist helpers and handler selector functions for db, MOK, CA keys, code-signing keys, and dbx. Defines `UEFI_QUIRK_SKIP_CERT(vendor, product)` if not already provided.

Control flow: No runtime flow. Consumers pass the declared handler selectors to `parse_efi_signature_list()`.

State and persistence: No state. It defines compile-time interface and DMI match helper data shape.

Dependencies and integration: Includes EFI types and is included by UEFI and powerpc certificate loaders and handler implementation.

Risks and test signals: Risks are declaration drift and quirk macro mismatch with DMI arrays. Build coverage across EFI and powerpc configurations is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/keyring_handler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_ipl_s390.c -->
# sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_ipl_s390.c

Purpose: Loads certificates from the s390 IPL report into the platform trusted keyring during late init.

Important APIs/types/functions: `load_ipl_certs()` walks `ipl_cert_list_addr`/`ipl_cert_list_size` from architecture boot data and calls `add_to_platform_keyring("IPL:db", ptr, len)` for each length-prefixed certificate.

Control flow: If no IPL certificate list address is present, it exits successfully. Otherwise it converts the physical address with `__va()`, iterates until the end pointer, reads an unsigned length, advances to certificate data, imports it, and advances by length.

State and persistence: No local persistent state. Imported certs persist in the platform keyring.

Dependencies and integration: s390 boot data, integrity platform keyring, and late initcall ordering after keyring initialization.

Risks and test signals: Risks include trusting malformed firmware length fields and lack of explicit bounds checks for each entry. Platform tests should cover empty list, single/multiple certs, and corrupted length data if fixture support exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_ipl_s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_powerpc.c -->
# sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_powerpc.c

Purpose: Loads powerpc secure variable certificate and revocation databases into keyrings/blacklists.

Important APIs/types/functions: `get_cert_list()` reads a named secure variable into kmalloc memory. `load_powerpc_certs()` handles db, dbx, trustedcadb, and moduledb and is registered with `late_initcall`.

Control flow: It requires `secvar_ops`, checks the firmware format string against supported OPAL/PLPKS secure boot formats, applies an 8-byte timestamp offset for PLPKS variables, reads each database, logs absent optional variables, parses EFI signature lists with the correct handler selector, frees buffers, and returns the last non-fatal parse/read status.

State and persistence: Local buffers are transient; parsed certificates and hashes persist in platform, machine, secondary, or blacklist keyrings.

Dependencies and integration: Depends on powerpc secure variable ops, secure boot formats, EFI signature parser, keyring handler selectors, and integrity keyring APIs.

Risks and test signals: Risks include offset/size underflow in `extract_esl`, unsupported format rejection, inconsistent error propagation across multiple variables, and malformed ESL parsing. Tests should use fake secvar ops for absent, error, unsupported, PLPKS-offset, and malformed database cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_powerpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_uefi.c -->
# sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_uefi.c

Purpose: Loads UEFI db/dbx/MokListRT/MokListXRT certificates and revocations into kernel keyrings and blacklists.

Important APIs/types/functions: Includes DMI `uefi_skip_cert` quirk table, `uefi_check_ignore_db()`, `get_cert_list()`, `load_moklist_certs()`, and `load_uefi_certs()` as a late initcall.

Control flow: `load_uefi_certs()` skips known Apple T2 systems, requires EFI get-variable support, optionally reads db unless `MokIgnoreDB` is set, reads dbx, and only when secure boot is enabled reads MokListXRT and MokListRT. `load_moklist_certs()` first tries the EFI MOKvar config table and falls back to the UEFI variable. Each blob is parsed by `parse_efi_signature_list()` with db, dbx, or MOK handlers and then freed.

State and persistence: Uses transient kmalloc buffers; imported certs/hashes persist in platform/machine keyrings or revocation/blacklist infrastructure.

Dependencies and integration: EFI runtime services, shim MOK variables, secure boot status, DMI quirks, keyring handlers, IMA secure boot policy inputs, and system keyrings.

Risks and test signals: Risks include firmware crashes mitigated by quirks, silent skip when variables are absent, secure-boot trust semantics for MOK, and buffer-size probing errors. Tests should cover quirk skip, `MokIgnoreDB`, missing variables, MOK table fallback, secure boot disabled behavior, and malformed ESL blobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/load_uefi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/machine_keyring.c -->
# sources/distributed-fs/ceph-client/security/integrity/platform_certs/machine_keyring.c

Purpose: Initializes and populates the machine keyring, used for machine-owner or platform-imputed trust.

Important APIs/types/functions: `machine_keyring_init()` initializes `INTEGRITY_KEYRING_MACHINE`. `add_to_machine_keyring()` imports certificates and falls back to the platform keyring on EFI systems when machine restrictions reject a key. `imputed_trust_enabled()` checks whether platform-provided imputed keys may be trusted, using MOK trust state on UEFI.

Control flow: The device initcall creates the keyring before late certificate loading. MOK trust is lazily cached by `trust_moklist()`, which checks for `MokListTrustedRT` in the EFI MOKvar table. Non-UEFI platforms allow imputed trust by default.

State and persistence: The initialized machine keyring persists globally. `trust_moklist()` caches `initialized` and `trust_mok` booleans.

Dependencies and integration: Depends on EFI MOK table helpers, integrity cert loading, platform keyring fallback, and key permission policy.

Risks and test signals: Risks include overly broad non-UEFI trust, fallback hiding machine restriction failures, and MOK trust cache timing. Tests should cover UEFI trusted/untrusted MOK, non-UEFI behavior, cert load failures, and fallback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/machine_keyring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/platform_keyring.c -->
# sources/distributed-fs/ceph-client/security/integrity/platform_certs/platform_keyring.c

Purpose: Initializes the platform keyring and provides an init-only helper to import firmware/platform certificates without validating their chain.

Important APIs/types/functions: `add_to_platform_keyring()` calls `integrity_load_cert(INTEGRITY_KEYRING_PLATFORM, ...)` with broad positional permissions minus setattr and user view permission. `platform_keyring_init()` initializes the keyring via `integrity_init_keyring()`.

Control flow: Device initcall creates the keyring before late platform cert loaders. Import failures are logged but not fatal to callers.

State and persistence: Platform keyring is global integrity state. This file does not keep local state.

Dependencies and integration: Used by UEFI, s390 IPL, powerpc secure variable, and machine fallback loaders. Depends on integrity keyring/cert APIs.

Risks and test signals: Risks include accepting firmware trust anchors without chain validation by design, late init ordering, and non-fatal load failures reducing available trust silently. Tests should verify keyring creation order and certificate import error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/platform_certs/platform_keyring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/Kconfig -->
# sources/distributed-fs/ceph-client/security/ipe/Kconfig

Purpose: Defines build-time configuration for the Integrity Policy Enforcement LSM and its optional trust providers/tests.

Important APIs/types/functions: `SECURITY_IPE` enables the LSM and selects crypto, PKCS#7, system verification, securityfs, audit, and optional dm-verity/fs-verity provider symbols. Other options include `IPE_BOOT_POLICY`, secondary/platform keyring policy signature verification, dm-verity root hash/signature properties, fs-verity digest/builtin signature properties, and `SECURITY_IPE_KUNIT_TEST`.

Control flow: Kconfig dependency/select relationships determine which LSM blob fields, property evaluators, integrity hooks, and parser tests compile.

State and persistence: No runtime state; `IPE_BOOT_POLICY` embeds an initial policy into generated source.

Dependencies and integration: Ties IPE to LSM, securityfs, audit, auditable syscalls, cryptographic verification, dm-verity, fs-verity, trusted keyrings, and KUnit.

Risks and test signals: Build matrix risk is high because property code is config-gated. Test signals are allmodconfig/allyesconfig/minimal builds and KUnit parser coverage with each provider combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/Makefile -->
# sources/distributed-fs/ceph-client/security/ipe/Makefile

Purpose: Builds IPE objects and generates a built-in boot policy source when configured.

Important APIs/types/functions: Defines `quiet_cmd_polgen`/`cmd_polgen` to run `scripts/ipe/polgen/polgen security/ipe/boot_policy.c $(CONFIG_IPE_BOOT_POLICY)`. Builds `boot_policy.o`, digest/eval/hooks/fs/ipe/policy/policy_fs/policy_parser/audit objects when `CONFIG_SECURITY_IPE=y`, and `policy_tests.o` for KUnit.

Control flow: Kbuild regenerates `boot_policy.c` when the policy generator or configured policy changes, tracks it as a target, and removes it via `clean-files`.

State and persistence: Generated `boot_policy.c` is build output, not source-controlled runtime state.

Dependencies and integration: Depends on kernel scripts, Kbuild, config symbols, and IPE boot policy embedding consumed by `ipe.c`.

Risks and test signals: Risks are stale boot policy generation and missing dependency rebuilds. Build tests should check empty and non-empty `CONFIG_IPE_BOOT_POLICY` paths plus clean target behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/audit.c -->
# sources/distributed-fs/ceph-client/security/ipe/audit.c

Purpose: Emits audit records for IPE access decisions, policy loads, policy activations, and enforcement-mode changes.

Important APIs/types/functions: Provides `ipe_audit_match()`, `ipe_audit_policy_load()`, `ipe_audit_policy_activation()`, and `ipe_audit_enforce()`. Internal helpers format rules, dm-verity/fs-verity digest properties, policy metadata, and SHA-256 policy digest.

Control flow: Access auditing skips allowed decisions unless `success_audit` is enabled, then logs operation, hook, enforcing state, pid, command, path/dev/ino, and matched rule/default. Policy load/activation logs names, versions, SHA-256 digest of PKCS#7 data, session/audit uid, result, and errno. Enforcement changes log old/new mode through audit.

State and persistence: Reads global `success_audit` and `enforce`; no local persistent state. Audit records persist externally in audit logs.

Dependencies and integration: Uses audit subsystem, current task identity, IPE policy/eval structures, digest formatting helpers, and SHA-256 library.

Risks and test signals: Risks include NULL file/path handling, digesting NULL `pkcs7` for unsigned policies, audit format drift, and calling `audit_log_start()` with atomic allocation in hook paths. Tests should inspect records for rule/table/global matches, deny/allow with success audit, policy load failure, activation from no boot policy, and enforce toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/audit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/audit.h -->
# sources/distributed-fs/ceph-client/security/ipe/audit.h

Purpose: Declares the IPE audit interface used by evaluation, policy, and securityfs code.

Important APIs/types/functions: Prototypes `ipe_audit_match()`, `ipe_audit_policy_load()`, `ipe_audit_policy_activation()`, and `ipe_audit_enforce()`.

Control flow: No runtime logic. The declarations encode where audit side effects occur around policy evaluation and configuration changes.

State and persistence: No state.

Dependencies and integration: Includes `policy.h` for policy/evaluation types; referenced by `eval.c`, `fs.c`, `policy.c`, and `policy_fs.c`.

Risks and test signals: Interface risks are type drift and audit calls being skipped by future code paths. Build coverage and audit-event tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/digest.c -->
# sources/distributed-fs/ceph-client/security/ipe/digest.c

Purpose: Parses, compares, frees, and audits digest values used in IPE policy properties.

Important APIs/types/functions: Implements `ipe_digest_parse()`, `ipe_digest_eval()`, `ipe_digest_free()`, and `ipe_digest_audit()`. Data shape is `struct digest_info` from `digest.h`.

Control flow: Parser expects `<alg_name>:<hex>`, duplicates the algorithm string, allocates digest bytes sized from hex length, decodes with `hex2bin()`, and returns ERR_PTR on parse or allocation failure. Evaluation requires equal digest length, identical algorithm string, and byte-for-byte digest equality. Audit emits algorithm as untrusted string plus hex digest.

State and persistence: Digest objects are heap allocations owned by parsed policies or LSM blobs. No global state.

Dependencies and integration: Used by IPE parser, dm-verity/fs-verity evaluators, audit formatting, and block-device integrity storage.

Risks and test signals: Odd hex lengths are rounded up before `hex2bin()`, so parser behavior should be validated carefully. Risks also include algorithm-string case sensitivity and no crypto algorithm availability check. Tests should cover missing colon, invalid hex, odd length, empty algorithm/digest, equal/different algorithms, and freeing ERR/NULL values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/digest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/digest.h -->
# sources/distributed-fs/ceph-client/security/ipe/digest.h

Purpose: Declares IPE digest representation and helper APIs.

Important APIs/types/functions: `struct digest_info` stores algorithm name, digest bytes, and length. Declares parser, free, audit, and equality helpers.

Control flow: Header-only interface; functions are implemented in `digest.c`.

State and persistence: Digest info instances are dynamically allocated by policy parsing or LSM blob update paths and must be freed with `ipe_digest_free()`.

Dependencies and integration: Includes audit and policy headers; consumed by IPE policy parser, evaluation, hooks, and audit.

Risks and test signals: Risks are const pointer ownership ambiguity and callers freeing non-owned digest values. Static analysis and KUnit parser tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/digest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/eval.c -->
# sources/distributed-fs/ceph-client/security/ipe/eval.c

Purpose: Maintains active IPE policy state, builds evaluation contexts, evaluates policy properties/rules/defaults, audits results, and enforces deny decisions.

Important APIs/types/functions: Exports `ipe_active_policy`, `success_audit`, `enforce`, `ipe_build_eval_ctx()`, and `ipe_evaluate_event()`. Property evaluators cover boot-verified, dm-verity root hash/signature, fs-verity digest, and fs-verity builtin signature depending on config.

Control flow: Hook code builds `struct ipe_eval_ctx` with file, op, hook, initramfs flag, optional block-device blob, inode, and inode blob. `ipe_evaluate_event()` RCU-loads the active policy, handles invalid ops through global default, scans rules for the operation in insertion order and requires all rule properties to match, then falls back to operation default or global default. It audits before leaving the RCU section, returns `-EACCES` for deny, and suppresses enforcement when `enforce` is false.

State and persistence: Active policy pointer is RCU-protected. `success_audit` and `enforce` are module parameters/securityfs-controlled booleans.

Dependencies and integration: Integrates with LSM blob accessors, fs-verity digest API, dm-verity integrity data stored by hooks, policy parser structures, and audit.

Risks and test signals: Risks include NULL active policy allowing all, missing global default causing warning/allow for invalid ops, RCU lifetime of policy/rule pointers during audit, and config-gated properties evaluating false. Tests should evaluate ordered rule matching, default precedence, permissive mode, no-policy mode, and each provider property.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/eval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/eval.h -->
# sources/distributed-fs/ceph-client/security/ipe/eval.h

Purpose: Declares IPE evaluation state, LSM blob data, match enums, and evaluation APIs.

Important APIs/types/functions: Defines `IPE_EVAL_CTX_INIT`, externs `ipe_active_policy`, `success_audit`, and `enforce`, and declares `struct ipe_superblock`, optional `struct ipe_bdev`, optional `struct ipe_inode`, `struct ipe_eval_ctx`, `enum ipe_match`, `ipe_build_eval_ctx()`, and `ipe_evaluate_event()`.

Control flow: No logic, but config guards mirror Kconfig provider selection and determine which context fields exist.

State and persistence: Structures model persistent LSM blob data: initramfs superblock flag, dm-verity root hash/signature state, and fs-verity signature state.

Dependencies and integration: Shared by LSM registration, hooks, policy, audit, and fs code.

Risks and test signals: Risk is config mismatch between blob sizing and context accessors. Build matrix and provider-specific evaluation tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/eval.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/fs.c -->
# sources/distributed-fs/ceph-client/security/ipe/fs.c

Purpose: Creates top-level IPE securityfs controls for success auditing, enforcement mode, policy directory, and new policy submission.

Important APIs/types/functions: Exports `policy_root` and `ipe_init_securityfs()`. File operations implement `setaudit/getaudit`, `setenforce/getenforce`, and `new_policy`.

Control flow: Writes require `CAP_MAC_ADMIN` in the initial user namespace. Audit/enforce writes parse booleans and update global variables, with enforce changes audited. `new_policy` copies user data, treats it as PKCS#7 policy data, creates a new policy via `ipe_new_policy(NULL, 0, copy, len)`, creates policyfs nodes, and audits load success/failure. Init creates `/sys/kernel/security/ipe`, `success_audit`, `enforce`, `policies`, existing active policy node if present, and `new_policy`.

State and persistence: Securityfs dentries are retained for the lifetime of IPE. Global booleans and policyfs directory state are exposed through files.

Dependencies and integration: Depends on securityfs, capability checks, policy parser/signature verifier, policyfs node creation, and audit.

Risks and test signals: Risks include partial securityfs creation cleanup, unsigned boot policy node creation, user-data length/memory handling, and CAP namespace policy. Tests should verify permissions, bool parsing, policy upload errors, existing active policy exposure, and cleanup on init failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/fs.h -->
# sources/distributed-fs/ceph-client/security/ipe/fs.h

Purpose: Declares IPE policy securityfs node helpers and shared policy root dentry.

Important APIs/types/functions: Externs `policy_root` and declares `ipe_new_policyfs_node()` and `ipe_del_policyfs_node()`.

Control flow: No logic; it exposes policyfs lifecycle functions to top-level fs and policy cleanup code.

State and persistence: `policy_root` points to the securityfs policies directory once initialized.

Dependencies and integration: Included by `fs.c`, `policy.c`, and `policy_fs.c`.

Risks and test signals: Build-time interface drift and NULL `policy_root` use before securityfs init are the main risks. Init-order tests cover this.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/hooks.c -->
# sources/distributed-fs/ceph-client/security/ipe/hooks.c

Purpose: Implements IPE LSM hook handlers and integrity blob update hooks that feed evaluation context state.

Important APIs/types/functions: Hook handlers include `ipe_bprm_check_security()`, `ipe_bprm_creds_for_exec()`, `ipe_mmap_file()`, `ipe_file_mprotect()`, `ipe_kernel_read_file()`, `ipe_kernel_load_data()`, `ipe_unpack_initramfs()`, optional `ipe_bdev_free_security()`, `ipe_bdev_setintegrity()`, and optional `ipe_inode_setintegrity()`.

Control flow: Exec hooks evaluate `IPE_OP_EXEC` for normal binary checks and AT_EXECVE_CHECK script checks. mmap/mprotect evaluate executable mappings only when gaining execute permission. Kernel read/load hooks map kernel ids to IPE operations for firmware, modules, kexec image/initramfs, policy, and X.509 certs, warning and using invalid op for unknown ids. Initramfs hook marks the root superblock. Integrity hooks store dm-verity root hashes/signature booleans on block-device blobs and fs-verity builtin signature booleans on inode blobs.

State and persistence: LSM blobs persist on superblocks, block devices, and inodes; block-device root hash allocations are freed by `ipe_bdev_free_security()`.

Dependencies and integration: Tied to LSM hook registration, kernel_read/load ids, dm-verity/fs-verity integrity events, digest helpers, and evaluation.

Risks and test signals: Risks include NULL file handling for mmap/mprotect, incorrect id-to-op mapping, stale root hash replacement, and provider config behavior. Tests should cover all hook mappings, permissive/enforce decisions, executable transition checks, and integrity blob lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/hooks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/hooks.h -->
# sources/distributed-fs/ceph-client/security/ipe/hooks.h

Purpose: Declares IPE LSM hook functions, hook enum identifiers, and optional integrity blob hook interfaces.

Important APIs/types/functions: Defines `enum ipe_hook_type` and `IPE_HOOK_INVALID`, then prototypes all hook handlers implemented in `hooks.c`.

Control flow: No runtime logic; enum values must stay aligned with audit hook name array in `audit.c`.

State and persistence: No state.

Dependencies and integration: Includes kernel file/binfmt/security/block/fsverity types and is used by `ipe.c`, `eval.c`, and `audit.c`.

Risks and test signals: Risks include enum/name mismatch and missing prototypes under config guards. Build and audit output tests cover this.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/ipe.c -->
# sources/distributed-fs/ceph-client/security/ipe/ipe.c

Purpose: Registers IPE as an LSM, reserves LSM blob sizes, exposes blob accessors, installs hooks, and loads the built-in boot policy.

Important APIs/types/functions: Defines `ipe_enabled`, `ipe_blobs`, `ipe_lsmid`, blob accessors `ipe_sb()`, optional `ipe_bdev()`, optional `ipe_inode()`, hook array `ipe_hooks`, and `ipe_init()` registered through `DEFINE_LSM(ipe)`.

Control flow: During LSM init, hooks are added, IPE is marked enabled, and if generated `ipe_boot_policy` is non-empty, it is parsed as plaintext and assigned to `ipe_active_policy`. Securityfs initialization is registered as `initcall_fs`.

State and persistence: LSM blob offsets/sizes persist after init. Active boot policy persists as the initial RCU policy until replaced.

Dependencies and integration: Depends on LSM framework, generated boot policy object, policy parser, evaluation globals, hooks, and securityfs init.

Risks and test signals: Risks include blob offset arithmetic, boot policy parse failure aborting init, and hook registration despite later policy failure. Tests should include boot with/without built-in policy and provider config blob sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/ipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/ipe.h -->
# sources/distributed-fs/ceph-client/security/ipe/ipe.h

Purpose: Shared IPE top-level declarations and logging prefix.

Important APIs/types/functions: Defines `pr_fmt`, declares `ipe_sb()`, `ipe_enabled`, optional `ipe_bdev()`/`ipe_inode()`, and `ipe_init_securityfs()`.

Control flow: Header-only interface.

State and persistence: Exposes global enablement and blob accessors for persistent LSM blob storage.

Dependencies and integration: Included across IPE source files and depends on LSM hook types.

Risks and test signals: Interface risks are config guard mismatch and accessor misuse before blob allocation. Build matrix validates most issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/ipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy.c -->
# sources/distributed-fs/ceph-client/security/ipe/policy.c

Purpose: Allocates, verifies, parses, updates, activates, and frees IPE policies.

Important APIs/types/functions: Provides global `ipe_policy_lock`, `ipe_free_policy()`, `ipe_update_policy()`, `ipe_new_policy()`, and `ipe_set_active_pol()`. Internal `ver_to_u64()` compares major/minor/revision, and `set_pkcs7_data()` extracts signed policy plaintext from PKCS#7 verification.

Control flow: `ipe_new_policy()` accepts either plaintext or PKCS#7 data. For signed data it copies the blob, verifies against secondary and optionally platform keyrings, captures plaintext via callback, and parses. Plaintext is duplicated directly. `ipe_update_policy()` requires inode lock, parses a new policy, enforces same name and strictly newer version, swaps policyfs ownership, updates active policy if replacing the active one under `ipe_policy_lock`, synchronizes RCU, and frees old policy. `ipe_set_active_pol()` forbids activating a policy older than the current active version.

State and persistence: Policies hold PKCS#7 blob, plaintext pointer/length, parsed policy, and securityfs dentry. Active policy is RCU-protected; writer serialization uses `ipe_policy_lock` plus policyfs inode locks.

Dependencies and integration: Integrates with system data verification, trusted keyrings, policy parser, policyfs nodes, audit, RCU, and securityfs.

Risks and test signals: Risks include unsigned/signed text ownership subtleties, version comparison rules, policyfs swap correctness, RCU lifetime, and keyring fallback semantics. Tests should cover signed verification failures, same-name enforcement, stale update rejection, active policy replacement, and freeing policies with/without PKCS#7.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy.h -->
# sources/distributed-fs/ceph-client/security/ipe/policy.h

Purpose: Defines IPE policy model types and policy lifecycle APIs.

Important APIs/types/functions: Enumerates operations (`EXEC`, firmware, module, kexec image/initramfs, policy, X.509), actions (`ALLOW`, `DENY`), and properties (boot verified, dm-verity root hash/signature, fs-verity digest/signature). Defines `struct ipe_prop`, `ipe_rule`, `ipe_op_table`, `ipe_parsed_policy`, and `ipe_policy`, plus lifecycle/update/activation prototypes and `ipe_policy_lock`.

Control flow: No logic, but the structure layout drives parser output, evaluator traversal, audit formatting, and securityfs reads.

State and persistence: `struct ipe_policy` is the persistent runtime policy object and contains both source text/blob and parsed decision tables.

Dependencies and integration: Shared by all IPE subsystems.

Risks and test signals: Risks include enum order coupling to parser/audit arrays and property config support. Compile-time and parser/evaluator tests should catch drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy_fs.c -->
# sources/distributed-fs/ceph-client/security/ipe/policy_fs.c

Purpose: Implements per-policy securityfs directories and files for reading policy metadata/content, activating, updating, and deleting deployed IPE policies.

Important APIs/types/functions: File handlers include `read_pkcs7()`, `read_policy()`, `read_name()`, `read_version()`, `setactive()`, `getactive()`, `update_policy()`, and `delete_policy()`. Exports `ipe_new_policyfs_node()` and `ipe_del_policyfs_node()`.

Control flow: Each policy directory contains `pkcs7`, `policy`, `name`, `version`, `active`, `update`, and `delete`. Reads take the parent inode shared lock and return `-ENOENT` when deleted/initializing; `pkcs7` also returns `-ENOENT` for unsigned policies. Writes require `CAP_MAC_ADMIN`. Activation only accepts true, locks the parent inode, and calls `ipe_set_active_pol()`. Update copies signed policy data and delegates to `ipe_update_policy()`. Delete refuses active policies under `ipe_policy_lock`, clears `i_private`, synchronizes RCU, and frees the policy.

State and persistence: Policy directories keep `root->i_private` as the owning policy pointer and `p->policyfs` as the dentry. Active state is derived from `ipe_active_policy`.

Dependencies and integration: Uses securityfs, inode locking, RCU, policy lifecycle functions, capability checks, and audit on update failures.

Risks and test signals: Risks include active pointer comparison outside locks in `getactive()`, policy deletion races, partial directory creation cleanup, update ownership swap, and refusing deletion of active policies. Tests should cover read-after-delete, update version/name errors, activation of older policies, duplicate names, and cleanup on file creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy_fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy_parser.c -->
# sources/distributed-fs/ceph-client/security/ipe/policy_parser.c

Purpose: Parses plaintext IPE policy text into validated `struct ipe_parsed_policy` decision tables.

Important APIs/types/functions: Implements `ipe_parse_policy()` and `ipe_free_parsed_policy()`. Internals include `new_parsed_policy()`, line preprocessing, `parse_version()`, `parse_header()`, `parse_operation()`, `parse_action()`, `parse_property()`, `parse_rule()`, `free_rule()`, and `validate_policy()`.

Control flow: The parser duplicates NUL-terminated policy text, splits on newline/CR, strips comments and trailing spaces, parses the first non-empty line as ordered `policy_name=` then `policy_version=`, then parses rules. Rule syntax requires optional leading `DEFAULT`, operation before properties, and action as the final token. Default rules cannot have properties. Non-default rules are appended to operation tables. Validation requires either a global default action or per-operation defaults for every operation.

State and persistence: Allocates parsed policy, name string, rules, properties, and digest values. Freeing walks all operation rule lists and frees digest-backed properties.

Dependencies and integration: Uses kernel match token parser, digest parser, policy type definitions, and IPE lifecycle code.

Risks and test signals: Risks include strict token ordering surprises, `while (t = strsep(...), line)` relying on final token handling, embedded NUL truncation, duplicate defaults, and digest property parse behavior. `policy_tests.c` covers many syntax failures; additional evaluator tests should verify semantic ordering and provider-disabled properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy_parser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy_parser.h -->
# sources/distributed-fs/ceph-client/security/ipe/policy_parser.h

Purpose: Declares IPE plaintext policy parser and parsed-policy cleanup APIs.

Important APIs/types/functions: Prototypes `ipe_parse_policy()` and `ipe_free_parsed_policy()`.

Control flow: No runtime logic.

State and persistence: Parsed policy ownership is transferred into `struct ipe_policy` on success and freed through the declared cleanup function.

Dependencies and integration: Used by `policy.c` and parser tests.

Risks and test signals: Build drift and missing cleanup on parser failure are primary risks. KUnit parser tests cover most interface use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy_tests.c -->
# sources/distributed-fs/ceph-client/security/ipe/policy_tests.c

Purpose: Provides KUnit tests for unsigned IPE policy parser behavior.

Important APIs/types/functions: Defines `struct policy_case`, `policy_cases[]`, KUnit parameter generator `KUNIT_ARRAY_PARAM(ipe_policies, ...)`, tests `ipe_parser_unsigned_test()` and `ipe_parser_widestring_test()`, and suite `ipe-parser`.

Control flow: Parameterized tests call `ipe_new_policy(policy, strlen(policy), NULL, 0)` and compare expected errno or validate parsed/text/pkcs7 fields for success. The wide-string test passes UTF-16-like data and expects parser failure.

State and persistence: Allocates temporary policies through production policy creation and frees successful policies.

Dependencies and integration: Exercises parser, digest parsing, policy allocation/freeing, and KUnit. It does not require signed policy verification.

Risks and test signals: Strong coverage exists for comments, whitespace, CRLF, versions, malformed headers, duplicate defaults, invalid operations/actions, old-style digests, embedded NUL behavior, and wide strings. Gaps include signed PKCS#7 policy load, active policy update semantics, evaluator outcomes, and config-gated provider evaluation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/ipe/policy_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/Kconfig -->
# sources/distributed-fs/ceph-client/security/keys/Kconfig

Purpose: Configures Linux key retention support and optional key types/features used by filesystems, crypto, and integrity subsystems.

Important APIs/types/functions: `KEYS` enables core keyrings. Options include request-key caching, persistent per-UID keyrings, `BIG_KEYS`, trusted keys, encrypted keys, user-decrypted encrypted-key data, Diffie-Hellman key operations, and key notifications.

Control flow: Kconfig symbols select required crypto and subsystem dependencies, such as associative arrays, tmpfs for big keys, ChaCha20-Poly1305, AES/CBC/SHA256/RNG for encrypted keys, crypto DH/KDF for DH operations, and watch queues for notifications.

State and persistence: No runtime state. Options determine which kernel key types and syscalls are built.

Dependencies and integration: Network filesystems, eCryptfs/encrypted keys, IMA/EVM, request_key(), and userspace keyctl depend on these capabilities.

Risks and test signals: Build-matrix risk is high because many files are config-gated. Test with minimal KEYS off/on, BIG_KEYS, ENCRYPTED_KEYS, TRUSTED_KEYS, DH operations, and notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/Makefile -->
# sources/distributed-fs/ceph-client/security/keys/Makefile

Purpose: Kbuild object list for core key management and optional key features.

Important APIs/types/functions: Always builds core key management objects (`gc.o`, `key.o`, `keyring.o`, `keyctl.o`, `permission.o`, `process_keys.o`, `request_key.o`, `request_key_auth.o`, `user_defined.o`). Adds compat, proc, sysctl, persistent keyrings, DH, public-key ops, big key, trusted keys, and encrypted keys based on config.

Control flow: Config symbols choose object inclusion and compat DH support.

State and persistence: No runtime state.

Dependencies and integration: Coordinates subdirectories `trusted-keys/` and `encrypted-keys/` plus syscall compatibility code.

Risks and test signals: Risks include missing objects under unusual config combinations, especially compat DH. Build matrix is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/big_key.c -->
# sources/distributed-fs/ceph-client/security/keys/big_key.c

Purpose: Implements the `big_key` key type for payloads up to 1 MiB, storing small payloads in memory and large payloads encrypted in shmem so they can be swapped.

Important APIs/types/functions: Defines `struct big_key_payload`, `key_type_big_key`, and operations `big_key_preparse()`, `big_key_free_preparse()`, `big_key_revoke()`, `big_key_destroy()`, `big_key_update()`, `big_key_describe()`, `big_key_read()`, and `big_key_init()`.

Control flow: Preparse rejects empty, oversized, or missing data and charges a small quota. Payloads larger than `BIG_KEY_FILE_THRESHOLD` are encrypted with a per-key random ChaCha20-Poly1305 key, stored in an anonymous shmem file, and pinned by path; smaller payloads are copied into kmalloc memory. Read returns required length when no/too-small buffer is supplied, otherwise decrypts from shmem or copies memory payload. Revoke truncates shmem and clears quota; destroy drops path references and wipes key material; update destroys old positive payload after reserving quota.

State and persistence: Key payload stores data pointer or encryption key, shmem path, and plaintext length. Large ciphertext persists in tmpfs while the key lives.

Dependencies and integration: Uses key type framework, shmem, kernel read/write, random bytes, and ChaCha20-Poly1305.

Risks and test signals: Risks include nonce reuse if update semantics changed, encrypted file read/write size mismatches, sensitive buffer wiping, path reference leaks, and quota mismatch. Tests should cover threshold boundary, read length query, update/revoke/destroy, bad authentication tag, OOM/error cleanup, and swap-backed storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/big_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/compat.c -->
# sources/distributed-fs/ceph-client/security/keys/compat.c

Purpose: Implements 32-bit compatibility dispatch for the `keyctl` syscall on 64-bit kernels.

Important APIs/types/functions: `COMPAT_SYSCALL_DEFINE5(keyctl, ...)` switches over `KEYCTL_*` operation codes and forwards to native helpers, converting 32-bit user pointers with `compat_ptr()` where needed.

Control flow: Each case calls the corresponding keyctl helper for keyring ids, joining, update, revoke, describe, clear/link/unlink/search/read, ownership/permission, instantiate/reject/invalidate, persistent keyrings, DH compute, keyring restriction, public-key operations, move, capabilities, and watch keys. Unknown operations return `-EOPNOTSUPP`.

State and persistence: No local state; all state changes occur in core key/keyring code.

Dependencies and integration: Depends on compat syscall layer, keyctl helper APIs, optional compat DH helper, public-key helpers, and watch queue support.

Risks and test signals: Risks are pointer conversion mistakes, argument width truncation, missing new KEYCTL operations in compat dispatch, and invalid reserved-argument handling for public-key query. Compat syscall tests should compare 32-bit userspace behavior to native keyctl for all supported options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/compat_dh.c -->
# sources/distributed-fs/ceph-client/security/keys/compat_dh.c

Purpose: Converts 32-bit compatibility KDF parameters for `KEYCTL_DH_COMPUTE` before invoking the native DH implementation.

Important APIs/types/functions: Implements `compat_keyctl_dh_compute()` and maps `struct compat_keyctl_kdf_params` to `struct keyctl_kdf_params`.

Control flow: If no KDF pointer is supplied, it forwards directly with NULL. Otherwise it copies the compat struct from userspace, converts `hashname` and `otherinfo` pointers via `compat_ptr()`, copies length and spare fields, and calls `__keyctl_dh_compute()`.

State and persistence: No local state.

Dependencies and integration: Used by `compat.c` for DH operations and depends on native `dh.c` implementation.

Risks and test signals: Risks include bad pointer conversion and spare field mismatch. Compat DH tests should cover no-KDF, KDF, bad userspace pointer, and reserved-field validation in the native path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/compat_dh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/dh.c -->
# sources/distributed-fs/ceph-client/security/keys/dh.c

Purpose: Implements Diffie-Hellman public/shared secret computation and optional SP800-108 counter-mode KDF using values stored in kernel user keys.

Important APIs/types/functions: Key helpers `dh_data_from_key()` and `dh_free_data()`, KDF helpers `kdf_alloc()`, `kdf_dealloc()`, `keyctl_dh_compute_kdf()`, core `__keyctl_dh_compute()`, and syscall-facing `keyctl_dh_compute()`.

Control flow: The main function validates user pointers, copies DH params, optionally validates KDF spare fields and output/otherinfo length limits, loads the requested hash transform, reads prime/base/private key payloads with `KEY_NEED_READ`, encodes DH inputs, allocates crypto KPP `dh`, sets the secret, determines output length, and either reports required length, rejects too-small buffers, performs DH calculation, optionally appends KDF otherinfo and derives requested bytes, or copies raw DH output to userspace. Cleanup wipes sensitive buffers.

State and persistence: No persistent local state. It copies key payloads into temporary sensitive buffers and frees them before returning.

Dependencies and integration: Depends on key permission/validation, user key type payloads, crypto KPP DH, scatterlists, async crypto wait helpers, shash, and SP800-108 KDF.

Risks and test signals: Risks include side-channel-sensitive buffer handling, user copy failures, key type restrictions, raw output length probing, KDF length limits, and crypto backend errors. Tests should cover permission denial, non-user keys, buffer query/overflow, KDF reserved fields, bad hash names, otherinfo copying, and known DH vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/dh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/Makefile -->
# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/Makefile

Purpose: Builds the encrypted key type and optional trusted master key support.

Important APIs/types/functions: Builds `encrypted-keys.o` from `encrypted.o` and `ecryptfs_format.o`, and conditionally adds `masterkey_trusted.o` based on `CONFIG_TRUSTED_KEYS` and `CONFIG_ENCRYPTED_KEYS`.

Control flow: Kbuild combines objects into the encrypted-keys composite object when `CONFIG_ENCRYPTED_KEYS` is enabled.

State and persistence: No runtime state.

Dependencies and integration: Connects encrypted key type with eCryptfs payload formatting and trusted-key master support.

Risks and test signals: Risks are conditional object expression mistakes for built-in/module combinations. Build tests should cover encrypted keys with trusted keys disabled, built-in, and modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/ecryptfs_format.c -->
# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/ecryptfs_format.c

Purpose: Provides helper functions that format encrypted-key payloads as eCryptfs authentication tokens.

Important APIs/types/functions: Exports `ecryptfs_get_auth_tok_key()`, `ecryptfs_get_versions()`, and `ecryptfs_fill_auth_tok()`.

Control flow: `ecryptfs_get_auth_tok_key()` returns the session key encryption key location inside an auth token. `ecryptfs_get_versions()` reports kernel-supported eCryptfs version constants. `ecryptfs_fill_auth_tok()` initializes token version, password token type, signature from key description, max key bytes, session-key-encryption flag, empty encrypted session key, default SHA-512 hash algorithm, and clears persistent-password flag. It intentionally leaves salt and session key material initialization to other code.

State and persistence: No local state. It mutates caller-provided `struct ecryptfs_auth_tok` that is later stored or used by encrypted/eCryptfs key code.

Dependencies and integration: Depends on Linux eCryptfs structures and is linked into encrypted keys. Exports symbols for users elsewhere in the kernel.

Risks and test signals: Risks include structure layout/version drift, signature truncation/padding behavior, fixed SHA-512 hash policy, and assumptions about external key material initialization. Tests should validate generated token fields and compatibility with eCryptfs consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/ecryptfs_format.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/ecryptfs_format.h -->
# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/ecryptfs_format.h

Purpose: Declares eCryptfs formatting helpers for encrypted keys.

Important APIs/types/functions: Defines `PGP_DIGEST_ALGO_SHA512` and prototypes `ecryptfs_get_auth_tok_key()`, `ecryptfs_get_versions()`, and `ecryptfs_fill_auth_tok()`.

Control flow: Header-only interface.

State and persistence: No state; callers pass auth-token storage.

Dependencies and integration: Includes `linux/ecryptfs.h` and is consumed by encrypted key implementation.

Risks and test signals: Risks are constant mismatch with eCryptfs expectations and prototype drift. Build and token compatibility tests provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/ecryptfs_format.h -->
