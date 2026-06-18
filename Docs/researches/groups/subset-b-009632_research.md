# Research Group subset-b-009632

This grouped report covers four Impacket protocol/support files. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/mqtt.py -->
# sources/user-network-fs/impacket/impacket/mqtt.py

## Purpose
`mqtt.py` is a minimal MQTT client implementation focused on basic broker connection, subscription, unsubscription, publishing, and receiving published messages. It is intentionally incomplete: the file header calls out missing control-packet coverage and missing QoS 2 publish handling. Its practical integration point in this tree is `examples/mqtt_check.py`, which uses `MQTTConnection` and `CONNECT_ACK_ERROR_MSGS` to validate MQTT credentials.

## Important APIs, Types, and Functions
The module defines MQTT packet-type constants (`PACKET_CONNECT`, `PACKET_CONNACK`, `PACKET_PUBLISH`, `PACKET_SUBSCRIBE`, `PACKET_DISCONNECT`, and related ACK packet values), CONNECT flag constants, connection return-code text in `CONNECT_ACK_ERROR_MSGS`, and QoS constants.

`MQTT_Packet` is the base `impacket.structure.Structure` packet wrapper. It models the fixed header as `PacketType` plus an MQTT remaining-length field, decodes the variable-length remaining-length encoding in `fromString()`, emits that encoding in `getData()`, and applies QoS bits through `setQoS()`. `MQTT_String` models MQTT's two-byte length-prefixed strings.

The packet subclasses are small `Structure` layouts: `MQTT_Connect`, `MQTT_ConnectAck`, `MQTT_Publish`, `MQTT_Disconnect`, `MQTT_Subscribe`, `MQTT_SubscribeACK`, and `MQTT_UnSubscribe`. `MQTT_Publish.getData()` dynamically adds a `MessageID` field when QoS bits are set. `MQTTSessionError` is the catchable client error wrapper with accessors for code, packet, and text. `MQTTConnection` is the high-level socket client exposing `connectSocket()`, `send()`, `sendReceive()`, `recv()`, `connect()`, `subscribe()`, `unSubscribe()`, `publish()`, and `disconnect()`.

## Control Flow
Constructing `MQTTConnection` stores the target host, port, SSL setting, initializes `_messageId`, and immediately opens a socket. `connectSocket()` creates a TCP socket, connects to the target, and optionally wraps it in a pyOpenSSL `SSL.Connection` with `SSL.TLS_METHOD` and an explicitly broad cipher list (`ALL:@SECLEVEL=0`) before doing the TLS handshake.

Outbound operations build a packet structure, fill nested `MQTT_String` values, optionally call `setQoS()`, then call `sendReceive()` or `send()`. `connect()` builds a CONNECT packet with protocol name, version, flags, keepalive, client ID, and username/password payload strings. It sends the packet, parses the first response as `MQTT_ConnectAck`, and raises `MQTTSessionError` if the return code is non-zero. `subscribe()` builds a single-topic SUBSCRIBE packet and validates `MQTT_SubscribeACK.ReturnCode <= 2`. `unSubscribe()` builds an UNSUBSCRIBE packet for one topic. `publish()` builds a PUBLISH packet and always waits for a response, even though QoS 0 publishes normally have no acknowledgement. `disconnect()` sends a DISCONNECT packet without waiting.

Inbound `recv()` reads chunks up to 8192 bytes until a short read, then repeatedly parses `MQTT_Packet` objects out of the accumulated buffer. If parsing fails, it appends one more socket read and retries. The sample `__main__` block connects to a hard-coded host, subscribes to `$SYS/#`, and interprets every received packet as `MQTT_Publish`.

## State and Persistence Behavior
Runtime state is limited to `_targetHost`, `_targetPort`, `_isSSL`, `_socket`, and `_messageId`. `_messageId` is incremented after every `recv()` call but most public methods accept a default `messageID=1`, so the internal counter is not consistently used for outbound packet identifiers. The module does not persist files, caches, or credentials. Socket state is long-lived until `disconnect()` or external close.

Several packet classes mutate their structure while serializing. `MQTT_Packet.getData()` temporarily removes and then replaces `commonHdr` to compute the MQTT remaining length. `MQTT_Publish.getData()` replaces `self.structure` when QoS is enabled so that `MessageID` appears between topic and message.

## Dependencies and Integration Points
The module depends on Python `logging`, `struct`, `socket`, pyOpenSSL `OpenSSL.SSL`, and Impacket `Structure`. Import fails hard if pyOpenSSL is absent, even for non-SSL MQTT use. The main repository consumer is `examples/mqtt_check.py`, which constructs `MQTTConnection(target, port, ssl)` and calls `connect()` with parsed username/password values.

On the wire it integrates with MQTT 3.1/3.1.1-era brokers. Defaults still use protocol name `MQIsdp` and version `3`, while the `connect()` docstring notes that some brokers expect `MQTT` and version `4`.

## Risks and Edge Cases
This file is Python-2-style in several important places: `send()` calls `sendall(str(request))`, packet buffers are initialized as `''`, `ord(data[index])` assumes one-character strings, and `packetType + struct.pack(...)` mixes scalar/string/bytes semantics. Those choices are fragile under Python 3 unless `Structure` compatibility masks them.

The MQTT remaining-length encoder uses `/=` after importing no future division in this file, so Python 3 would convert `packetLen` to float after the first loop. Remaining-length decoding stops only after multiplier exceeds three continuation steps, and malformed/truncated packets can surface generic exceptions. `recv()` treats a short socket read as message completion, which is unreliable for stream protocols and can block for brokers that keep the connection open without returning a short read. It also retries parsing by appending one more chunk but can loop poorly on invalid data.

Protocol behavior is partial. QoS 2 is explicitly unimplemented. QoS 0 publish still waits for a response. SUBSCRIBE and UNSUBSCRIBE support only one topic through the high-level helpers. `connect()` sets both username and password flags when username is present, even if password is `None`, and still serializes empty username/password strings into the payload. TLS configuration lowers cipher restrictions, useful for legacy brokers but risky in security-sensitive contexts.

## Test Signals
Useful tests include serializing and parsing each packet type, especially MQTT remaining-length boundaries at 0, 127, 128, 16383, and malformed continuation encodings. Integration tests should cover anonymous and username/password CONNECT responses for all `CONNECT_ACK_ERROR_MSGS`, protocol-name/version combinations (`MQIsdp`/3 and `MQTT`/4), SSL and non-SSL sockets, SUBSCRIBE success/failure return codes, QoS 0 versus QoS 1 publish behavior, single-topic UNSUBSCRIBE, and receiving multiple packets in one TCP read. Python 3 compatibility tests should explicitly assert byte output from `getData()` and avoid `str(packet)` regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/mqtt.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/msada_guids.py -->
# sources/user-network-fs/impacket/impacket/msada_guids.py

## Purpose
`msada_guids.py` is a static Active Directory GUID name catalog. It maps schema object GUIDs and extended-right GUIDs to human-readable names so tools can render security descriptors, ACE object types, validated writes, schema attributes/classes, and control-access rights meaningfully instead of showing raw GUID strings.

## Important APIs, Types, and Functions
The file exports two dictionaries and no functions or classes. `SCHEMA_OBJECTS` contains 1,769 lowercase GUID string keys mapped to Active Directory schema object names. Its values span core classes and attributes (`User`, `Computer`, `Group`, `Object-Guid`, `Object-Sid`), service families (FRS/DFSR, DHCP, DNS, MSMQ, MSSQL, WMI), certificate/PKI fields, terminal services fields, POSIX/NIS additions, and modern AD claims/device/authentication policy objects. `EXTENDED_RIGHTS` contains 80 lowercase GUID string keys mapped to control-access or validated-write names, including password changes, replication rights, certificate enrollment, `Send-As`, `Receive-As`, validated DNS host name, validated SPN, and other domain/security operations.

The dictionaries are plain module-level constants. The primary in-tree consumer is `examples/dacledit.py`, which imports both dictionaries, merges them into `OBJECT_TYPES_GUID`, and uses the merged mapping to label ACL object type GUIDs while editing or displaying Active Directory DACLs.

## Control Flow
There is no runtime control flow beyond Python module import and dictionary construction. Importing the module allocates both dictionaries. Consumers perform normal dictionary lookups or merge the dictionaries into their own mapping. Since `dacledit.py` calls `OBJECT_TYPES_GUID.update(SCHEMA_OBJECTS)` and then `OBJECT_TYPES_GUID.update(EXTENDED_RIGHTS)`, any duplicate GUIDs between the two maps are intentionally resolved in favor of the extended-right name for that consumer.

## State and Persistence Behavior
The module has no mutable state management, I/O, network access, or persistence. The exported dictionaries are mutable Python dictionaries, so an importing caller can accidentally modify global process state unless it copies them first. There is no generated-data timestamp or schema version metadata embedded beyond the header comments and source references.

## Dependencies and Integration Points
The file has no imports. It is populated from Microsoft MS-ADA schema references and a cleaned external SDDL parser data source noted in the header. Its main integration point is Active Directory security tooling that needs to map binary/string GUIDs to display names after converting LDAP security descriptor values. In this repository, `dacledit.py` is the visible direct integration; other tools could import these constants without side effects.

## Risks and Edge Cases
The main risk is data freshness and completeness. Active Directory schema extensions evolve across Windows releases and environments, and forest-specific custom schema GUIDs will not be present. The header explicitly notes that entries may be missing. The keys are lowercase hyphenated GUID strings; callers that use uppercase GUIDs, binary little-endian GUID forms, braces, or non-canonical formatting must normalize before lookup.

Because `SCHEMA_OBJECTS` and `EXTENDED_RIGHTS` can contain overlapping GUIDs, merge order matters. For example, a GUID may be meaningful both as a schema object and as a validated right label depending on context; a flat merged map can hide that distinction. The file provides no reverse mapping, collision detection, validation against duplicate values, or lookup helper that communicates unknown GUIDs cleanly.

## Test Signals
Tests should verify import succeeds with no dependencies and the dictionaries remain non-empty at expected scales (`SCHEMA_OBJECTS` around 1,769 entries and `EXTENDED_RIGHTS` around 80 entries). Spot checks should cover high-value rights such as `DS-Replication-Get-Changes`, `DS-Replication-Get-Changes-All`, `User-Force-Change-Password`, `Validated-SPN`, and `Send-As`, plus common schema objects such as `User`, `Computer`, `Group`, `Object-Guid`, and `User-Principal-Name`. Consumer tests for `dacledit.py` should cover GUID normalization, unknown GUID fallback, and duplicate-key merge behavior between schema objects and extended rights.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/msada_guids.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/mssql/version.py -->
# sources/user-network-fs/impacket/impacket/mssql/version.py

## Purpose
`mssql/version.py` parses the four-byte SQL Server version field returned in the TDS pre-login response and provides a human-readable SQL Server product/update label. It is used by `impacket/tds.py` after `TDS_PRELOGIN` parsing to populate `self.mssql_version`.

## Important APIs, Types, and Functions
The file exports `MSSQL_VERSION`. `VERSION_NAME` is a nested static lookup shaped as `("Microsoft SQL Server", {major: (major_name, {minor: (minor_suffix, {build: update_label})})})`. It includes historical versions from SQL Server 6.0 and 6.5 through 2022 build entries present at the time this table was authored.

`__init__(self, version)` unpacks the supplied bytes with `struct.unpack_from(">bbH", version)`, storing signed one-byte `major`, signed one-byte `minor`, and unsigned big-endian two-byte `build`. `version_number` returns `"{major}.{minor}.{build}"`. `version_name` walks the nested table and returns a string such as `Microsoft SQL Server 2019 (CU20)` when all keys are known. `__repr__()` returns the display name followed by the numeric version in parentheses.

## Control Flow
The normal control path is `tds.MSSQL.preLogin()`: send a TDS pre-login packet, parse the response as `TDS_PRELOGIN`, then call `MSSQL_VERSION(response["Version"])`. After construction, callers can render `repr(mssql_version)` or inspect `version_number` and `version_name`.

The `version_name` property starts with the root string, appends the major version label, minor suffix, and build label in order, and suppresses `KeyError` for unknown major/minor/build table entries. It returns from a `finally` block.

## State and Persistence Behavior
Instances are immutable in practice after `major`, `minor`, and `build` are assigned, though the attributes are public and can be reassigned. The class has no I/O, persistence, caching, or network behavior. The large static `VERSION_NAME` table is process-global and mutable because it is a normal class attribute.

## Dependencies and Integration Points
The only import is Python `struct`. The direct integration point is `impacket/tds.py`, which imports `MSSQL_VERSION` and sets `self.mssql_version` during pre-login. Downstream SQL tools can use that value for banners, logging, compatibility decisions, or diagnostics after connecting to a server.

## Risks and Edge Cases
The `version_name` property has a correctness bug for unknown major versions: if `MSSQL_VERSION.VERSION_NAME[1][self.major]` raises before `string` is assigned, the `finally` block attempts to return an unbound local variable. Unknown minor or build values return a partial name because `string` has already been initialized and partly appended. The code catches only `KeyError`, so malformed `VERSION_NAME` structure would raise other exceptions.

`struct.unpack_from(">bbH", version)` requires at least four bytes; shorter pre-login version fields raise `struct.error`. The signed byte format is harmless for current SQL Server major/minor values but semantically odd for protocol version bytes. The static build table can become stale as new SQL Server cumulative updates ship, so a current server can produce only a partial `Microsoft SQL Server 2022` style label or fail for a new major release. The table also has no metadata indicating source date.

## Test Signals
Unit tests should parse known four-byte values for representative versions: SQL Server 2000, 2005, 2012, 2019 CU entries, and 2022 entries. Tests should assert `version_number`, `version_name`, and `repr()`. Negative tests should include unknown build for a known major/minor, unknown minor for a known major, unknown major, and too-short byte strings. The unknown-major test should document or fix the current unbound-local behavior. Integration tests should verify `tds.MSSQL.preLogin()` stores an `MSSQL_VERSION` object from a mocked `TDS_PRELOGIN` response.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/mssql/version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/nmb.py -->
# sources/user-network-fs/impacket/impacket/nmb.py

## Purpose
`nmb.py` implements NetBIOS name service helpers and NetBIOS session service framing used by Impacket's SMB stack and related examples. It handles RFC 1001/1002 name encoding/decoding, NBNS query/registration/status packet structures over UDP port 137, NetBIOS session packet framing over TCP port 139, direct SMB session use over TCP port 445, and NetBIOS datagram framing over UDP port 138.

## Important APIs, Types, and Functions
The module defines constants for NetBIOS name-service ports, SMB direct-hosting port, node/name types, opcodes, NBNS flags, question/resource-record types, response codes, name flags, NetBIOS session packet types, and `NAME_TYPES` display text.

`encode_name(name, nametype, scope)` and `decode_name(name)` implement first- and second-level NetBIOS name encoding. `_do_first_level_encoding()` and `_do_first_level_decoding()` are regex callbacks. `NetBIOSError` and `NetBIOSTimeout` are the module's error types.

The `Structure` packet classes model NBNS payloads: `NBNSResourceRecord`, `NBNodeStatusResponse`, `NBPositiveNameQueryResponse`, `NAME_SERVICE_PACKET`, `QUESTION_ENTRY`, `RESOURCE_RECORD`, `NAME_REGISTRATION_REQUEST`, `NAME_OVERWRITE_REQUEST`, `NAME_REFRESH_REQUEST`, `NAME_REGISTRATION_RESPONSE`, `NAME_CONFLICT_DEMAND`, `NAME_QUERY_REQUEST`, `ADDR_ENTRY`, `NODE_STATUS_REQUEST`, `NODE_NAME_ENTRY`, and `STATISTICS`.

`NetBIOS` is the high-level NBNS client. It exposes nameserver/broadcast setters and getters, `gethostbyname()`, `getnodestatus()`, `getnetbiosname()`, `getmacaddress()`, `name_registration_request()`, `name_query_request()`, and `node_status_request()`.

The session-service classes are `NetBIOSSessionPacket`, abstract `NetBIOSSession`, `NetBIOSUDPSessionPacket`, `NetBIOSUDPSession`, and `NetBIOSTCPSession`. `NetBIOSTCPSession` is the important SMB-facing class, with `send_packet()`, `recv_packet()`, `_request_session()`, `polling_read()`, `non_polling_read()`, and private `__read()` for exact-length reads.

## Control Flow
NBNS name lookup starts by encoding a NetBIOS name, filling a request structure with a random transaction ID, and calling `NetBIOS.send()`. `_setup_connection()` opens a UDP socket bound to a random high source port and enables broadcast. `send()` sends the packet to the configured destination, waits with `select.select()`, retries up to three times on timeout, parses a `NAME_SERVICE_PACKET`, validates the transaction ID, raises `NetBIOSError` for negative response codes, and returns the response. `name_query_request()` wraps successful responses in `NBPositiveNameQueryResponse`. `node_status_request()` wraps the answer in `NBNodeStatusResponse`, updates the cached MAC address, and returns the parsed node-name entries.

`NetBIOSSession.__init__()` normalizes local and remote names to 15 uppercase characters, handles the special `*SMBSERVER` name by substituting the IP address for direct port 445 or trying an NBNS node-status lookup for port 139, opens or adopts a socket, and requests a NetBIOS session only when connecting to port 139. `NetBIOSTCPSession._request_session()` sends a session request containing encoded remote and local names, then waits for positive or negative session responses while ignoring keepalives and unrelated session messages.

TCP `send_packet()` wraps upper-layer data in a `NETBIOS_SESSION_MESSAGE` header. `recv_packet()` reads an exact packet, recursively discards keepalives, and returns a `NetBIOSSessionPacket`. `__read()` first reads the four-byte session header, computes 17-bit session-message lengths from the flags byte when needed, then reads the indicated payload length using either `polling_read()` or `non_polling_read()`.

UDP session sends build `NetBIOSUDPSessionPacket` datagrams with source/destination encoded names and data payload, send to the connected peer, close and reopen the UDP socket, and receive only packets whose peer tuple matches the configured remote endpoint.

## State and Persistence Behavior
`NetBIOS` stores the configured name-service port, optional nameserver, broadcast address, cached socket during a send, and the last node-status MAC address. Requests use transaction IDs from `random.SystemRandom()` when available. No filesystem persistence occurs.

`NetBIOSSession` stores normalized local/remote names, local/remote types, remote host, and the active socket. `NetBIOSUDPSession` also tracks a peer tuple and monotonically incremented datagram ID. `NetBIOSTCPSession` stores whether select polling is used and selects a read function at construction. Sockets are closed only through explicit `close()` or by UDP send's close/reopen behavior; TCP receive timeouts temporarily mutate the socket timeout during reads.

## Dependencies and Integration Points
The module depends on `errno`, `re`, `select`, `socket`, `string`, `time`, `random`, `struct.pack/unpack`, `six` helpers, and Impacket `Structure`. It is central to SMB integration: `impacket/smb.py`, `impacket/smb3.py`, and `impacket/smbconnection.py` instantiate `NetBIOSTCPSession`; `smbserver.py` and ntlmrelayx SOCKS SMB plugins also use it. Examples such as `DumpNTLMInfo.py` use NetBIOS sessions directly. Tests in `tests/SMB_RPC/test_nmb.py` cover name encode/decode, local mocked NBNS parsing, and remote NBNS operations.

## Risks and Edge Cases
`encode_name()` and `decode_name()` are old compatibility code. Scope decoding appears flawed because `decoded_domain` is overwritten rather than appended for multiple labels, and the remote tests include a TODO to fix scope functionality. `decode_name()` uses `assert name_length == 32`, so optimized Python mode would remove that validation and invalid data could fail later.

`NetBIOS._setup_connection()` initializes `has_bind = 1`, so the final `Cannot bind` branch is effectively unreachable even if all bind attempts fail; the socket may continue without a successful explicit bind. It also does not break after a successful bind. `send()` closes the UDP socket only after a matching response; repeated mismatched responses can keep looping until timeout/retry behavior exits. Negative responses are decoded only from the low four bits of `FLAGS`.

`NBNodeStatusResponse.rawData()` builds `res` but does not return it. `NetBIOSError.get_error_code()` returns `self.error`, which is never assigned; callers should use `error_code` directly or this should be fixed. Some exception handlers assume `ex.errno` exists for arbitrary exceptions. `NetBIOSUDPSession._setup_connection()` creates and connects a UDP socket, then immediately replaces it with a second socket, wasting the first. UDP session send uses `str(p)`, another Python-2-style byte/string risk.

TCP exact-length reads are robust in intent but can block up to a one-hour default when timeout is `None`. `recv_packet()` recursively discards keepalives, which is fine for normal traffic but could recurse repeatedly on a pathological stream. Direct-hosted SMB on port 445 skips the NetBIOS session request but still uses session-message framing, as expected by Impacket SMB.

## Test Signals
Existing tests already exercise encode/decode truncation, mocked node status parsing, mocked name lookup parsing, and remote NBNS flows. Additional focused tests should cover scoped names with multiple labels, invalid encoded-name length, `NetBIOSError.get_error_code()`, `NBNodeStatusResponse.rawData()` return behavior, bind failure in `_setup_connection()`, timeout/retry accounting in `NetBIOS.send()`, transaction-ID mismatch handling, TCP session length parsing above 65535 bytes, keepalive discard, and Python 3 byte output for UDP/TCP packet sends. Integration tests should keep covering SMB1/SMB2/SMB3 use through `NetBIOSTCPSession` on ports 139 and 445.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/nmb.py -->
