# sources/user-network-fs/impacket/impacket/mapi_constants.py lines 2896-3582

## Scope

This chunk is the final slice of `MAPI_PROPERTIES` in `impacket/mapi_constants.py`. It starts at property id `0x35eb` (`UMVoicemailFolderEntryId`) and runs through the dictionary close at EOF, ending with `0x8d0d` (`ExternalDirectoryObjectId`). The range contains 686 MAPI property-id entries.

The source is declarative constant data, not executable protocol logic. Each entry maps a 16-bit MAPI property id to a seven-element tuple documented near the start of `MAPI_PROPERTIES`: property type, optional Active Directory LDAP display name, optional Active Directory CN, partial-attribute-set status, optional MS-OXPROPS canonical name, optional PR-style alternate name, and internal Exchange property name. In this chunk all entries have AD metadata and public canonical names set to `None`, the partial-attribute-set classification set to `4`, and the internal Exchange name populated.

## Purpose

`MAPI_PROPERTIES` is Impacket's local lookup table for translating property ids observed in Exchange/MAPI responses into readable names and expected MAPI property types. This chunk extends the table with non-Active-Directory, largely Exchange-internal properties covering folder identifiers, search and indexing state, BigFunnel and assistant control data, FastTransfer/incremental sync markers, replication identifiers, mailbox quota and profile state, event and inference telemetry, conversation/person/signal metadata, user photo/cache fields, and cloud or compliance-related flags.

Because this is the tail of the table, it also owns the syntactic close of `MAPI_PROPERTIES`; malformed edits here can break import of the whole `impacket.mapi_constants` module.

## Data Shape And Important APIs

There are no functions or classes in this line range. The exported API affected by the chunk is the module-level dictionary:

- `MAPI_PROPERTIES[property_id][0]`: MAPI property type. Common values in this range include `0x0102` binary, `0x0003` 32-bit integer, `0x001f` Unicode string, `0x000b` Boolean, `0x0040` FILETIME, `0x0014` 64-bit integer, `0x0048` GUID, plus multivalue forms such as `0x101f`, `0x1003`, `0x1102`, and `0x1014`.
- `MAPI_PROPERTIES[property_id][1]` and `[2]`: Active Directory names. In this chunk they are consistently `None`.
- `MAPI_PROPERTIES[property_id][3]`: classification value. Every entry in this chunk uses `4`, meaning "not an Active Directory property" per the table comment.
- `MAPI_PROPERTIES[property_id][4]` and `[5]`: canonical and PR alternate names. These are also consistently `None` in this chunk.
- `MAPI_PROPERTIES[property_id][6]`: internal Exchange name. This is the meaningful display label for every property in the chunk.

Type distribution in the assigned range is a useful maintenance signal: 225 binary properties, 168 integer32 properties, 130 Unicode string properties, 61 Boolean properties, 32 FILETIME properties, 25 integer64 properties, 12 GUID properties, and a small set of multivalue string/integer/binary/GUID variants.

## Property Families Covered

The `0x35xx` and `0x36xx` entries are mostly folder, mailbox, and search/indexing identifiers: Recoverable Items folders (`DeletionsFolderEntryId`, `PurgesFolderEntryId`, `DiscoveryHoldsFolderEntryId`, `VersionsFolderEntryId`), archive/system/public folder entry ids, packed named properties, content indexing flags, search folder diagnostics, BigFunnel point-of-interest fields, folder views, aging policy, public folder split/processor state, and low-latency container quota fields.

The `0x3dxx` and `0x3exx` groups add security descriptor and ACL fields, BigFunnel posting-list maintenance state, mailbox move and tenant hints, internal conversation/change keys, virtual read/unread state, identity/resource/status fields, and remote-progress fields.

The `0x3fxx` and `0x40xx` groups include control layout metadata, attachment and replica identifiers, ACL checksums, rule/move targets, quota type, FastTransfer stream markers (`StartMessage`, `EndAttachment`, `IncrSyncChange`, `FastTransferDelProp`, `IdsetGiven`), sender/recipient flag fields, creator/modifier/report address fields, original-address variants, and incremental sync progress/control properties.

The `0x5dxx`, `0x60xx`, `0x65xx`, `0x66xx`, and `0x67xx` groups cover SMTP address variants, SIP URI, RSS lock state, scheduling/rule message blobs, profile settings, deleted item counts, ICS/change keys, internet content, mailbox/folder quota counters, replication timing/status, mailbox ownership, delivery policy, reserved counter ranges, public folder search/categorization sets, change-number sets, CAI address identity blobs, and ICS view/filter metadata.

The `0x68xx` and `0x69xx` groups are dominated by event, inference, activity, delegate, immutable id, person, conversation, and signal telemetry properties. They include event folder/message ids, inference session/window ids, activity container ids, delegate entry ids/flags, mailbox-wide person fields, conversation preview/member/category/thread/mention state, and client signal fields such as app id, tenant id, device id, IP, user agent, location, locale, and timestamp.

The `0x70xx`, `0x7cxx`, `0x7dxx`, `0x7fxx`, and final `0x8d0d` entries add assistant control blobs, People Relevance counters, mailbox feature storage, favorites and sync state, photo cache ids, immutable id replacement/cloud-cache status, dynamic time-based assistant control data, tenant size estimate, ATP/DLP markers, and `ExternalDirectoryObjectId`.

## Control Flow

There is no runtime branching in this chunk. The only control-flow effect is Python import-time evaluation of the dictionary literal. After import, callers perform ordinary dictionary lookup by property id.

The main consumer found in this source tree is `examples/exchanger.py`. Its `print_row` method derives `PropertyId = aulPropTag >> 16`, checks membership in `MAPI_PROPERTIES`, then chooses a display name from tuple index `[1]`, falling back to `[5]`, then `[6]`. For this chunk, the fallback to `[6]` is the path that produces useful names because all LDAP and alternate-name fields are `None`.

## State And Persistence Behavior

This chunk does not persist data and has no mutable internal state beyond the module-level dictionary object. The dictionary is effectively static reference data for a running process.

The represented properties themselves often name persistent Exchange mailbox, folder, sync, replication, assistant, telemetry, or compliance state, but `mapi_constants.py` only labels those wire/storage properties. It does not parse, validate, serialize, or store their values.

## Dependencies And Integration Points

Direct dependencies are minimal: this module uses only Python literals. It is imported by:

- `examples/exchanger.py`, which imports `MAPI_PROPERTIES` and `PR_CONTAINER_FLAGS_VALUES` to render Exchange/NPSI table rows and container flags in human-readable form.
- `impacket.dcerpc.v5.nspi` and `impacket.dcerpc.v5.oxabref`, which import `mapi_constants` for MAPI error lookup from earlier parts of the same module.

The practical integration contract for this chunk is tuple compatibility with the table comment and with `exchanger.py`'s hard-coded tuple indices. Property ids must remain integer keys, property types must stay numeric, and internal Exchange names must remain strings for entries that lack public names.

## Risks And Maintenance Notes

The highest-risk issue is silent tuple-index drift. There is no named structure or accessor, so adding/removing/reordering tuple fields would break callers that use numeric indexes. This is especially visible in `exchanger.py`, where chunk entries depend on index `[6]` as the display-name fallback.

The table mixes official-looking and internal Exchange property names without local validation against MS-OXPROPS or server behavior. Incorrect property ids or types would not fail import, but they would mislabel Exchange output or confuse downstream tooling that assumes the type code is authoritative.

Because this chunk closes the `MAPI_PROPERTIES` literal and the file, trailing comma, brace, or indentation mistakes can make the whole module fail to import. Duplicate property ids in the dictionary would also be accepted by Python with last-write-wins semantics, so uniqueness should be checked mechanically when editing.

Several names reflect mailbox telemetry or client signal data (`SignalClientIp`, `SignalUserAgent`, location fields). This module only exposes labels, but tools that print values for these property ids can surface sensitive operational metadata.

## Test Signals

Useful validation signals for this chunk include:

- `python -m py_compile impacket/mapi_constants.py` or importing `impacket.mapi_constants` successfully.
- Assert that `MAPI_PROPERTIES[0x35eb] == (0x0102, None, None, 4, None, None, "UMVoicemailFolderEntryId")`.
- Assert that `MAPI_PROPERTIES[0x8d0d] == (0x001f, None, None, 4, None, None, "ExternalDirectoryObjectId")`.
- Count 686 property entries in lines 2896-3582, with first key `0x35eb` and last key `0x8d0d`.
- Spot-check consumer behavior in `examples/exchanger.py` by rendering a property tag whose high word is a chunk id, such as `0x35eb0102`, and verifying the display name falls back to the internal Exchange name.
- Run a duplicate-key scan over `MAPI_PROPERTIES` source literals if the table is regenerated or manually edited, because Python import alone will not expose overwritten keys.
