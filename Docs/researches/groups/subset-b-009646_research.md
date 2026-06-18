# subset-b-009646 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagement.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagement.py

Purpose: Exercises Impacket's 802.11 beacon management-frame decoding and mutation path from a complete RadioTap capture.

Important APIs, types, and functions: `TestDot11ManagementBeaconFrames` uses `RadioTapDecoder.decode`, `Dot11Types` constants, `Dot11.get_type`, `get_subtype`, `get_type_n_subtype`, `Dot11ManagementFrame` address/sequence helpers, and `Dot11ManagementBeacon` timestamp, beacon interval, capability, SSID, supported-rates, DS parameter, and vendor-specific IE helpers.

Control flow: `setUp` decodes a raw RadioTap frame, walks `radiotap.child()` to `Dot11`, then to the management base and beacon body. Tests validate fixed fields first, then mutate variable tagged parameters and check resulting header-size changes.

State and persistence behavior: All state is in packet objects built from in-memory bytes; setters mutate the packet buffer and derived length metadata. No filesystem or network persistence occurs.

Dependencies and integration points: Integrates `impacket.ImpactDecoder.RadioTapDecoder` with `impacket.dot11` packet classes and Python 2/3 class-name compatibility through `six.PY2`.

Risks: The suite is sensitive to tagged information element offsets and assumes vendor-specific IE parsing preserves ordering. Header-size assertions catch regressions where setters fail to resize packet buffers.

Test signals: Strong regression signal for beacon decoding, address mutation, sequence masking, supported-rate human-readable conversion, and vendor IE append behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagement.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAssociationRequest.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAssociationRequest.py

Purpose: Validates parsing and editing of 802.11 association request frames from a captured RadioTap sample.

Important APIs, types, and functions: Uses `RadioTapDecoder`, `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_ASSOCIATION_REQUEST`, `Dot11ManagementFrame` duration/address/sequence methods, and `Dot11ManagementAssociationRequest` capability, listen interval, SSID, supported rates, RSN, and vendor-specific methods.

Control flow: `setUp` decodes a raw frame and asserts each child class in the decoder chain before tests operate on the base and association request body. Individual tests mutate fields, then assert updated values and dynamic header-size effects.

State and persistence behavior: Packet state is entirely in memory. RSN, SSID, supported-rates, and vendor-specific setters rewrite variable-length body regions and update packet length calculations.

Dependencies and integration points: Connects RadioTap decoding to management subtype dispatch and exercises WPA/RSN information element handling.

Risks: Header-length regressions are likely if information-element insertion/removal miscomputes offsets. The test also guards 4-bit fragment and 12-bit sequence-number masking.

Test signals: Covers fixed association request fields, selected IE parsing, human-readable rate conversion, RSN replacement, and vendor IE append ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAssociationRequest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAssociationResponse.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAssociationResponse.py

Purpose: Tests 802.11 association response decoding and mutation through Impacket's Dot11 management-frame hierarchy.

Important APIs, types, and functions: `TestDot11ManagementAssociationResponseFrames` uses `RadioTapDecoder`, `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_ASSOCIATION_RESPONSE`, `Dot11ManagementAssociationResponse.get/set_capabilities`, `get/set_status_code`, `get/set_association_id`, supported-rates accessors, and vendor-specific IE helpers.

Control flow: The setup phase decodes the raw RadioTap capture, checks class dispatch, extracts the management base, and then tests base-frame fields and association response body fields.

State and persistence behavior: Tests mutate packet objects in memory only. Supported-rate and vendor IE edits resize the body and provide direct signals that serialized packet layout remains coherent.

Dependencies and integration points: Depends on `six.PY2` for legacy assertion formatting and the Dot11 tagged-parameter parser for variable response body content.

Risks: Association ID and status fields are compact fixed-width values; endian or offset mistakes can silently corrupt later tagged parameters. Vendor IE appending must preserve pre-existing IE tuples.

Test signals: Confirms subtype dispatch, duration/address/sequence helpers, body bytes, response status/capability/AID fields, rate conversion, and vendor IE growth.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAssociationResponse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAuthentication.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAuthentication.py

Purpose: Validates authentication management-frame decoding, fixed authentication fields, and vendor-specific tagged-parameter handling.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_AUTHENTICATION`, `Dot11ManagementAuthentication.get/set_authentication_algorithm`, `get/set_authentication_sequence`, `get/set_authentication_status`, and base management-frame duration/address/sequence helpers.

Control flow: `setUp` decodes a raw RadioTap capture and asserts the child chain reaches `Dot11ManagementAuthentication`. Tests cover base-frame fields, raw frame body, authentication triplet fields, and vendor-specific append behavior.

State and persistence behavior: No durable state. Setters rewrite in-memory packet data, and header-size checks verify appended vendor IEs are reflected in packet metadata.

Dependencies and integration points: Exercises `RadioTapDecoder` subtype dispatch and the common management-frame body parser used by many 802.11 management subclasses.

Risks: Authentication algorithm, sequence, and status are adjacent 16-bit fields; endian or offset regressions would produce plausible but wrong values. Vendor IE resizing remains a shared risk with other management tests.

Test signals: Good coverage for authentication subtype classification, class hierarchy, fixed field mutation, and vendor IE parsing/append.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementAuthentication.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementDeauthentication.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementDeauthentication.py

Purpose: Tests deauthentication management-frame parsing and reason-code mutation.

Important APIs, types, and functions: Uses `RadioTapDecoder`, `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_DEAUTHENTICATION`, common `Dot11ManagementFrame` field helpers, and `Dot11ManagementDeauthentication.get_reason_code` / `set_reason_code`.

Control flow: Setup decodes a compact RadioTap frame to `Dot11ManagementDeauthentication`. Tests assert header sizes, fixed base fields, frame body bytes, sequence/fragment masking, and the two-byte reason code.

State and persistence behavior: Mutates in-memory packet bytes only. No external state is read beyond the raw literal frame.

Dependencies and integration points: Integrates management subtype dispatch with the common deauth/disassoc reason-code packet shape.

Risks: The class name in this file is still `TestDot11ManagementBeaconFrames`, so test discovery relies on method naming rather than semantic class naming. Reason-code parsing is tiny, making offset mistakes the main implementation risk.

Test signals: Covers subtype dispatch, address/sequence operations, exact body extraction, and reason-code setter/getter behavior for deauthentication frames.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementDeauthentication.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementDisassociation.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementDisassociation.py

Purpose: Validates Dot11 disassociation frame decoding and reason-code accessors.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_DISASSOCIATION`, `RadioTapDecoder.decode`, `Dot11ManagementFrame` duration/address/sequence helpers, and `Dot11ManagementDisassociation.get_reason_code` / `set_reason_code`.

Control flow: The setup phase decodes a full RadioTap sample and checks class dispatch down to `Dot11ManagementDisassociation`; tests then mutate base fields and the body reason code.

State and persistence behavior: All packet state is transient and in memory. Setters update the backing packet buffer; no persistent outputs are produced.

Dependencies and integration points: Shares the common management-frame base with association, authentication, and deauthentication tests.

Risks: Like deauthentication, the body is only two bytes, so incorrect body offsets or FCS handling would dominate failures. Python 2/3 class-string assertions add legacy compatibility noise.

Test signals: Confirms subtype classification, address setters, sequence-number masking, frame-body extraction, and disassociation reason-code mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementDisassociation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementProbeRequest.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementProbeRequest.py

Purpose: Tests probe request management-frame decoding and variable information element mutation.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_PROBE_REQUEST`, `Dot11ManagementProbeRequest.get/set_ssid`, `get/set_supported_rates`, and common `Dot11ManagementFrame` fixed-field helpers.

Control flow: Setup decodes a raw probe request through RadioTap and Dot11 layers, then tests header sizes, base-frame fields, raw body bytes, SSID replacement, and supported-rate replacement.

State and persistence behavior: No external state. SSID and rate setters mutate variable-length IE content and update packet-size accounting in memory.

Dependencies and integration points: Exercises RadioTap-to-Dot11 management subtype dispatch and tagged IE parsing for client-originated probe requests.

Risks: Probe requests often contain short variable sections; length changes can shift all later IEs. Header-size assertions specifically guard those offset calculations.

Test signals: Validates broadcast destination/BSSID handling, source address extraction, sequence masking, SSID parsing, supported-rate tuple conversion, and dynamic header-size recalculation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementProbeRequest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementProbeResponse.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementProbeResponse.py

Purpose: Exercises probe response decoding, beacon-like fixed fields, and large vendor-specific IE lists including WPS/WPA data.

Important APIs, types, and functions: Uses `Dot11ManagementProbeResponse` timestamp, beacon interval, capabilities, SSID, supported-rates, DS parameter, and vendor-specific helpers with `RadioTapDecoder` and `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_PROBE_RESPONSE`.

Control flow: Setup decodes a large raw RadioTap probe response and asserts class dispatch. Tests verify base fields, fixed beacon-compatible fields, variable IEs, and appending a new vendor-specific element.

State and persistence behavior: State is packet-local. Variable IE operations mutate the backing bytes and update header-size calculations.

Dependencies and integration points: Integrates management parsing with WPS and WPA vendor IE tuple extraction, preserving multiple OUIs in order.

Risks: The large frame body makes offset drift likely when one IE is resized. Vendor-specific parsing must handle multiple entries with the same OUI and different payload lengths.

Test signals: Strong signal for probe-response body parsing, timestamp endian handling, DS channel, rate conversion, vendor IE enumeration, and appended IE size accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementProbeResponse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementReassociationRequest.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementReassociationRequest.py

Purpose: Validates reassociation request parsing, including the current-AP address field and RSN/tagged parameters.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_REASSOCIATION_REQUEST`, `Dot11ManagementReassociationRequest.get/set_capabilities`, `get/set_listen_interval`, `get/set_current_ap`, SSID/rate/RSN helpers, and vendor-specific helpers.

Control flow: Setup decodes a RadioTap sample through management base to the reassociation request object. Tests mutate base fields, then body fixed fields and variable IEs.

State and persistence behavior: Packet object mutations are in-memory. Current AP and RSN setters rewrite body bytes, while variable IE changes update header-size metadata.

Dependencies and integration points: Extends association-request behavior with the current AP field, sharing the same management IE parser.

Risks: The current AP field sits between fixed fields and tagged parameters, so an incorrect fixed header length would break all subsequent IE parsing. Test names include a minor "Ressociation" typo but discovery remains unaffected.

Test signals: Covers subtype dispatch, fixed reassociation fields, SSID/rate/RSN replacement, vendor IE append ordering, and dynamic size changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementReassociationRequest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementReassociationResponse.py -->
# sources/user-network-fs/impacket/tests/dot11/test_FrameManagementReassociationResponse.py

Purpose: Tests reassociation response parsing and mutation, mirroring association response behavior for the reassociation subtype.

Important APIs, types, and functions: Uses `Dot11Types.DOT11_SUBTYPE_MANAGEMENT_REASSOCIATION_RESPONSE`, `Dot11ManagementReassociationResponse.get/set_capabilities`, `get/set_status_code`, `get/set_association_id`, supported-rates helpers, and vendor-specific helpers.

Control flow: Setup decodes a raw RadioTap sample and asserts class dispatch into the reassociation response object. Tests verify base-frame fields, raw body bytes, fixed response fields, rates, and vendor IEs.

State and persistence behavior: All state is transient packet-buffer mutation. Rate replacement shrinks the header and vendor IE append expands it.

Dependencies and integration points: Exercises subtype dispatch distinction between association response and reassociation response while sharing fixed body layout.

Risks: Because the layout matches association response, regressions may accidentally pass one subtype and fail the other if subtype mapping is wrong. Vendor IE appending must preserve pre-existing tuple content.

Test signals: Confirms reassociation response subtype mapping, AID/status/capability fields, sequence masking, rate humanization, and variable IE size accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_FrameManagementReassociationResponse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_RadioTap.py -->
# sources/user-network-fs/impacket/tests/dot11/test_RadioTap.py

Purpose: Provides broad regression coverage for the `RadioTap` packet class: present flags, optional field accessors, field insertion/removal, serialization, and extended present flags.

Important APIs, types, and functions: Uses `RadioTap` constants such as `RTF_TSFT`, `RTF_FLAGS`, `RTF_CHANNEL`, `RTF_EXT`; getters/setters for TSFT, flags, rate, channel, FHSS, antenna signal/noise, lock quality, attenuation, TX power, antenna, FCS, retries, TX flags, xchannel, and `get_packet`; also uses `ImpactPacket.Data`.

Control flow: `setUp` builds four representative RadioTap frames with different present bit layouts. Tests read existing fields, insert absent fields, unset fields, serialize fresh RadioTap objects, and validate extended present-bit parsing.

State and persistence behavior: RadioTap instances mutate in memory. Setters modify present flags, byte layout, header length, and total size; no external persistence.

Dependencies and integration points: Core integration point for all RadioTap decoder tests and Dot11 frame decoding; payload containment is checked with `Data`.

Risks: Optional-field ordering and alignment are high-risk because adding/removing one field shifts later field offsets. Extended present words are also error-prone.

Test signals: Strong signal across field presence bits, dynamic length updates, serialization defaults, payload containment, and extended-present interpretation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_RadioTap.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_RadioTapDecoder.py -->
# sources/user-network-fs/impacket/tests/dot11/test_RadioTapDecoder.py

Purpose: Verifies end-to-end decoder chaining from RadioTap through Dot11 data, LLC, and SNAP layers.

Important APIs, types, and functions: Uses `RadioTapDecoder.decode`, `get_protocol`, and protocol classes `RadioTap`, `Dot11`, `Dot11DataFrame`, `LLC`, `SNAP`, and `Dot11WPA`.

Control flow: `setUp` decodes a raw RadioTap ARP packet and stores consecutive `child()` nodes. Tests assert class types at each decoded layer and verify protocol lookup returns instances already present in the decoded stack, while absent protocols return `None`.

State and persistence behavior: Decoder state is in-memory protocol-chain state; no persistent storage.

Dependencies and integration points: Integrates `ImpactDecoder` with `impacket.dot11` and `ImpactPacket` payload discovery. ARP/Data assertions are commented out, so coverage stops at SNAP for protocol types.

Risks: Reliance on stringified class names for Python 2 compatibility is brittle but intentional. `get_protocol` correctness depends on child-chain traversal order.

Test signals: Good signal for decoder dispatch, protocol stack linking, and protocol lookup failure behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_RadioTapDecoder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_WEPDecoder.py -->
# sources/user-network-fs/impacket/tests/dot11/test_WEPDecoder.py

Purpose: Tests decoding and decryption of an encrypted 802.11 WEP data frame into LLC/SNAP/IP/ICMP payloads.

Important APIs, types, and functions: Uses `Dot11`, `Dot11DataFrame`, `Dot11WEP`, `Dot11WEPData`, `KeyManager`, `Dot11Decoder`, `IP`, and `ICMP`. Exercises `is_WEP`, IV/key ID accessors, ICV accessors, `get_computed_icv`, `check_icv`, and protocol lookup.

Control flow: Setup manually parses Dot11 and WEP header/body objects and configures a `KeyManager`. Decoder tests then run `Dot11Decoder` with `FCS_at_end(False)` and the key manager to decrypt and walk the resulting protocol stack.

State and persistence behavior: Holds cryptographic key material and decrypted packet bytes in memory only.

Dependencies and integration points: Integrates WEP decryption with Dot11 decoder dispatch, key lookup by MAC address, and downstream IP/ICMP parsing.

Risks: Test vectors depend on exact RC4/WEP semantics and ICV endian handling. A likely typo calls `set_iv` inside the key ID test, so key ID setter coverage is incomplete.

Test signals: Strong signal for WEP frame recognition, decryption, ICV validation, decrypted payload bytes, and nested IP/ICMP extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_WEPDecoder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_WEPEncoder.py -->
# sources/user-network-fs/impacket/tests/dot11/test_WEPEncoder.py

Purpose: Validates construction and encryption of a WEP-protected Dot11 data frame from scratch.

Important APIs, types, and functions: Builds `Dot11`, `Dot11DataFrame`, `Dot11WEP`, `Dot11WEPData`, `LLC`, `SNAP`, `ImpactPacket.IP`, `ImpactPacket.ICMP`, `ImpactPacket.Data`, and `KeyManager`; exercises `get_icv`, `get_computed_icv`, `set_icv`, `get_encrypted_data`, and `encrypt_frame`.

Control flow: `setUp` constructs the full protocol stack with explicit frame-control flags, addresses, sequence numbers, WEP IV/key ID, LLC/SNAP, IP, ICMP, and payload data. Tests compare computed ICV and encrypted output against known bytes.

State and persistence behavior: All packet and key state is in memory. Encryption mutates the WEP frame payload.

Dependencies and integration points: Connects packet construction APIs to WEP encryption and lower-level IP/ICMP serialization.

Risks: Exact ciphertext is sensitive to IV, key bytes, payload serialization, and CRC/ICV byte order. The key manager is initialized but not directly used in assertions.

Test signals: Strong deterministic vector for WEP ICV computation and encrypted payload output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_WEPEncoder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_WPA.py -->
# sources/user-network-fs/impacket/tests/dot11/test_WPA.py

Purpose: Tests parsing of a WPA/TKIP-style Dot11 data frame header and encrypted payload metadata.

Important APIs, types, and functions: Uses `Dot11`, `Dot11DataFrame`, `Dot11WPA`, and `Dot11WPAData`; exercises `is_WPA`, `get/set_extIV`, `get/set_keyid`, `get/set_WEPSeed`, `get/set_TSC0` through `get/set_TSC5`, `get_MIC`, `set_MIC`, and `get_icv`.

Control flow: Setup parses a raw data frame into Dot11 data, WPA header, and WPA data body. Tests mutate header counter fields and validate body, MIC, and ICV extraction.

State and persistence behavior: Mutates packet bytes in memory only; no decryption state or key material is used.

Dependencies and integration points: Covers WPA header/body classes inside the Dot11 parser without invoking crypto.

Risks: Decryption is explicitly TODO, so this catches structural parsing but not TKIP correctness. Bitfield setters for extIV/key ID/TSC fields are the main risk.

Test signals: Provides regression vectors for WPA classification, counter field accessors, body slicing, MIC replacement, and ICV offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_WPA.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_WPA2.py -->
# sources/user-network-fs/impacket/tests/dot11/test_WPA2.py

Purpose: Tests structural parsing of WPA2/CCMP Dot11 data frames.

Important APIs, types, and functions: Uses `Dot11`, `Dot11DataFrame`, `Dot11WPA2`, `Dot11WPA2Data`; exercises `is_WPA2`, `get/set_extIV`, `get/set_keyid`, `get/set_PN0` through `get/set_PN5`, `WPA2Data.body_string`, `get_MIC`, and `set_MIC`.

Control flow: Setup parses a raw Dot11 data frame into WPA2 header/data objects. Tests mutate protected header fields, assert encrypted body slicing, and validate MIC replacement.

State and persistence behavior: In-memory packet parsing and mutation only. No crypto keys or decrypted payload state.

Dependencies and integration points: Tests the Dot11 protected-data subtype path and WPA2 packet classes, but not CCMP decryption.

Risks: Packet-number field offsets and bit masking are error-prone. Absence of decrypt tests means payload confidentiality/integrity logic is not covered here.

Test signals: Good structural signal for WPA2 recognition, PN field setters/getters, encrypted body boundaries, and MIC accessors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_WPA2.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_helper.py -->
# sources/user-network-fs/impacket/tests/dot11/test_helper.py

Purpose: Tests the descriptor/helper framework used to build `ProtocolPacket` classes.

Important APIs, types, and functions: Defines an inline `MockPacket` subclass of `impacket.helper.ProtocolPacket` using `Byte`, `Word`, `ThreeBytesBigEndian`, `Long`, and `Bit` descriptors plus `header_size` and `tail_size`.

Control flow: The test assigns descriptor-backed fields, checks readback, toggles a bit alias, and round-trips `get_packet()` through a new `MockPacket`.

State and persistence behavior: Descriptor state lives in the packet buffer in memory. No filesystem or network state.

Dependencies and integration points: Validates helper descriptors consumed by packet classes in `impacket.dot11` and related protocol modules.

Risks: Bit alias writes can overwrite adjacent byte-field content if masks are wrong. Round-trip serialization is the main guard against descriptor offset regressions.

Test signals: Small but useful signal for descriptor read/write behavior, bitfield aliasing, and packet reparse stability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_helper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_wps.py -->
# sources/user-network-fs/impacket/tests/dot11/test_wps.py

Purpose: Tests WPS TLV container serialization/deserialization with typed value builders.

Important APIs, types, and functions: Uses `wps.TLVContainer`, `wps.StringBuilder`, `wps.ByteBuilder`, `wps.NumBuilder`, `append`, `to_ary`, `from_ary`, and `first`.

Control flow: Builds a TLV container with builders for string, byte, and two-byte numeric types, appends known and unknown TLV kinds, serializes to an array, reparses into a second container, and compares values plus serialized output.

State and persistence behavior: TLV state is held in memory as array-like bytes. No persistence.

Dependencies and integration points: Supports WPS information element parsing used by wireless management-frame vendor-specific payloads.

Risks: Unknown TLV kinds must round-trip as raw byte arrays. Builder mismatches could alter byte order or value type on reparse.

Test signals: Validates normal builder dispatch, unknown-kind preservation, `first` lookup semantics, and stable serialization round-trip.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/dot11/test_wps.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/__init__.py -->
# sources/user-network-fs/impacket/tests/misc/__init__.py

Purpose: Package marker for the miscellaneous Impacket test package.

Important APIs, types, and functions: Defines no runtime APIs, imports, classes, or functions. It contains only the project license header.

Control flow: No executable control flow beyond module import.

State and persistence behavior: No state, persistence, or side effects.

Dependencies and integration points: Enables `tests.misc` to be treated as a Python package by older tooling and test discovery flows.

Risks: Minimal. Removing it could affect legacy import/package discovery even though modern namespace packages may not require it.

Test signals: No direct tests; its presence is structural.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ccache.py -->
# sources/user-network-fs/impacket/tests/misc/test_ccache.py

Purpose: Tests Kerberos credential cache loading, Kirbi conversion, and environment-driven cache parsing.

Important APIs, types, and functions: Uses `CCache.loadFile`, `CCache.loadKirbiFile`, `CCache.parseFile`, `CCache.getCredential`, `Credential`, `prettyPrint`, `pytest.mark.skipif`, and `unittest.mock.patch.dict`.

Control flow: Shared `assert_ccache` validates loaded caches. Tests verify nonexistent files, unsupported v1/v2 caches, valid v3/v4 ccache files, Kirbi inputs, absent `KRB5CCNAME`, missing cache paths, and domain/user filtering.

State and persistence behavior: Reads fixture files under `tests/data`; temporarily patches `os.environ` for `KRB5CCNAME`. No writes.

Dependencies and integration points: Integrates Kerberos ccache parser with filesystem fixtures and environment-based credential discovery.

Risks: Fixture paths are relative to the repository working directory. Python 2 skips environment-patching tests due to mock availability.

Test signals: Good signal for ccache format support, error handling, Kirbi conversion, and TGT/TGS selection from environment caches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ccache.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_crypto.py -->
# sources/user-network-fs/impacket/tests/misc/test_crypto.py

Purpose: Verifies generic AES-CMAC helper functions against published-style vectors.

Important APIs, types, and functions: Uses `Generate_Subkey`, `AES_CMAC`, `AES_CMAC_PRF_128`, plus local formatting helpers `by8`, `hex8`, and `pp`.

Control flow: Tests derive CMAC subkeys and compare them to fixed hex strings, then compute CMAC outputs for multiple message lengths and PRF outputs for multiple key lengths.

State and persistence behavior: Pure in-memory cryptographic vector tests. No external state.

Dependencies and integration points: Supports Kerberos and other protocol code that depends on Impacket's crypto primitives.

Risks: Formatting helpers compare grouped hex text, so failures show exact byte-level differences. The unused `M` variable in `test_subkey` is harmless.

Test signals: Strong deterministic vectors for subkey generation, zero/partial/full-block CMAC, and AES-CMAC-PRF-128 key-length behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_crypto.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_dcerpc_v5_ndr.py -->
# sources/user-network-fs/impacket/tests/misc/test_dcerpc_v5_ndr.py

Purpose: Regression-tests DCE/RPC NDR and NDR64 serialization for arrays, strings, padding, and null pointers.

Important APIs, types, and functions: Uses `NDRSTRUCT`, `NDRLONG`, `NDRSHORT`, `NDRUniFixedArray`, `NDRUniVaryingArray`, `NDRUniConformantVaryingArray`, `NDRVaryingString`, `NDRConformantVaryingString`, and `NDRPOINTERNULL`. Shared `NDRTest` supplies `create`, `do_test`, and round-trip validation.

Control flow: Each test class defines an inline NDR structure, populates it, serializes with and without `isNDR64`, checks hex output, reparses, and verifies reserialization stability.

State and persistence behavior: Pure in-memory serialization tests.

Dependencies and integration points: Protects low-level NDR packing used by all DCE/RPC v5 interfaces in Impacket.

Risks: NDR64 offset/count widths differ from classic NDR, making alignment regressions likely. Some conformant array coverage is commented out.

Test signals: Strong byte-level signal for fixed arrays, struct padding, varying/conformant strings and arrays, and null pointer representation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_dcerpc_v5_ndr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_dns.py -->
# sources/user-network-fs/impacket/tests/misc/test_dns.py

Purpose: Tests DNS packet stringification for queries and responses with compressed names and multiple record sections.

Important APIs, types, and functions: Uses `impacket.dns.DNS` and `str(DNS(packet_bytes))`; local `chk` helper compares full formatted output.

Control flow: Feeds raw DNS query/response bytes for several domains into `DNS`, then asserts the exact multi-line string representation, including header fields, questions, answers, authority, and additional records.

State and persistence behavior: Pure parser/formatter tests over in-memory bytes.

Dependencies and integration points: Validates DNS parser behavior used by packet inspection and display paths.

Risks: Exact string comparison is intentionally brittle; harmless formatting changes will fail tests. Name compression handling is central because many records use pointers.

Test signals: Good signal for DNS header counts, query/response classification, CNAME/A/NS record formatting, TTLs, IP addresses, compressed domain decoding, and section ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_dns.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_dpapi.py -->
# sources/user-network-fs/impacket/tests/misc/test_dpapi.py

Purpose: Tests DPAPI parsing/decryption helpers for system keys, master keys, credentials, protected blobs, and Windows Vault files.

Important APIs, types, and functions: Uses `DPAPI_SYSTEM`, `MasterKeyFile`, `MasterKey`, `CredentialFile`, `DPAPI_BLOB`, `CREDENTIAL_BLOB`, `VAULT_VPOL`, `VAULT_VPOL_KEYS`, `VAULT_VCRD`, `VAULT_KNOWN_SCHEMAS`, `AES`, `HMAC`, `MD4`, and `SHA1`. Includes `dpapi_protect` ctypes helper for Windows-only blob generation.

Control flow: Tests parse static binary fixtures embedded as byte literals, decrypt master keys and blobs with known keys/entropy, derive user keys, decrypt vault policy/credential data, and skip live Windows protection outside Windows.

State and persistence behavior: Uses embedded fixture bytes and in-memory crypto. `dpapi_protect` calls Windows CryptoAPI only in the skipped Windows-specific test.

Dependencies and integration points: Integrates DPAPI structures with PyCryptodome primitives and Windows credential/vault schema parsing.

Risks: Large embedded vectors are hard to audit and brittle to structure changes. `atest_adminMasterKeyFile` is intentionally not discovered because it is prefixed `atest`.

Test signals: Strong signal for DPAPI_SYSTEM parsing, master key decryption, credential blob username extraction, optional entropy handling, VPOL key extraction, and VCRD schema decryption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_dpapi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ese.py -->
# sources/user-network-fs/impacket/tests/misc/test_ese.py

Purpose: Tests ESENT large-page tag parsing, especially high-bit reserved tag state.

Important APIs, types, and functions: Uses `ESENT_PAGE`, `ESENT_PAGE_HEADER`, `FIRST_AVAILABLE_PAGE_TAG_MASK`, and `FIRST_AVAILABLE_PAGE_TAG_RESERVED_SHIFT`. Helper `_build_page` constructs synthetic 32 KiB pages.

Control flow: Builds page headers and trailing page tags with controlled `FirstAvailablePageTag` values, then verifies tag count/reserved splitting, tag retrieval, bounds errors, and data-tag iteration skipping reserved tags.

State and persistence behavior: Pure in-memory synthetic page bytes. No ESE files are read.

Dependencies and integration points: Protects ESE database page parsing used by offline database readers.

Risks: Large page tag metadata packs reserved and count bits together; misinterpreting high bits can expose reserved tags as records or break iteration.

Test signals: Strong targeted regression signal for high-bit tag state, reserved tag skipping, tag payload lookup, and invalid tag errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ese.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ip6_address.py -->
# sources/user-network-fs/impacket/tests/misc/test_ip6_address.py

Purpose: Tests IPv6 address parsing, byte conversion, canonical string compression, and malformed input handling.

Important APIs, types, and functions: Uses `IP6_Address`, `as_bytes`, `as_string`, `six.assertRaisesRegex`, and local `hexl`.

Control flow: Iterates valid IPv6 strings, asserts exact 16-byte hex output and canonical compressed string output, then checks several invalid forms raise expected error messages.

State and persistence behavior: Pure in-memory value parsing.

Dependencies and integration points: Supports packet/address code that consumes Impacket's `IP6_Address` helper.

Risks: IPv6 zero-compression and malformed-colon detection are easy to mishandle. Additional invalid cases are noted but commented out, so coverage is not exhaustive.

Test signals: Covers full addresses, internal zero compression, leading/trailing double-colon forms, all-zero address, oversized group rejection, and triple-colon rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ip6_address.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_krb5_crypto.py -->
# sources/user-network-fs/impacket/tests/misc/test_krb5_crypto.py

Purpose: Validates Kerberos crypto implementations against deterministic vectors across AES, DES3, RC4, and DES string-to-key.

Important APIs, types, and functions: Uses `Key`, `Enctype`, `encrypt`, `decrypt`, `Cksumtype`, `verify_checksum`, `_zeropad`, `string_to_key`, `prf`, and `cf2`.

Control flow: Each test builds keys from hex or string-to-key inputs, runs encryption/decryption, checksum verification, PRF, or CF2 combination, and compares exact bytes.

State and persistence behavior: Pure in-memory crypto tests. No tickets or keytabs are read.

Dependencies and integration points: Core coverage for Kerberos AS/TGS, PAC signing, and GSSAPI code paths that rely on these primitives.

Risks: Crypto vector changes may indicate serious interoperability regressions. DES/RC4 legacy paths remain covered despite weaker algorithms because Kerberos deployments can still encounter them.

Test signals: Strong signal for AES128/AES256 encryption/checksum/string-to-key/PRF/CF2, DES3 encryption/checksum/string-to-key/CF2, RC4 encryption/checksum/string-to-key/CF2, and DES MD5 string-to-key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_krb5_crypto.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_krb5_gssapi.py -->
# sources/user-network-fs/impacket/tests/misc/test_krb5_gssapi.py

Purpose: Tests Kerberos GSSAPI token framing, implementation selection, MIC padding, RC4 wrap/MIC behavior, LDAP wrap round-trip, and AES rotate helpers.

Important APIs, types, and functions: Uses `GSSAPI`, `GSSAPI_RC4`, `GSSAPI_AES128`, `GSSAPI_AES256`, `MechIndepToken`, `KRB_OID`, `_calculateMICPad`, and Kerberos encryption type constants. `_SessionKey` supplies minimal `.contents`.

Control flow: Tests invalid token tags, short/long DER length encoding, token round-trip, MIC pad calculation, factory dispatch by enctype, direction-sensitive RC4 MICs, no-encryption RC4 wrapping, LDAP wrap/unwrap, and AES rotate/unrotate inverse behavior.

State and persistence behavior: In-memory tokens and synthetic session keys only.

Dependencies and integration points: Covers GSSAPI paths used by SMB/LDAP/Kerberos authentication integrations.

Risks: Token length encoding and direction-specific sequence handling are interoperability-sensitive. Tests use synthetic keys, so external KDC behavior is not covered.

Test signals: Good signal for token framing, supported enctype selection, unsupported enctype rejection, RC4 MIC/wrap behavior, LDAP sealing round-trip, and AES rotation helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_krb5_gssapi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ntfs_read.py -->
# sources/user-network-fs/impacket/tests/misc/test_ntfs_read.py

Purpose: Unit-tests `examples/ntfs-read.py` logic for nonresident data runs, reading, attribute lists, directory walking, and data-size reporting.

Important APIs, types, and functions: Dynamically imports `examples/ntfs-read.py` via `importlib.util`; uses `AttributeNonResident`, `AttributeListEntry`, `AttributeList`, `INODE`, constants `DATA`, `FILE_NAME`, `FILE_NAME_WIN32`, `FILE_NAME_DOS`, `INDEX_ROOT`, plus mock BPB/volume/inode/index fixtures and binary builders.

Control flow: Helper builders synthesize NTFS attribute records. Test classes cover data-run parsing, sparse runs, negative deltas, multi-run VCN ranges, truncated data-run handling, `readVCN`, read clamping/zero-fill/partial offsets, attribute-list entry parsing, attribute-list iteration, directory walk filtering, and `getDataSize`.

State and persistence behavior: Uses `io.BytesIO` as a mock disk volume; no real filesystem or NTFS image is read.

Dependencies and integration points: Integrates example-script parsing logic with generated raw NTFS structures and volume-style reads.

Risks: The tested script has a hyphenated filename and is loaded dynamically, so path assumptions matter. Data-run parsing is complex and failure-prone around signed offsets, sparse regions, and truncation.

Test signals: Strong signal for NTFS nonresident read correctness, sparse zero filling, EOF behavior, attribute-list robustness, directory walk filtering, and initialized/data size distinction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ntfs_read.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_pac_helpers.py -->
# sources/user-network-fs/impacket/tests/misc/test_pac_helpers.py

Purpose: Tests Kerberos PAC helper functions for explicit buffer ordering and AES checksum type inference.

Important APIs, types, and functions: Uses `pac.build_pac_type`, `pac.sign_pac`, `PAC_INFO_BUFFER`, `PAC_SIGNATURE_DATA`, PAC type constants, and Kerberos checksum constants.

Control flow: The first test builds PAC buffers from a dictionary with an explicit order and parses the serialized buffer list to assert order. The second builds placeholder server/private checksums, signs with an AES128 key, and validates checksum type updates and signature lengths.

State and persistence behavior: In-memory PAC byte structures only.

Dependencies and integration points: PAC construction/signing is used by Kerberos ticket tooling, especially forged ticket generation.

Risks: Buffer ordering affects PAC consumer interoperability. Checksum type inference from key length can silently choose the wrong checksum if key encoding assumptions change.

Test signals: Covers ordered PAC serialization, in-place PAC checksum data updates, AES128 checksum inference, and expected four-buffer PAC output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_pac_helpers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_socksserver.py -->
# sources/user-network-fs/impacket/tests/misc/test_socksserver.py

Purpose: Regression-tests SOCKS request handling for a successful relay tunnel to ensure no extra failure reply is sent.

Important APIs, types, and functions: Uses `SocksRequestHandler`, `socket`, `struct`, `unittest.mock`, and `_SuccessfulRelay` with `initConnection`, `skipAuthentication`, and `tunnelConnection`.

Control flow: Builds a mock SOCKS5 connection with greeting and connect request bytes, injects server relay/plugin state into a manually allocated handler, runs `handle`, and asserts two sends plus relay `inUse` cleanup.

State and persistence behavior: Uses mock socket/server state only. The handler mutates `activeRelays` in memory by toggling `inUse`.

Dependencies and integration points: Covers ntlmrelayx SOCKS server integration with protocol plugin lifecycle.

Risks: Manual private-attribute setup is brittle if handler internals are renamed. The test is narrow but targets a user-visible protocol bug.

Test signals: Confirms successful tunnel path sends only expected SOCKS replies and releases relay state after handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_socksserver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_structure.py -->
# sources/user-network-fs/impacket/tests/misc/test_structure.py

Purpose: Regression-tests Impacket's generic `Structure` binary packing/unpacking DSL across strings, arrays, alignment, nested structures, optional pointers, computed fields, and error reporting.

Important APIs, types, and functions: Uses `impacket.structure.Structure`, shared `_StructureTest`, `hexl`, and multiple inline `Structure` subclasses with format codes such as `z`, `u`, `w`, `:`, `B*<L`, `_`, length expressions, optional pointer syntax, and alignment.

Control flow: Shared tests populate structures, serialize, compare expected hex, reparse, and reserialize. Specialized tests cover bogus length failure, aligned packing, UTF-16 embedded NUL handling, nested structures, optional sparse pointers, ASCII-Z arrays, unpack-code fields, clear errors for missing NUL terminators, and computed bitfield decomposition.

State and persistence behavior: Pure in-memory serialization tests.

Dependencies and integration points: `Structure` underpins many Impacket protocol parsers, so this suite protects broad binary parsing behavior.

Risks: Format-expression evaluation and alignment changes have wide blast radius. Exact byte assertions are deliberately brittle to catch layout changes.

Test signals: Strong signal for round-trip stability, alignment, pointer optionality, string termination errors, nested packing, computed fields, and field-name-rich exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_structure.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_tds.py -->
# sources/user-network-fs/impacket/tests/misc/test_tds.py

Purpose: Tests TDS/MSSQL packet serialization, TDS 8 negotiation behavior, packet receive buffering, SQL batch wrapping, and MSSQL SOCKS relay TDS8 handling.

Important APIs, types, and functions: Uses `tds.TDSPacket`, `TDS_PRELOGIN`, `TDS_INFO_ERROR`, `TDS_INFO_ERROR72`, `TDS_LOGIN`, `MSSQL`, constants such as `TDS_PRE_LOGIN`, `TDS_TABULAR`, `TDS_ENCRYPT_STRICT`, and `MSSQLSocksRelay`.

Control flow: `TDSTests` builds packets and mocks MSSQL sockets/prelogin behavior to validate serialization, retry policy, TDS8 wrapping, partial reads, and buffered next-packet handling. `MSSQLSocksRelayTests` mocks relay sessions and sockets to validate strict encryption advertisement, TLS-first local clients, wrapping policy, and partial reads from local clients.

State and persistence behavior: Uses mocked sockets and in-memory buffers. `recvTDS` maintains buffered bytes across calls.

Dependencies and integration points: Integrates core `impacket.tds` with ntlmrelayx MSSQL SOCKS plugin behavior.

Risks: Packet reassembly and TDS8 negotiation are network-state-sensitive. Timeout vs connection-close retry behavior is intentionally distinct.

Test signals: Strong signal for TDS length fields, default login version, TDS8 retry/wrap logic, partial TLS reads, buffered packet preservation, strict encryption negotiation, and relay wrapping decisions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_tds.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ticketer.py -->
# sources/user-network-fs/impacket/tests/misc/test_ticketer.py

Purpose: Tests `examples.ticketer.TICKETER` ticket-time extraction and reuse for requested Kerberos tickets.

Important APIs, types, and functions: Uses `TICKETER`, `EncASRepPart`, `EncTGSRepPart`, `EncTicketPart`, `EncryptionTypes`, `PrincipalNameType`, `TicketFlags`, `encodeFlags`, `KerberosTime`, pyasn1 `encoder`, `noValue`, `mock.patch`, and `SimpleNamespace` options.

Control flow: Helpers build synthetic options and DER-encoded AS/TGS reply parts with fixed timestamps. Tests patch `_enctype_table` with fake ciphers to assert key usage, verify fallback handling for missing optional times, mock `getKerberosTGT` and decoder wiring, then seed requested times and validate `customizeTicket` applies them to both encrypted reply and ticket parts.

State and persistence behavior: In-memory ASN.1 structures. `TICKETER` stores requested times in private `__requested_ticket_times`.

Dependencies and integration points: Integrates ticket generation example code with Kerberos ASN.1, crypto table dispatch, and KDC-request reuse behavior.

Risks: Private attribute assertions are coupled to implementation internals. Timestamp handling is sensitive to optional ASN.1 fields and AS/TGS key-usage differences.

Test signals: Strong signal for reply decryption key usage, time extraction, optional time fallbacks, request wiring, and requested-lifetime reuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_ticketer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_tsts.py -->
# sources/user-network-fs/impacket/tests/misc/test_tsts.py

Purpose: Tests Terminal Services Runtime Interface helpers for SID conversion and process-info SID extraction.

Important APIs, types, and functions: Uses `impacket.dcerpc.v5.tsts.binary_sid_to_string`, `RpcWinStationGetAllProcessesResponse`, and `TS_ALL_PROCESSES_INFO`.

Control flow: One test converts a binary SYSTEM SID to canonical SID text. The other constructs a response with one process entry, populates nested pointer data and SID bytes, serializes, reparses, and asserts `getSid()` returns `SYSTEM`.

State and persistence behavior: In-memory NDR structures only.

Dependencies and integration points: Covers TSTS DCE/RPC structure parsing and SID display logic.

Risks: Nested pointer field manipulation is brittle and depends on NDR field internals. SID alias mapping must stay consistent.

Test signals: Good targeted signal for binary SID conversion, populated pointer serialization, response reparse, and friendly SID mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_tsts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_utils.py -->
# sources/user-network-fs/impacket/tests/misc/test_utils.py

Purpose: Tests example-script credential and target parsing helpers.

Important APIs, types, and functions: Uses `parse_target` and `parse_credentials` from `impacket.examples.utils`.

Control flow: Each test defines a dictionary of input strings to expected tuples and loops through them with `assertTupleEqual`. `parse_target` cases include host-only, username, password, domain, slashes, colons, and passwords containing `@`. `parse_credentials` cases cover domain, username, password, extra colons, and slash-containing passwords.

State and persistence behavior: Pure string parsing; no external state.

Dependencies and integration points: These helpers are widely used by Impacket example CLI tools for interpreting user-supplied targets and credentials.

Risks: Ambiguous delimiters in passwords are common user-facing edge cases. The tests intentionally preserve `@`, `:`, and `/` inside password fields where appropriate.

Test signals: Good signal for parsing empty inputs, domain/user separators, target host extraction, password delimiter handling, and credential-only parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/misc/test_utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tests/walkmodules.py -->
# sources/user-network-fs/impacket/tests/walkmodules.py

Purpose: Smoke script that imports every module under the `impacket` package to surface import-time failures.

Important APIs, types, and functions: Uses `pkgutil.walk_packages`, `impacket.__path__`, dynamic `__import__`, and `traceback.print_exc`.

Control flow: Iterates discovered modules with the `impacket.` prefix. Each module import is attempted inside `try/except`; exceptions are printed and swallowed so the walk continues.

State and persistence behavior: Import-time side effects of modules may occur, but this script itself stores no durable state and writes only to stdout/stderr.

Dependencies and integration points: Broad integration smoke check for package importability and dependency availability.

Risks: Swallowing exceptions means process exit can still be successful even if imports fail. Importing all modules can trigger unintended import-time behavior in modules not designed for eager loading.

Test signals: Useful manual/CI diagnostic for import regressions, but weak as an automated pass/fail gate unless wrapped to fail on printed exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tests/walkmodules.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/impacket/tox.ini -->
# sources/user-network-fs/impacket/tox.ini

Purpose: Defines Impacket's tox test matrix, pytest/coverage commands, GitHub Actions Python mapping, and coverage reporting configuration.

Important APIs, types, and functions: Configures `[tox] envlist` for `clean`, Python 3.6-3.11, and `report`; `[gh-actions]` version mapping; `[testenv]` dependencies, `REMOTE_CONFIG` pass-through, `pip check`, and `pytest --cov`; coverage clean/report/html environments; pytest marker `remote`; and coverage omit/exclude rules.

Control flow: Tox runs `clean` before Python test environments, appends coverage per environment, then runs `report`. `py311` is allowed to ignore errors.

State and persistence behavior: Creates coverage data and HTML reports during tox runs. Passes `REMOTE_CONFIG` from the host environment for remote tests.

Dependencies and integration points: Integrates tox, pytest, coverage, requirements-test.txt, and GitHub Actions matrix selection.

Risks: `py311 ignore_errors = true` can hide failures on that interpreter. Coverage paths omit `remcom` and `.tox`; broad exclusions can mask untested defensive paths.

Test signals: Defines the primary local/CI test contract, multi-version compatibility coverage, remote marker metadata, and coverage reporting behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/impacket/tox.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/.github/workflows/c-cpp.yml -->
# sources/user-network-fs/ksmbd-tools/.github/workflows/c-cpp.yml

Purpose: GitHub Actions workflow for ksmbd-tools CI builds across autotools and Meson, with and without Kerberos support.

Important APIs, types, and functions: Workflow `ksmbd-tools CI` triggers on pushes and pull requests to `master` and `next`; one `build` job runs on `ubuntu-latest`; steps use `actions/checkout@v4`, apt package installation, `pip3 install --user meson`, `./autogen.sh`, `configure`, `make distcheck`, and `meson dist`.

Control flow: Installs build prerequisites, prints compiler versions, bootstraps autotools, then runs six build/dist lanes: autotools without krb5, autotools with MIT krb5, autotools with Heimdal krb5, Meson without krb5, Meson with MIT krb5, and Meson with Heimdal krb5.

State and persistence behavior: Creates temporary build directories inside the CI workspace. No artifacts are explicitly uploaded.

Dependencies and integration points: Integrates Ubuntu packages for netlink, GLib, MIT/Heimdal Kerberos, Ninja, Meson, autotools, and ksmbd-tools packaging checks.

Risks: `PATH=$HOME/.local/bin:$PATH` is scoped only within that shell step, but all Meson invocations occur in later steps where GitHub may not preserve the assignment. Package names and distro versions can change on `ubuntu-latest`.

Test signals: Strong build/distribution signal across both supported build systems and Kerberos provider variants, but no runtime tests are shown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/.github/workflows/c-cpp.yml -->
