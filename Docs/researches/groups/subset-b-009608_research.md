# Research Group subset-b-009608

This grouped report covers selected Impacket examples under `sources/user-network-fs/impacket/examples`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/filetime.py -->
# sources/user-network-fs/impacket/examples/filetime.py

## Purpose

`filetime.py` is an SMB timestamp inspection and modification utility. It mimics `stat` and `touch` behavior for remote files or directories by opening an SMB path, querying basic file information, and optionally setting selected Windows FILETIME fields. It supports NTLM, hashes, Kerberos, AES keys, explicit ports, target IP override, DC IP, and optional post-write validation.

## Important APIs, Types, and Functions

`FileTimes` is a dataclass containing `creation_time`, `last_access_time`, `last_write_time`, and `change_time` as Windows FILETIME integers. `pretty_repr()` converts populated fields with `FTtoPOSIX()` and `datetime.fromtimestamp()`, rendering `None` as `N/A`.

`filetime_query(connection, tid, fid)` chooses `SMBQueryFileBasicInfo` for SMB1 dialects and `FILE_BASIC_INFORMATION` for SMB2/3, then returns a `FileTimes` object. `filetime_set(connection, tid, fid, filetimes)` performs the inverse, building `SMBSetFileBasicInfo` or `FILE_BASIC_INFORMATION` and calling `SMBConnection.setInfo()`. `main()` owns CLI parsing, credential handling, SMB login, tree connect, file open, query/set, validation, and cleanup.

## Control Flow

The CLI requires `target`, `share`, `path`, and an action subcommand: `stat` or `touch`. For `touch`, the caller must provide exactly one source of new times: `--reference <share> <path>` to copy timestamps from another SMB object, or `--timestamp` parsed by `datetime.fromisoformat()`. The `-c/-a/-w/-m` flags decide which fields are written; unselected fields are reset to `None`, which `filetime_set()` serializes as zero so the server leaves them unchanged.

After parsing credentials with `parse_target()`, the script creates an `SMBConnection`, authenticates with either `kerberosLogin()` or `login()`, optionally opens a reference object, opens the target object with minimal access rights, performs `stat` or `touch`, and closes handles and tree connections in `finally` blocks.

## State and Persistence Behavior

State is mostly local CLI and connection state. The only persistent external effect is a remote SMB metadata update through `setInfo()`. The script does not create local files. It keeps selected timestamps as in-memory FILETIME values and depends on the SMB server preserving unspecified timestamp fields when zero is supplied in a set-basic-info request.

## Dependencies and Integration Points

The script integrates with Impacket `smbconnection`, SMB1 structures from `impacket.smb`, SMB2/3 structures from `impacket.smb3` and `impacket.smb3structs`, `parse_target()`, and the shared example logger. It is an executable example rather than a library API, but its helper functions could be reused by other SMB tools.

## Risks and Edge Cases

The file contains duplicate import blocks, including repeated `argparse`, `smbconnection`, and SMB constants, which is harmless but noisy. The `finally` blocks call `closeFile()` and `disconnectTree()` even if `connectTree()` or `openFile()` failed before assigning IDs, so connection errors can mask the original exception with an unbound local error. Timestamp parsing uses local timezone semantics when `fromisoformat()` returns a naive datetime. The `None -> 0` update behavior is protocol-dependent and should be verified against SMB servers before assuming fields are untouched. Directory support relies on `creationOption=0`; server implementations may vary.

## Test Signals

Useful tests mock `SMBConnection` dialects and assert that `filetime_query()` and `filetime_set()` select the expected info classes and field names for SMB1 versus SMB2. Integration tests should cover `stat`, timestamp-based `touch`, reference-based `touch`, validation mode, Kerberos/hash/no-password paths, malformed timestamp input, missing action, and failure during open/close cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/filetime.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/findDelegation.py -->
# sources/user-network-fs/impacket/examples/findDelegation.py

## Purpose

`findDelegation.py` queries Active Directory LDAP data to report unconstrained delegation, constrained delegation with or without protocol transition, and resource-based constrained delegation (RBCD). It helps identify accounts and systems whose delegation settings create lateral movement paths, including cross-domain targeting through `-target-domain`.

## Important APIs, Types, and Functions

`checkIfSPNExists(ldapConnection, sAMAccountName, rights)` searches for either `HOST/<account>` or a delegated SPN and returns `Yes`, `No`, or `-`. `FindDelegation.printTable()` formats fixed-width output. `FindDelegation.__init__()` stores credentials, Kerberos settings, KDC host/IP, disabled-user filtering, requested account filtering, and builds the LDAP base DN from the target domain. `FindDelegation.run()` performs LDAP login, builds the delegation search filter, parses returned entries, resolves RBCD security descriptors, and prints result rows.

## Control Flow

CLI parsing uses `parse_identity()` for `domain[/username[:password]]`, initializes logging, determines the query domain, and instantiates `FindDelegation`. `run()` calls `ldap_login()` with FQDN mode, then searches for entries matching delegation-related LDAP attributes or UAC bits. It filters disabled accounts depending on `-disabled` and optionally narrows by `-user`.

For each `SearchResultEntry`, the script inspects `sAMAccountName`, `userAccountControl`, `objectCategory`, `msDS-AllowedToDelegateTo`, and `msDS-AllowedToActOnBehalfOfOtherIdentity`. RBCD values are parsed as `SR_SECURITY_DESCRIPTOR`; ACE SIDs are converted into a follow-up LDAP OR query so the delegating principals can be named. Results are collected as rows containing account, type, delegation type, rights target, and SPN existence.

## State and Persistence Behavior

The script is read-only against LDAP. It maintains local answer rows and temporary per-entry parsing state. No local cache or output file is written. Cross-domain mode clears explicit KDC host/IP settings because a single custom KDC setting can break referral ticket processing.

## Dependencies and Integration Points

It depends on Impacket LDAP helpers, LDAP ASN.1 result types, SAMR UAC constants, and `ldaptypes.SR_SECURITY_DESCRIPTOR`. It integrates with AD LDAP schema attributes and security descriptor ACL parsing. The output is plain text intended for operator workflows and can be consumed by scripts if column widths remain stable.

## Risks and Edge Cases

The LDAP filter is string-built and only lightly constrained; unusual `sAMAccountName` values supplied through `-user` are not escaped. `printTable()` assumes at least one data row and all rows have the same width, though it is only called when results exist. RBCD parsing assumes a present DACL and does not guard each ACE shape. LDAP search uses `sizeLimit=999` without paging, so large domains can produce incomplete results. Attribute order assumptions appear in the RBCD follow-up response when reading `attributes[0]` and `attributes[1]`.

## Test Signals

Tests should mock LDAP search responses for each delegation type, disabled filtering, target-user filtering, empty results, and `sizeLimitExceeded` handling. RBCD tests should include multiple ACEs, missing DACLs, disabled delegating accounts, and SPN-existence lookups. Integration signals are successful LDAP bind with NTLM, Kerberos, hashes, AES keys, and cross-domain query behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/findDelegation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/getArch.py -->
# sources/user-network-fs/impacket/examples/getArch.py

## Purpose

`getArch.py` remotely infers whether Windows targets are 32-bit or 64-bit by attempting to bind to the endpoint mapper with the NDR64 transfer syntax over TCP port 135. It requires no authentication and supports either a single target or a file of targets.

## Important APIs, Types, and Functions

`TARGETARCH` stores CLI options, a machine list, and the NDR64 syntax tuple `('71710533-BEBA-4937-8319-B5DBEF9CCC36', '1.0')`. `TARGETARCH.run()` reads targets, creates `DCERPCTransportFactory` bindings, sets connect timeouts, connects, and calls `dce.bind(MSRPC_UUID_PORTMAP, transfer_syntax=self.NDR64Syntax)`.

## Control Flow

The command validates that `-target` or `-targets` is present, initializes logging, and runs `TARGETARCH`. For each machine, it connects to `ncacn_ip_tcp:<machine>[135]`. If the NDR64 bind fails with `syntaxes_not_supported`, the target is printed as 32-bit. If the bind succeeds, it is printed as 64-bit. Other DCE/RPC or socket errors are logged per target and processing continues.

## State and Persistence Behavior

State is limited to the in-memory target list and transient DCE/RPC connections. No authentication state, local files, or remote changes are produced. The `-targets` file is read line by line and stripped.

## Dependencies and Integration Points

The script uses Impacket DCE/RPC transport, endpoint mapper UUID constants, and `DCERPCException`. It integrates with Windows RPC endpoint mapper behavior documented by Microsoft. It is intentionally not reliable for Samba and has unknown macOS behavior.

## Risks and Edge Cases

The architecture inference depends on endpoint mapper transfer-syntax behavior, not an explicit OS architecture API. Firewalls, non-Windows RPC stacks, Samba, port filtering, or endpoint mapper hardening can lead to errors or misleading output. Input files are not de-duplicated and blank lines become connection attempts. Only the substring `syntaxes_not_supported` is treated as a 32-bit signal.

## Test Signals

Unit tests can mock DCE bind outcomes for success, `syntaxes_not_supported`, and unrelated failures. Integration tests need known 32-bit and 64-bit Windows systems or captured DCE/RPC behavior. CLI tests should cover target file parsing, timeout propagation, missing-target validation, and continued processing after one target fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/getArch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/getPac.py -->
# sources/user-network-fs/impacket/examples/getPac.py

## Purpose

`getPac.py` obtains and prints the Privilege Attribute Certificate (PAC) for a target user using a normal authenticated account. It combines Kerberos S4U2Self with user-to-user authentication so the returned ticket can be decrypted and the PAC authorization data can be decoded.

## Important APIs, Types, and Functions

`S4U2SELF.printPac(data)` decodes an `EncTicketPart`, extracts `AD_IF_RELEVANT`, parses `PACTYPE`, walks `PAC_INFO_BUFFER` entries, and decodes known PAC buffer types including `KERB_VALIDATION_INFO`, `PAC_CLIENT_INFO`, server and KDC checksums, and UPN/DNS info. Unknown buffers are hex-dumped.

`S4U2SELF.__init__()` stores the authenticated account, domain, target user, and optional LM/NT hashes. `S4U2SELF.dump()` requests a TGT with `getKerberosTGT()`, manually builds an AP-REQ and TGS-REQ with `PA_FOR_USER_ENC`, sets `enc_tkt_in_skey`, embeds the account TGT as an additional ticket, sends the request with `sendReceive()`, decrypts the returned ticket, and passes the plaintext ticket to `printPac()`.

## Control Flow

The CLI requires credentials and `-targetUser`. It parses identity and hashes, then runs `S4U2SELF.dump()`. The Kerberos flow is hand-built with pyasn1 structures: TGT acquisition, AP-REQ authenticator encryption using key usage 7, S4U checksum computation over the target user/domain/auth package with HMAC-MD5, TGS request body construction, additional ticket inclusion for U2U, KDC request/response exchange, service ticket decryption, and PAC printing.

## State and Persistence Behavior

The script is read-only from the domain perspective and writes no ccache. It prints PAC contents to stdout and debug logs. In-memory state includes credentials, Kerberos tickets, ciphers, session keys, and decoded PAC structures.

## Dependencies and Integration Points

It depends on Impacket Kerberos ASN.1 types, crypto tables, PAC structures, `getKerberosTGT()`, `sendReceive()`, pyasn1 DER encoding/decoding, and the example logger. It integrates tightly with Kerberos KDC behavior for S4U2Self and U2U.

## Risks and Edge Cases

The script has a library-safety bug: in `dump()`, key derivation references `password` instead of `self.__password`, which works only when the module is executed as `__main__` and a global `password` variable exists. The hash/key handling is RC4-centric and has fragile type checks around `self.__nthash`. PAC parsing assumes expected authorization-data layout and buffer offsets. Because requests are manually assembled, KDC policy differences, encryption-type restrictions, protected users, and domain functional behavior can break the flow. Debug mode can print sensitive ticket and PAC material.

## Test Signals

Tests should cover PAC buffer parsing with captured tickets, unknown buffer hexdump behavior, and key selection with password versus hashes. A regression test should import `S4U2SELF` and call `dump()` with mocked Kerberos functions to catch the global `password` dependency. Integration tests need a lab KDC supporting S4U2Self/U2U and should verify expected PAC fields for a known target user.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/getPac.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/getST.py -->
# sources/user-network-fs/impacket/examples/getST.py

## Purpose

`getST.py` obtains Kerberos service tickets and saves them as ccache files. It supports normal TGS requests, TGT renewal, S4U2Self/S4U2Proxy constrained delegation, resource-based constrained delegation with an additional ticket, user-to-user mode in S4U flows, alternate service-name rewriting, forced forwardable-ticket modification for CVE-2020-17049 style testing, and DMSA key package extraction.

## Important APIs, Types, and Functions

`GETST.__init__()` stores credentials, hashes, AES key, KDC host, S4U flags, additional ticket path, DMSA mode, and output-name state. `saveTicket(ticket, sessionKey)` builds a `CCache` from a TGS, optionally rewrites the ticket service principal and ccache credential server when `-altservice` is used, and saves `<user-or-impersonated>@<service>.ccache`.

`doS4U2ProxyWithAdditionalTicket()` loads an existing ccache service ticket, optionally rewrites its forwardable flag by decrypting and re-encrypting the ticket, then builds an S4U2Proxy TGS-REQ with `PA_PAC_OPTIONS.resource_based_constrained_delegation`.

`doS4U()` builds S4U2Self padata using either traditional `PA_FOR_USER_ENC` HMAC-MD5 or DMSA `PA_S4U_X509_USER`, optionally requests U2U, optionally extracts `KERB_DMSA_KEY_PACKAGE`, and then either returns the S4U2Self ticket or performs S4U2Proxy. `run()` chooses cached TGT, fresh TGT, normal TGS, renew, S4U with additional ticket, or S4U without additional ticket.

## Control Flow

The CLI validates combinations: `-spn` is required unless `-self` is set, `-impersonate` is required for S4U2Self-only and additional-ticket modes, and `-altservice` in self-only mode must include service class and hostname. Identity parsing then feeds `GETST.run()`.

`run()` first tries `CCache.parseFile()` for a TGT. If none exists, it requests one with `getKerberosTGT()`. Without `-impersonate`, it calls `getKerberosTGS()` for the requested SPN or renews the TGT. With impersonation, it runs S4U logic. S4U2Proxy paths construct AP-REQ authenticators, KDC option flags, SPN principals, additional tickets, and encryption-type lists manually, then call `sendReceive()`.

## State and Persistence Behavior

The primary persistent output is a ccache file in the current directory. The script also reads existing ccaches from `KRB5CCNAME` through Impacket and reads an additional ticket ccache when requested. It mutates in-memory tickets for alternate service names and forced forwardable flags before saving or forwarding them. DMSA mode logs extracted current and previous keys.

## Dependencies and Integration Points

Dependencies include Impacket Kerberos ASN.1, ccache, crypto, NTLM hash helpers, pyasn1, and the example logger. Integration points are KDC AS/TGS exchanges, existing Kerberos credential caches, ccache consumers such as SMB/WMI tools, and AD delegation policy.

## Risks and Edge Cases

This is security-sensitive code that can print or save reusable tickets and keys. `-force-forwardable` requires correct account keys; wrong hashes/AES keys cause decrypt/re-encrypt failure. Alternate service rewriting changes ticket metadata without changing the encrypted ticket server name semantics expected by all services, so compatibility varies. Error handling catches broad exceptions and may return without a nonzero exit. DMSA handling returns early if no encrypted padata exists, which can skip ticket saving. Manual ASN.1 construction is brittle across KDC policy changes. The condition checking `options.u2u is not None` is always true for argparse booleans, so its intended validation is weaker than written.

## Test Signals

Unit tests should mock Kerberos responses and validate padata construction, KDC option flags, ccache naming, altservice rewrite cases, and parser validation. Regression tests should cover imported use, additional-ticket loading errors, `-self` without SPN, `-force-forwardable` key selection for RC4 and AES, and DMSA no-key-package behavior. Integration tests need an AD lab with normal SPN issuance, constrained delegation, RBCD, U2U, and renewal cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/getST.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/getTGT.py -->
# sources/user-network-fs/impacket/examples/getTGT.py

## Purpose

`getTGT.py` requests a Kerberos TGT, or optionally a service ticket directly through AS-REQ via `-service`, and saves the result as a ccache file. It supports password, NTLM hashes, AES key, KDC IP override, and configurable Kerberos principal name type.

## Important APIs, Types, and Functions

`GETTGT.__init__()` stores the target username, password, domain, hashes, AES key, KDC host, requested service, and options. `saveTicket(ticket, sessionKey)` creates a `CCache`, populates it with `fromTGT()`, and saves `<username>.ccache`. `run()` builds a `Principal`, calls `getKerberosTGT()` with credentials and optional `serverName`, then saves the ticket.

## Control Flow

The CLI parses `[domain/]username[:password]`, initializes logging, prompts for a password when needed, validates a domain and `-principalType`, then executes `GETTGT.run()`. Hashes are split into LM/NT strings and converted with `unhexlify()` at the Kerberos call boundary. The `-service` option is passed as `serverName`, enabling AS-REQ service-ticket style requests supported by the underlying Impacket function.

## State and Persistence Behavior

The script writes exactly one ccache file named after the username in the current directory. It does not mutate remote state. It may read a password from stdin. Ticket and session key material live in memory until saved.

## Dependencies and Integration Points

It depends on Impacket `getKerberosTGT()`, `CCache`, Kerberos `Principal`, constants, `parse_identity()`, and the shared logger. The output ccache integrates with other Impacket examples and system Kerberos tooling through `KRB5CCNAME`.

## Risks and Edge Cases

`GETTGT.run()` references global `options.principalType` instead of `self.__options.principalType`, so imported or reused class instances depend on a module-level CLI variable. The output filename can collide across domains or overwrite an existing ccache for the same username. `domain is None` is rejected, but an empty string can pass depending on `parse_identity()` behavior. Invalid hash strings fail at `unhexlify()`. The saved ccache uses `oldSessionKey`, matching Impacket convention, but tests should guard that behavior if `getKerberosTGT()` changes.

## Test Signals

Tests should mock `getKerberosTGT()` and `CCache.saveFile()` to verify credential conversion, service forwarding, output naming, and principal type handling. A regression test should instantiate `GETTGT` without global `options` to catch the class/global coupling. Integration tests should request TGTs with password, hashes, AES key, non-default principal type, and `-service`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/getTGT.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/goldenPac.py -->
# sources/user-network-fs/impacket/examples/goldenPac.py

## Purpose

`goldenPac.py` is an MS14-068 exploitation example. It builds a forged PAC with elevated group SIDs, requests Kerberos tickets that include the forged authorization data, obtains a CIFS service ticket, logs into SMB with that ticket, and optionally executes a command through a RemCom/PSEXEC-style service workflow or writes the forged TGT to a ccache.

## Important APIs, Types, and Functions

`RemComMessage` and `RemComResponse` define pipe protocol structures. `PSEXEC.run()` installs or uploads a service executable, opens named pipes, sends command data, starts stdin/stdout/stderr pipe threads, waits for completion, uninstalls the service, and removes copied files. `Pipes`, `RemoteStdOutPipe`, `RemoteStdErrPipe`, `RemoteStdInPipe`, and `RemoteShell` implement the interactive pipe transport and file transfer commands.

`MS14_068` stores target, credentials, hashes, command/copy/write options, domain SID, forest SID, domain controllers, and KDC host. `getGoldenPAC(authTime)` builds `KERB_VALIDATION_INFO`, group memberships, optional forest enterprise admin SID, PAC client info, unkeyed MD5 checksums, and returns encoded authorization data. `getKerberosTGS()` injects that PAC as encrypted authorization data in a TGS-REQ and extracts the returned session key. `getForestSid()`, `getDomainControllers()`, and `getUserSID()` query NRPC, LSAT, DRSUAPI, and SAMR. `exploit()` orchestrates SID discovery, DC selection, vulnerable-ticket generation, CIFS TGS request, SMB Kerberos login, ccache write, and command execution.

## Control Flow

The CLI parses a target identity, command, optional upload file, optional ccache output, DC IP, target IP, and hashes. `exploit()` discovers the user SID and optionally the forest SID/domain controllers. For each candidate DC it requests a PAC-less TGT, decrypts the AS-REP to obtain `authTime`, creates a forged krbtgt TGS with the generated PAC, then requests `cifs/<target>`. Success breaks the loop; failure logs the DC as not vulnerable. On success it builds a TGS dictionary, authenticates SMB with `kerberosLogin(useCache=False)`, and invokes `PSEXEC` unless the command is `None`.

## State and Persistence Behavior

The script can persist a ccache through `-w`, install and remove a remote service, upload and delete a remote file, and execute remote commands. It also opens long-lived named pipes and changes local process state in `RemoteShell` commands such as `lcd`. Global variables such as `dialect` and `LastDataSent` coordinate pipe threads.

## Dependencies and Integration Points

It integrates with Kerberos, PAC, SAMR, LSAT, NRPC, DRSUAPI, SMB, SCM service installation, and Impacket RemCom service helpers. Many imports needed by class methods are performed only inside the `__main__` block, including `transport`, `samr`, Kerberos ASN.1 types, `MD5`, `NDRULONG`, and SAMR constants.

## Risks and Edge Cases

This is exploit code with invasive remote effects. Cleanup is best-effort; service uninstall or copied-file deletion can fail after partial execution. Imported use is fragile because several class methods depend on names imported only in `__main__`, and `PSEXEC` references `sys`, `transport`, `username`, and `domain` outside its constructor scope. Cryptographic behavior intentionally uses unkeyed PAC checksums for vulnerable DCs only. The stdout suppression check compares `LastDataSent > 10`, which is type-incorrect for bytes/strings versus integers. Broad exception handling can hide root causes and continue to the next DC.

## Test Signals

Most validation requires an isolated vulnerable lab. Unit tests can still cover PAC layout generation with fixed SID/RID/authTime, ccache write path mocking, DC selection fallbacks, and service cleanup on exceptions. Static/import tests should instantiate classes without running `__main__` to catch missing global imports. Integration tests should verify no service or uploaded file remains after success and failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/goldenPac.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/karmaSMB.py -->
# sources/user-network-fs/impacket/examples/karmaSMB.py

## Purpose

`karmaSMB.py` runs a deceptive SMB server that responds to any requested share/path with configured file contents. It can serve a default file for all reads or map file extensions to specific payload files. It hooks SMB1 and SMB2 server commands to make arbitrary requested filenames appear to exist while redirecting actual file opens to local payload paths.

## Important APIs, Types, and Functions

`KarmaSMBServer` subclasses `Thread`. Its constructor builds an in-memory SMB server config with IPC$, NETLOGON, and SYSVOL shares, optionally enables SMB2, unregisters dangerous write/delete commands, hooks SMB1 commands and TRANS2 calls, hooks SMB2 tree connect/create/query/read/close commands, and registers an SRVS named pipe.

Key hooks are `findFirst2()`, `smbComNtCreateAndX()`, `queryPathInformation()`, `smb2TreeConnect()`, `smb2Create()`, `smb2QueryDirectory()`, `smb2Read()`, `smb2Close()`, and `smbComTreeConnectAndX()`. `setDefaultFile()` and `setExtensionsConfig()` define the payload mapping.

## Control Flow

The server accepts all SMB tree connects by synthesizing connected-share entries. When a client queries or opens a file, the hook extracts the original requested path, chooses a target local file from the extension map or default, rewrites the request to the local target, and delegates to the original Impacket server handler. Directory search responses are rewritten so returned filenames match the client's requested basename. SMB2 query-directory responses are synthesized with file size and timestamps from the chosen target file. SMB2 close may return `STATUS_USER_SESSION_DELETED` after reads to force clients to refresh cached directory data.

## State and Persistence Behavior

Persistent local state is limited to reading payload/config files. The server does not intentionally write remote data, and it unregisters many SMB write/delete operations. Runtime state includes `defaultFile`, `extensions`, the Impacket server object, SRVS helper thread, and per-connection `MS15011` dictionaries tracking requested file data, find state, and connection-stop behavior.

## Dependencies and Integration Points

It depends on Impacket `smbserver`, SMB1/SMB2 structures, NT status codes, SRVS server support, `ConfigParser`, and local filesystem metadata through `os.stat()`. It binds to `0.0.0.0:445`, so it requires privileges or capabilities on most systems and conflicts with any local SMB service.

## Risks and Edge Cases

The header warns that SMB2 behavior is cache-sensitive when clients request multiple filenames quickly. Write blocking is incomplete by design; only selected commands and access masks are denied. Config parsing assumes each non-comment line contains exactly one `=`. Missing payload files surface later during stat/open handling. The server claims all shares exist, which can surprise clients and logs. Binding to privileged port 445 and serving arbitrary configured files creates operational risk if run on a shared host.

## Test Signals

Tests should exercise extension mapping, default-file fallback, SMB1 open/search rewriting, SMB2 create/query-directory/read/close state transitions, and denied write/delete dispositions. Integration tests should run against Windows and Samba clients for SMB1 and SMB2, verify requested filenames appear while payload bytes match configured files, and ensure write attempts do not modify payload files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/karmaSMB.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/keylistattack.py -->
# sources/user-network-fs/impacket/examples/keylistattack.py

## Purpose

`keylistattack.py` performs the Kerberos KERB-KEY-LIST-REQ attack using an RODC krbtgt number and AES key to recover target account key material without deploying an agent on the target. It can enumerate candidate users over SMB/SAMR or operate on a provided target list.

## Important APIs, Types, and Functions

`KeyListDump.__init__()` stores domain credentials, Kerberos settings, RODC key and number, remote KDC/host settings, enumeration mode, target list, and object handles for SMB, remote operations, and key-list secrets. `connect()` authenticates to SMB with NTLM or Kerberos, allowing a fallback to cached Kerberos tickets when SMB login raises and `KRB5CCNAME` is set. `run()` either enumerates domain users through `RemoteOperations` and `KeyListSecrets` or uses supplied targets, then creates partial TGTs, obtains full TGTs, extracts keys, and prints `domain\user:rid:nthash-like-key`. `getAllDomainUsers()` filters built-in denied RIDs and `krbtgt_` accounts.

## Control Flow

The CLI requires `-rodcNo` and `-rodcKey`. In normal target mode, the target must include `@<KDC>` and valid SMB credentials; the script enumerates allowed users or all users with `-full`. In `LIST` mode, it reads one user or a target file, requires `-kdc`, derives `remoteName` and optionally domain from the FQDN, and skips SMB enumeration. Each target user is converted to a Kerberos `Principal`, passed through `createPartialTGT()`, `getFullTGT()`, and `getKey()`, then printed if a full TGT was returned.

## State and Persistence Behavior

The script writes no files unless stdout is redirected. It reads optional target files and environment variable `KRB5CCNAME`. Remote state is read-only from the script perspective but sends Kerberos requests and may perform SAMR enumeration.

## Dependencies and Integration Points

It depends on Impacket `secretsdump.RemoteOperations`, `secretsdump.KeyListSecrets`, SMB connection handling, Kerberos principals/constants, and `parse_target()`. It integrates with AD KDC/RODC key-list behavior and SAMR domain user enumeration.

## Risks and Edge Cases

Supplying `-full` can be noisy and cause more KDC rejections. LIST-mode target entries from `-t` do not append `:N/A`, while file entries do, so output formatting can differ. `connect()` silently continues after SMB failure when Kerberos cache exists, but later SAMR operations may still fail. There is no explicit cleanup for `RemoteOperations` connections. The printed key format strips the first two characters from `key`, assuming a fixed prefix.

## Test Signals

Tests should mock `KeyListSecrets` to verify partial/full TGT/key call sequencing, LIST parsing, required option validation, domain derivation from `-kdc`, and all-user filtering. Integration tests need an RODC lab and should compare extracted keys for allowed users, denied built-in users, full enumeration, and explicit target-file mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/keylistattack.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/kintercept.py -->
# sources/user-network-fs/impacket/examples/kintercept.py

## Purpose

`kintercept.py` is a TCP interception proxy aimed at Kerberos KDC traffic. It can transparently forward streams or modify Kerberos TGS requests/replies for S4U testing, especially PA-FOR-USER unkeyed checksum cases related to CVE-2018-16860 and CVE-2019-0734.

## Important APIs, Types, and Functions

`process_s4u2else_req(data, impostor)` decodes a `TGS_REQ`, finds `PA_TGS_REQ` and `PA_FOR_USER`, changes the PA-FOR-USER user name to an impostor, recalculates a CRC32 checksum, and returns a re-encoded request. `mod_tgs_rep_user(data, reply_user)` decodes a `TGS_REP` and rewrites the cname.

`InterceptConn` is an `asyncore.dispatcher` that pairs with a peer connection, buffers outbound data, handles half-closed sockets, and forwards bytes. `InterceptKRB5Tcp(process_record_func, arg)` returns a subclass that parses Kerberos TCP record framing and applies a record transformer. `InterceptConnFactory` maps handler names to connection classes. `InterceptServer` listens locally, connects upstream, pairs downstream/upstream dispatchers, and enters `asyncore.loop()`.

## Control Flow

The CLI accepts upstream server/port, local listen address/port, optional request handler, and optional reply handler. On accept, the server creates a downstream connection class and upstream connection class from the factories, links them as peers, and connects upstream to the target KDC. Plain connections forward byte buffers. Kerberos-aware connections accumulate record data, parse the 4-byte big-endian length prefix, transform complete records when possible, rebuild the length prefix, and forward modified or original records.

## State and Persistence Behavior

No filesystem state is used. Each connection pair maintains buffers, EOF flags, socket state, and for Kerberos-aware connections a protocol buffer. The tool can alter live Kerberos messages in transit but does not persist tickets or keys.

## Dependencies and Integration Points

It depends on deprecated Python `asyncore`, sockets, pyasn1 DER handling, Impacket Kerberos ASN.1 structures, principals, constants, and logger setup. It integrates externally with port forwarding, firewall redirection, or client configuration that routes KDC TCP traffic through the local listener.

## Risks and Edge Cases

The code has Python 3 bytes/str hazards: it uses `''.join(reversed(str(self.proto_buffer[:4])))` and string concatenation around binary headers/messages, which can corrupt framing or raise type errors. The CRC32 S4U byte array also mixes `impostor` with strings. Handler argument parsing assumes exactly `HANDLER:ARG`. Unknown handler names return `None`, causing failures when called. `asyncore` is deprecated, and the proxy handles only TCP framing, not UDP Kerberos. Message rewriting is intentionally security-sensitive and can invalidate checksums for modern KDCs.

## Test Signals

Tests should feed captured Kerberos TCP records through the returned `InterceptKRB5Tcp` class and assert framing, transformed cname/userName, and fallback forwarding for non-TGS records. Python 3 tests should specifically catch bytes/str failures. Integration tests can run the proxy in front of a lab KDC and verify normal forwarding, request-handler modification, reply-handler modification, partial-record buffering, and half-close behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/kintercept.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/lookupsid.py -->
# sources/user-network-fs/impacket/examples/lookupsid.py

## Purpose

`lookupsid.py` brute-forces RID values through LSARPC lookup calls to enumerate local or domain account names. It connects over SMB named pipe `\pipe\lsarpc` on port 139 or 445 and uses LSA policy information to derive the base SID.

## Important APIs, Types, and Functions

`LSALookupSid.KNOWN_PROTOCOLS` maps SMB ports to LSARPC string bindings. `__init__()` stores credentials, hashes, port, maximum RID, domain SID mode, and Kerberos flag. `dump(remoteName, remoteHost)` builds the DCE/RPC transport, applies remote host and credentials, and calls `__bruteForce()`. `__bruteForce()` connects, binds LSAT, opens a policy handle, queries the base SID, batches candidate SIDs, calls `hLsarLookupSids()`, and prints mapped names.

## Control Flow

The CLI parses target, optional max RID, connection port, `-domain-sids`, and authentication settings. `parse_target()` provides credentials and remote name; the script prompts for a password when needed and sets `target_ip` default. Batches of 1000 RIDs are generated from `0` through `maxRid`. `STATUS_NONE_MAPPED` skips a batch; `STATUS_SOME_NOT_MAPPED` still yields a packet with partial names; unknown SID uses are suppressed.

## State and Persistence Behavior

The script is read-only and writes only stdout/log output. It maintains local batch counters and DCE connection state, then disconnects after enumeration.

## Dependencies and Integration Points

It depends on Impacket DCE/RPC transport, LSAT/LSAD helpers, SAMR `SID_NAME_USE`, `MAXIMUM_ALLOWED`, and `DCERPCException`. It integrates with Windows LSA lookup policy and can use NTLM or Kerberos over SMB.

## Risks and Edge Cases

Large `maxRid` values generate many lookup requests and can be noisy. `SIMULTANEOUS=1000` may exceed limits if packet privacy or fragmentation settings are enabled, as comments note. `dump()` catches and re-raises, while the CLI catches all exceptions and suppresses them with `pass`, so failures may only be visible in logs. `entries` is unused. Domain SID mode may forward requests to a DC and behave differently from local account-domain enumeration.

## Test Signals

Tests should mock LSA responses for no mappings, partial mappings, full mappings, host SID versus domain SID selection, and port-specific transport settings. Integration tests should verify output against known local accounts and domain users, Kerberos authentication, redirected stdout encoding, and behavior for max RID boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/lookupsid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/machine_role.py -->
# sources/user-network-fs/impacket/examples/machine_role.py

## Purpose

`machine_role.py` queries MS-DSSP to retrieve a Windows host's machine role and primary domain details. It is intended as a lightweight pre-check for workflows that need to know whether a target is a workstation, member server, backup DC, or primary DC.

## Important APIs, Types, and Functions

`MachineRole.MACHINE_ROLES` maps `dssp.DSROLE_MACHINE_ROLE` enum values to human-readable labels. `MachineRole.__init__()` stores NTLM/Kerberos credentials, hashes, AES key, KDC host, and SMB port. `print_info(remoteName, remoteHost)` authenticates, fetches domain information, prints key/value output, and disconnects. `__get_transport()` builds an `ncacn_np:<remote>[\pipe\lsarpc]` transport and binds credentials/Kerberos settings. `__fetch()` calls `hDsRolerGetPrimaryDomainInformation()` and extracts role, NetBIOS domain, DNS domain, forest name, and GUID.

## Control Flow

The CLI parses target and connection/authentication options, prompts for a password when needed, forces Kerberos when `-aesKey` is supplied, defaults target IP to the parsed remote name, instantiates `MachineRole`, and prints fetched information. Authentication errors and fetch errors are logged as critical and exit with status 1.

## State and Persistence Behavior

The script is read-only and writes only stdout/log output. Runtime state is credentials and a transient DCE/RPC connection. No caches or local files are used.

## Dependencies and Integration Points

It depends on Impacket DCE/RPC transport, MS-DSSP helpers, UUID formatting, `parse_target()`, and the example logger. The endpoint is reached over SMB named pipe transport and uses either NTLM or Kerberos authentication.

## Risks and Edge Cases

The string binding uses `\pipe\lsarpc` while binding the DSSP UUID; this relies on the target exposing DSSP through that named pipe path. The role map assumes all returned enum values are known, so unexpected values raise `KeyError`. `__log_and_exit()` exits the process, limiting library reuse. Empty domain strings are allowed for local accounts. There is no explicit `finally` disconnect if printing raises after fetch.

## Test Signals

Tests should mock `hDsRolerGetPrimaryDomainInformation()` for every role enum, validate GUID formatting, and verify transport credential/Kerberos settings. Integration tests should run against standalone, member, and DC hosts on ports 139 and 445, with password, hashes, AES, and ccache-backed Kerberos.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/machine_role.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/mimikatz.py -->
# sources/user-network-fs/impacket/examples/mimikatz.py

## Purpose

`mimikatz.py` is a mini shell for controlling a remote Mimikatz RPC server through Impacket's `mimilib` DCE/RPC interface. It discovers the Mimikatz endpoint, negotiates an encrypted command channel, and sends interactive or file-driven commands.

## Important APIs, Types, and Functions

`MimikatzShell` subclasses `cmd.Cmd`. Its constructor performs a Diffie-Hellman exchange with `mimilib.hMimiBind()`, derives a 16-byte RC4 key from the shared secret, and stores the remote context handle. `default(line)` UTF-16LE encodes the command, encrypts it with ARC4, calls `hMimiCommand()`, decrypts the encrypted result, and prints it. `do_shell()` runs a local OS command. `do_help()` sends the Mimikatz `::` help command. `main()` handles endpoint discovery, authentication, binding, shell creation, and command-file execution.

## Control Flow

The script first tries authenticated SMB named-pipe endpoint mapper access at `\pipe\epmapper`, with packet privacy and optional Kerberos/GSS negotiate. If Mimikatz is not registered on named pipes, or no username was supplied, it falls back to TCP endpoint mapping. After binding to `MSRPC_UUID_MIMIKATZ`, it creates `MimikatzShell`. With `-file`, non-comment lines are executed sequentially; otherwise an interactive prompt starts.

## State and Persistence Behavior

The script stores the derived RC4 key, remote Mimikatz handle, last local shell output, and DCE connection. It writes no local files by itself, but remote Mimikatz commands can have arbitrary effects depending on the server. It may reuse an SMB connection from endpoint mapping for the final bind.

## Dependencies and Integration Points

It depends on `Cryptodome.Cipher.ARC4`, Impacket EPM, `mimilib`, DCE/RPC transport, RPC privacy/auth constants, and `parse_target()`. It integrates with a separately deployed Mimikatz RPC server exposing the expected UUID.

## Risks and Edge Cases

This is highly sensitive operational tooling. If pycryptodomex is missing, the import handler logs warnings but does not exit, so later ARC4 use can fail. Endpoint discovery has multiple credential setup calls, including a second `set_credentials()` without AES key in the fallback path. Command files skip lines whose first character is `#`, but blank lines can raise indexing errors. Local `shell` commands execute on the operator machine, not the target. Debug logging may expose connection failures and details useful to attackers.

## Test Signals

Tests should mock `mimilib` bind/command calls to verify RC4 key derivation ordering, command encoding/encryption, decrypted output, file command handling, and endpoint fallback logic. Integration tests require a controlled Mimikatz RPC server and should verify SMB named-pipe binding, TCP fallback, Kerberos mode, packet privacy, and command-file behavior with comments and blank lines.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/mimikatz.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/mqtt_check.py -->
# sources/user-network-fs/impacket/examples/mqtt_check.py

## Purpose

`mqtt_check.py` is a small MQTT login-check example. It connects to a target broker with optional username/password, optional client ID, optional SSL, and reports a successful connection acknowledgment.

## Important APIs, Types, and Functions

`MQTT_LOGIN.__init__()` stores parsed target, credentials, and options, converting an empty username to `None`. `MQTT_LOGIN.run()` constructs `MQTTConnection(target, port, ssl)`, chooses a client ID (`' '` when none is supplied), calls `connect(clientId, username, password)`, and logs `CONNECT_ACK_ERROR_MSGS[0]`.

## Control Flow

The CLI parses a target in Impacket target syntax, `-client-id`, `-ssl`, `-port`, and logging flags. `parse_target()` extracts username/password/address and ignores the domain for MQTT. The script initializes logging, creates `MQTT_LOGIN`, runs it, and logs exceptions with optional traceback in debug mode.

## State and Persistence Behavior

No local or remote persistence is used beyond the MQTT connection attempt. Credentials are held in memory. The script writes only logs.

## Dependencies and Integration Points

It depends on Impacket `MQTTConnection`, `CONNECT_ACK_ERROR_MSGS`, `parse_target()`, and the example logger. It integrates with MQTT brokers over plain TCP or SSL/TLS and uses Impacket's MQTT packet implementation rather than a full client loop.

## Risks and Edge Cases

The default client ID is a single space even though the help says default random; this may not behave as expected on strict brokers. Only success code `0` is logged after `connect()` returns; nonzero CONNACK handling is delegated to `MQTTConnection`. There is no timeout option, no certificate validation configuration, and no disconnect call. The target syntax supports a domain component that is ignored.

## Test Signals

Tests should mock `MQTTConnection.connect()` to verify username `'' -> None`, port/SSL propagation, client ID selection, and exception logging. Integration tests should cover anonymous login, username/password login, failed CONNACK codes, TLS brokers, invalid ports, and brokers requiring non-empty unique client IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/mqtt_check.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/mssqlclient.py -->
# sources/user-network-fs/impacket/examples/mssqlclient.py

## Purpose

`mssqlclient.py` is an interactive or scripted Microsoft SQL Server TDS client. It authenticates to MSSQL with SQL authentication, Windows authentication, hashes, Kerberos, or AES key support, then exposes Impacket's SQL shell for queries and administrative commands.

## Important APIs, Types, and Functions

The script is CLI-only. It constructs `tds.MSSQL(target_ip, port, remoteName, workstation_id, application_name, client_interface_name)`, calls `connect()`, authenticates with `kerberosLogin()` or `login()`, prints server replies, and on success creates `SQLSHELL(ms_sql, show_queries)`. Commands can come from `-file`, `-command`, or the interactive shell.

## Control Flow

After parsing target and options, the script prompts for a password when needed, defaults `target_ip`, forces Kerberos when an AES key is provided, and opens the MSSQL TCP connection. Authentication exceptions are logged and set `res=False`. If authentication succeeds, commands are replayed in order from file or CLI, otherwise `cmdloop()` starts. Finally `disconnect()` is called.

## State and Persistence Behavior

The script does not write local files by itself. It maintains a live TDS connection and an interactive shell object. Remote persistence depends entirely on SQL commands executed by the user or command file. The `-show` flag controls query echoing.

## Dependencies and Integration Points

It depends on Impacket `tds.MSSQL`, `examples.mssqlshell.SQLSHELL`, `parse_target()`, and logger setup. It integrates with SQL Server TDS on port 1433 by default, Windows authentication, Kerberos KDCs, and SQL shell helper commands.

## Risks and Edge Cases

`disconnect()` is called after the shell path, but an exception raised before that point can skip cleanup. `-command` uses `argparse` `extend` with `nargs='*'`, so shell quoting affects command grouping. Password prompting is skipped when AES or hashes are supplied. Query execution can have arbitrary remote database effects. The code does not wrap `ms_sql.connect()` in the authentication try block.

## Test Signals

Tests should mock `tds.MSSQL` and `SQLSHELL` to verify connection parameters, login mode selection, command-file replay, command-list replay, interactive fallback, and disconnect on normal paths. Integration tests should cover SQL auth, Windows auth, Kerberos auth, database selection, custom client properties, failed logins, and SSL/TDS negotiation behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/mssqlclient.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/mssqlinstance.py -->
# sources/user-network-fs/impacket/examples/mssqlinstance.py

## Purpose

`mssqlinstance.py` queries the SQL Server Browser service using Impacket's MC-SQLR support and prints MSSQL instance metadata advertised by a target host.

## Important APIs, Types, and Functions

The script is CLI-only. It constructs `tds.MSSQL(options.host)`, calls `getInstances(timeout)`, and prints either `No MSSQL Instances found` or each returned instance dictionary as `key:value` lines with an instance index in the logs.

## Control Flow

The CLI accepts host, timeout, debug, and timestamp flags. After logging initialization, it sends the instance discovery request through `MSSQL.getInstances()`. The response is treated as a list of dictionaries and printed in returned key order.

## State and Persistence Behavior

No persistence is used. The script sends a discovery request and writes stdout/log output only.

## Dependencies and Integration Points

It depends on Impacket `tds.MSSQL` and the example logger. It integrates with SQL Server Browser / MC-SQLR discovery, normally over UDP 1434 as implemented by Impacket.

## Risks and Edge Cases

There is no exception wrapper around discovery, so network or parsing failures can terminate with a traceback depending on logging/debug context. Timeout is parsed as an integer only at call time. Returned instance dictionaries are printed without stable key sorting, which can vary by parser behavior. Firewalls often block SQL Browser discovery, producing empty results even when SQL Server is reachable on a fixed port.

## Test Signals

Tests should mock `getInstances()` for empty, single-instance, multi-instance, timeout, and malformed-return cases. Integration tests should query hosts with default and named SQL instances, blocked UDP discovery, and custom timeout values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/mssqlinstance.py -->
