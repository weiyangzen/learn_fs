# subset-b-007002 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ssd_driver.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_ssd_driver.cc

## Purpose
`rgw_ssd_driver.cc` implements the SSD-backed D4N cache driver. It maps RGW cache keys into a local filesystem hierarchy, stores cached data in ordinary files, stores RGW/cache metadata in extended attributes, exposes synchronous and POSIX AIO-backed read/write paths, and restores dirty/clean cache records after restart.

## Important APIs, Types, and Functions
Static helpers split `CACHE_DELIM` keys, derive `<cache>/<bucket_id>/<object>/<version[_offset_len]>`, create directories through temporary names and atomic rename, and return final paths. `SSDDriver::initialize()` prepares or evicts the cache directory and initializes libc aio tunables. `put()`, `get()`, `append_data()`, `delete_data()`, and `rename()` implement the core file operations. Template `get_async()` and `put_async()` wrap `AsyncReadOp` and `AsyncWriteRequest` in `ceph::async::Completion`; public `get_async()`/`put_async()` adapt those operations to `rgw::Aio`. Attribute methods use `listxattr()`, `getxattr()`, `setxattr()`, and `removexattr()`.

## Control Flow
Writes create a temporary file path, prepare an `aiocb`, copy the bufferlist into heap memory, submit `aio_write()`, set xattrs on the temporary file in the callback, refresh free-space accounting, then rename the temp file into the final version path. Reads open the resolved path, allocate a bufferlist-backed buffer, submit `aio_read()`, and dispatch the completion with the data. Synchronous wrappers either run the async path on a yield executor or block through `ceph::async::use_blocked`.

`restore_blocks_objects()` scans the cache directory by bucket and object, parses version or block filenames, reads dirty/local-weight/metadata xattrs, rebuilds object keys, decodes ACL owner information, and calls supplied object/block callbacks.

## State and Persistence Behavior
Persistent state is the local directory tree plus file xattrs. The driver tracks `Partition`, `free_space`, `cct`, an `admin` flag, and a mutex for free-space updates. Data writes are made atomic at file-name level by temp-write plus rename, but xattr writes happen before the rename. Dirty cached objects store enough metadata to reconstruct object callbacks.

## Dependencies and Integration Points
The file depends on `CacheDriver`, RGW AIO throttling, `DoutPrefixProvider`, `rgw::sal::Attrs`, RGW cache xattr names, ACL decoding, URL encode/decode helpers, `std::filesystem`, POSIX file I/O, xattrs, and libc AIO. It is the file-backed cache backend used by D4N cache code and administrative restore flows.

## Risks
The key parser only handles 3- and 5-token forms, so malformed keys can yield empty paths. `get_attr()` returns positive `errno` in some paths while other methods return negative errors. Write callbacks assign errors from `ret` after attr failure even though `ret` may be zero. `malloc()` failure closes the fd but returns the old open result. Directory creation/removal races are partially handled, but path-based operations remain sensitive to concurrent deletes. `get()` allocates a stack small_vector sized by caller length, which can be large.

## Test Signals
Exercise initialization with and without eviction, admin mode, key parsing for head and block keys, temp-file rename atomicity, xattr round trips, read/write/append/delete paths, ENOENT retry on write, concurrent delete/write races, restore of dirty and clean entries, ACL decode failures, reserve-space accounting, and AIO error callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ssd_driver.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ssd_driver.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_ssd_driver.h

## Purpose
`rgw_ssd_driver.h` declares the SSD cache driver that implements `rgw::cache::CacheDriver` on top of local files, xattrs, and POSIX AIO.

## Important APIs, Types, and Functions
`SSDDriver` overrides cache operations for initialization, put/get, async put/get, append, delete, rename, attribute CRUD, free-space reporting, partition reporting, and block/object restoration. Private nested handlers bridge Boost/system errors into `rgw::AioResult`. `libaio_aiocb_deleter` closes file descriptors and releases `aiocb` objects. `AsyncReadOp` owns the read result and aiocb; `AsyncWriteRequest` owns paths, copied data, fd, attrs, and backpointer to the driver.

## Control Flow
The public interface follows the `CacheDriver` contract. Synchronous methods call the private async templates with a yield or blocked token. RGW Aio methods return operation functions that schedule local AIO and complete into the upstream throttle.

## State and Persistence Behavior
The class stores `Partition partition_info`, `free_space`, `CephContext*`, a mutex, and `admin`. Nested operation objects own transient async state until callbacks dispatch completion. Persistent behavior is implemented in the `.cc` file through filesystem files and xattrs.

## Dependencies and Integration Points
The header includes `rgw_common.h`, `rgw_cache_driver.h`, POSIX aio, Ceph async completion, Boost ASIO executor support, and RGW Aio types. It is consumed by the D4N cache factory and code that expects a `CacheDriver`.

## Risks
The nested completion data contains non-owning references to `DoutPrefixProvider`, `SSDDriver`, and `rgw::Aio`; callers must keep them live until callbacks complete. The custom deleter assumes `aio_fildes > 0`, so fd zero would not be closed. The API accepts full `Attrs` maps, which can be expensive to copy into async lambdas.

## Test Signals
Compile/link coverage should verify the `CacheDriver` override signatures. Runtime tests should cover async completion lifetime, callback dispatch into `rgw::Aio`, attr propagation, and destructor cleanup of `aiocb` file descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_ssd_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_string.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_string.cc

## Purpose
`rgw_string.cc` implements wildcard matching for RGW string utilities.

## Important APIs, Types, and Functions
`match_wildcards(pattern, input, flags)` maps RGW's `MATCH_CASE_INSENSITIVE` flag to `FNM_CASEFOLD` and delegates matching to libc `fnmatch()`.

## Control Flow
The function builds the `fnmatch()` flag word, calls `fnmatch(pattern.data(), input.data(), flag)`, and returns true only on exact match success.

## State and Persistence Behavior
The file is stateless and has no persistence side effects.

## Dependencies and Integration Points
It depends on `rgw_string.h` and `<fnmatch.h>`. Callers use it for glob-style matching of RGW policy/configuration strings.

## Risks
`std::string::data()` is expected to be null-terminated in modern C++; older assumptions would be risky. Behavior follows platform `fnmatch()`, including escaping and path-separator semantics. Case folding depends on `FNM_CASEFOLD` availability.

## Test Signals
Cover `*`, `?`, empty strings, literal metacharacters, case-sensitive and insensitive matches, and platform behavior for path separators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_string.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_string.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_string.h

## Purpose
`rgw_string.h` provides small reusable string utilities for case-insensitive comparisons, numeric conversion, `string_view` conversion, efficient concatenation/join, and wildcard matching.

## Important APIs, Types, and Functions
`ltstr_nocase` and `stringcasecmp()` wrap `strcasecmp()`/`strncasecmp()`. `stringtoll()`, `stringtoull()`, `stringtol()`, and `stringtoul()` parse decimal strings and reject trailing characters. `sview2cstr()` copies a `string_view` into a small-vector-backed C string. `sarrlen()` returns string literal length at compile time. `string_size()`, `string_cat_reserve()`, and `string_join_reserve()` precompute lengths to avoid repeated reallocations. `MATCH_CASE_INSENSITIVE` and `match_wildcards()` expose glob matching.

## Control Flow
Most helpers are inline templates. Concatenation and join compute total reserve size through `detail::sum()` and `string_traits`, then append `string_view` arguments in order.

## State and Persistence Behavior
No persistent state. Output strings and vectors are caller-owned.

## Dependencies and Integration Points
The header uses Boost small_vector, C string conversion functions, and RGW callers across auth, policy, and request parsing. `match_wildcards()` is implemented in `rgw_string.cc`.

## Risks
The integer parsers only check max sentinels, not `errno`, so some underflow/overflow and range truncation cases can slip through. `stringcasecmp(s1, ofs, size, s2)` trusts offsets. `string_traits<const char*>` calls `strlen()` and cannot handle null pointers. Literal size specialization throws on unterminated arrays.

## Test Signals
Test numeric conversions at boundaries and invalid suffixes, string literals and mutable arrays, char delimiter joins, `string_view` with embedded nulls, and wildcard matching through the exported declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sts.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_sts.cc

## Purpose
`rgw_sts.cc` implements Security Token Service request validation, assumed-role identity construction, encrypted temporary credential generation, role lookup, and GetSessionToken/AssumeRole/AssumeRoleWithWebIdentity flows.

## Important APIs, Types, and Functions
`Credentials::generateCredentials()` generates random access/secret keys, computes expiration, serializes `SessionToken`, encrypts it with AES using `rgw_sts_key`, and base64-encodes it. `AssumedRoleUser::generateAssumedRoleUser()` converts role ARN resources into assumed-role ARNs and role session ids. `AssumeRoleRequestBase::validate_input()` enforces duration, policy, ARN, and session-name constraints. Derived validators add provider id, external id, serial number, and token-code checks. `STSService::getRoleInfo()` parses ARNs and loads roles from SAL. `assumeRole()`, `assumeRoleWithWebIdentity()`, and `getSessionToken()` produce response structs.

## Control Flow
AssumeRole parses and loads the role, applies the role max session duration to the request, validates input, computes packed policy size, builds assumed-role user metadata, then generates credentials with policy and role id embedded in the token. Web identity mode builds token claims from issuer/audience/subject and principal tags, then generates role credentials. GetSessionToken skips role lookup and embeds the current identity fields.

## State and Persistence Behavior
The generated STS token is self-contained encrypted state carrying keys, expiration, policy, role id, user, account attributes, role session, token claims, issued-at time, and principal tags. The service stores a `unique_ptr` to the last loaded role while serving role operations. It does not persist new objects directly.

## Dependencies and Integration Points
The file integrates with RGW role SAL APIs, ARN parsing, IAM policy evaluation through embedded policy text, AES crypto handlers, `rgw_sts_key`, random generation, JSON formatting, Ceph time/ISO8601 helpers, account validation, and auth `Identity`.

## Risks
`MAX_DURATION_IN_SECS` is set through `setMaxDuration()` but is not initialized in the base constructor before validation unless callers set it. The token-code check rejects only non-empty six-character codes, which appears inverted for MFA-style validation. Packed policy size uses integer division before multiplying by 100, losing expected percentages below 100 percent. Web identity assumes `role` is already loaded and does not call `getRoleInfo()` in this file path.

## Test Signals
Cover missing/invalid `rgw_sts_key`, AES secret validation, duration min/max and role max duration, session-name regex, policy-size limits, malformed ARN/path mismatch, role-not-found mapping, web identity claim embedding, principal tags, encrypted token decode compatibility, and GetSessionToken identity propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sts.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sts.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_sts.h

## Purpose
`rgw_sts.h` declares RGW's STS request, response, token, credential, and service types.

## Important APIs, Types, and Functions
`AssumeRoleRequestBase` owns duration, policy, role ARN, role session name, and shared validation limits. `AssumeRoleWithWebIdentityRequest`, `AssumeRoleRequest`, and `GetSessionTokenRequest` represent STS operation inputs. `AssumedRoleUser` exposes assumed-role ARN/id output. `SessionToken` is the encoded authorization payload, versioned through struct version 5. `Credentials` stores access key, secret key, session token, and expiration. `STSService` coordinates role loading and STS operations.

## Control Flow
Construct request objects from REST parameters, call `validate_input()`, then feed validated requests into `STSService`. The service returns simple structs/tuples with negative RGW/Ceph error codes or populated credentials.

## State and Persistence Behavior
`SessionToken` is a persisted wire/storage format inside encrypted session tokens; decoding preserves backward compatibility for role session, token claims, issued-at, and principal tags by checking struct version. Other classes are transient request/response containers.

## Dependencies and Integration Points
The header depends on `rgw_role.h`, `rgw_auth.h`, `rgw_web_idp.h`, Ceph encoding macros, SAL driver/role types, `rgw_user`, and auth identity. It is used by STS REST handlers and auth code that decrypts session tokens.

## Risks
Public getters expose references to mutable internals, so callers must respect object lifetime. Constructor parsing of GetSessionToken uses `stoull()` and can throw, unlike the base request's strict parser. Type aliases repeat struct names, which is harmless but noisy.

## Test Signals
Test binary encode/decode compatibility across `SessionToken` versions, construction from empty and numeric durations, role/session getters, response formatting, and service integration with mocked SAL roles and identities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_swift_auth.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_swift_auth.cc

## Purpose
`rgw_swift_auth.cc` implements Swift authentication engines and the legacy Swift auth endpoint. It supports TempURL HMAC authentication, external Swift auth URL validation, locally signed `AUTH_rgwtk` tokens, and token issuance from `X-Auth-User`/`X-Auth-Key`.

## Important APIs, Types, and Functions
`TempURLApplier` mutates content-disposition and marks log entries as temp-url. `TempURLEngine` loads bucket-owner temp URL keys, converts ISO8601 expirations, rejects expired URLs/disallowed headers, selects HMAC helper by signature form, supports prefixed temp URLs, and grants a temp-url applier on match. `ExternalTokenEngine` validates tokens by querying configured `rgw_swift_auth_url`. `build_token()` and `encode_token()` serialize swift user, nonce, expiration, and HMAC-SHA1. `SignedTokenEngine` decodes, verifies expiration and HMAC, loads the mapped user, and grants a local applier. `RGW_SWIFT_Auth_Get::execute()` issues Swift storage URL and auth tokens.

## Control Flow
The strategy invokes engines in order. TempURL requires query args, loads owner info from URL bucket/account context, checks each configured temp URL key against allowed methods and path variants, and returns grant/reject. Signed token strips `AUTH_rgwtk`, hex-decodes the payload, decodes fields, loads the Swift user, rebuilds the token with the user's Swift key, and compares bytes. External auth calls a remote token endpoint and maps the first returned auth group to a Swift user. The auth endpoint validates the supplied Swift key and emits headers.

## State and Persistence Behavior
No durable state is written except request logs. Issued signed tokens contain user, nonce, expiration, and HMAC in a hex payload. Authentication loads user/account/policy state through SAL and configures request-local appliers.

## Dependencies and Integration Points
The file depends on RGW auth strategy/applier classes, Keystone/external auth, SAL user lookup, account policy loading, RGW HTTP client header collection, HMAC-SHA implementations, base64 helpers, request env/args, and Swift URL config.

## Risks
TempURL path compatibility tries two path variants and special HEAD method fallbacks, so regressions are easy. Signature comparison length logic includes `dest_size + 1`, which relies on generated strings being null terminated. External auth throws on validator errors, so strategy behavior depends on caller exception handling. Legacy signed tokens use HMAC-SHA1. The auth endpoint uses `goto` cleanup and may expose misconfiguration through headers/logs.

## Test Signals
Cover TempURL SHA1/SHA256/SHA512 bare and named-base64 signatures, ISO8601 expires, expired and malformed expires, prefixed temp URLs, HEAD fallbacks, disallowed manifest header, tenant/account URL cases, external token header parsing, signed token tampering/expiration, missing Swift keys, and auth endpoint URL construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_swift_auth.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_swift_auth.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_swift_auth.h

## Purpose
`rgw_swift_auth.h` declares Swift authentication engines, appliers, default strategy wiring, signature helpers, and the Swift auth REST handler.

## Important APIs, Types, and Functions
`TempURLApplier`, `TempURLEngine`, `SignedTokenEngine`, `ExternalTokenEngine`, `SwiftAnonymousApplier`, and `SwiftAnonymousEngine` define authentication units. `DefaultStrategy` constructs and orders TempURL, signed-token, optional Keystone, optional external-token, and anonymous engines while producing local/remote/temp-url appliers. Signature templates define digest size/name metadata, `SignatureHelperT`, and `FormatSignature` for bare hex or `name:base64url` signatures. `RGW_SWIFT_Auth_Get`, `RGWHandler_SWIFT_Auth`, and `RGWRESTMgr_SWIFT_Auth` expose the auth endpoint.

## Control Flow
The default strategy adds engines with `SUFFICIENT` control and conditionally enables Keystone/external auth based on config. Engines receive tokens through extractor structs reading `HTTP_X_AUTH_TOKEN` and `HTTP_X_SERVICE_TOKEN`.

## State and Persistence Behavior
The header declares request-local applier state and engine references to config, SAL driver, token extractors, and factories. It does not define durable storage.

## Dependencies and Integration Points
Includes RGW REST/auth/filter/Keystone/SAL/B64 headers, Ceph crypto types, Formatter, and XML-adjacent request classes. It is central to Swift REST authentication setup.

## Risks
Factories return heap-allocated composed applier wrappers, so ownership must remain consistent with `aplptr_t`. Signature template defaults use `-1` in unsigned constants for unsupported types, which should never instantiate. Anonymous auth is sufficient and must remain last to avoid bypassing real token failures.

## Test Signals
Compile tests should instantiate all supported hash/flavor combinations. Integration tests should verify engine ordering, Keystone/external enablement flags, extractor behavior, factory-created appliers, and Swift auth manager handler selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_swift_auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sync_policy.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_sync_policy.cc

## Purpose
`rgw_sync_policy.cc` implements mutation, expansion, matching, JSON decode/dump, and helper logic for RGW multisite sync policy data structures.

## Important APIs, Types, and Functions
Filter tags parse `key` or `key=value` strings, filters manage optional prefixes and tag sets, and check whether object names/tags pass. Bucket entity helpers apply buckets, add/remove zones, set wildcard bucket fields, expand aggregate zone/bucket sets into concrete pipe endpoints, and compute related buckets. Data-flow helpers find/create/remove symmetrical groups and directional rules. Policy group helpers find/create/remove pipes and walk related buckets. Dump/decode functions serialize the policy model to JSON.

## Control Flow
Admin/config operations mutate `rgw_sync_policy_info` through group/pipe/filter/data-flow helpers. Runtime code expands aggregate pipes into concrete `rgw_sync_bucket_pipe` combinations and uses match helpers to discover whether a bucket may source or receive sync. JSON decode maps lists of groups back into the `groups` map keyed by id.

## State and Persistence Behavior
The file mutates in-memory policy structures that are encoded by the header's Ceph encoding methods for persistence in realm/zonegroup/bucket metadata. Wildcards are represented by empty bucket fields, unset zones, or `all_zones`.

## Dependencies and Integration Points
It depends on `rgw_sync_policy.h`, `rgw_bucket.h`, `rgw_tag.h`, Boost prefix matching, Ceph JSON encoders, and bucket-key parsing. It integrates with multisite sync policy admin commands and data-sync selection logic.

## Risks
`rgw_sync_pipe_filter_tag::operator==(const string&)` appears to compare `s` against itself for the key range, which can make tag-string equality wrong. Tag filters use any-match semantics in `check_tags()`, not all-match semantics. Wildcard representation through empty strings can be subtle when tenant/name/bucket_id are partially set. Decode silently resets invalid bucket strings.

## Test Signals
Cover `key` and `key=value` parsing, prefix subset checks, tag add/remove and object tag matching, wildcard bucket fields, all-zones expansion, directional/symmetrical removal, aggregate pipe expansion, related bucket discovery, JSON round trips, and invalid bucket-key decode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sync_policy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sync_policy.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_sync_policy.h

## Purpose
`rgw_sync_policy.h` defines the serialized data model for RGW multisite sync policies: flows between zones, bucket pipes, source filters, destination transforms, ownership translation, user/system modes, group status, and complete policy info.

## Important APIs, Types, and Functions
Core types include `rgw_sync_symmetric_group`, `rgw_sync_directional_rule`, `rgw_sync_bucket_entity`, `rgw_sync_pipe_filter_tag`, `rgw_sync_pipe_filter`, `rgw_sync_pipe_acl_translation`, source/dest/combined pipe params, concrete `rgw_sync_bucket_pipe`, aggregate `rgw_sync_bucket_entities` and `rgw_sync_bucket_pipes`, `rgw_sync_data_flow_group`, `rgw_sync_policy_group`, and `rgw_sync_policy_info`. Each type has Ceph encode/decode and JSON dump/decode declarations.

## Control Flow
Policies are built as groups. A group can constrain data flow and define pipes from aggregate sources to aggregate destinations. Aggregate entities expand into concrete zone/bucket entities for runtime matching. Filters and destination params refine sync behavior per pipe.

## State and Persistence Behavior
All structs are versioned with Ceph encoding macros and persisted as part of RGW metadata. Optional fields represent absent constraints; empty strings often represent wildcards. `Session`-like runtime state is absent.

## Dependencies and Integration Points
The header depends on `rgw_basic_types.h`, `rgw_tag.h`, Ceph Formatter/JSON/encoding utilities, `rgw_bucket`, `rgw_user`, and `rgw_zone_id`. It is consumed by multisite sync, admin policy manipulation, and metadata persistence code.

## Risks
Because this is a durable encoding contract, field reordering or type changes would break compatibility. Wildcard semantics span `all_zones`, unset optionals, and empty bucket fields. `rgw_sync_policy_group::status` has no default initializer in the declaration, so callers must set it before encoding/dumping.

## Test Signals
Binary encode/decode compatibility, JSON round trips, default-instance generation, group status parsing, pipe specificity, optional user/mode handling, ACL translation equality, and expansion for all wildcard combinations are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_sync_policy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tag.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_tag.cc

## Purpose
`rgw_tag.cc` implements RGW object tag storage and parsing helpers.

## Important APIs, Types, and Functions
`add_tag()` and `emplace_tag()` insert into the multimap. `check_and_add_tag()` enforces count, key length, value length, and non-empty key limits. `set_from_string()` parses URL-encoded `k=v&k2=v2` tag strings. `dump()` emits a `tagset` object. `generate_test_instances()` supplies encode-test fixtures.

## Control Flow
Input strings are split on `&`; each component is split on the first `=`, URL-decoded, validated, and inserted. The function returns immediately on invalid tag input.

## State and Persistence Behavior
Tags are held in an in-memory multimap and encoded by the header. No external persistence is performed here.

## Dependencies and Integration Points
Depends on `rgw_tag.h`, `rgw_common.h` URL decoding, Boost string split, Formatter, and RGW error codes. Used by S3 tagging, sync filters, lifecycle, and metadata paths.

## Risks
The max tag count check runs before insert, so duplicate multimap keys count independently. URL decoding errors are not surfaced separately. Empty values are allowed by core tags but S3 XML layer rejects empty values.

## Test Signals
Cover empty input, URL-encoded keys/values, missing `=`, duplicate keys, max count, maximum key/value lengths, empty keys, and formatter output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tag.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tag.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_tag.h

## Purpose
`rgw_tag.h` declares `RGWObjTags`, the versioned RGW object-tag container.

## Important APIs, Types, and Functions
`RGWObjTags` stores tags as `std::multimap<std::string,std::string>`, exposes add/validate/parse/clear/count/access methods, and provides Ceph encode/decode, Formatter dump, and test instances. The decode path first tries binary Ceph format, then falls back to legacy URL-encoded plain text.

## Control Flow
Decoding saves the starting iterator, attempts `DECODE_START_LEGACY_COMPAT_LEN`, and on `buffer::error` restores the iterator, copies remaining bytes, strips trailing nulls, and calls `set_from_string()`.

## State and Persistence Behavior
This is a durable object metadata format. Struct version 1 encodes the tag multimap. Legacy plain-string fallback preserves older object tag values.

## Dependencies and Integration Points
The header depends on Ceph encoding and Formatter forward declarations. It is used by S3 tagging, sync policy tag filters, and object metadata encoding.

## Risks
Fallback decoding can reinterpret arbitrary invalid binary bytes as a tag string if they parse. Multimap semantics allow duplicate keys. Limits are instance-level for tag count but compile-time for key/value lengths.

## Test Signals
Binary and legacy string decode tests, trailing null stripping, invalid fallback rethrow behavior, duplicate tag encode/decode, and custom max tag count coverage are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tag_s3.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_tag_s3.cc

## Purpose
`rgw_tag_s3.cc` adapts core `RGWObjTags` to S3 XML Tagging request/response formats.

## Important APIs, Types, and Functions
`RGWObjTagEntry_S3::decode_xml()` reads mandatory `Key` and `Value`. `dump_xml()` emits them and rejects empty values. `RGWObjTagSet_S3::decode_xml()` reads all `Tag` entries and inserts them. `rebuild()` validates and copies parsed tags into a destination `RGWObjTags`. `RGWObjTagging_S3::decode_xml()` reads mandatory `TagSet`.

## Control Flow
XML decode builds an S3 tag set first, then `rebuild()` applies core RGW tag validation. XML dump iterates the stored tag map and emits one `Tag` object per entry.

## State and Persistence Behavior
No external state is persisted here. Parsed XML is converted into the durable `RGWObjTags` representation by callers.

## Dependencies and Integration Points
Depends on RGW XML decoder/encoder helpers, Formatter, and `rgw_tag.h`. Used by S3 PutObjectTagging/GetObjectTagging and related operations.

## Risks
Decode inserts tags without validation until `rebuild()` is called, so callers must not skip rebuild. Dump rejects empty value even though core RGW tags allow it. Duplicate keys follow multimap behavior.

## Test Signals
Cover mandatory field failures, empty key/value dump rejection, too many tags via rebuild, duplicate tags, XML round trip, and TagSet omission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tag_s3.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tag_s3.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_tag_s3.h

## Purpose
`rgw_tag_s3.h` declares S3 XML wrappers for object tagging.

## Important APIs, Types, and Functions
`RGWObjTagEntry_S3` stores one key/value pair with XML decode/dump. `RGWObjTagSet_S3` derives from `RGWObjTags` and can dump/decode XML and rebuild a validated core tag set. `RGWObjTagging_S3` owns a tag set and exposes top-level XML decode plus rebuild.

## Control Flow
S3 operation handlers parse XML into `RGWObjTagging_S3`, call `rebuild()` to produce `RGWObjTags`, then persist those tags through normal object metadata paths.

## State and Persistence Behavior
These classes are transient XML request/response models. Persistence is delegated to `RGWObjTags`.

## Dependencies and Integration Points
Includes Formatter, expat, RGW XML helpers, and core tags. It is part of S3 REST tagging support.

## Risks
Inheritance exposes core tag mutation methods on the S3 set. The header does not itself enforce S3 tag limits until implementation rebuild.

## Test Signals
Compile coverage for XML decoder overloads, rebuild validation, and S3 operation integration with malformed XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tag_s3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tar.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_tar.h

## Purpose
`rgw_tar.h` provides a lightweight TAR block interpreter for RGW code that reads tar streams.

## Important APIs, Types, and Functions
`BLOCK_SIZE` is 512. `StatusIndicator` tracks whether the current block is empty and whether two consecutive empty blocks mark EOF. `FileType` distinguishes unknown, normal file, and directory. `HeaderView` overlays a 512-byte tar header and exposes file type, filename, and octal file size. `interpret_block()` returns updated status and an optional header view.

## Control Flow
Callers initialize `StatusIndicator::create()`, feed 512-byte bufferlists to `interpret_block()`, and stop when `status.eof()` becomes true. Nonzero blocks produce a `HeaderView`; zero blocks produce no header and update EOF state.

## State and Persistence Behavior
No persistence. `HeaderView` references the caller's buffer memory, so it is only valid while that buffer lives.

## Dependencies and Integration Points
Uses Ceph bufferlist, Boost optional, reversed range adaptor, and standard string utilities. It can support bulk import/export or archive parsing code.

## Risks
`interpret_block()` assumes `bl.c_str()` references at least 512 bytes. Octal parsing does not validate that all characters are octal digits. `HeaderView` uses `strlen()` on fixed-width filename data, which relies on null termination within the field.

## Test Signals
Cover normal file, directory, unknown type, exact zero-block EOF sequence, padded octal sizes, malformed size bytes, non-null-terminated filenames, and undersized input defense at caller level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_token.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_token.cc

## Purpose
`rgw_token.cc` implements the `radosgw-token` utility for producing base64-encoded JSON tokens from access/secret credentials.

## Important APIs, Types, and Functions
`usage()` prints CLI help. `main()` parses Ceph global args, reads `RGW_ACCESS_KEY_ID` and `RGW_SECRET_ACCESS_KEY`, accepts `--access`, `--secret`, `--ttype`, `--encode`, `--decode`, and `--verbose`, builds an `RGWToken`, dumps JSON through `JSONFormatter`, and prints base64.

## Control Flow
The program initializes Ceph context, parses options, requires `--encode` and a supported type, creates the token, optionally prints expanded/decoded forms in verbose mode, then prints base64 JSON to stdout.

## State and Persistence Behavior
No persistent state. Secrets are held in process globals and output to stdout by design.

## Dependencies and Integration Points
Depends on Ceph argparse/global init, Formatter, `rgw_token.h`, and base64 helpers. Used by administrators or scripts generating auth tokens for AD/LDAP style integrations.

## Risks
The `--decode` flag only has effect under verbose encode mode; standalone decode is not implemented. The token formatter is allocated with `new` and never deleted, acceptable for process exit but noisy. Secrets may be printed in verbose output.

## Test Signals
Cover environment fallback, option overrides, invalid/missing token type, encode output base64 validity, verbose decode output, and help path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_token.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_token.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_token.h

## Purpose
`rgw_token.h` defines `rgw::RGWToken`, a small credential token model with binary encoding, JSON encoding/decoding, and base64 JSON output.

## Important APIs, Types, and Functions
`token_type` supports none, AD, Keystone, and LDAP. `to_type()`/`from_type()` convert names. `valid()` checks type/id/key presence. Constructors build empty, explicit, or JSON-decoded tokens. `encode()`/`decode()` implement Ceph binary format. `dump()`, `encode_json()`, `decode_json()`, and `encode_json_base64()` provide Formatter/JSON support. `operator<<` prints token fields.

## Control Flow
JSON construction parses a top-level object, decodes nested `RGW_TOKEN`, and fills type/id/key. Binary encoding stores a name marker, version, type string, id, and key.

## State and Persistence Behavior
The token stores secret material in clear text in memory and encoded JSON/binary. It is a durable/interchange format for integration tokens.

## Dependencies and Integration Points
Depends on Ceph JSON/Formatter, encoding macros, Boost case-insensitive comparison, and RGW base64 helpers. Used by `radosgw-token` and external auth integrations.

## Risks
No version validation is performed on JSON decode. `operator<<` prints the secret key. JSON parse errors are not checked before decode. `encode_json()` opens an outer `RGW_TOKEN` section and then encodes another `RGW_TOKEN`, so consumers must expect that nested shape.

## Test Signals
Cover JSON and binary round trips, type conversions, invalid JSON, empty fields, base64 output, and redaction expectations for logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_token.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tools.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_tools.cc

## Purpose
`rgw_tools.cc` initializes and queries a MIME type map used by RGW based on extension-to-MIME mappings from a configured file.

## Important APIs, Types, and Functions
`parse_mime_map_line()` skips leading whitespace, splits a line on whitespace, treats the first token as MIME type, and maps each remaining extension to it. `parse_mime_map()` iterates lines. `ext_mime_map_init()` reads the configured file safely and fills the map. `rgw_find_mime_by_ext()` looks up an extension. `rgw_tools_init()` allocates and populates the global map. `rgw_tools_cleanup()` releases it.

## Control Flow
Initialization allocates a transparent-comparator map, attempts to read `rgw_mime_types_file`, ignores initialization errors, and leaves lookups available. File-size races cause a recursive retry.

## State and Persistence Behavior
The only state is the process-global `ext_mime_map`; no persistent writes occur.

## Dependencies and Integration Points
Depends on Ceph safe I/O, config, split utility, error logging, and `driver/rados/rgw_tools.h`. RGW object serving code uses the MIME lookup when deriving content types.

## Risks
`rgw_find_mime_by_ext()` assumes `rgw_tools_init()` has run. Recursive retry on file-size race could loop if the file changes constantly. Parse logic does not skip comment lines explicitly unless split behavior or file format makes them harmless.

## Test Signals
Cover missing mime file, comments/blank lines, multiple extensions per MIME type, lookup before/after cleanup, file-size race handling, and transparent `string_view` lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tools.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_torrent.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_torrent.cc

## Purpose
`rgw_torrent.cc` builds and reads bencoded torrent metadata for RGW object torrent support.

## Important APIs, Types, and Functions
`bencode_dict()`, `bencode_list()`, `bencode_end()`, `bencode_key()`, and overloads of `bencode()` write bencoded primitives and dictionary entries. `rgw_read_torrent_file()` loads stored object torrent info and adds configured tracker/comment/created-by/encoding fields. `RGWPutObj_Torrent::process()` computes SHA1 piece hashes while streaming upload data. `bencode_torrent()` produces the stored info dictionary for eligible objects.

## Control Flow
On upload, the torrent pipe forwards all data downstream while updating piece digest state. A final zero-length process call flushes the last partial piece. If object length reaches the configured max, hash state is cleared and no torrent metadata is produced. On read, stored info is appended after top-level configured fields.

## State and Persistence Behavior
The pipe stores upload-local length, piece length, current piece offset, piece count, SHA1 state, and concatenated piece hashes. The object's torrent info is persisted by callers using the buffer returned from `bencode_torrent()`.

## Dependencies and Integration Points
Depends on Ceph SHA1, bufferlist, config fields (`rgw_torrent_tracker`, etc.), SAL object `get_torrent_info()`, and put-object filter pipeline.

## Risks
Integer bencode overloads accept `int`, while object lengths are `size_t`; large values may truncate through overload selection. Torrent generation stops at `len >= max_len`, excluding objects exactly at the limit. Bencode correctness depends on stored info already containing a valid `info` key sequence.

## Test Signals
Cover small object, exact piece boundary, partial final piece, max length boundary, multiple trackers, empty optional config fields, bencode syntax, and read failure from `get_torrent_info()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_torrent.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_torrent.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_torrent.h

## Purpose
`rgw_torrent.h` declares bencode helpers, torrent read support, and the put-object pipeline filter that computes torrent metadata.

## Important APIs, Types, and Functions
Free functions write bencode control characters, keys, values, and dictionary entries. `rgw_read_torrent_file()` reads a complete torrent file for an object. `RGWPutObj_Torrent` derives from `rgw::putobj::Pipe`, overrides `process()`, and exposes `bencode_torrent(filename)`.

## Control Flow
Callers insert `RGWPutObj_Torrent` into the upload data processor chain, stream object data through it, then request the final bencoded torrent metadata after completion.

## State and Persistence Behavior
The class holds only upload-local hash state and does not persist on its own.

## Dependencies and Integration Points
Depends on `rgw_putobj.h`, SAL forward declarations, Ceph SHA1, async yield context, and Dout logging. It integrates with object upload and GetObjectTorrent paths.

## Risks
The class assumes a final zero-length flush call to capture partial-piece hashes. If callers skip it, torrent metadata will miss the last piece.

## Test Signals
Pipeline tests should confirm downstream forwarding, final flush behavior, disabled output above max length, and correct piece hash count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_torrent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tracer.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_tracer.cc

## Purpose
`rgw_tracer.cc` defines the global RGW tracing object declared in the header.

## Important APIs, Types, and Functions
It instantiates `tracing::rgw::tracer`.

## Control Flow
There is no runtime control flow beyond static/global initialization.

## State and Persistence Behavior
The global tracer is process state used by tracing instrumentation; no direct persistence occurs.

## Dependencies and Integration Points
Depends on `rgw_tracer.h` and Ceph tracing infrastructure. RGW request paths import the global tracer to create spans.

## Risks
Global initialization order can matter if tracing code uses the object before normal startup. The file is intentionally minimal.

## Test Signals
Link tests should ensure exactly one tracer definition exists and tracing-enabled builds resolve it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tracer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tracer.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_tracer.h

## Purpose
`rgw_tracer.h` declares RGW tracing tag constants, the global tracer, and a helper to recover span context from object attributes.

## Important APIs, Types, and Functions
Constants name common span attributes such as bucket, user, object, operation result, upload id, transaction id, and host id. `extern tracing::Tracer tracer` is the RGW tracer handle. `extract_span_context()` looks for `RGW_ATTR_TRACE` in an attrs map and decodes a `jspan_context`.

## Control Flow
Callers pass object attrs into `extract_span_context()`, which silently ignores missing or malformed trace attrs.

## State and Persistence Behavior
Trace context can be persisted as `RGW_ATTR_TRACE` in object metadata. The helper only decodes it into request-local state.

## Dependencies and Integration Points
Depends on Ceph `common/tracer.h`, RGW attrs, and tracing decode support. Used by object operations that continue distributed traces across stored metadata.

## Risks
Decode failures are swallowed, which keeps request paths robust but hides corrupt trace attrs. Constants are untyped string pointers.

## Test Signals
Cover valid trace attr decode, missing attr, corrupt bufferlist, and span tags appearing in traced RGW operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_tracer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_url.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_url.cc

## Purpose
`rgw_url.cc` implements URL authority/userinfo parsing helpers.

## Important APIs, Types, and Functions
`rgw::parse_url_authority()` parses a URI and extracts host, optional port, user, and password. `rgw::parse_url_userinfo()` extracts only user and password.

## Control Flow
Both functions call `boost::urls::parse_uri()`, return false on parse failure, and otherwise copy fields out of the URL view. Authority parsing formats `host:port` when a port is present.

## State and Persistence Behavior
The file is stateless and has no persistence.

## Dependencies and Integration Points
Depends on Boost.URL and fmt. Used by notification, cloud, or external service configuration that embeds credentials in URLs.

## Risks
No scheme allowlist is enforced here despite header comments listing expected schemes. Percent-decoding behavior is whatever Boost.URL exposes for `user()`/`password()`. IPv6 host plus port formatting must be verified against Boost output.

## Test Signals
Cover no port, port, userinfo, password-only/empty password, invalid URI, IPv6 literals, percent-encoded credentials, and unsupported schemes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_url.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_url.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_url.h

## Purpose
`rgw_url.h` declares RGW URL parsing helpers for authority and userinfo extraction.

## Important APIs, Types, and Functions
`parse_url_authority(url, host, user, password)` and `parse_url_userinfo(url, user, password)` return bool success and write extracted strings.

## Control Flow
Callers pass mutable string references and check the boolean return before using outputs.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Only includes `<string>`. Implementation uses Boost.URL. The helpers are suitable for config parsing without exposing Boost types to callers.

## Risks
The comment documents accepted schemes but enforcement is in callers, not this helper.

## Test Signals
Header-level tests should verify callers include it without Boost.URL headers and link against the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_url.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_usage.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_usage.cc

## Purpose
`rgw_usage.cc` implements display, trim, and clear operations for RGW usage logs.

## Important APIs, Types, and Functions
`dump_usage_categories_info()` emits per-category bytes/ops counters with optional filtering. `RGWUsage::show()` pages usage entries from a bucket, user, or all-driver scope, formats detailed entries and/or summaries, and flushes output incrementally. `trim()` delegates usage deletion by scope. `clear()` clears all usage through the driver.

## Control Flow
`show()` opens a top-level `usage` object, loops while backend results are truncated, reads up to 1000 entries at a time, optionally emits entries grouped by user, aggregates per-user summaries, handles `-ENOENT` as empty, then emits summary totals if requested.

## State and Persistence Behavior
Usage data is read and trimmed through SAL bucket/user/driver interfaces. Local `summary_map` aggregates transient display totals. `trim()` and `clear()` mutate persisted usage logs.

## Dependencies and Integration Points
Depends on SAL Driver/User/Bucket usage APIs, `rgw_usage_log_entry`, `rgw_user_bucket`, Formatter flusher, and RGW formats. Used by admin commands and usage APIs.

## Risks
`usage` map is not cleared inside the pagination loop, so stale entries could be reprocessed if backend appends rather than replaces. Category filtering affects totals and category display. The function assumes map ordering groups users for entry output.

## Test Signals
Cover all three scopes, pagination, `-ENOENT`, entries-only, summary-only, category filters, s3select counters, trim/clear delegation, and large result flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_usage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_usage.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_usage.h

## Purpose
`rgw_usage.h` declares static helpers for RGW usage-log reporting and maintenance.

## Important APIs, Types, and Functions
`RGWUsage::show()` formats usage logs over a time range with optional entries, summaries, and category filtering. `trim()` removes usage records for a scope. `clear()` removes all usage records through the driver.

## Control Flow
The API is stateless; callers choose driver/user/bucket pointers to define scope and pass a formatter flusher for output.

## State and Persistence Behavior
The class itself has no fields. Persistence is owned by the SAL backend invoked by the implementation.

## Dependencies and Integration Points
Depends on Formatter, Dout, RGW formats, RADOS user types, SAL forwards, and optional yield context. Used by `radosgw-admin usage` style operations.

## Risks
Null/non-null pointer combinations define behavior and must be passed consistently. Static API makes mocking require mock SAL objects.

## Test Signals
Compile and integration tests should validate scope precedence: bucket over user over driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_usage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_user.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_user.cc

## Purpose
`rgw_user.cc` implements user helper functions for bucket-stat synchronization, bucket usage collection, tenant validation, anonymous user setup, and access/secret key generation.

## Important APIs, Types, and Functions
`rgw_sync_all_stats()` lists all buckets for an owner/tenant, loads each bucket, syncs owner stats, checks bucket shards, and completes stat flushing. `rgw_user_get_all_buckets_stats()` builds a bucket metadata usage map from listed buckets. `rgw_validate_tenant_name()` allows only alnum and underscore. `rgw_get_anon_user()` populates anonymous user info. `rgw_generate_access_key()` generates unique public access key ids and checks duplicates through SAL. `rgw_generate_secret_key()` generates a random secret.

## Control Flow
Bucket listing loops on `listing.next_marker` with chunk size from config. Access-key generation loops until a generated key is not found by `get_user_by_access_key()`, returning only `-ENOENT` as success.

## State and Persistence Behavior
The stat sync function mutates persisted bucket/owner stats via SAL bucket and driver methods. Key generation only returns strings; persistence of keys is handled by callers.

## Dependencies and Integration Points
Depends on RADOS SAL headers, bucket/user types, random generation, RGW error constants, and `rgw_list_buckets_max_chunk`. Used by admin/user management paths.

## Risks
Access-key generation can loop indefinitely under pathological duplicate/random failures. `rgw_sync_all_stats()` logs shard-check errors but does not fail on them. Tenant validation depends on C locale `isalnum()` behavior for signed chars.

## Test Signals
Cover paginated bucket listing, load failures, stat sync failure, flush failure, bucket usage map population, invalid tenant characters, anonymous user clearing, duplicate access key retry, and secret key length/charset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_user.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_user_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_user_types.h

## Purpose
`rgw_user_types.h` defines fundamental serialized RGW owner identity types without depending on full RGW runtime headers.

## Important APIs, Types, and Functions
`rgw_account_id` is a strong typedef over `std::string`. `rgw_user` stores tenant, namespace, and id; supports versioned encode/decode, string conversion/parsing using `$` separators, clear/empty checks, default comparison, Formatter dump, and test instances. `rgw_owner` is a variant of `rgw_user` or `rgw_account_id`. Free functions parse, stringify, stream, and JSON encode/decode owners.

## Control Flow
`rgw_user::to_str()` emits `tenant$id`, `tenant$ns$id`, `$ns$id`, or plain id depending on populated fields. `from_str()` reverses that split.

## State and Persistence Behavior
This is a durable encoding contract. `rgw_user` struct version 2 adds namespace while preserving version 1 decode. `rgw_owner` variant ordering is part of binary compatibility.

## Dependencies and Integration Points
Depends on Formatter, JSON, fmt, strings, variants, and Ceph buffer encoding. Included broadly by RGW user, bucket, account, ACL, and policy code.

## Risks
`rgw_account_id` inherits from `std::string`, which can surprise overload resolution. `$` separator parsing cannot represent ids containing `$` unambiguously. The file warns that variant alternatives cannot be changed or removed.

## Test Signals
Binary compatibility for version 1 and 2 users, string round trips with tenant/ns/id combinations, owner variant JSON round trips, ordering comparisons, and account-id formatting are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_user_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_web_idp.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_web_idp.h

## Purpose
`rgw_web_idp.h` declares a small claim container for web identity provider tokens.

## Important APIs, Types, and Functions
`rgw::web_idp::WebTokenClaims` stores subject, audience, issuer, username, client id, and authorized party (`azp`).

## Control Flow
No functions are defined; callers populate the struct after decoding a web identity token and pass claims to STS/auth logic.

## State and Persistence Behavior
The struct is transient request state and has no encoding or persistence behavior in this file.

## Dependencies and Integration Points
Used by STS AssumeRoleWithWebIdentity and web identity token validation code. It intentionally has minimal dependencies.

## Risks
No validation is encoded in the type, so callers must validate required claims, audience matching, and issuer trust externally.

## Test Signals
Integration tests should verify decoded claims are correctly propagated into STS session token claims and trust-policy evaluation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_web_idp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_website.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_website.cc

## Purpose
`rgw_website.cc` implements S3 bucket website configuration behavior: redirect rule matching/application, effective index-document key selection, JSON/XML dump/decode, and validation of website redirect/error rules.

## Important APIs, Types, and Functions
`RGWBWRoutingRuleCondition::check_key_condition()` matches prefixes. `RGWBWRoutingRule::apply_rule()` constructs redirect URLs from default or rule protocol/host and replacement key settings. `RGWBWRoutingRules` checks rules by key, error code, or both. `RGWBucketWebsiteConf::should_redirect()` handles redirect-all or routing rules. `get_effective_key()` maps empty, directory, pseudo-directory, and file keys to index documents. Dump/decode functions cover JSON and S3 XML shapes.

## Control Flow
Website request handling asks for effective keys when serving website endpoints and calls `should_redirect()` on errors or redirect-all configs. XML decode gives `RedirectAllRequestsTo` precedence; otherwise it decodes index, error, and routing rules.

## State and Persistence Behavior
The file mutates in-memory website config structs that are encoded by the header into bucket metadata. It does not directly perform I/O.

## Dependencies and Integration Points
Depends on RGW XML/JSON helpers, Formatter, and website config structs. Used by bucket website PUT/GET and website request routing.

## Risks
`should_redirect()` sets `redirect_all.http_redirect_code = 301` on the configuration object instead of only the local rule, creating side effects in a predicate-like method. Redirect code validation allows 301-399 for redirects and 400-599 for error conditions. `apply_rule()` does not escape generated key segments.

## Test Signals
Cover redirect-all, key+error matching, key-only mismatch, replacement prefix/key mutual exclusion, redirect code validation, index suffix for root/directory/file, XML round trips, JSON round trips, and side-effect-free redirect checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_website.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_website.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_website.h

## Purpose
`rgw_website.h` declares the serialized bucket website configuration model and routing helpers.

## Important APIs, Types, and Functions
`RGWRedirectInfo` stores protocol, host, and redirect code. `RGWBWRedirectInfo` adds key replacement controls. `RGWBWRoutingRuleCondition` stores key prefix and HTTP error condition. `RGWBWRoutingRule` combines condition and redirect. `RGWBWRoutingRules` stores ordered rules. `RGWBucketWebsiteConf` stores redirect-all, index suffix, error document, listing metadata, flags, and routing rules.

## Control Flow
Callers decode config from XML/JSON, persist it in bucket metadata through Ceph encoding, and later evaluate redirect/effective-key helpers during website requests.

## State and Persistence Behavior
All structs use Ceph encode/decode. `RGWBucketWebsiteConf` struct version 2 adds subdir marker, listing CSS doc, and listing enabled while preserving older decode. Boolean flags such as `is_redirect_all` and `is_set_index_doc` are decode/request-state hints rather than encoded fields.

## Dependencies and Integration Points
Depends on Ceph JSON, RGW XML, Formatter, bufferlist encoding, and bucket website REST handlers.

## Risks
Ordering of `std::list<RGWBWRoutingRule>` matters for first-match semantics. `is_empty()` ignores redirect-all and routing rules, so callers must understand what emptiness means. Listing fields are encoded but not dumped to XML in this implementation.

## Test Signals
Binary version compatibility, XML decode flags, routing rule order, redirect-all encoding, listing-field decode, and effective-key behavior should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_website.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_worker.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_worker.h

## Purpose
`rgw_worker.h` declares a base class for periodic RGW RADOS background threads.

## Important APIs, Types, and Functions
`RGWRadosThread` owns nested `Worker`, a `Thread` and `DoutPrefixProvider` that waits on a condition variable and calls the parent processor. The parent exposes virtual `interval_msec()`, `process()`, optional `init()` and `stop_process()`, lifecycle methods `start()`/`stop()`, `signal()`, and down-flag controls.

## Control Flow
Derived classes implement `process()` and interval selection. The worker thread sleeps or waits, wakes on signal or interval, and stops when `down_flag` is set.

## State and Persistence Behavior
The base stores process-local thread state: worker pointer, Ceph context, RADOS store, atomic down flag, and thread name. Persistence is the responsibility of derived `process()` implementations.

## Dependencies and Integration Points
Depends on Ceph `Thread`, mutex/condition variable wrappers, RGWRados forward declaration, and DoutPrefixProvider. Used by RGW services that need periodic RADOS-side maintenance.

## Risks
Implementation is out of line elsewhere, so derived classes rely on undocumented exact entry-loop semantics. `worker` is a raw pointer, making start/stop ownership important. `stop()` is called from the destructor and must be safe for partially initialized instances.

## Test Signals
Derived-thread tests should cover start/stop idempotence, signal wakeups, interval wakeups, process error handling, down flag visibility, and destructor stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_worker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_xml.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_xml.cc

## Purpose
`rgw_xml.cc` implements RGW's lightweight Expat-backed XML tree, decoder primitives, and XML encoder overloads.

## Important APIs, Types, and Functions
`XMLObjIter` iterates child maps. `XMLObj` stores tag type, text data, children, attributes, and callbacks for parser events. `RGWXMLParser` owns an Expat parser, buffers input, creates allocated or lazy XML objects, and exposes `init()`/`parse()`. `decode_xml_obj()` overloads parse numeric types, bool, base64 bufferlist, `utime_t`, and `real_time`. `encode_xml()` overloads dump strings, bool, integers, times, and base64 bufferlists.

## Control Flow
`RGWXMLParser::init()` registers static callbacks. `parse()` appends incoming bytes to its saved buffer and calls Expat. Start callbacks allocate an object, link it to the current object, and push it on a stack vector. End callbacks invoke `xml_end()` and restore the parent. Character callbacks append data to the current object. Higher-level decode templates in the header traverse this tree.

## State and Persistence Behavior
The XML tree and parse buffer are in-memory request state. No durable persistence occurs here, but many RGW metadata XML APIs rely on these conversions before persisting decoded structs.

## Dependencies and Integration Points
Depends on Expat, Ceph bufferlist, Formatter, `utime_t`, and RGW XML declarations. Used broadly by S3/Swift XML REST APIs such as tagging, website config, ACLs, lifecycle, and notifications.

## Risks
`call_xml_handle_data()` assumes `cur_obj` is non-null. `parse()` retains a full copy of all parsed input, which can be expensive for large XML bodies. Parse errors are printed to stderr. Numeric decoders accept trailing whitespace but reject other suffixes. `strncasecmp(..., 8)` treats strings beginning with `true` or `false` as booleans even with suffixes inside 8-byte comparison behavior.

## Test Signals
Cover incremental parse, attributes, repeated child tags, mandatory and optional decode, numeric range errors, bool parsing, base64 decode failure, time parsing, custom `alloc_obj()` ownership, parse failure, and encoder output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_xml.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_xml.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_xml.h

## Purpose
`rgw_xml.h` declares RGW's XML object tree, parser, generic decode templates, and XML encoder overloads.

## Important APIs, Types, and Functions
`XMLObjIter`, `XMLObj`, and `RGWXMLParser` form the parse tree API. `RGWXMLDecoder::err` is the exception type for decode failures. Template `decode_xml()` overloads decode one object, vectors, callback-driven containers, and defaulted values. Free `decode_xml_obj()` overloads supply type-specific conversion. Template `encode_xml()` and `do_encode_xml()` emit object, namespace, vector/list, and optional XML structures.

## Control Flow
Callers parse XML into an `RGWXMLParser`, then call `RGWXMLDecoder::decode_xml()` on named children. Missing mandatory fields throw. Decode errors are wrapped with the field name. Encoder helpers open Formatter sections and call `dump_xml()` on complex values.

## State and Persistence Behavior
The header defines transient parsing and formatting contracts, not persistent storage. It is used to translate request XML into persisted RGW structs.

## Dependencies and Integration Points
Depends on Ceph buffer forwards, Formatter, Ceph time, XML Expat forward declarations, and STL containers. Integrated into many RGW REST resource parsers.

## Risks
Template decode resets missing optional values to default-constructed `T`, which can erase prior caller state. `XMLObjIter` typedefs const and non-const iterators to the same mutable iterator type. Complex type support relies on ADL/free `decode_xml_obj()` overloads.

## Test Signals
Cover template behavior for scalar, vector, list callback, optional, defaulted decode, mandatory missing fields, error wrapping, and encoder section nesting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_xml_enc.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_xml_enc.cc

## Purpose
`rgw_xml_enc.cc` is a placeholder/translation unit for XML encoding support.

## Important APIs, Types, and Functions
The file includes `rgw_common.h`, `rgw_xml.h`, and Formatter, defines RGW dout subsystem, and has no functions or classes of its own.

## Control Flow
No runtime control flow is present.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
It may exist to preserve build targets or historical linkage for XML encoding code now implemented inline/in `rgw_xml.cc`.

## Risks
Because it is empty, stale build references could hide dead-code assumptions. Removing it would require checking build files and downstream link expectations.

## Test Signals
Build-system tests should verify the translation unit remains included or can be removed safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_xml_enc.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_xxh_digest.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_xxh_digest.h

## Purpose
`rgw_xxh_digest.h` wraps xxHash XXH3 64-bit streaming digest behind RGW's digest interface style.

## Important APIs, Types, and Functions
`rgw::digest::XXH3` stores `XXH3_state_t`, exposes `digest_size = 8`, initializes and restarts state, updates with bytes, and writes the final digest in big-endian order using RGW byte-swap helpers when native endian is not big.

## Control Flow
Constructors initialize/reset state. Callers call `Update()` zero or more times, then `Final()` to digest the current stream.

## State and Persistence Behavior
State is in-memory hash state only. The final digest byte order is stable for wire/storage uses.

## Dependencies and Integration Points
Depends on `rgw_crc_digest.h`, `xxhash.h` with `XXH_INLINE_ALL`, `<bit>` endian support, and C memory APIs. Used by RGW checksum/digest code when XXH3 is selected.

## Risks
`XXH_INLINE_ALL` in a header can increase compile time and risks ODR surprises if xxhash configuration differs elsewhere. `Final()` does not restart state after digesting. Callers must provide at least 8 bytes of output buffer.

## Test Signals
Compare against known XXH3-64 vectors, incremental vs one-shot updates, empty input, endian-stable byte output, restart reuse, and buffer-size assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_xxh_digest.h -->
