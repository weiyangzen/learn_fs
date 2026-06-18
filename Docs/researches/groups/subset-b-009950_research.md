# subset-b-009950 research

This grouped report covers the requested Samba scripting, development helper, provision fixture, and selftest files. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_dnsupdate -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_dnsupdate

Purpose: updates the AD DC DNS records listed in `dns_update_list`, using GSS-TSIG `nsupdate`, RPC `samba-tool dns`, or RODC netlogon calls depending on credentials, options, and server role.

Important APIs/types/functions: `dnsobj` parses A, AAAA, SRV, CNAME, NS, and `RPC`-prefixed records; `get_subst_vars` gathers `${DNSDOMAIN}`, `${DNSFOREST}`, `${HOSTNAME}`, `${SITE}`, GUIDs, and role conditionals from `SamDB`; `check_dns_name`, `call_nsupdate`, `call_samba_tool`, `call_rodc_update`, and `rodc_dns_update` implement lookup and update paths. It uses `DNSResolver`, dnspython, `gensec.Security`, `cmd_dns`, `winbind.winbind`, `netlogon`, and KCC site coverage helpers.

Control flow: options and loadparm are parsed, local interface IPs are split into IPv4/IPv6, the update list and cache are read under a file lock, substitutions expand template records, site-specific records are duplicated for uncovered sites, `$IP` records expand across interfaces, and DNS/cache state determines add and delete work. Credentials are obtained only when needed. Deletes run first, then adds, choosing RPC, RODC, or nsupdate per record. The cache is rebuilt atomically when expected records changed.

State and persistence behavior: persists `dns_update_cache` and optionally a test `--use-file` DNS store with `fcntl` locking and temporary-file rename. It creates and later removes a temporary Kerberos ccache and temporary nsupdate command files. Live updates mutate DNS zones through DNS protocol, Samba RPC, or netlogon.

Dependencies and integration points: invoked from Samba AD DC maintenance and installed by the scripting build. It integrates with private `krb5.conf`, `dns_update_list`, `dns_update_cache`, interface configuration, `smb.conf`, internal DNS or BIND DNS, winbind IRPC, and KCC uncovered-site logic.

Risks: DNS update behavior is sensitive to resolver configuration, Kerberos ticket acquisition, stale SOA/NS records, and mixed forest/domain zone layouts. The `--use-file` delete path reparses raw lines and can fail on unexpected entries. RODC mapping only covers selected netlogon DNS names. Failed updates accumulate in `error_count`, so partial DNS state is possible without `--fail-immediately`.

Test signals: selftest can exercise `--use-file`, socket-wrapper environments, DNS update lists, RODC paths, and cache rebuilds. Operational signals are verbose "need update/delete", nsupdate exit codes, samba-tool errors, netlogon status, and rebuilt cache content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_dnsupdate -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_downgrade_db -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_downgrade_db

Purpose: downgrades a Samba AD database from newer LDB storage/index formats to formats older Samba releases can read.

Important APIs/types/functions: command option `-H/--URL`; raw `ldb.Ldb` with `modules:` disabled; `SamDB`; `dbcheck.reindex_database`; `ldb.PACKING_FORMAT` and `PACKING_FORMAT_V2`; `@PARTITION` and `@INDEXLIST` metadata.

Control flow: the script opens `sam.ldb` or the supplied URL without creating it, reads `@PARTITION`, and branches on `backendStore`. LMDB (`mdb`) is reopened with `pack_format_override` and committed to rewrite pack-format metadata. TDB-style stores disable `dsdb:guid index`, replace `@IDXGUID` and `@IDX_DN_GUID` on the main DB and partition databases, then reopen through the full Samba stack and trigger reindexing.

State and persistence behavior: directly modifies database metadata and partition indexes in transactions. It does not create backups. A later Samba 4.8+ or 4.11+ tool can re-upgrade the database automatically, as noted by the script output.

Dependencies and integration points: depends on Samba loadparm, LDB internals, partition layout under the private directory, and `dbchecker`. It is an administrative migration utility for offline or carefully controlled AD DB compatibility work.

Risks: destructive format changes occur in-place. Missing backups, unexpected partition paths, or running services can leave a difficult recovery situation. LMDB handling only downgrades pack format because GUID index removal is not safe with long DNs.

Test signals: successful transaction commits, printed downgrade messages, and a subsequent `dbcheck` reindex are the main signals. Compatibility should be validated by opening the DB with the target older Samba version.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_downgrade_db -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_kcc -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_kcc

Purpose: command-line entry point for the Samba Knowledge Consistency Checker, computing and optionally applying AD replication topology.

Important APIs/types/functions: `KCC`, `test_all_reps_from`, `verify_and_dot`, `list_verify_tests`, `GraphError`, and options such as `--readonly`, `--verify`, `--dot-file-dir`, `--importldif`, `--exportldif`, `--forced-local-dsa`, `--test-all-reps-from`, and link-forgetting flags.

Control flow: options configure logging, deterministic randomness, time override, credentials, and DB URL. Export exits after dumping topology LDIF. Import creates a temporary DB from LDIF and refuses to clobber an existing temp DB. The main path loads samdb, optionally lists valid DSAs or runs `test_all_reps_from`, and then calls `kcc.run` with topology mutation or read-only calculation.

State and persistence behavior: normal runs can write NTDS connection/topology changes to samdb unless `--readonly` is set. Import mode creates a temporary schemaless DB. Dot output writes Graphviz files. The test-all path repeatedly reconstructs KCC state for each DSA.

Dependencies and integration points: integrates with `samba.kcc`, graph verification, credentials, live DSA connection tests, LDIF import/export helpers, and AD replication metadata in samdb.

Risks: non-readonly runs alter replication topology. `--attempt-live-connections` adds network dependency. Import temp DB protection avoids accidental overwrite, but DB URL/import combinations are rejected only by option checks. Time and random seed options can change topology decisions.

Test signals: graph verifier errors, generated dot graphs, exit codes from `kcc.run`, listed verify tests, and read-only output are direct signals. `--test-all-reps-from` is useful for broad topology consistency validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_kcc -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_spnupdate -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_spnupdate

Purpose: ensures the local DC computer object has all service principal names from `spn_update_list`.

Important APIs/types/functions: `get_subst_vars`, local `local_update`, RODC `call_rodc_update`, `SamDB`, `secrets.ldb` credential lookup for `SAMDB Credentials`, `drsuapi.DsWriteAccountSpn`, and `samba.substitute_var`.

Control flow: the script loads credentials and tries to open `secrets.ldb` for stored SAMDB credentials, then opens samdb. It builds substitution values, checks whether this DC hosts DomainDnsZones and ForestDnsZones, filters SPN templates accordingly, expands SPNs, searches the DC computer object, computes case-insensitive missing SPNs, and exits if none are needed. RWDCs modify `servicePrincipalName` locally; RODCs find a writable DC and issue a DRS `DsWriteAccountSpn` add request.

State and persistence behavior: mutates the local samdb computer object on RWDCs. On RODCs, changes are sent to a writable DC over sealed DRS. It reads but does not change `spn_update_list` or `secrets.ldb`.

Dependencies and integration points: integrates with Samba AD provisioning, machine credentials, DNS application partition ownership, NetLogon DC discovery, and DRSUAPI.

Risks: missing or wrong `SAMDB Credentials` can prevent local DB access. RODC update filters one DRS replication GUID SPN for unclear protocol reasons. The ForestDnsZones ownership check compares against the domain base DN in this version, which is a subtle source of skipped forest DNS SPNs if naming contexts differ.

Test signals: verbose old/new SPN lists, successful local LDB modify, and DRS `WERR_OK` status are main signals. RODC tests should verify writable DC discovery and replication of added SPNs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_spnupdate -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_upgradedns -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_upgradedns

Purpose: upgrades an older Samba DNS provision to AD-integrated DNS using either `SAMBA_INTERNAL` or `BIND9_DLZ`, optionally migrating records from a flat BIND zone file.

Important APIs/types/functions: `find_bind_gid`, `convert_dns_rdata`, `import_zone_data`, cleanup helpers, `create_dns_partitions`, `fill_dns_data_partitions`, `add_dns_accounts`, `secretsdb_setup_dns`, `create_samdb_copy`, `create_named_conf`, `create_named_txt`, and DNS record classes such as `ARecord`, `SRVRecord`, and `SOARecord`.

Control flow: the command parses `--dns-backend` and `--migrate`, loads provision parameters and LDB handles, validates domain functional level, ensures `DnsAdmins`, optionally parses an existing zone and serial, creates DNS application partitions if missing, fills them automatically or imports zone records, marks the local NTDS DSA as hosting DNS naming contexts, and performs backend-specific setup. BIND9_DLZ creates or repairs dns-HOSTNAME credentials, bind DNS directory contents, keytab links, a SAM DB copy, and configuration files. SAMBA_INTERNAL removes BIND-facing sensitive files/accounts and restores private directory permissions.

State and persistence behavior: mutates samdb, secrets.ldb, DNS application partitions, NTDS naming context attributes, bind DNS directories, keytabs, named configuration files, and old DNS file trees. Cleanup removes obsolete DNS artifacts.

Dependencies and integration points: depends on dnspython zone parsing, Samba provisioning helpers, security SID/NDR packing, system `bind` or `named` group lookup, `smb.conf` server services, BIND DLZ module conventions, and internal DNS service configuration.

Risks: zone migration supports common RR types only; unsupported records are logged and ignored. File cleanup can remove BIND artifacts when switching to internal DNS. Missing IPv4 addresses abort partition creation. Existing partial DNS partitions or backend directories require careful idempotency.

Test signals: logger messages for account creation, partition creation, record import, backend file creation, and final server-services warnings. Post-upgrade tests should query DNS partitions and validate BIND/internal DNS startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_upgradedns -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_upgradeprovision -->
# sources/user-network-fs/samba/source4/scripting/bin/samba_upgradeprovision

Purpose: legacy Samba AD provision upgrader that compares the current provision against a freshly generated reference provision, backs up state, and updates databases, schema-related objects, secrets, passwords, DNS support files, GPO metadata, and security descriptors.

Important APIs/types/functions: global copy filters `attrNotCopied`, overwrite policy `hashOverwrittenAtt`, link/backlink tracking, `check_for_DNS`, `populate_links`, `populateNotReplicated`, `populate_dnsyntax`, `sanitychecks`, `handle_special_case`, `add_missing_object`, `add_missing_entries`, `handle_links`, `checkKeepAttributeWithMetadata`, `update_present`, `reload_full_schema`, `update_partition`, `rebuild_sd`, `backup_provision`, `sync_calculated_attributes`, and helpers imported from `samba.upgradehelpers`.

Control flow: after parsing debug/full/backup/very-old flags, the script gets current paths and LDB handles, creates a backup under the private directory, starts grouped transactions, derives provision names and previous provision USN ranges, sanity-checks for a single DC, creates a reference provision in a temp directory, opens its LDBs, loads schema/link metadata, updates base samdb metadata, prepares a schema reload closure, optionally performs full partition update, updates secrets and machine/DNS account passwords, recalculates security descriptors when needed, updates OEM/provision USN/GPO/policy IDs, commits both DB sets, reopens samdb to trigger reindexing, and deletes the reference provision. Exceptions leave the backup and exit nonzero.

State and persistence behavior: creates a full database/sysvol backup, a temporary reference provision, and many transactional DB changes. It can copy TDB/LMDB partition files, move old partition files into `sam.ldb.d`, modify samdb objects and descriptors, update secrets.ldb, change account passwords, create DNS config templates, update GPOs, and write provision USN ranges.

Dependencies and integration points: deeply integrated with Samba provisioning internals, schema loading, LDB transactions, NDR security descriptors, DRS replication metadata, xattr-preserving sysvol copies, TDB/MDB copy utilities, DNS provisioning files, and GPO update helpers.

Risks: this is high-impact operational migration code with many version-specific special cases. Incorrect USN range detection can overwrite administrator changes or skip needed updates. The single-DC sanity check prevents unsupported multi-DC upgrades. Rollback relies on the backup directory rather than automatic restore. Some legacy branches are only useful for very old alpha provisions.

Test signals: successful grouped commits, "Upgrade finished", backup presence on failure, reindex reopen success, and debug categories for object changes and security descriptors. Strong tests require fixture provisions from multiple historical releases and validation that schema, secrets, DNS, GPO, and SD state match expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba_upgradeprovision -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/setup_dns.sh -->
# sources/user-network-fs/samba/source4/scripting/bin/setup_dns.sh

Purpose: example helper for setting DNS records after vampiring a domain.

Important APIs/types/functions: shell variables `HOSTNAME`, `DOMAIN`, `IP`, `PRIVATEDIR`, `OBJECTGUID`; tools `samba-tool testparm`, `ldbsearch`, `kinit` or `samba4kinit`, `nsupdate-gss`, `rndc`, and `host`.

Control flow: validates three arguments, uppercases host/domain, derives the DN suffix, discovers private dir when not supplied, looks up the NTDS Settings objectGUID, performs keytab kinit as the machine account, adds the host A record and NTDS GUID CNAME using `nsupdate-gss`, flushes BIND, and checks both names.

State and persistence behavior: writes DNS records to the configured DNS server and uses Kerberos credentials from `secrets.keytab`. It does not edit local DB files directly.

Dependencies and integration points: expects Samba build-tree tools, a matching `PRIVATEDIR`, BIND `rndc`, Kerberos keytab, and the legacy `nsupdate-gss` helper.

Risks: command substitutions are lightly quoted and assume default site paths. It hardcodes `Default-First-Site-Name` and old update tooling. Failure leaves partial DNS state if A succeeds and CNAME fails.

Test signals: visible `host` lookups after `rndc flush` confirm records; failed kinit or nsupdate returns nonzero.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/setup_dns.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/subunitrun -->
# sources/user-network-fs/samba/source4/scripting/bin/subunitrun

Purpose: deprecated wrapper for running Samba Python tests through the Samba subunit test runner while still accepting Samba-specific credentials and loadparm options.

Important APIs/types/functions: `SubunitOptions`, `TestProgram`, `CredentialsOptions`, `SambaOptions`, and `samba.tests.cmdline_credentials`.

Control flow: sets SIGINT to default, prepends `bin/python`, parses test, credential, Samba, and subunit options, initializes command-line credentials unless listing tests, injects `--load-list` into runner args when supplied, and dispatches `TestProgram`.

State and persistence behavior: no persistent state. It stores credentials in the in-process `samba.tests` module for tests.

Dependencies and integration points: integrates test modules under `python/samba/tests`, subunit output, and older blackbox/selftest invocations that pass credentials to this wrapper.

Risks: deprecated behavior can diverge from `python -m samba.subunit.run`. Tests depending on global credentials can hide fixture coupling.

Test signals: subunit output, list-tests output, and successful import/execution of named test modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/subunitrun -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/wscript_build -->
# sources/user-network-fs/samba/source4/scripting/bin/wscript_build

Purpose: Waf build snippet that registers Samba scripting binaries for installation from `source4/scripting/bin`.

Important APIs/types/functions: `bld.CONFIG_SET`, `bld.SAMBA_SCRIPT`, and build conditionals `AD_DC_BUILD_IS_ENABLED` and `HAVE_ADS`.

Control flow: AD DC builds install DNS/SPN/KCC/provision/downgrade scripts plus `gen_output.py`. ADS builds install `samba-tool`. `samba-gpupdate` is always registered.

State and persistence behavior: affects build metadata and install outputs, not runtime state.

Dependencies and integration points: consumed by the top-level `source4/scripting/wscript_build`, which recurses into `bin`.

Risks: conditional omissions can remove admin tools from builds lacking AD DC or ADS support. Script names must match files.

Test signals: Waf configure/build logs and installed script presence under expected bindir/sbindir.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/addlotscontacts -->
# sources/user-network-fs/samba/source4/scripting/devel/addlotscontacts

Purpose: development/load helper that bulk-creates contact objects under `OU=Contacts` in the local provision.

Important APIs/types/functions: `get_paths`, `get_ldbs`, `find_provision_key_parameters`, LDB `Message`, `MessageElement`, and transaction helpers.

Control flow: parses an optional contact count defaulting to 10000, opens local provision DBs without Kerberos, creates `OU=Contacts` if missing, loops adding `CN=contactN` objects, prints progress every tenth chunk or 5000 items, and commits the grouped transaction.

State and persistence behavior: mutates samdb by adding an OU and many `contact` objects.

Dependencies and integration points: intended for local Samba AD performance or scale testing, using the configured private provision.

Risks: large default object count can bloat a development DB. No cleanup path is provided. `increment = num_contacts / 10` is floating-point on Python 3, so modulo checks are unusual but still compare to a numeric value.

Test signals: object count under `OU=Contacts`, progress prints, and grouped transaction commit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/addlotscontacts -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/chgkrbtgtpass -->
# sources/user-network-fs/samba/source4/scripting/devel/chgkrbtgtpass

Purpose: development utility to regenerate/update the local `krbtgt` account password in a Samba provision.

Important APIs/types/functions: `get_paths`, `get_ldbs`, `system_session`, `update_krbtgt_account_password`, and credentials forced to `DONT_USE_KERBEROS`.

Control flow: parses Samba and credential options, opens local provision LDBs, starts transactions, calls `update_krbtgt_account_password`, and commits.

State and persistence behavior: mutates samdb secrets for the Kerberos ticket-granting account and commits the change transactionally.

Dependencies and integration points: uses Samba upgrade helper password update logic. It is useful during provision repair or testing Kerberos key rollover behavior.

Risks: changing `krbtgt` can invalidate Kerberos behavior if not replicated or coordinated. No confirmation or backup is built in.

Test signals: successful transaction commit and subsequent Kerberos authentication/key version behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/chgkrbtgtpass -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/chgtdcpass -->
# sources/user-network-fs/samba/source4/scripting/devel/chgtdcpass

Purpose: development utility to update the local DC machine account password in samdb and secrets.ldb.

Important APIs/types/functions: `find_provision_key_parameters`, `update_machine_account_password`, `get_paths`, `get_ldbs`, and grouped transactions.

Control flow: parses options, opens provision LDBs, derives provision names/SIDs/realm data, calls the helper that updates the machine account password, and commits.

State and persistence behavior: mutates samdb and secrets.ldb credentials for the DC machine account.

Dependencies and integration points: integrates with Samba upgrade helper password logic and local provision paths.

Risks: uncoordinated machine-password changes can break DC authentication or replication. No automatic rollback beyond LDB transaction failure exists.

Test signals: successful commit and working machine-account Kerberos/NetLogon authentication afterward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/chgtdcpass -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/config_base -->
# sources/user-network-fs/samba/source4/scripting/devel/config_base

Purpose: prints a set of `--configfile` and `--option` arguments for running Samba tools under an alternate prefix.

Important APIs/types/functions: static `vars` mapping for ncalrpc, private, lock, pid, winbind socket, and ntp signd directories.

Control flow: requires one base directory, ensures `<base>/etc/smb.conf` exists, substitutes `${PREFIX}` into all options, and prints a single command-line fragment.

State and persistence behavior: creates the config directory and an empty `smb.conf` if missing. It does not modify Samba databases.

Dependencies and integration points: used by developers to call `samba-tool` and related commands against isolated prefixes.

Risks: option names are generated by removing spaces, which matches Samba long option style but is easy to misuse elsewhere. The script prints shell text rather than structured data.

Test signals: created config file and successful use of printed options with Samba commands.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/config_base -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/crackname -->
# sources/user-network-fs/samba/source4/scripting/devel/crackname

Purpose: DRSUAPI development client for exercising `DsCrackNames` against a server.

Important APIs/types/functions: local `do_DsBind`, `drsuapi.drsuapi`, `DsNameRequest1`, name format options, and `misc.GUID`.

Control flow: parses server, credentials, input name, input format, and output format. It refuses anonymous/no-server use, binds to `ncacn_ip_tcp:<server>[seal,print]`, sends one name in `DsCrackNames`, and prints status, result name, and DNS domain.

State and persistence behavior: read-only RPC call with no local persistence.

Dependencies and integration points: integrates with Samba DRS client bindings and is useful for plugfest or replication-debug testing.

Risks: hardcoded default name is a GUID; callers must know DRS name format constants. It assumes sealed TCP DRS is available.

Test signals: returned count/status/result fields from `DsCrackNames`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/crackname -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/demodirsync.py -->
# sources/user-network-fs/samba/source4/scripting/devel/demodirsync.py

Purpose: demonstration and diagnostic client for LDAP DirSync controls and cookies against a Samba/AD LDAP server.

Important APIs/types/functions: `printdirsync`, `Ldb("ldap://host:389")`, `searchex`, `drsblobs.ldapControlDirSyncCookie`, `ndr_pack`, `ndr_unpack`, `base64`, and `misc.GUID`.

Control flow: requires `--host`, opens remote LDAP, performs an initial DirSync search to discover server invocation GUID, then performs multiple searches with no cookie, saved cookie, modified GUIDs, and modified high-watermarks. It prints continuation status, GUID, highest USN fields, extra cursor USN, and entry counts.

State and persistence behavior: read-only LDAP queries. Cookie objects are mutated in memory to exercise edge cases.

Dependencies and integration points: integrates LDAP DirSync control parsing with DRS blob structures and Samba LDB remote connections.

Risks: Python 2 shebang style and byte/string assumptions can be fragile on modern Python. It is a demo script, not a stable test harness, and intentionally tampers with cookies.

Test signals: printed cookie high-watermark transitions and returned entry counts indicate server DirSync behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/demodirsync.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/revampire_ad.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/drs/revampire_ad.sh

Purpose: development shell workflow to re-vampire an AD domain, repair DNS zone templates, and apply FSMO LDIF substitutions.

Important APIs/types/functions: sourced `vars`, `vampire_ad.sh`, `ldbsearch`, zone template copying, `sed`, `rndc reconfig`, and `ldbmodify`.

Control flow: sources environment variables, runs the vampire join script, reads the local NTDS objectGUID, copies and patches DNS zone and named configuration templates, reconfigures BIND, creates a temporary FSMO LDIF from template substitutions, applies it to sam.ldb, and removes the temp file.

State and persistence behavior: mutates local provision files, DNS zone files, named configuration, and sam.ldb FSMO-related records.

Dependencies and integration points: depends on adjacent DRS test templates and `vars`, Samba build-tree tools, sudo, and BIND `rndc`.

Risks: heavily environment-specific and uses `set -x` with potentially sensitive variables. Direct `sudo ldbmodify` and template substitutions can damage a test provision if variables are wrong.

Test signals: successful vampire script, patched zone/named files, `rndc reconfig`, and successful `ldbmodify`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/revampire_ad.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/unvampire_ad.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/drs/unvampire_ad.sh

Purpose: development cleanup helper that removes a vampired DC from a remote AD and deletes local private LDBs.

Important APIs/types/functions: sourced `vars`, `ldbdel -r`, remote LDAP URLs, administrator credentials, and `PREFIX/private/*.ldb` removal.

Control flow: sets default site if needed, deletes the machine from `CN=Computers`, `OU=Domain Controllers`, and the site server container on the remote server, then removes local `.ldb` files.

State and persistence behavior: deletes remote AD objects recursively and removes local provision database files.

Dependencies and integration points: coupled to the DRS development `vars` file and test AD topology.

Risks: destructive and credential-bearing. Wrong `server`, `machine`, `dn`, or `PREFIX` values can delete unintended objects or local databases.

Test signals: successful `ldbdel` commands and absent local `.ldb` files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/unvampire_ad.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/vampire_ad.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/drs/vampire_ad.sh

Purpose: development workflow to join a Samba DC to an AD domain using vampire/domain-join style setup.

Important APIs/types/functions: sourced `vars`, BIND named template substitution, `rndc reconfig`, `unvampire_ad.sh`, `kinit`, `nsupdate`, and `samba-tool domain join`.

Control flow: creates a named.conf from template, reconfigures BIND, runs cleanup, deletes an existing A record via GSS `nsupdate`, derives uppercase realm, and runs `samba-tool domain join ... DC` with forced ADS function-level options. Old `setup_dns.sh` calls are left commented.

State and persistence behavior: writes named.conf, changes BIND state, deletes DNS records, and creates/updates a local Samba DC provision through domain join.

Dependencies and integration points: depends on DRS test environment variables, administrator password, BIND, Kerberos, and `samba-tool`.

Risks: destructive cleanup runs before join. Password is piped to `kinit` and also appears in command arguments. Hardcoded function-level options target old AD compatibility scenarios.

Test signals: successful `samba-tool domain join`, BIND reconfig, and DNS update completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/vampire_ad.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/enumprivs -->
# sources/user-network-fs/samba/source4/scripting/devel/enumprivs

Purpose: small LSA RPC diagnostic that enumerates privileges on a server and prints display names.

Important APIs/types/functions: `get_display_name`, `lsa.lsarpc`, `OpenPolicy2`, `EnumPrivs`, `LookupPrivDisplayName`, and `security.SEC_FLAG_MAXIMUM_ALLOWED`.

Control flow: parses one server and credentials, refuses unauthenticated use, connects over `ncacn_np:<server>[print]`, opens an LSA policy handle, enumerates up to 100 privileges, looks up each display name, and prints LUID/name/display text.

State and persistence behavior: read-only RPC calls, no persistence.

Dependencies and integration points: Samba DCE/RPC LSA bindings and credential parser.

Risks: Python statement `''.decode('utf-8')` is invalid on Python 3 strings, so this historical script may require compatibility fixes. The 100 privilege cap is static.

Test signals: printed privilege rows with LUIDs and display strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/enumprivs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/getncchanges -->
# sources/user-network-fs/samba/source4/scripting/devel/getncchanges

Purpose: command-line DRS replication diagnostic for issuing `DsGetNCChanges` requests against a server.

Important APIs/types/functions: `drs_DsBind`, `DsGetNCChangesRequest8`, `drs_get_rodc_partial_attribute_set`, replica flag options, `SamDB`, `ndr_unpack(misc.GUID)`, and high-watermark update loop.

Control flow: parses server, credentials, naming context DN, extended operation, partial attribute set, iteration count, destination DSA, and replica flags. It adjusts flags for RODC or partial RW modes, connects to DRS over sealed TCP, opens remote LDAP, discovers destination DSA invocation ID if absent, builds a request8 from zero high-watermark, optionally adds the RODC PAS, calls `DsGetNCChanges` repeatedly while `more_data` is set, and feeds back the returned high-watermark.

State and persistence behavior: read-only replication pull from the target, with no local writes.

Dependencies and integration points: exercises Samba DRS server behavior, LDAP metadata discovery, and partial attribute set generation.

Risks: uses `opts.dn.decode("utf-8")`, which is Python 2-era and problematic when `opts.dn` is already `str`. Incorrect flags can ask for secret-processing or partial replicas unexpectedly. Output is minimal, so failures may need DRS tracing.

Test signals: DRS bind handle, successful iterations, `more_data` termination, and absence of RPC exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/getncchanges -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/nmfind -->
# sources/user-network-fs/samba/source4/scripting/devel/nmfind

Purpose: shell helper to find object files containing a symbol.

Important APIs/types/functions: positional `TARGET`, object-file arguments, `nm`, and `grep`.

Control flow: shifts off the target, loops over each file, runs `nm` piped to grep, and prints bracketed filenames plus matching symbol lines when found.

State and persistence behavior: read-only inspection of object files.

Dependencies and integration points: developer build debugging helper for compiled Samba objects.

Risks: unquoted `$*` and grep pattern usage can mis-handle spaces or regex metacharacters. It scans serially.

Test signals: printed object filenames and matching `nm` rows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/nmfind -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/pfm_verify.py -->
# sources/user-network-fs/samba/source4/scripting/devel/pfm_verify.py

Purpose: verifies that a server's cached DRS prefixMap and schemaInfo match the values stored in the Schema naming context.

Important APIs/types/functions: `_samdb_fetch_pfm`, `_samdb_fetch_schi`, `_drs_fetch_pfm`, `_pfm_verify`, `_pfm_schi_verify`, `DsGetNCChangesRequest8`, `drsblobs.prefixMapBlob`, `schemaInfoBlob`, and DRS mapping counters.

Control flow: parses server and credentials, falls back to `DC_SERVER`, opens LDAP SamDB, fetches prefixMap/schemaInfo over DRS with `max_object_count=0`, removes the schemaInfo pseudo mapping from the DRS mapping counter, fetches LDB-stored prefixMap/schemaInfo, compares count, prefix IDs, OID lengths/binary OIDs, marker, revision, and invocation ID, and exits 1 or 2 on mismatches.

State and persistence behavior: read-only LDAP and DRS queries.

Dependencies and integration points: combines DRS replication wire mapping data with schema NC attributes. Useful for diagnosing schema replication/cache correctness.

Risks: uses `str(res[0]['prefixMap'])` and `str(schemaInfo)` for NDR input, which can be fragile if the binding expects bytes. Assertions can abort without clean diagnostics. Hardcoded destination DSA GUID is artificial.

Test signals: zero exit means prefixMap and schemaInfo match. Exit 1 indicates prefixMap mismatch; exit 2 indicates schemaInfo mismatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/pfm_verify.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/rebuild_zone.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/rebuild_zone.sh

Purpose: rebuilds a BIND zone file for a Samba AD domain by extracting DC GUIDs and generating common AD service records.

Important APIs/types/functions: `dcname`, `getip`, `ldbsearch`, `nmblookup`, here-doc zone template, and `rndc reload`.

Control flow: requires `sam.ldb` and output zone path, reads DNS hostname, realm, NTDS DSA objectGUIDs, and domain GUID, writes SOA/NS header, appends A records for each DC, emits `_msdcs`, LDAP, GC, Kerberos, and kpasswd SRV/CNAME/A records per DC, writes a Kerberos TXT record, and reloads BIND.

State and persistence behavior: overwrites the target zone file and reloads BIND. It reads sam.ldb but does not modify it.

Dependencies and integration points: intended for old BIND flat-file DNS setups. Depends on build-tree `ldbsearch`, NetBIOS name lookup, and system `rndc`.

Risks: IP discovery falls back to `XX.XX.XX.XX`, requiring manual edits. Site name is hardcoded to `Default-First-Site-Name`. Shell variables and output path are not robustly quoted.

Test signals: generated zone file contents, successful `rndc reload`, and DNS query results for generated records.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/rebuild_zone.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/rodcdns -->
# sources/user-network-fs/samba/source4/scripting/devel/rodcdns

Purpose: diagnostic client for the netlogon RODC DNS update IRPC call.

Important APIs/types/functions: `winbind.winbind("irpc:winbind_server")`, `netlogon.NL_DNS_NAME_INFO_ARRAY`, `NL_DNS_NAME_INFO`, and `DsrUpdateReadOnlyServerDnsRecords`.

Control flow: parses weight, priority, port, netlogon DNS type, and site; builds one DNS name info request with `dns_register=True`; calls winbind netlogon with TTL 600; prints returned status.

State and persistence behavior: asks winbind/netlogon to register DNS records for an RODC. No local files are written.

Dependencies and integration points: depends on a running local winbind server and Samba netlogon IRPC implementation.

Risks: numeric record type is user-supplied and defaults to LDAP-at-site. It does not expose unregister mode or detailed returned names.

Test signals: printed status code from `DsrUpdateReadOnlyServerDnsRecords`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/rodcdns -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/speedtest.py -->
# sources/user-network-fs/samba/source4/scripting/devel/speedtest.py

Purpose: Samba Python subunit performance test for bulk user creation/deletion and ACL-filtered LDAP searches.

Important APIs/types/functions: `SpeedTest`, `SpeedTestAddDel`, `AclSearchSpeedTest`, `create_user`, `create_bundle`, `remove_bundle`, `run_bundle`, `run_search_bundle`, `SamDB`, `sd_utils.SDUtils`, `delete_force`, and `TestProgram`.

Control flow: requires a host, builds sealed credentials, opens `SamDB` with `paged_searches`, then subunit discovers test methods. Add/delete tests remove stale users and time three attempts for 10, 100, and 1000 object bundles. ACL search tests create a restricted user, add ACEs to users or container, search as admin or restricted user, average three search timings, and clean up.

State and persistence behavior: mutates the target directory by creating and deleting `speedtestuserN` and `acltestuser` objects and modifying DACLs. Cleanup is attempted through test teardown and delete helpers.

Dependencies and integration points: integrates with Samba test framework, LDB over LDAP, security descriptors, and credential/gensec sealing.

Risks: performance tests are invasive and can leave objects after interruption. The 10000-user test is disabled because it is slow. Global `ldb` is initialized after class definitions but before `TestProgram`, so import ordering matters.

Test signals: subunit test results plus printed timing averages for ADD, DEL, and SEARCH operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/speedtest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/tmpfs.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/tmpfs.sh

Purpose: developer helper that remounts build output directories `bin` and `st` as tmpfs for faster builds/tests.

Important APIs/types/functions: `sudo umount`, `rm -rf bin st`, `mount -t tmpfs`, and `chown $USER`.

Control flow: prompts through `sudo echo`, removes existing directories, unmounts stale tmpfs mounts if present, recreates directories, mounts tmpfs on each, changes ownership, and prints completion messages.

State and persistence behavior: destructively removes current `bin` and `st` contents and replaces them with volatile tmpfs mounts.

Dependencies and integration points: local developer workflow for Samba build/test directories.

Risks: data loss if `bin` or `st` contain wanted files. Requires sudo and assumes Linux tmpfs semantics.

Test signals: mounted tmpfs filesystems on `bin` and `st` and writable ownership by the current user.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/tmpfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/watch_servers.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/watch_servers.sh

Purpose: repeatedly compares LDAP search output from two servers.

Important APIs/types/functions: `watch`, `ldbsearch -S`, administrator credentials, filter pattern, and optional attributes.

Control flow: requires two DB/server URLs, password, search expression, and optional attrs; runs `watch -n1` with two `ldbsearch` commands, filtering boilerplate lines and deduplicating output with `uniq`.

State and persistence behavior: read-only polling.

Dependencies and integration points: developer replication/debug helper for comparing two Samba/AD servers.

Risks: password appears in the watch command line. Shell quoting is brittle for complex LDAP filters or attributes.

Test signals: live side-by-side terminal output showing differences or convergence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/watch_servers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/man/samba-gpupdate.8.xml -->
# sources/user-network-fs/samba/source4/scripting/man/samba-gpupdate.8.xml

Purpose: DocBook manpage source for `samba-gpupdate(8)`.

Important APIs/types/functions: DocBook `refentry`, `refmeta`, `refsynopsisdiv`, option paragraphs, and manual metadata version `4.8.0`.

Control flow: static documentation describes the command synopsis, purpose, supported options, Samba common options, credential options, version option, and author section.

State and persistence behavior: no runtime state; it is transformed into a manpage when manpage generation is enabled.

Dependencies and integration points: installed by `source4/scripting/wscript_build` through `bld.MANPAGES` when `XSLTPROC_MANPAGES` is enabled.

Risks: documented command name title uses `SAMBA_GPOUPDATE`, which differs from `samba-gpupdate`. Option text can drift from actual command implementation.

Test signals: successful DocBook/XML validation and generated `samba-gpupdate.8` content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/man/samba-gpupdate.8.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/wscript_build -->
# sources/user-network-fs/samba/source4/scripting/wscript_build

Purpose: Waf build script for installing Samba scripting tools and manpages.

Important APIs/types/functions: `MODE_755`, `bld.CONFIG_SET`, `bld.INSTALL_FILES`, `bld.MANPAGES`, and `bld.RECURSE('bin')`.

Control flow: builds an AD DC script list when AD DC support is enabled, adds `samba-gpupdate` when Python is enabled, optionally installs the manpage, installs `samba-tool` for ADS builds, and recurses into `bin`.

State and persistence behavior: affects installation outputs and permissions, not runtime state.

Dependencies and integration points: ties top-level scripting install layout to `bin/wscript_build` script registration and manpage XML.

Risks: `man_files` is assigned only in the Python-enabled branch but referenced only when `sbin_files` is non-empty and manpage generation is enabled; current flow is safe because `samba-gpupdate` is the documented manpage target. Conditional install lists must stay synchronized with actual files.

Test signals: Waf install output, executable mode `0755`, Python fixups, and generated manpage installation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/wscript_build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/krb5.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/krb5.conf

Purpose: Kerberos configuration fixture for an old `alpha13.samba.corp` provision.

Important APIs/types/functions: `[libdefaults]`, realm `ALPHA13.SAMBA.CORP`, KDC/admin server host `ares.alpha13.samba.corp`, and `[domain_realm]` mappings.

Control flow: static config directs Kerberos clients to use DNS lookup and the explicit realm host mappings.

State and persistence behavior: no code; consumed as configuration by tests or upgrade fixtures.

Dependencies and integration points: part of selftest historical provision data used by upgrade/dump tests.

Risks: hardcoded hostnames are fixture values and should not be used as live config. DNS lookup settings can mask missing explicit KDCs.

Test signals: Kerberos tools using this fixture should resolve the default realm and host mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/krb5.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/named.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/named.conf

Purpose: BIND flat-file DNS configuration fixture from an old alpha13 Samba provision.

Important APIs/types/functions: forward zone `alpha13.samba.corp.`, zone file path, `named.conf.update` include, `check-names ignore`, and commented reverse-zone example.

Control flow: static BIND include config defines a master zone with dynamic update policy included from Samba-generated content.

State and persistence behavior: no executable code; represents historical DNS configuration state.

Dependencies and integration points: used by provision upgrade tests that migrate old BIND flat-file DNS setups.

Risks: absolute paths are fixture-specific. Comments reference old BIND GSS-TSIG behavior and optional reverse-zone setup.

Test signals: upgrade fixtures can detect/migrate this file and validate generated AD DNS/BIND DLZ replacements.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/named.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/phpldapadmin-config.php -->
# sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/phpldapadmin-config.php

Purpose: phpLDAPadmin configuration fixture customized for an old Samba4 LDAP server.

Important APIs/types/functions: `$ldapservers = new LDAPServers`, `SetValue` calls for server name, LDAPI host URL, session auth type, and DN login attribute.

Control flow: static PHP config initializes one LDAP server entry pointing at the fixture private LDAPI socket path.

State and persistence behavior: no runtime mutation in the Samba tree; consumed as config by phpLDAPadmin if used.

Dependencies and integration points: part of historical provision data, useful for upgrade/dump fidelity.

Risks: absolute LDAPI path is developer-machine-specific. Legacy phpLDAPadmin API may not match current releases.

Test signals: fixture-preservation tests should confirm the file survives dump/undump or upgrade workflows when expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/alpha13/private/phpldapadmin-config.php -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/dump.sh -->
# sources/user-network-fs/samba/source4/selftest/provisions/dump.sh

Purpose: converts `.tdb` and `.ldb` files in a provision directory into `.dump` text files using `tdbdump`.

Important APIs/types/functions: arguments `<DIRECTORY> [TARGETDIR] [TDBDUMP]`, `find`, `tdbdump`, target directory creation, and source DB file removal.

Control flow: validates input, selects `tdbdump` command, changes into the provision directory, sets target directory, dumps each `.tdb` and `.ldb` file to a mirrored `.dump` path, removes the original DB file after successful dump, and exits.

State and persistence behavior: destructive conversion: original database files are removed after dump files are created.

Dependencies and integration points: paired with `undump.sh` for storing provision fixtures in dump form.

Risks: unquoted `find` loop breaks on spaces. Running against a live or valuable provision removes DB files. Errors abort after partial conversion.

Test signals: `.dump` files in the target tree and absence of original `.tdb`/`.ldb` files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/dump.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/GPT.INI.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/GPT.INI.xml

Purpose: XML-normalized Group Policy Template INI fixture for a generalized GPO backup.

Important APIs/types/functions: root `IniFile`, section `General`, parameters `Version=1179715` and `displayName=New Group Policy Object`.

Control flow: static data maps original `GPT.INI` content into Samba's XML backup representation.

State and persistence behavior: fixture only; no mutation.

Dependencies and integration points: consumed by GPO backup/restore tests that split generalized XML from concrete `.SAMBABACKUP` files.

Risks: policy version must remain synchronized with the paired backup file. XML structure is simple but order-sensitive tests may rely on parameter order.

Test signals: parser should reconstruct the General section and exact version/display name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/GPT.INI.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/Audit/audit.csv.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/Audit/audit.csv.xml

Purpose: XML-normalized audit policy CSV fixture for machine policy backup.

Important APIs/types/functions: root `CsvFile`, header row, audit subcategories `Audit Credential Validation` and `Audit Kerberos Authentication Service`, GUIDs, inclusion settings `Success`/`Failure`, setting values `1`/`2`, and generalized `user_id` entity placeholders.

Control flow: static row data represents CSV policy content with generalized security principal references.

State and persistence behavior: fixture only; no runtime state.

Dependencies and integration points: used by generalized GPO backup tests for CSV parsing, user-ID token substitution, and restore fidelity.

Risks: XML contains custom Samba entity references that generic XML parsers need a resolver or placeholder handling for. CSV column ordering is part of the fixture contract.

Test signals: backup tooling should regenerate audit CSV rows and substitute principal tokens correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/Audit/audit.csv.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/SecEdit/GptTmpl.inf.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/SecEdit/GptTmpl.inf.xml

Purpose: XML-normalized security template fixture for machine policy settings.

Important APIs/types/functions: root `GptTmplInfFile`; sections for Unicode, Version, System Access, Kerberos Policy, logs, Event Audit, Registry Values, Privilege Rights, Service General Setting, Registry Keys, File Security, and Group Membership. It includes password history, guest enablement, Kerberos max renew age, event audit, registry values, privilege user tokens, ACL token placeholders, and group membership tokens.

Control flow: static section/parameter representation of a UTF-16 `GptTmpl.inf` policy backup.

State and persistence behavior: fixture only.

Dependencies and integration points: exercises Samba GPO backup restore logic for security templates, SID/user ID generalization, registry ACLs, service settings, and group membership.

Risks: custom entity tokens and empty values require specialized XML handling. Sections with no parameters are still meaningful and must not be dropped.

Test signals: restore should recreate the original secedit template, including user/ACL substitutions and empty sections.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Microsoft/Windows NT/SecEdit/GptTmpl.inf.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Registry.pol.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Registry.pol.xml

Purpose: XML-normalized machine `Registry.pol` fixture.

Important APIs/types/functions: root `PolFile` with `signature=PReg`, `version=1`, and `num_entries=76`; `Entry` nodes with registry key, value name, type/type_name, and one or more values. It covers certificate policy hives, QoS settings, software restriction policies, DNS client policy config, and binary certificate blobs.

Control flow: static serialized representation of binary machine registry policy entries.

State and persistence behavior: fixture only.

Dependencies and integration points: used by GPO backup/restore tests for `Registry.pol` parsing, type preservation, binary/base64 value handling, and machine-policy reconstruction.

Risks: large binary values and many empty `REG_NONE` entries can be accidentally normalized away. Entry count must match actual entries.

Test signals: parser should read 76 entries, preserve type distribution, and regenerate a valid `PReg` machine policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Registry.pol.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Scripts/psscripts.ini.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Scripts/psscripts.ini.xml

Purpose: empty XML-normalized PowerShell scripts INI fixture for machine policy.

Important APIs/types/functions: root `IniFile` with no sections.

Control flow: static representation of an empty or absent machine PowerShell scripts policy file.

State and persistence behavior: fixture only.

Dependencies and integration points: ensures GPO backup/restore handles empty XML policy artifacts without dropping the file.

Risks: empty files are easy to treat as non-data, but presence can be significant for round-trip tests.

Test signals: tooling should preserve the empty `IniFile` and produce an empty corresponding scripts file if required.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Scripts/psscripts.ini.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Scripts/scripts.ini.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Scripts/scripts.ini.xml

Purpose: XML-normalized machine startup/shutdown scripts policy fixture.

Important APIs/types/functions: root `IniFile`, sections `Shutdown` and `Startup`, parameters `0CmdLine` and `0Parameters`, and generalized `network_path` entity placeholders.

Control flow: static INI representation for machine scripts, mapping commands to network paths and blank parameter values.

State and persistence behavior: fixture only.

Dependencies and integration points: tests GPO script policy backup/restore and network path generalization.

Risks: custom network path entities need Samba-specific substitution. Blank parameter values must be preserved.

Test signals: restore should recreate startup/shutdown script INI entries with substituted UNC paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/Machine/Scripts/scripts.ini.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Documents & Settings/fdeploy.ini.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Documents & Settings/fdeploy.ini.xml

Purpose: empty XML-normalized folder redirection INI fixture.

Important APIs/types/functions: root `IniFile` with no sections.

Control flow: static empty policy representation for user folder deployment settings.

State and persistence behavior: fixture only.

Dependencies and integration points: verifies generalized GPO backup logic keeps empty user policy files aligned with their source tree path, including a directory name containing spaces.

Risks: path spaces and empty XML content are both common sources of reconciliation or parser mistakes.

Test signals: file presence and empty `IniFile` round-trip behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Documents & Settings/fdeploy.ini.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Documents & Settings/fdeploy1.ini.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Documents & Settings/fdeploy1.ini.xml

Purpose: XML-normalized folder redirection fixture with two redirected folders.

Important APIs/types/functions: root `IniFile`, `version` section, `Folder_Redirection` section mapping folder GUIDs to generalized user IDs, per-folder sections keyed by `fdeploy_GUID` and `fdeploy_SID`, flags `1219`/`1211`, and generalized network paths for Pictures and Desktop.

Control flow: static folder-redirection INI representation with tokenized SIDs and UNC paths.

State and persistence behavior: fixture only.

Dependencies and integration points: exercises GPO backup/restore handling for folder redirection, user SID abstraction, network path abstraction, and directories with spaces.

Risks: XML entity tokens require custom handling. GUID section attributes and parameter keys both carry semantic identity and must be preserved.

Test signals: restore should recreate folder redirection settings for the two GUIDs and network paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Documents & Settings/fdeploy1.ini.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Registry.pol.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Registry.pol.xml

Purpose: XML-normalized user `Registry.pol` fixture.

Important APIs/types/functions: root `PolFile` with `signature=PReg`, `version=1`, and `num_entries=36`; entries for user certificate stores, trusted publisher safer settings, QoS policy, software restriction policy, and path rules with `REG_*` type names.

Control flow: static serialized representation of binary user registry policy.

State and persistence behavior: fixture only.

Dependencies and integration points: used by generalized GPO backup/restore tests for user registry policy parsing and binary/base64 value preservation.

Risks: includes a large certificate blob and many empty `REG_NONE` entries. Entry count and order may be used by round-trip tests.

Test signals: parser should read 36 entries and regenerate a valid user `Registry.pol`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Registry.pol.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Scripts/scripts.ini.xml -->
# sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Scripts/scripts.ini.xml

Purpose: XML-normalized user logon scripts policy fixture.

Important APIs/types/functions: root `IniFile`, section `Logon`, keys `0CmdLine` and `0Parameters`, and generalized `network_path` token for a netlogon batch file.

Control flow: static INI representation of one logon script command with empty parameters.

State and persistence behavior: fixture only.

Dependencies and integration points: exercises user script GPO backup/restore and UNC path generalization.

Risks: custom network path entity must be resolved by Samba tooling; empty parameter value is semantically significant.

Test signals: restored scripts.ini should contain the logon command and blank parameters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/generalized-gpo-backup/policy/{1E1DC8EA-390C-4800-B327-98B56A0AEA5D}/User/Scripts/scripts.ini.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/etc/smb.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/etc/smb.conf

Purpose: smb.conf fixture for a multi-DC Samba AD provision.

Important APIs/types/functions: `[global]` parameters `workgroup=SAMDOM`, `realm=samdom.example.com`, `netbios name=Q-0-1`, `server role=active directory domain controller`, `log level=3`, plus `netlogon` and `sysvol` shares.

Control flow: static Samba configuration consumed by tests or upgrade fixtures.

State and persistence behavior: configuration only.

Dependencies and integration points: points `netlogon` and `sysvol` at `/usr/local/samba/var/locks/sysvol`, matching the fixture layout expectations.

Risks: absolute paths are fixture-specific. Share writeability is appropriate for AD sysvol tests but not a general hardening example.

Test signals: `testparm` or provision tests should parse it and expose AD DC role plus netlogon/sysvol shares.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/etc/smb.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/private/krb5.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/private/krb5.conf

Purpose: minimal Kerberos fixture for the multi-DC `SAMDOM.EXAMPLE.COM` provision.

Important APIs/types/functions: `[libdefaults]`, `default_realm`, `dns_lookup_realm=false`, and `dns_lookup_kdc=true`.

Control flow: static Kerberos client defaults for tests.

State and persistence behavior: configuration only.

Dependencies and integration points: consumed by Samba/Kerberos commands in historical provision tests.

Risks: DNS KDC lookup means tests need suitable DNS or socket-wrapper setup.

Test signals: Kerberos tools should select `SAMDOM.EXAMPLE.COM` as default realm.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/multi-dc-samba-master-c596ac6/private/krb5.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-0-0/private/krb5.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-0-0/private/krb5.conf

Purpose: minimal Kerberos configuration fixture for a Samba 4.0.0 release provision.

Important APIs/types/functions: default realm `RELEASE-4-0-0.SAMBA.CORP`, `dns_lookup_realm=false`, and `dns_lookup_kdc=true`.

Control flow: static config used by upgrade/selftest fixtures.

State and persistence behavior: configuration only.

Dependencies and integration points: pairs with release-4-0-0 provision data for upgrade compatibility tests.

Risks: relies on DNS KDC lookup in the test environment.

Test signals: Kerberos client realm selection for release fixture tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-0-0/private/krb5.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-0rc3/private/named.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-0rc3/private/named.conf

Purpose: BIND9 DLZ named configuration fixture from a Samba 4.1.0rc3 provision.

Important APIs/types/functions: DLZ block `AD DNS Zone`, `dlopen` database line for BIND 9.8.0, commented alternative for BIND 9.9.0, and absolute module paths.

Control flow: static BIND include configuring DLZ-backed AD DNS.

State and persistence behavior: configuration fixture only.

Dependencies and integration points: used by DNS/provision upgrade tests to recognize and migrate BIND DLZ-era configuration.

Risks: absolute paths are historical and not portable. Only one database line should be active for the target BIND version.

Test signals: upgrade tooling should preserve or replace BIND DLZ config according to backend migration rules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-0rc3/private/named.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-6-partial-object/private/krb5.conf -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-6-partial-object/private/krb5.conf

Purpose: minimal Kerberos configuration fixture for a Samba 4.1.6 partial-object provision.

Important APIs/types/functions: default realm `SAMBA.EXAMPLE.COM`, `dns_lookup_realm=false`, and `dns_lookup_kdc=true`.

Control flow: static Kerberos defaults.

State and persistence behavior: configuration only.

Dependencies and integration points: accompanies the partial-object historical provision fixture.

Risks: DNS KDC lookup dependency must be provided by tests.

Test signals: Kerberos commands should use `SAMBA.EXAMPLE.COM` by default.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-1-6-partial-object/private/krb5.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/add-deleted-user.sh -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/add-deleted-user.sh

Purpose: fixture-generation helper that creates and deletes a user to capture deleted-object and deactivated-link state.

Important APIs/types/functions: `SAMBA_TOOL`, `samba-tool user/group add`, `group addmembers`, `user delete`, and `ldbsearch --show-recycled --show-deleted --show-deactivated-link --reveal`.

Control flow: targets `st/provision/simple-dc/private/sam.ldb`, creates user `fred`, creates group `swimmers`, adds membership, deletes `fred`, and greps revealed deleted/recycled output for `fred` and `swimmers`.

State and persistence behavior: mutates the simple-dc test provision and is intended to help create/update an LDB dump fixture.

Dependencies and integration points: tied to `make test TESTS="samba4.blackbox.group.py"` and simple-dc provision paths.

Risks: hardcoded DB and destination paths. It does not write the dump itself despite defining `DEST`.

Test signals: grep output showing deleted user and group link state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/add-deleted-user.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/simple-dc-steps.sh -->
# sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/simple-dc-steps.sh

Purpose: documented shell steps for reproducing simple-DC group/deleted-user fixture state.

Important APIs/types/functions: `make test TESTS=samba4.blackbox.group.py`, `samba-tool user add`, `group add`, `group addmembers`, `user delete`, and `ldbsearch` with deleted/recycled/deactivated-link controls.

Control flow: runs the group blackbox test to prepare a provision, adds user and group, shows state before deletion, deletes the user, and shows state after deletion.

State and persistence behavior: mutates `st/provision/simple-dc/private/sam.ldb`.

Dependencies and integration points: selftest fixture authoring helper for release-4-5-0-pre1 provision data.

Risks: hardcoded paths and credentials/password. Intended for manual fixture generation, not general automation.

Test signals: before/after `ldbsearch` output for `fred` and `swimmers`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/release-4-5-0-pre1/simple-dc-steps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/undump.sh -->
# sources/user-network-fs/samba/source4/selftest/provisions/undump.sh

Purpose: restores provision `.dump` files back to `.tdb` or `.ldb` database files using `tdbrestore`.

Important APIs/types/functions: arguments `<DIRECTORY> [TARGETDIR] [TDBRESTORE]`, `find`, `tdbrestore`, target directory creation, and output replacement.

Control flow: validates input, selects restore command, changes into dump directory, sets target dir, loops over `.dump` files, derives output filename by removing `.dump`, removes existing output, restores from dump content, and exits.

State and persistence behavior: creates/restores DB files in the target tree and removes any existing output file before restore.

Dependencies and integration points: paired with `dump.sh` for checked-in provision fixtures.

Risks: unquoted loop breaks on paths with spaces. Existing DB files are removed before restore. Partial restores can leave mixed state after failure.

Test signals: restored `.tdb`/`.ldb` files and successful `tdbrestore` exit codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/provisions/undump.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_samba3dump.sh -->
# sources/user-network-fs/samba/source4/selftest/test_samba3dump.sh

Purpose: blackbox selftest wrapper verifying that `samba3dump` completes on bundled Samba3 test data.

Important APIs/types/functions: `testprogs/blackbox/subunit.sh`, `subunit_start_test`, `subunit_pass_test`, `subunit_fail_test`, `$PYTHON`, and `source4/scripting/bin/samba3dump`.

Control flow: starts a subunit test named `samba3dump`, computes source root, runs `samba3dump` against `testdata/samba3`, and reports pass/fail through subunit helpers.

State and persistence behavior: no expected persistent writes beyond tool behavior/output.

Dependencies and integration points: part of Samba selftest blackbox scripts and validates the Samba3 dump conversion script.

Risks: only checks command success, not dump content correctness.

Test signals: subunit pass or fail for `samba3dump`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_samba3dump.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_w2k3.sh -->
# sources/user-network-fs/samba/source4/selftest/test_w2k3.sh

Purpose: runs a curated set of RPC torture tests expected to pass against a Windows Server 2003 DC.

Important APIs/types/functions: `test_functions.sh`, `testit`, `smbtorture`, transport lists for `ncacn_np` and `ncacn_ip_tcp`, bind options such as `padcheck`, `sign`, `seal`, `bigendian`, and RPC test names.

Control flow: validates server, username, password, domain, and realm arguments, builds authentication options, runs a spoolss named-pipe test, then loops bind options, transports, and RPC test lists, finally running DRSUAPI over sealed TCP in normal and big-endian modes.

State and persistence behavior: remote RPC tests may create temporary server state depending on smbtorture subtests; the script itself writes no files.

Dependencies and integration points: used for interoperability testing against a real W2K3 DC with administrator credentials.

Risks: requires live Windows infrastructure and credentials. Some smbtorture tests may be invasive. Argument shift expects five values after only checking at least four, so missing realm can behave poorly.

Test signals: `testit` subunit results for each RPC/transport/bind-option combination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_w2k3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_w2k3_file.sh -->
# sources/user-network-fs/samba/source4/selftest/test_w2k3_file.sh

Purpose: runs SMB file-serving torture tests expected to pass against Windows Server 2003.

Important APIs/types/functions: `test_functions.sh`, `testit`, `smbtorture`, UNC target, username/password, `TORTURE_OPTIONS`, and a curated `tests` list.

Control flow: validates UNC, username, and password, shifts optional args, declares expected-failing tests for visibility, and loops through base/raw SMB tests invoking `smbtorture` with credentials.

State and persistence behavior: remote file-serving torture tests can create/delete files on the target share; the script itself writes no local state.

Dependencies and integration points: interoperability/selftest helper for Windows file server behavior baselines.

Risks: `start` argument is captured but unused. Requires a prepared writable UNC and credentials. Known failing tests are printed but not dynamically filtered from the active list if later added.

Test signals: `testit` subunit results per SMB torture test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_w2k3_file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_win.sh -->
# sources/user-network-fs/samba/source4/selftest/test_win.sh

Purpose: orchestrates Windows 2003 VM interoperability tests through the `wintest` harness.

Important APIs/types/functions: `selftest/test_functions.sh`, `vm_get_ip.pl`, `restore_snapshot`, `testit`, `wintest_base.sh`, `wintest_raw.sh`, `wintest_rpc.sh`, `wintest_net.sh`, `wintest_client.sh`, and `wintest_2k3_dc.sh`.

Control flow: obtains the remote Windows VM IP from `VM_CFG_PATH`, restores the snapshot and exits if missing, then runs BASE, RAW, RPC, NET, Windows-client-against-Samba, and selected DC RPC tests with environment-provided credentials.

State and persistence behavior: external VM tests may mutate the Windows guest and Samba test environment; snapshot restore handles the initial IP failure path only.

Dependencies and integration points: requires `WINTEST_DIR`, VM configuration, credentials/workgroup environment variables, and the wintest scripts.

Risks: highly environment-specific and dependent on a working VM controller. Failure paths outside initial IP discovery do not automatically restore snapshots in this wrapper.

Test signals: `testit` subunit results for each wintest phase.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/selftest/test_win.sh -->
