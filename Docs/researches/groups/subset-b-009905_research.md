# Research: subset-b-009905

This grouped report covers the requested Samba DSDB trust, DNS update, forest trust scanner, gMSA/GKDI, and KCC files. Each section is bounded by source-path markers so the reconciliation lane can split it into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_trusts.c -->
# sources/user-network-fs/samba/source4/dsdb/common/util_trusts.c

## Purpose

`util_trusts.c` is the DSDB trust utility implementation for Active Directory trusted domain objects, forest trust information, trust routing, and claims transformation policy lookup. It converts local `crossRef` partition objects and trustedDomain (`TDO`) records into LSA trust structures, builds forest-trust record lists, normalizes and merges forest trust data, detects collisions, searches trustedDomain objects by name/SID/type, extracts incoming trust passwords, and builds a routing table used by name/SID trust resolution.

## Important APIs, Types, and Functions

- `dsdb_trust_forest_info_add_record()` is the internal copy/validation helper for `lsa_ForestTrustRecord2` entries. It deep-copies DNS, NetBIOS, SID, scanner-info, and binary records into a `lsa_ForestTrustInformation2` array and rejects malformed names, missing mandatory strings, overlong NetBIOS names, and invalid record types.
- `dsdb_trust_parse_crossref_info()`, `dsdb_trust_crossref_tdo_info()`, `dsdb_trust_local_tdo_info()`, and `dsdb_trust_xref_tdo_info()` synthesize `lsa_TrustDomainInfoInfoEx` structures from `crossRef` records under `CN=Partitions`.
- `dsdb_trust_xref_forest_info()` enumerates local forest crossRefs and UPN/SPN suffixes into an LSA forest-trust information list.
- `dsdb_trust_parse_tdo_info()`, `dsdb_trust_parse_forest_info()`, and `dsdb_trust_default_forest_info()` parse TDO attributes and create default forest trust blobs.
- `dsdb_trust_normalize_forest_info_step1()` validates, copies, de-duplicates, strips one trailing dot from DNS names, and checks TLN/domain relationships while preserving original indexes by leaving duplicate slots as NULL.
- `dsdb_trust_normalize_forest_info_step2()` compacts/reorders records in Windows-compatible order and assigns timestamps where missing.
- `dsdb_trust_verify_forest_info()` compares new forest-trust information against a reference forest and records TLN, NetBIOS, and SID collisions in `lsa_ForestTrustCollisionInfo`.
- `dsdb_trust_merge_forest_info()` merges existing and newly discovered forest trust information, preserving admin-disabled domain records, exclusions, scanner info, binary records, times, and flags where applicable.
- `dsdb_trust_search_tdo()`, `dsdb_trust_search_tdo_by_type()`, `dsdb_trust_search_tdo_by_sid()`, and `dsdb_trust_search_tdos()` are search helpers over the local System container.
- `dsdb_trust_get_incoming_passwords()` parses `trustAuthIncoming`, selects current/previous NTOWF trust passwords, and hashes cleartext secrets with MD4.
- `dsdb_trust_routing_table_load()`, `dsdb_trust_routing_by_name()`, `dsdb_trust_domain_by_sid()`, and `dsdb_trust_domain_by_name()` build and query in-memory routing state for trusted forests/domains.
- `dsdb_trust_get_claims_tf_policy()` validates a TDO-linked claims transformation policy DN, reads `msDS-TransformationRules`, unwraps XML, and parses the claims rule set.

## Control Flow

The crossRef path starts at a domain DN, searches `CN=Partitions` for the matching `crossRef`, parses its DNS/NetBIOS/SID from `ncName` extended DN metadata, and optionally follows `rootTrust` and `trustParent` crossRef links. Forest info generation then sorts crossRefs so forest-root and parent domains are handled predictably, adds top-level names and domain-info records, adds UPN/SPN suffixes that are not covered by existing TLNs, and removes child TLNs when a parent TLN covers the same namespace.

Forest trust normalization is split into two explicit phases. Step 1 deep-copies input, sanitizes DNS names, rejects impossible TLN/exclusion/domain relationships, and NULLs duplicates while retaining count/index positions for collision reporting. Step 2 traverses the Step 1 result in reverse groups: TLN/TLN_EX first, domain-info second, scanner-info third, binary data last. It also fills zero timestamps with the current time.

Collision verification scans each new TLN and domain-info record against a reference forest trust list. For TLNs, overlapping enabled names produce `LSA_TLN_DISABLED_CONFLICT` unless exclusions or disabled flags allow coexistence. For domain-info records, SID and NetBIOS conflicts set corresponding disabled flags, while DNS and NetBIOS strings may be normalized to existing casing. Merge then constructs a final list by adding unique TLNs, unique domains, retained admin-disabled old domains, still-valid exclusions, scanner records, and binary records.

Routing-table loading first models the local domain from crossRef data. If the local domain is the forest root, or the local domain has a root-direction TDO, it attaches local forest info generated from crossRefs. It then appends all TDOs, parsing forest trust blobs for forest-transitive trusts. Routing lookups iterate this list and prefer exact NetBIOS/DNS/SID matches or the most specific enabled TLN that covers a child name.

## State and Persistence Behavior

Most functions build talloc-owned transient structures, but their inputs and outputs mirror persisted AD data. Persistent reads include `crossRef` attributes, `trustedDomain` attributes, `msDS-TrustForestTrustInfo`, `trustAuthIncoming`, `uPNSuffixes`, `msDS-SPNSuffixes`, and claims policy objects. This file itself does not usually modify LDB state; it prepares data for callers that write trust blobs or make routing decisions. Password extraction zeroes the local selected password structs before freeing the stack frame, but the returned `samr_Password` copies remain caller-owned.

## Dependencies and Integration Points

The file sits between DSDB/LDB search helpers, generated LSA/DRS NDR structures, DNS comparison helpers, LSARPC forest trust conversion helpers, security/claims code, and crypto helpers. It is consumed by trust RPC implementations, forest-trust scanning, authentication/routing logic, and claims transformation enforcement.

## Risks

The main behavioral risk is compatibility with Windows forest-trust semantics. List order, duplicate retention, disabled flags, and collision indexes are observable through LSA APIs. DNS comparison uses `dns_cmp()` and must preserve case-normalized values without allowing malformed names. Trust password parsing handles secret material and must avoid lifetime mistakes or accidental logging. Routing lookups are security-sensitive because an incorrect best TLN or disabled-flag interpretation can send authentication or authorization traffic to the wrong trust.

## Test Signals

Useful tests include forest trust normalization with trailing dots, duplicates, TLN/TLN_EX hierarchy violations, scanner-info records, admin-disabled records, SID/NetBIOS collisions, and Windows trace-compatible ordering. Routing tests should cover exact NetBIOS, exact DNS, child DNS best-match, disabled TLN/SID/NB flags, non-transitive trusts, downlevel trusts, and missing forest trust blobs. Secret tests should cover `trustAuthIncoming` with NTOWF, cleartext, previous-missing fallback, corrupt NDR, and absent attributes. Claims policy tests should cover DN containment, missing rules, malformed XML/rules, and non-policy objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/common/util_trusts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/dns/dns_update.c -->
# sources/user-network-fs/samba/source4/dsdb/dns/dns_update.c

## Purpose

`dns_update.c` registers Samba's `dnsupdate` task service for Active Directory domain controllers. The service periodically runs configured helper commands to update DC DNS names and SPNs, and exposes an IRPC endpoint used by netlogon to request RODC DNS updates for a specific read-only domain controller.

## Important APIs, Types, and Functions

- `struct dnsupdate_service` stores task context, system session credentials, local `samdb`, and periodic command state for configuration/name updates.
- `dnsupdate_check_names()` starts the configured `dns update command` and `spn update command` asynchronously through `samba_runcmd_send()`.
- `dnsupdate_nameupdate_done()` and `dnsupdate_spnupdate_done()` receive command completion and log success/failure.
- `dnsupdate_nameupdate_schedule()` and `dnsupdate_nameupdate_handler_te()` implement the `dnsupdate:name interval` tevent timer.
- `struct dnsupdate_RODC_state` tracks an async RODC update request, temporary files, and the deferred IRPC reply.
- `dnsupdate_dnsupdate_RODC()` validates the target RODC, writes requested DNS records to a temporary update-list file, launches the DNS update command with `--update-list` and `--update-cache`, and defers the IRPC reply until completion.
- `dnsupdate_task_init()` starts the service only on AD DCs, connects to samdb as system, runs the first update, schedules periodic updates, and registers the `"dnsupdate"` IRPC name and `DNSUPDATE_RODC` handler.
- `server_service_dnsupdate_init()` registers the task service.

## Control Flow

Service initialization rejects non-AD-DC roles, creates service state, obtains `system_session()`, opens local samdb, reads the name-update interval (default 600 seconds), performs an immediate DNS/SPN update, schedules the next timer, and registers IRPC. On each timer, the handler calls `dnsupdate_check_names()` and reschedules itself.

For regular updates, existing DNS update child state is freed before starting a new DNS update command. The code then starts the SPN update command independently. Both commands have a 20 second startup timeout and use callbacks to clear request pointers and log exit status.

For RODC updates, the IRPC handler creates a temporary update-list file and a cache path. It maps the incoming domain SID to a DN, finds the RODC site and NTDS GUID, reads `dNSHostName`, and writes only supported `NL_DNS_NAME_INFO` record types as SRV or CNAME update instructions. It then closes the file, launches the DNS update command with file arguments, marks the IRPC message as deferred, and replies from `dnsupdate_RODC_callback()`. The callback maps command failure to an NTSTATUS result and applies that status to every returned DNS name entry.

## State and Persistence Behavior

The service does not directly modify DNS zones; persistence is delegated to the configured helper scripts and their caches. It reads samdb for RODC site, NTDS GUID, and hostname. Temporary update-list and cache files are owned by `dnsupdate_RODC_state`; the destructor closes the fd if still open and unlinks both paths. Periodic state is in-memory tevent timers and child requests.

## Dependencies and Integration Points

This task integrates with Samba service registration, `samba_runcmd`, loadparm command settings, samdb helpers, netlogon IRPC, and the external `samba_dnsupdate`/SPN update commands. It depends on AD DC role configuration and local system credentials.

## Risks

Command execution and temporary file handling are the primary operational risks. A failed helper command only logs and retries later, so persistent misconfiguration can leave DNS/SPN data stale. The regular DNS update frees only `nameupdate.subreq` before launching a new run, so concurrent SPN update handling depends on the previous SPN request lifetime and command behavior. RODC requests trust the input DNS-name type enum and write update lines; future enum additions need explicit handling. Error mapping in command callbacks uses `sys_errno` as the logged exit code, so diagnostics may be confusing if the helper exits normally with a nonzero status.

## Test Signals

Tests should assert service startup behavior by role, interval scheduling, immediate command launch, callback cleanup, and graceful command failure. RODC tests should cover missing site, missing NTDS GUID, missing `dNSHostName`, each supported DNS name type, temporary-file cleanup on early errors, deferred IRPC reply, and per-name result propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/dns/dns_update.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_periodic.c -->
# sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_periodic.c

## Purpose

`ft_scanner_periodic.c` provides the periodic scheduler for the forest trust scanner task. It controls when the scanner runs and ensures only the current PDC emulator performs trust scanning.

## Important APIs, Types, and Functions

- `ft_scanner_periodic_schedule()` schedules or reschedules the next tevent timer for a `struct ft_scanner_service`.
- `ft_scanner_periodic_handler_te()` is the timer callback; it clears the current timer, runs the scanner, then schedules the next regular interval.
- `ft_scanner_periodic_run()` checks whether the local DC is the current PDC and invokes `ft_scanner_check_trusts()`.

## Control Flow

Scheduling clamps a zero interval to one second to avoid tight loops, computes `timeval_current_ofs(next_interval, 50)`, and compares it with any already scheduled timestamp. If an existing event is earlier than the proposed one, no reschedule occurs. Otherwise, it creates a new tevent timer, logs the scheduled time, frees the old timer, and stores the new timer.

When the timer fires, the handler clears `service->periodic.te`, runs the scanner, and schedules the next run using `service->periodic.interval`. If scheduling fails, it terminates the task. The run function uses `samdb_is_pdc()` to avoid multi-DC writers. Non-PDC DCs log a no-op. The PDC calls `ft_scanner_check_trusts()` and logs warnings on failure; it does not terminate the task for scan errors.

## State and Persistence Behavior

This file owns only in-memory timer state: `periodic.interval`, `periodic.next_event`, and `periodic.te`. It does not write samdb itself. Persistence occurs indirectly through `ft_scanner_check_trusts()` in `ft_scanner_tdos.c`.

## Dependencies and Integration Points

It depends on `struct ft_scanner_service` from `ft_scanner_service.h`, samdb PDC-role detection, tevent timers, task termination, and the scanner entry point declared through `ft_scanner_service_proto.h`.

## Risks

The scheduler intentionally avoids delaying an already earlier event, which is important if callers request an immediate or startup scan. Incorrect PDC detection would either suppress scanning or cause multiple DCs to race on trust blob updates. The 50 microsecond offset is small and mostly prevents exact-now scheduling edge cases; tests should avoid depending on exact timestamps.

## Test Signals

Tests should cover zero interval clamping, no-op reschedule when an earlier timer exists, replacement when a sooner timer is requested, PDC-only scanner invocation, non-fatal scan failure, and task termination on timer allocation/reschedule failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_periodic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_service.c -->
# sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_service.c

## Purpose

`ft_scanner_service.c` registers and initializes the `ft_scanner` task service. The service periodically scans inbound forest-transitive trusts from writable AD DCs and records discovered trusted-forest domain data into trust forest information.

## Important APIs, Types, and Functions

- `ft_scanner_connect_samdb()` obtains a system session and connects `service->l_samdb` to local samdb.
- `ft_scanner_task_init()` performs role gating, allocates `struct ft_scanner_service`, connects samdb, rejects RODCs, reads configuration intervals, schedules the startup timer, and registers the service IRPC name.
- `server_service_ft_scanner_init()` registers the service under name `"ft_scanner"`.

## Control Flow

Startup is role-gated. Standalone and domain-member roles terminate the task with `NT_STATUS_INVALID_DOMAIN_ROLE`; AD DCs continue. After service allocation, `startup_time` is recorded and the task's private data is set. A local samdb connection is opened as the system session. The code queries `samdb_rodc()` and refuses to run on RODCs because the scanner writes local trust metadata.

The service reads `ft_scanner:periodic_startup_interval` with a default of 15 seconds and `ft_scanner:periodic_interval` with a default of 900 seconds. The regular interval is clamped to at least 60 seconds. It then schedules the first scan with the startup interval and registers `"ft_scanner"` on the messaging context. There are no file-local IRPC handlers in this file.

## State and Persistence Behavior

Persistent effects are indirect. Initialization stores service state on the task talloc tree and opens samdb. Actual trust-object modifications occur in `ft_scanner_tdos.c`. Configuration values are read from loadparm at startup; changing them after startup will not affect the already stored interval unless the service is restarted.

## Dependencies and Integration Points

The file integrates with Samba's server service framework, auth system sessions, local samdb, loadparm, IRPC naming, and the scheduler from `ft_scanner_periodic.c`. It is compiled with the scanner implementation and generated local prototypes.

## Risks

The service must not run on RODCs or non-DC roles. Failing open would allow unauthorized or impossible writes. Startup failures terminate the task, which is appropriate for missing local samdb but can make deployment problems visible as service absence. The minimum 60 second regular interval protects against busy scan loops; tests should confirm this clamp.

## Test Signals

Tests should cover role-based startup decisions, RODC rejection, samdb connection failure handling, interval defaults and clamping, startup scheduling errors, IRPC name registration, and successful service registration details (`inhibit_fork_on_accept`, `inhibit_pre_fork`, task init pointer).
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_service.h -->
# sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_service.h

## Purpose

`ft_scanner_service.h` defines the shared service state for Samba's forest trust scanner task. The structure is used by service initialization, periodic scheduling, and trust scanning code.

## Important APIs, Types, and Functions

- `struct ft_scanner_service` contains:
  - `task`: the owning `struct task_server`.
  - `startup_time`: timestamp captured at service creation.
  - `l_samdb`: local samdb connection used for PDC checks, TDO searches, and trust blob writes.
  - `periodic.interval`: regular scan interval in seconds.
  - `periodic.next_event`: timestamp of the currently scheduled event.
  - `periodic.te`: the active tevent timer.

There are no function declarations in this header beyond the type definition; function prototypes are supplied by the generated `ft_scanner_service_proto.h`.

## Control Flow

The header does not implement control flow, but its fields define the service lifecycle. `ft_scanner_service.c` allocates and initializes the structure, `ft_scanner_periodic.c` mutates `periodic` fields during timer scheduling, and `ft_scanner_tdos.c` uses `task`, `l_samdb`, and `periodic.interval` for asynchronous scan work and timeout calculation.

## State and Persistence Behavior

All state here is in-memory and tied to the task talloc lifetime. `l_samdb` is a live database connection, but the header itself does not define persisted attributes. The periodic fields are process-local scheduler state and are lost on restart.

## Dependencies and Integration Points

The type depends on Samba task server, timeval, LDB context, and tevent timer definitions from included compilation units. It is the shared contract among the ft_scanner service, scheduler, and TDO scanner.

## Risks

Because the structure is shared across asynchronous callbacks, lifetime must stay rooted under the task for the duration of outstanding timers and scan requests. Future fields that are mutated by callbacks should be considered single-event-loop state unless explicit locking is added. The spelling/comment typo "between to periodic runs" is harmless but indicates comments should not be treated as API.

## Test Signals

Compile-time integration is the main signal. Runtime tests should indirectly validate that `periodic.te` replacement, `l_samdb` availability, and task-private data casting remain consistent across service startup, timer callbacks, and scanner callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_service.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_tdos.c -->
# sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_tdos.c

## Purpose

`ft_scanner_tdos.c` implements the forest-trust scanner. It finds inbound forest-transitive trustedDomain objects, connects to a GC-capable DC in each trusted forest, reads the remote forest's crossRef domain list, and updates the local `msDS-TrustForestTrustInfo` blob with `FOREST_TRUST_SCANNER_INFO` records for discovered domains.

## Important APIs, Types, and Functions

- `struct ft_scanner_scann_forest_state` is the async per-forest state: target TDO, discovery data, LDAP connection, TLS/GENSEC settings, partitions DN, and discovered domain array.
- `ft_scanner_scann_forest_send()` starts the async chain by selecting LDAP wrapping mode, setting DC discovery requirements, and calling `finddcs_cldap_send()`.
- The callback chain is `found_dc -> tcp_connected -> optional starttls -> optional tls_connect -> gensec_bind -> rootDSE config search -> partitions container search -> crossRef search -> done`.
- `ft_scanner_scann_forest_recv()` returns the discovered `ForestTrustDataDomainInfo` array.
- `struct ft_scanner_check_trusts_state` and `struct ft_scanner_check_trusts_domain` track all outstanding forest scans for one periodic run.
- `ft_scanner_check_trusts()` searches all TDOs and launches scans for inbound forest-transitive trusts with a bounded end time.
- `ft_scanner_check_trusts_scanned()` receives scan results, revalidates the TDO inside a transaction, updates scanner-info records, and frees the shared run state when all scans complete.

## Control Flow

`ft_scanner_check_trusts()` reads trust attributes via `dsdb_trust_search_tdos()`, parses each TDO, filters to inbound forest-transitive trusts, and starts one async scan per qualifying TDO. The timeout is usually `periodic.interval - 15` when the interval is above 75 seconds, otherwise the full interval.

The scan chain discovers a remote DC with LDAP, DS, and GC flags. It builds a target principal `ldap/<dc>/<domain>@<UPPERDOMAIN>`, creates an address using the discovered IP and port 389 or 636, opens TCP, constructs a tldap context, optionally performs StartTLS or LDAPS based on client LDAP SASL wrapping settings, and binds with system credentials using `tldap_gensec_bind_send()`. With the LDAP session established, it reads `configurationNamingContext` from rootDSE, searches `CN=Partitions` for the crossRef container, then searches child `crossRef` objects whose `systemFlags` indicate domain NCs. It extracts `dnsRoot` and `nETBIOSName` into an array and disconnects.

On completion, the callback starts an LDB transaction and re-searches the TDO by original object GUID. It verifies the SID, DNS name, NetBIOS name, inbound direction, and forest-transitive attribute still match. It parses existing forest trust info or creates the default TLN/domain-info blob. It removes stale scanner-info records not present in the latest remote scan, appends missing scanner-info records with current timestamp, NDR-encodes the updated `ForestTrustInfo`, replaces `msDS-TrustForestTrustInfo`, and commits. If nothing changed, it cancels the transaction.

## State and Persistence Behavior

Persistent state is the trustedDomain object's `msDS-TrustForestTrustInfo` attribute. Scanner-info records are derived cache entries and can be removed if no longer found remotely. The code is careful to re-read by GUID and revalidate TDO identity before modifying to avoid acting on stale async state. Transaction boundaries protect each trust blob update. Async state is talloc-owned by the periodic run and is released after the last outstanding scan callback clears its domain's `state` pointer.

## Dependencies and Integration Points

The file integrates with trust helpers from `util_trusts.c`, CLDAP DC discovery, tstream sockets, tldap, TLS parameter loading, GENSEC bind, loadparm LDAP wrapping policy, generated DRS forest trust NDR structures, and local samdb transactions. It is invoked only through the ft_scanner periodic service.

## Risks

This is network and security sensitive. TLS/wrapping configuration determines whether LDAP signing/sealing or TLS protects remote queries. Remote responses are minimally validated: current code reads DNS and NetBIOS names but not SIDs from remote crossRefs, while equality checks for scanner-info include SID, so additions may carry zero/default SID values. Availability failures are intentionally logged and retried later, not fatal. Concurrent TDO changes are handled by revalidation, but modifications by other writers after the transaction starts may still require normal LDB conflict handling. The function name contains `scann`, which is cosmetic but visible in symbols.

## Test Signals

Tests should exercise DC discovery failure, missing PDC DNS name, TCP/TLS/StartTLS/GENSEC failures, rootDSE shape errors, empty partitions result, malformed crossRef attributes, timeout behavior, no-trust/no-forest-trust fast paths, TDO mutation between launch and callback, default forest info creation, stale scanner-info removal, missing scanner-info addition, no-op update cancellation, and transaction commit/cancel behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/ft_scanner/ft_scanner_tdos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/gmsa/gkdi.c -->
# sources/user-network-fs/samba/source4/dsdb/gmsa/gkdi.c

## Purpose

`gkdi.c` implements DSDB accessors and creators for Group Key Distribution Infrastructure root keys used by gMSA password derivation. It converts `msKds-ProvRootKey` LDB messages into crypto-layer `ProvRootKey` objects, creates new root-key objects from GKDI server configuration, finds a root key by GUID, and selects the most recently created usable root key before a requested time.

## Important APIs, Types, and Functions

- `gkdi_root_key_from_msg()` reads `msKds-Version`, `msKds-CreateTime`, `msKds-UseStartTime`, `msKds-DomainID`, `msKds-RootKeyData`, `msKds-KDFAlgorithmID`, and `msKds-KDFParam`, parses the KDF algorithm, and calls `ProvRootKey()`.
- `gkdi_root_key_use_start_time()` calculates a use start time from the current GKDI interval plus key cycle duration and max clock skew. The source comments note it is unused.
- `gkdi_create_root_key()` is the internal root-key object creator. It reads server configuration, validates supported version/KDF parameters, generates random root key data and GUID, populates an `msKds-ProvRootKey` add message, and calls `dsdb_add()`.
- `root_key_attrs` defines the attributes needed by callers; public/private/secret-agreement fields are intentionally excluded because Samba does not implement GKDI public-key functionality.
- `gkdi_new_root_key()` creates a root key and reads the resulting object back.
- `gkdi_root_key_from_id()` searches a root key by GUID-derived DN.
- `gkdi_most_recently_created_root_key()` searches the root-key container for keys with `msKds-UseStartTime <= not_after`, parses GUIDs from RDNs, and returns the candidate with greatest `msKds-CreateTime`.

## Control Flow

Root-key creation first locates the GKDI server configuration object under `CN=Group Key Distribution Service Server Configuration,...,CN=Services`. Missing configuration blocks creation. It requires readable `msKds-Version` and only supports version 1. It defaults missing KDF settings to SP800-108 CTR HMAC with SHA512 parameters, defaults secret agreement settings to DH and built-in FFC DH parameters, defaults public/private key lengths, generates root secret bytes with `generate_secret_buffer()`, sets create and use times, stores the server reference DN as `msKds-DomainID`, creates a random GUID from generated bytes, derives the root-key DN, and adds the object.

Selection by ID constructs the canonical root-key DN and reads `root_key_attrs`. Selection by time scans one level below the root-key container, not sorting in LDB. It filters candidates by RDN length and GUID parseability, then compares create times in process. If no suitable key exists, it maps the error to `HRES_NTE_NO_KEY`.

## State and Persistence Behavior

This file persists new GKDI root keys as `msKds-ProvRootKey` objects. Root key data is generated randomly and stored in `msKds-RootKeyData`; use/start timestamps and algorithm parameters are replicated AD attributes. Read functions return talloc-owned LDB messages or crypto objects. No transaction is started locally around `dsdb_add()`, so callers that need grouping must provide broader transaction context.

## Dependencies and Integration Points

It depends on `lib/crypto/gkdi`, generated GKDI NDR, DSDB LDB helpers, `samdb_gkdi_root_key_dn()`/container helpers, and Samba random secret generation. `gmsa/util.c` uses these APIs to derive current and previous managed service account passwords.

## Risks

Root-key creation is security-critical. Unsupported or unreadable server configuration must fail closed. Default DH parameters and KDF parameters must remain protocol-compatible. Random GUID generation via random bytes then `GUID_from_ndr_blob()` means invalid NDR conversion would fail creation. `gkdi_most_recently_created_root_key()` ignores malformed RDNs and relies on `msKds-CreateTime`; duplicate or clock-skewed keys can affect selection. The source notes Windows gives up with more than 1000 keys, but this implementation does not enforce that limit.

## Test Signals

Tests should cover missing server configuration, unreadable/missing version, unsupported version, default and explicit KDF params, unsupported KDF, missing secret agreement params, successful add/readback, GUID DN construction, no-key error mapping, malformed root-key RDNs, multiple candidate create times, future `UseStartTime` exclusion, and conversion from LDB message to `ProvRootKey`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/gmsa/gkdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/gmsa/gkdi.h -->
# sources/user-network-fs/samba/source4/dsdb/gmsa/gkdi.h

## Purpose

`gkdi.h` declares the DSDB-facing GKDI root-key API used by gMSA code. It exposes conversion from LDB root-key messages to crypto objects, root-key use-start-time calculation, root-key creation, lookup by GUID, and lookup of the most recent usable root key.

## Important APIs, Types, and Functions

- Forward declarations: `struct ldb_message`, `struct ldb_context`, and `struct ProvRootKey`.
- `gkdi_root_key_from_msg()` converts a root-key LDB message and known GUID into a `ProvRootKey`.
- `gkdi_root_key_use_start_time()` calculates a protocol-oriented use start time from a current time.
- `gkdi_new_root_key()` creates and returns a new root-key LDB message.
- `gkdi_root_key_from_id()` reads a root-key LDB message by GUID.
- `gkdi_most_recently_created_root_key()` selects a usable key by time bounds.

## Control Flow

The header does not implement control flow. It defines the boundary between DSDB/LDB storage and crypto derivation. Callers generally fetch a message with one of the LDB-returning functions and then call `gkdi_root_key_from_msg()` to obtain a `ProvRootKey` suitable for password derivation.

## State and Persistence Behavior

The API implies two ownership patterns: returned `struct ldb_message` pointers are talloc-owned by the caller-supplied memory context, while returned `ProvRootKey` objects are also caller-owned. `gkdi_new_root_key()` is the only declared function that creates persistent directory state.

## Dependencies and Integration Points

The header includes talloc, `DATA_BLOB`, time, NTSTATUS, and GUID definitions. It is consumed by `gmsa/util.c` and implemented by `gkdi.c`.

## Risks

Because this header hides LDB details behind integer return codes for lookup/create functions and NTSTATUS for conversion, callers must handle both LDB and NTSTATUS error domains. Future changes to root-key selection semantics need coordinated changes in both `gkdi.c` and gMSA rollover logic.

## Test Signals

Compile/link tests should verify that all declared functions are implemented. Behavioral tests should focus through `gkdi.c` and `gmsa/util.c`: creation, lookup, no-key errors, and conversion to `ProvRootKey`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/gmsa/gkdi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/gmsa/util.c -->
# sources/user-network-fs/samba/source4/dsdb/gmsa/util.c

## Purpose

`gmsa/util.c` implements Group Managed Service Account password access, derivation, packing, recalculation, and database update support. It computes gMSA passwords from GKDI root keys and account SID, determines when managed password IDs are stale, builds system password-update requests, updates `msDS-ManagedPasswordId`/previous ID, supports operational `msDS-ManagedPassword` blob generation, and redacts secrets on RODCs.

## Important APIs, Types, and Functions

- `gmsa_allowed_to_view_managed_password()` enforces `msDS-GroupMSAMembership` security descriptor access checks, allowing system unconditionally.
- `struct RootKey` models no key, a specific `KeyEnvelopeId`, a nonspecific key-start-time lookup, or an obtained root key plus derived password.
- `gmsa_managed_pwd_id()`, `gmsa_update_managed_pwd_id()`, and `gmsa_pack_managed_pwd_id()` parse/create/update/pack GKDI `KeyEnvelope` password IDs.
- `gmsa_specific_password()`, `gmsa_nonspecific_password()`, `gmsa_fetch_root_key()`, and `gmsa_get_root_key()` retrieve root keys and derive passwords.
- `gmsa_system_update_password_id_req()` builds an LDB modify request for current and previous password ID attributes and marks it `DSDB_FLAG_AS_SYSTEM`.
- `gmsa_generate_blobs()` creates a fresh managed password ID blob and password from the most recent root key usable within one GKDI interval.
- `gmsa_create_update()` prepares old password, new password, and password-ID update requests.
- `gmsa_pack_managed_pwd()` packs a `MANAGEDPASSWORD_BLOB` for operational attribute reads.
- `dsdb_account_is_gmsa()`, `gmsa_get_managed_pwd_id()`, `samdb_gmsa_key_is_recent()`, and `gmsa_recalculate_managed_pwd()` implement account classification and rollover logic.
- `dsdb_update_gmsa_entry_keys()` applies a prepared update transactionally after verifying the managed password ID has not changed.
- `dsdb_update_gmsa_keys()` updates all gMSA entries in a search result or redacts secrets when running on an RODC.
- `dsdb_gmsa_current_time()` and `dsdb_gmsa_set_current_time()` support real or test-injected time via LDB opaque `DSDB_GMSA_TIME_OPAQUE`.

## Control Flow

Access checks first inspect DSDB session info. System users are allowed; normal users must have read-property access through the `msDS-GroupMSAMembership` security descriptor using the account SID as object context.

Password derivation starts from a specific password ID or a desired key start time. Specific lookups fetch the root key by GUID and use the GKID from the ID. Nonspecific lookups select the most recently created root key with `UseStartTime <= key_start_time` and derive the GKID for that interval. `gmsa_fetch_root_key()` converts these pending descriptions into obtained root keys and derived null-terminated passwords; missing nonspecific keys are tolerated as "no key" for cases like optional previous passwords.

`gmsa_recalculate_managed_pwd()` is the main policy engine. It reads the rollover interval, creation time, object SID, and current `msDS-ManagedPasswordId`. If the current key has not expired, no database update is needed, although requested operational return data may still be derived. If expired or absent, it calculates the next key start time, determines whether the current key becomes the previous key, derives current and optional previous passwords, and creates update requests. For operational reads near expiration, it may return a future key as current and the existing current key as previous, extending `unchanged_interval` accordingly.

`dsdb_update_gmsa_entry_keys()` wraps updates in one transaction. Before applying requests, it re-reads `msDS-ManagedPasswordId` and compares it with the value observed during planning. If it differs, the function returns success without writing so the caller can retry the search. It then performs optional old password update, current password update, and password-ID update in order.

## State and Persistence Behavior

Persistent attributes touched include `unicodePwd`/password hashes through `gmsa_system_password_update_request()`, `msDS-ManagedPasswordId`, and `msDS-ManagedPasswordPreviousId`. The operational `msDS-ManagedPassword` blob is packed for return but not persisted by `gmsa_pack_managed_pwd()`. `dsdb_update_gmsa_keys()` only writes when connected locally through the partition module opaque; non-local connections skip writes. RODCs remove secret attributes from result messages so clients can be referred to writable DCs.

## Dependencies and Integration Points

The file integrates with GKDI storage APIs, `lib/crypto/gmsa`, generated GKDI/GMSA/security NDR, DSDB password update helpers, LDB requests/transactions, security descriptor access checks, session info opaques, and samdb RODC detection. It is used by DSDB search/operational attribute paths and KDC-facing account lookup flows.

## Risks

This code is secret-handling and time-sensitive. A wrong rollover calculation can make gMSA passwords stale, future-dated, or unavailable until time catches up. The comments explicitly note that out-of-band password resets are not detected until rollover because the managed password ID is treated as the source of truth. Missing root keys can make a gMSA unusable until the next rollover or permanently if required root keys are deleted. Transactional verification prevents overwriting concurrent updates but requires callers to honor `retry_out`. RODC redaction must remain complete for all secret attributes.

## Test Signals

Tests should cover system and non-system access checks, malformed membership security descriptors, absent/invalid password IDs, current-key-valid no-op, expired-key update creation, account younger than rollover, previous password ID handling, future-key return within max clock skew, missing specific root key error, missing nonspecific previous key tolerance, transaction conflict no-op, update request ordering, RODC secret redaction, non-local no-write behavior, test time opaque behavior, and NDR packing for `KeyEnvelope` and `MANAGEDPASSWORD_BLOB`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/gmsa/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/gmsa/util.h -->
# sources/user-network-fs/samba/source4/dsdb/gmsa/util.h

## Purpose

`gmsa/util.h` declares the public DSDB gMSA utility contract for managed password access checks, password ID packing, password derivation, operational password blob packing, account classification, managed password recalculation, database updates, and testable current time.

## Important APIs, Types, and Functions

- `struct gmsa_update` carries a prepared update: target DN, originally observed password ID, optional previous-password request, current-password request, and password-ID modify request.
- `struct gmsa_update_pwd_part` pairs a `ProvRootKey` with a `Gkid`.
- `struct gmsa_update_pwd` groups previous and new password parts.
- `gmsa_allowed_to_view_managed_password()` checks whether a caller can read a gMSA managed password.
- `gmsa_update_managed_pwd_id()` and `gmsa_pack_managed_pwd_id()` mutate and encode `KeyEnvelope` password IDs.
- `gmsa_generate_blobs()` produces a managed password ID blob and derived password for account creation or initialization.
- `gmsa_pack_managed_pwd()` encodes the operational `MANAGEDPASSWORD_BLOB`.
- `dsdb_account_is_gmsa()` identifies gMSA objects by objectClass.
- `gmsa_get_managed_pwd_id()` extracts a `KeyEnvelopeId`.
- `struct gmsa_return_pwd` carries previous/current passwords and query/unchanged intervals for operational reads.
- `samdb_gmsa_key_is_recent()`, `gmsa_recalculate_managed_pwd()`, `dsdb_update_gmsa_entry_keys()`, `dsdb_update_gmsa_keys()`, and `dsdb_gmsa_current_time()` expose rollover/update helpers.

## Control Flow

The header's contract splits gMSA operations into calculation and persistence. Callers can calculate an update with `gmsa_recalculate_managed_pwd()`, inspect returned password data if requested, then apply a prepared update through `dsdb_update_gmsa_entry_keys()` or let `dsdb_update_gmsa_keys()` process search results and signal retry.

## State and Persistence Behavior

`struct gmsa_update` intentionally stores both planned LDB requests and the password ID observed when planning. This enables compare-before-write behavior in the implementation. The `DSDB_GMSA_TIME_OPAQUE` macro defines an LDB opaque key for injecting current time in tests or controlled flows.

## Dependencies and Integration Points

The header depends on LDB, LDB modules, talloc, GKDI/GMSA crypto headers, `DATA_BLOB`, and Samba time types. It is consumed by DSDB modules that need to expose or maintain gMSA secrets.

## Risks

Because the header exposes raw password pointers in `gmsa_return_pwd` and update request pointers in `gmsa_update`, ownership and lifetime must be respected by callers. Any new secret attributes must be reflected in implementation redaction/update logic, not only in this contract.

## Test Signals

Compile tests should ensure C files include the header without circular dependency issues. Behavioral tests should validate all declared functions through `util.c`, especially update planning/application, operational password return, RODC handling, and time opaque injection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/gmsa/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/garbage_collect_tombstones.c -->
# sources/user-network-fs/samba/source4/dsdb/kcc/garbage_collect_tombstones.c

## Purpose

`garbage_collect_tombstones.c` implements DSDB garbage collection for deleted objects and expired tombstoned linked-attribute values. It is used by the KCC timed event and by `samba-tool domain expunge tombstones`.

## Important APIs, Types, and Functions

- `dsdb_garbage_collect_tombstones()` is the public entry point. It computes the expunge cutoff from current time and `tombstoneLifetime`, builds a search filter covering deleted objects and expired forward links, assembles needed attributes from the schema, and processes each naming context partition.
- `garbage_collect_tombstones_part()` processes one partition. It finds the Deleted Objects container, searches for candidates with internal/recycled visibility, deletes expired deleted objects, and removes expired deleted forward-link values.

## Control Flow

The public function gets the schema and computes `expunge_time` as `current_time - tombstoneLifetime * 24h`, both as LDAP generalized time and NTTIME. It builds an OR filter containing a custom `DSDB_MATCH_FOR_EXPUNGE` clause for every forward linked attribute, plus an `isDeleted=TRUE`/`whenChanged<=cutoff` clause. It also builds an attribute list containing all forward linked attributes plus `isDeleted`.

For each partition, the helper first tries to find its Deleted Objects DN. If a partition has none, it returns success. It searches the whole partition subtree with flags `DSDB_SEARCH_SHOW_RECYCLED`, `DSDB_SEARCH_SHOW_DN_IN_STORAGE_FORMAT`, and `DSDB_SEARCH_REVEAL_INTERNALS`. For each result with `isDeleted=TRUE`, it skips the Deleted Objects container itself and calls `dsdb_delete()` with recycled visibility and relaxed modify flags. For non-deleted results, it scans attributes, skips non-forward links and back links, parses deleted extended DN values, reads `RMD_CHANGETIME`, compares against cutoff, extracts target GUID, constructs a delete value in `<GUID=...>;DN` form, and batches deletes per object. The batch modify uses `DSDB_REPLMD_VANISH_LINKS`.

## State and Persistence Behavior

This code permanently deletes expired tombstone objects and removes expired link tombstones from forward linked attributes. It reports counts through `num_objects_removed` and `num_links_removed` and may set `error_string` for search failures. It does not wrap the entire run in one transaction; each delete/modify is attempted independently, with warnings for per-object failures.

## Dependencies and Integration Points

It depends on DSDB schema metadata, extended DN parsing, matching rules, recycled-object search flags, repl metadata vanish-link semantics, GUID parsing, and Samba time conversion. It is integrated into KCC periodic maintenance and administrative tombstone expunge tooling.

## Risks

The filter is deliberately complex to avoid loading the entire database unnecessarily. Schema mistakes or match-rule bugs can either miss expired values or return too many objects. The link cleanup path depends on internal extended DN components (`RMD_CHANGETIME`, `GUID`) being present and valid. `tombstoneLifetime` multiplication and subtraction assume sensible values; very large values or current times before the lifetime window could produce unexpected cutoffs. Because individual delete failures are logged but not fatal, partial cleanup is possible.

## Test Signals

Tests should cover partitions without Deleted Objects containers, expired and non-expired deleted objects, skipping the Deleted Objects container, forward-link tombstones before/after cutoff, malformed extended DN values, missing `RMD_CHANGETIME`, invalid GUID components, back-link exclusion, counter increments, search failure error strings, and partial delete/modify failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/garbage_collect_tombstones.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/garbage_collect_tombstones.h -->
# sources/user-network-fs/samba/source4/dsdb/kcc/garbage_collect_tombstones.h

## Purpose

`garbage_collect_tombstones.h` declares the public tombstone garbage collection entry point used by KCC and administrative tools.

## Important APIs, Types, and Functions

- `dsdb_garbage_collect_tombstones()` accepts a memory context, samdb connection, linked list of naming-context partitions, current Unix time, tombstone lifetime in days, output counters for removed objects and links, and an output error string.

## Control Flow

The header only declares the API. Callers provide the partition list and timing inputs; the implementation handles schema-driven search, object deletion, and expired linked-value cleanup.

## State and Persistence Behavior

The declared function mutates DSDB persistent state by deleting expired tombstones and vanished link values. Output counters are reset and populated by the implementation, and `error_string` is set on certain fatal failures.

## Dependencies and Integration Points

The header includes Samba parameter, samdb, and DSDB utility headers so the partition list and LDB types are visible. It is implemented by `garbage_collect_tombstones.c` and called from KCC maintenance and tooling.

## Risks

The signature exposes destructive behavior without an explicit transaction handle or dry-run flag. Callers must ensure `current_time`, `tombstoneLifetime`, and partition scope are correct. Output pointers must be non-NULL as the implementation writes through them immediately.

## Test Signals

Compile tests should confirm callers see the declaration. Integration tests should invoke the function with controlled partitions and validate object/link removal counters and error-string behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/garbage_collect_tombstones.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_connection.c -->
# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_connection.c

## Purpose

`kcc_connection.c` manages generated `nTDSConnection` objects for the KCC service. It finds existing inbound replication connection objects under the local NTDS Settings object, compares them with desired DSA connection entries, adds missing generated connections, and deletes obsolete ones.

## Important APIs, Types, and Functions

- `kccsrv_add_connection()` creates a new `nTDSConnection` child under the local NTDS Settings DN, names it with a random GUID, resolves the source server DN from `conn->dsa_guid`, sets required attributes, and marks `options` with `NTDSCONN_OPT_IS_GENERATED`.
- `kccsrv_delete_connection()` finds an existing connection object by `conn->obj_guid` and deletes it.
- `kccsrv_apply_connections()` reconciles an existing NTDS connection list with a desired DSA list by deleting missing entries and adding absent desired entries.
- `kccsrv_find_connections()` searches one level below local NTDS Settings for `objectClass=nTDSConnection`, extracts each connection object's GUID, resolves the `fromServer` DN to a DSA GUID, and returns a `struct kcc_connection_list`.

## Control Flow

Discovery starts at `samdb_ntds_settings_dn()` and performs an LDB one-level search for `nTDSConnection` objects with `objectGUID` and `fromServer`. Each result records the connection object's GUID and the source DSA GUID. Entries whose `fromServer` cannot be resolved are logged and skipped.

Reconciliation first iterates existing NTDS connections and deletes those whose `dsa_guid` is absent from the desired DSA list. It then iterates desired DSA connections and creates any whose `dsa_guid` is absent from the existing list. Add operations build a new child DN, resolve `fromServer`, set `objectClass`, `showInAdvancedViewOnly`, `enabledConnection`, `fromServer`, and generated `options`, then call `ldb_add()`.

## State and Persistence Behavior

The file persists additions and deletions of `nTDSConnection` objects in the configuration partition. It does not create explicit transactions around the whole reconciliation. The returned connection list is talloc-owned by the caller. The `schedule` field exists in the data type but schedule writes are commented out in add logic.

## Dependencies and Integration Points

It depends on KCC service state (`struct kccsrv_service`), samdb NTDS Settings helpers, GUID/DN resolution helpers, generated DRS constants, LDB add/delete/search, and the connection structures declared in `kcc_connection.h`.

## Risks

The file has an explicit FIXME: `kccsrv_apply_connections()` does not respect administrator-created connections whose generated option bit is not set. As written, it can delete any existing connection absent from the desired list, regardless of whether it was generated. Lack of transaction means a reconciliation can partially add/delete. Add uses random GUID names and does not populate schedule. Desired-list null handling is asymmetric: deletion assumes `dsa_list` is non-NULL.

## Test Signals

Tests should cover discovery with valid and invalid `fromServer`, add attribute content and generated option, delete by object GUID, no-op when lists match, delete obsolete generated connections, add missing desired connections, behavior when existing list is NULL, and the admin-created connection risk once fixed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_connection.h -->
# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_connection.h

## Purpose

`kcc_connection.h` defines lightweight connection records and lists used by KCC connection reconciliation.

## Important APIs, Types, and Functions

- `struct kcc_connection` contains the connection object's GUID (`obj_guid`), source DSA GUID (`dsa_guid`), invocation ID, and an 84-byte schedule buffer.
- `struct kcc_connection_list` contains a count and dynamically allocated array of `struct kcc_connection`.

No functions are declared in this header; functions are implemented in `kcc_connection.c` and made visible through other local prototype generation.

## Control Flow

The header does not implement control flow. Its structures are populated by `kccsrv_find_connections()` and consumed by `kccsrv_apply_connections()`.

## State and Persistence Behavior

The structures are in-memory projections of persisted `nTDSConnection` objects or desired topology state. `obj_guid` identifies existing connection objects; `dsa_guid` identifies source DSAs used for matching. The `schedule` field is currently not persisted by the add path in this subset.

## Dependencies and Integration Points

It relies on `struct GUID` being available from including compilation units. It is included by KCC service code that computes and applies topology.

## Risks

The header does not record whether a connection is generated or administrator-created, which contributes to the reconciliation risk noted in `kcc_connection.c`. Future fixes may need to extend this structure with option flags or provenance.

## Test Signals

Tests should indirectly validate structure use through connection discovery and reconciliation. Static analysis should ensure callers initialize all fields they compare or persist.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_connection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_drs_replica_info.c -->
# sources/user-network-fs/samba/source4/dsdb/kcc/kcc_drs_replica_info.c

## Purpose

`kcc_drs_replica_info.c` implements the KCC IRPC handler for `DsReplicaGetInfo`. It builds responses for selected DRS replication information types: inbound neighbors, outbound repsTo neighbors, up-to-date cursors, pending operations, and object metadata version 2. Many other info types are explicitly not supported.

## Important APIs, Types, and Functions

- `get_linked_attribute_value_stamp()` reads extended metadata (`RMD_VERSION`, `RMD_CHANGETIME`, `RMD_ORIGINATING_USN`) for a linked attribute value.
- `get_repl_prop_metadata_ctr()` reads and NDR-decodes `replPropertyMetaData`.
- `get_dn_from_invocation_id()` finds an `nTDSDSA` DN by `invocationId`.
- `kccdrs_replica_get_info_obj_metadata2()` returns per-attribute metadata, with optional linked-attribute stamp improvement for active forward links.
- `kccdrs_replica_get_info_cursors()` and `kccdrs_replica_get_info_cursors2()` load up-to-date vectors via `dsdb_load_udv_v1()` and `dsdb_load_udv_v2()`.
- `kccdrs_replica_get_info_pending_ops()` returns a timestamped empty pending-ops list.
- `get_master_ncs()` and `get_ncs_list()` build naming-context lists from `msDS-hasMasterNCs`/`hasPartialReplicaNCs` or a requested object DN.
- `copy_repsfrom_1_to_2()` converts version 1 reps blobs into version 2 shape.
- `fill_neighbor_from_repsFrom()` and `fill_neighbor_from_repsTo()` populate `drsuapi_DsReplicaNeighbour` records.
- `kccdrs_replica_get_info_neighbours()` and `kccdrs_replica_get_info_repsto()` enumerate `repsFrom` and `repsTo` blobs.
- `kccdrs_replica_get_info()` validates request level, dispatches by info type, fills the output info type/result, and returns `NT_STATUS_OK` for IRPC transport.

## Control Flow

The handler accepts request levels `DRSUAPI_DS_REPLICA_GET_INFO` and `DRSUAPI_DS_REPLICA_GET_INFO2`. Level 1 starts at base index zero; level 2 honors `enumeration_context` and returns `WERR_NO_MORE_ITEMS` for `0xffffffff`. It chooses `info_type`, optional object DN, source DSA GUID, and base index, then dispatches.

Neighbor enumeration builds an NC list. If an object DN is supplied, it uses only that DN. Otherwise, it searches the local nTDSDSA object by service `ntds_guid` and reads hosted master/partial NC attributes. For each NC, it loads `repsFrom` or `repsTo`, normalizes version 1 to version 2 if needed, filters inbound neighbors by requested source DSA GUID when provided, applies base-index pagination, and appends populated neighbor records. Neighbor population resolves source DSA and transport GUIDs to DNs, fills NC GUIDs, high-watermarks, attempt/success timestamps, result codes, and failure counts.

Object metadata reads `replPropertyMetaData`, maps attribute IDs to schema names, optionally improves forward-link metadata using link value stamps for level 2 requests with active linked-attribute flags, applies base index, resolves originating invocation IDs to DSA DNs, and fills `DsReplicaObjMetaData2` entries.

Cursor responses validate the DN and load UDV v1/v2. Pending ops reports no pending operations with the current timestamp.

## State and Persistence Behavior

The file is read-only. It exposes replication state persisted in `replPropertyMetaData`, up-to-date vectors, hosted NC attributes, `repsFrom`, `repsTo`, object GUIDs, invocation IDs, and extended linked-value metadata. It allocates response structures on a request memory context and stores only the WERROR in the outgoing IRPC result.

## Dependencies and Integration Points

It integrates with KCC service private data, DRSUAPI generated types, DSDB replication metadata helpers, schema lookup, GUID/DN resolution, reps blob loaders, UDV loaders, and IRPC. It is part of the KCC service's DRS management surface.

## Risks

Several paths log at level 0 and return generic internal errors, which can be noisy or opaque. `get_linked_attribute_value_stamp()` appears to write `RMD_ORIGINATING_USN` into `attr_version` rather than `attr_orig_usn`, which would lose the actual originating USN in improved metadata; this deserves focused review. Object metadata indexing uses `attr = &array[j]` while looping `i`, so skipped/base-index logic should be checked carefully for off-by-one behavior. Many info types are unsupported, which may affect interoperability. DN construction from caller-supplied object strings must rely on LDB validation paths.

## Test Signals

Tests should cover both request levels, enumeration context handling, unsupported info types, inbound/outbound neighbor enumeration with version 1 and version 2 reps blobs, source GUID filtering, base-index pagination, missing source/transport DN resolution, UDV v1/v2 success and bad NC errors, empty pending ops, object metadata for normal and linked attributes, invocation-ID-to-DN failures, malformed `replPropertyMetaData`, and the suspected `RMD_ORIGINATING_USN` assignment bug.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/dsdb/kcc/kcc_drs_replica_info.c -->
