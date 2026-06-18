# Research: subset-b-008332

Grouped research report for fscrypt security, integrity, filesystem metadata, keyring, PAM, and metadata sources. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/key.go -->
# sources/security-integrity/fscrypt/crypto/key.go

## Purpose
`key.go` defines the `crypto.Key` abstraction used throughout fscrypt to hold sensitive key and passphrase material. It allocates key buffers with `mmap`, optionally asks the kernel to keep pages locked, wipes buffers before freeing them, and provides helpers for reading keys from Go or C inputs. It also encodes and decodes human-transcribable recovery codes for policy keys.

## Important APIs, Types, and Functions
`UseMlock` controls whether allocations use `MAP_LOCKED`. `Key` wraps a private `[]byte` buffer. `NewBlankKey`, `NewKeyFromReader`, `NewFixedLengthKeyFromReader`, and `NewKeyFromCString` are construction paths. `Wipe`, `Len`, `Equals`, `Data`, `UnsafePtr`, `UnsafeToCString`, and `Clone` expose lifecycle or interop operations. `WriteRecoveryCode` and `ReadRecoveryCode` convert `metadata.PolicyKeyLen` keys to and from base32 blocks separated by dashes.

## Control Flow
`NewBlankKey` validates size, maps anonymous private memory, translates `EAGAIN` into the package-level mlock-limit error, and installs a finalizer that calls `Wipe`. `NewKeyFromReader` starts with one page, reads until EOF, doubles capacity when full, then shrinks to the actual read length. Recovery-code writing validates key length, encodes into a temporary locked key, and writes fixed-size base32 blocks. Reading performs the inverse sequence, validating separators before base32 decoding.

## State and Persistence
State is in process memory only. Sensitive buffers are zeroed before `munmap`; recovery encoding uses temporary `Key` buffers that are wiped on return. The only external persistence is whatever caller-supplied `io.Writer` receives for recovery codes.

## Dependencies and Integration Points
This file depends on `golang.org/x/sys/unix` for memory mapping, `crypto/subtle` for constant-time equality, cgo for C string interop, `metadata` constants for key lengths, and `util` helpers for pointer conversion, min, length checks, and error-aware readers/writers. Key objects feed key wrapping, metadata protectors, kernel keyring payloads, and PAM secret handling.

## Risks
`Key` is explicitly not thread-safe; concurrent use and wipe can race or double-free. `Data`, `UnsafePtr`, and `UnsafeToCString` bypass some safety guarantees, especially because the C copy is not locked or automatically wiped. A caller that relies only on the finalizer keeps secrets resident longer than needed. Recovery codes are equivalent to raw policy keys and must be treated as high-value secrets.

## Test Signals
`recovery_test.go` exercises recovery-code determinism, encode/decode round trips, invalid lengths, bad characters, bad separators, and benchmarks. Broader `crypto` tests outside this subset cover key allocation, wiping, resizing, random generation, wrapping, descriptor derivation, and passphrase hashing.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/rand.go -->
# sources/security-integrity/fscrypt/crypto/rand.go

## Purpose
`rand.go` centralizes secure random generation for fscrypt keys and generated passphrases using Linux `getrandom(2)` in nonblocking mode. It intentionally avoids returning bytes before the kernel entropy pool is initialized.

## Important APIs, Types, and Functions
`NewRandomBuffer(length)` returns a random byte slice. `NewRandomKey(length)` returns a locked `*Key` filled from the same source. `NewRandomPassphrase(length)` produces lowercase alphabetic random passphrases. `randReader` implements `io.Reader` over `unix.Getrandom`.

## Control Flow
`NewRandomBuffer` calls `io.ReadFull(randReader{}, buffer)`. `NewRandomKey` delegates to `NewFixedLengthKeyFromReader`. `NewRandomPassphrase` allocates a protected key, repeatedly obtains twice as many raw bytes as remaining characters, rejects values in the modulo-bias tail, maps accepted values to `a` through `z`, and wipes each temporary raw key.

## State and Persistence
No state persists beyond returned buffers or keys. Temporary raw random keys used during passphrase creation are wiped. The functions depend on kernel RNG state and return errors instead of blocking when entropy is unavailable.

## Dependencies and Integration Points
Depends on `golang.org/x/sys/unix` for `Getrandom`, `io.ReadFull`, and the package's `Key` allocation path. It supplies random policy/internal keys and recovery test fixtures to crypto, filesystem metadata, and keyring tests.

## Risks
`GRND_NONBLOCK` means startup on low-entropy systems can fail and callers must handle that. `NewRandomBuffer` returns ordinary heap bytes rather than locked memory, so it is less appropriate for long-lived secrets. `NewRandomPassphrase` only uses lowercase letters; it is random but intentionally constrained.

## Test Signals
Crypto tests outside this specific file check that generated keys exist, large key generation works, and random buffers are not trivially compressible or equal. Recovery tests rely on `NewRandomKey` for round-trip test inputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/rand.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/recovery_test.go -->
# sources/security-integrity/fscrypt/crypto/recovery_test.go

## Purpose
This test file validates recovery-code encoding and decoding for fscrypt policy keys. It ensures recovery strings are stable, reversible, and rejected when malformed.

## Important APIs, Types, and Functions
Helpers include `getRecoveryCodeFromKey`, `getRandomRecoveryCodeBuffer`, `getKeyFromRecoveryCode`, `testKeyEncodeDecode`, and `testRecoveryDecodeEncode`. Tests include `TestFakeSecretKey`, `TestEncodeDecode`, `TestDecodeEncode`, `TestWrongLengthError`, `TestBadCharacterError`, and `TestBadEndCharacterError`. Benchmarks cover encode, decode, encode/decode, and decode/encode paths.

## Control Flow
The tests construct or generate policy-length keys, call `WriteRecoveryCode`, read them back through `ReadRecoveryCode`, and compare raw key bytes or recovery-code bytes. Negative tests mutate key length, a base32 character, or the separator byte and assert decoding or encoding fails.

## State and Persistence
All state is in memory. Random keys are wiped with `defer key.Wipe()` where applicable. A package-level `fakeSecretKey` and expected string encode a deterministic fixture.

## Dependencies and Integration Points
Uses `metadata.PolicyKeyLen` and the crypto package's key construction helpers. It directly validates the public recovery-code API used by recovery workflows outside this package.

## Risks
The package-level fake key is deliberately insecure and marked testing-only. These tests do not validate user-interface handling, storage of recovery codes, or all possible truncation/extra-data cases.

## Test Signals
The file is itself the test signal: it confirms deterministic encoding of a known key, randomized round trips in both directions, rejection of short keys, rejection of lowercase base32, and rejection of bad separators.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/crypto/recovery_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/filesystem.go -->
# sources/security-integrity/fscrypt/filesystem/filesystem.go

## Purpose
`filesystem.go` implements fscrypt metadata storage for a mounted filesystem. It creates and validates the `.fscrypt` directory tree, reads and writes policy/protector protobuf files, links protectors across filesystems, filters metadata by trusted owners, and protects metadata reads from malicious filesystem objects.

## Important APIs, Types, and Functions
Key types are `Mount`, `SetupMode`, `ErrAlreadySetup`, `ErrCorruptMetadata`, `ErrFollowLink`, `ErrInsecurePermissions`, `ErrNoCreatePermission`, `ErrNotSetup`, `ErrPolicyNotFound`, and `ErrProtectorNotFound`. Public methods include `BaseDir`, `ProtectorDir`, `PolicyDir`, `PolicyPath`, `CheckSupport`, `CheckSetup`, `GetSetupMode`, `Setup`, `RemoveAllMetadata`, `AddProtector`, `AddLinkedProtector`, `GetRegularProtector`, `GetProtector`, `RemoveProtector`, `ListProtectors`, `AddPolicy`, `GetPolicy`, `RemovePolicy`, and `ListPolicies`.

## Control Flow
Setup first checks if metadata already exists, rejects unsupported filesystem types, builds a temporary mount directory, creates `.fscrypt/policies` and `.fscrypt/protectors` with the selected permissions, then atomically renames into place. Metadata writes validate protobuf objects, marshal with `proto.Marshal`, preserve existing owner/mode when possible, write to a synced temporary file, rename over the destination, and sync the parent directory. Reads use `readMetadataFileSafe`, unmarshal, then call `CheckValidity`.

## State and Persistence
Persistent state lives under `<mount>/.fscrypt`, or under a symlink target if `.fscrypt` was intentionally pre-created as a symlink. Policy and protector files are protobuf-encoded and normally mode `0600`. Linked protectors are small `.link` files containing `UUID=` and/or `PATH=` records pointing to another mount. `RemoveAllMetadata` atomically renames the metadata directory away and deletes it via deferred cleanup.

## Dependencies and Integration Points
The file integrates with `metadata` protobuf validation, `mountpoint.go` link resolution via `makeLink` and `getMountFromLink`, `path.go` stat helpers, `util` user/ownership helpers, `unix` for umask and open flags, and `actions` callers that use metadata to unlock/provision policies. It is the persistence layer for protectors and policies consumed by the CLI and PAM module.

## Risks
Metadata security depends on ownership checks and rejecting symlinks/FIFOs/oversized files. The non-atomic overwrite fallback can corrupt an existing file if the write fails, though it is only used when directory creation is denied but file write is possible. `CheckSetup` intentionally allows `.fscrypt` itself to be a symlink, which supports read-only root filesystems but increases reliance on owner and subdirectory checks. `SortDescriptorsByLastMtime` is global mutable state for tests.

## Test Signals
`filesystem_test.go` covers setup/removal, absolute and relative `.fscrypt` symlinks, setup modes, insecure permissions, invalid metadata rejection, policy/protector round trips, spoofed login protector ownership, metadata file modes, linked protectors, and safe metadata-file reads rejecting symlinks, FIFOs, nonexistent files, and oversized files.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/filesystem_test.go -->
# sources/security-integrity/fscrypt/filesystem/filesystem_test.go

## Purpose
This file tests fscrypt metadata setup, persistence, validation, linked protectors, ownership protections, and safe file reading against a real test mount supplied by `util.TestRoot`.

## Important APIs, Types, and Functions
Helpers construct fake protectors and policies with real wrapped key data: `getFakeProtector`, `getFakeLoginProtector`, `getFakePolicy`, `getSetupMount`, `getTwoSetupMounts`, `cleanupTwoMounts`, and `createFile`. Tests cover `Setup`, `RemoveAllMetadata`, setup through `.fscrypt` symlinks, setup modes, `CheckSetup`, `AddProtector`, `AddPolicy`, `GetPolicy`, `GetRegularProtector`, linked protectors, and `readMetadataFileSafe`.

## Control Flow
Most tests obtain a test mount, run `Setup(WorldWritable)`, perform metadata operations, and defer cleanup through `RemoveAllMetadata`. Negative tests mutate metadata fields after a successful control case to assert validation fails. The safe-read test creates files with varying types and sizes and checks expected error classes.

## State and Persistence
Tests write real `.fscrypt` metadata under the configured test filesystem and remove it afterward. Temporary directories and fake mount subdirectories are used for symlink and linked-protector scenarios. Package-level fake keys are created once for wrapping fixtures.

## Dependencies and Integration Points
Depends on `crypto.Wrap`, metadata structs, `proto.Equal`, `unix.Mkfifo`, and test support in `util.TestRoot`. It validates interactions between filesystem persistence and metadata validators rather than only unit-level helpers.

## Risks
Tests require a suitable test root and can be skipped or fail depending on permissions, root status, and filesystem capabilities. Because they mutate `.fscrypt`, a misconfigured `TestRoot` could affect real metadata. Several behaviors vary for root versus non-root ownership checks.

## Test Signals
Strong coverage exists for setup semantics, metadata round trips, validation failures, mode `0600`, linked-protector lookup, login protector UID spoofing, and TOCTOU-oriented safe reading. It does not exhaustively test write crash consistency or all possible malformed protobuf contents.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/filesystem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/mountpoint.go -->
# sources/security-integrity/fscrypt/filesystem/mountpoint.go

## Purpose
`mountpoint.go` discovers mounted filesystems, parses `/proc/self/mountinfo`, chooses one "main" mount per filesystem for fscrypt metadata, and resolves filesystem links by UUID or path.

## Important APIs, Types, and Functions
Global maps `mountsByDevice` and `mountsByPath` are protected by `mountMutex`. Public functions include `EscapeString`, `AllFilesystems`, `UpdateMountInfo`, `FindMount`, and `GetMount`. Internal functions include `parseMountInfoLine`, `findMainMount`, `readMountInfo`, `loadMountInfo`, `getMountFromLink`, `getFilesystemUUID`, and `makeLink`.

## Control Flow
`loadMountInfo` lazily opens `/proc/self/mountinfo` and passes it to `readMountInfo`. Each line is parsed, invalid or non-directory mounts are ignored, duplicate mountpoints keep the latest entry, and mounts are grouped by device number. `findMainMount` builds path trees and mounted-subtree sets to choose an unambiguous metadata location, preferring read-write mounts. `FindMount` first uses the containing device number, then falls back to walking canonical parent paths for cases like btrfs. `GetMount` additionally verifies the requested path is the main mount using `os.SameFile`.

## State and Persistence
Mount data is cached in memory until `UpdateMountInfo` invalidates and reloads it. Link persistence is text generated by `makeLink`, usually with `UUID=<uuid>` and `PATH=<mount>`, stored by `filesystem.go` in `.link` files.

## Dependencies and Integration Points
Uses `path.go` helpers for device numbers, directory checks, and canonicalization. It depends on `/proc/self/mountinfo`, `/sys/dev/block`, `/dev/disk/by-uuid`, and regular OS stat/readlink behavior. `filesystem.go`, actions, keyring options, and PAM policy scans rely on accurate `Mount` resolution.

## Risks
Mount discovery is namespace-sensitive and can be ambiguous with independent bind mounts; the code stores an explicit nil main mount in such cases. UUID lookup can fail or mismatch on filesystems such as btrfs, so link resolution falls back to paths. The cached maps can go stale unless callers invoke `UpdateMountInfo` after mount changes.

## Test Signals
`mountpoint_test.go` exercises mountinfo parsing, special-character escaping, invalid lines, duplicate mountpoints, read-only preference, subtree/mountpoint selection, ambiguous mounts, link generation and fallback, legacy UUID-only links, and mount comparison after reload.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/mountpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/mountpoint_test.go -->
# sources/security-integrity/fscrypt/filesystem/mountpoint_test.go

## Purpose
This test file validates mountinfo parsing and main-mount selection logic with synthetic mountinfo strings and selected live-system checks.

## Important APIs, Types, and Functions
Helpers `beginLoadMountInfoTest`, `endLoadMountInfoTest`, `loadMountInfoFromString`, and `mountForDevice` isolate global mount maps. Tests cover basic parsing, source device resolution, ignoring non-directory mounts, latest mount precedence, escape/unescape behavior, invalid line rejection, read-only flags, main-mount selection, link creation/resolution, UUID/path fallback, and reload value equality.

## Control Flow
Tests lock `mountMutex`, inject synthetic mountinfo via `readMountInfo`, inspect `mountsByDevice` and `mountsByPath`, then reset initialization state. Link tests use the real test mount and `makeLink`/`getMountFromLink`.

## State and Persistence
The tests mutate global mount cache state and use temporary directories for synthetic mountpoints. Link tests read live UUID state under `/dev/disk/by-uuid` when available but do not write metadata files themselves.

## Dependencies and Integration Points
Depends on live directories such as `/tmp`, `/mnt`, `/home`, and sometimes `/dev/loop0` or a configured test root. It provides regression coverage for `filesystem.FindMount`, `GetMount`, and linked-protector resolution.

## Risks
Some cases skip depending on the host environment. Tests that rely on well-known directories can be sensitive to containers or minimal systems. They do not simulate concurrent callers beyond lock isolation.

## Test Signals
Coverage is broad for bind-mount and container-like mount layouts, including ambiguous topologies where the code must refuse to choose a main mount. It also verifies link fallback when UUID or path is invalid.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/mountpoint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/path.go -->
# sources/security-integrity/fscrypt/filesystem/path.go

## Purpose
`path.go` provides low-level path, stat, access, and device-number helpers used by filesystem setup and mount discovery.

## Important APIs, Types, and Functions
`OpenFileOverridingUmask` creates files with exact permissions. `canonicalizePath`, `loggedStat`, `loggedLstat`, `isDir`, `isRegularFile`, and `HaveReadAccessTo` wrap common filesystem checks. `DeviceNumber` represents combined major/minor device numbers, with `String`, `newDeviceNumberFromString`, `getDeviceNumber`, and `getNumberOfContainingDevice`.

## Control Flow
The helpers are direct wrappers around `filepath.Abs`, `filepath.EvalSymlinks`, `os.Stat`, `os.Lstat`, `unix.Access`, `unix.Stat`, and `unix.Lstat`. Device parsing uses `fmt.Sscanf`, and formatting uses `unix.Major`/`unix.Minor`.

## State and Persistence
No persistent state is maintained. `OpenFileOverridingUmask` temporarily changes the process umask and restores it with `defer`, which is process-global state during the call.

## Dependencies and Integration Points
Used by mountpoint parsing for device matching and directory filtering, and by filesystem metadata setup for safe stat behavior. It depends on `golang.org/x/sys/unix` and `github.com/pkg/errors`.

## Risks
Changing umask is process-global and can affect concurrent file creation in other goroutines during the small critical section. `HaveReadAccessTo` reports kernel access checks without opening the file, so callers still need race-safe open logic for security-sensitive reads.

## Test Signals
`path_test.go` validates `/dev/null` device formatting/parsing, invalid device strings, nonexistent device errors, and read-access checks for non-root users across permission modes.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/path_test.go -->
# sources/security-integrity/fscrypt/filesystem/path_test.go

## Purpose
This test file covers device-number conversion and Linux read-access behavior used by mount and metadata helpers.

## Important APIs, Types, and Functions
`TestDeviceNumber` validates `getDeviceNumber`, `DeviceNumber.String`, and `newDeviceNumberFromString`. `TestHaveReadAccessTo` checks `HaveReadAccessTo` against temporary file permission modes.

## Control Flow
The device test asserts `/NONEXISTENT` fails, `/dev/null` formats as `1:3`, and invalid strings fail to parse. The access test creates a temporary file, changes permissions, and compares `HaveReadAccessTo` with expected Linux owner-bit precedence.

## State and Persistence
State is limited to temporary files removed at test end. No repository files are modified.

## Dependencies and Integration Points
Uses `util.IsUserRoot` to skip access checks under root, because root bypasses normal permission behavior. Validates assumptions used by `filesystem` and `mountpoint`.

## Risks
The read-access test is Linux-specific and intentionally skipped as root. `/dev/null` major/minor assumptions are Linux-specific.

## Test Signals
Coverage confirms basic parsing/formatting and non-root permission semantics. It does not cover symlink canonicalization or umask override behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/filesystem/path_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/keyring/fs_keyring.go -->
# sources/security-integrity/fscrypt/keyring/fs_keyring.go

## Purpose
`fs_keyring.go` implements the modern fscrypt filesystem-keyring ioctl path for adding, removing, and querying encryption keys on a mounted filesystem.

## Important APIs, Types, and Functions
Public support detection is `IsFsKeyringSupported`. Internal core functions are `fsAddEncryptionKey`, `fsRemoveEncryptionKey`, `fsGetEncryptionKeyStatus`, `buildKeySpecifier`, `dropPrivsIfNeeded`, `restorePrivs`, and `validateKeyDescriptor`.

## Control Flow
Support detection opens the mount path and probes `FS_IOC_ADD_ENCRYPTION_KEY` with a null argument, treating `ENOTTY` as unsupported and `EFAULT` as supported. Add builds a locked `FscryptAddKeyArg` plus raw key payload, fills the key specifier from a hex descriptor, optionally drops UIDs for v2 user claims, invokes the add ioctl, restores privileges, then validates the returned v2 descriptor. Remove chooses either single-user or all-users ioctl, interprets removal status flags, and maps kernel states to package errors. Status maps kernel status and flags to `KeyStatus`.

## State and Persistence
State is in the kernel keyring and fscrypt key claims, not on disk. Support detection is cached globally in `fsKeyringSupported`/`fsKeyringSupportedKnown`. UID changes are process-wide through the `security` package and are restored after each ioctl.

## Dependencies and Integration Points
Depends on `crypto.Key` for locked ioctl buffers, `filesystem.Mount`, `security.SetUids/GetUids`, Linux fscrypt ioctl structs/constants from `unix`, and cgo `memcpy`. It is selected by `keyring.go` for v2 policy descriptors and optionally for v1 descriptors.

## Risks
Privilege changes are process-wide and risky in multithreaded Go programs, though the code restores saved IDs. Failure to restore privileges is not propagated if ignored after ioctl. Support is cached globally after the first mount probe, assuming kernel-wide support. Incorrect v2 descriptors trigger best-effort cleanup.

## Test Signals
`keyring_test.go` covers v1 filesystem keyring when root and supported, v2 add/remove/status, cross-user removal behavior, multiple-user claims, wrong descriptors, bad mounts, and all-user removal.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/keyring/fs_keyring.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/keyring/keyring.go -->
# sources/security-integrity/fscrypt/keyring/keyring.go

## Purpose
`keyring.go` provides the package-level API for adding, removing, and querying fscrypt policy keys while selecting between deprecated user keyrings and modern filesystem keyrings.

## Important APIs, Types, and Functions
Public errors include `ErrKeyAddedByOtherUsers`, `ErrKeyFilesOpen`, `ErrKeyNotPresent`, and `ErrV2PoliciesUnsupported`. `Options` selects mount, target user, and v1 filesystem-keyring preference. Public functions are `AddEncryptionKey`, `RemoveEncryptionKey`, and `GetEncryptionKeyStatus`. `KeyStatus` enumerates absent/present/busy/other-user states.

## Control Flow
`shouldUseFsKeyring` distinguishes v1 descriptors by hex-encoded `FSCRYPT_KEY_DESCRIPTOR_SIZE`; v1 can use user keyring unless configured otherwise, while v2 always requires filesystem keyring support. `AddEncryptionKey` validates policy key length then delegates to `fsAddEncryptionKey` or `userAddKey`. Remove and status perform the same dispatch and normalize results.

## State and Persistence
No direct state is stored here. It routes operations that affect kernel keyrings. Options are caller-owned and include the target mount/user.

## Dependencies and Integration Points
Integrates crypto key lengths, metadata constants, mount filesystem type, user identity, and both implementation files. `actions.Policy` and PAM provisioning call this layer to provision or deprovision policy keys.

## Risks
Descriptor length is the switch between v1 and v2 semantics; malformed but correctly sized descriptors pass to lower layers for decoding. v2 policies cannot work without filesystem-keyring support. User-keyring fallback for v1 preserves legacy behavior but has different lifetime and privilege semantics.

## Test Signals
`keyring_test.go` exercises dispatch through user keyring, fs keyring for v1, and fs keyring for v2, including invalid key length, duplicate add, absent remove, and status transitions.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/keyring/keyring.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/keyring/keyring_test.go -->
# sources/security-integrity/fscrypt/keyring/keyring_test.go

## Purpose
This integration test file verifies kernel keyring operations across user keyrings, filesystem keyrings for v1 policies, and filesystem keyrings for v2 policies.

## Important APIs, Types, and Functions
Helpers include `ConstReader`, `makeKey`, `assertKeyStatus`, `getTestMount`, `getTestMountV2`, `requireRoot`, `getNonRootUsers`, `getOptionsForFsKeyringUsers`, and `testAddAndRemoveKey`. Tests cover user keyring, fs keyring v1, v2 policy keys, cross-user removal, multiple user claims, wrong v2 descriptors, bad mounts, and root all-user removal.

## Control Flow
Common tests add a fake policy key, assert present status, remove it, assert absent status, confirm removing again returns `ErrKeyNotPresent`, assert duplicate add succeeds, and assert wrong-length keys fail. V2 tests use additional users and root to validate kernel claim semantics.

## State and Persistence
State is in live kernel keyrings. Tests can add and remove keys for real users and require a test mount. Some paths require root and configured users with UIDs starting at 1000.

## Dependencies and Integration Points
Depends on `filesystem.GetMount`, `util.TestRoot`, crypto descriptor derivation, metadata key lengths, and Linux fscrypt kernel support. It validates the real behavior used by policy provisioning and PAM session handling.

## Risks
Tests are environment-sensitive and skip when root, test users, filesystem keyring support, or test mount are unavailable. Failed cleanup could leave keys in kernel keyrings until session/user keyring cleanup or explicit removal.

## Test Signals
The tests strongly signal expected kernel-keyring semantics, especially v2 user-claim isolation and all-user removal. They do not mock ioctl failures beyond nonexistent mount paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/keyring/keyring_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/keyring/user_keyring.go -->
# sources/security-integrity/fscrypt/keyring/user_keyring.go

## Purpose
`user_keyring.go` implements the legacy Linux user-keyring path for v1 fscrypt policy keys. It creates `logon` keys containing `unix.FscryptKey` payloads and links/accesses target users' uid keyrings.

## Important APIs, Types, and Functions
Errors are `ErrAccessUserKeyring` and `ErrSessionUserKeyring`. `KeyType` is `logon`. Core functions are `userAddKey`, `userRemoveKey`, `userFindKey`, `UserKeyringID`, `userKeyringIDLookup`, `isUserKeyringInSession`, and `keyringLink`.

## Control Flow
Operations lock the current OS thread to keep thread-keyring possession stable. Adding builds a locked `FscryptKey` payload, resolves the target user keyring, then calls `unix.AddKey`. Removing searches then unlinks. `UserKeyringID` ensures non-root callers only use a user keyring linked into the session keyring when requested, while root links target keyrings into root's user keyring to keep access. `userKeyringIDLookup` temporarily changes real/effective UIDs to make `KEY_SPEC_USER_KEYRING` refer to the target UID, links it into the thread keyring, then restores UIDs.

## State and Persistence
State is in kernel user/session/thread keyrings. The function temporarily changes process UIDs and persists links in root or thread keyrings as needed. Sensitive key payloads are allocated as `crypto.Key` and wiped after `AddKey`.

## Dependencies and Integration Points
Depends on `crypto.Key`, `security.SetUids/GetUids`, Linux keyctl syscalls, `runtime.LockOSThread`, and user identity helpers. It is selected by `keyring.go` for v1 policies when filesystem keyrings are not configured or unavailable.

## Risks
UID switching and keyring possession are subtle and process-wide/thread-sensitive. Non-root behavior depends on session keyring setup; otherwise `ErrSessionUserKeyring` is returned. The legacy mechanism has weaker policy semantics than filesystem keyrings and is unsuitable for v2.

## Test Signals
`keyring_test.go` covers user keyring add/status/remove for v1 descriptors and invalid key lengths. Root/session edge cases are indirectly tested through integration conditions rather than unit mocks.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/keyring/user_keyring.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/checks.go -->
# sources/security-integrity/fscrypt/metadata/checks.go

## Purpose
`checks.go` defines validation for all metadata protobuf structures before they are persisted or trusted after reading from disk.

## Important APIs, Types, and Functions
`Metadata` combines `CheckValidity` and `proto.Message`. `CheckValidity` methods exist for `EncryptionOptions_Mode`, `SourceType`, `HashingCosts`, `WrappedKeyData`, `ProtectorData`, `EncryptionOptions`, `WrappedPolicyKey`, `PolicyData`, and `Config`. `MaxParallelism` constrains Argon2 parallelism.

## Control Flow
Validation rejects default or unknown enums, nil messages, invalid Argon2 cost ranges, invalid salt/IV/HMAC/key/descriptor lengths, missing source-specific fields, bad padding, and unsupported policy versions. `EncryptionOptions.CheckValidity` normalizes unset policy version `0` to `1` for legacy compatibility. `HashingCosts` preserves backwards compatibility by truncating old overlarge parallelism when `TruncationFixed` is false and the uint8 truncation is nonzero.

## State and Persistence
Validation mutates `EncryptionOptions.PolicyVersion` from `0` to `1` and may log truncation behavior. It otherwise reads in-memory protobuf structs. Its results gate filesystem persistence and loaded metadata trust.

## Dependencies and Integration Points
Depends on metadata constants, `util.CheckValidLength`, padding arrays from `policy.go`, protobuf interfaces, and `github.com/pkg/errors`. `filesystem.addMetadata`, `filesystem.getMetadata`, config loading, and policy setup rely on these checks.

## Risks
Validation is a security boundary for disk metadata. Backward-compatible parallelism truncation is intentional but can surprise operators reading old metadata. Because `CheckValidity` mutates policy version, callers should not assume it is pure.

## Test Signals
`filesystem_test.go`, `config_test.go`, and `policy_test.go` exercise many validation failures: bad source, missing hashing costs, wrong wrapped key lengths, bad descriptor lengths, invalid padding/modes, and legacy config policy-version normalization.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/checks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/config.go -->
# sources/security-integrity/fscrypt/metadata/config.go

## Purpose
`config.go` serializes and deserializes the global fscrypt config protobuf as human-readable JSON.

## Important APIs, Types, and Functions
`WriteConfig(config, out)` marshals `Config` using `protojson.MarshalOptions` with multiline indentation, proto field names, enum names, and unpopulated fields. `ReadConfig(in)` reads all JSON and unmarshals with `DiscardUnknown` for forward and legacy compatibility.

## Control Flow
Writing marshals the config, writes the bytes, then writes a trailing newline. Reading consumes the entire reader, allocates a new `Config`, and unmarshals JSON into it.

## State and Persistence
This file does not choose the config path but defines the serialized on-disk format used for `/etc/fscrypt.conf`-style configuration. It does not call `CheckValidity`; callers must validate after reading.

## Dependencies and Integration Points
Depends on `google.golang.org/protobuf/encoding/protojson` and `io`. The config fields feed actions, protector defaults, policy options, filesystem keyring behavior for v1 policies, and cross-user metadata behavior.

## Risks
Unknown fields are discarded, which is useful for compatibility but can hide misspellings or unsupported settings. `EmitUnpopulated` writes explicit false/zero values, so output changes when schema fields are added.

## Test Signals
`config_test.go` verifies exact JSON shape modulo whitespace, read/write round trip via `proto.Equal`, legacy unknown `compatibility` field handling, default false booleans, and policy version normalization after validity checks.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/config_test.go -->
# sources/security-integrity/fscrypt/metadata/config_test.go

## Purpose
This file tests JSON config serialization, deserialization, and compatibility with older config files.

## Important APIs, Types, and Functions
`testConfig` and `testConfigString` define the expected config object and JSON. `compact` normalizes JSON for comparison. Tests are `TestWrite`, `TestRead`, and `TestOptionalFields`.

## Control Flow
`TestWrite` serializes the config and compares compacted JSON. `TestRead` parses the fixture and compares protobuf equality. `TestOptionalFields` parses a legacy JSON document without newer fields and with the removed `compatibility` field, then validates defaults and `CheckValidity` normalization.

## State and Persistence
All config data is in memory. No real config files are written.

## Dependencies and Integration Points
Uses `encoding/json` for test normalization and protobuf equality. It validates behavior consumed by actions and PAM configuration loading.

## Risks
Exact JSON expectations can need updates when proto schema or marshal options change. The test checks compatibility but not invalid configs or malformed JSON.

## Test Signals
The tests confirm proto field names, enum names, int64 string encoding in protojson, emitted false booleans, unknown-field discard, and legacy policy-version upgrade from `0` to `1`.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/constants.go -->
# sources/security-integrity/fscrypt/metadata/constants.go

## Purpose
`constants.go` defines shared key, descriptor, IV, salt, HMAC, and default metadata option constants for fscrypt.

## Important APIs, Types, and Functions
Constants include `PolicyDescriptorLenV1`, `ProtectorDescriptorLen`, `PolicyDescriptorLenV2`, `InternalKeyLen`, `IVLen`, `SaltLen`, `HMACLen`, and `PolicyKeyLen`. Variables include `DefaultOptions` and `DefaultSource`.

## Control Flow
There is no runtime control flow beyond package initialization of default options. Lengths derive from kernel fscrypt constants and SHA-256 size.

## State and Persistence
`DefaultOptions` is a mutable pointer to an `EncryptionOptions` struct, so callers could accidentally mutate shared defaults. The constants define on-disk and kernel-facing metadata sizes.

## Dependencies and Integration Points
Depends on `crypto/sha256` and `golang.org/x/sys/unix`. Used across crypto recovery, keyring validation, metadata checks, policy setup, config defaults, and tests.

## Risks
Because defaults are exported as a pointer, defensive cloning is needed if callers plan to modify options. Kernel constant changes can affect compatibility assumptions.

## Test Signals
Covered indirectly by metadata validation, recovery-code tests, policy tests, and keyring tests that rely on these exact lengths and defaults.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/constants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/metadata.pb.go -->
# sources/security-integrity/fscrypt/metadata/metadata.pb.go

## Purpose
`metadata.pb.go` is generated Go code for `metadata.proto`. It provides the concrete protobuf message and enum types used for fscrypt on-disk metadata and JSON config serialization.

## Important APIs, Types, and Functions
Generated enums are `SourceType` and `EncryptionOptions_Mode`. Generated messages are `HashingCosts`, `WrappedKeyData`, `ProtectorData`, `EncryptionOptions`, `WrappedPolicyKey`, `PolicyData`, and `Config`, each with `Reset`, `String`, `ProtoReflect`, descriptor accessors, and field getters. `File_metadata_metadata_proto` exposes the file descriptor.

## Control Flow
The generated init path builds enum/message descriptors with `protoimpl.TypeBuilder`, compresses raw descriptors on demand, and exposes getters that return zero values when receivers are nil.

## State and Persistence
This code defines the in-memory representation of serialized metadata. Persistent compatibility is tied to field numbers in the raw descriptor and the reserved `compatibility` field.

## Dependencies and Integration Points
Generated by `protoc-gen-go`; depends on `protoreflect`, `protoimpl`, `reflect`, `sync`, and `unsafe`. All metadata validation, filesystem persistence, config JSON, and key wrapping metadata operate on these types.

## Risks
Manual edits would be overwritten and can desynchronize from `metadata.proto`. Regeneration requires a compatible `protoc`/plugin toolchain. Since this is generated, security logic should live in hand-written validation rather than in this file.

## Test Signals
Tests exercise generated behavior through `proto.Marshal`, `proto.Unmarshal`, `proto.Equal`, protojson, getters, and validation. No tests should target implementation details of generated descriptor construction directly.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/metadata.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/metadata.proto -->
# sources/security-integrity/fscrypt/metadata/metadata.proto

## Purpose
`metadata.proto` is the authoritative schema for fscrypt metadata stored in `.fscrypt` files and for the global JSON config.

## Important APIs, Types, and Functions
Messages define hashing costs, wrapped keys, protectors, encryption options, wrapped policy keys, policies, and config. Enums define protector source types and encryption modes corresponding to kernel fscrypt mode constants. The `compatibility` field number and name are reserved.

## Control Flow
There is no runtime control flow. Schema changes require running `make gen` to regenerate `metadata.pb.go`.

## State and Persistence
Field numbers define persistent wire compatibility. `ProtectorData` stores source, optional passphrase hashing settings, salt, UID, and wrapped internal key. `PolicyData` stores key descriptor, encryption options, and wrapped policy-key slots. `Config` stores defaults and behavior flags.

## Dependencies and Integration Points
The Go package option maps generated code to `github.com/google/fscrypt/metadata`. The schema is consumed by filesystem metadata persistence, crypto wrapping, config JSON, actions, keyring selection, and PAM login protector discovery.

## Risks
Changing field numbers or enum values would break compatibility with existing metadata. Adding new encryption modes must be matched with validation and kernel support logic. Reserved fields protect legacy configs from accidental reuse.

## Test Signals
Config, filesystem, policy, and generated-code usage tests indirectly validate that the schema matches expected JSON and protobuf behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/metadata.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/policy.go -->
# sources/security-integrity/fscrypt/metadata/policy.go

## Purpose
`policy.go` interfaces with Linux fscrypt policy ioctls to get, set, and support-check encryption policies on files or directories.

## Important APIs, Types, and Functions
Public errors include `ErrEncryptionNotSupported`, `ErrEncryptionNotEnabled`, `ErrAlreadyEncrypted`, `ErrBadEncryptionOptions`, `ErrDirectoryNotOwned`, `ErrLockedRegularFile`, and `ErrNotEncrypted`. Public functions are `GetPolicy`, `SetPolicy`, and `CheckSupport`. Internal helpers map kernel policy structs and flags: `getPolicyIoctl`, `setPolicy`, `flagsToPadding`, `buildV1PolicyData`, `buildV2PolicyData`, `shouldUseDirectKeyFlag`, `buildPolicyFlags`, `setV1Policy`, and `setV2Policy`.

## Control Flow
`GetPolicy` opens the path, tries `FS_IOC_GET_ENCRYPTION_POLICY_EX`, falls back to the legacy ioctl on `ENOTTY`, maps kernel errors to package errors, and converts v1 or v2 structs into `PolicyData`. `SetPolicy` opens the directory, validates metadata, decodes the descriptor, dispatches to v1 or v2 policy setting, disambiguates old-kernel `EINVAL`, and maps errors to domain-specific messages. `CheckSupport` sets an intentionally invalid policy and interprets kernel errors to infer encryption support/enabled state.

## State and Persistence
Successful `SetPolicy` persists an encryption policy on the target directory in the filesystem through kernel ioctls and syncs the file descriptor. No `.fscrypt` metadata file is written here; that is handled by `filesystem.go`.

## Dependencies and Integration Points
Depends on Linux fscrypt ioctl constants, metadata structs, `util.Lookup`, and descriptor lengths from validation. Called by actions when encrypting directories and by filesystem support checks through `Mount.CheckSupport`.

## Risks
Ioctl behavior differs across kernel versions; the code includes fallbacks and error disambiguation but notes race potential when statting after `EINVAL`. `CheckSupport` deliberately calls set-policy with invalid data and must panic if the impossible success path occurs. Caller must ensure policy keys are provisioned before setting v2 policies as required by the kernel.

## Test Signals
`policy_test.go` covers setting policies on empty directories, failing on nonempty directories and files, rejecting bad descriptors, reading back v1 policy data, unencrypted directory errors, and v2 no-key behavior for non-root users when supported.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/policy_test.go -->
# sources/security-integrity/fscrypt/metadata/policy_test.go

## Purpose
This test file validates setting and reading kernel fscrypt policies on a test filesystem and error behavior for invalid targets or descriptors.

## Important APIs, Types, and Functions
Fixtures include `goodV1Policy`, `goodV2Policy`, and encryption option structs. Helpers `createTestDirectory`, `createTestFile`, and `requireV2PolicySupport` prepare test directories and gate v2 behavior. Tests cover empty directories, nonempty directories, regular files, bad descriptors, reading policies, unencrypted directories, and v2 policy without key.

## Control Flow
Tests create directories under `util.TestRoot`, call `SetPolicy`, use `GetPolicy` for round trips, and remove temporary directories. Negative cases assert error presence rather than exact kernel error for every scenario.

## State and Persistence
Tests set real fscrypt policies on temporary directories and then remove the directory tree. Once a policy is set, it is a filesystem-level state until deletion.

## Dependencies and Integration Points
Depends on Linux fscrypt support in the test filesystem, `unix` ioctl constants, and `proto.Equal`. It validates behavior used by encrypt actions and metadata support checks.

## Risks
Environment-sensitive tests may skip or fail depending on kernel, filesystem feature flags, root status, and configured test root. Tests do not cover all v2 success paths, which are handled in keyring tests.

## Test Signals
The file confirms core kernel policy interactions and validates important user-facing error cases around nonempty dirs, regular files, malformed descriptors, and missing v2 keys.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/metadata/policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/constants.go -->
# sources/security-integrity/fscrypt/pam/constants.go

## Purpose
`pam/constants.go` exposes selected Linux PAM item and flag constants to Go code via cgo.

## Important APIs, Types, and Functions
`Item` wraps PAM item identifiers such as `Service`, `User`, `Tty`, `Rhost`, `Authtok`, `Oldauthtok`, `Ruser`, and `UserPrompt`. `Flag` wraps PAM flags such as `Silent`, `DisallowNullAuthtok`, credential flags, `ChangeExpiredAuthtok`, `PrelimCheck`, and `UpdateAuthtok`.

## Control Flow
There is no runtime logic; constants are assigned from C PAM macros at compile time.

## State and Persistence
No state or persistence. These constants parameterize PAM calls in `pam.go` and `pam_fscrypt.go`.

## Dependencies and Integration Points
Uses cgo and links `-lpam`, including `<security/pam_modules.h>`. Values are consumed by handle item access, authentication, and password-change hooks.

## Risks
Requires PAM development headers and libpam at build time. Constant availability follows the target platform PAM implementation.

## Test Signals
Only indirect coverage through PAM wrapper and module code; `pam_test.go` is a stub.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/constants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/login.go -->
# sources/security-integrity/fscrypt/pam/login.go

## Purpose
`pam/login.go` verifies whether a supplied `crypto.Key` matches a user's login passphrase by running a PAM authentication transaction.

## Important APIs, Types, and Functions
`ErrPassphrase` reports failed authentication. Exported cgo callbacks `userInput` and `passphraseInput` provide PAM conversation responses. `IsUserLoginToken(username, token, quiet)` is the public verification API. Global `tokenLock` and `tokenToCheck` serialize callback state.

## Control Flow
`IsUserLoginToken` locks global callback state, stores the token, starts the `fscrypt` PAM service transaction, calls `Authenticate`, and maps false authentication to `ErrPassphrase`. `passphraseInput` returns a C string copy of the token on first prompt and then clears `tokenToCheck` so repeated secret prompts fail. `userInput` prompts on stdout for echo-on input.

## State and Persistence
The login token remains caller-owned; this file does not wipe it. A transient C string copy is returned to PAM and must be cleaned by the PAM conversation cleanup. Global state exists only while the lock is held.

## Dependencies and Integration Points
Uses `crypto.Key.UnsafeToCString`, PAM transaction wrappers in `pam.go`, util line input, cgo exports, and libpam. It is used by higher-level actions that need to validate login passphrases.

## Risks
Global callback state prevents concurrent PAM token checks and would be unsafe without the mutex. `UnsafeToCString` creates an unmanaged C copy, so cleanup correctness is important. PAM modules may request multiple secret prompts, which this implementation deliberately rejects.

## Test Signals
No substantive local tests; PAM package has only a trivial stub. Behavior is indirectly exercised where login protector workflows are integration-tested outside this subset.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/login.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/pam.c -->
# sources/security-integrity/fscrypt/pam/pam.c

## Purpose
`pam.c` provides the C side of the Go/PAM bridge: conversation callback plumbing, data cleanup functions, locked secret copying, secure secret freeing, and message emission.

## Important APIs, Types, and Functions
`conversation` implements `pam_conv`. `goConv` exposes it to Go. Cleanup helpers are `freeData`, `freeArray`, and `freeSecret`. `copyIntoSecret` creates a locked C copy of a secret. `infoMessage` wraps `pam_info`.

## Control Flow
The conversation allocates a response array, iterates PAM messages, dispatches echo-off prompts to Go `passphraseInput`, echo-on prompts to Go `userInput`, prints informational/error messages, and frees partial responses on callback failure. Secret cleanup zeroes via a volatile `memset` function pointer, calls `munlock`, then frees.

## State and Persistence
PAM response arrays and secret copies are heap allocations. `copyIntoSecret` attempts to `mlock` the copied secret but does not report lock failure. No persistent state is written.

## Dependencies and Integration Points
Includes PAM headers, cgo export header, libc allocation/string functions, and `sys/mman.h`. Called from `pam.go` for transactions and handle data management.

## Risks
`mlock`/`munlock` return values are ignored in the C helpers. Conversation messages that do not match known styles are not explicitly handled beyond the switch fallthrough behavior. Correct cleanup depends on PAM invoking registered cleanup functions.

## Test Signals
No direct C unit tests. PAM wrapper and module tests are mostly stubs, so this bridge is primarily validated by build/link success and external integration.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/pam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/pam.go -->
# sources/security-integrity/fscrypt/pam/pam.go

## Purpose
`pam.go` wraps libpam handles and transactions for Go code and PAM modules, including PAM data storage, item access, privilege switching to the PAM user, messaging, transaction start/end, and authentication.

## Important APIs, Types, and Functions
`Handle` wraps `pam_handle_t` and tracks `status`, original privileges, and `PamUser`. Public methods include `NewHandle`, `ClearData`, `SetSecret`, `GetSecret`, `SetString`, `GetString`, `GetItem`, `GetServiceName`, `StartAsPamUser`, `StopAsPamUser`, and `InfoMessage`. `Transaction` supports `Start`, `End`, and `Authenticate`.

## Control Flow
`NewHandle` retrieves the PAM username and resolves it through `os/user`. Data helpers allocate C strings or locked secret copies and register cleanup callbacks. `StartAsPamUser` saves current process privileges and switches effective UID/GID/groups to the PAM user. `StopAsPamUser` restores saved privileges. `Start` calls `pam_start` with `goConv`, while `Authenticate` invokes `pam_authenticate` with disallow-null and optional silent flags.

## State and Persistence
State is stored in the live PAM handle and process credentials. Secrets stored with `SetSecret` are copied into locked C memory and later wiped by C cleanup. `origPrivs` in `Handle` tracks whether privilege restoration is needed.

## Dependencies and Integration Points
Uses cgo libpam, C helpers from `pam.h`, `security` privilege management, and `os/user`. `pam_fscrypt` depends heavily on `Handle` for authentication/session/password hooks.

## Risks
Process-wide privilege switching is sensitive in Go and must be balanced. PAM data pointers are raw C memory and type correctness is manual. `ClearData` replaces data with an empty C string rather than removing the key outright. Authentication false is separated from PAM execution errors.

## Test Signals
Local `pam_test.go` is a trivial compile/pass test. Real confidence comes from build integration and PAM module workflows, not unit coverage.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/pam.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/pam.h -->
# sources/security-integrity/fscrypt/pam/pam.h

## Purpose
`pam.h` declares the C bridge functions and types shared between `pam.c` and cgo in `pam.go`.

## Important APIs, Types, and Functions
It declares `goConv`, `CleanupFunc`, `freeData`, `freeArray`, `copyIntoSecret`, `freeSecret`, and `infoMessage`.

## Control Flow
There is no implementation control flow in the header. It defines ABI signatures used by Go cgo declarations.

## State and Persistence
No state is stored here. The declarations govern PAM data cleanup and secret handling implemented in `pam.c`.

## Dependencies and Integration Points
Includes `<security/pam_appl.h>`. Used by both the C implementation and Go cgo block.

## Risks
Signature mismatches would cause build or runtime memory safety issues. The typo in comments (`CleaupFunc`) is harmless but present.

## Test Signals
Covered by successful cgo compilation and any PAM integration tests. There are no direct header tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/pam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/pam_test.go -->
# sources/security-integrity/fscrypt/pam/pam_test.go

## Purpose
This is a stub test file for the PAM package.

## Important APIs, Types, and Functions
It defines only `TestTrivial`, which always passes.

## Control Flow
No meaningful control flow beyond an empty test function.

## State and Persistence
No state or persistence.

## Dependencies and Integration Points
Imports `testing` and ensures the package participates in `go test`.

## Risks
It provides no behavioral coverage for PAM transactions, C cleanup, privilege switching, or login token checks.

## Test Signals
The only signal is compile/package viability. PAM functionality requires external integration testing.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam/pam_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam_fscrypt/config -->
# sources/security-integrity/fscrypt/pam_fscrypt/config

## Purpose
This file is the PAM profile metadata for installing/enabling `pam_fscrypt` passphrase support.

## Important APIs, Types, and Functions
It declares the profile name, default enablement, priority, and auth/session/password stack entries using `PAM_INSTALL_PATH`.

## Control Flow
There is no program control flow. The PAM stack consumes these directives during installation or configuration.

## State and Persistence
When installed, it influences persistent PAM configuration by adding optional auth, session, and password hooks for the fscrypt PAM module.

## Dependencies and Integration Points
Integrates with PAM configuration tooling and the built shared object path substituted for `PAM_INSTALL_PATH`. It corresponds to exported functions in `pam_fscrypt.go`.

## Risks
Because hooks are optional, module failures may not block login depending on PAM stack behavior, but password/session integration can still affect unlock/lock behavior. Incorrect install path substitution would make the profile ineffective.

## Test Signals
No automated tests for this config file in the subset. Behavior is validated by packaging or PAM integration tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam_fscrypt/config -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam_fscrypt/pam_fscrypt.go -->
# sources/security-integrity/fscrypt/pam_fscrypt/pam_fscrypt.go

## Purpose
`pam_fscrypt.go` implements the exported PAM module hooks that copy login tokens, unlock fscrypt policies at session open, lock them at final session close, and rewrap login protectors after password changes.

## Important APIs, Types, and Functions
Constants define PAM data labels and module flags: `authtokLabel`, `pidLabel`, `debugFlag`, `lockPoliciesFlag`, `unlockOnlyFlag`, and `dropCachesFlag`. Core functions are `Authenticate`, `OpenSession`, `CloseSession`, `lockLoginPolicies`, `Chauthtok`, `setupUserKeyringIfNeeded`, `isUnsupportedFork`, `beginProvisioningOp`, and `endProvisioningOp`. Exported PAM symbols include `pam_sm_authenticate`, `pam_sm_setcred`, `pam_sm_open_session`, `pam_sm_close_session`, and `pam_sm_chauthtok`.

## Control Flow
`Authenticate` switches to the PAM user, saves the current PID, detects whether a login protector exists, and stores a locked copy of `AUTHTOK` for later session use. `OpenSession` increments the session count, switches to the PAM user, finds the login protector and policies needing unlock, detects unsupported fork-between-auth-and-session cases, prepares keyrings, unlocks the protector from stored `AUTHTOK`, then provisions each policy, temporarily regaining root for operations that need it. `CloseSession` decrements the count and, only for the last session and unless `unlock_only` is set, deprovisions login-protected policies and drops inode/dentry caches if user-keyring policies require it. `Chauthtok` unlocks the login protector with `OLDAUTHTOK` and rewraps it with new `AUTHTOK`.

## State and Persistence
PAM handle data stores the copied auth token and original PID. Session counts persist under `/run/fscrypt` via `run_fscrypt.go`. Policy provisioning changes kernel keyring state; protector rewrapping updates metadata through actions. Secrets are cleared from PAM data after session open.

## Dependencies and Integration Points
Integrates with `actions` protectors/policies, `crypto.NewKeyFromCString`, `keyring.UserKeyringID`, `pam.Handle`, and `security.DropFilesystemCache`. It is the bridge between system login/session/password lifecycle and fscrypt policy key provisioning.

## Risks
PAM modules run in sensitive login processes. The code has explicit fork detection because Go runtime after fork can deadlock, but detection may occur after Go code has already run. Correct privilege switching is critical. If `AUTHTOK` is missing, login-protected directories will not unlock. The deprecated flags are accepted but mostly no-ops, which can surprise older configurations.

## Test Signals
Direct tests are sparse; `run_test.go` only covers empty argument parsing. Behavior relies on integration with actions, keyring, filesystem metadata, PAM handle wrappers, and system-level PAM tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam_fscrypt/pam_fscrypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam_fscrypt/run_fscrypt.go -->
# sources/security-integrity/fscrypt/pam_fscrypt/run_fscrypt.go

## Purpose
`run_fscrypt.go` contains support code for executing PAM module functions: argument parsing, syslog setup, panic handling, system-user skipping, login protector discovery, policy scanning, and session count tracking.

## Important APIs, Types, and Functions
`PamFunc` wraps a named PAM operation. Important functions include `isSystemUser`, `(*PamFunc).Run`, `parseArgs`, `setupLogging`, `loginProtector`, `policiesUsingProtector`, `AdjustCount`, and `getCount`. Constants define `/run/fscrypt` count files, permissions, count format, and `uidMin`.

## Control Flow
`Run` parses argv, configures logging, defers panic-to-syslog conversion, creates a PAM handle, skips users below `uidMin` except root, and invokes the wrapped implementation. `loginProtector` builds an actions context for the login protector mountpoint, applies trusted-user restrictions unless cross-user metadata is allowed, then selects a PAM passphrase protector matching the PAM UID. `policiesUsingProtector` scans all filesystems, follows protectors, lists policies, loads each policy in a cloned context, filters by protector usage and provisioned state, and returns matches. `AdjustCount` creates `/run/fscrypt`, locks a per-UID count file, clamps counts at zero, rewrites the count, and returns it.

## State and Persistence
Session counts are persisted in tmpfs under `/run/fscrypt/<uid>.count` with root-only permissions and reset on reboot. Logging goes to syslog. Policy scans read metadata across mounted filesystems but do not directly modify it.

## Dependencies and Integration Points
Depends on `actions`, `filesystem.AllFilesystems`, `metadata`, PAM handles, `util.PointerSlice`, and `unix.Flock`. It supports all exported hooks in `pam_fscrypt.go`.

## Risks
Count files need root privileges and correct locking; stale counts can affect whether close-session locks policies. Policy scanning can be expensive across many filesystems and is sensitive to metadata ownership rules. Panic handling converts failures to PAM service errors but cannot undo partial provisioning.

## Test Signals
`run_test.go` only verifies empty argument parsing. Most behavior needs integration tests with PAM handles, metadata, mounted filesystems, and syslog.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam_fscrypt/run_fscrypt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/pam_fscrypt/run_test.go -->
# sources/security-integrity/fscrypt/pam_fscrypt/run_test.go

## Purpose
This test file minimally verifies PAM module argument parsing.

## Important APIs, Types, and Functions
It contains `TestParseArgsEmpty`, which calls `parseArgs(0, nil)`.

## Control Flow
The test asserts that empty C argc/argv produces a non-nil empty Go map.

## State and Persistence
No state is written.

## Dependencies and Integration Points
Imports only `testing` but validates a helper used by `PamFunc.Run` before every PAM hook invocation.

## Risks
Coverage is very narrow. Non-empty argv parsing, syslog setup, login protector discovery, policy scanning, and count-file handling are untested here.

## Test Signals
The file confirms a basic no-argument case and package test viability.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/pam_fscrypt/run_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/security/cache.go -->
# sources/security-integrity/fscrypt/security/cache.go

## Purpose
`cache.go` exposes a helper to drop reclaimable inode and dentry caches so locked encrypted directories become inaccessible after key removal.

## Important APIs, Types, and Functions
`DropFilesystemCache()` is the only function.

## Control Flow
The function logs a sync step, calls `unix.Sync`, opens `/proc/sys/vm/drop_caches` with write and sync flags, writes `"2"`, and returns any open or write error.

## State and Persistence
It changes kernel VM cache state and requires root privileges. It does not persist repository or fscrypt metadata state.

## Dependencies and Integration Points
Uses `golang.org/x/sys/unix`, `os`, and `log`. `pam_fscrypt.CloseSession` calls it when deprovisioning user-keyring policies requires cache dropping to complete locking.

## Risks
Requires root and access to procfs. Dropping dentries/inodes can affect system performance, though it avoids dropping the entire page cache. It assumes cache dropping is needed only in specific legacy/user-keyring cases.

## Test Signals
No direct behavioral tests beyond package stub. Root-only integration would be required to validate actual cache dropping.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/security/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/security/privileges.go -->
# sources/security-integrity/fscrypt/security/privileges.go

## Purpose
`privileges.go` manages process credentials for fscrypt, especially PAM and keyring flows that need to temporarily act as a target user or regain root.

## Important APIs, Types, and Functions
`Privileges` stores effective UID, effective GID, and supplementary groups. Public functions are `ProcessPrivileges`, `UserPrivileges`, `SetProcessPrivileges`, `SetUids`, and `GetUids`.

## Control Flow
`ProcessPrivileges` reads current uid/gid and supplementary groups. `UserPrivileges` converts an `os/user.User` to target UID/GID/groups. `SetProcessPrivileges` elevates effective UID to root, sets groups, effective GID, then effective UID, and logs resulting privileges. `SetUids` first sets all real/effective/saved UIDs to root, then sets requested real/effective/saved IDs. `GetUids` reads real/effective/saved IDs.

## State and Persistence
These functions mutate process-wide credentials through libc calls. No disk state is written. Saved `Privileges` objects are in-memory snapshots used to restore previous credentials.

## Dependencies and Integration Points
Uses cgo libc functions rather than raw syscalls because Go raw credential syscalls are per-thread on Linux. This is critical for `pam_fscrypt`, PAM handle privilege switching, and keyring v2 user-claim operations.

## Risks
Privilege changes are security-critical. Incorrect ordering or failure to restore can leave the process with wrong privileges. The code assumes root capability for many transitions. Because these are process-wide, concurrent goroutines may observe changed privileges.

## Test Signals
`security_test.go` is only a trivial stub. Indirect tests exercise privilege functions through keyring and PAM integration when run with root.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/security/privileges.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/fscrypt/security/security_test.go -->
# sources/security-integrity/fscrypt/security/security_test.go

## Purpose
This is a stub test file for the `security` package.

## Important APIs, Types, and Functions
It defines only `TestTrivial`.

## Control Flow
The test has no assertions or operations.

## State and Persistence
No state is read or written.

## Dependencies and Integration Points
Imports `testing` and keeps the package in the test suite.

## Risks
It provides no coverage for root-only cache dropping or process credential mutation, both of which are high-risk behaviors.

## Test Signals
Only package compile/test harness viability is signaled. Real validation comes indirectly from keyring/PAM integration tests or manual system tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/fscrypt/security/security_test.go -->
