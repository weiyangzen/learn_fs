# Research Group subset-b-009817

This grouped report covers Samba source3 Group Policy extension modules and libnet domain-join/DSSync support. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libgpo/gpext/registry.c -->
# sources/user-network-fs/samba/source3/libgpo/gpext/registry.c

## Purpose

`registry.c` implements the Samba source3 Group Policy registry client-side extension. It locates each changed GPO's cached `Registry.pol`, parses the Windows `PReg` policy format, converts policy entries into Samba `gp_registry_entry` records, and applies them to the supplied registry root.

## Important APIs, Types, and Functions

The exported initializer is `gpext_registry_init`, which registers `registry_methods` under `GP_EXT_GUID_REGISTRY`. `reg_parse_value` maps special policy value names such as `**DelVals.`, `**Del.`, and `**SecureKey=1` to `enum gp_reg_action`. `gp_reg_entry_from_file_entry` converts an NDR `preg_entry` into a `gp_registry_entry` and serializes its typed `winreg_Data` into a `registry_value`. `reg_parse_registry` loads and validates `Registry.pol`. `reg_apply_registry` loops over parsed entries and calls `reg_apply_registry_entry`. `registry_process_group_policy` is the extension callback.

## Control Flow

`gpext_registry_init` creates a module talloc context and registers callbacks. During GPO processing, `registry_process_group_policy` ignores deleted GPOs, iterates `changed_gpo_list`, resolves each GPO cache path with `gpo_get_unix_path`, calls `reg_parse_registry`, optionally dumps entries, and applies them. Parsing uses `gp_find_file`, `file_load`, `ndr_pull_preg_file`, signature/version validation, entry conversion, and `add_gp_registry_entry_to_array`. Applying is sequential; the first failed registry write aborts the current pass.

## State and Persistence Behavior

The module owns only a static registration context `ctx`. Runtime state is talloc-scoped arrays and blobs. Persistent effects are registry mutations performed through `reg_apply_registry_entry`; the file also reads cached GPO files from `GPO_CACHE_DIR`. Unsupported policy directives intentionally panic rather than persist a partial interpretation.

## Dependencies and Integration Points

It depends on libgpo file discovery, generated NDR `preg` parsers, `registry.h` helpers, registry apply logic, and the `gpext` module registration ABI. Build integration is through `gpext_registry` in `wscript_build`, with `NDR_PREG` as an explicit dependency.

## Risks and Test Signals

Risks include unsupported special value names (`**DeleteValues`, `**DeleteKeys`, `**SecureKey=0`) causing `smb_panic`, treating some conversion failures as `NT_STATUS_NO_MEMORY`, and deleted-GPO processing being unimplemented. Good tests cover malformed `Registry.pol`, wrong signature/version, add/delete value actions, secure-key policy, verbose NDR printing, and registry write failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libgpo/gpext/registry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libgpo/gpext/scripts.c -->
# sources/user-network-fs/samba/source3/libgpo/gpext/scripts.c

## Purpose

`scripts.c` implements the Group Policy Scripts extension. It reads `Scripts/scripts.ini` from changed GPOs, transforms Startup, Shutdown, Logon, and Logoff script entries into registry policy values under `Software\Policies\Microsoft\Windows\System\Scripts`, and stores GPO metadata next to those values.

## Important APIs, Types, and Functions

`gpext_scripts_init` registers the extension. `scripts_get_reg_config` advertises `ProcessGroupPolicy`, `NoGPOListChanges`, `NoSlowLink`, and `NotifyLinkTransition` registry metadata. `scripts_parse_ini_section` scans numbered script entries and produces three registry values for each script: `Script`, `Parameters`, and zeroed `ExecTime`. `generate_gp_registry_entry` constructs `gp_registry_entry` objects. `scripts_apply` deletes/recreates a section-specific policy registry key and applies generated entries. `scripts_process_group_policy` drives all sections for each changed GPO.

## Control Flow

Processing starts at `scripts_process_group_policy`, which resolves each changed GPO cache path and initializes a `gp_inifile_context` for `Scripts/scripts.ini`. It loops over the four known sections. For each section, `scripts_parse_ini_section` increments indexes from `0` until a `cmdline` or `parameters` key is missing, using `push_reg_sz` for strings and an eight-byte zero blob for `REG_QWORD` execution time. `scripts_apply` removes the previous section key, creates a new subkey, stores GPO identity values, then applies each registry entry.

## State and Persistence Behavior

The only module-level state is static `ctx`. Persistent side effects are registry writes and recursive deletion of the section key for each processed GPO/section. Deleted GPO lists are ignored. A FIXME notes failures for empty strings and `REG_QWORD`; `scripts_process_group_policy` currently continues on `scripts_apply` errors.

## Dependencies and Integration Points

The file integrates libgpo INI parsing, registry helpers from `registry.h`, `reg_apply_registry_entry`, and the `gpext` extension ABI. `wscript_build` packages it as `gpext_scripts`.

## Risks and Test Signals

Risks include partially applied script sections because apply errors are skipped, no deleted-GPO cleanup, fixed section ordering, possible key overwrite from always using group index `0` in `scripts_apply`, and memory ownership quirks in generated entries. Tests should cover missing script sections, sparse numbering, empty parameters, multiple GPOs, registry key replacement, and advertised extension configuration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libgpo/gpext/scripts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libgpo/gpext/security.c -->
# sources/user-network-fs/samba/source3/libgpo/gpext/security.c

## Purpose

`security.c` registers a skeletal Group Policy Security extension. It locates each changed GPO's `Microsoft/Windows NT/SecEdit/GptTmpl.inf`, validates the security template header, and reserves a processing hook for mapping template sections to registry or security settings.

## Important APIs, Types, and Functions

`gpext_security_init` registers `security_methods` under `GP_EXT_GUID_SECURITY`. `gpttmpl_parse_header` validates `[Version] signature="$CHICAGO$"`, `Revision`, and `[Unicode] Unicode=true`. `gpttmpl_init_context` opens the template with `gp_inifile_init_context` and calls the header parser. `gpttmpl_process` is currently a no-op. `security_process_group_policy` drives changed GPO handling. `security_get_reg_config` advertises `ProcessGroupPolicy`, `NoUserPolicy`, and `ExtensionDebugLevel`.

## Control Flow

When invoked, `security_process_group_policy` obtains the GPO cache root, ignores deleted GPOs, loops over `changed_gpo_list`, resolves each GPO path, opens `GptTmpl.inf`, validates the header, calls `gpttmpl_process`, and frees the INI context. Any path, parse, or process failure aborts the loop and logs the NTSTATUS.

## State and Persistence Behavior

The module uses only static registration context `ctx`. The current processing path reads cached template files and validates them but does not persist settings because `gpttmpl_process` returns `NT_STATUS_OK` without applying the declared security sections.

## Dependencies and Integration Points

It depends on libgpo INI parsing and the `gpext` ABI. Constants enumerate expected security-template sections such as Registry Values, System Access, Kerberos Policy, Event Audit, Privilege Rights, group membership, file security, and services. `wscript_build` builds it as `gpext_security`.

## Risks and Test Signals

The main functional risk is incompleteness: valid templates are accepted but their contents are not applied. Deleted-GPO cleanup is also absent. Header parsing is strict and may reject templates with missing Unicode markers or unexpected signature spelling. Tests should validate registration metadata, header success/failure cases, cache path resolution, and the no-op behavior until real section processing is implemented.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libgpo/gpext/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libgpo/gpext/wscript_build -->
# sources/user-network-fs/samba/source3/libgpo/gpext/wscript_build

## Purpose

`wscript_build` declares the Samba3 build targets for the Group Policy extension modules in this directory: registry, scripts, and security.

## Important APIs, Types, and Functions

The file uses Waf's `bld.SAMBA3_MODULE` helper three times. It defines `gpext_registry` from `registry.c` with dependency `NDR_PREG`, `gpext_scripts` from `scripts.c`, and `gpext_security` from `security.c`. Each target uses subsystem `gpext`, leaves `init_function` empty, and derives `internal_module` and `enabled` from `SAMBA3_IS_STATIC_MODULE` and `SAMBA3_IS_ENABLED_MODULE`.

## Control Flow

At configure/build time Waf evaluates the module declarations. Whether a module is built statically, dynamically, or disabled is controlled by Samba module configuration. There is no runtime code in this file.

## State and Persistence Behavior

No runtime state exists. Persistent build effects are generated objects/modules under the build tree. The declarations also encode the only explicit dependency in this directory: `registry.c` needs generated `NDR_PREG` support.

## Dependencies and Integration Points

The targets integrate the C extension files with Samba's source3 module subsystem. The empty `init_function` means module discovery/initialization follows the surrounding Samba module conventions rather than a named Waf-provided initializer entry.

## Risks and Test Signals

Risks are build-configuration related: missing `NDR_PREG` breaks registry policy parsing, and disabled module flags silently omit extension functionality. Test signals are successful Waf configuration, expected module enablement in build summaries, and link/load tests for all three `gpext` modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libgpo/gpext/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_dssync.c -->
# sources/user-network-fs/samba/source3/libnet/libnet_dssync.c

## Purpose

`libnet_dssync.c` is the common DRSUAPI replication driver used by Samba `libnet` DSSync backends. It binds to a domain controller, resolves the naming context, constructs `DsGetNCChanges` requests, decrypts replicated secret attributes, and dispatches objects and linked attributes to backend callbacks.

## Important APIs, Types, and Functions

Public APIs are `libnet_dssync_init_context` and `libnet_dssync`. The callback contract is defined in `struct dssync_ops` from `libnet_dssync.h`. Key internal functions are `libnet_dssync_bind`, `libnet_dssync_lookup_nc`, `libnet_dssync_build_request`, `libnet_dssync_getncchanges`, and `libnet_dssync_process`. `libnet_dssync_free_context` unbinds DRSUAPI handles from the talloc destructor.

## Control Flow

`libnet_dssync` allocates a temporary context, binds using `DsBind`, looks up `nc_dn` with `DsCrackNames` if needed, calls backend `startup`, then replicates either the whole naming context or requested object DNs. The request level is 8 when the remote advertises `GETCHGREQ_V8`, otherwise 5. `libnet_dssync_getncchanges` loops until `more_data` clears, handles uncompressed and compressed reply levels 1, 2, 6, and 7, updates high-watermarks, decrypts attributes with the RPC auth session key and object RID, then calls `process_objects` and `process_links`. Finally, backend `finish` receives the new up-to-dateness vector.

## State and Persistence Behavior

The common layer stores connection handles, bind metadata, session key, replication flags, requested objects, result/error messages, and backend private data in `dssync_context`. It persists nothing directly; persistence is delegated to backends through callback outputs. Incremental replication state is represented as `replUpToDateVectorBlob` passed between `startup`, request building, and `finish`.

## Dependencies and Integration Points

It integrates with RPC pipe clients, generated DRSUAPI client stubs, Samba DRS helpers, and backends `libnet_dssync_keytab_ops` and `libnet_dssync_passdb_ops`. Callers must provide an authenticated `rpc_pipe_client`, domain names, and an ops table.

## Risks and Test Signals

Risks include handling only known reply compression shapes, decrypted secret exposure in memory, partial replication if backend callbacks fail mid-loop, and correct UTDV handling across full, forced, and single-object modes. Tests should exercise bind negotiation lengths 24/28/32/48/52, incremental vectors v1/v2, compressed replies, linked attributes, single-object replication, and backend error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_dssync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_dssync.h -->
# sources/user-network-fs/samba/source3/libnet/libnet_dssync.h

## Purpose

`libnet_dssync.h` declares the shared context and callback interface for source3 DSSync replication consumers.

## Important APIs, Types, and Functions

`struct dssync_ops` defines four optional backend hooks: `startup`, `process_objects`, `process_links`, and `finish`. `struct dssync_context` carries domain names, RPC client, naming context DN, replication mode flags, object filters, DRS bind/session data, output filename, remote bind capabilities, private backend data, callback table, and result/error strings. The header declares `libnet_dssync_init_context`, `libnet_dssync`, and external ops tables for keytab and passdb backends.

## Control Flow

The header encodes the control-flow contract implemented by `libnet_dssync.c`: initialize context, fill connection/options, set `ops`, call `libnet_dssync`, let the common driver invoke startup, object/link processing, and finish.

## State and Persistence Behavior

The context is mutable and talloc-owned. Backend persistence is indirect through `private_data`, `output_filename`, and callback implementations. The shared context also owns DRS bind handle and session key material that must be treated as sensitive.

## Dependencies and Integration Points

It includes generated DRSUAPI and DRS blob types, forward-declares `rpc_pipe_client`, and is included by the common driver plus keytab/passdb backends. Its ABI couples backends to DRS replicated object and linked-attribute structures.

## Risks and Test Signals

Risks include callers omitting required fields such as `cli`, `domain_name`, or `ops`, and backends assuming `private_data` type without runtime checks beyond talloc. Tests should verify context defaults, destructor unbind behavior through the implementation, null optional callbacks, and both declared backend ops tables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_dssync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_dssync_keytab.c -->
# sources/user-network-fs/samba/source3/libnet/libnet_dssync_keytab.c

## Purpose

`libnet_dssync_keytab.c` is a DSSync backend that converts replicated account and trust secrets into keytab entries. It also stores the replication up-to-dateness vector and selected object attributes as synthetic keytab entries so later runs can resume or complete sparse object data.

## Important APIs, Types, and Functions

The exported `libnet_dssync_keytab_ops` supplies `keytab_startup`, `keytab_process_objects`, and `keytab_finish`. Important parsers include `parse_supplemental_credentials`, `parse_user`, `parse_tdo`, `parse_trustAuthInOutBlob`, and `parse_AuthenticationInformation`. `store_or_fetch_attribute` persists or recovers missing metadata in keytab entries. `dn_is_in_object_list` implements a positive write filter when not using single-object replication.

## Control Flow

Startup opens the target keytab, attaches the keytab context to `ctx->private_data`, and searches for a `UTDV/<nc_dn>@<realm>` entry to load the old vector. Object processing ignores deleted/recycled objects, then routes user password attributes to `parse_user` and trust auth attributes to `parse_tdo`. User parsing collects SPNs, UPN, account name, kvno from `unicodePwd` metadata, NT hash, password history, and Kerberos supplemental keys; it emits RC4/AES entries for current and historical kvnos. Trust parsing derives incoming/outgoing krbtgt salt principals and emits keys from current and previous trust auth arrays. Finish serializes the new UTDV back into a keytab entry and calls `libnet_keytab_add`.

## State and Persistence Behavior

Persistent state is the keytab itself. It stores real service principals, trust principals, UTDV blobs, and metadata entries such as `sAMAccountName/<dn>@<realm>` and `REMOTETRUSTNAME/<dn>@<realm>`. With `clean_old_entries`, final keytab writing removes old matching entries. When `HAVE_ADS` is absent, all callbacks return `NT_STATUS_NOT_SUPPORTED`.

## Dependencies and Integration Points

The backend depends on Kerberos support, `libnet_keytab` helpers, generated `drsblobs` NDR parsers, MD4 for NT hashes from clear trust passwords, and DRS decrypted attributes supplied by the common driver.

## Risks and Test Signals

Risks include storing sensitive replicated secrets in keytabs, kvno underflow around old/older keys, partial metadata recovery from stale synthetic entries, and continuing after some trust parse errors. Tests should cover UTDV round-trip, Primary:Kerberos v3/v4 parsing, password history kvnos, trust incoming/outgoing clear and NT4OWF auth info, object filtering, deleted objects, and non-ADS builds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_dssync_keytab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_dssync_passdb.c -->
# sources/user-network-fs/samba/source3/libnet/libnet_dssync_passdb.c

## Purpose

`libnet_dssync_passdb.c` is a DSSync backend that imports replicated domain users and groups into Samba's local passdb, group mapping database, and Unix account/group membership environment.

## Important APIs, Types, and Functions

The exported `libnet_dssync_passdb_ops` supplies startup, object/link processing, and finish callbacks. Internal state is `struct dssync_passdb`, `dssync_passdb_obj`, and `dssync_passdb_mem`. Object handlers are `handle_account_object`, `handle_alias_object`, `handle_group_object`, and a not-implemented trust handler. Attribute helpers `find_drsuapi_attr_*` and `GET_*` macros decode replicated attributes. `sam_account_from_object` maps DRS attributes to `struct samu`.

## Control Flow

Startup selects a passdb backend from `ctx->output_filename` or `lp_passdb_backend()` and creates in-memory RBT indexes for all objects, aliases, and groups. `passdb_process_objects` parses each replicated object, checks `sAMAccountType`, stores it by GUID, and dispatches to the relevant handler. Account handling ensures a Unix account exists via add-user/machine scripts, then adds or updates the Samba account with names, SID/rids, profile fields, logon times, logon hours, counters, password hashes, and account flags. Group and alias handlers create Unix groups and passdb group mappings, then stage member links. Linked attributes create active/inactive membership records. Finish traverses staged aliases and groups to add/delete alias members and Unix group members.

## State and Persistence Behavior

The backend uses in-memory dbwrap RBT databases to relate GUIDs and membership links during a run. Persistent effects include passdb account writes, group mapping updates, Unix user/group creation scripts, primary group changes, alias membership changes, Unix group membership edits, and removal of local secrets only through other join code. UTDV is not persisted by this backend.

## Dependencies and Integration Points

It integrates DRSUAPI replicated attributes with passdb APIs, dbwrap, local NSS lookups, Samba add-user/add-machine scripts, group mapping helpers, SID utilities, base64 userParameters storage, and Unix group modification helpers.

## Risks and Test Signals

Risks are high because replication input can create local users/groups and alter memberships. Pointer values are stored inside in-memory TDB records, so the RBT databases must remain process-local. Duplicate inserts abort, trust objects are not implemented, some group-member paths return `-1` for benign primary-member cases, and password history/account expiry TODOs remain. Tests should use isolated passdb/NSS backends to cover user add/update, group/alias creation, linked add/delete, missing members, distribution-group filtering, hash import, and script failure handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_dssync_passdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_join.c -->
# sources/user-network-fs/samba/source3/libnet/libnet_join.c

## Purpose

`libnet_join.c` implements Samba source3 domain join, offline join, join verification, unjoin, local secret storage, and optional registry-backed configuration updates.

## Important APIs, Types, and Functions

Public APIs are `libnet_init_JoinCtx`, `libnet_init_UnjoinCtx`, `libnet_Join`, `libnet_Unjoin`, and `libnet_join_ok`. Major internal paths are `libnet_DomainJoin`, `libnet_DomainOfflineJoin`, `libnet_DomainUnjoin`, `libnet_join_joindomain_rpc`, `libnet_join_joindomain_rpc_unsecure`, ADS helpers for LDAP account/SPN/UPN/encryption-type updates, and config helpers `do_JoinConfig`/`libnet_unjoin_config`.

## Control Flow

Join pre-processing validates domain and machine names, parses `DOMAIN\DC`, initializes secrets unless provisioning/offline mode skips it, then either performs an online or offline domain join. Online join discovers a writable DC, creates local krb5 config, queries LSA domain info, checks local config, optionally precreates the machine account over LDAP, then joins over SAMR or unsecure Netlogon password set. Post-processing updates AD attributes, stores SAF DC hints, stores secrets, updates smb.conf registry backend if requested, creates a keytab, adds domain RIDs to builtins, and verifies the Netlogon secure channel. Offline join reads ODJ provision blobs and populates output state without network operations. Unjoin can delete via ADS, disable over SAMR, remove local secrets, delete SAF hints, and reset config.

## State and Persistence Behavior

Persistent effects include AD machine account creation/modification/deletion or disablement, machine trust secrets in `secrets.tdb`, SAF join cache entries, generated private krb5 config, keytab synchronization, local smb.conf registry parameters, and builtin group membership setup. Rollback invokes unjoin if post-join verification fails.

## Dependencies and Integration Points

The file integrates ADS LDAP, SAMR/LSA/Netlogon RPC, dsgetdcname discovery, credentials/gensec, passdb secrets, smbconf registry backend, keytab sync, offline-join NDR helpers, and Samba loadparm configuration.

## Risks and Test Signals

Risks include many multi-step side effects with partial rollback, sensitive machine password handling, DC replication timing mitigated by temporary krb5 config, differences between ADS and RPC account creation, and config mutation only supporting registry backend. Tests should cover online AD join, NT-style domain join, unsecure join with passed password, provision-only mode, offline join, LDAP precreate fallback, post-verify rollback, unjoin delete/disable/no-delete modes, and config validation messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_join.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_join.h -->
# sources/user-network-fs/samba/source3/libnet/libnet_join.h

## Purpose

`libnet_join.h` declares the source3 libnet join/unjoin public interface.

## Important APIs, Types, and Functions

It forward-declares `struct messaging_context` and declares `libnet_join_ok`, `libnet_init_JoinCtx`, `libnet_init_UnjoinCtx`, `libnet_Join`, and `libnet_Unjoin`. The concrete `libnet_JoinCtx` and `libnet_UnjoinCtx` structures come from generated `ndr_libnet_join.h`, included by implementation users rather than this small header.

## Control Flow

Callers allocate and initialize a context, fill input fields and credentials, call `libnet_Join` or `libnet_Unjoin`, then inspect `out.result` and error strings. `libnet_join_ok` is a standalone secure-channel verification helper.

## State and Persistence Behavior

The header itself has no state. It exposes functions whose implementations mutate remote domain state, local secrets, local config, and keytabs depending on context flags.

## Dependencies and Integration Points

This is the stable include surface for command-line tools and other source3 components that need domain join functionality without including the large implementation file.

## Risks and Test Signals

The main risk is API misuse: contexts must be initialized before use and must contain valid domain, messaging, credential, and flag fields. Tests should compile users against this header and exercise successful and failing join/unjoin calls through initialized contexts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_join.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_join_offline.c -->
# sources/user-network-fs/samba/source3/libnet/libnet_join_offline.c

## Purpose

`libnet_join_offline.c` composes and reads Windows Offline Domain Join provision data for Samba join flows.

## Important APIs, Types, and Functions

The public functions are `libnet_odj_compose_ODJ_PROVISION_DATA`, `libnet_odj_find_win7blob`, and `libnet_odj_find_joinprov3`. Internal composers build `ODJ_WIN7BLOB`, `OP_JOINPROV3_PART`, `OP_PACKAGE_PART`, `OP_PACKAGE_PART_COLLECTION`, and `OP_PACKAGE`. `libnet_odj_compose_OP_JOINPROV2_PART` is a stub returning `WERR_INVALID_LEVEL`.

## Control Flow

Composition starts with `libnet_odj_compose_ODJ_PROVISION_DATA`, which allocates two blobs: a Win7-format blob containing domain, machine, password, SID/GUID, and DC info; and a Win8-format OP package containing join-provider and join-provider3 parts. Provider3 carries account RID and full account SID string. Lookup functions scan provision blobs; `find_win7blob` accepts either direct Win7 format or Win8 package provider data, while `find_joinprov3` searches Win8 package parts for the provider3 GUID.

## State and Persistence Behavior

All data is talloc-owned in-memory NDR model state. The file does not serialize to disk directly, but callers can marshal the generated `ODJ_PROVISION_DATA`. Sensitive machine password material is embedded in the provision blob.

## Dependencies and Integration Points

It depends on generated ODJ and libnet-join NDR types, domain SID helpers, and Netlogon DC-info copying. `libnet_join.c` uses the find helpers during offline join and composition can serve provisioning workflows.

## Risks and Test Signals

Risks include clear machine password presence, provider2 unimplemented, assumptions about package part pointers being populated, and returning `WERR_BAD_FORMAT` for unknown blob formats. Tests should round-trip composed data through NDR, verify Win7 and provider3 extraction, cover missing wrapped collections, invalid GUID levels, machine account names with trailing `$`, and offline join consumption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_join_offline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_join_offline.h -->
# sources/user-network-fs/samba/source3/libnet/libnet_join_offline.h

## Purpose

`libnet_join_offline.h` declares helper APIs for composing and extracting Offline Domain Join provision structures.

## Important APIs, Types, and Functions

It declares `libnet_odj_compose_ODJ_PROVISION_DATA`, `libnet_odj_find_win7blob`, and `libnet_odj_find_joinprov3`. These functions operate on generated `ODJ_PROVISION_DATA`, `ODJ_WIN7BLOB`, and `OP_JOINPROV3_PART` types and a `libnet_JoinCtx`.

## Control Flow

Provisioning callers compose ODJ data from a populated join context. Offline join callers parse incoming provision data by extracting the Win7 domain/machine blob and provider3 RID/SID part.

## State and Persistence Behavior

The header has no state. Implementations allocate returned structures under caller-provided talloc contexts and expose data that may include machine passwords.

## Dependencies and Integration Points

It is consumed by `libnet_join.c` and relies on generated ODJ NDR declarations being visible to compilation units that include it.

## Risks and Test Signals

Risks are mostly contract-level: callers must pass valid generated ODJ structures and protect sensitive provision data. Tests should compile include users and verify compose/find behavior through the C implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_join_offline.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_keytab.c -->
# sources/user-network-fs/samba/source3/libnet/libnet_keytab.c

## Purpose

`libnet_keytab.c` provides Kerberos keytab management helpers for libnet code. It opens a writable keytab, stages entries, removes duplicates or stale entries, derives keys from supplied password/key material, adds entries, and searches existing entries.

## Important APIs, Types, and Functions

Public functions are `libnet_keytab_init`, `libnet_keytab_add`, `libnet_keytab_search`, and `libnet_keytab_add_to_keytab_entries`. Internal helpers are `keytab_close`, `libnet_keytab_remove_entries`, and `libnet_keytab_add_entry`.

## Control Flow

Initialization creates a Kerberos context, opens a relative keytab with write access, records its resolved name, and installs a talloc destructor. Callers stage entries with `libnet_keytab_add_to_keytab_entries`, which builds `prefix/name@realm` principals. `libnet_keytab_add` optionally removes all old entries matching staged principals/enctypes, then for each staged entry removes the exact duplicate kvno/enctype principal and calls `libnet_keytab_add_entry`. Adding parses the principal, fetches Samba's salt principal from secrets, derives a Kerberos key with `create_kerberos_key_from_string`, and writes it. Search iterates the keytab for exact principal, kvno, and enctype and returns copied key bytes.

## State and Persistence Behavior

State lives in `libnet_keytab_context`: Kerberos context, keytab handle/name, ADS pointer, DNS realm, staged entries, and `clean_old_entries`. Persistent effects are mutations to the target keytab. The code is compiled only under `HAVE_KRB5`.

## Dependencies and Integration Points

It depends on Samba Kerberos wrappers, ADS/secrets helpers, talloc arrays, and keytab context types from `libnet_keytab.h`. It is used by DSSync keytab import and join keytab synchronization paths.

## Risks and Test Signals

Risks include deriving keys even when caller already has raw key material semantics, reliance on secrets salt principal, keytab iteration restart during removal, exact kvno matching in search, and sensitive key bytes in memory. Tests should cover init failure paths, duplicate replacement, clean-old behavior ignoring kvno, search hits/misses, multi-enctype entries, and builds without Kerberos.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_keytab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_keytab.h -->
# sources/user-network-fs/samba/source3/libnet/libnet_keytab.h

## Purpose

`libnet_keytab.h` declares libnet keytab context and helper APIs when Samba is built with Kerberos support.

## Important APIs, Types, and Functions

Inside `#ifdef HAVE_KRB5`, `struct libnet_keytab_entry` stores display name, principal, password/key blob, kvno, and enctype. `struct libnet_keytab_context` stores Kerberos handles, keytab name, ADS pointer, DNS realm, staged entries, and cleanup flag. It declares initialization, add, search, and staging functions implemented in `libnet_keytab.c`.

## Control Flow

Users initialize a context, set fields such as `dns_domain_name` and `clean_old_entries`, stage entries, then call `libnet_keytab_add`. Search supports consumers that need to recover existing synthetic or real keytab entries.

## State and Persistence Behavior

The header defines talloc-owned in-memory staging structures for persistent keytab writes. `DATA_BLOB password` may hold plaintext-like input, raw keys, or serialized state depending on caller convention.

## Dependencies and Integration Points

It depends on Kerberos types, Samba `DATA_BLOB`, and `struct ads_struct`. It is included by keytab utilities, DSSync keytab backend, and join-related code.

## Risks and Test Signals

Risks include all APIs disappearing in non-Kerberos builds, ambiguous `password` semantics, and callers needing to set DNS realm before principal construction. Test signals are compile coverage with and without `HAVE_KRB5` plus functional keytab add/search tests through the implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/libnet_keytab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/netapi.pc.in -->
# sources/user-network-fs/samba/source3/libnet/netapi.pc.in

## Purpose

`netapi.pc.in` is the pkg-config template for Samba's `libnetapi` client library.

## Important APIs, Types, and Functions

It defines substitution variables `prefix`, `exec_prefix`, `libdir`, and `includedir`, and pkg-config fields `Name`, `Description`, `Version`, `Libs`, `Cflags`, and `URL`. `@PACKAGE_VERSION@` and `@LIB_RPATH@` are replaced by the build system.

## Control Flow

There is no runtime control flow. During installation/configuration, the template becomes a `.pc` file consumed by `pkg-config`.

## State and Persistence Behavior

The installed `.pc` file persists build-time paths and linker flags. Consumers use it to compile and link against `-lnetapi`.

## Dependencies and Integration Points

The template integrates Samba's install layout with external build systems. `Libs` points at `${libdir}` and `Cflags` at `${includedir}`.

## Risks and Test Signals

Risks include stale path substitution, missing rpath flags where needed, and the URL using plain HTTP. Test signals are `pkg-config --cflags --libs netapi`, successful external compilation using libnetapi headers, and install packaging checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libnet/netapi.pc.in -->
