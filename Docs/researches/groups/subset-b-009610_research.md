# subset-b-009610 Research

Grouped research for Impacket example scripts in `sources/user-network-fs/impacket/examples`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/rdp_check.py -->
# sources/user-network-fs/impacket/examples/rdp_check.py

## Purpose

`rdp_check.py` is a partial RDPBCGR/CredSSP client used to validate whether supplied NTLM credentials are accepted by an RDP endpoint. It hand-builds the TPKT/TPDU negotiation, upgrades to TLS, performs an NTLM SPNEGO exchange inside CredSSP `TSRequest` messages, and reports access granted or denied without establishing a full RDP session.

## Important APIs, Types, and Functions

The packet structures are `TPKT`, `TPDU`, `CR_TPDU`, `DATA_TPDU`, `RDP_NEG_REQ`, `RDP_NEG_RSP`, and `RDP_NEG_FAILURE`, all using Impacket `Structure`. CredSSP ASN.1 payloads are modeled by `TSPasswordCreds`, `TSCredentials`, and `TSRequest` subclasses of `GSSAPI`. Runtime-only `SPNEGOCipher` wraps NTLM signing/sealing state. `check_rdp()` drives negotiation, TLS setup, NTLM type 1/type 3 creation, public key sealing, credential sealing, and result logging.

## Control Flow

The CLI parses `[[domain/]user[:pass]@]target`, optional hashes, IPv6, and logging flags. `check_rdp()` sends an RDP negotiation request for SSL plus hybrid CredSSP, rejects servers that do not support hybrid mode, starts a pyOpenSSL TLS session, sends NTLM type 1 in `TSRequest.NegoData`, parses the server challenge, computes NTLM type 3 with password or hashes, extracts the server certificate public key, seals it into `pubKeyAuth`, and sends the final auth token. It then parses the server `pubKeyAuth`, seals `TSCredentials`, sends them as `authInfo`, closes TLS, and logs success if the preceding exchange did not raise an access-denied exception.

## State and Persistence Behavior

The script opens a TCP connection to port 3389 and mutates only in-memory protocol state. It does not create files or persistent remote state. The target receives a real CredSSP authentication attempt, so account lockout and audit records are possible. Passwords and NTLM hashes are kept in process memory.

## Dependencies and Integration Points

It depends on `get_connected_socket`, `parse_target`, Impacket `ntlm`, ASN.1 helpers from `impacket.spnego`, `Cryptodome.Cipher.ARC4`, and pyOpenSSL `SSL`/`crypto`. It integrates directly with RDP servers that support CredSSP hybrid security and with Impacket's example logger.

## Risks and Edge Cases

The implementation intentionally shortcuts full CredSSP verification and notes incomplete signature validation. TLS is configured with `ALL:@SECLEVEL=0` and unsafe legacy renegotiation compatibility, which broadens protocol compatibility at security cost. Hash parsing requires `LMHASH:NTHASH`. Socket/TLS reads have fixed buffer sizes and limited recovery behavior. Authentication attempts can trigger lockouts, and the "access granted" inference relies on observed protocol behavior rather than a complete RDP login.

## Test Signals

Unit tests should round-trip `TSRequest`, `TSPasswordCreds`, and `TSCredentials` encoding/decoding and mock NTLM sealing. Integration tests need Windows RDP targets with valid, invalid, hash-based, and IPv6 authentication cases, plus a non-CredSSP server path that should log unsupported hybrid security.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/rdp_check.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/reg.py -->
# sources/user-network-fs/impacket/examples/reg.py

## Purpose

`reg.py` is a remote Windows registry manipulation tool modeled after `reg.exe`. It authenticates over SMB, starts or triggers the RemoteRegistry service when needed, binds to the Remote Registry Protocol (`\pipe\winreg`), and supports query, add, delete, save, and backup operations.

## Important APIs, Types, and Functions

`RemoteOperations` owns service-control and winreg RPC connections, tracks whether RemoteRegistry was disabled or stopped, and restores service state in `finish()`. `RegHandler` owns credentials, SMB login, action dispatch, and registry operations. Key methods include `connect()`, `run()`, `triggerWinReg()`, `save()`, `query()`, `add()`, `delete()`, `__strip_root_key()`, `__print_key_values()`, `__print_all_subkeys_and_entries()`, and `__parse_lp_data()`.

## Control Flow

The CLI builds subcommands for `query`, `add`, `delete`, `save`, and `backup`, parses target/auth/connection options, prompts for a password when needed, and instantiates `RegHandler`. `run()` logs into SMB, creates `RemoteOperations`, attempts `enableRegistry()`, falls back to opening the `\winreg` named pipe to trigger startup, then dispatches the requested action. Queries open a root hive and either read a value, default value, direct values/subkeys, or recursively enumerate. Add can create a volatile or persistent key or set typed value data. Delete removes keys, one value, default value, or all values. Save and backup call `hBaseRegSaveKey()` to a UNC path visible to the target.

## State and Persistence Behavior

Remote state can change substantially: RemoteRegistry may be started and possibly reconfigured from disabled to demand start, registry keys and values can be created/deleted, and registry hives can be saved to a remote UNC path. `RemoteOperations.finish()` tries to stop and disable RemoteRegistry only if it changed those states. Local state is limited to stdout/logging and interactive password input.

## Dependencies and Integration Points

It integrates with Impacket `SMBConnection`, DCE/RPC transports, `rrp`, `scmr`, `rpcrt`, Windows service control, and `ERROR_NO_MORE_ITEMS`. Kerberos, AES keys, NTLM hashes, target IP override, and SMB port 139/445 are supported.

## Risks and Edge Cases

Registry writes and deletes are high-impact and not transactionally rolled back. The fallback named-pipe trigger assumes a target behavior and sleeps for one second. Recursive queries may hit access denied or bad stub data and skip branches. `REG_BINARY` input is padded if odd-length hex is provided. `save()` writes on the target side to a UNC path, so permissions and path interpretation can fail. Service-state restoration can fail if the process is interrupted after remote changes.

## Test Signals

Mock tests should cover root-key parsing, value type conversion, binary padding, `REG_MULTI_SZ` construction, delete-mode dispatch, service state restoration decisions, and recursive enumeration error handling. Integration tests require a Windows host and should verify query, volatile/persistent add, delete variants, Kerberos/hash login, RemoteRegistry disabled/start/restore behavior, and hive save to a controlled share.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/reg.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/registry-read.py -->
# sources/user-network-fs/impacket/examples/registry-read.py

## Purpose

`registry-read.py` is an offline Windows registry hive reader. It opens a local hive through Impacket `winregistry`, then enumerates keys, enumerates values, reads a value, reads class metadata, or walks a subtree.

## Important APIs, Types, and Functions

`bootKey()` demonstrates SYSTEM boot key reconstruction from `ControlSet001\Control\Lsa\JD`, `Skew1`, `GBG`, and `Data` class data, although it is not exposed through the CLI. `getClass()`, `getValue()`, `enumValues()`, `enumKey()`, and `walk()` are thin wrappers around parser methods. `main()` owns argument parsing, logger setup, parser creation through `winregistry.get_registry_parser()`, action dispatch, and `reg.close()`.

## Control Flow

The script requires a hive path and one subcommand. After parsing and logger setup, it opens the hive parser and dispatches by uppercase action. `enum_key` finds a key and prints child keys, recursing when requested. `enum_values` lists value names and uses `printValue()` for each. `get_value` and `get_class` print one value/class payload. `walk` delegates traversal to the parser. The parser is closed at the end of normal execution.

## State and Persistence Behavior

The script is read-only for the input hive. It prints decoded data to stdout and does not write output files. It holds hive parser state until `close()`.

## Dependencies and Integration Points

It depends on `impacket.winregistry`, `ntpath` for key/value path splitting, `hexlify`/`unhexlify` for boot key demonstration, and the Impacket example logger. It integrates with offline registry hive files, not the remote registry protocol.

## Risks and Edge Cases

The CLI does not expose `bootKey()`, and that function mixes byte-oriented `unhexlify()` output with a string accumulator, which is fragile under Python 3 if called. Missing keys simply return without explicit status. `enumValues()` decodes value names as UTF-8, which can fail for unusual names. The parser is not closed if an exception occurs before the final close.

## Test Signals

Tests should use small fixture hives to verify key enumeration, recursive traversal, value rendering, class rendering, missing-key behavior, and binary value formatting. A direct test of `bootKey()` should catch Python 3 byte/string compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/registry-read.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/regsecrets.py -->
# sources/user-network-fs/impacket/examples/regsecrets.py

## Purpose

`regsecrets.py` remotely extracts SAM hashes, cached domain credentials, and LSA secrets by using registry-backed techniques from `impacket.examples.regsecrets`. It is a narrower, registry-focused secrets dumper that does not include the broader NTDS/DRSUAPI modes in `secretsdump.py`.

## Important APIs, Types, and Functions

`DumpSecrets` stores target identity, SMB/auth settings, output file base name, bootkey override, skip flags, history, and throttle. `connect()` establishes SMB with NTLM or Kerberos. `dump()` enables RemoteRegistry, obtains or parses a boot key, instantiates `SAMHashes` and `LSASecrets`, dumps selected data, exports optional files, and calls `cleanup()`. `cleanup()` finishes remote operations and logs off SMB.

## Control Flow

The CLI parses target, `-bootkey`, `-nosam`, `-nocache`, `-nolsa`, throttle, output, history, keytab, hashes, Kerberos, AES, DC IP, and target IP. Keytab or AES options force Kerberos. `DumpSecrets.dump()` logs into SMB, builds `RemoteOperations`, enables the registry service, retrieves the boot key unless supplied, extracts SAM unless skipped, extracts cached hashes unless skipped, extracts LSA secrets unless skipped, exports requested output files, and attempts cleanup both on normal and error paths.

## State and Persistence Behavior

RemoteRegistry may be started or reconfigured temporarily by the helper implementation and restored by `finish()`. Hive data may be saved/read remotely by the imported helper classes. Local output files are created when `-outputfile` is used, with helper-specific suffixes for SAM/cached/secrets data. Credentials and extracted secrets are printed and kept in memory during execution.

## Dependencies and Integration Points

It depends on `SMBConnection`, `parse_target`, `Keytab`, and `LSASecrets`, `RemoteOperations`, and `SAMHashes` from `impacket.examples.regsecrets`. It integrates with SMB, RemoteRegistry, Windows registry hive semantics, Kerberos credential caches/keytabs, and Impacket logging.

## Risks and Edge Cases

This is a credential extraction tool and exposes sensitive material by design. If `RemoteOperations` setup fails, later `getBootKey()` calls can encounter `None` state. Cleanup calls `self.__smbConnection.logoff()` without checking whether the connection exists, so early failures can produce secondary cleanup errors. Bootkey parsing accepts optional `0x` prefix but otherwise assumes valid hex. Remote service/hive artifacts depend on helper cleanup.

## Test Signals

Mock tests should exercise bootkey override parsing, skip-flag dispatch, output export calls, cleanup after partial connection failure, and keytab/AES option handling. Integration tests need a controlled Windows target and should verify SAM-only, cache-only, LSA-only, history, throttle, Kerberos/keytab, and cleanup behavior with RemoteRegistry initially stopped or disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/regsecrets.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/rpcdump.py -->
# sources/user-network-fs/impacket/examples/rpcdump.py

## Purpose

`rpcdump.py` queries a remote DCE/RPC endpoint mapper and prints registered interfaces grouped by UUID, provider, protocol, annotation, and string bindings. It supports common endpoint mapper transports over TCP, SMB named pipes, RPC over HTTP, and RPC proxy.

## Important APIs, Types, and Functions

`RPCDump.KNOWN_PROTOCOLS` maps ports 135, 139, 443, 445, and 593 to binding string templates. `RPCDump.__init__()` stores credentials, hashes, and selected port. `dump()` builds the transport, applies SMB or HTTP proxy authentication as needed, calls `__fetchList()`, groups endpoint entries, maps UUIDs through `epm.KNOWN_UUIDS` and `epm.KNOWN_PROTOCOLS`, and prints the results. `__fetchList()` connects and calls `epm.hept_lookup()`.

## Control Flow

The CLI parses target, target IP, endpoint mapper port, hashes, logging flags, and optional password prompt. `dump()` chooses the binding string from the port, configures credentials for SMB transports or RPC proxy, then fetches endpoint entries. Exceptions are logged, with special explanations for common RPC proxy failures. Successful results are grouped by interface UUID and printed with all bindings.

## State and Persistence Behavior

The script is read-only against the target endpoint mapper. It opens network connections and prints discovered metadata; it writes no local files and creates no remote state.

## Dependencies and Integration Points

It uses Impacket `transport`, `epm`, `uuid`, RPC over HTTP error constants, `AUTH_NTLM`, and `parse_target`. It integrates with Windows/Samba endpoint mappers and RPC proxy deployments.

## Risks and Edge Cases

The port must be one of the hard-coded choices. RPC proxy support assumes NTLM for proxy authentication. Endpoint annotations are decoded as UTF-8 after stripping the trailing null and can fail for unexpected encodings. `__fetchList()` does not use `finally` for disconnect, so exceptions before disconnect can leave sockets until process exit.

## Test Signals

Tests can mock `epm.hept_lookup()` responses and verify grouping, provider/protocol lookup, binding formatting, and port-specific credential setup. Integration coverage should query ports 135, 445, 593, and a negative RPC proxy scenario.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/rpcdump.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/rpcmap.py -->
# sources/user-network-fs/impacket/examples/rpcmap.py

## Purpose

`rpcmap.py` discovers listening MSRPC interfaces for an arbitrary string binding. It first asks the MGMT interface for registered interface IDs, optionally brute-forces known UUIDs, and can further brute-force interface major versions or operation numbers.

## Important APIs, Types, and Functions

`RPCMap` owns a parsed `DCERPCStringBinding`, auth level, brute-force options, UUID database, transport, and DCE object. Key methods are `set_transport_credentials()`, `set_rpc_credentials()`, `set_smb_info()`, `connect()`, `disconnect()`, `do()`, `bruteforce_versions()`, `bruteforce_opnums()`, `bruteforce_uuids()`, and `handle_discovered_tup()`. The CLI uses `parse_identity()` separately for transport and MSRPC credentials.

## Control Flow

The CLI validates options, parses separate auth material for RPC and transport, loads either a single UUID or `rpcdatabase.uuid_database`, creates `RPCMap`, configures credentials and SMB host/port overrides, connects, runs discovery, and disconnects. `do()` binds MGMT and calls `mgmt.hinq_if_ids()`, unless MGMT is unavailable or brute UUID mode is requested. Each found tuple is printed with known protocol/provider metadata and optional version/opnum brute-force results.

## State and Persistence Behavior

The script does not persist local or remote data, but it can generate many RPC connections and calls. `set_rpc_credentials()` enables a lockout-protection flag so access denied on MGMT with credentials does not automatically brute-force unauthenticated paths.

## Dependencies and Integration Points

It depends on Impacket `transport`, `rpcrt`, `epm`, `mgmt`, `uuid`, `rpcdatabase`, `DCERPCStringBinding`, `SMBTransport`, RPC proxy error constants, and `AUTH_BASIC`. It integrates with named-pipe, TCP, HTTP, and RPC-proxy string bindings.

## Risks and Edge Cases

The source TODO notes connections are never fully closed during brute-force loops, because each bind path reconnects on the same DCE object. `elif str(e).find('rpc_s_access_denied')` treats `-1` as truthy, so that condition is broader than intended. Brute opnum mode sends empty calls that can trigger server-side faults or logs. Auth failures and brute forcing may cause lockouts or detection. The printed label has a `Procotol` typo for unknown protocols.

## Test Signals

Mock tests should cover MGMT success, MGMT unavailable fallback, access denied with/without credentials, UUID filtering, version result compaction, opnum result compaction, and SMB transport host/port overrides. Integration tests should include a named-pipe endpoint, an unauthenticated endpoint, authenticated endpoint, and capped brute-force ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/rpcmap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/sambaPipe.py -->
# sources/user-network-fs/impacket/examples/sambaPipe.py

## Purpose

`sambaPipe.py` is an exploit helper for CVE-2017-7494. It authenticates to a Samba SMB server, finds a writable share, uploads a user-supplied shared object, and attempts to trigger loading through a crafted path opened on `IPC$`.

## Important APIs, Types, and Functions

`PIPEDREAM` owns the SMB client and CLI options. `isShareWritable()` probes share write access. `findSuitableShare()` uses SRVSVC `NetrShareEnum` level 2 to find writable shares and their server-side paths. `uploadSoFile()` uploads the local `-so` file. `create()` manually builds an SMB2 CREATE packet. `openPipe()` builds the absolute share path and sends either SMB1 `NT_CREATE_ANDX` or SMB2 CREATE without Impacket's normal NT path conversion. `run()` orchestrates find/upload/trigger/delete.

## Control Flow

The CLI parses target, required `-so`, auth, Kerberos/AES, target IP, DC IP, and SMB port. It logs in with NTLM or Kerberos, disables SMB3 encryption by clearing `SMB2_SESSION_FLAG_ENCRYPT_DATA` when using SMB2/3, then runs `PIPEDREAM`. The exploit path enumerates shares, chooses the first writable one, uploads the shared object, opens `IPC$` with a path pointing at the uploaded object, handles expected `STATUS_OBJECT_NAME_NOT_FOUND`, and deletes the uploaded file in `finally`.

## State and Persistence Behavior

The tool writes the supplied `.so` to a remote writable share and deletes it afterward. If deletion fails or the process is interrupted, the library remains. It may execute code inside vulnerable Samba. It also mutates the in-memory SMB session flags to disable encryption.

## Dependencies and Integration Points

It integrates with `SMBConnection`, low-level SMB1/SMB2 packet classes, SRVSVC over DCE/RPC, Kerberos/NTLM auth, and Samba share path semantics. It relies on Samba exposing Windows-style share metadata and on CVE-2017-7494 behavior.

## Risks and Edge Cases

This is exploit code and can run arbitrary code on vulnerable targets. Writable share detection opens the share root with write access and may miss shares with path-specific permissions. The first writable share may not be suitable. Disabling SMB3 encryption is intrusive and uses private connection internals. `create()` returns only on success and otherwise implicitly returns `None`. Cleanup only removes the uploaded filename from the selected share.

## Test Signals

Unit tests can mock SRVSVC share enumeration, writable probes, upload/delete calls, SMB1/SMB2 dialect selection, and path construction. Integration testing should be restricted to a lab Samba version and should verify cleanup on expected and unexpected trigger errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/sambaPipe.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/samedit.py -->
# sources/user-network-fs/impacket/examples/samedit.py

## Purpose

`samedit.py` edits an offline SAM hive in place to replace an existing local user's password hash. It uses a SYSTEM hive or explicit bootkey to decrypt/encrypt SAM password material and either derives an NT hash from a password or accepts supplied hashes.

## Important APIs, Types, and Functions

This script has no custom classes. It uses `LocalOperations.getBootKey()` from `impacket.examples.secretsdump`, `SAMHashes.edit()`/`finish()`, and `ntlm.NTOWFv1()`. CLI validation enforces exactly one bootkey source and exactly one password/hash source.

## Control Flow

The CLI requires user and SAM hive paths plus either `-system` or `-bootkey`, and either `-password` or `-hashes`. It initializes logging, validates mutually exclusive options, obtains the bootkey, constructs `SAMHashes(options.sam, bootkey, False)`, converts the desired credential material to LM/NT hash bytes, calls `hive.edit(user, NTHash, LMHash)`, logs errors, and always calls `hive.finish()`.

## State and Persistence Behavior

The SAM hive file is modified in place. No backup is created by this script. The SYSTEM hive is read-only when supplied. Password/hash data exists in memory during the run and may be visible in shell history if passed as arguments.

## Dependencies and Integration Points

It depends on Impacket `ntlm`, `LocalOperations`, `SAMHashes`, and the example logger. It integrates with offline Windows SAM/SYSTEM hive formats rather than remote services.

## Risks and Edge Cases

The tool only replaces an existing user's password and does not create users. In-place editing can corrupt a hive if interrupted or if the wrong bootkey is supplied. Hash parsing accepts a single NT hash or `LM:NT` pair but does not validate lengths before unhexlify/use. `logger.init(options.ts)` ignores the debug flag until logging level is manually set.

## Test Signals

Tests should use disposable SAM/SYSTEM fixtures to verify password-derived hash editing, direct NT hash editing, LM:NT hash editing, invalid option combinations, invalid hex handling, missing user behavior, and that `finish()` is invoked on edit failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/samedit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/samrdump.py -->
# sources/user-network-fs/impacket/examples/samrdump.py

## Purpose

`samrdump.py` enumerates users from a remote SAMR service and prints account metadata. It can emit human-readable output or CSV.

## Important APIs, Types, and Functions

`SAMRDump` stores auth settings, Kerberos options, SMB port, and CSV mode. `getUnixTime()` converts Windows FILETIME to Unix time. `dump()` prepares the `\pipe\samr` transport, fetches entries, converts password-last-set and account flags, and prints output. `__fetchList()` connects to SAMR, enumerates domains, opens the first domain, pages through users, opens each user, queries `UserAllInformation`, and closes user handles.

## Control Flow

The CLI parses target, CSV, auth, Kerberos/AES, DC IP, target IP, and SMB port. After password prompting and option normalization, `dump()` connects through `ncacn_np:<remote>[\pipe\samr]`, sets credentials and Kerberos, calls `__fetchList()`, then prints each returned `(username, rid, userInfo)` as CSV or key/value lines.

## State and Persistence Behavior

The script is read-only against SAMR and does not write files. It prints user metadata and can expose account status information. It opens and closes DCE/RPC and SAMR handles during enumeration.

## Dependencies and Integration Points

It uses Impacket `transport`, `samr`, `DCERPCException`, `STATUS_MORE_ENTRIES`, target parsing, and the example logger. It integrates with SMB named-pipe SAMR on Windows or compatible servers.

## Risks and Edge Cases

Only the first enumerated domain is queried. CSV output performs simple comma replacement on comments but does not quote fields, so embedded newlines or commas in other fields can still break CSV. `datetime.fromtimestamp()` uses local timezone. Exceptions during enumeration can skip disconnect because no `finally` wraps `dce.disconnect()`. Large domains can produce many per-user open/query calls.

## Test Signals

Mock SAMR tests should cover paged enumeration, `STATUS_MORE_ENTRIES` exception packets, FILETIME conversion, flag decoding, CSV formatting, and handle closing. Integration tests should include anonymous/low-privilege behavior, Kerberos/hash login, CSV mode, and a domain with enough users to require pagination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/samrdump.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/secretsdump.py -->
# sources/user-network-fs/impacket/examples/secretsdump.py

## Purpose

`secretsdump.py` is Impacket's broad credential extraction entry point. It can dump local SAM/SECURITY/NTDS files, remotely extract SAM and LSA secrets via RemoteRegistry, dump NTDS data via DRSUAPI replication, use VSS/remote shadow-copy methods, or use the Kerberos RODC key-list method.

## Important APIs, Types, and Functions

`DumpSecrets` stores mode flags, target/auth state, hive paths, output settings, filtering options, and helper instances. `connect()` establishes SMB. `ldapConnect()` creates LDAP/LDAPS connections and base DN. `dump()` selects local, remote, remote shadow-copy, key-list, SAM/LSA, and NTDS flows. `cleanup()` finishes `RemoteOperations`, `SAMHashes`, `LSASecrets`, `NTDSHashes`, and `KeyListSecrets`. Imported helper classes do most protocol and parsing work.

## Control Flow

The CLI validates many mutually exclusive modes: `LOCAL`, `-just-dc-user`/`-ldapfilter`, VSS, remote WMI shadow-copy, resume files, key-list RODC requirements, keytab/AES Kerberos, and target IP defaults. In remote registry mode, `dump()` may connect to LDAP for filters, logs into SMB, creates `RemoteOperations`, sets the remote execution method, enables RemoteRegistry when SAM/LSA or VSS needs it, gets the bootkey, and checks LM-hash policy. It then optionally dumps SAM, SECURITY/LSA, and NTDS. NTDS may use DRSUAPI, VSS, local file parsing, or downloaded shadow-copy files. Error handling can remove a bad DRSUAPI resume file and suggests VSS fallback.

## State and Persistence Behavior

Remote modes can start services, save hives, create VSS snapshots, execute remote commands through selected methods, download hive/NTDS files, and create temporary remote artifacts through helper classes. Local output files are created when `-outputfile` is supplied, and DRSUAPI resume files may persist unless deleted. `cleanup()` delegates cleanup to helpers on normal and error paths.

## Dependencies and Integration Points

It depends on `SMBConnection`, `LDAPConnection`, `LocalOperations`, `RemoteOperations`, `SAMHashes`, `LSASecrets`, `NTDSHashes`, `KeyListSecrets`, `Keytab`, Kerberos caches/keytabs, RemoteRegistry, DRSUAPI, LDAP/LDAPS, VSS, WMI shadow copy, and SMB-based remote execution.

## Risks and Edge Cases

This script intentionally extracts highly sensitive credential material. Mode interactions are complex and rely on CLI validation to avoid unsupported combinations. Remote cleanup depends on helper success and may leave services, temp files, snapshots, or resume files after interruption. Some conditionals use `str(e).find(...)` without comparing to `>= 0`, which can misclassify errors because `-1` is truthy. LDAP base DN inference from target/domain can be wrong for unusual names. Output files and command-line secrets require careful handling.

## Test Signals

Mock tests should cover CLI validation, local bootkey mode, remote registry flow, LDAP stronger-auth retry, key-list requirements, VSS/resume incompatibilities, DRSUAPI resume deletion on `ERROR_DS_DRA_BAD_DN`, and cleanup ordering. Integration tests require isolated Windows/AD labs for SAM/LSA, DRSUAPI, VSS, remote WMI shadow-copy, just-user/filter, Kerberos/keytab, and failure cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/secretsdump.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/services.py -->
# sources/user-network-fs/impacket/examples/services.py

## Purpose

`services.py` manipulates Windows services over the Service Control Manager Remote Protocol. It can list services, query status/configuration, start, stop, delete, create, or change a service.

## Important APIs, Types, and Functions

`SVCCTL` stores credentials, Kerberos settings, selected action, and SMB port. `run()` creates an `ncacn_np:<remote>[\pipe\svcctl]` transport and configures auth. `doStuff()` binds SCMR, opens the service control manager, optionally opens a service, dispatches the requested action, encrypts service account passwords with `encryptSecret()` for change operations, closes handles, and disconnects.

## Control Flow

The CLI defines subcommands for `start`, `stop`, `delete`, `status`, `config`, `list`, `create`, and `change`, then parses auth and connection settings. `doStuff()` opens SCM, branches on `self.__action`, and calls the corresponding `scmr.hR*` helper. Read operations print decoded state/config. Mutating operations call start/stop/delete/create/change and close service handles when implemented.

## State and Persistence Behavior

Start/stop affect service runtime state. Delete, create, and change persistently alter SCM configuration. Changing a service account password encrypts the password with the SMB session key before transmission. The script writes no local files.

## Dependencies and Integration Points

It depends on Impacket `transport`, `scmr`, NDR `NULL`, `encryptSecret`, target parsing, Kerberos/AES/hash support, and SMB named-pipe transport on ports 139/445.

## Risks and Edge Cases

Service operations are high impact and can break hosts. Error handling is mostly outer-level; the file TODO notes error checking is incomplete. Handles may not close if an exception occurs before the close calls. `CREATE` does not close a returned service handle. Numeric service/start types are accepted as raw integers with little validation. Password arguments can leak through shell history.

## Test Signals

Mock tests should verify action dispatch, SCMR calls, state label rendering, config rendering, password encryption invocation, and close/disconnect behavior. Integration tests should run against disposable services on a lab Windows host for all subcommands and auth modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/services.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/smbclient.py -->
# sources/user-network-fs/impacket/examples/smbclient.py

## Purpose

`smbclient.py` is a command-line wrapper around Impacket's `MiniImpacketShell`. It authenticates to an SMB server and either opens an interactive shell or runs commands from an input file.

## Important APIs, Types, and Functions

`main()` owns all behavior. It parses target/auth/connection/logging options, creates `SMBConnection`, performs NTLM or Kerberos login, instantiates `MiniImpacketShell(smbClient, None, outputfile)`, optionally writes an output-file header, and runs either scripted `onecmd()` calls or `cmdloop()`.

## Control Flow

After parsing, the script normalizes domain and target IP, prompts for a password unless disabled or alternate credentials are present, splits hashes, logs into SMB, and creates the shell. In input-file mode it skips comment lines that start with `#`, prints each command, and sends it to the shell. Without an input file, it enters the interactive command loop.

## State and Persistence Behavior

Remote state depends on commands executed in `MiniImpacketShell` and can include file uploads, deletes, directory changes, and other SMB operations. Locally, `-outputfile` appends a target header and shell actions through the shell implementation. The input file is read but not modified.

## Dependencies and Integration Points

It depends on `SMBConnection`, `MiniImpacketShell`, target parsing, Impacket logger, Kerberos/AES/hash auth, and SMB ports 139/445. It is mainly an entry point for the reusable shell implementation in `impacket.examples.smbclient`.

## Risks and Edge Cases

Input-file processing indexes `line[0]`, so blank lines can raise `IndexError`. Output-file header writing is separate from shell logging and can fail independently. The script does not explicitly log off or close the SMB connection. Command side effects are delegated and can be destructive.

## Test Signals

Mock tests should cover auth option normalization, hash splitting, password prompt suppression, blank/comment/scripted input handling, output-file header creation, and shell invocation. Integration tests should cover interactive login, Kerberos, hash login, and scripted file operations against a test SMB share.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/smbclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/smbexec.py -->
# sources/user-network-fs/impacket/examples/smbexec.py

## Purpose

`smbexec.py` provides a semi-interactive remote command shell by creating transient Windows services through SCMR. Command output is redirected to a target share or copied back to a locally started SMB server.

## Important APIs, Types, and Functions

`SMBServer` is a thread that creates a temporary local SMB server rooted at `__tmp` with share `TMP`. `CMDEXEC` owns auth settings, mode, share, service name, and shell type. `RemoteShell` extends `cmd.Cmd` and manages SCMR handles, output paths, command encoding, service creation, output retrieval, and cleanup. Important methods include `RemoteShell.execute_remote()`, `get_output()`, `send_data()`, `do_cd()`, and `finish()`.

## Control Flow

The CLI parses target, share/server mode, codec, shell type, service name, keytab/auth, and connection options. `CMDEXEC.run()` creates an SCMR transport, optionally starts the local SMB server in SERVER mode, then enters `RemoteShell.cmdloop()`. Each command is wrapped in a temporary batch file under `%SYSTEMROOT%`, run as a service binary path, redirected to `\\%COMPUTERNAME%\<share>\<output>`, optionally copied to the local SMB server, then the service and batch file are deleted and output is fetched.

## State and Persistence Behavior

Remote state includes transient service entries, temporary batch files, and output files. SERVER mode creates local `__tmp`, binds a local SMB server on port 445, receives output, and removes the directory on stop. `finish()` attempts to delete the remote output file and service. Artifacts may remain on interruption or cleanup failure.

## Dependencies and Integration Points

It integrates with Impacket `smbserver`, SCMR over SMB named pipes, Kerberos keytabs, `SMBConnection` obtained from the transport, Python `cmd`, and Windows command processors. PowerShell mode base64-encodes UTF-16LE commands for `powershell.exe -Enc`.

## Risks and Edge Cases

This is remote code execution and creates many Windows service events. SERVER mode usually requires root/admin locally to bind port 445. `SMBServer.stop()` uses private thread `_Thread__stop()` and can be fragile. Cleanup may fail if service creation partially fails. Command construction relies on `echo` and shell escaping, which can mishandle complex metacharacters. The output codec defaults to local stdout encoding, which may not match the target.

## Test Signals

Mock tests should cover service command construction, PowerShell encoding, share versus server output retrieval, cleanup on exceptions, codec fallback, and custom service name use. Integration tests should use a lab Windows host for SHARE and SERVER modes, command output, PowerShell mode, Kerberos/keytab, and interrupted-session cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/smbexec.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/smbserver.py -->
# sources/user-network-fs/impacket/examples/smbserver.py

## Purpose

`smbserver.py` starts a simple Impacket SMB server exposing one user-specified share. It can allow anonymous access, require a username/password or NTLM hashes, support SMB2, and optionally configure computer-account credentials for clients that require signing.

## Important APIs, Types, and Functions

The script is a single CLI entry point around `smbserver.SimpleSMBServer`. It calls `addShare()`, `setSMB2Support()`, `setDropSSP()`, `setKerberosSupport()`, `setNTLMSupport()`, `addCredential()`, `setComputerAccount()`, `setSMBChallenge()`, `setLogFile()`, and `start()`. Passwords are converted with `compute_lmhash()` and `compute_nthash()`.

## Control Flow

The CLI parses share name/path, optional auth, computer account signing options, listen address/port, IPv6, read-only mode, SMB2 support, NTLM/Kerberos toggles, drop-SSP, and output log file. It initializes logging, defaults the listen address, builds the server, adds the share, configures protocol/auth settings, validates mutually exclusive user versus computer-account auth, adds credentials if requested, sets an empty/default challenge, and starts the server until interrupted.

## State and Persistence Behavior

The process listens on the configured interface and port and exposes the provided filesystem path. It does not persist configuration outside memory. If `-outputfile` is used, server logs are written to that file. Shared files can be read or written by clients unless `-readonly` is set.

## Dependencies and Integration Points

It depends on Impacket `smbserver`, NTLM hash helpers, the example logger, local filesystem paths, and optional domain controller communication for computer account support.

## Risks and Edge Cases

Binding port 445 usually requires elevated privileges. Anonymous writable shares are possible by default if no username and no `-readonly` are set. Misconfigured computer-account options abort. The share path is trusted from the CLI and can expose sensitive local files. The fixed empty challenge delegates default behavior but users may expect explicit randomization.

## Test Signals

Tests should verify option validation, credential hash generation, anonymous versus authenticated configuration, read-only flag mapping, IPv4/IPv6 listen defaults, computer-account validation, and output log configuration. Integration tests should connect with SMB1/SMB2 clients and verify read/write/auth behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/smbserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/sniff.py -->
# sources/user-network-fs/impacket/examples/sniff.py

## Purpose

`sniff.py` is a pcap-based live packet sniffer. It prompts for a capture interface when needed, applies an optional BPF filter, decodes Ethernet or Linux cooked frames with ImpactDecoder, and prints decoded packets.

## Important APIs, Types, and Functions

`DecoderThread` selects `EthDecoder` or `LinuxSLLDecoder` based on `pcapObj.datalink()`, then runs `pcap.loop(0, packetHandler)`. `packetHandler()` decodes and prints each packet. `getInterface()` lists devices from `pcapy.findalldevs()` and prompts if there are multiple. `main(filter)` opens the interface with `open_live()`, sets the BPF filter, prints capture metadata, and starts the decoder thread.

## Control Flow

The script treats all command-line arguments as one BPF filter string. It prints a deprecation warning banner, selects an interface, opens a live pcap handle with snaplen 1500, non-promiscuous mode, and 100 ms timeout, applies the filter, prints network/mask/linktype, and starts the background decoder thread.

## State and Persistence Behavior

It captures live network traffic and prints decoded packet structures. It writes no files. The process runs indefinitely until interrupted, and the background thread owns the pcap loop.

## Dependencies and Integration Points

It depends on `pcapy`, libpcap permissions/device availability, Impacket `ImpactDecoder`, and link-layer constants `DLT_EN10MB` and `DLT_LINUX_SLL`.

## Risks and Edge Cases

Live capture often requires elevated privileges. Unsupported datalink types raise an exception. Interface selection does not validate numeric input. The pcap handle is not explicitly closed. Packet printing can be very noisy and may expose sensitive traffic. The code starts a non-daemon thread and has no graceful stop path.

## Test Signals

Unit tests can mock pcap handles for datalink selection, filter application, interface selection branches, and packet decoding. Integration tests should verify BPF filters, Ethernet and Linux SLL captures, unsupported datalink behavior, and permission-denied messaging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/sniff.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/sniffer.py -->
# sources/user-network-fs/impacket/examples/sniffer.py

## Purpose

`sniffer.py` is a raw-socket IP packet sniffer. It listens for one or more IP protocols, decodes received packets with `ImpactDecoder.IPDecoder`, and prints them.

## Important APIs, Types, and Functions

There are no custom functions or classes. Module-level code computes `toListen`, creates one raw `AF_INET` socket per protocol from `socket.getprotobyname()`, sets `IP_HDRINCL`, uses `select()` to wait for packets, calls `recvfrom()`, and decodes with `ImpactDecoder.IPDecoder()`.

## Control Flow

With no arguments it listens for `icmp`, `tcp`, and `udp`. With arguments it treats each argument as a protocol name, skips unknown protocols, exits if none remain, then enters a loop over sockets ready for reading. Empty reads close and remove a socket; non-empty reads are decoded and printed.

## State and Persistence Behavior

The script opens raw sockets and prints live packet data. It writes no files and persists no state beyond the running process.

## Dependencies and Integration Points

It depends on OS raw socket support, protocol name resolution, `select`, and Impacket `ImpactDecoder`. It is IP-layer only and assumes returned packets include IP headers.

## Risks and Edge Cases

Raw sockets require elevated privileges on most systems and are platform-dependent. The code mutates `toListen` while iterating over it when dropping unknown protocols, which can skip later entries. There is no timeout or signal cleanup. Printed packet data may expose sensitive traffic.

## Test Signals

Mock tests should cover default protocols, unknown protocol filtering, empty protocol exit, socket creation options, empty reads, and decode/print flow. Integration tests require a privileged environment and controlled ICMP/TCP/UDP traffic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/sniffer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/split.py -->
# sources/user-network-fs/impacket/examples/split.py

## Purpose

`split.py` reads an offline pcap file and splits TCP/IP traffic into one output pcap per connection. Output filenames are derived from endpoint IP addresses and ports.

## Important APIs, Types, and Functions

`Connection` stores two peer tuples, produces a filename with `getFilename()`, implements Python 2-era `__cmp__()`, and hashes both peers order-independently. `Decoder` chooses an Ethernet or Linux SLL decoder, stores a mapping of connection keys to pcap dumpers, starts pcap iteration, and handles packets in `packetHandler()`. `main()` opens the pcap with `open_offline()`, applies an `ip proto \tcp` filter, and starts decoding.

## Control Flow

The CLI prints a deprecation warning and requires one pcap filename. `main()` opens the file, filters for TCP, and calls `Decoder.start()`. Each packet is decoded to IP and TCP children, source/destination tuples are built, a connection key is checked, a new dumper is opened for first-seen connections, and the original packet is dumped to that connection's pcap.

## State and Persistence Behavior

For every observed TCP connection, the script creates a new pcap file in the current working directory. Dumpers remain open until process exit. It does not modify the input pcap.

## Dependencies and Integration Points

It depends on `pcapy.open_offline()`, `pcap.dump_open()`, BPF filtering, `EthDecoder`, `LinuxSLLDecoder`, and packet child APIs from ImpactDecoder.

## Risks and Edge Cases

The intended order-independent connection equality is not actually used because dictionary keys are string concatenations of `con.p1` and `con.p2`; reverse-direction packets can be written to a separate file. `__cmp__()` is ignored in Python 3. Filenames can collide or be unsafe in unusual address formats. Non-TCP packets are filtered, but malformed decoded packets can still break child traversal. Dumpers are not explicitly closed.

## Test Signals

Tests should cover connection filename generation, reverse-direction grouping behavior, datalink selection, dumper creation failure, malformed packet handling, and output pcap creation. Integration tests should use a small pcap with bidirectional TCP traffic to expose whether both directions land in one file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/split.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ticketConverter.py -->
# sources/user-network-fs/impacket/examples/ticketConverter.py

## Purpose

`ticketConverter.py` converts Kerberos tickets between KRB-CRED `.kirbi` format and MIT/Heimdal ccache format. It can also decode a base64-wrapped input ticket before conversion.

## Important APIs, Types, and Functions

`parse_args()` defines input, output, and `--base64`. `main()` selects input source, detects format, dispatches conversion, and cleans temporary files. `is_kirbi_file()` checks for leading byte `0x76`. `is_ccache_file()` checks for leading byte `0x05`. `convert_kirbi_to_ccache()` uses `CCache.loadKirbiFile()` and `saveFile()`. `convert_ccache_to_kirbi()` uses `CCache.loadFile()` and `saveKirbiFile()`. `base64_decode_with_unwrap()` strips line wrapping and decodes Latin-1 text.

## Control Flow

The CLI prints the banner, parses arguments, optionally writes decoded base64 bytes to a named temporary file, then tests the effective input filename. Kirbi input is converted to ccache; ccache input is converted to kirbi; unknown leading bytes print an error. Base64 temporary files are closed and unlinked manually, with `PermissionError` handled for Windows.

## State and Persistence Behavior

The requested output file is written or overwritten by the `CCache` helper. With `--base64`, a temporary decoded ticket file is created with `delete=False` and then manually removed. No remote state is involved.

## Dependencies and Integration Points

It depends on `impacket.krb5.ccache.CCache`, `base64`, `struct`, `tempfile`, and filesystem access. It integrates with tools that use kirbi/KRB-CRED exports and ccache files consumed by Impacket/Kerberos workflows.

## Risks and Edge Cases

`decoded_file` is only defined when `--base64` is set; later guarded use is safe but fragile if code is rearranged. Format detection reads only one byte and can raise on empty files. Unknown formats do not set a nonzero exit status. Base64 decoding reads the whole file into memory and leaves temp files behind on non-`PermissionError` cleanup failures or crashes.

## Test Signals

Tests should cover kirbi-to-ccache conversion, ccache-to-kirbi conversion, base64 unwrap/cleanup, unknown and empty files, output overwrite behavior, and cleanup failure handling. Fixture tickets can be minimal parser-compatible files or mocked `CCache` calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ticketConverter.py -->
