# subset-b-010023 research

Grouped research report for SMBLibrary SMB1 metadata helpers/structures and SMB2 command, enum, and cryptography files. Each section preserves the source path and is delimited for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/FindInformationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/FindInformationHelper.cs

Purpose: Bridges SMB1 TRANS2 find information levels to the shared FSCC query-directory model and back to SMB1 wire structures.

Important APIs/types/functions: `ToFileInformationClass`, `ToFindInformationList`, and `ToFindInformation` map SMB1 `FindInformationLevel` values and `QueryDirectoryFileInformation` subclasses to concrete `FindInformation` records.

Control flow: Dispatch is type- and enum-based. `ToFindInformationList` walks query results until adding another serialized entry would exceed `maxLength`, preserving page boundaries for directory enumeration responses.

State and persistence behavior: No persistent state; it mutates only the returned list and per-entry DTO fields including timestamps, EA size, short name, file id, and attributes.

Dependencies and integration points: Depends on SMB1 find structures, shared `FileInformationClass` / query-directory classes, and `Utilities` byte helpers indirectly through serialized length calculations. It is used by SMB1 file-store query-directory response assembly.

Risks and edge cases: Unsupported levels throw `UnsupportedInformationLevelException`; unknown input subclasses throw `NotImplementedException`. Several mappings use last-write time as last-change/attribute-change time, which can lose fidelity when a backend exposes separate change time.

Test signals: Round-trip tests should cover every supported information level, max-length truncation at entry boundaries, Unicode and OEM length calculation, and preservation of file id / short-name fields for both ID and non-ID formats.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/FindInformationHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryFSInformationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryFSInformationHelper.cs

Purpose: Converts SMB1 file-system query levels to shared FSCC file-system information classes and converts shared responses back to SMB1 query structures.

Important APIs/types/functions: `ToFileSystemInformationClass` supports volume, size, device, and attribute levels; `FromFileSystemInformation` creates `QueryFSVolumeInfo`, `QueryFSSizeInfo`, `QueryFSDeviceInfo`, or `QueryFSAttibuteInfo`.

Control flow: The helper performs a straight switch for request level translation and an `is` chain for response DTO conversion.

State and persistence behavior: Stateless; it copies volume labels, serials, allocation unit counts, device metadata, and file-system attributes into new SMB1 objects.

Dependencies and integration points: Integrates SMB1 TRANS2 query FS handling with shared `FileSystemInformation` classes and the concrete SMB1 query FS serializers.

Risks and edge cases: Unknown levels and subclasses fail fast. The attribute class name is misspelled as `QueryFSAttibuteInfo`, so callers must use the existing type name consistently.

Test signals: Tests should cover all four conversions, Unicode file-system names, and failure behavior for unsupported information classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryFSInformationHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryInformationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryInformationHelper.cs

Purpose: Maps SMB1 file query information levels to shared FSCC classes and performs bidirectional conversion between shared `FileInformation` DTOs and SMB1 query structures.

Important APIs/types/functions: `ToFileInformationClass`, `FromFileInformation`, `ToFileInformationLevel`, and `ToFileInformation` cover basic, standard, EA, name, all, alternate-name, stream, and compression information.

Control flow: Enum switches choose information classes. Type dispatch copies fields into equivalent wire DTOs; composite `FileAllInformation` is flattened to or assembled from nested basic, standard, EA, and name objects.

State and persistence behavior: No persistence; conversions allocate new objects and copy timestamps, attributes, allocation sizes, flags, stream entries, compression fields, and names.

Dependencies and integration points: Sits between SMB1 transaction handlers and shared filesystem abstractions. It depends on `FileInformation`, stream entries, compression enums, `ExtendedFileAttributes`, and SMB1 query DTO serializers.

Risks and edge cases: Unrecognized subclasses throw `NotImplementedException`. Attribute enum casts assume overlapping SMB1/shared bit values. Stream entries are shallow-copied via `AddRange`, so mutable entry objects are shared.

Test signals: Tests should verify bidirectional round trips for all supported classes, `FileAllInformation` composition, stream list behavior, compression reserved bytes, and unsupported-level exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/QueryInformationHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/SetInformationHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/SetInformationHelper.cs

Purpose: Translates SMB1 set-information request DTOs into shared FSCC `FileInformation` operations for backend application.

Important APIs/types/functions: `ToFileInformation` supports basic timestamps/attributes, disposition/delete-pending, allocation size, and end-of-file size.

Control flow: A type-dispatch chain creates the corresponding shared information class and copies writable fields.

State and persistence behavior: Stateless; it returns new shared DTOs and preserves SMB1 set-time sentinel semantics through `SetFileTime` fields.

Dependencies and integration points: Used by SMB1 SET_PATH/SET_FILE information handling before calling the file-store implementation. Depends on SMB1 set DTOs and shared file information classes.

Risks and edge cases: Unsupported set classes throw `NotImplementedException`. Allocation-size comments note SMB1 inputs are byte lengths rather than cluster-aligned values, which backend implementations must interpret carefully.

Test signals: Tests should cover each supported set class, delete-pending boolean encoding, zero/sentinel set times, and allocation/end-of-file boundary values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Helpers/SetInformationHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/ExtendedAttributeName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/ExtendedAttributeName.cs

Purpose: Represents the [MS-CIFS] SMB_GEA extended attribute name record used by SMB1 extended attribute query/set payloads.

Important APIs/types/functions: Public API is the `ExtendedAttributeName` constructor(s), `WriteBytes`, `GetBytes` where present, and `Length`; the record details are length-prefixed ANSI name with required trailing null in the computed size.

Control flow: Parsing reads fields sequentially from a caller-provided buffer offset. Serialization recomputes length fields from current string/list contents and writes little-endian or ANSI bytes.

State and persistence behavior: The object stores only in-memory attribute names, values, flags, and list membership. There is no external persistence or caching.

Dependencies and integration points: Depends on `Utilities` byte readers/writers and SMB1 extended-attribute enums. Integrated into SMB1 transaction payloads that request or provide EA lists.

Risks and edge cases: Buffer constructors trust length fields and do not validate EOF, null terminators, string byte length overflow, or malformed list progress; non-ASCII ANSI conversion can also be lossy.

Test signals: Tests should include empty and multiple-entry lists, ANSI names/values, length-field round trips, ref-offset advancement for FEA lists, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/ExtendedAttributeName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/ExtendedAttributeNameList.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/ExtendedAttributeNameList.cs

Purpose: Represents the [MS-CIFS] SMB_GEA_LIST collection used by SMB1 extended attribute query/set payloads.

Important APIs/types/functions: Public API is the `ExtendedAttributeNameList` constructor(s), `WriteBytes`, `GetBytes` where present, and `Length`; the record details are 32-bit list length followed by repeated `ExtendedAttributeName` entries.

Control flow: Parsing reads fields sequentially from a caller-provided buffer offset. Serialization recomputes length fields from current string/list contents and writes little-endian or ANSI bytes.

State and persistence behavior: The object stores only in-memory attribute names, values, flags, and list membership. There is no external persistence or caching.

Dependencies and integration points: Depends on `Utilities` byte readers/writers and SMB1 extended-attribute enums. Integrated into SMB1 transaction payloads that request or provide EA lists.

Risks and edge cases: Buffer constructors trust length fields and do not validate EOF, null terminators, string byte length overflow, or malformed list progress; non-ASCII ANSI conversion can also be lossy.

Test signals: Tests should include empty and multiple-entry lists, ANSI names/values, length-field round trips, ref-offset advancement for FEA lists, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/ExtendedAttributeNameList.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/FullExtendedAttribute.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/FullExtendedAttribute.cs

Purpose: Represents the [MS-CIFS] SMB_FEA full extended attribute record used by SMB1 extended attribute query/set payloads.

Important APIs/types/functions: Public API is the `FullExtendedAttribute` constructor(s), `WriteBytes`, `GetBytes` where present, and `Length`; the record details are flag, ANSI name, null separator, and ANSI value length fields.

Control flow: Parsing reads fields sequentially from a caller-provided buffer offset. Serialization recomputes length fields from current string/list contents and writes little-endian or ANSI bytes.

State and persistence behavior: The object stores only in-memory attribute names, values, flags, and list membership. There is no external persistence or caching.

Dependencies and integration points: Depends on `Utilities` byte readers/writers and SMB1 extended-attribute enums. Integrated into SMB1 transaction payloads that request or provide EA lists.

Risks and edge cases: Buffer constructors trust length fields and do not validate EOF, null terminators, string byte length overflow, or malformed list progress; non-ASCII ANSI conversion can also be lossy.

Test signals: Tests should include empty and multiple-entry lists, ANSI names/values, length-field round trips, ref-offset advancement for FEA lists, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/FullExtendedAttribute.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/FullExtendedAttributeList.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/FullExtendedAttributeList.cs

Purpose: Represents the [MS-CIFS] SMB_FEA_LIST collection used by SMB1 extended attribute query/set payloads.

Important APIs/types/functions: Public API is the `FullExtendedAttributeList` constructor(s), `WriteBytes`, `GetBytes` where present, and `Length`; the record details are 32-bit total length and repeated `FullExtendedAttribute` entries with an overload that advances a ref offset.

Control flow: Parsing reads fields sequentially from a caller-provided buffer offset. Serialization recomputes length fields from current string/list contents and writes little-endian or ANSI bytes.

State and persistence behavior: The object stores only in-memory attribute names, values, flags, and list membership. There is no external persistence or caching.

Dependencies and integration points: Depends on `Utilities` byte readers/writers and SMB1 extended-attribute enums. Integrated into SMB1 transaction payloads that request or provide EA lists.

Risks and edge cases: Buffer constructors trust length fields and do not validate EOF, null terminators, string byte length overflow, or malformed list progress; non-ASCII ANSI conversion can also be lossy.

Test signals: Tests should include empty and multiple-entry lists, ANSI names/values, length-field round trips, ref-offset advancement for FEA lists, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/ExtendedFileAttributes/FullExtendedAttributeList.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileBothDirectoryInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileBothDirectoryInfo.cs

Purpose: Concrete SMB1 find-information wire record for `SMB_FIND_FILE_BOTH_DIRECTORY_INFO`.

Important APIs/types/functions: `FindFileBothDirectoryInfo` exposes parsed metadata fields, a buffer constructor, `WriteBytes`, `GetLength`, and `InformationLevel`; fixed portion is 94 bytes and carries directory metadata plus EA size, reserved byte, UTF-16 short name, and long file name.

Control flow: `Read` constructors consume `NextEntryOffset`, fixed metadata, a byte-counted file name, and optional EA/short-name/file-id fields. `WriteBytes` recomputes byte lengths and emits an SMB1 string with a null terminator.

State and persistence behavior: State is per-record DTO state only. `NextEntryOffset` is assigned by `FindInformationList` for chained responses.

Dependencies and integration points: Depends on `FindInformation`, `SMB1Helper`, `FileTimeHelper`, endian helpers, and SMB1 attribute enums. Integrated by both-directory responses and SMB1 find helper conversions.

Risks and edge cases: Constructors trust wire lengths. Some classes cast Unicode file-name byte length through `byte` before writing, which risks truncation for long names. Short-name parsing uses byte length against a UTF-16 string and may be fragile for non-ASCII short names.

Test signals: Tests should serialize/parse Unicode and OEM names, long names near 255+ bytes, zero timestamps, multi-entry `NextEntryOffset`, short-name padding, and file-id fields where present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileBothDirectoryInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileDirectoryInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileDirectoryInfo.cs

Purpose: Concrete SMB1 find-information wire record for `SMB_FIND_FILE_DIRECTORY_INFO`.

Important APIs/types/functions: `FindFileDirectoryInfo` exposes parsed metadata fields, a buffer constructor, `WriteBytes`, `GetLength`, and `InformationLevel`; fixed portion is 64 bytes and carries basic directory metadata and long file name.

Control flow: `Read` constructors consume `NextEntryOffset`, fixed metadata, a byte-counted file name, and optional EA/short-name/file-id fields. `WriteBytes` recomputes byte lengths and emits an SMB1 string with a null terminator.

State and persistence behavior: State is per-record DTO state only. `NextEntryOffset` is assigned by `FindInformationList` for chained responses.

Dependencies and integration points: Depends on `FindInformation`, `SMB1Helper`, `FileTimeHelper`, endian helpers, and SMB1 attribute enums. Integrated by directory-info responses without EA or short-name data.

Risks and edge cases: Constructors trust wire lengths. Some classes cast Unicode file-name byte length through `byte` before writing, which risks truncation for long names. Short-name parsing uses byte length against a UTF-16 string and may be fragile for non-ASCII short names.

Test signals: Tests should serialize/parse Unicode and OEM names, long names near 255+ bytes, zero timestamps, multi-entry `NextEntryOffset`, short-name padding, and file-id fields where present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileDirectoryInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileFullDirectoryInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileFullDirectoryInfo.cs

Purpose: Concrete SMB1 find-information wire record for `SMB_FIND_FILE_FULL_DIRECTORY_INFO`.

Important APIs/types/functions: `FindFileFullDirectoryInfo` exposes parsed metadata fields, a buffer constructor, `WriteBytes`, `GetLength`, and `InformationLevel`; fixed portion is 68 bytes and carries directory metadata, EA size, and long file name.

Control flow: `Read` constructors consume `NextEntryOffset`, fixed metadata, a byte-counted file name, and optional EA/short-name/file-id fields. `WriteBytes` recomputes byte lengths and emits an SMB1 string with a null terminator.

State and persistence behavior: State is per-record DTO state only. `NextEntryOffset` is assigned by `FindInformationList` for chained responses.

Dependencies and integration points: Depends on `FindInformation`, `SMB1Helper`, `FileTimeHelper`, endian helpers, and SMB1 attribute enums. Integrated by full-directory responses.

Risks and edge cases: Constructors trust wire lengths. Some classes cast Unicode file-name byte length through `byte` before writing, which risks truncation for long names. Short-name parsing uses byte length against a UTF-16 string and may be fragile for non-ASCII short names.

Test signals: Tests should serialize/parse Unicode and OEM names, long names near 255+ bytes, zero timestamps, multi-entry `NextEntryOffset`, short-name padding, and file-id fields where present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileFullDirectoryInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileIDBothDirectoryInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileIDBothDirectoryInfo.cs

Purpose: Concrete SMB1 find-information wire record for `SMB_FIND_FILE_ID_BOTH_DIRECTORY_INFO`.

Important APIs/types/functions: `FindFileIDBothDirectoryInfo` exposes parsed metadata fields, a buffer constructor, `WriteBytes`, `GetLength`, and `InformationLevel`; fixed portion is 104 bytes and carries both-directory metadata plus file id and reserved fields.

Control flow: `Read` constructors consume `NextEntryOffset`, fixed metadata, a byte-counted file name, and optional EA/short-name/file-id fields. `WriteBytes` recomputes byte lengths and emits an SMB1 string with a null terminator.

State and persistence behavior: State is per-record DTO state only. `NextEntryOffset` is assigned by `FindInformationList` for chained responses.

Dependencies and integration points: Depends on `FindInformation`, `SMB1Helper`, `FileTimeHelper`, endian helpers, and SMB1 attribute enums. Integrated by ID both-directory responses.

Risks and edge cases: Constructors trust wire lengths. Some classes cast Unicode file-name byte length through `byte` before writing, which risks truncation for long names. Short-name parsing uses byte length against a UTF-16 string and may be fragile for non-ASCII short names.

Test signals: Tests should serialize/parse Unicode and OEM names, long names near 255+ bytes, zero timestamps, multi-entry `NextEntryOffset`, short-name padding, and file-id fields where present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileIDBothDirectoryInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileIDFullDirectoryInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileIDFullDirectoryInfo.cs

Purpose: Concrete SMB1 find-information wire record for `SMB_FIND_FILE_ID_FULL_DIRECTORY_INFO`.

Important APIs/types/functions: `FindFileIDFullDirectoryInfo` exposes parsed metadata fields, a buffer constructor, `WriteBytes`, `GetLength`, and `InformationLevel`; fixed portion is 80 bytes and carries full-directory metadata plus file id.

Control flow: `Read` constructors consume `NextEntryOffset`, fixed metadata, a byte-counted file name, and optional EA/short-name/file-id fields. `WriteBytes` recomputes byte lengths and emits an SMB1 string with a null terminator.

State and persistence behavior: State is per-record DTO state only. `NextEntryOffset` is assigned by `FindInformationList` for chained responses.

Dependencies and integration points: Depends on `FindInformation`, `SMB1Helper`, `FileTimeHelper`, endian helpers, and SMB1 attribute enums. Integrated by ID full-directory responses.

Risks and edge cases: Constructors trust wire lengths. Some classes cast Unicode file-name byte length through `byte` before writing, which risks truncation for long names. Short-name parsing uses byte length against a UTF-16 string and may be fragile for non-ASCII short names.

Test signals: Tests should serialize/parse Unicode and OEM names, long names near 255+ bytes, zero timestamps, multi-entry `NextEntryOffset`, short-name padding, and file-id fields where present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileIDFullDirectoryInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileNamesInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileNamesInfo.cs

Purpose: Concrete SMB1 find-information wire record for `SMB_FIND_FILE_NAMES_INFO`.

Important APIs/types/functions: `FindFileNamesInfo` exposes parsed metadata fields, a buffer constructor, `WriteBytes`, `GetLength`, and `InformationLevel`; fixed portion is 12 bytes and carries file index and long file name only.

Control flow: `Read` constructors consume `NextEntryOffset`, fixed metadata, a byte-counted file name, and optional EA/short-name/file-id fields. `WriteBytes` recomputes byte lengths and emits an SMB1 string with a null terminator.

State and persistence behavior: State is per-record DTO state only. `NextEntryOffset` is assigned by `FindInformationList` for chained responses.

Dependencies and integration points: Depends on `FindInformation`, `SMB1Helper`, `FileTimeHelper`, endian helpers, and SMB1 attribute enums. Integrated by name-only enumeration responses.

Risks and edge cases: Constructors trust wire lengths. Some classes cast Unicode file-name byte length through `byte` before writing, which risks truncation for long names. Short-name parsing uses byte length against a UTF-16 string and may be fragile for non-ASCII short names.

Test signals: Tests should serialize/parse Unicode and OEM names, long names near 255+ bytes, zero timestamps, multi-entry `NextEntryOffset`, short-name padding, and file-id fields where present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindFileNamesInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformation.cs

Purpose: Abstract base for SMB1 find-information records and factory for decoding records by information level.

Important APIs/types/functions: `NextEntryOffset`, abstract `WriteBytes`, `GetLength`, `InformationLevel`, and static `ReadEntry` define the common contract.

Control flow: `ReadEntry` switches on `FindInformationLevel` and instantiates the matching concrete record at the supplied buffer offset and Unicode mode.

State and persistence behavior: No persistent state beyond the common link offset field stored on each entry.

Dependencies and integration points: Integration point for `FindInformationList`, helper conversions, and SMB1 transaction parsers that need polymorphic find entries.

Risks and edge cases: Unsupported levels throw. The factory does not validate structure size before dispatch; concrete constructors are responsible for consuming the expected layout.

Test signals: Tests should assert dispatch for each supported level and exception behavior for unsupported levels.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformationList.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformationList.cs

Purpose: List wrapper for parsing and serializing chained SMB1 find-information entries.

Important APIs/types/functions: Constructors parse a buffer into entries; `GetBytes` assigns `NextEntryOffset` for all but the final entry; `GetLength` sums serialized lengths.

Control flow: Parsing follows each entry’s `NextEntryOffset` until zero. Serialization first updates offsets, then writes entries sequentially.

State and persistence behavior: Mutates contained entries by setting `NextEntryOffset`; otherwise state is the list contents only.

Dependencies and integration points: Depends on `FindInformation.ReadEntry` and concrete entry length calculations. Used by directory enumeration responses and parsers.

Risks and edge cases: A malformed non-advancing or out-of-range `NextEntryOffset` can break parsing. Serialization does not 8-byte-align entries, so it relies on each SMB1 structure’s expected length behavior.

Test signals: Tests should cover one-entry and multi-entry buffers, final zero offset, malformed offsets, Unicode/OEM lengths, and page-size truncation via `FindInformationHelper`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/FindInformation/FindInformationList.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSAttibuteInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSAttibuteInfo.cs

Purpose: Concrete SMB1 query-file-system information DTO for `SMB_QUERY_FS_ATTRIBUTE_INFO`.

Important APIs/types/functions: `QueryFSAttibuteInfo` provides a buffer constructor, `GetBytes`, `Length`, and `InformationLevel`; fixed portion is 12 bytes and contains file-system attributes, max component byte length, and UTF-16 file-system name.

Control flow: Parsing reads fixed fields and then any length-prefixed UTF-16 string. Serialization recomputes dynamic string byte lengths and writes a new byte array.

State and persistence behavior: State is the DTO fields only; no caching or persistence.

Dependencies and integration points: Used by `QueryFSInformation.GetQueryFSInformation` and `QueryFSInformationHelper` to bridge SMB1 FS queries to shared backend information.

Risks and edge cases: Buffer parsing trusts declared lengths. Volume label parsing appears to pass byte size as a UTF-16 character count, a likely boundary/overread risk for non-empty labels.

Test signals: Tests should cover empty and non-empty Unicode labels/names, numeric round trips, and truncated buffer rejection or documented failure modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSAttibuteInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSDeviceInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSDeviceInfo.cs

Purpose: Concrete SMB1 query-file-system information DTO for `SMB_QUERY_FS_DEVICE_INFO`.

Important APIs/types/functions: `QueryFSDeviceInfo` provides a buffer constructor, `GetBytes`, `Length`, and `InformationLevel`; fixed portion is 8 bytes and contains device type and characteristics.

Control flow: Parsing reads fixed fields and then any length-prefixed UTF-16 string. Serialization recomputes dynamic string byte lengths and writes a new byte array.

State and persistence behavior: State is the DTO fields only; no caching or persistence.

Dependencies and integration points: Used by `QueryFSInformation.GetQueryFSInformation` and `QueryFSInformationHelper` to bridge SMB1 FS queries to shared backend information.

Risks and edge cases: Buffer parsing trusts declared lengths. Volume label parsing appears to pass byte size as a UTF-16 character count, a likely boundary/overread risk for non-empty labels.

Test signals: Tests should cover empty and non-empty Unicode labels/names, numeric round trips, and truncated buffer rejection or documented failure modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSDeviceInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSSizeInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSSizeInfo.cs

Purpose: Concrete SMB1 query-file-system information DTO for `SMB_QUERY_FS_SIZE_INFO`.

Important APIs/types/functions: `QueryFSSizeInfo` provides a buffer constructor, `GetBytes`, `Length`, and `InformationLevel`; fixed portion is 24 bytes and contains total/free allocation units, sectors per allocation unit, and bytes per sector.

Control flow: Parsing reads fixed fields and then any length-prefixed UTF-16 string. Serialization recomputes dynamic string byte lengths and writes a new byte array.

State and persistence behavior: State is the DTO fields only; no caching or persistence.

Dependencies and integration points: Used by `QueryFSInformation.GetQueryFSInformation` and `QueryFSInformationHelper` to bridge SMB1 FS queries to shared backend information.

Risks and edge cases: Buffer parsing trusts declared lengths. Volume label parsing appears to pass byte size as a UTF-16 character count, a likely boundary/overread risk for non-empty labels.

Test signals: Tests should cover empty and non-empty Unicode labels/names, numeric round trips, and truncated buffer rejection or documented failure modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSSizeInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSVolumeInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSVolumeInfo.cs

Purpose: Concrete SMB1 query-file-system information DTO for `SMB_QUERY_FS_VOLUME_INFO`.

Important APIs/types/functions: `QueryFSVolumeInfo` provides a buffer constructor, `GetBytes`, `Length`, and `InformationLevel`; fixed portion is 18 bytes and contains volume creation time, serial, reserved field, and UTF-16 label.

Control flow: Parsing reads fixed fields and then any length-prefixed UTF-16 string. Serialization recomputes dynamic string byte lengths and writes a new byte array.

State and persistence behavior: State is the DTO fields only; no caching or persistence.

Dependencies and integration points: Used by `QueryFSInformation.GetQueryFSInformation` and `QueryFSInformationHelper` to bridge SMB1 FS queries to shared backend information.

Risks and edge cases: Buffer parsing trusts declared lengths. Volume label parsing appears to pass byte size as a UTF-16 character count, a likely boundary/overread risk for non-empty labels.

Test signals: Tests should cover empty and non-empty Unicode labels/names, numeric round trips, and truncated buffer rejection or documented failure modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSVolumeInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSInformation.cs

Purpose: Abstract base and factory for SMB1 query-file-system information payloads.

Important APIs/types/functions: Defines abstract `GetBytes(bool isUnicode)`, `Length`, `InformationLevel`, and static `GetQueryFSInformation`.

Control flow: Factory switches on `QueryFSInformationLevel` and constructs the matching concrete class from buffer offset zero.

State and persistence behavior: No state beyond subclass data.

Dependencies and integration points: Integrated by SMB1 query FS transaction handling and `QueryFSInformationHelper` conversions.

Risks and edge cases: The `isUnicode` parameter is not used by current concrete FS info classes because these structures use Unicode strings by specification. Unsupported levels throw.

Test signals: Tests should verify factory dispatch and unsupported-level exception paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryFSInformation/QueryFSInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileAllInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileAllInfo.cs

Purpose: Concrete SMB1 query-file information payload for `SMB_QUERY_FILE_ALL_INFO`.

Important APIs/types/functions: `QueryFileAllInfo` exposes a buffer constructor, `GetBytes`, and `InformationLevel`; it carries combined basic, standard, EA, and name information with a variable UTF-16 name.

Control flow: Parsing reads the FSCC-like binary layout from a supplied offset. Serialization builds a fresh byte array, recomputing length fields and writing little-endian numeric values and UTF-16 strings where applicable.

State and persistence behavior: State is the in-memory DTO fields only. `QueryFileStreamInfo` owns a mutable `Entries` list and calculates padded serialized length from it.

Dependencies and integration points: Used by `QueryInformation.GetQueryInformation` and `QueryInformationHelper` for SMB1 query responses and conversions to shared file-store objects.

Risks and edge cases: Constructors trust declared lengths and offsets. Stream parsing depends on nonzero `NextEntryOffset` progress; string classes do not validate even byte counts. Boolean fields accept any nonzero byte as true.

Test signals: Tests should include parse/write round trips, empty and long UTF-16 names, stream alignment with multiple entries, compression reserved bytes, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileAllInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileAltNameInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileAltNameInfo.cs

Purpose: Concrete SMB1 query-file information payload for `SMB_QUERY_FILE_ALT_NAME_INFO`.

Important APIs/types/functions: `QueryFileAltNameInfo` exposes a buffer constructor, `GetBytes`, and `InformationLevel`; it carries length-prefixed UTF-16 8.3 alternate file name.

Control flow: Parsing reads the FSCC-like binary layout from a supplied offset. Serialization builds a fresh byte array, recomputing length fields and writing little-endian numeric values and UTF-16 strings where applicable.

State and persistence behavior: State is the in-memory DTO fields only. `QueryFileStreamInfo` owns a mutable `Entries` list and calculates padded serialized length from it.

Dependencies and integration points: Used by `QueryInformation.GetQueryInformation` and `QueryInformationHelper` for SMB1 query responses and conversions to shared file-store objects.

Risks and edge cases: Constructors trust declared lengths and offsets. Stream parsing depends on nonzero `NextEntryOffset` progress; string classes do not validate even byte counts. Boolean fields accept any nonzero byte as true.

Test signals: Tests should include parse/write round trips, empty and long UTF-16 names, stream alignment with multiple entries, compression reserved bytes, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileAltNameInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileBasicInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileBasicInfo.cs

Purpose: Concrete SMB1 query-file information payload for `SMB_QUERY_FILE_BASIC_INFO`.

Important APIs/types/functions: `QueryFileBasicInfo` exposes a buffer constructor, `GetBytes`, and `InformationLevel`; it carries creation/access/write/change times, extended attributes, and reserved field.

Control flow: Parsing reads the FSCC-like binary layout from a supplied offset. Serialization builds a fresh byte array, recomputing length fields and writing little-endian numeric values and UTF-16 strings where applicable.

State and persistence behavior: State is the in-memory DTO fields only. `QueryFileStreamInfo` owns a mutable `Entries` list and calculates padded serialized length from it.

Dependencies and integration points: Used by `QueryInformation.GetQueryInformation` and `QueryInformationHelper` for SMB1 query responses and conversions to shared file-store objects.

Risks and edge cases: Constructors trust declared lengths and offsets. Stream parsing depends on nonzero `NextEntryOffset` progress; string classes do not validate even byte counts. Boolean fields accept any nonzero byte as true.

Test signals: Tests should include parse/write round trips, empty and long UTF-16 names, stream alignment with multiple entries, compression reserved bytes, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileBasicInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileCompressionInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileCompressionInfo.cs

Purpose: Concrete SMB1 query-file information payload for `SMB_QUERY_FILE_COMPRESSION_INFO`.

Important APIs/types/functions: `QueryFileCompressionInfo` exposes a buffer constructor, `GetBytes`, and `InformationLevel`; it carries compressed size, compression format, shifts, and three reserved bytes.

Control flow: Parsing reads the FSCC-like binary layout from a supplied offset. Serialization builds a fresh byte array, recomputing length fields and writing little-endian numeric values and UTF-16 strings where applicable.

State and persistence behavior: State is the in-memory DTO fields only. `QueryFileStreamInfo` owns a mutable `Entries` list and calculates padded serialized length from it.

Dependencies and integration points: Used by `QueryInformation.GetQueryInformation` and `QueryInformationHelper` for SMB1 query responses and conversions to shared file-store objects.

Risks and edge cases: Constructors trust declared lengths and offsets. Stream parsing depends on nonzero `NextEntryOffset` progress; string classes do not validate even byte counts. Boolean fields accept any nonzero byte as true.

Test signals: Tests should include parse/write round trips, empty and long UTF-16 names, stream alignment with multiple entries, compression reserved bytes, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileCompressionInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileEaInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileEaInfo.cs

Purpose: Concrete SMB1 query-file information payload for `SMB_QUERY_FILE_EA_INFO`.

Important APIs/types/functions: `QueryFileEaInfo` exposes a buffer constructor, `GetBytes`, and `InformationLevel`; it carries EA size as a 32-bit value.

Control flow: Parsing reads the FSCC-like binary layout from a supplied offset. Serialization builds a fresh byte array, recomputing length fields and writing little-endian numeric values and UTF-16 strings where applicable.

State and persistence behavior: State is the in-memory DTO fields only. `QueryFileStreamInfo` owns a mutable `Entries` list and calculates padded serialized length from it.

Dependencies and integration points: Used by `QueryInformation.GetQueryInformation` and `QueryInformationHelper` for SMB1 query responses and conversions to shared file-store objects.

Risks and edge cases: Constructors trust declared lengths and offsets. Stream parsing depends on nonzero `NextEntryOffset` progress; string classes do not validate even byte counts. Boolean fields accept any nonzero byte as true.

Test signals: Tests should include parse/write round trips, empty and long UTF-16 names, stream alignment with multiple entries, compression reserved bytes, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileEaInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileNameInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileNameInfo.cs

Purpose: Concrete SMB1 query-file information payload for `SMB_QUERY_FILE_NAME_INFO`.

Important APIs/types/functions: `QueryFileNameInfo` exposes a buffer constructor, `GetBytes`, and `InformationLevel`; it carries length-prefixed UTF-16 file name.

Control flow: Parsing reads the FSCC-like binary layout from a supplied offset. Serialization builds a fresh byte array, recomputing length fields and writing little-endian numeric values and UTF-16 strings where applicable.

State and persistence behavior: State is the in-memory DTO fields only. `QueryFileStreamInfo` owns a mutable `Entries` list and calculates padded serialized length from it.

Dependencies and integration points: Used by `QueryInformation.GetQueryInformation` and `QueryInformationHelper` for SMB1 query responses and conversions to shared file-store objects.

Risks and edge cases: Constructors trust declared lengths and offsets. Stream parsing depends on nonzero `NextEntryOffset` progress; string classes do not validate even byte counts. Boolean fields accept any nonzero byte as true.

Test signals: Tests should include parse/write round trips, empty and long UTF-16 names, stream alignment with multiple entries, compression reserved bytes, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileNameInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileStandardInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileStandardInfo.cs

Purpose: Concrete SMB1 query-file information payload for `SMB_QUERY_FILE_STANDARD_INFO`.

Important APIs/types/functions: `QueryFileStandardInfo` exposes a buffer constructor, `GetBytes`, and `InformationLevel`; it carries allocation size, EOF, link count, delete-pending, and directory flags.

Control flow: Parsing reads the FSCC-like binary layout from a supplied offset. Serialization builds a fresh byte array, recomputing length fields and writing little-endian numeric values and UTF-16 strings where applicable.

State and persistence behavior: State is the in-memory DTO fields only. `QueryFileStreamInfo` owns a mutable `Entries` list and calculates padded serialized length from it.

Dependencies and integration points: Used by `QueryInformation.GetQueryInformation` and `QueryInformationHelper` for SMB1 query responses and conversions to shared file-store objects.

Risks and edge cases: Constructors trust declared lengths and offsets. Stream parsing depends on nonzero `NextEntryOffset` progress; string classes do not validate even byte counts. Boolean fields accept any nonzero byte as true.

Test signals: Tests should include parse/write round trips, empty and long UTF-16 names, stream alignment with multiple entries, compression reserved bytes, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileStandardInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileStreamInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileStreamInfo.cs

Purpose: Concrete SMB1 query-file information payload for `SMB_QUERY_FILE_STREAM_INFO`.

Important APIs/types/functions: `QueryFileStreamInfo` exposes a buffer constructor, `GetBytes`, and `InformationLevel`; it carries a list of FSCC `FileStreamEntry` records aligned to 8-byte boundaries.

Control flow: Parsing reads the FSCC-like binary layout from a supplied offset. Serialization builds a fresh byte array, recomputing length fields and writing little-endian numeric values and UTF-16 strings where applicable.

State and persistence behavior: State is the in-memory DTO fields only. `QueryFileStreamInfo` owns a mutable `Entries` list and calculates padded serialized length from it.

Dependencies and integration points: Used by `QueryInformation.GetQueryInformation` and `QueryInformationHelper` for SMB1 query responses and conversions to shared file-store objects.

Risks and edge cases: Constructors trust declared lengths and offsets. Stream parsing depends on nonzero `NextEntryOffset` progress; string classes do not validate even byte counts. Boolean fields accept any nonzero byte as true.

Test signals: Tests should include parse/write round trips, empty and long UTF-16 names, stream alignment with multiple entries, compression reserved bytes, and malformed/truncated buffers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryFileStreamInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryInformation.cs

Purpose: Abstract base and factory for SMB1 query-file information records.

Important APIs/types/functions: Defines abstract `GetBytes`, `InformationLevel`, and static `GetQueryInformation` covering basic, standard, EA, name, all, alternate-name, stream, and compression classes.

Control flow: Factory switches on `QueryInformationLevel` and constructs concrete DTOs at offset zero.

State and persistence behavior: No internal state beyond subclass payloads.

Dependencies and integration points: Central parser entry for SMB1 query file/path information responses and helper conversion logic.

Risks and edge cases: Unsupported levels throw. The factory does not pre-check buffer length, so malformed inputs surface from concrete constructors.

Test signals: Tests should exercise every supported dispatch branch and unsupported-level behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/QueryInformation/QueryInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileAllocationInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileAllocationInfo.cs

Purpose: Concrete SMB1 set-information request payload for `SMB_SET_FILE_ALLOCATION_INFO`.

Important APIs/types/functions: `SetFileAllocationInfo` provides default and buffer constructors, `GetBytes`, and `InformationLevel`; it carries allocation size as an Int64 byte length.

Control flow: Parsing reads the fixed-size little-endian structure. Serialization emits the fixed-size request body from current field values.

State and persistence behavior: State is the requested mutation values only; persistence happens later in the file-store backend after helper conversion.

Dependencies and integration points: Used by `SetInformation.GetSetInformation` and `SetInformationHelper` to convert SMB1 set requests into shared `FileInformation` mutation DTOs.

Risks and edge cases: Constructors trust buffer length. Time-setting semantics depend on `SetFileTime` sentinel handling, and size fields require backend validation for negative or unsupported truncation/extension values.

Test signals: Tests should cover fixed lengths, boolean encoding, set-time sentinel values, negative and large sizes, and helper conversion into shared classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileAllocationInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileBasicInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileBasicInfo.cs

Purpose: Concrete SMB1 set-information request payload for `SMB_SET_FILE_BASIC_INFO`.

Important APIs/types/functions: `SetFileBasicInfo` provides default and buffer constructors, `GetBytes`, and `InformationLevel`; it carries set-time values for creation/access/write/change plus attributes and reserved field.

Control flow: Parsing reads the fixed-size little-endian structure. Serialization emits the fixed-size request body from current field values.

State and persistence behavior: State is the requested mutation values only; persistence happens later in the file-store backend after helper conversion.

Dependencies and integration points: Used by `SetInformation.GetSetInformation` and `SetInformationHelper` to convert SMB1 set requests into shared `FileInformation` mutation DTOs.

Risks and edge cases: Constructors trust buffer length. Time-setting semantics depend on `SetFileTime` sentinel handling, and size fields require backend validation for negative or unsupported truncation/extension values.

Test signals: Tests should cover fixed lengths, boolean encoding, set-time sentinel values, negative and large sizes, and helper conversion into shared classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileBasicInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileDispositionInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileDispositionInfo.cs

Purpose: Concrete SMB1 set-information request payload for `SMB_SET_FILE_DISPOSITION_INFO`.

Important APIs/types/functions: `SetFileDispositionInfo` provides default and buffer constructors, `GetBytes`, and `InformationLevel`; it carries delete-pending boolean.

Control flow: Parsing reads the fixed-size little-endian structure. Serialization emits the fixed-size request body from current field values.

State and persistence behavior: State is the requested mutation values only; persistence happens later in the file-store backend after helper conversion.

Dependencies and integration points: Used by `SetInformation.GetSetInformation` and `SetInformationHelper` to convert SMB1 set requests into shared `FileInformation` mutation DTOs.

Risks and edge cases: Constructors trust buffer length. Time-setting semantics depend on `SetFileTime` sentinel handling, and size fields require backend validation for negative or unsupported truncation/extension values.

Test signals: Tests should cover fixed lengths, boolean encoding, set-time sentinel values, negative and large sizes, and helper conversion into shared classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileDispositionInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileEndOfFileInfo.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileEndOfFileInfo.cs

Purpose: Concrete SMB1 set-information request payload for `SMB_SET_FILE_END_OF_FILE_INFO`.

Important APIs/types/functions: `SetFileEndOfFileInfo` provides default and buffer constructors, `GetBytes`, and `InformationLevel`; it carries end-of-file size as an Int64 byte length.

Control flow: Parsing reads the fixed-size little-endian structure. Serialization emits the fixed-size request body from current field values.

State and persistence behavior: State is the requested mutation values only; persistence happens later in the file-store backend after helper conversion.

Dependencies and integration points: Used by `SetInformation.GetSetInformation` and `SetInformationHelper` to convert SMB1 set requests into shared `FileInformation` mutation DTOs.

Risks and edge cases: Constructors trust buffer length. Time-setting semantics depend on `SetFileTime` sentinel handling, and size fields require backend validation for negative or unsupported truncation/extension values.

Test signals: Tests should cover fixed lengths, boolean encoding, set-time sentinel values, negative and large sizes, and helper conversion into shared classes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetFileEndOfFileInfo.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetInformation.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetInformation.cs

Purpose: Abstract base and factory for SMB1 set-information request payloads.

Important APIs/types/functions: Defines abstract `GetBytes`, `InformationLevel`, and static `GetSetInformation` for basic, disposition, allocation, and EOF levels.

Control flow: Factory switches on `SetInformationLevel` and constructs concrete fixed-layout DTOs.

State and persistence behavior: No state beyond subclass payloads.

Dependencies and integration points: Integration point for SMB1 transaction handlers before `SetInformationHelper` maps requests into backend file information classes.

Risks and edge cases: Unsupported levels throw. Buffer length is not checked before dispatch.

Test signals: Tests should cover all factory branches, unsupported-level exception behavior, and short-buffer handling expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB1FileStore/Structures/SetInformation/SetInformation.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CancelRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CancelRequest.cs

Purpose: Implements the SMB2 CANCEL request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `CancelRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for fixed 4-byte reserved body used to cancel an outstanding async request; no response class is expected except error handling in dispatcher.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CancelRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ChangeNotifyRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ChangeNotifyRequest.cs

Purpose: Implements the SMB2 CHANGE_NOTIFY request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `ChangeNotifyRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for watch flags, output buffer length, file id, completion filter, and reserved field; `WatchTree` toggles `SMB2_WATCH_TREE`.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ChangeNotifyRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ChangeNotifyResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ChangeNotifyResponse.cs

Purpose: Implements the SMB2 CHANGE_NOTIFY response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `ChangeNotifyResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for output buffer offset/length and raw notify buffer; helpers convert to/from `FileNotifyInformation` lists.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ChangeNotifyResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CloseRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CloseRequest.cs

Purpose: Implements the SMB2 CLOSE request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `CloseRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for close flags, reserved field, and file id; `PostQueryAttributes` exposes the post-query flag.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CloseRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CloseResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CloseResponse.cs

Purpose: Implements the SMB2 CLOSE response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `CloseResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for post-close timestamps, allocation/EOF sizes, and file attributes; used when close requests ask for post-query attributes.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CloseResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CreateRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CreateRequest.cs

Purpose: Implements the SMB2 CREATE request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `CreateRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for oplock, impersonation, access, attributes, sharing, disposition/options, UTF-16 name, and optional create contexts; pads name to 8 bytes before create contexts.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CreateRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CreateResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CreateResponse.cs

Purpose: Implements the SMB2 CREATE response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `CreateResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for oplock, create action, timestamps, sizes, file attributes, file id, and optional create contexts; sets `Header.IsResponse` and serializes create contexts after the fixed body.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/CreateResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/EchoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/EchoRequest.cs

Purpose: Implements the SMB2 ECHO request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `EchoRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for fixed 4-byte keepalive body; simple liveness command.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/EchoRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/EchoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/EchoResponse.cs

Purpose: Implements the SMB2 ECHO response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `EchoResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for fixed 4-byte echo response body; sets response header bit.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/EchoResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ErrorResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ErrorResponse.cs

Purpose: Implements the SMB2 ERROR response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `ErrorResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for error context count, byte count, and variable error data; ensures a one-byte error data field when `ByteCount` is zero.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ErrorResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/FlushRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/FlushRequest.cs

Purpose: Implements the SMB2 FLUSH request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `FlushRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for reserved fields and file id; requests backend flush for an open handle.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/FlushRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/FlushResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/FlushResponse.cs

Purpose: Implements the SMB2 FLUSH response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `FlushResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for fixed reserved body; acknowledges flush completion.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/FlushResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/IOCtlRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/IOCtlRequest.cs

Purpose: Implements the SMB2 IOCTL request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `IOCtlRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for control code, file id, input/output buffers, max response sizes, and flags; `IsFSCtl` toggles FSCTL request flag.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/IOCtlRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/IOCtlResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/IOCtlResponse.cs

Purpose: Implements the SMB2 IOCTL response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `IOCtlResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for control code, file id, input/output buffers, flags, and reserved field; pads input to an 8-byte boundary before output.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/IOCtlResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LockRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LockRequest.cs

Purpose: Implements the SMB2 LOCK request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `LockRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for lock count, packed LSN/index, file id, and lock elements; serializes variable `LockElement` list.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LockRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LockResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LockResponse.cs

Purpose: Implements the SMB2 LOCK response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `LockResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for fixed reserved body; acknowledges byte-range lock operation.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LockResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LogoffRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LogoffRequest.cs

Purpose: Implements the SMB2 LOGOFF request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `LogoffRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for fixed reserved body; terminates a session.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LogoffRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LogoffResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LogoffResponse.cs

Purpose: Implements the SMB2 LOGOFF response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `LogoffResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for fixed reserved body; acknowledges session logoff.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/LogoffResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/NegotiateRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/NegotiateRequest.cs

Purpose: Implements the SMB2 NEGOTIATE request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `NegotiateRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for security mode, capabilities, client GUID, dialects, client start time or SMB 3.1.1 negotiate contexts; detects SMB 3.1.1 dialect to parse/write negotiate context list.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/NegotiateRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/NegotiateResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/NegotiateResponse.cs

Purpose: Implements the SMB2 NEGOTIATE response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `NegotiateResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for security mode, dialect, server GUID, capabilities, max sizes, times, security buffer, and negotiate contexts; pads security buffer before SMB 3.1.1 contexts.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/NegotiateResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryDirectoryRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryDirectoryRequest.cs

Purpose: Implements the SMB2 QUERY_DIRECTORY request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `QueryDirectoryRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for file information class, flags, file index, file id, output length, and optional UTF-16 pattern; boolean properties toggle restart/single-entry/reopen flags.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryDirectoryRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryDirectoryResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryDirectoryResponse.cs

Purpose: Implements the SMB2 QUERY_DIRECTORY response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `QueryDirectoryResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for output buffer offset/length and raw directory entries; helpers convert to/from `QueryDirectoryFileInformation` lists.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryDirectoryResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryInfoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryInfoRequest.cs

Purpose: Implements the SMB2 QUERY_INFO request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `QueryInfoRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for info type, class byte, output size, optional input buffer, additional information, flags, and file id; typed properties reinterpret class/additional fields for file, filesystem, and security info.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryInfoRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryInfoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryInfoResponse.cs

Purpose: Implements the SMB2 QUERY_INFO response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `QueryInfoResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for output buffer offset/length and typed helper decoders; helpers parse file, filesystem, or security descriptor information.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/QueryInfoResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ReadRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ReadRequest.cs

Purpose: Implements the SMB2 READ request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `ReadRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for read length, offset, file id, minimum count, channel data, remaining bytes, and flags; writes one zero buffer byte when no read-channel info is present.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ReadRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ReadResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ReadResponse.cs

Purpose: Implements the SMB2 READ response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `ReadResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for data offset/length, remaining bytes, and payload data; omits payload when data length is zero.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/ReadResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SMB2Command.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SMB2Command.cs

Purpose: Implements the abstract SMB2 command base and dispatcher packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `SMB2Command` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for common header ownership, serialization, command-chain packing, response/request factories, and signing integration; handles 8-byte command-chain alignment and response-vs-error disambiguation by structure size and status.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SMB2Command.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SessionSetupRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SessionSetupRequest.cs

Purpose: Implements the SMB2 SESSION_SETUP request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `SessionSetupRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for flags, security mode, capabilities, channel, previous session id, and security buffer; carries SPNEGO/NTLM/Kerberos token bytes.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SessionSetupRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SessionSetupResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SessionSetupResponse.cs

Purpose: Implements the SMB2 SESSION_SETUP response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `SessionSetupResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for session flags and security buffer; returns authentication continuation or final token.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SessionSetupResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SetInfoRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SetInfoRequest.cs

Purpose: Implements the SMB2 SET_INFO request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `SetInfoRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for info type, class byte, buffer, additional/security information, and file id; helpers encode file, filesystem, or security information into the buffer.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SetInfoRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SetInfoResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SetInfoResponse.cs

Purpose: Implements the SMB2 SET_INFO response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `SetInfoResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for 2-byte structure-size-only success body; acknowledges metadata update.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/SetInfoResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeConnectRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeConnectRequest.cs

Purpose: Implements the SMB2 TREE_CONNECT request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `TreeConnectRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for reserved field and UTF-16 UNC path; writes path immediately after fixed body.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeConnectRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeConnectResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeConnectResponse.cs

Purpose: Implements the SMB2 TREE_CONNECT response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `TreeConnectResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for share type, flags, capabilities, and maximal access; describes connected share semantics.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeConnectResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeDisconnectRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeDisconnectRequest.cs

Purpose: Implements the SMB2 TREE_DISCONNECT request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `TreeDisconnectRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for fixed reserved body; disconnects a tree id.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeDisconnectRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeDisconnectResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeDisconnectResponse.cs

Purpose: Implements the SMB2 TREE_DISCONNECT response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `TreeDisconnectResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for fixed reserved body; acknowledges tree disconnect.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/TreeDisconnectResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/WriteRequest.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/WriteRequest.cs

Purpose: Implements the SMB2 WRITE request packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `WriteRequest` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for data offset/length, file offset, file id, channel info, remaining bytes, and write flags; places write-channel info before data to keep data offset representable.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/WriteRequest.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/WriteResponse.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/WriteResponse.cs

Purpose: Implements the SMB2 WRITE response packet payload as an `SMB2Command` subclass.

Important APIs/types/functions: Important API is `WriteResponse` constructors, `WriteCommandBytes`, `CommandLength`, and public fields/properties for written byte count, remaining count, and optional channel info; acknowledges write completion.

Control flow: The buffer constructor first parses the common SMB2 header through the base class, then reads command fields at `SMB2Header.Length` offsets. Serialization recomputes offset/length fields, writes the fixed structure, and appends variable buffers when present.

State and persistence behavior: State is per-packet DTO state. Response classes set `Header.IsResponse`; no command persists data beyond its serialized fields.

Dependencies and integration points: Depends on `SMB2Header`, command enums, shared FSCC/file metadata structures, `FileID`, create/negotiate/lock context helpers, security descriptors, and `Utilities` endian/byte helpers. The base dispatcher integrates these classes with network packet parsing.

Risks and edge cases: Most parsers trust remote offset/length fields and do not bound-check before `ByteReader` calls. Offset-zero with nonzero length, integer truncation, and required one-byte-buffer rules are key protocol edge cases.

Test signals: Tests should include parse/write round trips, exact `StructureSize`/`CommandLength`, zero and nonzero variable buffers, offset alignment, response/error dispatch cases, and malformed length/offset inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Commands/WriteResponse.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/ChangeNotify/ChangeNotifyFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/ChangeNotify/ChangeNotifyFlags.cs

Purpose: Defines change notify request flags for SMB2 wire packet fields.

Important APIs/types/functions: `ChangeNotifyFlags` maps protocol constants for `WatchTree` / `SMB2_WATCH_TREE` for recursive directory monitoring.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `ChangeNotifyRequest.WatchTree` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/ChangeNotify/ChangeNotifyFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Close/CloseFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Close/CloseFlags.cs

Purpose: Defines close request/response flags for SMB2 wire packet fields.

Important APIs/types/functions: `CloseFlags` maps protocol constants for `PostQueryAttributes` / `SMB2_CLOSE_FLAG_POSTQUERY_ATTRIB`.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `CloseRequest` and `CloseResponse` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Close/CloseFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/CreateAction.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/CreateAction.cs

Purpose: Defines create response action codes for SMB2 wire packet fields.

Important APIs/types/functions: `CreateAction` maps protocol constants for superseded, opened, created, and overwritten outcomes.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `CreateResponse.CreateAction` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/CreateAction.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/CreateResponseFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/CreateResponseFlags.cs

Purpose: Defines create response flags for SMB2 wire packet fields.

Important APIs/types/functions: `CreateResponseFlags` maps protocol constants for `ReparsePoint` flag.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `CreateResponse.Flags` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/CreateResponseFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/OplockLevel.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/OplockLevel.cs

Purpose: Defines oplock level values for SMB2 wire packet fields.

Important APIs/types/functions: `OplockLevel` maps protocol constants for none, level II, exclusive, batch, and lease.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by create request/response oplock fields and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Create/OplockLevel.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/IOCtl/IOCtlRequestFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/IOCtl/IOCtlRequestFlags.cs

Purpose: Defines IOCTL request flags for SMB2 wire packet fields.

Important APIs/types/functions: `IOCtlRequestFlags` maps protocol constants for `IsFSCtl` / filesystem-control request bit.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `IOCtlRequest.IsFSCtl` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/IOCtl/IOCtlRequestFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/InfoType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/InfoType.cs

Purpose: Defines SMB2 query/set info type selector for SMB2 wire packet fields.

Important APIs/types/functions: `InfoType` maps protocol constants for file, filesystem, security, and quota categories.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `QueryInfoRequest` and `SetInfoRequest` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/InfoType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/Capabilities.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/Capabilities.cs

Purpose: Defines global negotiate capability flags for SMB2 wire packet fields.

Important APIs/types/functions: `Capabilities` maps protocol constants for DFS, leasing, large MTU, multichannel, persistent handles, directory leasing, encryption, and notifications.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by negotiate and session setup packets and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/Capabilities.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/NegotiateContextType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/NegotiateContextType.cs

Purpose: Defines SMB 3.1.1 negotiate context type ids for SMB2 wire packet fields.

Important APIs/types/functions: `NegotiateContextType` maps protocol constants for preauth, encryption, compression, netname, transport, RDMA transform, and signing contexts.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by negotiate context parsing and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/NegotiateContextType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/SMB2Dialect.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/SMB2Dialect.cs

Purpose: Defines SMB2 dialect identifiers for SMB2 wire packet fields.

Important APIs/types/functions: `SMB2Dialect` maps protocol constants for SMB 2.0.2 through 3.1.1 plus wildcard SMB2xx.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by negotiate packets and cryptography selection and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/SMB2Dialect.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/SecurityMode.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/SecurityMode.cs

Purpose: Defines SMB2 signing security-mode flags for SMB2 wire packet fields.

Important APIs/types/functions: `SecurityMode` maps protocol constants for signing enabled and signing required.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by negotiate/session setup security mode fields and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Negotiate/SecurityMode.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/QueryDirectory/QueryDirectoryFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/QueryDirectory/QueryDirectoryFlags.cs

Purpose: Defines query-directory flags for SMB2 wire packet fields.

Important APIs/types/functions: `QueryDirectoryFlags` maps protocol constants for restart scans, return single entry, index specified, and reopen.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `QueryDirectoryRequest` flag properties and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/QueryDirectory/QueryDirectoryFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Read/ReadFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Read/ReadFlags.cs

Purpose: Defines read request flags for SMB2 wire packet fields.

Important APIs/types/functions: `ReadFlags` maps protocol constants for unbuffered read request bit.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `ReadRequest.Flags` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Read/ReadFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2CommandName.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2CommandName.cs

Purpose: Defines SMB2 command identifiers for SMB2 wire packet fields.

Important APIs/types/functions: `SMB2CommandName` maps protocol constants for negotiate through oplock break command numbers.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by base request/response dispatcher and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2CommandName.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2PacketHeaderFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2PacketHeaderFlags.cs

Purpose: Defines SMB2 packet header flags for SMB2 wire packet fields.

Important APIs/types/functions: `SMB2PacketHeaderFlags` maps protocol constants for server-to-redirector, async, related operations, signed, and DFS operations.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `SMB2Header` and signing paths and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2PacketHeaderFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2TransformHeaderFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2TransformHeaderFlags.cs

Purpose: Defines SMB2 transform-header flags for SMB2 wire packet fields.

Important APIs/types/functions: `SMB2TransformHeaderFlags` maps protocol constants for encrypted transform marker.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by encrypted message transform header and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SMB2TransformHeaderFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SessionSetup/SessionFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SessionSetup/SessionFlags.cs

Purpose: Defines session setup response flags for SMB2 wire packet fields.

Important APIs/types/functions: `SessionFlags` maps protocol constants for guest, null session, and encrypt data.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `SessionSetupResponse.SessionFlags` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SessionSetup/SessionFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SessionSetup/SessionSetupFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SessionSetup/SessionSetupFlags.cs

Purpose: Defines session setup request flags for SMB2 wire packet fields.

Important APIs/types/functions: `SessionSetupFlags` maps protocol constants for binding flag.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `SessionSetupRequest.Flags` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/SessionSetup/SessionSetupFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareCapabilities.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareCapabilities.cs

Purpose: Defines tree-connect share capabilities for SMB2 wire packet fields.

Important APIs/types/functions: `ShareCapabilities` maps protocol constants for DFS, continuous availability, scaleout, cluster, and asymmetric share capabilities.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `TreeConnectResponse.Capabilities` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareCapabilities.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareFlags.cs

Purpose: Defines tree-connect share flags for SMB2 wire packet fields.

Important APIs/types/functions: `ShareFlags` maps protocol constants for caching modes, DFS flags, oplock/delete/namespace controls, hash flags, and encryption.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `TreeConnectResponse.ShareFlags` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareType.cs

Purpose: Defines tree-connect share type values for SMB2 wire packet fields.

Important APIs/types/functions: `ShareType` maps protocol constants for disk, pipe, and print shares.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `TreeConnectResponse.ShareType` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/TreeConnect/ShareType.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Write/WriteFlags.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Write/WriteFlags.cs

Purpose: Defines write request flags for SMB2 wire packet fields.

Important APIs/types/functions: `WriteFlags` maps protocol constants for write-through and unbuffered write bits.

Control flow: There is no control flow beyond enum value use; `[Flags]` enums are intended for bitwise composition while plain enums represent exclusive protocol values.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Integrated by `WriteRequest.Flags` and serialized by command/header classes through casts to the protocol byte/ushort/uint widths.

Risks and edge cases: Risks are specification drift, missing newer constants, and incorrect numeric values. Flag enums with zero-valued modes need care because `HasFlag`-style checks cannot identify a zero mode as set.

Test signals: Tests should assert numeric values against MS-SMB2 constants and cover bitwise helper properties that manipulate these enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Enums/Write/WriteFlags.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Cryptography.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Cryptography.cs

Purpose: Internal SMB2/SMB3 cryptography helper for signing, key derivation, hashing, and AES-CCM message transforms.

Important APIs/types/functions: `CalculateSignature`, `VerifySignature`, signing/encryption/decryption key derivation methods, `TransformMessage`, `EncryptMessage`, `DecryptMessage`, and `ComputeHash` implement dialect-specific crypto behavior.

Control flow: Signing uses HMAC-SHA256 for SMB 2.0.2/2.1 and AES-CMAC for newer dialects, truncating to the 16-byte SMB2 signature. Key derivation uses SP800-108 labels/contexts, with SMB 3.1.1 requiring preauth hash input. Encryption builds an SMB2 transform header, derives associated data, AES-CCM encrypts, and prefixes the transform header.

State and persistence behavior: No persistence, but `VerifySignature` mutates the supplied message buffer by clearing its signature field. Nonces are generated per transform and embedded in the transform header.

Dependencies and integration points: Used by `SMB2Command.GetCommandChainBytes`, SMB3 session setup, signing verification, and encrypted transport paths. Depends on `System.Security.Cryptography`, `AesCmac`, `AesCcm`, `SP800_1008`, SMB2 dialect/transform enums, and utility byte helpers.

Risks and edge cases: `GenerateAesCcmNonce` uses `new Random()` rather than a cryptographic RNG, which is risky for encryption nonce uniqueness and unpredictability. `VerifySignature` mutates caller buffers; callers needing original bytes must copy first. Only SHA512 is supported in `ComputeHash`.

Test signals: Tests should use known-answer vectors for SMB2 HMAC/AES-CMAC signatures, SMB3 key derivation labels/contexts, AES-CCM transform round trips, signature verification mutation behavior, and SMB 3.1.1 null preauth-hash exceptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/SMB2/SMB2Cryptography.cs -->
