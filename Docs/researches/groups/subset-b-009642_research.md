# Research Report: subset-b-009642

Grouped research for selected Impacket protocol, packaging, registry, WPS, ImpactPacket test, and SMB/RPC test files. Each section preserves the original source path and is wrapped for deterministic splitting into per-file research reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/tds.py -->
# sources/user-network-fs/impacket/impacket/tds.py

## Purpose

`tds.py` implements Impacket's SQL Server Discovery Protocol (`MC-SQLR`) and Tabular Data Stream (`MS-TDS`) client support. It can discover SQL instances over UDP 1434, connect to a SQL Server over TCP, negotiate TDS prelogin encryption, perform SQL authentication, NTLM, or Kerberos login, send SQL batches, parse server tokens, decode selected SQL row types, and print query results.

## Important APIs, Types, And Functions

The SQL Browser surface is `SQLR`, `SQLR_UCAST_INST`, `SQLR_UCAST_DAC`, `SQLR_Response`, and `MSSQL.getInstances()`. The TDS packet surface includes constants for packet types, encryption modes, token IDs, environment changes, column types, LOGIN7 versions, and TDS 8.0 all-headers fields. `TDSPacket`, `TDS_PRELOGIN`, `TDS_LOGIN`, `TDS_LOGIN_ACK`, `TDS_FEATUREEXTACK`, `TDS_INFO_ERROR`, `TDS_INFO_ERROR72`, `TDS_ENVCHANGE`, `TDS_DONE*`, `TDS_COLMETADATA`, `TDS_ROW`, and `TDS_SSVARIANT` model protocol messages.

The main class is `MSSQL`. Its public workflow APIs are `connect()`, `disconnect()`, `preLogin()`, `login()`, `kerberosLogin()`, `sendTDS()`, `recvTDS()`, `parseReply()`, `batch()`, `batchStatement()`, `sql_query`, `changeDB()`, `RunSQLQuery()`, and `RunSQLStatement()`. Helpers manage TLS (`set_tls_context()`, `_setup_tds8()`, `tls_send()`, `tls_recv()`), channel binding (`generate_cbt_from_tls_unique()`), LOGIN7 layout selection, row parsing, column metadata parsing, and result printing.

## Control Flow

`connect()` opens a TCP socket and resets TLS/session state. Authentication begins with `_negotiate_encryption()`, which sends a `TDS_PRELOGIN`, parses the encryption byte, retries as TDS 8.0 strict TLS if the plain prelogin is reset or if the server returns `TDS_ENCRYPT_STRICT`, and otherwise establishes in-memory TLS for login encryption. `login()` builds a `TDS_LOGIN`, chooses SQL auth or NTLM SSPI, sends LOGIN7, disables TLS after the first login packet when encryption is only login-scoped, handles NTLM challenge/response if needed, then parses the final tokens. `kerberosLogin()` follows the same prelogin/TLS setup, obtains or uses cached TGT/TGS data, constructs an SPNEGO AP-REQ with optional channel binding, sends it in `SSPI`, and accepts success when a LOGINACK token is present.

Packet send/receive is segmented by `packetSize`; `recvTDS()` reassembles packets until `TDS_STATUS_EOM`. TLS-over-TDS uses `ssl.MemoryBIO` and embeds handshake bytes inside prelogin packets. TDS 8.0 wraps the whole socket in TLS and prepends required all-headers data to SQL batches. Query execution sends UTF-16LE SQL batch text, receives tokens, updates `rows`, `colMeta`, `currentDB`, `packetSize`, and `lastError`, and returns decoded rows.

## State And Persistence Behavior

The module has no disk persistence. `MSSQL` maintains socket state, TLS objects, packet size, receive buffer, login version, current database, server version, accumulated replies, column metadata, decoded rows, and last error. `batch()` and `RunSQLQuery()` clear result state before sending new SQL. Remote state can be modified by arbitrary SQL supplied to `batch()` and `RunSQLStatement()`, and login paths can exercise domain authentication systems.

## Dependencies And Integration Points

Dependencies include `socket`, `select`, `ssl`, `datetime`, `decimal`, `uuid4`, `struct`, `binascii`, Impacket `ntlm`, `uuid`, logging, `Structure`, `impacket.mssql.version.MSSQL_VERSION`, Kerberos/SPNEGO modules, `pyasn1`, and optional credential cache material. It integrates with Impacket tools that need MSSQL authentication, query execution, SQL instance discovery, NTLM/Kerberos EPA channel binding, and SQL Server row decoding.

## Risks And Edge Cases

The file handles security-sensitive authentication and SQL execution. TLS verification is disabled (`CERT_NONE`) for both in-memory TLS and TDS 8.0 TLS, which is pragmatic for tooling but exposes MITM risk. Channel binding relies on `tls-unique`; TLS 1.3 is intentionally avoided for TDS 8.0 because `tls-unique` is unavailable. LOGIN7 layout depends on negotiated version state; wrong version selection corrupts token parsing, row count widths, and login extensions. Row decoding supports only selected SQL types and raises on unknown types. Some parsing uses identity comparisons for integer token types (`is`) and bitwise `|` on booleans; these generally work for small constants but are brittle style. `RunSQLQuery()` checks `lastError` twice. Registry-like global decimal precision changes in numeric parsing can affect later decimal operations in the process.

## Test Signals

Useful tests should cover prelogin encryption responses, TDS 8.0 retry on connection reset, LOGIN7 serialization for legacy and 7.4 layouts, FEATUREEXTACK parsing, NTLM MIC/channel-binding construction, Kerberos channel-binding checksum selection, packet fragmentation/reassembly, TDS 8.0 SQL batch all-headers, `parseColMetaData()` user type width changes, and `parseRow()` for nullable strings, GUID, numeric, date/time, money, and sql_variant values. Integration tests require a SQL Server fixture for SQL auth, NTLM, Kerberos, and strict encryption modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/tds.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/uuid.py -->
# sources/user-network-fs/impacket/impacket/uuid.py

## Purpose

`uuid.py` provides Impacket's UUID/GUID conversion helpers. It generates simple 16-byte identifiers and converts between binary DCE/RPC GUID layout, canonical string layout, UUID/version tuples, and packed UUID-plus-version values used by RPC interface bindings.

## Important APIs, Types, And Functions

`EMPTY_UUID` is the all-zero 16-byte value. `generate()` returns 16 random bytes assembled from four 31-bit random integers. `bin_to_string()` formats the DCE/RPC mixed-endian 16-byte GUID into `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`. `string_to_bin()` accepts canonical dashed UUIDs or raw 32-hex-character strings. `stringver_to_bin()` packs a major/minor version string as two little-endian `USHORT`s. `uuidtup_to_bin()`, `bin_to_uuidtup()`, `string_to_uuidtup()`, and `uuidtup_to_string()` bridge Impacket's `(uuid, version)` representation.

## Control Flow

The conversion path is mostly direct `struct.pack` and `struct.unpack`. Canonical UUID strings are parsed with a regular expression and packed with little endian for the first three fields and big endian for the remaining fields, matching Microsoft variant 2/DCE wire layout. `string_to_uuidtup()` searches for a UUID followed by any version-like `major.minor`, appending `" 1.0"` so missing versions default to `1.0`.

## State And Persistence Behavior

The module stores no mutable runtime state and persists nothing. Randomness is sourced from Python's `random.randrange`, not from a cryptographic RNG or durable UUID namespace state.

## Dependencies And Integration Points

It depends on `re`, `binascii`, `random.randrange`, and `struct`. It is a cross-cutting helper used by DCERPC binding modules, endpoint mapper code, packet parsers, and tests that need RPC interface UUID bytes.

## Risks And Edge Cases

`generate()` is not RFC UUID generation and is not cryptographically strong. `string_to_bin()` assumes the regex matches and will raise an attribute error for malformed dashed UUIDs. Undashed input is blindly unhexlified, so bad length or non-hex input raises from `binascii`. `uuidtup_to_bin()` silently returns `None` for non-two-element tuples. `bin_to_uuidtup()` uses an assertion for length checking, which can be disabled under optimized Python. `uuidtup_to_string()` expects the version in tuple form `(maj, min)`, while `string_to_uuidtup()` returns the version as a string, so callers must use the correct representation.

## Test Signals

Tests should round-trip canonical UUIDs through binary and tuple forms, validate mixed-endian byte ordering with known RPC UUID fixtures, cover default `1.0` extraction, malformed dashed and undashed strings, invalid tuple length, and the mismatch between string version and numeric tuple version representations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/uuid.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/version.py -->
# sources/user-network-fs/impacket/impacket/version.py

## Purpose

`version.py` centralizes runtime version presentation for Impacket. It reads the installed package version, builds user-facing banner strings, and exposes the library installation path.

## Important APIs, Types, And Functions

The module imports `importlib.metadata.version` as `get_version`, catches `PackageNotFoundError`, and reads `impacket.__path__`. It defines `version`, `BANNER`, `DEPRECATION_WARNING_BANNER`, and `getInstallationPath()`.

## Control Flow

At import time it tries `get_version('impacket')`. If metadata is unavailable, it sets `version = "?"` and prints a message suggesting `python setup.py egg_info` when running from source. `BANNER` is formatted from that value. `getInstallationPath()` returns a string containing `__path__[0]`.

## State And Persistence Behavior

The file has no persistence. Its only state is import-time module globals. The fallback path prints to stdout during import, which can affect command output for source-tree usage without installed metadata.

## Dependencies And Integration Points

It depends on Python package metadata and the `impacket` package path. Impacket examples and command-line tools use `BANNER`, `DEPRECATION_WARNING_BANNER`, and `getInstallationPath()` for startup messages and diagnostics.

## Risks And Edge Cases

Import-time printing can be noisy in libraries and tests. Editable/source checkouts without package metadata report `"?"`, which can make bug reports or tool output less precise. `getInstallationPath()` assumes `__path__` has at least one entry.

## Test Signals

Tests should mock `importlib.metadata.version` success and `PackageNotFoundError`, verify banner formatting, assert fallback version behavior without requiring real package metadata, and confirm `getInstallationPath()` reflects the package path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/winregistry.py -->
# sources/user-network-fs/impacket/impacket/winregistry.py

## Purpose

`winregistry.py` implements local and remote Windows registry hive parsing for Impacket. It can parse binary `regf` hive files, parse UTF-16LE exported `.reg` files, enumerate keys and values, read value data, print typed registry values, retrieve class data, and in limited cases modify existing binary hive values in place.

## Important APIs, Types, And Functions

The file exports registry type constants (`REG_NONE`, `REG_SZ`, `REG_EXPAND_SZ`, `REG_BINARY`, `REG_DWORD`, `REG_MULTISZ`, `REG_QWORD`) and binary hive structures `REG_REGF`, `REG_HBIN`, `REG_HBINBLOCK`, `REG_NK`, `REG_VK`, `REG_LF`, `REG_LH`, `REG_RI`, `REG_SK`, and `REG_HASH`. `Registry` is an abstract base class defining `walk()`, `findKey()`, `printValue()`, `enumKey()`, `enumValues()`, `getValue()`, and `getClass()`.

`saveRegistryParser` handles binary hive files or remote file-like objects. Important private helpers include `__findRootKey()`, `__getBlock()`, `__getValueBlocks()`, `__getData()`, `__setData()`, `__processDataBlocks()`, `__getValueData()`, `__setValueData()`, `__getLhHash()`, `__compareHash()`, `__findSubKey()`, and `__walkSubNodes()`. `exportRegistryParser` builds an in-memory `RegistryNode` tree from exported text. `get_registry_parser()` chooses the parser by file object status, `regf` magic, or exported registry header.

## Control Flow

Binary hive parsing starts by reading the 4096-byte base block, finding the root `nk` record, then walking hbin blocks and variable-sized cells. Key lookup strips a leading backslash, starts at the root key, and resolves path components through `lf`, `lh`, or `ri` subkey indexes. `ri` records are expanded into `lf`/`lh` records before scanning. Values are found through the key's value list, then data is read either from inline `OffsetData` for negative `DataLen` or from the pointed cell. `setValue()` locates a value and writes replacement bytes only when the new data length matches the recorded length.

Exported registry parsing reads UTF-16LE text, uses regexes to identify `[key]` sections and value assignments, converts type tags to Impacket registry constants, and stores children/values in a tree. `getValue()` returns UTF-16LE bytes for `REG_SZ` and unhexlified bytes for other exported types.

## State And Persistence Behavior

`saveRegistryParser` owns an open file descriptor and closes it in `close()`/`__del__()`. For local binary hives it opens with `r+b`, so `setValue()` can persist same-length value changes to disk or a remote file object. `exportRegistryParser` stores a full in-memory tree and is read-only. Traversal uses mutable `indent` for printing.

## Dependencies And Integration Points

Dependencies include `sys`, `re`, `ntpath`, `struct.unpack`, `binascii.unhexlify`, `six.b`, `abc`, Impacket `LOG`, `Structure`, and `hexdump`. The module is used by secrets-dumping and local operations code that needs SAM, SECURITY, SYSTEM, or exported registry data without invoking Windows APIs.

## Risks And Edge Cases

Binary hive parsing is permissive and catches broad exceptions while searching the root. Unsupported `li` records are a known TODO. Several `ri` expansion paths initialize `records` as a text string and concatenate bytes, which is fragile under Python 3 if exercised. Hash comparisons only check the first four bytes for `lf` and hash for `lh`, then verify full names. `__getValueBlocks()` reads `count + 1` in callers, which may overread depending on hive layout. `__getValueData()` returns an integer for inline small values, so print and consumer paths must tolerate int data for strings or DWORDs. Export parsing uses regexes that can fail on unusual escaping, deletion entries, comments, or complex multiline values. `RegistryNode.addChildNode()` uses dictionary union, requiring modern Python.

## Test Signals

Tests should use small binary hive fixtures with `lf`, `lh`, and `ri` subkeys; default values; inline small values; string, DWORD, QWORD, binary, and multistring data; missing keys; and same-length `setValue()` writes. Export parser tests should cover UTF-16LE headers, default values, `hex`, `hex(2)`, `hex(7)`, `hex(b)`, multiline backslash continuations, empty keys, and malformed unsupported formats. Integration tests should verify compatibility with `secretsdump.RemoteFile`-like objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/winregistry.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/wps.py -->
# sources/user-network-fs/impacket/impacket/wps.py

## Purpose

`wps.py` implements packet helpers for Wi-Fi Protected Setup Simple Configuration data. It provides TLV builders/parsers, enumerations for WPS element IDs and option values, and a `SimpleConfig` protocol packet wrapper for WSC opcode/flags plus TLV payload.

## Important APIs, Types, And Functions

Builder classes convert between typed values and byte arrays: `ArrayBuilder`, `ByteBuilder`, `StringBuilder`, and `NumBuilder`. `TLVContainer` stores ordered `(kind, value-array)` pairs and exposes `append()`, iteration with typed conversion, `all()`, `first()`, `to_ary()`, `get_packet()`, `n2ary()`, and `ary2n()`. Constant classes include `SCElem`, `MessageType`, `AuthTypeFlag`, `EncryptionTypeFlag`, `ConnectionTypeFlag`, `ConfigMethod`, `OpCode`, `AssocState`, `ConfigError`, `DevicePasswordId`, and `WpsState`. `SimpleConfig` extends `ProtocolPacket`, defines `op_code`, `flags`, `more_fragments`, and `length_field`, and maps known WPS elements to builders in `BUILDERS`.

## Control Flow

`TLVContainer.from_ary()` scans the input byte array as big-endian 16-bit type, big-endian 16-bit length, then raw value bytes until the array is consumed. Iteration converts values through the builder registered for each type, defaulting to raw arrays. Serialization reverses the process by emitting type, length, and stored raw value arrays. `SimpleConfig.build_tlv_container()` returns a `TLVContainer` preloaded with builders and symbolic descriptions derived from `SCElem`.

## State And Persistence Behavior

The module has no persistence. `TLVContainer` maintains mutable `elems`, optional descriptions, and an optional parent pointer. `SimpleConfig` instances store packet bytes through the `ProtocolPacket` base class. Builders themselves are stateless except for `NumBuilder.size`.

## Dependencies And Integration Points

Dependencies are `array`, `struct`, `functools.reduce`, `impacket.ImpactPacket.array_tobytes`, and `impacket.helper.ProtocolPacket`, `Byte`, and `Bit`. This module integrates with Impacket wireless packet code that needs to construct or decode WPS attributes in EAP/WSC contexts.

## Risks And Edge Cases

`TLVContainer.from_ary()` does not validate truncated headers or length overruns; malformed input can silently produce short values or raise from unpacking. `first()` raises `IndexError` for absent elements. `NumBuilder.to_ary()` raises if the integer does not fit, but does not reject negative values explicitly. `StringBuilder.to_ary()` expects a bytes-like value acceptable to `array.array('B', value)`. `AssocState.FAILURE` is accidentally a one-element tuple because of a trailing comma. `BUILDERS` maps `PUBLIC_KEY` to `NumBuilder(192)`, which treats it as one huge integer rather than a raw byte string, surprising callers that expect public key bytes. Fragmentation and length-field support are explicitly not implemented.

## Test Signals

Tests should round-trip TLVs for byte, string, numeric, and unknown elements; verify order preservation and duplicate element behavior; exercise absent `first()`, truncated TLV data, length overruns, numeric overflow, and negative numeric input; check `SimpleConfig` flag bits; and validate representative WPS M1/M2 attributes such as version, message type, UUID, nonce, auth/encryption flags, and public key handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/impacket/wps.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/setup.py -->
# sources/user-network-fs/impacket/setup.py

## Purpose

`setup.py` is Impacket's setuptools packaging entry point. It defines the package version, package metadata, Python classifiers, install requirements, scripts, packages, and optional data files.

## Important APIs, Types, And Functions

Top-level constants are `PACKAGE_NAME`, `VER_MAJOR`, `VER_MINOR`, `VER_MAINT`, `VER_PREREL`, and computed `VER_LOCAL`. `read(fname)` reads files relative to the setup script. The final `setup()` call provides package name, version, description, URL, author/maintainer, license, long description, package list, example scripts, data files, dependencies, extras, and classifiers.

## Control Flow

At import/execution time, the script probes whether `git branch` works. If so, it runs `git log -1 --format=%cd --date=format:%Y%m%d.%H%M%S` and `git rev-parse --short HEAD` to append a local version suffix. Failures fall back to no local suffix. Non-Darwin platforms install README, LICENSE, and `doc/*` under `share/doc/impacket`; Darwin disables `data_files`. Finally, `setup()` builds version `0.14.0.dev{+date.time.hash}`.

## State And Persistence Behavior

The script does not maintain application state, but build/install commands can write setuptools metadata, build artifacts, installed scripts, and package files. It reads Git metadata and `README.md`.

## Dependencies And Integration Points

It depends on `setuptools`, `glob`, `os`, `platform`, and `subprocess`. Runtime dependencies include `pyasn1`, `pyasn1_modules`, `pycryptodomex`, `pyOpenSSL`, `six`, `ldap3` with exclusions, `ldapdomaindump`, `flask`, and `charset_normalizer`; Windows gets `pyreadline3`. It integrates with packaging workflows, editable installs, source distributions, and Impacket's examples directory.

## Risks And Edge Cases

It uses `shell=True` for Git commands and wildcard subprocess imports. Version computation depends on Git availability and current repository state; source archives without `.git` omit the local suffix. `read()` does not specify encoding. Package lists are manually maintained, so new subpackages can be omitted. The homepage URL points to a legacy Core Security domain while maintainer is Fortra. `data_files` behavior differs on Darwin, so documentation installation is platform-dependent.

## Test Signals

Packaging checks should build metadata from a Git checkout and a non-Git source tree, verify the generated version string is PEP 440-compatible, confirm all intended subpackages are included, validate dependency constraints, and run `python -m build` or equivalent packaging smoke tests on Linux, macOS, and Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/setup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/__init__.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/__init__.py

## Purpose

This file marks `tests/ImpactPacket` as a Python package for Impacket's ImpactPacket test suite. It contains only the standard license/header comments and no executable test code.

## Important APIs, Types, And Functions

There are no public APIs, classes, functions, fixtures, imports, or module variables.

## Control Flow

Importing the package executes no logic beyond loading an empty module.

## State And Persistence Behavior

The file has no state and no persistence behavior.

## Dependencies And Integration Points

It integrates with Python's package discovery and allows test modules under `tests/ImpactPacket` to be imported as package members when test runners or tooling require package semantics.

## Risks And Edge Cases

The file is intentionally empty. The only practical risk is accidental addition of side effects, which would affect every test import under this package.

## Test Signals

No direct tests are needed. Test discovery of sibling modules is the effective signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_ICMP6.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_ICMP6.py

## Purpose

`test_ICMP6.py` validates construction and decoding of core ICMPv6 messages in Impacket. It checks byte-exact output for generated ICMPv6 packets after IPv6 pseudo-header checksum calculation and verifies decoder accessors for message type-specific fields.

## Important APIs, Types, And Functions

The test imports `unittest`, `IP6`, `ImpactDecoder`, and `ICMP6`. `TestICMP6.setUp()` builds message descriptions and reference byte arrays. Helper methods are `encapsulate_icmp6_packet_in_ip6_packet()`, `compare_icmp6_packet_with_reference_buffer()`, and `generate_icmp6_constructed_packets()`. Test methods are `test_message_construction()` and `test_message_decoding()`.

## Control Flow

The setup creates echo request/reply, parameter problem variants, destination unreachable variants, time exceeded variants, and packet-too-big messages with fixed payload data. Construction tests embed each ICMPv6 packet in a fixed IPv6 packet, set the next header and payload length, calculate the checksum, and compare header plus payload bytes to reference data. Decoding tests feed each reference byte list to `ImpactDecoder.ICMP6Decoder()` and assert message type, code, echo fields, parameter pointer, originating packet data, and MTU.

## State And Persistence Behavior

State is limited to per-test in-memory packet lists and reference lists. There is no network access or persistence.

## Dependencies And Integration Points

This test exercises `impacket.ICMP6`, `impacket.IP6`, and `ImpactDecoder.ICMP6Decoder`, including the IPv6 parent/child relationship required for ICMPv6 checksum calculation.

## Risks And Edge Cases

The tests use fixed checksum references tied to exact source/destination IPv6 addresses, hop limit, and payload. They cover common ICMPv6 error and echo messages but not neighbor discovery, router discovery, multicast listener, malformed lengths, unknown codes, or checksum failure handling.

## Test Signals

Passing tests signal stable ICMPv6 constructors, pseudo-header checksum calculation, decoder type/code dispatch, and accessor behavior for the covered messages. Additional tests should add malformed/truncated packets and neighbor discovery message classes if supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_ICMP6.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP.py

## Purpose

`test_IP.py` is a narrow regression test for IPv4 fragmentation behavior when an `IP` packet has no payload.

## Important APIs, Types, And Functions

It imports `unittest` and `impacket.ImpactPacket.IP`. The only test class is `TestIP`, and the only test method is `test_fragment_by_size_without_payload()`.

## Control Flow

The test creates an empty `IP()` packet, calls `fragment_by_size(8)`, and asserts the returned list is exactly `[ip]`. This verifies the method treats payload-less packets as already unfragmentable instead of creating bogus fragments or crashing.

## State And Persistence Behavior

State is local to the test. There is no network or disk behavior.

## Dependencies And Integration Points

The test integrates with `ImpactPacket.IP.fragment_by_size()` and Python `unittest`. It is part of local packet regression coverage.

## Risks And Edge Cases

Coverage is intentionally tiny. It does not test payload fragmentation, fragment offsets, flags, checksums, invalid sizes, or child protocol propagation. It only guards the no-payload edge case.

## Test Signals

Passing this test signals that empty IPv4 packets do not crash or mutate unexpectedly when fragmented by size. Broader fragmentation tests should cover data payloads and protocol-specific children.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6.py

## Purpose

`test_IP6.py` validates IPv6 header decoding and construction for a fixed UDP-carrying IPv6 header.

## Important APIs, Types, And Functions

It imports `unittest`, `IP6`, and `ImpactDecoder`. `TestIP6.setUp()` defines a 40-byte reference IPv6 header. `test_decoding()` verifies field extraction through `ImpactDecoder.IP6Decoder()`. `test_creation()` builds an `IP6.IP6()` object through setters and compares serialized bytes.

## Control Flow

Decoding converts the reference byte list into an IPv6 packet and checks version, traffic class, flow label, payload length, next header, hop limit, and compressed source/destination addresses. Creation sets the same fields on a new packet and compares `get_bytes().tolist()` to the reference.

## State And Persistence Behavior

State is limited to the in-memory reference header. No persistence or network I/O occurs.

## Dependencies And Integration Points

The test exercises `IP6.IP6` setters/getters, `IP6_Address` formatting via address accessors, and `ImpactDecoder.IP6Decoder` decoding.

## Risks And Edge Cases

The fixture covers one unfragmented IPv6 header and no payload decoding. It does not cover extension headers, invalid versions, jumbo payloads, flow label boundaries, address scope IDs, or payload length mismatches; those are partially covered by adjacent tests.

## Test Signals

Passing tests indicate stable IPv6 bitfield packing/unpacking and address formatting for the selected header. Additional signals should include boundary values and malformed packets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6_Address.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6_Address.py

## Purpose

`test_IP6_Address.py` validates IPv6 address parsing, conversion, compression, and scope-id handling in `impacket.IP6_Address`.

## Important APIs, Types, And Functions

It imports `unittest` and `IP6_Address`. `TestIP6_Address` defines `test_construction()`, `test_unicode_representation()`, `test_conversions()`, `test_compressions()`, and `test_scoped_addresses()`. `runTest()` is a no-op for compatibility.

## Control Flow

The tests construct addresses from full text, binary byte lists, unicode strings, compressed text, and scoped text. They assert successful construction for valid forms, exception raising for oversized, undersized, malformed, and empty forms, correct text-to-binary and binary-to-text conversion, compressed versus full formatting, and retrieval of scope ID and unscoped address.

## State And Persistence Behavior

The tests maintain only local address literals and expected byte lists. There is no persistence.

## Dependencies And Integration Points

This file exercises `IP6_Address.IP6_Address` constructor validation, `as_string()`, `as_bytes()`, `get_scope_id()`, and `get_unscoped_address()`. It supports higher-level IPv6 packet tests that depend on address formatting.

## Risks And Edge Cases

The tests assert exception behavior but do not inspect exception types/messages. They cover several compressed forms but not IPv4-mapped addresses, multiple `::` errors, lowercase normalization, zone indices with platform interface names beyond simple text, or numeric value boundary cases in every hextet.

## Test Signals

Passing tests signal stable validation, compression, round-trip conversion, and scope handling for representative IPv6 addresses. Future tests should add more malformed compression and normalization cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6_Address.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6_Extension_Headers.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6_Extension_Headers.py

## Purpose

`test_IP6_Extension_Headers.py` validates construction, chaining, IPv6 containment, and decoding of IPv6 hop-by-hop, destination options, routing options, and padding option headers.

## Important APIs, Types, And Functions

The file imports `unittest`, `six.PY2`, `IP6`, `ImpactDecoder`, and `IP6_Extension_Headers`. `TestIP6.string_to_list()` normalizes bytes behavior across Python 2 and 3. Test methods cover simple header creation, containment in IPv6, option addition and padding, chained extension headers, direct decoder use, full IPv6-chain decoding, and decoding from a bytes string.

## Control Flow

Construction tests instantiate `Hop_By_Hop`, `Destination_Options`, and `Routing_Options`, set next headers and routing fields, add `Option_PAD1` or `Option_PADN`, and compare serialized packets plus sizes to byte fixtures. Chaining tests use `.contains()` to nest destination, routing, and hop-by-hop headers, including inside an IPv6 packet. Decoder tests feed byte fixtures to `HopByHopDecoder`, `DestinationOptionsDecoder`, `RoutingOptionsDecoder`, and `IP6Decoder`, then assert next headers, extension length, routing type, segments left, header type, and option metadata.

## State And Persistence Behavior

All state is local packet fixtures and constructed packet objects. There is no network access or persistence.

## Dependencies And Integration Points

The tests exercise `impacket.IP6_Extension_Headers`, `IP6.IP6.contains()`, child chaining, extension header size calculation, option padding logic, and `ImpactDecoder` dispatch for IPv6 extension headers.

## Risks And Edge Cases

The tests are byte-exact and therefore sensitive to intentional serialization changes. They cover padding and simple chains but not malformed extension lengths, unknown option actions, jumbo option payloads, fragmentation headers, authentication/ESP headers, or decoder behavior on truncated chains. The class name `TestIP6` overlaps with another file but is harmless under module scoping.

## Test Signals

Passing tests signal stable extension header length calculation, option padding, next-header propagation, child chaining, and decoder dispatch for the covered basic headers. Additional tests should cover invalid length and unknown option behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6_Extension_Headers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP_fragment_issue2095.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP_fragment_issue2095.py

## Purpose

`test_IP_fragment_issue2095.py` is a regression test for issue 2095: IPv4 fragmentation must not crash when the payload is a generic `Data` object with no protocol number.

## Important APIs, Types, And Functions

It imports `unittest`, `IP`, and `Data` from `impacket.ImpactPacket`. `TestIPFragmentIssue2095.test_fragment_by_list_with_data_payload()` is the only test.

## Control Flow

The test creates an `IP()` packet, attaches `Data(b'HELLO WORLD')`, calls `fragment_by_list([8])`, and asserts the result is a non-empty list. The assertion focuses on successful execution and a plausible return shape rather than exact fragment bytes.

## State And Persistence Behavior

State is local to the packet object and returned fragment list. There is no persistence.

## Dependencies And Integration Points

The test directly exercises `IP.contains()`, `Data`, and `IP.fragment_by_list()` handling of children whose protocol is `None`.

## Risks And Edge Cases

The test does not verify exact offsets, flags, payload bytes, or checksum values. It only guards the crash condition. Fragment sizes other than 8 and multi-fragment payload distribution are not covered.

## Test Signals

Passing this test signals that generic data payloads no longer trigger the issue 2095 crash path during list-based fragmentation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_IP_fragment_issue2095.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_LinuxSLL.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_LinuxSLL.py

## Purpose

`test_LinuxSLL.py` validates selected setters/getters and serialization behavior for Linux cooked capture (`LinuxSLL`) packets.

## Important APIs, Types, And Functions

The file imports `unittest` and `LinuxSLL`. `TestLinuxSLL` defines `test_set_arphdr()` and `test_set_addr_bytes()`.

## Control Flow

`test_set_arphdr()` sets the ARP hardware type to `513` and reads it back. `test_set_addr_bytes()` sets a six-byte address, asserts it is padded to eight bytes with nulls, and asserts the serialized packet length is the 16-byte Linux SLL header size.

## State And Persistence Behavior

State is local to each `LinuxSLL` instance. There is no persistence.

## Dependencies And Integration Points

The tests exercise `ImpactPacket.LinuxSLL` header field setters/getters, address padding, and packet serialization length.

## Risks And Edge Cases

Coverage is small and does not test packet type, address length field, protocol field, decoding existing SLL frames, overlong addresses, or invalid field ranges.

## Test Signals

Passing tests signal stable ARP hardware field handling and address padding for short byte addresses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_LinuxSLL.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_TCP.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_TCP.py

## Purpose

`test_TCP.py` validates TCP header parsing, serialization, and common setter behavior for a fixed TCP SYN packet with options.

## Important APIs, Types, And Functions

It imports `unittest` and `TCP`. `TestTCP.setUp()` creates a byte fixture and parses it with `TCP(self.frame)`. Test methods `test_01()` through `test_09()` cover packet round-trip, getters, source/destination port setters, data offset setter isolation from flags, window setter, checksum setter, flag setters, `reset_flags()`, and `set_flags()`.

## Control Flow

Each test mutates the parsed TCP object and verifies getters. The offset test first sets flags to `0xAA`, changes header offset, and confirms flags are preserved. Flag tests verify bit-level behavior for SYN, FIN, ACK, RST, PSH, URG, ECE, and CWR.

## State And Persistence Behavior

State is a per-test TCP object derived from the fixture. There is no persistence or network behavior.

## Dependencies And Integration Points

The file exercises `ImpactPacket.TCP` parsing of options-bearing headers, header length fields, flag bit manipulation, and serialization through `get_packet()`.

## Risks And Edge Cases

The tests do not validate sequence/ack numbers, urgent pointer, option parsing content, checksum calculation, payload handling, invalid header lengths, or malformed option lengths; the latter is covered by `test_TCP_bug_issue7.py`.

## Test Signals

Passing tests signal that common TCP header fields and flag manipulation remain stable for an options-bearing packet.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_TCP.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_TCP_bug_issue7.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_TCP_bug_issue7.py

## Purpose

`test_TCP_bug_issue7.py` is a regression test ensuring TCP option parsing does not hang when an option advertises an invalid zero length.

## Important APIs, Types, And Functions

It imports `unittest`, `Thread`, `TCP`, and `ImpactPacketException`. `TestTCP.setUp()` stores a malformed TCP header string. `test_01()` defines a worker thread class `it_hangs` that attempts to parse the malformed frame.

## Control Flow

The worker thread constructs `TCP(frame)` inside exception handling. It accepts the expected `ImpactPacketException` message `'TCP Option length is too low'`, ignores other exceptions, and exits. The main test starts the daemon thread, joins for one second, and asserts the thread is no longer alive.

## State And Persistence Behavior

State is local thread execution and the malformed frame literal. There is no persistence.

## Dependencies And Integration Points

The test exercises `ImpactPacket.TCP` option parsing and `ImpactPacketException` behavior under malformed input. The threaded timeout specifically guards against infinite loops.

## Risks And Edge Cases

The frame is a Python string literal rather than bytes, which relies on `TCP` accepting that form. The test ignores unexpected non-`ImpactPacketException` exceptions, so it primarily detects hangs rather than all parser regressions. One-second timing can be noisy on very overloaded systems.

## Test Signals

Passing this test signals that malformed zero-length TCP options terminate quickly instead of hanging. Stronger tests should assert the exact exception in the main thread without swallowing unexpected errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_TCP_bug_issue7.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_ethernet.py -->
# sources/user-network-fs/impacket/tests/ImpactPacket/test_ethernet.py

## Purpose

`test_ethernet.py` validates Ethernet frame parsing and manipulation, especially 802.1Q/QinQ VLAN tag handling.

## Important APIs, Types, And Functions

The file imports `unittest`, `array.array`, `Ethernet`, and `EthernetTag`. `TestEthernet.setUp()` parses a VLAN-tagged Ethernet frame. Test methods cover basic getters, setters, `EthernetTag` getters/setters, and multi-tag stack manipulation through `push_tag()`, `pop_tag()`, `get_tag()`, and `set_tag()`.

## Control Flow

Tests first assert original frame, header size, ethertype, and source/destination addresses. Setter tests mutate ethertype and swap MACs. VLAN tests pop the original tag, inspect TPID/PCP/DEI/VID, mutate tag fields, push S-tags and deprecated QinQ tags, verify tag counts and header sizes, test negative indices, assert out-of-range `IndexError`, reconstruct an `Ethernet` object from serialized bytes, and remove a middle tag.

## State And Persistence Behavior

State is local Ethernet and tag objects. There is no persistence.

## Dependencies And Integration Points

The test exercises `ImpactPacket.Ethernet`, `EthernetTag`, byte serialization, MAC field storage as arrays, and VLAN tag stack behavior.

## Risks And Edge Cases

The tests cover VLAN stack manipulation well but do not test untagged frames, malformed short frames, payload preservation beyond ethertype, provider bridging variants beyond given TPIDs, or invalid VLAN field ranges.

## Test Signals

Passing tests signal stable VLAN tag parsing, insertion/removal, indexing semantics, header size updates, and Ethernet field mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/ImpactPacket/test_ethernet.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/__init__.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/__init__.py

## Purpose

This file marks `tests/SMB_RPC` as a Python package for SMB, RPC, LDAP, and related remote/local tests. It contains only the standard license/header comments and no executable logic.

## Important APIs, Types, And Functions

There are no classes, functions, imports, fixtures, constants, or public APIs.

## Control Flow

Importing the package has no side effects.

## State And Persistence Behavior

The file stores no state and persists nothing.

## Dependencies And Integration Points

It supports Python package discovery for sibling SMB/RPC test modules and their relative imports under the broader Impacket test suite.

## Risks And Edge Cases

The file is intentionally empty. Adding side effects here would affect many SMB/RPC tests and could interfere with remote-test configuration.

## Test Signals

No direct test is needed beyond successful discovery/import of sibling test modules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_acl.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_acl.py

## Purpose

`test_acl.py` validates Impacket's Windows file ACL management helpers over SMB at the unit level. It uses mocks for network-bound SMB/LSA interactions and byte fixtures for security descriptors, ACEs, and SIDs.

## Important APIs, Types, And Functions

The file imports `unittest`, `mock`, `MagicMock`, `patch`, `SMBFileACL`, `FileNTACE`, `ACL_SID`, `FileNTUser`, `SecurityAttributes`, `SUPPORTED_PERMISSIONS`, and `FileSecInformation`. `TestSMBFileACL.get_mock_smb_file_acl()` creates an `SMBFileACL` with patched `SMBConnection` and `SMBTransport`. Tests cover `name_to_sid()`, `permissions_to_ace()`, invalid permission handling, `SMBFileACL.insert_permission()` grant/revoke/delete behavior, and ACL structure formatting. `TestACLStructures` covers SID representation/build/equality, ACE flag and permission display, and `SecurityAttributes.__str__()`.

## Control Flow

Name resolution tests patch `lsat.hLsarLookupNames3()` to return a mock SID and assert stripped SID byte length. Permission conversion patches `name_to_sid()` and checks resulting `FileNTACE` action and rights. Insert-permission tests parse fixed security descriptor blobs, build new/revoke/delete ACEs, call `SMBFileACL.insert_permission()`, then parse the resulting DACL and assert ACE count changes or preservation. Structure tests instantiate SID and ACE objects from bytes or strings and inspect string output.

## State And Persistence Behavior

The tests do not touch real SMB servers because connection classes are patched. State is local mocks, byte buffers, and parsed structures. No persistence occurs.

## Dependencies And Integration Points

The file exercises `impacket.acl`, `impacket.smb3structs.FileSecInformation`, LSAT lookup integration through mocks, and Python mock/unittest. It protects ACL operations used by command-line or library callers that read and update Windows file permissions.

## Risks And Edge Cases

Two intended close-on-error tests appear nested inside `test_insert_permission_grant_new_ace()` after an assertion, making them local functions rather than discovered test methods. This means file handle cleanup on permission resolution/query errors is not actually tested. Most security descriptor checks assert ACE counts but not full binary descriptor integrity or exact rights after mutation. SID build has a comment acknowledging a known authority encoding issue. Real SMB open/query/set operations are mocked, so transport-level failures and server ACL canonicalization are not covered.

## Test Signals

Passing discovered tests signal that mocked SID lookup, permission string conversion, ACE insertion/merge/removal counts, SID equality/hash, ACE flag formatting, and security attribute display remain stable. The nested cleanup tests should be lifted to class scope to provide the intended resource cleanup signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_acl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_ldap.py -->
# sources/user-network-fs/impacket/tests/SMB_RPC/test_ldap.py

## Purpose

`test_ldap.py` provides remote integration tests for Impacket's LDAP client over LDAP and LDAPS. It validates login methods, searches, Kerberos authentication variants, and binary security descriptor round-tripping against an Active Directory target.

## Important APIs, Types, And Functions

The file imports `pytest`, `unittest`, `RemoteTestCase`, `impacket.ldap.ldap`, `ldapasn1`, `impacket.ldap.ldaptypes`, and `SR_SECURITY_DESCRIPTOR`. `LDAPTests` defines `connect()`, `tearDown()`, `dummySearch()`, and tests for security descriptors, Sicily package discovery, Sicily NTLM, SASL NTLM, Kerberos password login, Kerberos hash login, Kerberos AES-key login, NTLM hash login, and generic search. `LDAPTestsTCPTransport` and `LDAPTestsSSLTransport` are marked `pytest.mark.remote` and configure `ldap://` and `ldaps://` URLs.

## Control Flow

Transport subclasses call `set_transport_config(aes_keys=True)`, derive `url` from `serverName`, and build `baseDN` from the configured domain. `connect()` creates `ldap.LDAPConnection` and optionally performs simple login. `dummySearch()` searches for objects with `servicePrincipalName=*` and prints returned entries. `test_security_descriptor()` disables ACL size recalculation, searches for computer objects' `nTSecurityDescriptor`, parses each descriptor with `SR_SECURITY_DESCRIPTOR`, dumps it, and asserts byte-for-byte round-trip. Authentication tests connect without initial login, invoke specific LDAP login methods, then usually run `dummySearch()`.

## State And Persistence Behavior

The tests maintain a live `ldapConnection` attribute and close it in `tearDown()`. They do not intentionally modify directory objects, but they depend on remote directory state, credentials, Kerberos material, and certificate/TLS configuration. `test_security_descriptor()` mutates the module global `impacket.ldap.ldaptypes.RECALC_ACL_SIZE = False` and does not restore it.

## Dependencies And Integration Points

These tests integrate with the Impacket LDAP stack, ASN.1 LDAP message types, LDAP security descriptor structures, `RemoteTestCase` configuration, pytest remote markers, Active Directory, NTLM/SASL/Sicily authentication, Kerberos KDC access, LM/NT hashes, AES keys, and LDAPS transport.

## Risks And Edge Cases

The tests are environment-sensitive and require a reachable AD server with suitable credentials and test configuration. `baseDN` assumes a two-label domain and will break for deeper domains. Security descriptor comparison is binary-exact and intentionally disables ACL size recalculation to tolerate Windows padding, but the global setting can leak to later tests. Searches print entries, which can make logs noisy and may expose directory data. The tests do not skip gracefully inside the file when remote config is absent; that is delegated to pytest marks and `RemoteTestCase`.

## Test Signals

Passing tests signal working LDAP/LDAPS connectivity, simple/NTLM/SASL/Sicily/Kerberos authentication paths, search behavior, and security descriptor parse/serialize fidelity against a real domain. Unit tests with mocked LDAP responses would be useful for deterministic coverage of descriptor parsing and baseDN handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/SMB_RPC/test_ldap.py -->
