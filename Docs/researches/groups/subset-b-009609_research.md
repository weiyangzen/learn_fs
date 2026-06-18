# Research Group subset-b-009609

Grouped research for selected Impacket example scripts under `sources/user-network-fs/impacket/examples`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/net.py -->
# sources/user-network-fs/impacket/examples/net.py

## Purpose

`net.py` is an Impacket alternative to Windows `net.exe` for remote account and group administration over SMB-backed DCE/RPC. It exposes `user`, `computer`, `group`, and `localgroup` subcommands that enumerate, query, create, delete, enable/disable, and modify membership for SAM objects on a remote host or domain controller.

## Important APIs, Types, and Functions

The core abstractions are `LsaTranslator`, `SamrObject`, `User`, `Computer`, `Group`, `Localgroup`, and `Net`. `LsaTranslator` binds to `\pipe\lsarpc` and wraps `hLsarLookupNames3` and `hLsarLookupSids2` for SID/name conversion. `SamrObject` binds to `\pipe\samr`, opens builtin or account domains, resolves RIDs, and opens SAMR user, group, or alias handles.

`User` implements `Enumerate`, `Query`, `Create`, `Remove`, and `SetUserAccountControl`; `Computer` reuses `User` with workstation/server trust account flags. `Group` calls `hSamrEnumerateGroupsInDomain`, `hSamrGetMembersInGroup`, `hSamrAddMemberToGroup`, and `hSamrRemoveMemberFromGroup`. `Localgroup` switches to builtin aliases and uses SID-based `hSamrGetMembersInAlias`, `hSamrAddMemberToAlias`, and `hSamrRemoveMemberFromAlias`.

The `Net` facade parses credentials and action options, creates an `SMBConnection`, logs in with NTLM or Kerberos, dispatches to an action class by capitalizing the subcommand name, and formats account details.

## Control Flow

Command-line parsing builds a required subparser for the target object type and validates that `-name` accompanies join/unjoin and `-newPasswd` accompanies create. `parse_target` extracts domain, username, password, and address; missing passwords are prompted unless hashes, AES, Kerberos cache, or no-pass mode are selected. `Net.run()` connects, instantiates the selected action object, then executes exactly one operation by option precedence: create, remove, enable, disable, join, unjoin, query by name, or enumerate.

Querying a user is the richest path: it opens the account domain, retrieves `UserAllInformation`, collects global group RIDs, converts them to names, then reopens the builtin domain to resolve local alias memberships from constructed SID arrays.

## State and Persistence Behavior

The script mutates remote SAM state for create/delete, account-control, and membership operations. It stores only transient handles and connection state locally. SAMR domain handles are cached inside `SamrObject` but closed after operations. No local files are written. Passwords and hashes exist in process memory, and created users/computers are enabled after password setup.

## Dependencies and Integration Points

Integration points are `impacket.smbconnection.SMBConnection`, DCE/RPC transport factories, SAMR (`impacket.dcerpc.v5.samr`), LSAD/LSAT, `parse_target`, and the shared Impacket example logger. The script depends on remote named pipes `samr` and `lsarpc`, SMB port 139 or 445, and the caller having sufficient account-management privileges.

## Risks and Edge Cases

`__get_action_class()` resolves classes dynamically from the subcommand name, so parser choices are the main guard against unexpected dispatch. `User._hEnableAccount()` toggles the disabled bit with XOR; if called for an already-enabled account, it would set the disabled bit, although the public flow labels it as enable. Domain selection uses a fixed enumerated-domain index for builtin versus account domains, which can be brittle if server ordering differs. Several `STATUS_MORE_ENTRIES` paths ignore pagination beyond the first response. Group/localgroup option help strings are swapped, and success messages contain typos but not behavioral issues.

## Test Signals

Useful tests include parser validation for missing `-name` and `-newPasswd`, mocked SAMR/LSAT calls for class dispatch and handle closure, enumeration when SAMR raises `STATUS_MORE_ENTRIES`, user query formatting for never-expiring FILETIME values, and integration tests against a disposable AD lab for create/remove, enable/disable, and domain versus builtin membership changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/net.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/netview.py -->
# sources/user-network-fs/impacket/examples/netview.py

## Purpose

`netview.py` continuously monitors SMB reachable domain machines for remote sessions and locally logged-in users. It can discover computers from SAMR, import target lists, filter reported users, and loop with a background aliveness checker so hosts that go down can be retried later.

## Important APIs, Types, and Functions

Global `machinesAliveQueue` and `machinesDownQueue` coordinate the aliveness thread with the polling loop. `checkMachines()` probes TCP/445, records the local source IP used for filtering self-sessions, and moves reachable machines into the alive queue. `USERENUM` owns credentials, target lists, filter users, live DCE handles, and connection budget.

`getDomainMachines()` binds to `\samr` with `transport.SMBTransport`, calls `hSamrEnumerateUsersInDomain` for `USER_WORKSTATION_TRUST_ACCOUNT`, and strips trailing `$` from machine accounts. `getSessions()` binds or reuses `\PIPE\srvsvc` and calls `srvs.hNetrSessionEnum` level 10. `getLoggedIn()` binds or reuses `\PIPE\wkssvc` and calls `wkst.hNetrWkstaUserEnum` level 1.

## Control Flow

Main parses an identity with `parse_identity`, initializes logging, builds `USERENUM`, and calls `run()`. `run()` resolves targets, builds optional user filters, starts `checkMachines()` unless `-noloop` is set, then repeatedly drains new alive machines into `self.__targets`. Each active target is polled for server sessions and local workstation users. On selected errors, targets are removed permanently or queued back as down; in single-pass mode, the loop exits after one scan.

Session tracking compares current RPC results with prior `Sessions` and `LoggedIn` collections. New entries produce “logged from host” or “logged in LOCALLY” messages; missing entries produce logoff messages. Filtering is applied only at reporting time, not collection time.

## State and Persistence Behavior

Local state is in-memory only: target dictionaries hold cached SRVS/WKST DCE objects, admin capability, prior sessions, and local logon sets. The script keeps remote RPC connections open until the `-max-connections` budget is exhausted, after which it disconnects new handles. No files are written except optional reads from user or target list inputs. Remote state is read-only.

## Dependencies and Integration Points

The script integrates with SAMR for domain machine discovery, SRVS for session enumeration, WKST for local user enumeration, `socket.create_connection` for liveness, and Impacket SMB/DCE transports for NTLM or Kerberos. It requires NetBIOS/FQDN resolution for domain machines and enough privileges for the SRVS/WKST calls, especially local logon enumeration.

## Risks and Edge Cases

`checkMachines()` mutates `deadMachines` while iterating over it, which can skip entries. The global `myIP` is set from the last successful probe and may not match all target paths on multi-homed hosts. In `getLoggedIn()`, `elif str(e).upper().find('ACCESS_DENIED'):` is truthy for `-1`, so many non-broken-pipe exceptions can be treated as access denied. Connection budget is shared but not locked. Removing list entries while enumerating previous sessions can skip adjacent removed sessions.

## Test Signals

Test with mocked queues and socket failures for aliveness transitions, SAMR pagination for machine discovery, SRVS/WKST mocked responses for login/logoff delta detection, filter file handling, single-pass termination, broken-pipe reconnection, and access-denied handling. A lab integration signal is stable reporting against a Windows host with remote SMB sessions and a non-admin account.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/netview.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ntfs-read.py -->
# sources/user-network-fs/impacket/examples/ntfs-read.py

## Purpose

`ntfs-read.py` is a read-only NTFS volume browser and extractor. It opens a raw NTFS volume or image, parses boot-sector, MFT, attribute, index, and filename structures, then provides an interactive mini-shell with `cd`, `ls`, `cat`, `hexdump`, and `get`. It can also extract a single path via `-extract`.

## Important APIs, Types, and Functions

The file defines many `impacket.structure.Structure` models: `NTFS_BPB`, `NTFS_EXTENDED_BPB`, `NTFS_BOOT_SECTOR`, `NTFS_MFT_RECORD`, resident and non-resident attribute records, filename attributes, index headers, index roots/allocation blocks, index entries, data runs, and attribute-list entries.

`Attribute`, `AttributeResident`, and `AttributeNonResident` parse generic attribute headers and data. `AttributeNonResident.parseDataRuns()` decodes NTFS runlists, including sparse runs and signed delta LCNs. `readVCN()` and `read()` translate logical offsets into clustered reads, clamp to `DataSize`, and zero-fill beyond `InitializedSize`. `NonResidentDataAttribute` merges multi-extent `$DATA` streams referenced by `$ATTRIBUTE_LIST`.

`INODE` parses standard information, filename, attribute list, index root, and index allocation; performs NTFS fixups; searches attributes locally and through attribute-list extension records; walks directory index roots and subnodes; resolves path components; and returns data streams. `NTFS` mounts the volume, computes record and index sizes from the BPB, reads the MFT, and returns parsed inodes. `MiniShell` exposes user commands over these primitives.

## Control Flow

`main()` initializes logging, creates `MiniShell(volume)`, and either issues `get <extract>` or enters `cmdloop()`. Mounting reads the boot sector, computes `$MFT` start, creates the root inode, and pre-populates tab completion with `ls`. Directory traversal starts from `$FILE_Root`, searches index entries by uppercase filename, loads child MFT records, and updates the prompt. File reads reject directories, compressed files, and encrypted files, then stream bytes from the default `$DATA` attribute in 40 KiB chunks to stdout, a hexdump callback, or an output file.

## State and Persistence Behavior

The volume is opened read-only (`rb`). Local state includes current inode, current NTFS path, cached completion entries, parsed attributes, and a volume file descriptor. The only write behavior is local extraction through `get`, which writes a file named by the basename of the requested NTFS path in the current local directory. Remote or on-volume state is never modified.

## Dependencies and Integration Points

The script depends on Impacket `Structure` and `hexdump`, Python `cmd`, `ntpath`, `struct`, and raw device/image file access. It is standalone within the Impacket examples but models NTFS structures taken partly from NTFS-3G. It integrates with OS raw device permissions for paths such as `\\.\C:` or `/dev/...`.

## Risks and Edge Cases

The parser is intentionally “quick and dirty” and does not support compressed or encrypted file data. It trusts many on-disk lengths and offsets, so corrupt volumes can cause short reads, parse errors, or loops. Attribute-list extension lookup can recurse through MFT records and may not handle all malformed or unusual split attributes. Directory search assumes NTFS collation ordering but has broad fallback traversal. `do_get()` opens the destination before validating the source, so a failed extraction can leave an empty local file. `main()` calls `sys.exit(1)` after successful completion, which reports failure to callers.

## Test Signals

Useful tests include fixture NTFS images with resident files, non-resident files spanning multiple data runs, sparse files, fragmented `$MFT`, split `$DATA` attributes, large directories using index allocation subnodes, DOS and Win32 filename variants, empty files, and corrupt fixup signatures. CLI smoke tests should cover `-extract`, shell `ls/cd/pwd/cat/hexdump/get`, and rejection of compressed/encrypted flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ntfs-read.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ntlmrelayx.py -->
# sources/user-network-fs/impacket/examples/ntlmrelayx.py

## Purpose

`ntlmrelayx.py` is the top-level orchestration script for Impacket’s NTLM relay framework. It starts one or more inbound relay servers, configures protocol clients and attack modules, processes target selection, optionally exposes a SOCKS proxy and mini-shell, and keeps the process alive while relayed authentications are handled by the imported framework components.

## Important APIs, Types, and Functions

`RELAY_SERVERS` is populated with selected server classes such as `SMBRelayServer`, `HTTPRelayServer`, `WCFRelayServer`, `RAWRelayServer`, `RPCRelayServer`, `WinRMRelayServer`, `WinRMSRelayServer`, `MSSQLRelayServer`, and `RDPRelayServer`. `start_servers()` creates an `NTLMRelayxConfig` for each server, injects `PROTOCOL_CLIENTS`, `PROTOCOL_ATTACKS`, target processors, attack flags, protocol-specific settings, listening ports, WPAD/WebDAV/exploit options, AD CS, shadow credentials, and SCCM options, then starts server threads.

`stop_servers()` shuts down running relay server objects. `MiniShell` exposes runtime commands for target listing, finished attacks, SOCKS relay table display via the local HTTP API, and start/stop of relay listeners.

## Control Flow

The main block builds a large argparse surface grouped by server, SMB, RPC, MSSQL, HTTP, LDAP, IMAP, AD CS, shadow credentials, and SCCM options. After validation, it imports protocol client and attack registries, chooses relay mode from `-t` or `-tf` or reflection mode when no target exists, fills `RELAY_SERVERS` according to disabled server flags, optionally starts a target-file watcher, optionally starts a SOCKS server thread, chooses an interface bind address, and calls `start_servers()`. It then waits on `MiniShell.cmdloop()` when SOCKS mode is enabled or `stdin.read()` otherwise.

## State and Persistence Behavior

Runtime state lives in server threads, target processors, target-file watcher threads, the optional SOCKS server, and the global `RELAY_SERVERS` list. Persistence depends on configured attacks and options: loot and dumps are written under `-lootdir`, encrypted hashes may be written using `-output-file`, certificates or keys may be exported by shadow-credential attacks, and SCCM/LDAP/SMB attacks can modify remote services, LDAP attributes, DNS records, or domain objects through imported attack modules.

## Dependencies and Integration Points

The script is a central integration point for `impacket.examples.ntlmrelayx.servers`, `utils.config.NTLMRelayxConfig`, `utils.targetsutils.TargetsProcessor` and `TargetsFileWatcher`, `servers.socksserver.SOCKS`, protocol clients, and attack registries. It binds network services on privileged ports by default and depends on target-specific protocol support and security settings such as SMB signing, EPA, channel binding, SPN checks, and NTLM policies.

## Risks and Edge Cases

The option surface permits high-impact remote changes, including ACL abuse, DNS record creation, SCCM registration, AD CS enrollment, shadow credentials, and command execution. The SCCM validation assumes `options.target` is present when SCCM flags are set; using SCCM flags without a target can raise before a clean argparse error. `MiniShell.printTable()` assumes at least one row before computing max widths, though callers check item length. `stop_servers()` only shuts down instances of configured relay server classes, not auxiliary watcher or SOCKS threads. Privileged bind failures and partial server startup are mostly delegated to server implementations.

## Test Signals

Test signals include parser validation for incompatible RPC and SCCM options, `parse_listening_ports()` handling of ranges, correct `RELAY_SERVERS` population from disable flags, config setters called with expected values for HTTP, SMB, LDAP, AD CS, SCCM, and SOCKS options, MiniShell filter output, target-file watcher activation, and clean startup/shutdown of selected server classes under mocked network sockets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ntlmrelayx.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/owneredit.py -->
# sources/user-network-fs/impacket/examples/owneredit.py

## Purpose

`owneredit.py` reads or modifies the owner SID (`OwnerSid`) in an Active Directory object’s `nTSecurityDescriptor`. It is intended for scenarios where a caller has rights to inspect or change object ownership and wants to specify both target object and new owner by sAMAccountName, SID, or distinguished name.

## Important APIs, Types, and Functions

`WELL_KNOWN_SIDS` maps common SID strings to display names. `OwnerEdit` stores LDAP session/server objects, target selectors, new-owner selectors, and a `ldapdomaindump.domainDumper` used to locate the domain root. `search_target_principal_security_descriptor()` queries only owner information with `security_descriptor_control(sdflags=0x01)`. `read()` formats the current owner SID and resolves sAMAccountName/DN. `write()` replaces `OwnerSid` in an `ldaptypes.SR_SECURITY_DESCRIPTOR` and writes `nTSecurityDescriptor` with LDAP modify plus the owner-only security descriptor control. `resolveSID()` uses the well-known SID map first and LDAP `objectSid` lookup as fallback.

## Control Flow

`parse_args()` builds authentication, owner, target, and action options. `main()` validates that write has a new owner selector, parses credentials with `parse_identity`, initializes an LDAP or LDAPS session through `init_ldap_session`, constructs `OwnerEdit`, and runs `read` or `read` then `write`. Constructor logic resolves the target security descriptor immediately when target args exist and resolves new owner SID from sAMAccountName or DN when a raw SID was not provided.

## State and Persistence Behavior

Read mode is side-effect free. Write mode persists a changed owner SID to the target object’s `nTSecurityDescriptor` in Active Directory. Local state is only the parsed descriptor and LDAP lookup results. The script does not write files and does not maintain rollback data.

## Dependencies and Integration Points

The script depends on `ldap3`, `ldapdomaindump`, `ldap3.protocol.microsoft.security_descriptor_control`, Impacket `ldaptypes`, and example utilities `init_ldap_session`/`parse_identity`. It integrates with AD LDAP/LDAPS and requires appropriate directory permissions, especially `WRITE_OWNER` or equivalent control over the target.

## Risks and Edge Cases

The constructor condition `if self.new_owner_SID is None and self.new_owner_sAMAccountName is not None or self.new_owner_DN is not None` relies on Python precedence; DN lookup will run even when a SID is also supplied. The DN LDAP filters are not escaped in all paths. `read()` assumes owner SID can be found in LDAP and may fail for built-in or foreign SIDs after logging a well-known mapping. `main()` contains stale restore-action validation for an action that argparse does not expose. Failed writes log LDAP result messages but do not exit non-zero explicitly.

## Test Signals

Useful tests include selector precedence for target by sAMAccountName/SID/DN, new-owner resolution by all supported forms, well-known SID display without LDAP hit, LDAP modify payload preserving the rest of the security descriptor, insufficient-rights and constraint-violation result handling, Kerberos and LDAPS session initialization, and parser failure for write without owner.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/owneredit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ping.py -->
# sources/user-network-fs/impacket/examples/ping.py

## Purpose

`ping.py` is a minimal IPv4 ICMP echo example demonstrating Impacket `ImpactPacket` construction and `ImpactDecoder` parsing. It sends raw ICMP echo requests from a user-supplied source IP to a destination IP and prints matching echo replies.

## Important APIs, Types, and Functions

The script uses `ImpactPacket.IP`, `ImpactPacket.ICMP`, `ImpactPacket.Data`, and `ImpactDecoder.IPDecoder`. It sets IP source and destination addresses, sets ICMP type to `ICMP_ECHO`, attaches a 156-byte payload, and uses `ip.get_packet()` for transmission. Standard-library `socket`, `select`, and `time` implement raw I/O and one-second receive waits.

## Control Flow

At import-time execution, it requires two positional arguments: source and destination IPs. It builds a single IP/ICMP packet object, opens an IPv4 raw ICMP socket with `IP_HDRINCL`, then loops forever. Each iteration increments the ICMP identifier, clears and auto-computes the checksum, sends the packet, waits up to one second for a response, decodes the received IP packet, and prints a reply if source, destination, and ICMP type match expectations.

## State and Persistence Behavior

State is limited to the raw socket and `seq_id` counter. No files or remote state are modified. Network side effects are ICMP echo requests emitted continuously until interrupted.

## Dependencies and Integration Points

It depends on raw socket privileges and Impacket packet classes. It integrates directly with the host networking stack and assumes the caller can choose a source IP meaningful for the selected interface/routing path.

## Risks and Edge Cases

The script runs top-level code on import and has no argparse. It uses ICMP identifier as the sequence label rather than a separate sequence field. It sleeps only after receiving a reply, so unreachable targets can be probed faster than intended. It does not validate that replies correspond to the current identifier beyond printing the received ID, and it does not handle multiple queued packets.

## Test Signals

Test signals include packet field construction with a mocked raw socket, checksum regeneration, decoder handling of synthetic echo replies, argument-count validation, behavior without privileges, and live smoke tests against loopback or a lab host with ICMP enabled and disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ping.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ping6.py -->
# sources/user-network-fs/impacket/examples/ping6.py

## Purpose

`ping6.py` is a minimal IPv6 ICMP echo example. It demonstrates Impacket IPv6 and ICMPv6 packet construction, checksum calculation, raw IPv6 socket use, and ICMPv6 echo reply decoding.

## Important APIs, Types, and Functions

The script imports `IP6.IP6`, `ICMP6.ICMP6.Echo_Request`, `ImpactDecoder.ICMP6Decoder`, and `version.BANNER`. It configures IPv6 source/destination, traffic class, flow label, hop limit, next-header, payload length, and ICMPv6 checksum. It uses an `AF_INET6`, `SOCK_RAW`, `IPPROTO_ICMPV6` socket.

## Control Flow

After printing the Impacket banner and validating two positional arguments, the script creates an IPv6 packet template and a 156-byte payload. It loops forever, increments `seq_id`, creates a fresh echo request, attaches it to the IPv6 packet for metadata and checksum calculation, sends the ICMPv6 packet bytes to the destination, waits up to one second, decodes any response as ICMPv6, and prints payload size and sequence for echo replies.

## State and Persistence Behavior

State is limited to source/destination strings, the IPv6 packet object, payload bytes, raw socket, and sequence counter. There is no persistence. The only side effect is continuous ICMPv6 echo traffic until interrupted.

## Dependencies and Integration Points

It depends on raw ICMPv6 socket privileges, IPv6 routing, and Impacket ICMPv6 support. Unlike IPv4 `ping.py`, it sends `icmp.get_packet()` rather than the full IPv6 packet because the kernel handles IPv6 headers for this socket mode.

## Risks and Edge Cases

Like `ping.py`, it executes at import time and lacks argparse. It sleeps only when a packet is received, so no-reply paths loop aggressively. It does not check reply source, destination, identifier, or matching sequence beyond accepting any ICMPv6 echo reply decoded from the socket. Error messages and ICMPv6 unreachable responses are ignored.

## Test Signals

Useful tests include mocked checksum calculation and `sendto()` payloads, synthetic ICMPv6 echo reply decoding, no-argument usage behavior, raw-socket permission errors, and live loopback tests against `::1` with expected echo replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ping6.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/psexec.py -->
# sources/user-network-fs/impacket/examples/psexec.py

## Purpose

`psexec.py` implements PsExec-like remote command execution using the bundled RemCom service. It authenticates over SMB/RPC, installs a service binary, sends a command over named pipes, and provides an interactive remote shell with upload/download helpers.

## Important APIs, Types, and Functions

`RemComMessage` and `RemComResponse` model the named-pipe protocol structures. `PSEXEC` manages credentials, command, service options, optional executable/file copy, and RPC transport. `PSEXEC.run()` creates an `ncacn_np` binding to `\pipe\svcctl`; `doStuff()` connects, installs `remcomsvc.RemComSvc()` or a user-supplied binary through `serviceinstall.ServiceInstall`, opens `\RemCom_communicaton`, writes the command packet, starts three pipe threads, waits for the response, uninstalls, and cleans copied files.

`Pipes` opens separate SMB connections for each named pipe. `RemoteStdOutPipe` and `RemoteStdErrPipe` read remote output, buffer by prompt/newline, decode with `CODEC`, and suppress echoed commands via global `LastDataSent`. `RemoteStdInPipe` starts `RemoteShell`, whose commands include local shell execution, `lcd`, `lget`, `lput`, and default remote command submission.

## Control Flow

Main parses target, command, copy and binary options, authentication material, keytab, SMB port, service name, and remote binary name. It sets the output codec, parses target credentials, loads keytab keys when requested, prompts for missing password, defaults to `cmd.exe`, constructs `PSEXEC`, and calls `run()`. The remote process lifetime determines when `doStuff()` exits with the RemCom error code.

## State and Persistence Behavior

The script writes significant remote state: a temporary service and executable on an administrative share, optionally a copied file for execution, and named-pipe traffic. It attempts to uninstall the service and delete copied files on both success and error. Locally, `lget` downloads files into the current directory, `lput` reads local files, and keytab loading mutates options for Kerberos.

## Dependencies and Integration Points

Dependencies include SMB, DCE/RPC `svcctl`, Impacket `remcomsvc`, `serviceinstall`, `SMBConnection`, Kerberos keytab support, and Windows administrative shares. It requires service-control-manager access and file write privileges on the target. It integrates with both NTLM and Kerberos flows, preserving SMB dialect for pipe connections.

## Risks and Edge Cases

The tool is high impact: it creates services and executes commands remotely. Cleanup depends on reaching exception handlers and may fail if the process is interrupted or the target disconnects. Global variables `dialect` and `LastDataSent` coordinate threads and can race. Several broad `except` blocks swallow pipe errors, making broken output hard to diagnose. Unicode decoding depends on correct `-codec`. File transfer paths are minimally sanitized and operate relative to the connected share.

## Test Signals

Useful tests include mocked `ServiceInstall` install/uninstall/copy/delete paths, RemCom packet fields, pipe-open retry behavior, stdout/stderr buffering for prompt and newline boundaries, codec fallback warnings, keytab option mutation, command defaulting, and lab integration against a disposable Windows host validating service cleanup after success and failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/psexec.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/raiseChild.py -->
# sources/user-network-fs/impacket/examples/raiseChild.py

## Purpose

`raiseChild.py` automates a child-domain to forest privilege escalation workflow based on golden tickets with ExtraSids. Given child-domain administrator credentials, it discovers forest information, obtains child and parent credential material through DRS replication, builds a forged TGT containing the parent Enterprise Admin SID, optionally writes the ticket to a ccache, and optionally launches a PsExec-like shell on a target host.

## Important APIs, Types, and Functions

The file embeds a streamlined RemCom `PSEXEC` implementation plus pipe and shell classes similar to `psexec.py`, adjusted for Kerberos ticket use. `RetryableGoldenTicketError` marks ticket-building failures that should fall through to another credential method.

`RAISECHILD` is the main coordinator. `getChildInfo()` uses NRPC `hDsrGetDcNameEx` to return child domain and forest names. `getParentSidAndTargetName()` uses LSAT/LSAD to read the parent domain SID and resolve a target RID. `__connectDrds()` establishes DRSUAPI with packet privacy, handles DRSBind epoch negotiation, and locates the NTDS DSA object GUID. `DRSCrackNames()` and `DRSGetNCChanges()` locate and replicate target user objects. `__decryptHash()` decrypts `dBCSPwd` and `unicodePwd`; `__decryptSupplementalInfo()` extracts Kerberos AES keys from supplemental credentials.

`makeGolden()` decodes the AS-REP ticket, decrypts `EncTicketPart` with krbtgt key material, extends lifetime, rewrites PAC validation groups, appends the extra SID, signs the PAC, re-encodes authorization data, and re-encrypts the ticket. `raiseUp()` orders AES, RC4, password, and password-derived RC4 attempts for TGT/TGS acquisition and golden ticket validation.

## Control Flow

Main parses the child-domain identity and optional ticket output, target execution host, target RID, and authentication material. `exploit()` discovers the child and forest names, then `raiseUp()` gets the parent Enterprise Admin SID, dumps child `krbtgt`, obtains a child TGT, forges the golden ticket, requests a CIFS TGS for the parent or execution target, uses the forged ticket to DRS-replicate parent `krbtgt` and target user credentials, and returns target credentials plus tickets. `exploit()` writes a ccache when requested and starts the embedded PSEXEC path when `-target-exec` is present.

## State and Persistence Behavior

Remote read operations include NRPC, LSAT, and DRS replication of credential attributes. The forged ticket exists in memory and can be persisted locally with `-w`. If remote execution is requested, the embedded RemCom service flow writes and removes remote service artifacts and opens named pipes. The script prints recovered LM/NT hashes and Kerberos keys to stdout. Internal state caches DRS handles, partial attribute vectors, domain SID, credential dictionaries, and resolved target names.

## Dependencies and Integration Points

It integrates with Impacket Kerberos, PAC, DRSUAPI, NRPC, LSAT/LSAD, SMB, service installation, and RemCom modules, plus `pyasn1` DER encoders/decoders. It depends on DNS/SMB name resolution across child and forest domains, replication privileges in the child domain, compatible KDC encryption types, and trust behavior that accepts ExtraSids.

## Risks and Edge Cases

This is intentionally offensive and high impact: it extracts credential material, forges long-lived tickets, and can execute commands as a privileged parent-domain account. Name resolution failures are common because it converts IPs to DNS names through anonymous SMB. The embedded pipe code contains a likely bug comparing `LastDataSent > 10` where `LastDataSent` is usually bytes/string. `DRSGetNCChanges()` calls `__connectDrds(creds)` with an argument shape inconsistent with `__connectDrds(domainName, creds)`, though normal flows usually connect earlier through `DRSCrackNames()`. The TGS acquired in `raiseUp()` is not passed into final `kerberosLogin()` in `exploit()`, which may require cache/KDC behavior to compensate. Broad exception handling can leave service artifacts behind.

## Test Signals

Test signals include unit-level PAC mutation and signature verification for RC4/AES krbtgt keys, credential attempt ordering and retry behavior, DRS partial attribute set construction, supplemental credential parsing with malformed properties, LSAT target RID resolution, ccache writing from forged TGT, and lab integration in a disposable multi-domain forest for child krbtgt dump, parent target credential dump, and optional service cleanup after `-target-exec`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/raiseChild.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/rbcd.py -->
# sources/user-network-fs/impacket/examples/rbcd.py

## Purpose

`rbcd.py` reads and edits the `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute on an Active Directory computer account for resource-based constrained delegation workflows. It supports reading current entries, adding one delegate SID, removing one delegate SID, or flushing the attribute.

## Important APIs, Types, and Functions

`create_empty_sd()` builds a self-relative security descriptor with owner `BUILTIN\Administrators`, an empty DACL, and control flags suitable for the RBCD attribute. `create_allow_ace(sid)` creates an access-allowed ACE with mask `983551` (full-control style mask) for the supplied SID.

`RBCD` owns LDAP session/server objects, the `delegate_to` target, resolved `delegate_from` SID, target DN, and a `ldapdomaindump.domainDumper`. `read()`, `write()`, `remove()`, and `flush()` are the public actions. `get_allowed_to_act()` reads the raw attribute, parses it as `ldaptypes.SR_SECURITY_DESCRIPTOR`, logs entries by resolving SIDs, or creates an empty descriptor when the attribute is missing. `get_user_info()` and `get_sid_info()` perform LDAP lookups by sAMAccountName and objectSid.

## Control Flow

`main()` parses identity, delegation arguments, action, LDAP/LDAPS, and authentication options. It requires `-delegate-to` and additionally requires `-delegate-from` for write. After `parse_identity()` and `init_ldap_session()`, it constructs `RBCD` and dispatches to the requested action. Write and remove both resolve source and target, read the current security descriptor, mutate the DACL in memory, then replace the LDAP attribute.

## State and Persistence Behavior

Read mode is non-mutating. Write mode persists a modified binary security descriptor to `msDS-AllowedToActOnBehalfOfOtherIdentity`. Remove persists a descriptor with matching ACEs removed. Flush persists an empty attribute value by replacing it with an empty list. Local state is transient; no local files are written.

## Dependencies and Integration Points

The script depends on `ldap3`, `ldapdomaindump`, Impacket `ldaptypes`, `init_ldap_session`, and `parse_identity`. It integrates with AD LDAP/LDAPS and requires write access to the target computer object’s RBCD attribute. It expects computer account names to include trailing `$` when appropriate.

## Risks and Edge Cases

The CLI does not require `-delegate-from` for `remove`, so `remove(None)` can reach LDAP lookup with a null account. Replacing the full attribute can overwrite concurrent RBCD changes made between read and write. The full-control mask is broad. Empty or malformed descriptors are replaced with a newly constructed descriptor, which may lose nonstandard ACL metadata. Error handling logs LDAP result messages but does not necessarily fail the process. The script relies on sAMAccountName-only lookup; SID/DN direct inputs are left as a TODO.

## Test Signals

Useful tests include empty descriptor creation binary round-trip, ACE SID encoding, read/write/remove/flush LDAP modify payloads, duplicate SID detection, malformed or absent RBCD attribute handling, missing source/target account errors, LDAPS and Kerberos session initialization, and lab validation that S4U2Proxy works only after the expected ACE is present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/rbcd.py -->
