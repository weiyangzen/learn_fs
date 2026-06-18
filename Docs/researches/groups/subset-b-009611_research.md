# subset-b-009611 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ticketer.py -->
# sources/user-network-fs/impacket/examples/ticketer.py

Purpose: `ticketer.py` is an Impacket example that forges Kerberos TGT/TGS tickets and stores them as ccache files. It supports offline golden/silver ticket creation from a supplied krbtgt or service key, KDC-template cloning with `-request`, and a sapphire-ticket mode that uses S4U2Self+U2U to extract an impersonated user's PAC before resigning it.

Important APIs, types, and functions: `TICKETER` owns the workflow. `createBasicValidationInfo()` builds `KERB_VALIDATION_INFO` with user RID, groups, domain SID, logon timestamps, and account flags. `createBasicPac()` creates PAC buffers for logon info, client info, server checksum, private server checksum, and optional UPN/DNS, attributes, and requestor buffers. `createBasicTicket()` either requests a live TGT/TGS template through `getKerberosTGT()`/`getKerberosTGS()` or constructs an `AS_REP`/`TGS_REP` skeleton. `getKerberosS4U2SelfU2U()` manually builds an AP-REQ and TGS-REQ with `PA_FOR_USER_ENC` and `enc_tkt_in_skey`. `customizeTicket()` edits `EncTicketPart`, PAC logon fields, extra SIDs, flags, and reply part timing. `signEncryptTicket()` delegates PAC signing to `pac.sign_pac()`, encrypts the ticket enc-part with key usage 2, encrypts the reply enc-part with usage 3 or 8, and returns the serialized KDC reply plus session key. `saveTicket()` writes or updates `<target>.ccache`.

Control flow: The CLI validates required key material, parses golden versus silver mode from `-spn`, optionally prompts for a template-user password, and then calls `TICKETER.run()`. `run()` creates or requests the base reply, customizes the PAC and ticket body, signs/encrypts the result, and persists it. In request mode, ticket lifetime is copied from the KDC reply through `_extract_reply_ticket_times()`; otherwise the default duration is ten years. Sapphire mode first obtains a U2U ticket, decrypts its PAC using the TGT session key, clears signatures, adds missing modern PAC buffers when requested, then reuses that PAC in the forged ticket.

State and persistence behavior: Runtime state is mostly private fields containing target identity, service/server names, options, optional TGT/cipher/session key, and requested ticket times. Persistent output is a Kerberos ccache named after the target with slashes replaced by dots. `saveTicket()` may read an existing `KRB5CCNAME` ccache, but writes a new local `<target>.ccache`. Live network state is only used in `-request` and sapphire paths; pure offline forging sends no KDC traffic.

Dependencies and integration points: The script integrates deeply with `impacket.krb5.asn1`, `constants`, `crypto`, `pac`, `types`, `kerberosv5`, and `ccache`, plus DCE/RPC SID/NDR structures for PAC content. It relies on `pyasn1` DER encoding/decoding, `Keytab` for service key loading, and the example logger. Its output is consumed by Kerberos-aware Impacket tools and system Kerberos clients through ccache semantics.

Risks: This is high-impact offensive functionality; wrong keys, wrong AES length, or mismatched template encryption causes hard failures. The code depends on a module-level `options` variable inside `loadKeysFromKeytab()`, which makes the method less reusable outside the CLI path. Forged long-lived tickets and extra SIDs are security-sensitive by design. Some PAC and string fields are manually assembled, so alignment, encoding, and checksum ordering regressions can break interoperability. Sapphire mode warns that missing or default `-user-id` can cause KDC rejection.

Test signals: Direct tests should cover RC4/AES128/AES256 offline ticket generation, request-mode lifetime preservation, PAC buffer ordering, UPN/DNS and requestor/attributes toggles, extra SID insertion, keytab loading, and ccache output. The repository has a separate `tests/misc/test_ticketer.py` item, and integration tests need a KDC or recorded fixtures because request and sapphire paths depend on live Kerberos behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/ticketer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/tstool.py -->
# sources/user-network-fs/impacket/examples/tstool.py

Purpose: `tstool.py` is a Terminal Services/RDS remote administration example. It reproduces common Windows TS commands over SMB-backed DCE/RPC: session listing, process listing and termination, session connect/disconnect/logoff, system shutdown events, message boxes, and session shadow invitation retrieval.

Important APIs, types, and functions: `TSHandler` stores credentials, parsed action, Kerberos/hash options, and an `SMBConnection`. `connect()` authenticates to SMB over port 139 or 445. `get_session_list()`, `enumerate_sessions_config()`, and `enumerate_sessions_info()` populate `self.sessions` from `TSTS.TermSrvEnumeration`, `RCMPublic`, and `TermSrvSession`. Action handlers include `do_qwinsta()`, `do_tasklist()`, `do_taskkill()`, `do_tscon()`, `do_tsdiscon()`, `do_logoff()`, `do_shutdown()`, `do_msg()`, and `do_shadow()`. `lookupSids()` opens LSARPC and resolves process SIDs for task listing.

Control flow: The CLI builds subparsers for each action, parses credentials through `parse_target()`, prompts for a password when needed, and calls `TSHandler.run()`. `run()` performs action-specific validation for shutdown flags, connects once over SMB, and dispatches dynamically to `do_<action>`. Listing flows first gather raw session or process records and then format fixed-width output. Mutating flows open the target RPC context, open a session or server handle, issue the corresponding TSTS call, and map common error codes to readable messages. Shadowing calls `RpcShadow2`, checks permission, parses the returned invitation XML, and writes it to the requested file.

State and persistence behavior: In-memory state includes `self.sessions` and `self.sids`, both rebuilt during list operations. Remote state may be changed substantially: processes can be terminated, sessions connected/disconnected/logged off, systems shut down, users messaged, and shadow invitations requested. Local persistence only occurs in `do_shadow()`, which writes the invitation XML to `invite.msrcIncident` or the path supplied with `-file`.

Dependencies and integration points: The tool depends on `impacket.smbconnection`, `impacket.dcerpc.v5.tsts`, `transport`, `lsat`, `lsad`, and RPC auth constants. It integrates with Terminal Services named-pipe endpoints through the TSTS helper classes and with LSARPC for SID-to-name lookup. Kerberos mode reuses SMB Kerberos login and can take AES keys or ccache-backed credentials.

Risks: Many actions are destructive or disruptive, especially `taskkill`, `logoff`, and `shutdown`. The dynamic `getattr(self, 'do_' + action)` dispatch assumes parser action names remain trusted. `lookupSids()` truncates SID resolution to 32 entries, so large process lists may show unresolved SIDs. Several handlers rely on remote RPC exception objects having `error_code`; unexpected exceptions could produce secondary failures. Shadow invitation parsing includes repair heuristics for truncated XML but may silently reject unusual valid data.

Test signals: Useful tests include parser validation for missing action-specific arguments, mocked TSTS session enumeration and formatting, SID lookup fallback on partial mapping, shutdown flag composition, and file output from `do_shadow()`. Integration tests require an RDS-capable Windows target or fixtures for the TSTS RPC response structures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/tstool.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/wmiexec.py -->
# sources/user-network-fs/impacket/examples/wmiexec.py

Purpose: `wmiexec.py` executes commands on a remote Windows host through WMI/DCOM and optionally provides a semi-interactive shell. It uses WMI `Win32_Process.Create()` for execution and, when output is enabled, redirects stdout/stderr to a temporary file on an administrative SMB share that the client retrieves and deletes.

Important APIs, types, and functions: `WMIEXEC` stores credentials, hash/AES/Kerberos options, output mode, share, target host, and shell type. `WMIEXEC.run()` creates an optional `SMBConnection`, creates a `DCOMConnection`, logs into `//./root/cimv2`, obtains `Win32_Process`, and hands control to `RemoteShell`. `RemoteShell` implements local helpers `lcd`, `lget`, `lput`, shell exit handling, drive and directory tracking, command execution, output polling, and PowerShell base64 command wrapping. `load_smbclient_auth_file()` parses smbclient-style `username`, `password`, and `domain` files. `AuthFileSyntaxError` reports auth-file parse errors.

Control flow: The CLI parses target credentials and command arguments, loads optional auth/keytab material, configures COM version and output codec, and rejects unsupported interactive combinations with `-nooutput` or `-silentcommand`. `WMIEXEC.run()` authenticates to SMB unless output is disabled, reports the SMB dialect, starts DCOM, obtains WMI services, and either executes one command or enters `cmdloop()`. `RemoteShell.execute_remote()` builds a `cmd.exe /Q /c` or encoded PowerShell command, appends SMB redirection when output is enabled, calls `Win32_Process.Create()`, and then `get_output()` loops through sharing violations until the output file is readable.

State and persistence behavior: Local state includes the generated `OUTPUT_FILENAME`, current remote working directory, local current directory for helper commands, an output buffer, and the SMB/DCOM connections. Remote transient state includes created processes and a temporary output file under the chosen share; successful output collection deletes that file. `lget` writes downloaded files into the local working directory, and `lput` uploads local files to remote administrative shares. `-nooutput` avoids SMB output persistence and prints process information instead.

Dependencies and integration points: The script uses `SMBConnection`, `DCOMConnection`, WMI COM wrappers, `Keytab`, the Impacket example logger, and `parse_target()`. Kerberos paths integrate with ccache, AES keys, keytabs, and KDC host selection. The shell depends on Windows command processor behavior and administrative share access.

Risks: The tool requires administrative WMI/DCOM privileges and can execute arbitrary remote commands. Output redirection to `\\127.0.0.1\\<share>\\__<time>` leaves forensic artifacts if deletion fails or the process hangs. `OUTPUT_FILENAME` uses `time.time()`, so concurrent sessions are usually distinct but not cryptographically random. `do_lput()` splits arguments on spaces and cannot handle many quoted paths. `get_output()` can wait indefinitely on persistent sharing violations. `CODEC` defaults to local stdout encoding and may garble target output unless overridden.

Test signals: Unit tests can cover auth-file parsing, codec fallback, command construction for cmd versus PowerShell, path normalization for `cd`, and rejection of invalid CLI mode combinations. Integration coverage needs a mocked or real WMI/DCOM service plus SMB file operations, especially for output polling, reconnect handling, and cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/wmiexec.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/wmipersist.py -->
# sources/user-network-fs/impacket/examples/wmipersist.py

Purpose: `wmipersist.py` installs or removes a permanent WMI event consumer, event filter, timer instruction, and filter-to-consumer binding in `root/subscription`. The installed consumer executes supplied VBScript when a WQL event filter or interval timer fires.

Important APIs, types, and functions: `WMIPERSISTENCE` stores credentials, NTLM hashes, and CLI options. `checkError()` reads the WMI call status, maps known `WBEMSTATUS` values, and logs success or failure. `run()` creates the DCOM/WMI connection, logs into `//./root/subscription`, and branches on `INSTALL` versus `REMOVE`. Install mode spawns `ActiveScriptEventConsumer`, `__EventFilter`, optional `__IntervalTimerInstruction`, and `__FilterToConsumerBinding` instances. Remove mode deletes those instances by constructed WMI object paths.

Control flow: The CLI validates COM version, install action requirements, and mutually exclusive `-filter`/`-timer`. It parses target credentials, prompts for a password when needed, enables Kerberos when `-aesKey` is supplied, instantiates `WMIPERSISTENCE`, and calls `run()`. Install mode reads the entire VBS file, creates the consumer with `ScriptingEngine='VBScript'`, builds either a caller-provided WQL filter in `root\\cimv2` or a timer-backed filter in `root\\subscription`, and links the filter to the consumer. Remove mode attempts to delete all related objects for the name, including timer objects even if the original install was filter-based.

State and persistence behavior: The important state is remote and persistent: WMI subscription objects remain on the target until removed and can keep executing the script after the tool exits. Local state is limited to credentials and the opened VBS file. DCOM is disconnected after object creation/removal.

Dependencies and integration points: The script uses Impacket DCOM/WMI wrappers, `COMVERSION`, `parse_target()`, the example logger, and WMI class/object path semantics. It integrates with Windows WMI permanent eventing infrastructure and relies on administrative permissions in `root/subscription`.

Risks: This is explicitly persistence-oriented functionality; installed consumers may execute repeatedly and invisibly based on event or timer triggers. Names and WQL filters are interpolated into WMI paths and queries, so malformed names can break cleanup. The implementation references the global `options` variable inside `run()` instead of consistently using `self.__options`, reducing reusability. CreatorSID is hard-coded. Remove mode logs individual failures but does not roll back partial deletes.

Test signals: Tests should mock WMI service objects and verify install object fields, timer versus filter branching, binding paths, remove paths, and `checkError()` status mapping. CLI tests should cover mutual exclusion of `-filter` and `-timer`, password prompting conditions, COM version validation, and Kerberos enabling with AES keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/wmipersist.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/examples/wmiquery.py -->
# sources/user-network-fs/impacket/examples/wmiquery.py

Purpose: `wmiquery.py` is an interactive and batch WQL client for Windows Management Instrumentation over DCOM. It executes arbitrary WQL queries, prints tabular result properties, and describes WMI classes through `GetObject()`.

Important APIs, types, and functions: The `WMIQUERY` command class is defined inside the `__main__` block. It implements `do_describe()`, `default()` for WQL query execution, `printReply()` for enumerator output, `do_lcd()`, local shell execution via `do_shell()`, and `do_exit()`. The CLI establishes `DCOMConnection`, obtains `IWbemLevel1Login`, logs into a configurable namespace, and optionally adjusts RPC auth level to packet integrity or privacy.

Control flow: The CLI parses credentials, namespace, optional command file, COM version, and auth-level controls. It prompts for a password when necessary, splits hashes, connects to DCOM with Kerberos or NTLM, obtains WMI services, and releases the login interface. Without `-file`, it enters a WQL prompt. With `-file`, it echoes each command and executes it through `onecmd()`. Query results are consumed by repeated `iEnum.Next()` calls until an exception containing `S_FALSE` marks enumeration completion.

State and persistence behavior: Persistent remote state is not intentionally modified by this script; it is query/describe focused. Local state is the command shell, current local directory if `lcd` is used, and optional batch file handle. The `!` command can execute arbitrary local shell commands, so local side effects are possible.

Dependencies and integration points: The script uses Impacket DCOM/WMI wrappers, RPC auth constants, `parse_target()`, and the example logger. It integrates with any WMI namespace that the credentials can access; some namespaces may require `-rpc-auth-level privacy`.

Risks: Arbitrary WQL execution can be expensive or reveal sensitive host data. `do_describe()` indexes `sClass[-1:]` safely for empty strings but still sends empty class names to WMI if the user enters blank describe input. `printReply()` uses exception string matching for `S_FALSE`, which is brittle. Local `!` commands are intentionally powerful and can affect the operator machine. Query output assumes property values are printable and may be noisy for large result sets.

Test signals: Mock tests can exercise WQL trimming, semicolon removal, table printing for scalar and list values, batch file command dispatch, RPC auth-level selection, and cleanup on connection errors. Integration tests require a WMI endpoint or recorded COM enumerator fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/examples/wmiquery.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/Dot11Crypto.py -->
# sources/user-network-fs/impacket/impacket/Dot11Crypto.py

Purpose: `Dot11Crypto.py` provides a minimal RC4 stream cipher implementation used by IEEE 802.11/WEP packet handling code.

Important APIs, types, and functions: `RC4.__init__(key)` performs the key-scheduling algorithm into `self.state`. `encrypt(data)` runs the pseudo-random generation algorithm and XORs each byte with the keystream. `decrypt(data)` delegates to `encrypt()` because RC4 is symmetric.

Control flow: Construction converts the key to a bytearray, initializes the 256-byte permutation, and swaps entries based on key bytes. Encryption resets local `i` and `j` counters to zero for each call, mutates `self.state` as it emits keystream, and returns `bytes(out)`.

State and persistence behavior: The cipher state is held in the `RC4` instance and is mutated by every encryption/decryption call. There is no external persistence. Reusing one instance for multiple independent messages continues the keystream state and can produce incorrect output if the caller expected a fresh RC4 stream per packet.

Dependencies and integration points: The module has no imports. It is used indirectly by 802.11/WEP support in the `dot11` packet classes and by decoders that decrypt protected data.

Risks: RC4/WEP is cryptographically obsolete. Empty keys cause modulo-by-zero during key scheduling. Stateful reuse is easy to misuse because `encrypt()` does not reset the permutation. There is no integrity verification here; WEP ICV checks are handled in packet-layer code.

Test signals: Tests should cover known RC4 vectors, encrypt/decrypt symmetry with fresh instances, behavior on byte-like inputs, empty-key rejection or failure behavior, and stateful reuse semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/Dot11Crypto.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/Dot11KeyManager.py -->
# sources/user-network-fs/impacket/impacket/Dot11KeyManager.py

Purpose: `Dot11KeyManager.py` is a small BSSID-to-key registry for 802.11 decoders, allowing protected wireless frames to find the key associated with an access point address.

Important APIs, types, and functions: `KeyManager` exposes `add_key(bssid, key)`, `replace_key(bssid, key)`, `get_key(bssid)`, and `delete_key(bssid)`. The private `__get_bssid_hasheable_type()` validates that BSSID input is a list, tuple, or `array.array` and converts it to a tuple for dictionary use.

Control flow: Add, replace, and get normalize the BSSID to a tuple and operate on `self.keys`. `add_key()` refuses to overwrite an existing entry and returns a boolean. `replace_key()` always stores the key and returns true. `get_key()` returns the key or `False` if absent.

State and persistence behavior: State is the in-memory `self.keys` dictionary. There is no file or network persistence. Keys remain until deleted or the manager object is discarded.

Dependencies and integration points: The only dependency is `array.array` for accepted BSSID input. `ImpactDecoder.BaseDot11Decoder.find_key()` calls `key_manager.get_key()` and WEP decoding uses that key to decrypt frames by BSSID.

Risks: `delete_key()` appears broken: it normalizes the BSSID to a tuple, then checks `if not isinstance(bssid, list)` and raises, so normal valid inputs cannot pass deletion. Returning `False` for absent keys can collide with a legitimate falsey key value. The class performs no key length or type validation and is not thread-safe.

Test signals: Tests should cover tuple/list/array BSSID normalization, add duplicate behavior, replacement, lookup miss behavior, and the `delete_key()` bug. Decoder integration tests should verify that WEP frames find the correct BSSID-derived key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/Dot11KeyManager.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ICMP6.py -->
# sources/user-network-fs/impacket/impacket/ICMP6.py

Purpose: `ICMP6.py` defines an `ImpactPacket.Header` subclass for ICMPv6 packet construction, parsing, checksum calculation, message metadata, and helpers for common ICMPv6 message bodies.

Important APIs, types, and functions: `ICMP6` declares protocol number 58, header size 4, message type/code constants, node-information constants, and the `icmp_messages` description table. Accessors include `get_type()`, `get_code()`, `get_checksum()`, setters for the same fields, `calculate_checksum()`, `is_informational_message()`, `is_error_message()`, and `is_well_formed()`. Class factories build echo request/reply, destination unreachable, packet-too-big, time-exceeded, parameter-problem, neighbor solicitation/advertisement, and node information messages. Payload helpers expose target address, neighbor flags, node information qtype/nonce/flags/data, echo fields, MTU, parameter-problem pointer, and originating packet data.

Control flow: Construction creates a 4-byte header and optionally loads bytes. Message factories build the ICMP header, pack the message-specific body with `struct` and `array`, wrap it in `ImpactPacket.Data`, and link it with `contains()`. `calculate_checksum()` zeroes the checksum, asks the IPv6 parent for a pseudo-header, appends ICMP header bytes and child payload bytes, computes the checksum via `Header.compute_checksum()`, and stores it. Well-formedness checks known message type and valid code membership.

State and persistence behavior: State lives in the packet buffer and linked child payload; there is no persistence. Checksum calculation mutates the checksum field and requires the ICMP6 object to be attached below an IPv6 parent that implements `get_pseudo_header()`.

Dependencies and integration points: The module depends on `ImpactPacket.Header`, `ImpactPacket.Data`, `array_tobytes`, `IP6_Address`, `array`, and `struct`. It integrates with `ImpactDecoder.ICMP6Decoder`, `IP6.get_pseudo_header()`, and packet building code that composes IPv6/extension-header/ICMPv6 trees.

Risks: `__str__()`, code-description lookup, and `is_well_formed()` can raise `KeyError` for unknown message types because some lookups happen before all validation. `set_target_address()` calls `address.get_bytes()`, but `IP6_Address` exposes `as_bytes()`, suggesting a latent bug. `get_note_information_data()` has a typo in the method name. Factory methods do not calculate checksums automatically, so callers must attach to IPv6 and call `calculate_checksum()`.

Test signals: Tests should cover factory output layouts, checksum calculation under an IPv6 parent, validation of known/unknown type-code pairs, neighbor flag bit operations, node-information flag operations, echo field accessors, and the target-address setter path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ICMP6.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/IP6.py -->
# sources/user-network-fs/impacket/impacket/IP6.py

Purpose: `IP6.py` implements an IPv6 header class for Impacket packet trees. It exposes header field accessors, address setters/getters, extension-header-aware child linking, and pseudo-header construction for upper-layer checksums.

Important APIs, types, and functions: `IP6` defines ethertype `0x86DD`, 40-byte header size, and version 6. Accessors cover version, traffic class, flow label, payload length, next header, hop limit, source address, and destination address. Setters modify the same fields in the underlying byte buffer. `contains()` updates the IPv6 next-header field when the child is an `IP6_Extension_Header`. `get_pseudo_header()` builds the checksum pseudo-header and walks extension-header children to find the final upper-layer protocol and adjusted length. Deprecated aliases log warnings and call the newer address/version APIs.

Control flow: Construction initializes a 40-byte header and sets version 6 before optional load. Pseudo-header construction obtains source/destination bytes, starts with payload length and current next-header, subtracts each extension header's size while following child links, and serializes length, reserved bytes, and protocol number into an `array('B')`.

State and persistence behavior: State is the packet buffer plus parent/child links managed by `ImpactPacket.Header`. There is no persistence. Mutator methods directly alter the buffer; `contains()` can implicitly change next-header state.

Dependencies and integration points: The class depends on `ImpactPacket.Header`, `array_frombytes`, `IP6_Address`, `IP6_Extension_Header`, `struct`, `array`, and `LOG`. It is used by `ImpactDecoder.IP6Decoder`, ICMPv6 checksum calculation, Ethernet decoders for ethertype dispatch, and packet builders.

Risks: `get_pseudo_header()` has a FIXME for routing-header destination-address special handling. Payload length is not automatically synchronized when children are attached. `set_ip_src()` and `set_ip_dst()` assign `address.as_bytes()` into a mutable byte array; callers passing unusual array types should be covered. Deprecated methods still exist but only warn.

Test signals: Tests should cover bitfield packing/unpacking for traffic class and flow label, source/destination parsing, next-header updates when extension headers are attached, pseudo-header output with and without extension headers, and checksum integration with ICMPv6.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/IP6.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/IP6_Address.py -->
# sources/user-network-fs/impacket/impacket/IP6_Address.py

Purpose: `IP6_Address.py` provides a lightweight IPv6 address parser, formatter, classifier, and byte representation for Impacket's IPv6 packet classes.

Important APIs, types, and functions: `IP6_Address(address)` accepts a text address or 16-byte sequence. Public projectors include `as_string(compress_address=True, scoped_address=True)`, `as_bytes()`, `get_scope_id()`, and `get_unscoped_address()`. Semantic helpers include `is_multicast()`, `is_unicast()`, `is_link_local_unicast()`, `is_site_local_unicast()`, `is_unique_local_unicast()`, and `get_human_readable_address_type()`. `is_a_valid_text_representation()` uses construction as validation. Private helpers parse scoped addresses, expand `::`, insert leading zeroes, and compress output by trimming leading zeroes and the longest zero chain.

Control flow: Construction initializes a 16-byte zero array and empty scope id, then dispatches to string or byte parsing. String parsing separates a single `%scope`, expands compressed notation if present, pads each group to four hex digits, validates total text length and group count, and fills the byte array two bytes at a time. Formatting emits full hex groups, optionally trims leading zeroes and the longest zero group chain, and appends scope if requested.

State and persistence behavior: State is the private byte array and optional scope id. There is no persistence. `as_bytes()` returns the underlying array object rather than a defensive copy, so callers can mutate address state.

Dependencies and integration points: The module depends on `array` and `six.string_types`. It is used by `IP6`, `ICMP6`, and code needing IPv6 address display or classification.

Risks: The unicast classifier treats only `0xFE...` addresses as unicast and returns `unknown type` for many ordinary global unicast addresses. The parser does not support IPv4-embedded dotted-decimal notation. `__from_bytes()` stores the provided object directly if length is 16, which can preserve mutability and non-array types. Compression of all-zero or edge zero chains should be regression-tested carefully.

Test signals: Tests should cover full and compressed text forms, scoped addresses, invalid triple/multiple compression markers, round-trip string/bytes behavior, longest-zero-chain compression, all-zero and loopback forms, scope omission, and address-type classification edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/IP6_Address.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/IP6_Extension_Headers.py -->
# sources/user-network-fs/impacket/impacket/IP6_Extension_Headers.py

Purpose: `IP6_Extension_Headers.py` implements IPv6 extension-header classes and option buffers for Hop-by-Hop Options, Destination Options, and Routing Options. It also provides the registry used by the IPv6 decoder to map next-header values to decoder classes.

Important APIs, types, and functions: `IP6_Extension_Header` handles common next-header/header-ext-len fields, option loading, packet serialization, child linking, pseudo-header delegation, and subclass registry discovery through `get_extension_headers()`. `Extension_Option` handles generic option type, option length, data, and size. `Option_PAD1` and `Option_PADN` model padding. `Basic_Extension_Header` adds automatic 8-octet padding for option headers. `Hop_By_Hop`, `Destination_Options`, and `Routing_Options` define header type values and decoder lookups; `Routing_Options` adds routing type and segments-left fields.

Control flow: Base construction initializes common header fields and option list, then either parses a buffer or calls `reset()`. `load_header()` reads the fixed fields, computes the full extension header length as `(Hdr Ext Len + 1) * 8`, and parses only Pad1 and PadN options into `_option_list`. `Basic_Extension_Header.add_option()` removes current padding, appends the new option, then adds Pad1/PadN to maintain 8-byte alignment. `get_packet()` updates `Header Ext Len`, serializes fixed fields and options, and appends child data if present.

State and persistence behavior: State is the mutable header buffer, `_option_list`, and for `Basic_Extension_Header` the `padded` flag. There is no persistence. Attaching another extension header through `contains()` updates the next-header field.

Dependencies and integration points: The module depends on `ImpactPacket.Header`, `ImpactPacketException`, and `PacketBuffer`. Decoder lookups import `ImpactDecoder` lazily to avoid import cycles. It integrates with `IP6.contains()`, `IP6.get_pseudo_header()`, and `ImpactDecoder.IP6MultiProtocolDecoder`.

Risks: `load_header()` only materializes padding options; unknown extension options are treated as PadN-shaped buffers and lose their type/data semantics. The `Extension_Option` maximum-size exception string has malformed formatting text. `Option_PADN.OPTION_DESCRIPTION` comment says Pad1. `Basic_Extension_Header.add_padding()` uses recursive `add_option()` through overridden dispatch but relies on the `padded` flag to terminate. `get_header_size()` is based on parsed options, so malformed buffers with unsupported options may produce misleading sizes.

Test signals: Tests should cover padding insertion for option lengths, packet serialization updating `Header Ext Len`, parsing truncated packets, extension-header registry contents, child next-header propagation, routing-options field accessors, and unknown option handling expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/IP6_Extension_Headers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ImpactDecoder.py -->
# sources/user-network-fs/impacket/impacket/ImpactDecoder.py

Purpose: `ImpactDecoder.py` contains convenience decoders that turn raw link/network/application bytes into nested `ImpactPacket` object trees. It covers Ethernet, Linux cooked captures, IPv4, IPv6 and extension headers, ARP, UDP, TCP, ICMP/ICMPv6, IGMP, 802.11/RadioTap/WEP/WPA/WPA2, LLC/SNAP/CDP, EAP/EAPOL/WPS, BOOTP, and DHCP.

Important APIs, types, and functions: `Decoder` is the base class with `decode()`, decoded-protocol tracking, `get_protocol()`, and string tree rendering. Link decoders include `EthDecoder` and `LinuxSLLDecoder`. IP decoders include `IPDecoder`, `IP6Decoder`, `IP6MultiProtocolDecoder`, extension-header decoders, `ICMPDecoder`, `ICMP6Decoder`, and `IPDecoderForICMP`. Wireless decoders include `BaseDot11Decoder`, `RadioTapDecoder`, `Dot11Decoder`, control/data/management subtype decoders, WEP/WPA/WPA2 decoders, `LLCDecoder`, and `SNAPDecoder`. `BaseDecoder` plus `SimpleConfigDecoder`, `EAPExpandedDecoder`, `EAPRDecoder`, `EAPDecoder`, and `EAPOLDecoder` implement table-driven EAP parsing. `BootpDecoder` and `DHCPDecoder` parse DHCP payloads.

Control flow: Each decoder constructs the header object for its layer, records it with `set_decoded_protocol()`, computes the body offset, selects a child decoder from protocol fields, decodes the remaining body, links child to parent with `contains()`, and returns the parent. Unknown protocols fall back to `DataDecoder`. IPv4 dispatch uses IP protocol numbers and handles zero `ip_len` as TCP segmentation offload by resetting length to buffer size. IPv6 dispatch uses next-header values, extension-header registry lookups, and recursive multi-protocol decoding. Dot11 data decoding selects frame body class based on DS/QoS bits, then attempts WEP with key manager, WPA, WPA2, and raw data fallback.

State and persistence behavior: Decoders keep the last decoded protocol and some child decoder instances as attributes for inspection. Dot11 decoders may hold a key manager and FCS-at-end flag. There is no persistence; all packet trees are in memory.

Dependencies and integration points: This module is the central integration point for `ImpactPacket`, `IP6`, `ICMP6`, `IP6_Extension_Headers`, `dot11`, `wps`, `eap`, `dhcp`, `CDP`, and `LOG`. Capture tools and examples can choose the correct outer decoder and then inspect the returned object hierarchy.

Risks: Some subtype comparisons use `is` instead of `==`, which is unreliable outside CPython small-integer interning assumptions. `Dot11WPADataDecoder` and `Dot11WPA2DataDecoder` instantiate `llc_decoder` locally but call `self.llc_decoder.decode()`, a likely AttributeError on decrypted WPA/WPA2 data. `Dot11WPA2Decoder.decode()` has no return path when a key is supplied. `LinuxSLLDecoder` does not handle IPv6, unlike Ethernet. Many decoders assume minimum buffer lengths and may raise on truncated input. BOOTP attempts to instantiate a DHCP packet just to check the cookie, which may raise on short payloads.

Test signals: Tests should include protocol dispatch fixtures for Ethernet IPv4/IPv6/ARP/EAPOL/LLC, IPv6 extension chains, ICMP unreachable partial inner packets, zero-length IPv4 TSO adjustment, Dot11 protected and unprotected frames, WPA/WPA2 decrypted paths, EAP/WPS child selection, DHCP cookie detection, and truncation/fallback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/ImpactDecoder.py -->
