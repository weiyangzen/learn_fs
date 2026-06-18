# `sources/user-network-fs/impacket/impacket/mapi_constants.py` Lines 1-2895

## Purpose

This chunk defines Impacket's MAPI/Exchange constant catalog for NSPI, OXABREF, and the `examples/exchanger.py` tooling. It is a data-only module: importing it creates lookup dictionaries and integer constants used to decode MAPI HRESULTs, address book display/object metadata, address book container flags, and a large property-id metadata table.

The top of the file cites MAPI error and property references, then exposes four main lookup surfaces:

- `ERROR_MESSAGES`: MAPI, SYNC, and LDAP-style error codes mapped to symbolic names.
- `PR_DISPLAY_TYPE_VALUES`: `PR_DISPLAY_TYPE` numeric values for address-book, hierarchy, and folder rows.
- `PR_OBJECT_TYPE_VALUES`: MAPI object type IDs such as stores, folders, messages, attachments, sessions, and address book containers.
- `PR_CONTAINER_FLAGS_VALUES`: NSPI address book container bit flags.
- `MAPI_PROPERTIES`: property ID metadata mapping MAPI property IDs to type, Active Directory schema names, documented MS-OXPROPS names, alternate `PR_*` names, and Exchange internal names.

## Important APIs, Types, And Constants

There are no functions or classes in this line range. The public API is the module namespace itself.

`ERROR_MESSAGES` maps integer HRESULT-like status values to a single symbolic string, for example `MAPI_E_NOT_FOUND`, `MAPI_E_LOGON_FAILED`, `MAPI_E_NO_ACCESS`, `SYNC_E_CONFLICT`, and LDAP-related names such as `LDAP_SERVER_DOWN`. Lines 113-201 also publish the same numeric values as module-level constants, so callers can either compare against constants or lookup status names.

`PR_DISPLAY_TYPE_VALUES` is paired with constants such as `DT_MAILUSER`, `DT_DISTLIST`, `DT_GLOBAL`, `DT_FOLDER`, and `DT_FOLDER_SPECIAL`. It is intended for decoding `PR_DISPLAY_TYPE` values in address book contents, hierarchy, and folder hierarchy tables.

`PR_OBJECT_TYPE_VALUES` is paired with constants such as `MAPI_STORE`, `MAPI_ADDRBOOK`, `MAPI_FOLDER`, `MAPI_MESSAGE`, `MAPI_ATTACH`, and `MAPI_DISTLIST`. It gives string names for object type numeric values found in MAPI objects.

`PR_CONTAINER_FLAGS_VALUES` names bit values such as `AB_RECIPIENTS`, `AB_SUBCONTAINERS`, `AB_MODIFIABLE`, `AB_FIND_ON_OPEN`, and `AB_CONF_ROOMS`. `examples/exchanger.py` passes this dictionary into its `parse_bitmask()` helper to render NSPI hierarchy flags.

`MAPI_PROPERTIES` is the core table. Each key is a property ID, not a full property tag. Each value is an eight-field tuple:

`(PropertyType, ldapDisplayName, activeDirectoryCN, partialAttributeSetState, canonicalName, firstAlternateName, exchangeInternalName)`

The in-file comments define `partialAttributeSetState` as `1` for true, `2` for false, `3` for missing, and `4` for non-Active-Directory properties. Property types use MAPI property type IDs, including common values like `0x001f` Unicode string, `0x101f` multivalue Unicode string, `0x0003` integer, `0x000b` boolean, `0x0040` FILETIME, `0x0102` binary, `0x1102` multivalue binary, `0x000d` object/embedded table, and less common forms such as `0x0014` 64-bit integer and `0x0048` GUID.

## Table Coverage In This Chunk

The first part of `MAPI_PROPERTIES` covers address-book and Active Directory-backed Exchange attributes. Examples include identity and display attributes (`displayNamePrintable`, `mailNickname`, `givenName`, `sn`, `company`, `title`, `department`), contact details (`telephoneNumber`, `homePhone`, `mobile`, `pager`, address fields), certificates and object identity (`userCert`, `userSMIMECertificate`, `objectSid`, `objectGUID`, `thumbnailPhoto`), mailbox and routing data (`homeMDB`, `homeMTA`, `proxyAddresses`, `targetAddress`, delivery restrictions), moderation and hierarchical address book properties, resource room metadata, and extension attributes.

The middle of the table switches to non-AD named and tagged MAPI properties with state `4`. It includes Outlook/Exchange property families for appointments, recurrence, reminders, tasks, contacts, notes, RSS posts, sharing, conversation actions, body formats, recipients, delivery reports, attachments, folders, rules, search folders, free/busy, junk mail, retention, views, sync/change tracking, and store/profile configuration.

The later lines in this chunk add many Exchange internal and mailbox-store fields where canonical and alternate names are absent but internal names are present. These cover profile and transport state, store well-known folder entry IDs, search indexing fields, OOF and assistant control data, public folder and quota fields, logon and resource counters, conversation aggregate fields, mailbox user information properties, BigFunnel/MCDB indexing metrics, compliance/retention assistants, group mailbox state, and resource usage aggregation.

## Control Flow

This file has no runtime branching, loops, parsing, IO, or protocol calls in the requested range. Control flow is limited to Python import-time evaluation of literal assignments. Consumers perform lookup operations after import.

The effective lookup flow in downstream code is:

1. Import `mapi_constants`.
2. For an RPC/MAPI error code, test membership in `ERROR_MESSAGES` and render the symbolic string.
3. For address-book flag bitmasks, use `PR_CONTAINER_FLAGS_VALUES` to translate set bits.
4. For NSPI row properties, derive `PropertyId = aulPropTag >> 16` and `PropertyType = aulPropTag & 0xffff`; then use `MAPI_PROPERTIES[PropertyId]` to choose a display name.

`examples/exchanger.py` prefers `MAPI_PROPERTIES[PropertyId][1]` (`ldapDisplayName`) for row output, then falls back to the canonical MS-OXPROPS name and finally the Exchange internal name. This means tuple field ordering is a contract, not incidental formatting.

## State And Persistence Behavior

The module owns only immutable-looking module globals, but the dictionaries are ordinary mutable Python dictionaries. No code in this chunk persists data, opens files, writes network state, caches computed values, or protects the tables against mutation by importers.

Because table construction happens at import time, every importing process pays the memory cost of a large `MAPI_PROPERTIES` dictionary. There is no lazy loading and no validation pass over duplicate property IDs or tuple shape.

## Dependencies

This chunk has no imports. It depends only on Python literal syntax and the external correctness of the referenced Microsoft/Exchange property data. Downstream modules depend on it:

- `impacket/dcerpc/v5/nspi.py` imports `mapi_constants` and uses `ERROR_MESSAGES` in `DCERPCSessionError.__str__`.
- `impacket/dcerpc/v5/oxabref.py` does the same for OXABREF errors.
- `examples/exchanger.py` imports `PR_CONTAINER_FLAGS_VALUES` and `MAPI_PROPERTIES` for address-book hierarchy and property row rendering.

## Integration Points

The NSPI and OXABREF integrations expect `ERROR_MESSAGES` values to be strings. This differs from Impacket's generic `hresult_errors.ERROR_MESSAGES`, where values are two-item tuples. Code in `nspi.py` and `oxabref.py` correctly treats MAPI constants as direct strings and hresult entries as tuples.

The address-book tooling integrates at the property-tag level by extracting the high 16-bit property ID before indexing `MAPI_PROPERTIES`. As a result, type variants of the same property ID share the same metadata row. This fits the table's design but can lose information if a property ID is returned with a type different from the table's preferred or Unicode type.

The display/object/flag maps are intended for user-readable decoding and diagnostics rather than protocol serialization. The numeric constants are still useful for comparisons in new protocol helpers.

## Risks And Edge Cases

Duplicate property IDs are a structural risk. Python silently keeps the last entry for a duplicated key, so a later row can override earlier metadata without warning. This matters because `MAPI_PROPERTIES` combines AD attributes, named properties, tagged properties, and internal Exchange names in a single dictionary keyed only by property ID.

The `ERROR_MESSAGES` value shape is inconsistent with other Impacket error tables. New callers might assume tuple values and incorrectly index strings, or might accidentally pass these values into formatting code written for `hresult_errors`.

The property table is authoritative-looking but not self-validating. Typos in symbolic names, internal names, property types, or partial attribute state values will only surface as misleading decoded output. The module also includes legacy and internal Exchange properties that may not be stable across server versions.

Because `MAPI_PROPERTIES` is keyed by property ID only, named properties that share an ID in different property sets cannot be disambiguated by GUID/property-set context. Callers needing exact named-property identity must combine this table with named-property mapping data from protocol responses.

The table defaults to Unicode variants where possible. That is useful for display, but callers constructing exact property tags must not blindly combine a returned property ID with the table's stored type when the server supplied another type or an error type such as `0x000a`.

## Test Signals

Useful low-level checks for this chunk are import and shape checks:

- `python -m py_compile impacket/mapi_constants.py` should succeed.
- Importing `impacket.mapi_constants` should expose `ERROR_MESSAGES`, `PR_DISPLAY_TYPE_VALUES`, `PR_OBJECT_TYPE_VALUES`, `PR_CONTAINER_FLAGS_VALUES`, and `MAPI_PROPERTIES`.
- Every `MAPI_PROPERTIES` value should be a tuple of length 7, matching the comment's fields 2-8.
- Known lookups should remain stable: `MAPI_E_NOT_FOUND` should equal `0x8004010f`, `ERROR_MESSAGES[0x8004010f]` should name `MAPI_E_NOT_FOUND`, `PR_CONTAINER_FLAGS_VALUES[0x00000002]` should name `AB_SUBCONTAINERS`, and `MAPI_PROPERTIES[0x3001]` should identify display name metadata.

Integration tests should exercise `examples/exchanger.py` row rendering with known property tags for an AD-backed property, a documented MAPI-only property, and an internal-name-only property. Error formatting tests for `nspi.DCERPCSessionError` and `oxabref.DCERPCSessionError` should include one MAPI error and one generic HRESULT fallback to catch the string-versus-tuple distinction.
