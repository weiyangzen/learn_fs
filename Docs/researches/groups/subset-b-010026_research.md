<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/SettingsHelper.cs -->
# sources/user-network-fs/smblibrary/SMBServer/SettingsHelper.cs

Purpose: `SettingsHelper` is the SMBServer configuration loader for `Settings.xml` beside the Windows Forms executable. It converts XML user and share definitions into `UserCollection` and `List<ShareSettings>` instances consumed by the SMB server sample.

Important APIs/types/functions: `SettingsFileName` fixes the expected file name; `ReadXmlDocument(path)` loads an `XmlDocument`; `ReadSettingsXML()` derives the executable directory through `Application.ExecutablePath`; `ReadUserSettings()` reads `Settings/Users` child nodes and creates users from `AccountName` and `Password`; `ReadSharesSettings()` reads `Settings/Shares`, share `Name`/`Path`, and nested `ReadAccess`/`WriteAccess`; `ReadAccessList(XmlNode)` maps `Accounts="*"` to the local group string `Users` or splits comma-separated account names.

Control flow: callers request users or shares, the helper loads the XML fresh each time, selects the relevant top-level node, iterates children, extracts attributes without optional checks, and populates DTO containers. Access-list parsing is a small branch over missing node, wildcard, or comma-separated values.

State and persistence behavior: persistent state is external XML only. The class does not cache the document or watch for changes, so updates require a new method call. Passwords are read as plaintext strings and retained in memory in `User` objects.

Dependencies and integration points: depends on `System.Windows.Forms.Application`, `System.Xml`, `System.IO`, `UserCollection`, and `ShareSettings`. It is tightly coupled to the sample executable layout and the XML schema `Settings/Users/User` plus `Settings/Shares/Share`.

Risks: missing files, missing nodes, missing attributes, malformed XML, or blank `Accounts` strings throw runtime exceptions. Wildcard access maps to a hard-coded `Users` group, which may not match all deployments. Plaintext password storage is a security concern, and comma splitting does not trim whitespace.

Test signals: no local tests in this item. Useful tests would cover wildcard and comma access lists, absent optional access nodes, missing required attributes, reload behavior after XML changes, and path resolution relative to the executable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/SettingsHelper.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ShareSettings.cs -->
# sources/user-network-fs/smblibrary/SMBServer/ShareSettings.cs

Purpose: `ShareSettings` is a simple mutable data carrier for one SMB share definition.

Important APIs/types/functions: public fields `ShareName`, `SharePath`, `ReadAccess`, and `WriteAccess`; the constructor assigns all four values directly.

Control flow: there is no logic beyond construction. Instances are produced by `SettingsHelper.ReadSharesSettings()` and later consumed by server/share setup code.

State and persistence behavior: stores in-memory configuration only. The access lists are held by reference, not copied, so external mutations of the lists affect the instance.

Dependencies and integration points: depends on `System.Collections.Generic.List<string>` and is integrated with `SettingsHelper`.

Risks: public mutable fields allow uncontrolled changes and null values. No validation enforces a non-empty share name, valid path, or normalized access principals.

Test signals: tests should assert constructor assignment and downstream behavior when read/write lists are empty, wildcard-derived, or mutated after construction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/ShareSettings.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/User.cs -->
# sources/user-network-fs/smblibrary/SMBServer/User.cs

Purpose: `User` is the SMBServer account record used by `UserCollection`.

Important APIs/types/functions: public fields `AccountName` and `Password`; the constructor assigns both.

Control flow: no internal branching. It is constructed by `UserCollection.Add(accountName, password)` and by settings loading.

State and persistence behavior: in-memory plaintext credentials only; no hashing, expiration, or secure storage semantics.

Dependencies and integration points: used by `UserCollection` and populated from `SettingsHelper.ReadUserSettings()`.

Risks: public mutable plaintext password field is the main security and integrity risk. Null or duplicate account names are not rejected at this layer.

Test signals: tests should exercise construction, null/empty values if allowed by callers, and password lookup through `UserCollection`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/User.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/UserCollection.cs -->
# sources/user-network-fs/smblibrary/SMBServer/UserCollection.cs

Purpose: `UserCollection` extends `List<User>` with SMB account-specific lookup helpers.

Important APIs/types/functions: `Add(string,string)` creates a `User`; `IndexOf(string)` performs case-insensitive account lookup; `GetUserPassword(string)` returns the stored password or null; `ListUsers()` returns account names in list order.

Control flow: lookups linearly scan the list and compare `AccountName` using `StringComparison.OrdinalIgnoreCase`. Password lookup delegates to `IndexOf`.

State and persistence behavior: all state is inherited mutable list state. There is no duplicate enforcement, so the first case-insensitive match wins.

Dependencies and integration points: populated by `SettingsHelper` and likely consulted by authentication code.

Risks: linear lookup can be fine for small config files but scales poorly. Duplicate user names, null `AccountName`, and plaintext password handling are not guarded. Inheriting from `List<User>` exposes arbitrary mutation that can bypass helper semantics.

Test signals: useful tests include case-insensitive lookup, duplicate handling, null account behavior, empty collection lookup, and order preservation in `ListUsers()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBServer/UserCollection.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/BigEndianReader.cs -->
# sources/user-network-fs/smblibrary/Utilities/ByteUtils/BigEndianReader.cs

Purpose: `BigEndianReader` reads primitive numeric and GUID values from byte arrays or streams in network byte order.

Important APIs/types/functions: array readers for `Int16`, `UInt16`, 24-bit unsigned integer, `Int32`, `UInt32`, `Int64`, `UInt64`, and `Guid`; stream readers for the same except 24-bit uses a padded 4-byte buffer. `ref int offset` overloads advance the caller's cursor.

Control flow: each `ref` overload increments offset by the field width and calls `BigEndianConverter` at the prior offset. Stream overloads allocate fixed-size buffers and perform one `Read`.

State and persistence behavior: stateless utility; the only state mutation is the caller-provided offset.

Dependencies and integration points: depends on `BigEndianConverter` and `System.IO.Stream`. It pairs with `BigEndianWriter` for protocol serialization.

Risks: stream `Read` return values are ignored, so short reads produce partially zero-filled conversions rather than an error. Array overloads rely on runtime bounds exceptions. 24-bit conversion uses byte shifts promoted to signed `int`, but byte inputs remain safe for the target width.

Test signals: round-trip tests with `BigEndianWriter`, offset advancement tests, boundary buffer tests, and short stream read tests are the key coverage signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/BigEndianReader.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/BigEndianWriter.cs -->
# sources/user-network-fs/smblibrary/Utilities/ByteUtils/BigEndianWriter.cs

Purpose: `BigEndianWriter` serializes primitive numeric and GUID values to byte arrays or streams in big-endian order.

Important APIs/types/functions: `WriteInt16`, `WriteUInt16`, `WriteUInt24`, `WriteInt32`, `WriteUInt32`, `WriteInt64`, `WriteUInt64`, and `WriteGuid`; overloads write to buffer offsets, advance `ref int offset`, or write directly to a `Stream`.

Control flow: methods obtain bytes from `BigEndianConverter`, copy or write the relevant bytes, and advance offsets by fixed field sizes. UInt24 writes bytes 1..3 of a 32-bit big-endian representation.

State and persistence behavior: stateless except for mutating the target buffer/stream and offset.

Dependencies and integration points: pairs with `BigEndianReader` and `BigEndianConverter`, used wherever wire formats require network byte order.

Risks: no buffer capacity checks beyond `Array.Copy` exceptions. Stream writes assume the stream accepts the entire buffer. UInt24 silently truncates values above 24 bits.

Test signals: round trips for all widths, explicit byte-order assertions, offset movement, UInt24 truncation/bounds behavior, and GUID byte layout tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/BigEndianWriter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteReader.cs -->
# sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteReader.cs

Purpose: `ByteReader` provides endian-neutral byte, byte-array, ANSI, UTF-16, and null-terminated string reading helpers.

Important APIs/types/functions: `ReadByte`, `ReadBytes`, `ReadAnsiString`, `ReadUTF16String`, null-terminated ANSI/UTF-16 readers for arrays, `ReadBytes(Stream,count)`, `ReadAllBytes(Stream)`, and stream ANSI readers. ANSI uses code page 28591 to preserve byte values better than ASCII replacement.

Control flow: fixed-length methods copy or decode spans and advance `ref` offsets. Null-terminated methods loop until a zero terminator. Stream methods copy to a `MemoryStream` via `ByteUtils.CopyStream`.

State and persistence behavior: stateless, with caller offset mutation and stream position consumption.

Dependencies and integration points: depends on `ByteUtils.CopyStream`, `LittleEndianConverter` for UTF-16 null-terminated array reads, and .NET encodings.

Risks: null-terminated readers can overrun buffers or loop until stream `ReadByte()` returns -1, which becomes a nonzero char, if input is unterminated. No bounds checks precede array access. Stream fixed reads may return fewer bytes if the source ends early.

Test signals: fixed and null-terminated string tests, code page preservation tests for bytes above 0x7f, unterminated input failure behavior, offset advancement, and stream short-read cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteReader.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteUtils.cs -->
# sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteUtils.cs

Purpose: `ByteUtils` contains small byte-array and stream utilities shared by serialization and cryptography helpers.

Important APIs/types/functions: `Concatenate`, `AreByteArraysEqual`, `XOR` overloads, and `CopyStream` overloads with optional byte count.

Control flow: concatenation allocates and copies two arrays; equality compares length then bytes; XOR validates equal lengths or offset ranges and returns a newly allocated result; stream copy loops with up to a 1 MB buffer until count or EOF.

State and persistence behavior: stateless, but copies data from input streams to output streams and consumes stream position.

Dependencies and integration points: used by `ByteReader`, `AesCcm`, `AesCmac`, and other byte protocol code.

Risks: `AreByteArraysEqual` is not constant-time, so using it for authentication tags leaks timing information. `CopyStream` with a count of zero creates a zero-length buffer but does not read; with huge counts it loops until EOF. Null arrays are not handled.

Test signals: tests should cover XOR ranges, unequal length exceptions, copy limits, EOF before requested count, equality mismatch positions, and cryptographic call sites that need constant-time comparison.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteUtils.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteWriter.cs -->
# sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteWriter.cs

Purpose: `ByteWriter` writes raw bytes and encoded strings into byte arrays or streams.

Important APIs/types/functions: byte and byte-array writers, ANSI fixed-field writers using code page 28591, UTF-16 little-endian array writers, null-terminated ANSI/UTF-16 array writers, stream byte writers, ANSI stream writer with zero fill, UTF-8, UTF-16LE, and UTF-16BE stream string writers.

Control flow: buffer overloads write/copy at offsets and optionally advance `ref int offset`. Fixed string methods truncate to field length; stream ANSI pads with zero bytes when shorter than the field.

State and persistence behavior: stateless except target buffer/stream mutation and offset advancement.

Dependencies and integration points: pairs with `ByteReader` and protocol serializers.

Risks: buffer string writes do not zero-fill unused fixed fields, so stale bytes can remain. Truncation is silent. Length calculations use `value.Length`, which can differ from encoded byte length for non-Latin1 fallback cases. No explicit bounds validation.

Test signals: round-trip string tests, fixed-field truncation/padding tests, offset accounting, stale-byte behavior for short buffer writes, and UTF-16 terminator placement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/ByteWriter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/LittleEndianReader.cs -->
# sources/user-network-fs/smblibrary/Utilities/ByteUtils/LittleEndianReader.cs

Purpose: `LittleEndianReader` reads little-endian primitive integers and GUIDs from arrays and streams.

Important APIs/types/functions: array and stream readers for `Int16`, `UInt16`, `Int32`, `UInt32`, `Int64`, `UInt64`, and `Guid`, with `ref int offset` cursor advancement for arrays.

Control flow: methods advance offsets by fixed widths and delegate conversion to `LittleEndianConverter`; stream methods allocate exact-width buffers and read once.

State and persistence behavior: stateless apart from caller offset and stream position.

Dependencies and integration points: pairs with `LittleEndianWriter` and `LittleEndianConverter`; used for SMB-related binary layouts that are little-endian.

Risks: stream short reads are not detected. Array bounds errors are left to runtime exceptions. No float stream helpers despite converter support.

Test signals: endian byte-order assertions, writer round trips, offset advancement, GUID layout tests, and short stream behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/LittleEndianReader.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/LittleEndianWriter.cs -->
# sources/user-network-fs/smblibrary/Utilities/ByteUtils/LittleEndianWriter.cs

Purpose: `LittleEndianWriter` serializes integer and GUID values to byte arrays or streams in little-endian order.

Important APIs/types/functions: buffer/ref-offset/stream overloads for 16-, 32-, and 64-bit signed and unsigned integers, plus GUID buffer writers.

Control flow: delegates byte generation to `LittleEndianConverter`, copies/writes the bytes, and advances ref offsets by the field width.

State and persistence behavior: stateless except for target mutation and offset advancement.

Dependencies and integration points: pairs with `LittleEndianReader` and is a basic serializer for SMB binary structures.

Risks: no explicit capacity checks. Stream overload set lacks `WriteGuid(Stream, Guid)`, unlike the big-endian writer. Errors are runtime exceptions from the target.

Test signals: round-trip tests for each width, GUID buffer layout, offset movement, and consistency with `BitConverter` on little-endian hosts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/ByteUtils/LittleEndianWriter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Comparers/ReverseComparer.cs -->
# sources/user-network-fs/smblibrary/Utilities/Comparers/ReverseComparer.cs

Purpose: `ReverseComparer<T>` adapts an existing comparer to descending order.

Important APIs/types/functions: constructor stores an `IComparer<T>` and `Compare(x,y)` calls the wrapped comparer as `Compare(y,x)`.

Control flow: one delegated comparison with reversed operands.

State and persistence behavior: stores a comparer reference; no other state.

Dependencies and integration points: used by `KeyValuePairList.Sort` for descending key sort.

Risks: a null comparer causes `NullReferenceException`. Reversing operands can still overflow or violate ordering if the wrapped comparer is inconsistent.

Test signals: ascending versus descending sort tests and null-constructor behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Comparers/ReverseComparer.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Conversion/BigEndianConverter.cs -->
# sources/user-network-fs/smblibrary/Utilities/Conversion/BigEndianConverter.cs

Purpose: `BigEndianConverter` performs explicit big-endian conversions between byte arrays and integer/GUID values.

Important APIs/types/functions: `ToUInt16/Int16`, `ToUInt32/Int32`, `ToUInt64/Int64`, `ToGuid`, and `GetBytes` overloads for those types. GUID handling reverses the first three GUID fields on little-endian hosts to produce big-endian wire bytes.

Control flow: numeric reads combine shifted bytes; writes mask shifted values into byte arrays; GUID writes start from `Guid.ToByteArray()` and conditionally swap field bytes.

State and persistence behavior: stateless.

Dependencies and integration points: used by big-endian readers/writers and AES-CCM associated-data length encoding.

Risks: no bounds checks beyond runtime exceptions. `ToUInt32` shifts `byte` values as signed `int` before casting to `uint`, which still yields intended two's complement values but is subtle. GUID byte order is easy to misuse because .NET GUID layout differs from string/network layout.

Test signals: fixed vectors for integers and GUIDs, cross-platform tests for `BitConverter.IsLittleEndian`, and round trips through `BigEndianReader/Writer`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Conversion/BigEndianConverter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Conversion/Conversion.SimpleTypes.cs -->
# sources/user-network-fs/smblibrary/Utilities/Conversion/Conversion.SimpleTypes.cs

Purpose: this partial `Conversion` class provides forgiving object-to-simple-type conversion helpers with default values.

Important APIs/types/functions: `ToInt16`, `ToInt32`, `ToInt64`, `ToUInt16`, `ToUInt32`, `ToUInt64`, `ToFloat`, `ToDouble`, `ToDecimal`, `ToBoolean`, `ToString`, `ToChar`, and `ToDateTime`, most with overloads accepting a default value.

Control flow: each method initializes a result to the default, checks for null, calls the matching `System.Convert` method inside a broad `try/catch`, and silently returns the default on any exception.

State and persistence behavior: stateless.

Dependencies and integration points: likely used by UI/config parsing code that prefers defaults over exceptions.

Risks: catching all exceptions hides format, overflow, culture, and invalid-cast errors. `ToString(object)` has no caller-supplied default overload and returns empty string for null/failure. Culture-sensitive conversions may vary by current culture.

Test signals: tests should cover nulls, invalid strings, overflows, culture-sensitive decimal/date inputs, and explicit nonzero defaults.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Conversion/Conversion.SimpleTypes.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Conversion/LittleEndianConverter.cs -->
# sources/user-network-fs/smblibrary/Utilities/Conversion/LittleEndianConverter.cs

Purpose: `LittleEndianConverter` performs explicit little-endian conversions for integers, floating-point values, and GUIDs.

Important APIs/types/functions: `ToUInt16/Int16`, `ToUInt32/Int32`, `ToUInt64/Int64`, `ToFloat32`, `ToFloat64`, `ToGuid`, and `GetBytes` overloads for integer and GUID values.

Control flow: integer reads assemble bytes least-significant first; float reads copy bytes and reverse only on non-little-endian hosts before `BitConverter`; GUID reads use little-endian first fields and raw trailing bytes; writes mask shifted values.

State and persistence behavior: stateless.

Dependencies and integration points: used by little-endian readers/writers and UTF-16 null-terminated string reading.

Risks: bounds checks are implicit. Float write helpers are absent, so callers must use other APIs. GUID behavior follows .NET's mixed-endian layout and needs fixed-vector tests.

Test signals: integer, float, and GUID fixed vectors; cross-platform byte-order checks; round trips with reader/writer helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Conversion/LittleEndianConverter.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Cryptography/AesCcm.cs -->
# sources/user-network-fs/smblibrary/Utilities/Cryptography/AesCcm.cs

Purpose: `AesCcm` implements Counter with CBC-MAC mode as described by RFC 3610.

Important APIs/types/functions: public `Encrypt(key, nonce, data, associatedData, signatureLength, out signature)` and `DecryptAndAuthenticate(key, nonce, encryptedData, associatedData, signature)`; private `CalculateMac`, `BuildKeyStream`, `BuildB0Block`, `BuildABlock`, `ComputeFlagsByte`, and `AesEncrypt`.

Control flow: encryption validates nonce/tag length, builds an AES-CTR keystream, calculates CBC-MAC over B0, encoded associated data, padded associated data, and padded plaintext, XORs S0 with the MAC for the signature, then XORs plaintext with keystream after the first block. Decryption builds the same keystream, decrypts ciphertext, recomputes MAC, compares signatures, and throws on mismatch.

State and persistence behavior: stateless; all cryptographic material is passed as arrays and remains caller-managed.

Dependencies and integration points: uses `RijndaelManaged`, `CipherMode.CBC/ECB`, `ByteUtils`, `ByteReader`, `ByteWriter`, and `BigEndianConverter`. It likely supports SMB3 encryption/authentication paths.

Risks: associated data length >= 65280 is unsupported. Signature comparison uses non-constant-time `AreByteArraysEqual`. `RijndaelManaged` is legacy in modern .NET. Nonce reuse with a key would be catastrophic and is not prevented. Input arrays are not zeroed.

Test signals: RFC 3610 known-answer vectors, invalid nonce/tag length tests, tampered ciphertext/tag tests, empty associated data, unsupported associated-data length, and interop with platform AES-CCM where available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Cryptography/AesCcm.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Cryptography/AesCmac.cs -->
# sources/user-network-fs/smblibrary/Utilities/Cryptography/AesCmac.cs

Purpose: `AesCmac` computes AES-CMAC authentication tags.

Important APIs/types/functions: `CalculateAesCmac(key, buffer, offset, length)` slices input and delegates; `CalculateAesCmac(key, data)` generates subkeys, pads if necessary, encrypts with AES-CBC/no padding, and returns the final block; private `AESEncrypt` and `Rol`.

Control flow: AES encrypts a zero block to get L, left-shifts to K1 and conditionally XORs Rb, repeats for K2, mutates or pads the last data block, encrypts the full message under CBC with zero IV, and copies the last 16 bytes.

State and persistence behavior: stateless, but `CalculateAesCmac(key, data)` mutates the caller's `data` array for full-block messages and after padding reassignment for partial blocks.

Dependencies and integration points: uses `ByteReader`, `ByteUtils`, and `RijndaelManaged`; relevant for SMB signing or other protocol MACs.

Risks: mutating caller-provided data is surprising and can corrupt buffers reused by callers. Legacy AES API. No key length validation beyond crypto provider exceptions. No tests visible here.

Test signals: NIST SP 800-38B vectors, empty message, full-block and partial-block messages, assertion that input data is or is not mutated, and invalid key length behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Cryptography/AesCmac.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Cryptography/CRC32.cs -->
# sources/user-network-fs/smblibrary/Utilities/Cryptography/CRC32.cs

Purpose: `CRC32` implements a `HashAlgorithm` for standard CRC-32 and exposes convenience static computations.

Important APIs/types/functions: constants `DefaultPolynomial` and `DefaultSeed`; constructors for default/custom polynomial; overrides `Initialize`, `HashCore`, `HashFinal`, `HashSize`; static `Compute` overloads; `UPDC32` incremental update helper.

Control flow: initializes a 256-entry lookup table, iterates bytes updating the CRC, complements the final hash, and returns big-endian hash bytes for `HashAlgorithm`.

State and persistence behavior: instance state includes current `hash`, `seed`, and `table`; `defaultTable` is cached statically after first default initialization.

Dependencies and integration points: inherits `System.Security.Cryptography.HashAlgorithm`; can be used in stream hashing APIs.

Risks: `CalculateHash` loops `for (i = start; i < size; i++)`, treating `size` as an end index rather than `start + length`; this is correct only when `start` is zero and is a likely bug for `HashCore` with nonzero start. `defaultTable` initialization is not synchronized, though races produce equivalent data.

Test signals: standard CRC32 vector for `123456789`, HashAlgorithm incremental block tests with nonzero start offsets, custom polynomial tests, and `UPDC32` consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Cryptography/CRC32.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/BlockingQueue.cs -->
# sources/user-network-fs/smblibrary/Utilities/Generics/BlockingQueue.cs

Purpose: `BlockingQueue<T>` is a monitor-based producer/consumer queue with stop and abort semantics.

Important APIs/types/functions: `Enqueue(T)`, `Enqueue(List<T>)`, `TryDequeue(out T)`, `Stop()`, `Abort()`, and `Count`.

Control flow: enqueue ignores requests after stopping, locks the queue, enqueues items, increments `m_count`, and pulses a waiter when transitioning from empty. Dequeue waits while empty unless stopping, returns false when stopped and empty, otherwise dequeues and decrements. Abort clears queued items and stops.

State and persistence behavior: in-memory queue state only; `m_stopping` gates producers/consumers.

Dependencies and integration points: uses `Queue<T>` and `Monitor`; suitable for internal worker pipelines.

Risks: `Count` returns `m_count` without locking or `volatile`, so readers can see stale values. `Abort` clears `m_queue` but does not reset `m_count`, making `Count` inaccurate after abort. `Enqueue(List<T>)` only pulses one waiter even when many items arrive.

Test signals: multi-producer/multi-consumer tests, stop unblocks waiters, enqueue-after-stop behavior, abort count correctness, and count visibility under concurrency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/BlockingQueue.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/KeyValuePairList.Sort.cs -->
# sources/user-network-fs/smblibrary/Utilities/Generics/KeyValuePairList.Sort.cs

Purpose: this partial class adds key-based sorting helpers to `KeyValuePairList<TKey,TValue>`.

Important APIs/types/functions: `Sort()`, `Sort(ListSortDirection)`, `Sort(IComparer<TKey>, ListSortDirection)`, and `Sort(IComparer<TKey>)`.

Control flow: default sort uses `Comparer<TKey>.Default`; descending wraps the comparer with `ReverseComparer<TKey>`; final sorting delegates to `List<T>.Sort` with a comparison over pair keys.

State and persistence behavior: mutates the list in place.

Dependencies and integration points: depends on `ReverseComparer<T>`, `System.ComponentModel.ListSortDirection`, and the base partial `KeyValuePairList`.

Risks: key comparer exceptions propagate. Null keys may fail depending on comparer. Sort stability is not guaranteed.

Test signals: ascending/descending ordering, custom comparer behavior, duplicate keys, null key policy, and in-place mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/KeyValuePairList.Sort.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/KeyValuePairList.cs -->
# sources/user-network-fs/smblibrary/Utilities/Generics/KeyValuePairList.cs

Purpose: `KeyValuePairList<TKey,TValue>` is an ordered list of key/value pairs with convenience lookup and projection helpers.

Important APIs/types/functions: constructors, `ContainsKey`, `IndexOfKey`, `ValueOf`, `Add(key,value)`, `Keys`, `Values`, and a typed `GetRange`.

Control flow: key lookup scans linearly using `this[index].Key.Equals(key)`, value lookup returns the first match or `default(TValue)`, projections allocate new lists.

State and persistence behavior: inherits mutable `List<KeyValuePair<TKey,TValue>>`; ordering and duplicates are preserved.

Dependencies and integration points: sort behavior is supplied by `KeyValuePairList.Sort.cs`.

Risks: null keys cause `NullReferenceException` when `Equals` is called. Returning `default(TValue)` makes missing keys indistinguishable from stored default values. Duplicate keys are allowed and first-match semantics are implicit.

Test signals: duplicate key behavior, missing/default value ambiguity, null keys, range typing, and projection order.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/KeyValuePairList.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/Map.cs -->
# sources/user-network-fs/smblibrary/Utilities/Generics/Map.cs

Purpose: `Map<T1,T2>` implements a bidirectional one-to-one dictionary.

Important APIs/types/functions: `Add`, `ContainsKey`, `ContainsValue`, `TryGetKey`, `TryGetValue`, `RemoveKey`, `RemoveValue`, indexer by forward key, and `GetKey` by reverse value.

Control flow: `Add` inserts into both forward and reverse dictionaries; removals look up the opposite side and remove both entries; get methods delegate to the relevant dictionary.

State and persistence behavior: in-memory paired dictionaries only.

Dependencies and integration points: general utility for code needing reverse lookup.

Risks: `Add` is not transactional: if forward insert succeeds and reverse insert fails due to duplicate value, the map can become inconsistent. Null support depends on dictionary key types. No update method exists.

Test signals: duplicate key/value insertion, failed-add consistency, remove by key/value, reverse lookup, and missing-key exception behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/Map.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/Reference.cs -->
# sources/user-network-fs/smblibrary/Utilities/Generics/Reference.cs

Purpose: `Reference<T>` wraps a struct value in a mutable reference object.

Important APIs/types/functions: constructor, `Value` property, `ToString`, implicit conversion from wrapper to `T`, and implicit conversion from `T` to wrapper.

Control flow: no branching; conversions create or return the stored value.

State and persistence behavior: stores one mutable struct value in memory.

Dependencies and integration points: useful where APIs need reference-like mutation for value types.

Risks: implicit conversions can hide allocations and null wrapper dereferences. No thread safety.

Test signals: conversion behavior, mutation through `Value`, `ToString` delegation, and null wrapper conversion failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/Reference.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/SortedList.cs -->
# sources/user-network-fs/smblibrary/Utilities/Generics/SortedList.cs

Purpose: `SortedList<T>` is a custom sorted collection that inserts each item into a list at binary-search position.

Important APIs/types/functions: constructors with default/custom comparer, `Add`, `Contains`, `IndexOf`, `Remove`, `RemoveAt`, `CopyTo`, `Clear`, indexer, enumerators, `Count`, `IsReadOnly`, and static `FirstIndexOf`/`FindIndexForSortedInsert` overloads.

Control flow: `Add` finds an insertion index and inserts into the backing list. `FirstIndexOf` finds a candidate insertion point, checks equality, then walks backward to the first duplicate. `FindIndexForSortedInsert` performs a binary search and returns either an equal middle index or before/after the lower bound.

State and persistence behavior: stores sorted items in an in-memory `List<T>`.

Dependencies and integration points: generic utility; no persistence.

Risks: insertion is O(n) after O(log n) search. Returning an arbitrary equal index from insert means duplicate insertion order is not stable. Not thread-safe. Custom comparer inconsistency can break ordering.

Test signals: sorted insertion, duplicate handling, first-index lookup, custom comparer, removal, enumeration order, and empty/singleton edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Generics/SortedList.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Strings/QuotedStringUtils.cs -->
# sources/user-network-fs/smblibrary/Utilities/Strings/QuotedStringUtils.cs

Purpose: `QuotedStringUtils` provides simple quote wrapping, unwrapping, searching, and splitting while ignoring separators inside double quotes.

Important APIs/types/functions: `Quote`, `Unquote`, `IsQuoted`, `IndexOfUnquotedChar`, `IndexOfUnquotedString`, and `SplitIgnoreQuotedSeparators`.

Control flow: quote checks look at first/last characters. Search methods toggle an `inQuote` boolean on every `"` and match only outside quotes. Split repeatedly finds unquoted separators and applies optional `RemoveEmptyEntries`.

State and persistence behavior: stateless string utility.

Dependencies and integration points: general parser helper for command/config-like strings.

Risks: escaped quotes are not supported, unmatched quotes simply keep `inQuote` true through the end, and `IndexOfUnquotedString` repeatedly calls `Substring(index)`, which is less efficient. Null inputs are not handled.

Test signals: quoted and unquoted separators, empty entries, unmatched quotes, escaped quote expectations, multi-character string search, and null/empty strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Strings/QuotedStringUtils.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Threading/CountdownLatch.cs -->
# sources/user-network-fs/smblibrary/Utilities/Threading/CountdownLatch.cs

Purpose: `CountdownLatch` lets callers wait until an incremented count returns to zero.

Important APIs/types/functions: `Increment`, `Add`, `Decrement`, and `WaitUntilZero`.

Control flow: increments/adds adjust `m_count` atomically and reset the manual-reset event when transitioning from zero. Decrement decrements atomically, sets the event when count reaches zero, and throws if it goes negative.

State and persistence behavior: in-memory counter plus `EventWaitHandle`, initially signaled because count starts at zero.

Dependencies and integration points: uses `Interlocked` and `EventWaitHandle`; useful for coordinating worker completion.

Risks: `Decrement` checks `m_count == 0` rather than the local `count`, a minor race/read consistency smell. Negative decrement throws after decrementing, leaving count negative and the event state potentially inconsistent. The wait handle is never disposed.

Test signals: wait-until-zero behavior, add/increment transitions, negative decrement behavior, concurrent decrement race tests, and disposal expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Threading/CountdownLatch.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Threading/Parallel.cs -->
# sources/user-network-fs/smblibrary/Utilities/Threading/Parallel.cs

Purpose: `Parallel` provides a C# 2.0-era parallel for-loop implementation.

Important APIs/types/functions: delegates `ForDelegate` and `DelegateProcess`; overloads `For(fromInclusive,toExclusive,delegate)`, `For(...,chunkSize,delegate)`, and `For(...,chunkSize,threadCount,delegate)`.

Control flow: a shared `index` is advanced by `chunkSize` under a lock; each async delegate processes its chunk until it reaches `toExclusive`; the caller waits with `EndInvoke` for all delegates.

State and persistence behavior: no persistent state; parallel work can mutate caller-owned state.

Dependencies and integration points: uses `Environment.ProcessorCount`, delegates, and asynchronous delegate invocation.

Risks: exceptions propagate from `EndInvoke` but other workers may have already run. No cancellation. Invalid `chunkSize <= 0` can loop incorrectly. The name conflicts with `System.Threading.Tasks.Parallel` in newer code.

Test signals: coverage for chunk boundaries, out-of-order execution, exceptions, custom thread count, invalid chunk size, and inclusive/exclusive range correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/Utilities/Threading/Parallel.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/.appveyor.yml -->
# sources/user-network-fs/sshfs/.appveyor.yml

Purpose: AppVeyor CI config builds sshfs on Windows/Cygwin with WinFsp-backed FUSE.

Important APIs/types/functions: install steps download WinFsp v1.4B2, install cygfuse support for 64-bit and 32-bit Cygwin, install `libglib2.0-devel` and `meson`, and run `test\appveyor-build.sh` in both Cygwin environments.

Control flow: AppVeyor executes install commands, then build script commands for each architecture.

State and persistence behavior: CI-only environment setup; no repository persistence.

Dependencies and integration points: external WinFsp release URL, Cygwin setup mirrors, Meson/Ninja, and `test/appveyor-build.sh`.

Risks: old pinned WinFsp beta and HTTP Cygwin mirror can be availability/security risks. No explicit tests are run beyond build in the script shown.

Test signals: successful 32/64-bit Cygwin builds and installer availability are the main signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/.appveyor.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/.github/dependabot.yml -->
# sources/user-network-fs/sshfs/.github/dependabot.yml

Purpose: Dependabot configuration for GitHub Actions updates.

Important APIs/types/functions: version 2 config, `github-actions` ecosystem at `/`, weekly schedule, 14-day cooldown, and one group matching all action updates.

Control flow: Dependabot periodically scans workflow action references and groups matching updates.

State and persistence behavior: GitHub-hosted automation state only; no runtime effect.

Dependencies and integration points: integrates with GitHub Dependabot and the repository workflows.

Risks: grouped updates reduce PR noise but can make a broken action update harder to isolate. Cooldown delays security/nonsecurity updates.

Test signals: Dependabot PR generation and successful CI after grouped action bumps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/.github/workflows/build-platforms.yml -->
# sources/user-network-fs/sshfs/.github/workflows/build-platforms.yml

Purpose: GitHub Actions workflow validating sshfs across platform variants beyond the primary Ubuntu compiler matrix.

Important APIs/types/functions: triggers on push, pull request, and manual dispatch; read-only contents permission; concurrency cancellation; `linux-compat` matrix for Ubuntu latest/22.04/ARM/release/debug/hardened; Alpine musl container build; FreeBSD VM build; artifact upload on test/build failures.

Control flow: Linux jobs install compiler, Meson, FUSE3, GLib, and optionally OpenSSH/FUSE test dependencies, build with Meson/Ninja, configure localhost SSH for test lanes, check `/dev/fuse`, run pytest from build, and upload logs/results. Alpine and FreeBSD jobs perform build-only validation in their environments.

State and persistence behavior: CI artifacts persist test XML and Meson logs.

Dependencies and integration points: pinned GitHub actions, Docker Alpine image digest, `vmactions/freebsd-vm`, Meson build files, and pytest tests.

Risks: FUSE availability on hosted runners can be fragile. Build-only non-Linux lanes may miss runtime bugs. Pinned actions improve repeatability but require maintenance.

Test signals: matrix build success, pytest on Linux lanes, hardened CFLAGS build, musl build, FreeBSD build, and uploaded logs for failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/.github/workflows/build-platforms.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/.github/workflows/build-ubuntu.yml -->
# sources/user-network-fs/sshfs/.github/workflows/build-ubuntu.yml

Purpose: primary Ubuntu CI workflow for building and testing sshfs with GCC/Clang and strict warning settings.

Important APIs/types/functions: build-and-test matrix over `gcc`/`clang` and `debugoptimized`/`release`; strict-warnings matrix with extra warning flags; setup-python, checkout, dependency installation, Meson `-Dwerror=true`, Ninja build, artifact upload, SSH localhost setup, FUSE checks, and pytest execution.

Control flow: each build matrix installs deps, prints versions, sets up SSH keys/server, verifies FUSE, builds with selected compiler/buildtype, uploads `build/sshfs`, and runs tests. Strict-warning jobs build with warning-focused CFLAGS but do not run FUSE tests.

State and persistence behavior: CI artifacts include binary and pytest/Meson logs.

Dependencies and integration points: Ubuntu 24.04 runner, libfuse3, GLib, OpenSSH server/client, Meson, pytest, and repository tests.

Risks: `-Dwerror=true` can fail on compiler warning drift. Runtime tests depend on runner FUSE permissions and SSH service behavior. Artifacts may expose build outputs but not secrets.

Test signals: compiler/buildtype matrix, strict warnings, localhost SSH smoke test, `/dev/fuse` check, pytest JUnit output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/.github/workflows/build-ubuntu.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/.pre-commit-config.yaml -->
# sources/user-network-fs/sshfs/.pre-commit-config.yaml

Purpose: pre-commit hook configuration for basic repository hygiene and shell linting.

Important APIs/types/functions: `pre-commit-hooks` v4.0.1 for trailing whitespace, end-of-file fixer, YAML validation, and large-file checks; `jumanjihouse/pre-commit-hooks` 2.1.5 for `shellcheck`.

Control flow: `pre-commit run --all-files` executes these hooks, also used by `test/lint.sh`.

State and persistence behavior: modifies files when formatting hooks apply; otherwise local hook cache only.

Dependencies and integration points: pre-commit framework and shellcheck hook repo.

Risks: old hook revisions may lag current checks. C code formatting/linting is not covered.

Test signals: clean `pre-commit run --all-files --show-diff-on-failure` output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/.pre-commit-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/.travis.yml -->
# sources/user-network-fs/sshfs/.travis.yml

Purpose: legacy Travis CI configuration for lint and build/test jobs.

Important APIs/types/functions: Ubuntu focal C environment, pip cache, apt packages including shellcheck, valgrind, compilers, docutils, Meson, pytest, and GLib; install script `test/travis-install.sh`; jobs for lint and build/test.

Control flow: Travis installs dependencies, runs `./test/lint.sh` for lint job, and `test/travis-build.sh` for build/test job.

State and persistence behavior: CI-only cache/pipeline state.

Dependencies and integration points: scripts referenced here are outside this work item except `test/lint.sh`.

Risks: Travis may no longer be active for the project, and referenced scripts are omitted from the requested source list. Dependency versions are older than GitHub Actions workflows.

Test signals: lint and Travis build/test job success when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/.travis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/cache.c -->
# sources/user-network-fs/sshfs/cache.c

Purpose: `cache.c` implements a FUSE operation proxy that caches attributes, directory entries, and symlink targets for sshfs.

Important APIs/types/functions: public `cache_wrap`, `cache_parse_options`, `cache_add_attr`, `cache_invalidate`, and `cache_get_write_ctr`; internal `struct cache`, `struct node`, directory entry/file-handle wrappers, cache cleanup, lookup/purge helpers, cached `getattr`, `readlink`, `opendir/readdir/releasedir`, mutating operation invalidators, and `cache_fill`.

Control flow: `cache_wrap` records the underlying operations, creates a GLib hash table, initializes the mutex, and returns a filled wrapper operation table. Reads first check cache entries under lock and fall through to underlying FUSE callbacks on miss/expiry. Directory reads either replay cached entries or open/read the underlying directory and cache a null-terminated `GPtrArray`. Mutating operations delegate first and then purge affected entries/parents on success. `cache_add_attr` accepts a write counter snapshot and only caches if no write invalidation occurred since the snapshot.

State and persistence behavior: process-local cache state in a global `cache` struct. Entries expire by stat/link/dir TTL and are cleaned by size/time thresholds. `write_ctr` increments on writes to prevent stale attrs from racing into cache.

Dependencies and integration points: depends on libfuse3 operation signatures, GLib hash/pointer arrays, pthread mutexes, and `cache.h`. `sshfs.c` wraps `sshfs_oper` with this layer when `dir_cache` is enabled.

Risks: path-prefix child invalidation uses `strncmp(key,path,strlen(path))`, so `/foo` also matches `/foobar`. Directory cache replay ignores filler errors. `cache_init` assumes underlying `init` exists. Some indentation suggests legacy style but not behavior. TTL cache may expose stale remote state between invalidations.

Test signals: tests should cover stat/readlink/readdir hits and expiry, write-counter stale attr rejection, parent purge on create/delete/rename, prefix invalidation edge cases, and cache disabled/enabled integration via sshfs options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/cache.h -->
# sources/user-network-fs/sshfs/cache.h

Purpose: header declaring the sshfs FUSE cache wrapper API.

Important APIs/types/functions: `cache_wrap`, `cache_parse_options`, `cache_add_attr`, `cache_invalidate`, and `cache_get_write_ctr`.

Control flow: no implementation; it exposes cache lifecycle, option parsing, explicit invalidation, and write-counter access to `sshfs.c`.

State and persistence behavior: declarations only; state lives in `cache.c`.

Dependencies and integration points: includes FUSE headers and is included by `sshfs.c` and `cache.c`.

Risks: public functions expose raw paths and stat pointers; callers must follow locking/ordering expectations documented only by implementation.

Test signals: compile-time integration and behavior tests through `cache.c`/sshfs with `dir_cache` options.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/compat/darwin_compat.c -->
# sources/user-network-fs/sshfs/compat/darwin_compat.c

Purpose: provides a pthread-based POSIX semaphore compatibility layer for Darwin/macOS builds.

Important APIs/types/functions: `darwin_sem_init`, `darwin_sem_destroy`, `darwin_sem_getvalue`, `darwin_sem_post`, `darwin_sem_timedwait`, `darwin_sem_trywait`, and `darwin_sem_wait`.

Control flow: initialization rejects process-shared semaphores, initializes condition variable and mutex, stores count and an internal ID. Wait operations lock, validate ID, wait on the condition if count is zero, decrement on success, and use cleanup handlers to unlock. Post increments and signals on transition to one. Destroy marks invalid, broadcasts, destroys cond/mutex.

State and persistence behavior: semaphore state is embedded in `darwin_sem_t`; no global state.

Dependencies and integration points: used on Apple builds through macros in `darwin_compat.h`; `sshfs.c` uses `sem_t` for request completion.

Risks: `sem_wait` treats a spurious wakeup with zero count as `EINTR` instead of looping, which differs from normal semaphore semantics. Destroy while waiters exist is delicate. `sem_timedwait` asserts non-timeout errors from pthread condition wait.

Test signals: macOS build and concurrency tests for wait/post, trywait, timedwait timeout, destroy wakeups, and spurious wake tolerance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/compat/darwin_compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/compat/darwin_compat.h -->
# sources/user-network-fs/sshfs/compat/darwin_compat.h

Purpose: header that maps POSIX semaphore names to Darwin compatibility functions.

Important APIs/types/functions: `darwin_sem_t`, `DARWIN_SEM_VALUE_MAX`, prototypes for all `darwin_sem_*` functions, typedef `sem_t`, and macros mapping `sem_init`, `sem_destroy`, `sem_getvalue`, `sem_post`, `sem_timedwait`, `sem_trywait`, and `sem_wait`.

Control flow: declarations/macros only.

State and persistence behavior: semaphore instances hold count, mutex, and condition variable state.

Dependencies and integration points: included instead of `<semaphore.h>` on Apple builds by `sshfs.c`.

Risks: macro replacement requires callers not to include the system semaphore header. `DARWIN_SEM_VALUE_MAX` is low compared with some systems but enough for request semaphores.

Test signals: Apple compile, macro compatibility with `sshfs.c`, and behavior tests in `darwin_compat.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/compat/darwin_compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/make_release_tarball.sh -->
# sources/user-network-fs/sshfs/make_release_tarball.sh

Purpose: release helper that creates and signs an `sshfs-3*` source tarball from a Git tag.

Important APIs/types/functions: chooses latest matching tag unless an argument is provided, creates a directory, extracts `git archive`, deletes `.gitignore`, removes release-excluded CI/helper files, creates an xz tarball, signs it with GPG, and prints contributor names since the previous merged tag.

Control flow: `set -e` aborts on errors; tag selection branch; archive/exclusion/signing; previous tag lookup and `git log` summary.

State and persistence behavior: creates `${TAG}/`, `${TAG}.tar.xz`, and detached signature in the current directory.

Dependencies and integration points: Git tags, tar with xz support, GPG, and historical Travis scripts.

Risks: existing output directory causes failure. It removes fixed files that may not exist in newer trees. Tag lookup depends on tag naming/merge history.

Test signals: dry-run in a clean clone, expected tarball contents, valid GPG signature, and contributor range correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/make_release_tarball.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/meson.build -->
# sources/user-network-fs/sshfs/meson.build

Purpose: Meson build definition for the sshfs executable, man page, install helper, and tests.

Important APIs/types/functions: project `sshfs` C version 3.7.6; global compile arguments; compiler probe for broken `-Wunused-result`; `config.h` with `PACKAGE_VERSION` and platform `IDMAP_DEFAULT`; source list including Darwin compat when needed; dependencies `fuse3 >= 3.1.0`, `glib-2.0`, `gthread-2.0`; executable with `-DFUSE_USE_VERSION=31`; optional `rst2man` manpage target; install helper; `subdir('test')`.

Control flow: configure-time platform and compiler checks adjust defines/sources/arguments, then build targets are declared.

State and persistence behavior: generates build-directory `config.h`, executable, optional man page, copied test scripts, and install artifacts.

Dependencies and integration points: drives all CI workflows and local builds; integrates with `sshfs.c`, `cache.c`, `compat/darwin_compat.c`, and test Meson file.

Risks: old minimum Meson may limit newer features. `IDMAP_DEFAULT` differs by platform, changing runtime default behavior. Optional manpage silently skipped when rst2man is absent.

Test signals: Meson setup on Linux/Darwin/FreeBSD/Alpine, dependency resolution, warning probe behavior, executable build, manpage build when docutils is installed, and test subdir target generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/sshfs.c -->
# sources/user-network-fs/sshfs/sshfs.c

Purpose: `sshfs.c` is the main SSHFS FUSE filesystem implementation. It parses mount options, starts SSH/SFTP transports, marshals SFTP v3 packets, maps FUSE operations to SFTP requests, manages async reads/writes and multiple SFTP connections, handles UID/GID mapping, symlink policies, workarounds, and process lifecycle.

Important APIs/types/functions: SFTP constants and extensions; core state structs `conn`, `buffer`, `request`, `sshfs_file`, and global `sshfs`; option tables `sshfs_opts` and `workaround_opts`; buffer marshal/unmarshal helpers; connection functions `start_ssh`, `connect_to`, `connect_vsock`, `connect_remote`, `start_processing_thread`; request functions `sftp_request_send`, `sftp_request_wait`, `process_requests`; FUSE handlers in `sshfs_oper`; option parsing `sshfs_opt_proc`, `find_base_path`, `parse_workarounds`; id mapping `read_id_map`, `load_uid_map`, `load_gid_map`; and `main`.

Control flow: startup initializes defaults, parses FUSE/SSHFS/workaround/cache options, validates host and mountpoint, prepares SSH arguments, wraps operations with `cache_wrap` when enabled, creates and mounts a FUSE session, connects to SFTP unless delayed, daemonizes, and enters `fuse_loop` or `fuse_loop_mt`. Each FUSE handler builds a `buffer` for the relevant SFTP packet, chooses a connection with `get_conn`, sends through `sftp_request*`, waits or registers async completion, decodes replies, and returns negative errno on failure. A per-connection processing thread reads SFTP replies, matches IDs in `reqtab`, updates outstanding byte accounting, and wakes semaphores or runs async end callbacks.

State and persistence behavior: process state lives in global `sshfs`: connection array, request hash, open-file connection table, options, ID maps, stats, password page, and modification version. Remote filesystem state persists through the SFTP server. Directory/attribute/link cache state is delegated to `cache.c`. Passwords read from stdin are mmap/mlock-protected and zeroed/unmapped after first use when reconnect is disabled.

Dependencies and integration points: integrates libfuse3, GLib hash/list allocation helpers, pthreads, semaphores or Darwin compatibility semaphores, OpenSSH via child process/socketpair, direct TCP, Linux vsock, system passwd/group lookup, and `cache.h`. CI exercises it through Meson and pytest.

Risks: large global mutable state and mixed async/sync paths make concurrency correctness central. `find_base_path` now rejects dash-prefixed hostnames, mitigating option injection, but command construction and `ssh_command` tokenization still require care. `tokenize_on_space` inspects `*(pos - 1)` when `pos` is at the start, which is undefined behavior for a leading nonspace token. Reconnect and multi-connection ordering are complex. `read_id_map` requires ownership/non-writable checks but exits the process on config errors. The truncate workaround can copy whole files into memory when shrinking.

Test signals: GitHub workflows build with GCC/Clang, strict warnings, platform variants, and pytest. The requested test file specifically validates hostname option-injection rejection. Important additional tests include SFTP request error mapping, async read/write flush semantics, multi-connection ordering, symlink containment, UID/GID map parsing/security checks, reconnect behavior, truncate workaround paths, and cache-enabled operation integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/sshfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/appveyor-build.sh -->
# sources/user-network-fs/sshfs/test/appveyor-build.sh

Purpose: AppVeyor helper script that performs a Meson/Ninja build in an architecture-specific directory.

Important APIs/types/functions: detects `uname -m`, creates `build-$machine`, runs `meson ..`, then `ninja`.

Control flow: `set -e` aborts on the first failing command.

State and persistence behavior: creates a build directory under the repository checkout in CI.

Dependencies and integration points: invoked by `.appveyor.yml` for both Cygwin environments.

Risks: fails if build directory already exists. It does not run tests or pass warning flags.

Test signals: successful AppVeyor build for each architecture.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/appveyor-build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/conftest.py -->
# sources/user-network-fs/sshfs/test/conftest.py

Purpose: pytest configuration that improves failure diagnostics and fails tests on suspicious process output.

Important APIs/types/functions: `pytest_pyfunc_call` sleeps after a failed test; `pass_capfd` fixture attaches capture to unittest instances; `check_test_output` replays captured output, strips registered false positives, and scans for suspicious words/Valgrind prefixes; `register_output` monkeypatch helper; autouse `save_cap_fixtures`; `pytest_runtest_call` invokes output checks.

Control flow: every test gets a `capfd.false_positives` list and monkeypatched registration method. After test call, output is checked unless capture is disabled. Suspicious stdout/stderr raises `AssertionError`.

State and persistence behavior: uses module-global `current_capfd`, intentionally relying on sequential pytest execution.

Dependencies and integration points: pytest hook system, `capfd`, regex scanning, and test modules that can register expected output.

Risks: the global fixture hack is incompatible with parallel pytest execution. Broad suspicious-word scanning may create false positives. Output checks occur after the test body and can mask original intent if not diagnosed carefully.

Test signals: pytest self-behavior through the suite, false-positive registration tests if present, and no suspicious output in sshfs runtime tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/conftest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/lint.sh -->
# sources/user-network-fs/sshfs/test/lint.sh

Purpose: lint helper for CI/local validation using pre-commit.

Important APIs/types/functions: installs `pre-commit` with `pip3 --user` and runs `pre-commit run --all-files --show-diff-on-failure`.

Control flow: `set -e` aborts on install or hook failure.

State and persistence behavior: modifies user-local Python package state and may create pre-commit caches; hooks may report diffs.

Dependencies and integration points: used by Travis lint job; consumes `.pre-commit-config.yaml`.

Risks: installing into user site during CI can be version-sensitive. No pin for `pre-commit` itself.

Test signals: successful hook execution with no diffs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/lint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/meson.build -->
# sources/user-network-fs/sshfs/test/meson.build

Purpose: Meson test subdirectory definition for sshfs tests and helper files.

Important APIs/types/functions: `test_scripts` list includes pytest config, `test_sshfs.py`, `test_hostname_validation.py`, and `util.py`; `custom_target` copies them into the build dir; builds `wrong_command` helper from C; registers `test('wrong_cmd', wrong_cmd)`.

Control flow: during build, test scripts are copied preserving metadata; Meson also builds and can run the `wrong_cmd` test target.

State and persistence behavior: creates copied test files and helper executable in the build directory.

Dependencies and integration points: links source tests to build-tree pytest invocations used by CI.

Risks: the file list must stay in sync with test additions. The custom target copies rather than generating a package manifest, so omitted tests may not run from build dir.

Test signals: Meson build target completion and `ninja test` wrong-command helper behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/pytest.ini -->
# sources/user-network-fs/sshfs/test/pytest.ini

Purpose: pytest defaults for the sshfs test suite.

Important APIs/types/functions: `addopts` enables verbose output, assertion rewrite, native tracebacks, stop after first failure, and summary reporting; marker `uses_fuse` identifies tests requiring FUSE.

Control flow: pytest applies these defaults when run in the test directory or with this config discovered.

State and persistence behavior: no state; test runner configuration only.

Dependencies and integration points: used by CI pytest commands.

Risks: `-x` stops on first failure, which can reduce full failure visibility in local runs despite CI using `--maxfail=99` overrides in some workflows.

Test signals: pytest collection recognizes the `uses_fuse` marker without warnings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/pytest.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/sshfs/test/test_hostname_validation.py -->
# sources/user-network-fs/sshfs/test/test_hostname_validation.py

Purpose: focused pytest module validating that sshfs rejects dash-prefixed hostnames that could be interpreted as SSH options.

Important APIs/types/functions: executable self-runner under `__main__`; imports `subprocess`, `base_cmdline`, `basename`; tests `test_reject_option_injection_in_hostname` and `test_reject_dash_host_after_doubledash`.

Control flow: each test creates a temporary mount directory, constructs an sshfs command line pointing at the built executable, runs it with captured output and 10-second timeout, and asserts nonzero exit plus `invalid hostname` in stderr. One case uses bracketed host syntax resolving to `-oProxyCommand=...`; the other passes a dash-prefixed source after `--`.

State and persistence behavior: creates temporary directories only; no mount should occur because validation fails before connecting.

Dependencies and integration points: directly tests `find_base_path`/argument parsing behavior in `sshfs.c`, using test utilities from `util.py`.

Risks: depends on exact stderr wording. It covers dash-host rejection but not all command injection surfaces such as custom `ssh_command` tokenization or unusual bracket syntax.

Test signals: both tests must fail fast with nonzero return and `invalid hostname`, proving the host parser does not pass dash-prefixed hosts through to ssh.
<!-- END_FILE_RESEARCH: sources/user-network-fs/sshfs/test/test_hostname_validation.py -->
