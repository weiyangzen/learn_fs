# Group Research: subset-b-008321

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore2.h -->
# sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore2.h

## Purpose
Defines a block-store abstraction for creating, loading, storing, and removing block payloads by `BlockId`; the default `create` loop repeatedly allocates random IDs until `tryCreate` succeeds. This specific file has 53 source lines under `sources/security-integrity/cryfs/old-cpp/src/blockstore/interface` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `BlockStore2`. Macros/constants: `MESSMER_BLOCKSTORE_INTERFACE_BLOCKSTORE2_H_`. Important declarations or call sites include `virtual ~BlockStore2() {}`; `virtual BlockId createBlockId() const {`; `return BlockId::Random();`; `virtual bool tryCreate(const BlockId &blockId, const cpputils::Data &data) = 0;`; `virtual bool remove(const BlockId &blockId) = 0;`; `virtual boost::optional<cpputils::Data> load(const BlockId &blockId) const = 0;`; `virtual void store(const BlockId &blockId, const cpputils::Data &data) = 0;`; `BlockId create(const cpputils::Data& data) {`; `while (true) {`; `BlockId blockId = createBlockId();`. CMake commands used here include `while`, `if`. Primary includes/dependencies visible in the file include `Block.h`, `string`, `boost/optional.hpp`, `cpp-utils/pointer/unique_ref.h`, `cpp-utils/data/Data.h`, `cpp-utils/random/Random.h`.

## Control Flow
The important flow is `create(data)`: generate an ID via `createBlockId`, call virtual `tryCreate`, and retry until no collision occurs. Implementations provide the persistence behavior behind the virtual calls.

## State and Persistence Behavior
The interface itself stores no state; concrete block stores decide whether data is persisted, cached, or encrypted. The `create` retry loop relies on random `BlockId` uniqueness but does not record attempts.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Block.h`, `string`, `boost/optional.hpp`, `cpp-utils/pointer/unique_ref.h`, `cpp-utils/data/Data.h`, `cpp-utils/random/Random.h`.

## Risks and Edge Cases
A broken `tryCreate` implementation could make `create` spin forever. Collision handling and atomicity are delegated to implementations, so tests must cover duplicate IDs and partial writes.

## Test Signals
Exercise `tryCreate` collision, load/store/remove round trips, optional miss behavior, and ID uniqueness under repeated creation.

## File-Specific Notes
- `BlockStore2` exposes `tryCreate`, `remove`, `load`, and `store`; `create` is an inline convenience API that retries on random block-ID collisions.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/blockstore/interface/BlockStore2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/CMakeLists.txt

## Purpose
Describes how this source subtree is built, which sources enter the library or executable, and which third-party or sibling CryFS components are linked. This specific file has 102 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
CMake commands used here include `project`, `set`, `add_library`, `if`, `target_link_libraries`, `elseif`, `target_compile_definitions`, `else`, `find_program`, `message`, `endif`, `find_package`.

## Control Flow
CMake control is declarative: sources are grouped into targets, include directories are exposed, and link dependencies connect this subtree to Boost, Crypto++, fspp, blockstore, and CryFS components.

## State and Persistence Behavior
No runtime state is stored. The build graph persists only as generated build-system metadata.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Build scripts can silently omit files or platform-specific sources; target/link changes should be validated on Linux and Windows configurations.

## Test Signals
Validate by configuring and building the old-cpp tree on supported platforms, including test targets and platform-specific source selection.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/AssertFailed.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/AssertFailed.cpp

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `AssertFailed.h`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `AssertFailed.h`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/AssertFailed.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/AssertFailed.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/AssertFailed.h

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 26 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `AssertFailed`. Macros/constants: `MESSMER_CPPUTILS_ASSERT_ASSERTFAILED_H`. Important declarations or call sites include `explicit AssertFailed(std::string message) : _message(std::move(message)) { }`; `const char *what() const throw() override {`; `return _message.c_str();`. Primary includes/dependencies visible in the file include `stdexcept`, `string`, `../macros.h`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `stdexcept`, `string`, `../macros.h`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/AssertFailed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/assert.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/assert.cpp

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 4 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `assert.h`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `assert.h`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/assert.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/assert.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/assert.h

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 76 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `DisableAbortOnFailedAssertionRAII`. Macros/constants: `MESSMER_CPPUTILS_ASSERT_ASSERT_H`, `ASSERT`. Important declarations or call sites include `* This implements an ASSERT(expr, msg) macro.`; `: thread_id_(std::this_thread::get_id()) {`; `~DisableAbortOnFailedAssertionRAII() {`; `if (thread_id_ != std::this_thread::get_id()) {`; `LOG(ERR, "DisableAbortOnFailedAssertionRAII instance must be destructed in the same thread that created it");`; `static int num_instances() {`; `inline std::string format(const char *expr, const std::string &message, const char *file, int line) {`; `std::string result = std::string()+"Assertion ["+expr+"] failed in "+file+":"+std::to_string(line)+": "+message+"\n\n" + backtr...`; `auto msg = format(expr, message, file, line);`; `LOG(ERR, msg);`. CMake commands used here include `if`, `LOG`, `abort`. Primary includes/dependencies visible in the file include `AssertFailed.h`, `iostream`, `thread`, `backtrace.h`, `../logging/logging.h`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `AssertFailed.h`, `iostream`, `thread`, `backtrace.h`, `../logging/logging.h`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/assert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace.h

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 16 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_ASSERT_BACKTRACE_H`. Important declarations or call sites include `std::string backtrace();`; `void showBacktraceOnCrash();`. Primary includes/dependencies visible in the file include `string`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `string`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace_nonwindows.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace_nonwindows.cpp

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 50 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `string backtrace() {`; `str << boost::stacktrace::stacktrace();`; `return str.str();`; `void sigsegv_handler(int) {`; `LOG(ERR, "SIGSEGV\n{}", backtrace());`; `exit(1);`; `void sigill_handler(int) {`; `LOG(ERR, "SIGILL\n{}", backtrace());`; `exit(1);`; `void sigabrt_handler(int) {`. CMake commands used here include `LOG`, `exit`. Primary includes/dependencies visible in the file include `csignal`, `sstream`, `../logging/logging.h`, `cpp-utils/process/SignalHandler.h`, `boost/stacktrace.hpp`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `csignal`, `sstream`, `../logging/logging.h`, `cpp-utils/process/SignalHandler.h`, `boost/stacktrace.hpp`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace_nonwindows.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace_windows.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace_windows.cpp

## Purpose
Implements the cpp-utils assertion failure model, crash backtrace hooks, and thread-local controls used throughout CryFS to convert invariant failures into logs, exceptions, or aborts. This specific file has 187 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SymInitializeRAII`. Macros/constants: `HANDLE_CODE`. Important declarations or call sites include `std::string exception_code_string(DWORD exception_code) {`; `switch (exception_code) {`; `return str.str();`; `, success(::SymInitialize(process, NULL, TRUE)) {`; `~SymInitializeRAII() {`; `::SymCleanup(process);`; `std::string backtrace_to_string(CONTEXT* context_record) {`; `if (!sym.success) {`; `DWORD error = GetLastError();`; `memset(&stack_frame, 0, sizeof(stack_frame));`. CMake commands used here include `switch`, `HANDLE_CODE`, `SymInitializeRAII`, `if`, `memset`, `while`, `GetCurrentThread`, `SymSetOptions`, `LOG`, `return`, `RtlCaptureContext`. Primary includes/dependencies visible in the file include `backtrace.h`, `string`, `sstream`, `../logging/logging.h`, `Dbghelp.h`.

## Control Flow
Assertion paths format file/line/expression context, log the failure, optionally throw `AssertFailed` instead of aborting while the RAII disable counter is active, and crash handlers log platform backtraces before exiting.

## State and Persistence Behavior
State is process-local: assertion abort-disable counters are thread-aware/global in the assertion header, while signal/backtrace registration modifies process signal handling.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `backtrace.h`, `string`, `sstream`, `../logging/logging.h`, `Dbghelp.h`.

## Risks and Edge Cases
Assertion behavior changes process failure mode. Throw-vs-abort counters must be balanced and crash signal handlers must avoid unsafe work beyond logging/exiting.

## Test Signals
Assertion tests should cover throw mode, abort/log formatting in safe harnesses, RAII counter balance, and crash-backtrace registration on each platform.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/assert/backtrace_windows.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash/Hash.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash/Hash.cpp

## Purpose
Provides salted SHA-512 hashing helpers over cpp-utils `Data` buffers and fixed-size salt/digest value types. This specific file has 31 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `Hash hash(const Data& data, Salt salt) {`; `hasher.Update(static_cast<const CryptoPP::byte*>(salt.data()), Salt::BINARY_LENGTH);`; `hasher.Update(static_cast<const CryptoPP::byte*>(data.data()), data.size());`; `Digest digest = Digest::Null();`; `hasher.Final(static_cast<CryptoPP::byte*>(digest.data()));`; `Salt generateSalt() {`; `return Random::PseudoRandom().getFixedSize<8>();`. Primary includes/dependencies visible in the file include `Hash.h`, `cpp-utils/random/Random.h`, `vendor_cryptopp/sha.h`.

## Control Flow
Hashing initializes a Crypto++ SHA-512 instance, feeds salt before data, finalizes into a fixed-size digest, and returns value objects rather than mutable buffers.

## State and Persistence Behavior
No state is persisted by the helper; salt and digest bytes are caller-owned fixed-size values.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `Hash.h`, `cpp-utils/random/Random.h`, `vendor_cryptopp/sha.h`.

## Risks and Edge Cases
Salt must be unique and stored with the digest by callers. Hash comparison is not constant-time here, so authentication decisions should use higher-level crypto where needed.

## Test Signals
Known-vector tests should verify salt+data order, digest size, null/empty data handling, and salt generation length.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash/Hash.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash/Hash.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash/Hash.h

## Purpose
Provides salted SHA-512 hashing helpers over cpp-utils `Data` buffers and fixed-size salt/digest value types. This specific file has 29 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Hash`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_HASH_HASH_H`. Important declarations or call sites include `Salt generateSalt();`; `Hash hash(const cpputils::Data& data, Salt salt);`. Primary includes/dependencies visible in the file include `cpp-utils/data/FixedSizeData.h`, `cpp-utils/data/Data.h`.

## Control Flow
Hashing initializes a Crypto++ SHA-512 instance, feeds salt before data, finalizes into a fixed-size digest, and returns value objects rather than mutable buffers.

## State and Persistence Behavior
No state is persisted by the helper; salt and digest bytes are caller-owned fixed-size values.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `cpp-utils/data/FixedSizeData.h`, `cpp-utils/data/Data.h`.

## Risks and Edge Cases
Salt must be unique and stored with the digest by callers. Hash comparison is not constant-time here, so authentication decisions should use higher-level crypto where needed.

## Test Signals
Known-vector tests should verify salt+data order, digest size, null/empty data handling, and salt generation length.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/hash/Hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/PasswordBasedKDF.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/PasswordBasedKDF.cpp

## Purpose
Provides the password-based key derivation abstraction and the scrypt implementation/parameter serialization used to derive encryption keys from user passwords. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `PasswordBasedKDF.h`.

## Control Flow
Existing-key derivation deserializes saved KDF parameters, derives a key with Crypto++ scrypt, and verifies the parameters were fully consumed. New-key derivation creates salt/settings first and returns both the key and serialized parameters.

## State and Persistence Behavior
KDF parameters persist as serialized `Data` containing N/r/p and salt. Derived keys are in unswappable `EncryptionKey` buffers, while settings for new keys live in the `SCrypt` instance.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `PasswordBasedKDF.h`.

## Risks and Edge Cases
Scrypt parameter compatibility is critical for existing vaults. Weak N/r/p settings or salt reuse reduce password-hardening strength, and deserialization must reject truncated parameter blobs.

## Test Signals
Round-trip serialized scrypt parameters, derive stable existing keys from fixtures, reject malformed parameter data, and verify new-key salt uniqueness.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/PasswordBasedKDF.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/PasswordBasedKDF.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/PasswordBasedKDF.h

## Purpose
Provides the password-based key derivation abstraction and the scrypt implementation/parameter serialization used to derive encryption keys from user passwords. This specific file has 27 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `PasswordBasedKDF`, `KeyResult`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_KDF_PASSWORDBASEDKDF_H`. Important declarations or call sites include `virtual EncryptionKey deriveExistingKey(size_t keySize, const std::string& password, const Data& kdfParameters) = 0;`; `virtual KeyResult deriveNewKey(size_t keySize, const std::string& password) = 0;`. Primary includes/dependencies visible in the file include `../../crypto/symmetric/EncryptionKey.h`, `../../data/Data.h`.

## Control Flow
Existing-key derivation deserializes saved KDF parameters, derives a key with Crypto++ scrypt, and verifies the parameters were fully consumed. New-key derivation creates salt/settings first and returns both the key and serialized parameters.

## State and Persistence Behavior
KDF parameters persist as serialized `Data` containing N/r/p and salt. Derived keys are in unswappable `EncryptionKey` buffers, while settings for new keys live in the `SCrypt` instance.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../../crypto/symmetric/EncryptionKey.h`, `../../data/Data.h`.

## Risks and Edge Cases
Scrypt parameter compatibility is critical for existing vaults. Weak N/r/p settings or salt reuse reduce password-hardening strength, and deserialization must reject truncated parameter blobs.

## Test Signals
Round-trip serialized scrypt parameters, derive stable existing keys from fixtures, reject malformed parameter data, and verify new-key salt uniqueness.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/PasswordBasedKDF.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/SCryptParameters.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/SCryptParameters.cpp

## Purpose
Provides the password-based key derivation abstraction and the scrypt implementation/parameter serialization used to derive encryption keys from user passwords. This specific file has 41 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `Data SCryptParameters::serialize() const {`; `Serializer serializer(_serializedSize());`; `serializer.writeUint64(_n);`; `serializer.writeUint32(_r);`; `serializer.writeUint32(_p);`; `serializer.writeTailData(_salt);`; `return serializer.finished();`; `size_t SCryptParameters::_serializedSize() const {`; `return _salt.size() + sizeof(uint64_t) + sizeof(uint32_t) + sizeof(uint32_t);`; `SCryptParameters SCryptParameters::deserialize(const cpputils::Data &data) {`. Primary includes/dependencies visible in the file include `SCryptParameters.h`.

## Control Flow
Existing-key derivation deserializes saved KDF parameters, derives a key with Crypto++ scrypt, and verifies the parameters were fully consumed. New-key derivation creates salt/settings first and returns both the key and serialized parameters.

## State and Persistence Behavior
KDF parameters persist as serialized `Data` containing N/r/p and salt. Derived keys are in unswappable `EncryptionKey` buffers, while settings for new keys live in the `SCrypt` instance.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `SCryptParameters.h`.

## Risks and Edge Cases
Scrypt parameter compatibility is critical for existing vaults. Weak N/r/p settings or salt reuse reduce password-hardening strength, and deserialization must reject truncated parameter blobs.

## Test Signals
Round-trip serialized scrypt parameters, derive stable existing keys from fixtures, reject malformed parameter data, and verify new-key salt uniqueness.

## File-Specific Notes
- Serialization order is `uint64 n`, `uint32 r`, `uint32 p`, followed by tail salt; existing vault compatibility depends on this exact format.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/SCryptParameters.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/SCryptParameters.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/SCryptParameters.h

## Purpose
Provides the password-based key derivation abstraction and the scrypt implementation/parameter serialization used to derive encryption keys from user passwords. This specific file has 88 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SCryptParameters`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_KDF_KEYCONFIG_H`. Important declarations or call sites include `_n(n), _r(r), _p(p) { }`; `_n(rhs._n), _r(rhs._r), _p(rhs._p) { }`; `if (this == &rhs) {`; `_salt = rhs._salt.copy();`; `const Data &salt() const {`; `size_t n() const {`; `size_t r() const {`; `size_t p() const {`; `cpputils::Data serialize() const;`; `static SCryptParameters deserialize(const cpputils::Data &data);`. CMake commands used here include `SCryptParameters`, `_n`, `if`. Primary includes/dependencies visible in the file include `../../data/Data.h`, `../../data/Serializer.h`, `../../data/Deserializer.h`, `iostream`.

## Control Flow
Existing-key derivation deserializes saved KDF parameters, derives a key with Crypto++ scrypt, and verifies the parameters were fully consumed. New-key derivation creates salt/settings first and returns both the key and serialized parameters.

## State and Persistence Behavior
KDF parameters persist as serialized `Data` containing N/r/p and salt. Derived keys are in unswappable `EncryptionKey` buffers, while settings for new keys live in the `SCrypt` instance.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../../data/Data.h`, `../../data/Serializer.h`, `../../data/Deserializer.h`, `iostream`.

## Risks and Edge Cases
Scrypt parameter compatibility is critical for existing vaults. Weak N/r/p settings or salt reuse reduce password-hardening strength, and deserialization must reject truncated parameter blobs.

## Test Signals
Round-trip serialized scrypt parameters, derive stable existing keys from fixtures, reject malformed parameter data, and verify new-key salt uniqueness.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/SCryptParameters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/Scrypt.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/Scrypt.cpp

## Purpose
Provides the password-based key derivation abstraction and the scrypt implementation/parameter serialization used to derive encryption keys from user passwords. This specific file has 53 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `EncryptionKey _derive(size_t keySize, const std::string& password, const SCryptParameters& kdfParameters) {`; `auto result = EncryptionKey::Null(keySize);`; `if (status != 1) {`; `throw std::runtime_error("Error running scrypt key derivation. Error code: "+std::to_string(status));`; `SCryptParameters _createNewSCryptParameters(const SCryptSettings& settings) {`; `return SCryptParameters(Random::PseudoRandom().get(settings.SALT_LEN), settings.N, settings.r, settings.p);`; `:_settingsForNewKeys(settingsForNewKeys) {`; `EncryptionKey SCrypt::deriveExistingKey(size_t keySize, const std::string& password, const Data& kdfParameters) {`; `SCryptParameters parameters = SCryptParameters::deserialize(kdfParameters);`; `auto key = _derive(keySize, password, parameters);`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `Scrypt.h`, `vendor_cryptopp/scrypt.h`.

## Control Flow
Existing-key derivation deserializes saved KDF parameters, derives a key with Crypto++ scrypt, and verifies the parameters were fully consumed. New-key derivation creates salt/settings first and returns both the key and serialized parameters.

## State and Persistence Behavior
KDF parameters persist as serialized `Data` containing N/r/p and salt. Derived keys are in unswappable `EncryptionKey` buffers, while settings for new keys live in the `SCrypt` instance.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `Scrypt.h`, `vendor_cryptopp/scrypt.h`.

## Risks and Edge Cases
Scrypt parameter compatibility is critical for existing vaults. Weak N/r/p settings or salt reuse reduce password-hardening strength, and deserialization must reject truncated parameter blobs.

## Test Signals
Round-trip serialized scrypt parameters, derive stable existing keys from fixtures, reject malformed parameter data, and verify new-key salt uniqueness.

## File-Specific Notes
- The implementation throws when Crypto++ `DeriveKey` does not return success and asserts the derived key has the requested size.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/Scrypt.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/Scrypt.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/Scrypt.h

## Purpose
Provides the password-based key derivation abstraction and the scrypt implementation/parameter serialization used to derive encryption keys from user passwords. This specific file has 41 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SCryptSettings`, `SCrypt`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_KDF_SCRYPT_H`. Important declarations or call sites include `explicit SCrypt(const SCryptSettings& settingsForNewKeys);`; `EncryptionKey deriveExistingKey(size_t keySize, const std::string& password, const Data& kdfParameters) override;`; `KeyResult deriveNewKey(size_t keySize, const std::string& password) override;`; `DISALLOW_COPY_AND_ASSIGN(SCrypt);`. CMake commands used here include `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `../../macros.h`, `../../random/Random.h`, `../../pointer/unique_ref.h`, `PasswordBasedKDF.h`, `stdexcept`, `SCryptParameters.h`.

## Control Flow
Existing-key derivation deserializes saved KDF parameters, derives a key with Crypto++ scrypt, and verifies the parameters were fully consumed. New-key derivation creates salt/settings first and returns both the key and serialized parameters.

## State and Persistence Behavior
KDF parameters persist as serialized `Data` containing N/r/p and salt. Derived keys are in unswappable `EncryptionKey` buffers, while settings for new keys live in the `SCrypt` instance.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../../macros.h`, `../../random/Random.h`, `../../pointer/unique_ref.h`, `PasswordBasedKDF.h`, `stdexcept`, `SCryptParameters.h`.

## Risks and Edge Cases
Scrypt parameter compatibility is critical for existing vaults. Weak N/r/p settings or salt reuse reduce password-hardening strength, and deserialization must reject truncated parameter blobs.

## Test Signals
Round-trip serialized scrypt parameters, derive stable existing keys from fixtures, reject malformed parameter data, and verify new-key salt uniqueness.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/kdf/Scrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/AEAD_Cipher.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/AEAD_Cipher.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 91 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CryptoPPCipher`, `AEADCipher`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_AEADCIPHER_H_`. Important declarations or call sites include `static constexpr unsigned int ciphertextSize(unsigned int plaintextBlockSize) {`; `static constexpr unsigned int plaintextSize(unsigned int ciphertextBlockSize) {`; `static Data encrypt(const CryptoPP::byte *plaintext, unsigned int plaintextSize, const EncryptionKey &encKey);`; `static boost::optional<Data> decrypt(const CryptoPP::byte *ciphertext, unsigned int ciphertextSize, const EncryptionKey &encKey);`; `Data AEADCipher<CryptoPPCipher, KEYSIZE_, IV_SIZE_, TAG_SIZE_>::encrypt(const CryptoPP::byte *plaintext, unsigned int plaintext...`; `ASSERT(encKey.binaryLength() == AEADCipher::KEYSIZE, "Wrong key size");`; `FixedSizeData<IV_SIZE> iv = Random::PseudoRandom().getFixedSize<IV_SIZE>();`; `encryption.SetKeyWithIV(static_cast<const CryptoPP::byte*>(encKey.data()), encKey.binaryLength(), iv.data(), IV_SIZE);`; `Data ciphertext(ciphertextSize(plaintextSize));`; `iv.ToBinary(ciphertext.data());`. CMake commands used here include `ASSERT`, `if`. Primary includes/dependencies visible in the file include `../../data/FixedSizeData.h`, `../../data/Data.h`, `../../random/Random.h`, `Cipher.h`, `EncryptionKey.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../../data/FixedSizeData.h`, `../../data/Data.h`, `../../random/Random.h`, `Cipher.h`, `EncryptionKey.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

## File-Specific Notes
- The AEAD adapter prefixes the randomly generated IV and appends Crypto++ authentication data, so ciphertext length is plaintext plus IV plus tag.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/AEAD_Cipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/CFB_Cipher.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/CFB_Cipher.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 79 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CFB_Cipher`, `BlockCipher`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_CFBCIPHER_H_`. Important declarations or call sites include `static constexpr unsigned int ciphertextSize(unsigned int plaintextBlockSize) {`; `static constexpr unsigned int plaintextSize(unsigned int ciphertextBlockSize) {`; `static Data encrypt(const CryptoPP::byte *plaintext, unsigned int plaintextSize, const EncryptionKey &encKey);`; `static boost::optional<Data> decrypt(const CryptoPP::byte *ciphertext, unsigned int ciphertextSize, const EncryptionKey &encKey);`; `Data CFB_Cipher<BlockCipher, KeySize>::encrypt(const CryptoPP::byte *plaintext, unsigned int plaintextSize, const EncryptionKey...`; `ASSERT(encKey.binaryLength() == KeySize, "Wrong key size");`; `FixedSizeData<IV_SIZE> iv = Random::PseudoRandom().getFixedSize<IV_SIZE>();`; `auto encryption = typename CryptoPP::CFB_Mode<BlockCipher>::Encryption(static_cast<const CryptoPP::byte*>(encKey.data()), encKe...`; `Data ciphertext(ciphertextSize(plaintextSize));`; `iv.ToBinary(ciphertext.data());`. CMake commands used here include `ASSERT`, `if`. Primary includes/dependencies visible in the file include `../../data/FixedSizeData.h`, `../../data/Data.h`, `../../random/Random.h`, `boost/optional.hpp`, `vendor_cryptopp/modes.h`, `Cipher.h`, `EncryptionKey.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../../data/FixedSizeData.h`, `../../data/Data.h`, `../../random/Random.h`, `boost/optional.hpp`, `vendor_cryptopp/modes.h`, `Cipher.h`, `EncryptionKey.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

## File-Specific Notes
- The CFB adapter prefixes an IV but does not authenticate ciphertext; the source even carries a TODO around decrypt byte counts, making regression tests important.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/CFB_Cipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/Cipher.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/Cipher.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 36 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `X`, `CipherConcept`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_CIPHER_H_`. Important declarations or call sites include `BOOST_CONCEPT_USAGE(CipherConcept) {`; `same_type(UINT32_C(0), X::ciphertextSize(UINT32_C(5)));`; `same_type(UINT32_C(0), X::plaintextSize(UINT32_C(5)));`; `same_type(UINT32_C(0), X::KEYSIZE);`; `same_type(UINT32_C(0), X::STRING_KEYSIZE);`; `typename X::EncryptionKey key = X::EncryptionKey::CreateKey(Random::OSRandom(), X::KEYSIZE);`; `same_type(Data(0), X::encrypt(static_cast<uint8_t*>(nullptr), UINT32_C(0), key));`; `same_type(boost::optional<Data>(Data(0)), X::decrypt(static_cast<uint8_t*>(nullptr), UINT32_C(0), key));`; `template <typename T> void same_type(T const&, T const&);`. CMake commands used here include `BOOST_CONCEPT_USAGE`, `same_type`. Primary includes/dependencies visible in the file include `boost/concept_check.hpp`, `cstdint`, `../../data/Data.h`, `../../random/Random.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `boost/concept_check.hpp`, `cstdint`, `../../data/Data.h`, `../../random/Random.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/Cipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/EncryptionKey.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/EncryptionKey.cpp

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `EncryptionKey.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `EncryptionKey.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/EncryptionKey.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/EncryptionKey.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/EncryptionKey.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 107 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `EncryptionKey`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_ENCRYPTIONKEY_H_`. Important declarations or call sites include `: _keyData(std::move(keyData)) {`; `size_t binaryLength() const {`; `return _keyData->size();`; `size_t stringLength() const {`; `return 2 * binaryLength();`; `static EncryptionKey Null(size_t keySize) {`; `data->FillWithZeroes();`; `return EncryptionKey(std::move(data));`; `static EncryptionKey FromString(const std::string& keyData) {`; `EncryptionKey key(std::move(data));`. CMake commands used here include `EncryptionKey`, `ASSERT`. Primary includes/dependencies visible in the file include `cpp-utils/data/FixedSizeData.h`, `memory`, `cpp-utils/system/memory.h`, `cpp-utils/random/RandomGenerator.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `cpp-utils/data/FixedSizeData.h`, `memory`, `cpp-utils/system/memory.h`, `cpp-utils/random/RandomGenerator.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

## File-Specific Notes
- `EncryptionKey` stores key bytes in `Data` allocated through `UnswappableAllocator` and shares that memory through `shared_ptr` to avoid casual copies.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/EncryptionKey.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/GCM_Cipher.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/GCM_Cipher.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 16 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_GCMCIPHER_H_`. Primary includes/dependencies visible in the file include `AEAD_Cipher.h`, `vendor_cryptopp/gcm.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `AEAD_Cipher.h`, `vendor_cryptopp/gcm.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/GCM_Cipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/ciphers.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/ciphers.cpp

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 36 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `DEFINE_CIPHER`. Important declarations or call sites include `DEFINE_CIPHER(XChaCha20Poly1305);`; `DEFINE_CIPHER(AES256_GCM);`; `DEFINE_CIPHER(AES256_CFB);`; `DEFINE_CIPHER(AES128_GCM);`; `DEFINE_CIPHER(AES128_CFB);`; `DEFINE_CIPHER(Twofish256_GCM);`; `DEFINE_CIPHER(Twofish256_CFB);`; `DEFINE_CIPHER(Twofish128_GCM);`; `DEFINE_CIPHER(Twofish128_CFB);`; `DEFINE_CIPHER(Serpent256_GCM);`. CMake commands used here include `DEFINE_CIPHER`. Primary includes/dependencies visible in the file include `ciphers.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `ciphers.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/ciphers.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/ciphers.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/ciphers.h

## Purpose
Defines symmetric cipher adapters over Crypto++ primitives with a uniform CryFS `CipherConcept` interface for key sizing, encryption, and decryption. This specific file has 64 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `InstanceName`. Macros/constants: `MESSMER_CPPUTILS_CRYPTO_SYMMETRIC_CIPHERS_H_`, `SINGLE_ARG`, `DECLARE_CIPHER`. Important declarations or call sites include `BOOST_CONCEPT_ASSERT((CipherConcept<InstanceName>));                               \`; `DECLARE_CIPHER(XChaCha20Poly1305, "xchacha20-poly1305", SINGLE_ARG(AEADCipher<CryptoPP::XChaCha20Poly1305, 32, 24, 16>));`; `static_assert(32 == CryptoPP::AES::MAX_KEYLENGTH, "If AES offered larger keys, we should offer a variant with it");`; `DECLARE_CIPHER(AES256_GCM, "aes-256-gcm", SINGLE_ARG(GCM_Cipher<CryptoPP::AES, 32>));`; `DECLARE_CIPHER(AES256_CFB, "aes-256-cfb", SINGLE_ARG(CFB_Cipher<CryptoPP::AES, 32>));`; `DECLARE_CIPHER(AES128_GCM, "aes-128-gcm", SINGLE_ARG(GCM_Cipher<CryptoPP::AES, 16>));`; `DECLARE_CIPHER(AES128_CFB, "aes-128-cfb", SINGLE_ARG(CFB_Cipher<CryptoPP::AES, 16>));`; `static_assert(32 == CryptoPP::Twofish::MAX_KEYLENGTH, "If Twofish offered larger keys, we should offer a variant with it");`; `DECLARE_CIPHER(Twofish256_GCM, "twofish-256-gcm", SINGLE_ARG(GCM_Cipher<CryptoPP::Twofish, 32>));`; `DECLARE_CIPHER(Twofish256_CFB, "twofish-256-cfb", SINGLE_ARG(CFB_Cipher<CryptoPP::Twofish, 32>));`. CMake commands used here include `BOOST_CONCEPT_ASSERT`, `DECLARE_CIPHER`, `static_assert`. Primary includes/dependencies visible in the file include `vendor_cryptopp/aes.h`, `vendor_cryptopp/twofish.h`, `vendor_cryptopp/serpent.h`, `vendor_cryptopp/cast.h`, `vendor_cryptopp/mars.h`, `vendor_cryptopp/chachapoly.h`, `GCM_Cipher.h`, `CFB_Cipher.h`.

## Control Flow
Encryption validates key length, generates an IV with `Random::PseudoRandom`, prefixes IV bytes to the ciphertext, and delegates transformation/authentication to Crypto++. Decryption parses the IV prefix and returns `boost::none` on malformed or unauthenticated input.

## State and Persistence Behavior
Cipher functions are stateless apart from generated IV bytes embedded into ciphertext. Authentication tags or IV prefixes persist only inside the returned `Data` buffer.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `vendor_cryptopp/aes.h`, `vendor_cryptopp/twofish.h`, `vendor_cryptopp/serpent.h`, `vendor_cryptopp/cast.h`, `vendor_cryptopp/mars.h`, `vendor_cryptopp/chachapoly.h`, `GCM_Cipher.h`, `CFB_Cipher.h`.

## Risks and Edge Cases
IV uniqueness and authentication handling are security-sensitive. CFB variants provide confidentiality but not authentication, while AEAD callers must treat `boost::none` as an integrity failure.

## Test Signals
Round-trip encryption/decryption, wrong-key failure for AEAD, malformed short ciphertext, key-size assertion paths, zero-length plaintext, and CFB non-authentication expectations.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/ciphers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils/FakeAuthenticatedCipher.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils/FakeAuthenticatedCipher.cpp

## Purpose
Provides a deterministic fake authenticated cipher for tests that need cipher-like behavior without relying on real cryptographic transformations. This specific file has 8 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `FakeAuthenticatedCipher.h`.

## Control Flow
The fake cipher derives deterministic output from the fake key and payload sizes, appends/checks an authentication marker, and exposes the same static API shape as real ciphers for concept-based tests.

## State and Persistence Behavior
The fake cipher keeps no global state; deterministic fake keys and serialized test payloads are created in memory.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `FakeAuthenticatedCipher.h`.

## Risks and Edge Cases
The fake cipher is intentionally not secure and must remain test-only. Accidentally linking it into production paths would invalidate crypto guarantees.

## Test Signals
Use it only in tests that verify authentication-failure plumbing, serialization sizes, and deterministic fake key behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils/FakeAuthenticatedCipher.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils/FakeAuthenticatedCipher.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils/FakeAuthenticatedCipher.h

## Purpose
Provides a deterministic fake authenticated cipher for tests that need cipher-like behavior without relying on real cryptographic transformations. This specific file has 122 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `FakeKey`, `FakeAuthenticatedCipher`. Macros/constants: `MESSMER_CPPUTILS_TEST_CRYPTO_SYMMETRIC_TESTUTILS_FAKEAUTHENTICATEDCIPHER_H_`. Important declarations or call sites include `static FakeKey FromString(const std::string& keyData) {`; `size_t binaryLength() const {`; `return sizeof(uint64_t);`; `static FakeKey CreateKey(RandomGenerator &randomGenerator, size_t keySize) {`; `ASSERT(keySize == sizeof(uint64_t), "Wrong key size");`; `auto data = randomGenerator.getFixedSize<sizeof(uint64_t)>();`; `BOOST_CONCEPT_ASSERT((CipherConcept<FakeAuthenticatedCipher>));`; `static constexpr unsigned int KEYSIZE = sizeof(uint64_t);`; `static EncryptionKey Key1() {`; `static EncryptionKey Key2() {`. CMake commands used here include `ASSERT`, `BOOST_CONCEPT_ASSERT`, `_xor`, `if`, `for`. Primary includes/dependencies visible in the file include `cpp-utils/crypto/symmetric/Cipher.h`, `cpp-utils/data/FixedSizeData.h`, `cpp-utils/data/Data.h`, `cpp-utils/random/RandomGenerator.h`, `random`, `cpp-utils/data/SerializationHelper.h`.

## Control Flow
The fake cipher derives deterministic output from the fake key and payload sizes, appends/checks an authentication marker, and exposes the same static API shape as real ciphers for concept-based tests.

## State and Persistence Behavior
The fake cipher keeps no global state; deterministic fake keys and serialized test payloads are created in memory.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cpp-utils/crypto/symmetric/Cipher.h`, `cpp-utils/data/FixedSizeData.h`, `cpp-utils/data/Data.h`, `cpp-utils/random/RandomGenerator.h`, `random`, `cpp-utils/data/SerializationHelper.h`.

## Risks and Edge Cases
The fake cipher is intentionally not secure and must remain test-only. Accidentally linking it into production paths would invalidate crypto guarantees.

## Test Signals
Use it only in tests that verify authentication-failure plumbing, serialization sizes, and deterministic fake key behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/crypto/symmetric/testutils/FakeAuthenticatedCipher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Data.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Data.cpp

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 73 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `optional<Data> Data::LoadFromFile(const bf::path &filepath) {`; `ifstream file(filepath.string().c_str(), ios::binary);`; `if (!file.good()) {`; `optional<Data> result(LoadFromStream(file));`; `if (!file.good()) {`; `throw std::runtime_error("Error reading from file");`; `std::streampos Data::_getStreamSize(istream &stream) {`; `auto current_pos = stream.tellg();`; `stream.seekg(0, stream.end);`; `auto endpos = stream.tellg();`. CMake commands used here include `if`, `ASSERT`. Primary includes/dependencies visible in the file include `Data.h`, `stdexcept`, `vendor_cryptopp/hex.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Data.h`, `stdexcept`, `vendor_cryptopp/hex.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Data.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Data.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Data.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 205 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Allocator`, `DefaultAllocator`, `Data`. Macros/constants: `MESSMER_CPPUTILS_DATA_DATA_H_`. Important declarations or call sites include `virtual void* allocate(size_t size) = 0;`; `virtual void free(void* ptr, size_t size) = 0;`; `void* allocate(size_t size) override {`; `return std::malloc((size == 0) ? 1 : size);`; `void free(void* data, size_t /*size*/) override {`; `std::free(data);`; `explicit Data(size_t size, unique_ref<Allocator> allocator = make_unique_ref<DefaultAllocator>());`; `~Data();`; `Data copy() const;`; `Data copyAndRemovePrefix(size_t prefixSize) const;`. CMake commands used here include `Data`, `DISALLOW_COPY_AND_ASSIGN`, `if`, `_free`, `ASSERT`, `StoreToStream`. Primary includes/dependencies visible in the file include `cstdlib`, `boost/filesystem/path.hpp`, `boost/optional.hpp`, `../macros.h`, `memory`, `fstream`, `../assert/assert.h`, `../pointer/unique_ref.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cstdlib`, `boost/filesystem/path.hpp`, `boost/optional.hpp`, `../macros.h`, `memory`, `fstream`, `../assert/assert.h`, `../pointer/unique_ref.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

## File-Specific Notes
- `Data` is move-only, allocator-backed, and exposes raw pointers; `dataOffset` is convenient but trusts callers to respect bounds.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataFixture.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataFixture.cpp

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 25 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `Data DataFixture::generate(size_t size, unsigned long long int seed) {`; `Data result(size);`; `for(size_t i=0; i<size/sizeof(unsigned long long int); ++i) {`; `serialize<unsigned long long int>(result.dataOffset(i*sizeof(unsigned long long int)), val);`; `uint64_t alreadyWritten = (size/sizeof(unsigned long long int))*sizeof(unsigned long long int);`; `serialize<unsigned char>(result.dataOffset(alreadyWritten + i), remainingBytes[i]);`. CMake commands used here include `for`. Primary includes/dependencies visible in the file include `DataFixture.h`, `SerializationHelper.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `DataFixture.h`, `SerializationHelper.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataFixture.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataFixture.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataFixture.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 28 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `DataFixture`. Macros/constants: `MESSMER_CPPUTILS_DATA_DATAFIXTURE_H_`. Important declarations or call sites include `static Data generate(size_t size, unsigned long long int seed = 1);`; `template<size_t SIZE> static FixedSizeData<SIZE> generateFixedSize(long long int seed = 1);`; `template<size_t SIZE> FixedSizeData<SIZE> DataFixture::generateFixedSize(long long int seed) {`; `Data data = generate(SIZE, seed);`; `auto result = FixedSizeData<SIZE>::Null();`; `std::memcpy(result.data(), data.data(), SIZE);`. Primary includes/dependencies visible in the file include `Data.h`, `FixedSizeData.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Data.h`, `FixedSizeData.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataFixture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataUtils.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataUtils.cpp

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 13 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `Data resize(const Data& data, size_t newSize) {`; `Data newData(newSize);`; `newData.FillWithZeroes(); // TODO Only fill region after copied old data with zeroes`; `std::memcpy(newData.data(), data.data(), std::min(newData.size(), data.size()));`. Primary includes/dependencies visible in the file include `DataUtils.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `DataUtils.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataUtils.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataUtils.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataUtils.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 18 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_DATA_DATAUTILS_H`. Important declarations or call sites include `Data resize(const Data& data, size_t newSize);`. Primary includes/dependencies visible in the file include `Data.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Data.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/DataUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Deserializer.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Deserializer.cpp

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `Deserializer.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Deserializer.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Deserializer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Deserializer.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Deserializer.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 151 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Deserializer`. Macros/constants: `MESSMER_CPPUTILS_DATA_DESERIALIZER_H`. Important declarations or call sites include `Deserializer(const Data *source);`; `bool readBool();`; `uint8_t readUint8();`; `int8_t readInt8();`; `uint16_t readUint16();`; `int16_t readInt16();`; `uint32_t readUint32();`; `int32_t readInt32();`; `uint64_t readUint64();`; `int64_t readInt64();`. CMake commands used here include `Deserializer`, `DISALLOW_COPY_AND_ASSIGN`, `if`, `static_assert`, `_readData`. Primary includes/dependencies visible in the file include `Data.h`, `../macros.h`, `../assert/assert.h`, `FixedSizeData.h`, `SerializationHelper.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Data.h`, `../macros.h`, `../assert/assert.h`, `FixedSizeData.h`, `SerializationHelper.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

## File-Specific Notes
- Deserializer cursor advancement is strict: primitive and data reads throw on overflow and `finished` throws when trailing bytes remain.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Deserializer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/FixedSizeData.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/FixedSizeData.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 159 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `FixedSizeData`. Macros/constants: `MESSMER_CPPUTILS_DATA_FIXEDSIZEDATA_H_`. Important declarations or call sites include `static FixedSizeData<SIZE> Null();`; `static FixedSizeData<SIZE> FromString(const std::string &data);`; `std::string ToString() const;`; `static FixedSizeData<SIZE> FromBinary(const void *source);`; `void ToBinary(void *target) const;`; `const unsigned char *data() const;`; `unsigned char *data();`; `FixedSizeData<size> take() const;`; `FixedSizeData<SIZE - size> drop() const;`; `FixedSizeData() : _data() {}`. CMake commands used here include `FixedSizeData`, `ASSERT`, `static_assert`. Primary includes/dependencies visible in the file include `vendor_cryptopp/hex.h`, `string`, `array`, `cstring`, `../assert/assert.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `vendor_cryptopp/hex.h`, `string`, `array`, `cstring`, `../assert/assert.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/FixedSizeData.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/SerializationHelper.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/SerializationHelper.cpp

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `SerializationHelper.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `SerializationHelper.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/SerializationHelper.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/SerializationHelper.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/SerializationHelper.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 79 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `DataType`, `Enable`, `serialize`, `deserialize`. Macros/constants: `MESSMER_CPPUTILS_DATA_SERIALIZATIONHELPER_H`. Important declarations or call sites include `constexpr bool greater_than(size_t lhs, size_t rhs) {`; `static_assert(std::is_pod<DataType>::value, "Can only serialize PODs");`; `static void call(void *dst, const DataType &obj) {`; `static_assert(std::is_pod<DataType>::value, "Can only serialize PODs");`; `static void call(void *dst, const DataType &obj) {`; `std::memcpy(dst, &obj, sizeof(DataType));`; `static_assert(std::is_pod<DataType>::value, "Can only serialize PODs");`; `static DataType call(const void *src) {`; `static_assert(std::is_pod<DataType>::value, "Can only deserialize PODs");`; `static DataType call(const void *src) {`. CMake commands used here include `static_assert`. Primary includes/dependencies visible in the file include `type_traits`, `cstring`, `cstdint`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `type_traits`, `cstring`, `cstdint`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/SerializationHelper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Serializer.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Serializer.cpp

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `Serializer.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Serializer.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Serializer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Serializer.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Serializer.h

## Purpose
Implements binary buffer ownership, fixed-size byte values, serialization, deserialization, and deterministic test data helpers used across CryFS. This specific file has 149 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Serializer`. Macros/constants: `MESSMER_CPPUTILS_DATA_SERIALIZER_H`. Important declarations or call sites include `Serializer(size_t size);`; `void writeBool(bool value);`; `void writeUint8(uint8_t value);`; `void writeInt8(int8_t value);`; `void writeUint16(uint16_t value);`; `void writeInt16(int16_t value);`; `void writeUint32(uint32_t value);`; `void writeInt32(int32_t value);`; `void writeUint64(uint64_t value);`; `void writeInt64(int64_t value);`. CMake commands used here include `Serializer`, `DISALLOW_COPY_AND_ASSIGN`, `writeUint8`, `if`, `writeUint64`, `_writeData`, `ASSERT`. Primary includes/dependencies visible in the file include `Data.h`, `FixedSizeData.h`, `../macros.h`, `../assert/assert.h`, `string`, `SerializationHelper.h`.

## Control Flow
The data helpers allocate owned buffers, copy or move them explicitly, encode primitive values in a fixed byte order, advance serializer/deserializer cursors, and throw on overflow or unused trailing bytes.

## State and Persistence Behavior
Buffers own heap memory through an allocator; move operations invalidate the source. Serialized bytes are persisted only when callers store the returned `Data` or write it to streams/files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Data.h`, `FixedSizeData.h`, `../macros.h`, `../assert/assert.h`, `string`, `SerializationHelper.h`.

## Risks and Edge Cases
Bounds checks are partly assertion-based and partly exception-based. Raw `dataOffset` does not independently validate offsets, so caller misuse can corrupt memory.

## Test Signals
Cover move/copy ownership, file/stream load/store, hex string conversion, serializer/deserializer overflow, tail data, bool validation, and endian compatibility fixtures.

## File-Specific Notes
- Serializer preallocates the exact output size and refuses both overflow and underfilled output in `finished`.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/data/Serializer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/either.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/either.h

## Purpose
Provides a small CryFS C++ utility component. This specific file has 242 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Left`, `Right`, `either`, `Head`, `class`. Macros/constants: `MESSMER_CPPUTILS_EITHER_H`. Important declarations or call sites include `: _side(Side::left) {`; `_construct_left(std::forward<Head>(construct_left_head_arg), std::forward<Tail>(construct_left_tail_args)...);`; `: _side(Side::right) {`; `_construct_right(std::forward<Head>(construct_right_head_arg), std::forward<Tail>(construct_right_tail_args)...);`; `: _side(rhs._side) {`; `if(_side == Side::left) {`; `_construct_left(rhs._left);  // NOLINT(cppcoreguidelines-pro-type-union-access)`; `_construct_right(rhs._right);  // NOLINT(cppcoreguidelines-pro-type-union-access)`; `: _side(rhs._side) {`; `if(_side == Side::left) {`. CMake commands used here include `either`, `_construct_left`, `_construct_right`, `if`, `_destruct`, `new`. Primary includes/dependencies visible in the file include `boost/optional.hpp`, `iostream`, `assert/assert.h`.

## Control Flow
Control flow is local to the inline helpers or small translation unit and follows the surrounding cpp-utils conventions.

## State and Persistence Behavior
State behavior follows the directly visible member fields and is process-local unless delegated to filesystem/system APIs.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `boost/optional.hpp`, `iostream`, `assert/assert.h`.

## Risks and Edge Cases
Risks are local and should be tested through the module that consumes this helper.

## Test Signals
Use focused unit tests at the consuming module boundary.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/either.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/Console.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/Console.cpp

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 3 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `Console.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Console.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/Console.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/Console.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/Console.h

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 27 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Console`. Macros/constants: `MESSMER_CPPUTILS_IO_CONSOLE_H`. Important declarations or call sites include `virtual unsigned int ask(const std::string &question, const std::vector<std::string> &options) = 0;`; `virtual bool askYesNo(const std::string &question, bool defaultValue) = 0; // NoninteractiveConsole will just return the defaul...`; `virtual void print(const std::string &output) = 0;`; `virtual std::string askPassword(const std::string &question) = 0;`. Primary includes/dependencies visible in the file include `string`, `vector`, `iostream`, `boost/optional.hpp`, `../macros.h`, `../pointer/unique_ref.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `string`, `vector`, `iostream`, `boost/optional.hpp`, `../macros.h`, `../pointer/unique_ref.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/Console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/DontEchoStdinToStdoutRAII.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/DontEchoStdinToStdoutRAII.cpp

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 85 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `DontEchoStdinToStdoutRAII_`. Important declarations or call sites include `tcgetattr(STDIN_FILENO, &_old_state);`; `tcsetattr(STDIN_FILENO, TCSANOW, &new_state);`; `tcsetattr(STDIN_FILENO, TCSANOW, &_old_state);`; `DISALLOW_COPY_AND_ASSIGN(DontEchoStdinToStdoutRAII_);`; `HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);`; `GetConsoleMode(hStdin, &_old_state);`; `SetConsoleMode(hStdin, _old_state & (~ENABLE_ECHO_INPUT));`; `HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);`; `SetConsoleMode(hStdin, _old_state);`; `DISALLOW_COPY_AND_ASSIGN(DontEchoStdinToStdoutRAII_);`. CMake commands used here include `DontEchoStdinToStdoutRAII_`, `tcgetattr`, `tcsetattr`, `DISALLOW_COPY_AND_ASSIGN`, `GetConsoleMode`, `SetConsoleMode`. Primary includes/dependencies visible in the file include `DontEchoStdinToStdoutRAII.h`, `termios.h`, `unistd.h`, `windows.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `DontEchoStdinToStdoutRAII.h`, `termios.h`, `unistd.h`, `windows.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/DontEchoStdinToStdoutRAII.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/DontEchoStdinToStdoutRAII.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/DontEchoStdinToStdoutRAII.h

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 37 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `in`, `DontEchoStdinToStdoutRAII_`, `DontEchoStdinToStdoutRAII`. Macros/constants: `MESSMER_CPPUTILS_IO_DONTECHOSTDINTOSTDOUTRAII_H`. Important declarations or call sites include `DontEchoStdinToStdoutRAII();`; `~DontEchoStdinToStdoutRAII();`; `DISALLOW_COPY_AND_ASSIGN(DontEchoStdinToStdoutRAII);`. CMake commands used here include `DontEchoStdinToStdoutRAII`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `cpp-utils/pointer/unique_ref.h`, `../macros.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cpp-utils/pointer/unique_ref.h`, `../macros.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/DontEchoStdinToStdoutRAII.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/IOStreamConsole.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/IOStreamConsole.cpp

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 114 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `IOStreamConsole::IOStreamConsole(): IOStreamConsole(std::cout, std::cin) {`; `IOStreamConsole::IOStreamConsole(ostream &output, istream &input): _output(output), _input(input) {`; `optional<int> IOStreamConsole::_parseInt(const string &str) {`; `boost::algorithm::trim(trimmed);`; `int parsed = std::stoi(str);`; `if (std::to_string(parsed) != trimmed) {`; `} catch (const std::invalid_argument &e) {`; `} catch (const std::out_of_range &e) {`; `function<optional<unsigned int>(const string &input)> IOStreamConsole::_parseUIntWithMinMax(unsigned int min, unsigned int max) {`; `optional<int> parsed = _parseInt(input);`. CMake commands used here include `if`, `getline`, `for`, `ASSERT`. Primary includes/dependencies visible in the file include `IOStreamConsole.h`, `boost/algorithm/string/trim.hpp`, `DontEchoStdinToStdoutRAII.h`, `cpp-utils/assert/assert.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `IOStreamConsole.h`, `boost/algorithm/string/trim.hpp`, `DontEchoStdinToStdoutRAII.h`, `cpp-utils/assert/assert.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/IOStreamConsole.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/IOStreamConsole.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/IOStreamConsole.h

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 32 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `IOStreamConsole`. Macros/constants: `MESSMER_CPPUTILS_IO_IOSTREAMCONSOLE_H`. Important declarations or call sites include `IOStreamConsole();`; `IOStreamConsole(std::ostream &output, std::istream &input);`; `unsigned int ask(const std::string &question, const std::vector<std::string> &options) override;`; `bool askYesNo(const std::string &question, bool defaultValue) override;`; `void print(const std::string &output) override;`; `std::string askPassword(const std::string &question) override;`; `Return _askForChoice(const std::string &question, std::function<boost::optional<Return> (const std::string&)> parse);`; `static std::function<boost::optional<bool>(const std::string &input)> _parseYesNo();`; `static std::function<boost::optional<unsigned int>(const std::string &input)> _parseUIntWithMinMax(unsigned int min, unsigned i...`; `static boost::optional<int> _parseInt(const std::string &str);`. CMake commands used here include `IOStreamConsole`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `Console.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Console.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/IOStreamConsole.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/NoninteractiveConsole.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/NoninteractiveConsole.cpp

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 29 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `NoninteractiveConsole::NoninteractiveConsole(shared_ptr<Console> baseConsole): _baseConsole(std::move(baseConsole)) {`; `bool NoninteractiveConsole::askYesNo(const string &/*question*/, bool defaultValue) {`; `void NoninteractiveConsole::print(const std::string &output) {`; `_baseConsole->print(output);`; `unsigned int NoninteractiveConsole::ask(const string &/*question*/, const vector<string> &/*options*/) {`; `throw std::logic_error("Tried to ask a multiple choice question in noninteractive mode");`; `string NoninteractiveConsole::askPassword(const string &question) {`; `return _baseConsole->askPassword(question);`. Primary includes/dependencies visible in the file include `NoninteractiveConsole.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `NoninteractiveConsole.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/NoninteractiveConsole.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/NoninteractiveConsole.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/NoninteractiveConsole.h

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 27 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `NoninteractiveConsole`. Macros/constants: `MESSMER_CPPUTILS_IO_NONINTERACTIVECONSOLE_H`. Important declarations or call sites include `NoninteractiveConsole(std::shared_ptr<Console> baseConsole);`; `unsigned int ask(const std::string &question, const std::vector<std::string> &options) override;`; `bool askYesNo(const std::string &question, bool defaultValue) override;`; `void print(const std::string &output) override;`; `std::string askPassword(const std::string &question) override;`; `DISALLOW_COPY_AND_ASSIGN(NoninteractiveConsole);`. CMake commands used here include `NoninteractiveConsole`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `Console.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Console.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/NoninteractiveConsole.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/ProgressBar.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/ProgressBar.cpp

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 36 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `: ProgressBar(std::make_shared<IOStreamConsole>(), preamble, max_value) {}`; `, _lastPercentage(std::numeric_limits<decltype(_lastPercentage)>::max()) {`; `ASSERT(_max_value > 0, "Progress bar can't handle max_value of 0");`; `_console->print("\n");`; `update(0);`; `void ProgressBar::update(uint64_t value) {`; `if (percentage != _lastPercentage) {`; `_console->print(_preamble + std::to_string(percentage) + "%");`. CMake commands used here include `ASSERT`, `update`, `if`. Primary includes/dependencies visible in the file include `ProgressBar.h`, `iostream`, `limits`, `mutex`, `IOStreamConsole.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `ProgressBar.h`, `iostream`, `limits`, `mutex`, `IOStreamConsole.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/ProgressBar.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/ProgressBar.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/ProgressBar.h

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 32 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ProgressBar`. Macros/constants: `MESSMER_CPPUTILS_IO_PROGRESSBAR_H`. Important declarations or call sites include `explicit ProgressBar(std::shared_ptr<Console> console, const char* preamble, uint64_t max_value);`; `explicit ProgressBar(const char* preamble, uint64_t max_value);`; `void update(uint64_t value);`; `DISALLOW_COPY_AND_ASSIGN(ProgressBar);`. CMake commands used here include `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `cpp-utils/macros.h`, `string`, `memory`, `Console.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cpp-utils/macros.h`, `string`, `memory`, `Console.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/ProgressBar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/pipestream.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/pipestream.cpp

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `pipestream.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `pipestream.h`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/pipestream.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/pipestream.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/pipestream.h

## Purpose
Implements console, progress, terminal echo, and pipe-stream helpers for command-line interaction and subprocess-style stream integration. This specific file has 157 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `that`, `pipestream`. Macros/constants: `MESSMER_CPPUTILS_PIPESTREAM_H`. Important declarations or call sites include `*  std::istream istream(&pipe);`; `*  std::ostream ostream(&pipe);`; `this->setp(&this->d_out[0], &this->d_out[0] + this->d_out.size() - 1);`; `this->setg(&this->d_in[0], &this->d_in[0], &this->d_in[0]);`; `void close() {`; `std::unique_lock <std::mutex> lock(this->d_mutex);`; `while (this->pbase() != this->pptr()) {`; `this->internal_sync(lock);`; `this->d_condition.notify_all();`; `int_type underflow() override {`. CMake commands used here include `pipestream`, `while`, `if`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `algorithm`, `condition_variable`, `iostream`, `mutex`, `stdexcept`, `streambuf`, `string`, `thread`, `../macros.h`.

## Control Flow
Console flows read or write through injected streams or platform terminal controls; progress and pipe helpers translate incremental updates into stream output while keeping state in memory.

## State and Persistence Behavior
Console objects retain stream references or small flags; terminal echo and progress state is process/session-local and not persisted.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `algorithm`, `condition_variable`, `iostream`, `mutex`, `stdexcept`, `streambuf`, `string`, `thread`.

## Risks and Edge Cases
Terminal state must be restored on exceptions, and noninteractive console behavior must not block waiting for user input.

## Test Signals
Test interactive and noninteractive console paths with stream fakes, echo restoration, progress rendering boundaries, and pipe stream read/write behavior.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/io/pipestream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/CombinedLock.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/CombinedLock.h

## Purpose
Implements small synchronization helpers used where CryFS needs named locks, condition barriers, or coordinated release/reacquire behavior. This specific file has 37 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `is`, `CombinedLock`. Macros/constants: `MESSMER_CPPUTILS_LOCK_COMBINEDLOCK_H`. Important declarations or call sites include `: _outer(outer), _inner(inner) {`; `void lock() {`; `_outer->lock();`; `_inner->lock();`; `void unlock() {`; `_inner->unlock();`; `_outer->unlock();`; `DISALLOW_COPY_AND_ASSIGN(CombinedLock);`. CMake commands used here include `CombinedLock`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `../macros.h`.

## Control Flow
Lock helpers acquire internal mutexes, wait on condition variables when a named lock is busy, and release with notification. Combined locking temporarily releases and reacquires multiple locks in a controlled order.

## State and Persistence Behavior
Synchronization state is in-memory only: locked names, counters, mutexes, and condition variables are lost at process exit.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `../macros.h`.

## Risks and Edge Cases
Named-lock pools rely on callers releasing exactly once. Destructor assertions catch leaks late; missing release can deadlock waiters.

## Test Signals
Test contended same-name locks, release notification, destructor leak assertions, combined-lock wait behavior, and condition barrier wakeups.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/CombinedLock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/ConditionBarrier.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/ConditionBarrier.h

## Purpose
Implements small synchronization helpers used where CryFS needs named locks, condition barriers, or coordinated release/reacquire behavior. This specific file has 43 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ConditionBarrier`. Macros/constants: `MESSMER_CPPUTILS_LOCK_CONDITIONBARRIER_H`. Important declarations or call sites include `ConditionBarrier() :_mutex(), _cv(), _triggered(false) {`; `void wait() {`; `std::unique_lock<std::mutex> lock(_mutex);`; `void release() {`; `std::unique_lock<std::mutex> lock(_mutex);`; `_cv.notify_all();`; `DISALLOW_COPY_AND_ASSIGN(ConditionBarrier);`. CMake commands used here include `ConditionBarrier`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `mutex`, `condition_variable`, `../macros.h`.

## Control Flow
Lock helpers acquire internal mutexes, wait on condition variables when a named lock is busy, and release with notification. Combined locking temporarily releases and reacquires multiple locks in a controlled order.

## State and Persistence Behavior
Synchronization state is in-memory only: locked names, counters, mutexes, and condition variables are lost at process exit.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `mutex`, `condition_variable`, `../macros.h`.

## Risks and Edge Cases
Named-lock pools rely on callers releasing exactly once. Destructor assertions catch leaks late; missing release can deadlock waiters.

## Test Signals
Test contended same-name locks, release notification, destructor leak assertions, combined-lock wait behavior, and condition barrier wakeups.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/ConditionBarrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/LockPool.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/LockPool.cpp

## Purpose
Implements small synchronization helpers used where CryFS needs named locks, condition barriers, or coordinated release/reacquire behavior. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `LockPool.h`.

## Control Flow
Lock helpers acquire internal mutexes, wait on condition variables when a named lock is busy, and release with notification. Combined locking temporarily releases and reacquires multiple locks in a controlled order.

## State and Persistence Behavior
Synchronization state is in-memory only: locked names, counters, mutexes, and condition variables are lost at process exit.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `LockPool.h`.

## Risks and Edge Cases
Named-lock pools rely on callers releasing exactly once. Destructor assertions catch leaks late; missing release can deadlock waiters.

## Test Signals
Test contended same-name locks, release notification, destructor leak assertions, combined-lock wait behavior, and condition barrier wakeups.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/LockPool.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/LockPool.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/LockPool.h

## Purpose
Implements small synchronization helpers used where CryFS needs named locks, condition barriers, or coordinated release/reacquire behavior. This specific file has 91 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `LockName`, `LockPool`, `OuterLock`. Macros/constants: `MESSMER_CPPUTILS_LOCK_LOCKPOOL_H`. Important declarations or call sites include `LockPool();`; `~LockPool();`; `void lock(const LockName &lockName);`; `void lock(const LockName &lockName, std::unique_lock<std::mutex> *lockToFreeWhileWaiting);`; `void release(const LockName &lockName);`; `bool _isLocked(const LockName &lockName) const;`; `template<class OuterLock> void _lock(const LockName &lockName, OuterLock *lockToFreeWhileWaiting);`; `DISALLOW_COPY_AND_ASSIGN(LockPool);`; `inline LockPool<LockName>::LockPool(): _lockedLocks(), _mutex(), _cv() {}`; `inline LockPool<LockName>::~LockPool() {`. CMake commands used here include `LockPool`, `DISALLOW_COPY_AND_ASSIGN`, `ASSERT`, `_lock`, `if`. Primary includes/dependencies visible in the file include `mutex`, `condition_variable`, `vector`, `algorithm`, `../assert/assert.h`, `../macros.h`, `CombinedLock.h`.

## Control Flow
Lock helpers acquire internal mutexes, wait on condition variables when a named lock is busy, and release with notification. Combined locking temporarily releases and reacquires multiple locks in a controlled order.

## State and Persistence Behavior
Synchronization state is in-memory only: locked names, counters, mutexes, and condition variables are lost at process exit.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `mutex`, `condition_variable`, `vector`, `algorithm`, `../assert/assert.h`, `../macros.h`, `CombinedLock.h`.

## Risks and Edge Cases
Named-lock pools rely on callers releasing exactly once. Destructor assertions catch leaks late; missing release can deadlock waiters.

## Test Signals
Test contended same-name locks, release notification, destructor leak assertions, combined-lock wait behavior, and condition barrier wakeups.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/LockPool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/MutexPoolLock.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/MutexPoolLock.h

## Purpose
Implements small synchronization helpers used where CryFS needs named locks, condition barriers, or coordinated release/reacquire behavior. This specific file has 45 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `LockName`, `MutexPoolLock`. Macros/constants: `MESSMER_CPPUTILS_LOCK_MUTEXPOOLLOCK_H`. Important declarations or call sites include `MutexPoolLock(LockPool<LockName> *pool, const LockName &lockName): _pool(pool), _lockName(lockName) {`; `_pool->lock(_lockName);`; `: _pool(pool), _lockName(lockName) {`; `_pool->lock(_lockName, lockToFreeWhileWaiting);`; `MutexPoolLock(MutexPoolLock &&rhs) noexcept: _pool(rhs._pool), _lockName(std::move(rhs._lockName)) {`; `~MutexPoolLock() {`; `if (_pool != nullptr) {`; `unlock();`; `void unlock() {`; `ASSERT(_pool != nullptr, "MutexPoolLock is not locked");`. CMake commands used here include `MutexPoolLock`, `if`, `unlock`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `LockPool.h`.

## Control Flow
Lock helpers acquire internal mutexes, wait on condition variables when a named lock is busy, and release with notification. Combined locking temporarily releases and reacquires multiple locks in a controlled order.

## State and Persistence Behavior
Synchronization state is in-memory only: locked names, counters, mutexes, and condition variables are lost at process exit.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `LockPool.h`.

## Risks and Edge Cases
Named-lock pools rely on callers releasing exactly once. Destructor assertions catch leaks late; missing release can deadlock waiters.

## Test Signals
Test contended same-name locks, release notification, destructor leak assertions, combined-lock wait behavior, and condition barrier wakeups.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/lock/MutexPoolLock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging/Logger.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging/Logger.h

## Purpose
Defines the thin logging facade and logger interface used by assertion, process, and utility code. This specific file has 59 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Logger`. Macros/constants: `MESSMER_CPPUTILS_LOGGING_LOGGER_H`. Important declarations or call sites include `void setLogger(std::shared_ptr<spdlog::logger> logger) {`; `_logger->set_level(_level);`; `void reset() {`; `setLogger(_defaultLogger());`; `void setLevel(spdlog::level::level_enum level) {`; `_logger->set_level(_level);`; `return _logger.get();`; `static std::shared_ptr<spdlog::logger> _defaultLogger() {`; `static auto singleton = spdlog::stderr_logger_mt("Log");`; `Logger() : _logger(), _level() {`. CMake commands used here include `setLogger`, `Logger`, `reset`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `spdlog/spdlog.h`, `../macros.h`, `spdlog/sinks/stdout_sinks.h`.

## Control Flow
Call sites use logging macros/facade functions; the concrete logger receives severity and formatted text while headers keep dependencies light.

## State and Persistence Behavior
Logging state is whatever concrete logger is configured by consumers; these headers primarily define call interfaces.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `spdlog/spdlog.h`, `../macros.h`, `spdlog/sinks/stdout_sinks.h`.

## Risks and Edge Cases
Logging macros should not introduce heavy formatting or side effects when disabled. Error logs may include sensitive paths or operational details.

## Test Signals
Compile-time tests plus assertion/backtrace integration are the strongest signals for this lightweight facade.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging/Logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging/logging.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging/logging.h

## Purpose
Defines the thin logging facade and logger interface used by assertion, process, and utility code. This specific file has 92 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ERROR_TYPE`, `WARN_TYPE`, `INFO_TYPE`, `DEBUG_TYPE`, `LogType`. Macros/constants: `MESSMER_CPPUTILS_LOGGING_LOGGING_H`. Important declarations or call sites include `inline void setLogger(std::shared_ptr<spdlog::logger> newLogger) {`; `logger().setLogger(newLogger);`; `inline void reset() {`; `logger().reset();`; `inline void flush() {`; `logger()->flush();`; `inline void setLevel(ERROR_TYPE) {`; `logger().setLevel(spdlog::level::err);`; `inline void setLevel(WARN_TYPE) {`; `logger().setLevel(spdlog::level::warn);`. CMake commands used here include `logger`, `LOG`. Primary includes/dependencies visible in the file include `Logger.h`, `stdexcept`, `spdlog/fmt/ostr.h`, `spdlog/sinks/basic_file_sink.h`, `spdlog/sinks/msvc_sink.h`, `spdlog/sinks/syslog_sink.h`.

## Control Flow
Call sites use logging macros/facade functions; the concrete logger receives severity and formatted text while headers keep dependencies light.

## State and Persistence Behavior
Logging state is whatever concrete logger is configured by consumers; these headers primarily define call interfaces.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Logger.h`, `stdexcept`, `spdlog/fmt/ostr.h`, `spdlog/sinks/basic_file_sink.h`, `spdlog/sinks/msvc_sink.h`, `spdlog/sinks/syslog_sink.h`.

## Risks and Edge Cases
Logging macros should not introduce heavy formatting or side effects when disabled. Error logs may include sensitive paths or operational details.

## Test Signals
Compile-time tests plus assertion/backtrace integration are the strongest signals for this lightweight facade.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/logging/logging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/macros.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/macros.h

## Purpose
Collects portability and class-shape macros such as copy/assignment suppression and compiler-specific annotations. This specific file has 30 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_MACROS_H_`, `DISALLOW_COPY_AND_ASSIGN`, `UNUSED`, `WARN_UNUSED_RESULT`. CMake commands used here include `Class`.

## Control Flow
The header is compile-time only: macros expand at class declarations or compiler-specific locations and introduce no runtime flow.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Macro misuse can hide copy semantics or compiler differences; changes have wide compile-time blast radius.

## Test Signals
Build coverage across compilers is the primary signal; class copy-suppression macros should be checked by compile-fail or static assertions where practical.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/cast.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/cast.h

## Purpose
Defines ownership pointer adapters and casts used in old CryFS C++ code before newer standard-library facilities were fully available. This specific file has 26 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_POINTER_CAST_H_`. Important declarations or call sites include `inline std::unique_ptr<DST> dynamic_pointer_move(std::unique_ptr<SRC> &source) {`; `DST *casted = dynamic_cast<DST*>(source.get());`; `if (casted != nullptr) {`; `std::ignore = source.release();`; `return std::unique_ptr<DST>(casted);`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `memory`.

## Control Flow
Pointer helpers transfer or observe ownership, perform checked casts, and provide compatibility shims where old compilers or Boost containers had limitations.

## State and Persistence Behavior
Ownership wrappers store raw or smart pointers in memory and encode whether ownership is held by the wrapper.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `memory`.

## Risks and Edge Cases
Optional ownership and cast helpers can make lifetime/cast assumptions non-obvious. Failed dynamic moves must leave ownership in a well-defined state.

## Test Signals
Test ownership transfer, null/empty optional ownership, successful and failed dynamic casts, unique_ref move-only behavior, and Boost optional compatibility.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/cast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/gcc_4_8_compatibility.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/gcc_4_8_compatibility.h

## Purpose
Defines ownership pointer adapters and casts used in old CryFS C++ code before newer standard-library facilities were fully available. This specific file has 47 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `_MakeUniq`, `__invalid_type`. Macros/constants: `MESSMER_CPPUTILS_GCC48COMPATIBILITY_H`. Important declarations or call sites include `{ return unique_ptr<_Tp>(new _Tp(std::forward<_Args>(__args)...)); }`; `{ return unique_ptr<_Tp>(new remove_extent_t<_Tp>[__num]()); }`. CMake commands used here include `make_unique`. Primary includes/dependencies visible in the file include `memory`.

## Control Flow
Pointer helpers transfer or observe ownership, perform checked casts, and provide compatibility shims where old compilers or Boost containers had limitations.

## State and Persistence Behavior
Ownership wrappers store raw or smart pointers in memory and encode whether ownership is held by the wrapper.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `memory`.

## Risks and Edge Cases
Optional ownership and cast helpers can make lifetime/cast assumptions non-obvious. Failed dynamic moves must leave ownership in a well-defined state.

## Test Signals
Test ownership transfer, null/empty optional ownership, successful and failed dynamic casts, unique_ref move-only behavior, and Boost optional compatibility.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/gcc_4_8_compatibility.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/optional_ownership_ptr.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/optional_ownership_ptr.h

## Purpose
Defines ownership pointer adapters and casts used in old CryFS C++ code before newer standard-library facilities were fully available. This specific file has 50 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_POINTER_OPTIONALOWNERSHIPPOINTER_H_`. Important declarations or call sites include `optional_ownership_ptr<T> WithOwnership(std::unique_ptr<T> obj) {`; `auto deleter = obj.get_deleter();`; `return optional_ownership_ptr<T>(obj.release(), deleter);`; `optional_ownership_ptr<T> WithOwnership(unique_ref<T> obj) {`; `return WithOwnership(static_cast<std::unique_ptr<T>>(std::move(obj)));`; `optional_ownership_ptr<T> WithoutOwnership(T *obj) {`; `return optional_ownership_ptr<T>(obj, [](T*){});`; `optional_ownership_ptr<T> null() {`; `return WithoutOwnership<T>(nullptr);`. Primary includes/dependencies visible in the file include `unique_ref.h`, `functional`.

## Control Flow
Pointer helpers transfer or observe ownership, perform checked casts, and provide compatibility shims where old compilers or Boost containers had limitations.

## State and Persistence Behavior
Ownership wrappers store raw or smart pointers in memory and encode whether ownership is held by the wrapper.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `unique_ref.h`, `functional`.

## Risks and Edge Cases
Optional ownership and cast helpers can make lifetime/cast assumptions non-obvious. Failed dynamic moves must leave ownership in a well-defined state.

## Test Signals
Test ownership transfer, null/empty optional ownership, successful and failed dynamic casts, unique_ref move-only behavior, and Boost optional compatibility.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/optional_ownership_ptr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/unique_ref.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/unique_ref.h

## Purpose
Defines ownership pointer adapters and casts used in old CryFS C++ code before newer standard-library facilities were fully available. This specific file has 196 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `T`, `D`, `unique_ref`, `U`, `T2`, `D2`, `DST`, `SRC`, `std`, `hash`, `less`. Macros/constants: `MESSMER_CPPUTILS_POINTER_UNIQUE_REF_H`. Important declarations or call sites include `: _target(std::move(from._target)) {`; `_invariant();`; `: _target(std::move(from._target)) {`; `_invariant();`; `_target = std::move(from._target);`; `_invariant();`; `_target = std::move(from._target);`; `_invariant();`; `_invariant();`; `_invariant();`. CMake commands used here include `unique_ref`, `_invariant`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`, `if`. Primary includes/dependencies visible in the file include `memory`, `boost/optional.hpp`, `../macros.h`, `gcc_4_8_compatibility.h`, `cast.h`, `../assert/assert.h`.

## Control Flow
Pointer helpers transfer or observe ownership, perform checked casts, and provide compatibility shims where old compilers or Boost containers had limitations.

## State and Persistence Behavior
Ownership wrappers store raw or smart pointers in memory and encode whether ownership is held by the wrapper.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `memory`, `boost/optional.hpp`, `../macros.h`, `gcc_4_8_compatibility.h`, `cast.h`, `../assert/assert.h`.

## Risks and Edge Cases
Optional ownership and cast helpers can make lifetime/cast assumptions non-obvious. Failed dynamic moves must leave ownership in a well-defined state.

## Test Signals
Test ownership transfer, null/empty optional ownership, successful and failed dynamic casts, unique_ref move-only behavior, and Boost optional compatibility.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/unique_ref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h

## Purpose
Defines ownership pointer adapters and casts used in old CryFS C++ code before newer standard-library facilities were fully available. This specific file has 24 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_POINTER_UNIQUE_REF_BOOST_OPTIONAL_GTEST_WORKAROUND_H`. Important declarations or call sites include `inline std::ostream& operator<<(std::ostream& out, const cpputils::unique_ref<T> &ref) {`; `out << ref.get();`. Primary includes/dependencies visible in the file include `unique_ref.h`, `boost/optional/optional_io.hpp`.

## Control Flow
Pointer helpers transfer or observe ownership, perform checked casts, and provide compatibility shims where old compilers or Boost containers had limitations.

## State and Persistence Behavior
Ownership wrappers store raw or smart pointers in memory and encode whether ownership is held by the wrapper.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `unique_ref.h`, `boost/optional/optional_io.hpp`.

## Risks and Edge Cases
Optional ownership and cast helpers can make lifetime/cast assumptions non-obvious. Failed dynamic moves must leave ownership in a well-defined state.

## Test Signals
Test ownership transfer, null/empty optional ownership, successful and failed dynamic casts, unique_ref move-only behavior, and Boost optional compatibility.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalCatcher.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalCatcher.cpp

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 134 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SignalCatcherRegistry`, `SignalCatcherRegisterer`, `SignalCatcherImpl`. Important declarations or call sites include `void got_signal(int signal);`; `void add(int signal, details::SignalCatcherImpl* signal_occurred_flag) {`; `_catchers.write([&] (auto& catchers) {`; `catchers.emplace_back(signal, signal_occurred_flag);`; `void remove(details::SignalCatcherImpl* catcher) {`; `_catchers.write([&] (auto& catchers) {`; `auto found = std::find_if(catchers.rbegin(), catchers.rend(), [catcher] (const auto& entry) {return entry.second == catcher;});`; `ASSERT(found != catchers.rend(), "Signal handler not found");`; `catchers.erase(--found.base()); // decrement because it's a reverse iterator`; `~SignalCatcherRegistry() {`. CMake commands used here include `ASSERT`, `SignalCatcherRegistry`, `DISALLOW_COPY_AND_ASSIGN`, `SignalCatcherRegisterer`, `SignalCatcherImpl`, `for`. Primary includes/dependencies visible in the file include `SignalCatcher.h`, `SignalHandler.h`, `algorithm`, `stdexcept`, `vector`, `cpp-utils/assert/assert.h`, `cpp-utils/thread/LeftRight.h`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `SignalCatcher.h`, `SignalHandler.h`, `algorithm`, `stdexcept`, `vector`, `cpp-utils/assert/assert.h`, `cpp-utils/thread/LeftRight.h`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalCatcher.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalCatcher.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalCatcher.h

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 44 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SignalCatcherImpl`, `is`, `SignalCatcher`. Macros/constants: `MESSMER_CPPUTILS_PROCESS_SIGNALCATCHER_H_`. Important declarations or call sites include `SignalCatcher(std::initializer_list<int> signals);`; `~SignalCatcher();`; `bool signal_occurred() const {`; `DISALLOW_COPY_AND_ASSIGN(SignalCatcher);`. CMake commands used here include `SignalCatcher`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `cpp-utils/macros.h`, `atomic`, `csignal`, `memory`, `vector`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cpp-utils/macros.h`, `atomic`, `csignal`, `memory`, `vector`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalCatcher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalHandler.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalHandler.cpp

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `SignalHandler.h`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `SignalHandler.h`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.
- The signal catcher registry uses `LeftRight` so the actual signal handler can find the active catcher without taking a mutex.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalHandler.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalHandler.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalHandler.h

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 141 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SignalHandlerRAII`, `sigaction`, `on`, `SignalHandlerRunningRAII`. Macros/constants: `MESSMER_CPPUTILS_PROCESS_SIGNALHANDLER_H_`. Important declarations or call sites include `using SignalHandlerFunction = void(int);`; `: _old_handler(), _signal(signal) {`; `std::memset(&new_signal_handler, 0, sizeof(new_signal_handler));`; `int error = sigfillset(&new_signal_handler.sa_mask);  // block all signals while signal handler is running`; `if (0 != error) {`; `throw std::runtime_error("Error calling sigfillset. Errno: " + std::to_string(errno));`; `_sigaction(_signal, &new_signal_handler, &_old_handler);`; `~SignalHandlerRAII() {`; `_sigaction(_signal, &_old_handler, &removed_handler);`; `if (handler != removed_handler.sa_handler) {  // NOLINT(cppcoreguidelines-pro-type-union-access)`. CMake commands used here include `if`, `_sigaction`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `memory`, `csignal`, `cpp-utils/assert/assert.h`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `memory`, `csignal`, `cpp-utils/assert/assert.h`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/SignalHandler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/daemonize.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/daemonize.cpp

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 73 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `void daemonize() {`; `pid_t pid = fork();`; `if (pid < 0) {`; `exit(EXIT_FAILURE);`; `if (pid > 0) {`; `exit(EXIT_SUCCESS);`; `umask(0);`; `pid_t sid = setsid();`; `if (sid < 0) {`; `LOG(ERR, "Failed to get SID for daemon process");`. CMake commands used here include `if`, `exit`, `umask`, `LOG`, `close`. Primary includes/dependencies visible in the file include `daemonize.h`, `../logging/logging.h`, `sys/types.h`, `sys/stat.h`, `stdio.h`, `stdlib.h`, `fcntl.h`, `errno.h`, `unistd.h`, `syslog.h`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `daemonize.h`, `../logging/logging.h`, `sys/types.h`, `sys/stat.h`, `stdio.h`, `stdlib.h`, `fcntl.h`, `errno.h`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/daemonize.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/daemonize.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/daemonize.h

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 10 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_PROCESS_DAEMONIZE_H`. Important declarations or call sites include `void daemonize();`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/daemonize.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/subprocess.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/subprocess.cpp

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 178 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `OutputPipeHandler`, `InputPipeHandler`. Important declarations or call sites include `bf::path executable = bp::search_path(command);`; `throw std::runtime_error("Tried to run command " + std::string(command) + " but didn't find it in the PATH");`; `, output_() {`; `output_.reserve(output_.size() + n);`; `output_.insert(output_.end(), vOut_.begin(), vOut_.begin() + n);`; `if (ec) {`; `if (ec != PIPE_CLOSED) {`; `throw SubprocessError(std::string() + "Error getting output from subprocess. Error code: " + std::to_string(ec.value()) + " : "...`; `ba::async_read(pipe_, buffer_, onOutput);`; `ba::async_read(pipe_, buffer_, onOutput);`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `subprocess.h`, `cstdio`, `stdexcept`, `cerrno`, `array`, `boost/process.hpp`, `boost/asio.hpp`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `subprocess.h`, `cstdio`, `stdexcept`, `cerrno`, `array`, `boost/process.hpp`, `boost/asio.hpp`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.

## File-Specific Notes
- The subprocess helper uses Boost.Process with Boost.Asio async pipes to avoid stdout/stderr deadlocks while feeding stdin.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/subprocess.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/subprocess.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/subprocess.h

## Purpose
Implements process-level helpers for signals, daemonization, subprocess execution, and safe signal-catching integration. This specific file has 39 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SubprocessResult`, `SubprocessError`, `Subprocess`. Macros/constants: `MESSMER_CPPUTILS_PROCESS_SUBPROCESS_H`. Important declarations or call sites include `SubprocessError(std::string msg) : std::runtime_error(std::move(msg)) {}`; `static SubprocessResult call(const char *command, const std::vector<std::string> &args, const std::string& input);`; `static SubprocessResult call(const boost::filesystem::path &executable, const std::vector<std::string> &args, const std::string...`; `static SubprocessResult check_call(const char *command, const std::vector<std::string> &args, const std::string& input);`; `static SubprocessResult check_call(const boost::filesystem::path &executable, const std::vector<std::string> &args, const std::...`; `DISALLOW_COPY_AND_ASSIGN(Subprocess);`. CMake commands used here include `SubprocessError`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `string`, `vector`, `stdexcept`, `boost/filesystem/path.hpp`, `../macros.h`.

## Control Flow
Signal helpers install RAII signal handlers and route events through a registry; subprocess execution resolves an executable, wires async pipes for stdin/stdout/stderr, waits, and reports exit status/output.

## State and Persistence Behavior
Signal handlers and daemon/subprocess state are process-local. Subprocess outputs are accumulated in memory; daemonization changes process/session descriptors rather than project files.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `string`, `vector`, `stdexcept`, `boost/filesystem/path.hpp`, `../macros.h`.

## Risks and Edge Cases
Signal handlers, fork handling, and async subprocess pipe callbacks are sensitive to ordering. Deadlocks or thrown exceptions inside async callbacks can terminate command flows unexpectedly.

## Test Signals
Test subprocess stdout/stderr/stdin and nonzero exits, signal catcher flagging and unregistering, daemonization in integration harnesses, and signal handler restoration.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/process/subprocess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/OSRandomGenerator.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/OSRandomGenerator.cpp

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `OSRandomGenerator.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `OSRandomGenerator.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/OSRandomGenerator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/OSRandomGenerator.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/OSRandomGenerator.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 28 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `OSRandomGenerator`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_OSRANDOMGENERATOR_H`. Important declarations or call sites include `OSRandomGenerator();`; `void _get(void *target, size_t bytes) override;`; `DISALLOW_COPY_AND_ASSIGN(OSRandomGenerator);`; `inline OSRandomGenerator::OSRandomGenerator() {}`; `inline void OSRandomGenerator::_get(void *target, size_t bytes) {`; `CryptoPP::OS_GenerateRandomBlock(true, static_cast<CryptoPP::byte*>(target), bytes);`. CMake commands used here include `OSRandomGenerator`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `RandomGenerator.h`, `vendor_cryptopp/osrng.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `RandomGenerator.h`, `vendor_cryptopp/osrng.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/OSRandomGenerator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/PseudoRandomPool.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/PseudoRandomPool.cpp

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 7 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `PseudoRandomPool.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `PseudoRandomPool.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/PseudoRandomPool.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/PseudoRandomPool.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/PseudoRandomPool.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 40 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `PseudoRandomPool`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_PSEUDORANDOMPOOL_H`. Important declarations or call sites include `PseudoRandomPool();`; `void _get(void *target, size_t bytes) override;`; `DISALLOW_COPY_AND_ASSIGN(PseudoRandomPool);`; `inline void PseudoRandomPool::_get(void *target, size_t bytes) {`; `_buffer.get(target, bytes);`; `inline PseudoRandomPool::PseudoRandomPool(): _buffer(), _refillThread(&_buffer, MIN_BUFFER_SIZE, MAX_BUFFER_SIZE) {`; `_refillThread.start();`. CMake commands used here include `PseudoRandomPool`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `boost/thread.hpp`, `RandomGenerator.h`, `ThreadsafeRandomDataBuffer.h`, `RandomGeneratorThread.h`, `mutex`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `boost/thread.hpp`, `RandomGenerator.h`, `ThreadsafeRandomDataBuffer.h`, `RandomGeneratorThread.h`, `mutex`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/PseudoRandomPool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/Random.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/Random.cpp

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 6 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `Random.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `Random.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/Random.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/Random.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/Random.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 34 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Random`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_RANDOM_H`. Important declarations or call sites include `static PseudoRandomPool &PseudoRandom() {`; `std::unique_lock <std::mutex> lock(_mutex);`; `static OSRandomGenerator &OSRandom() {`; `std::unique_lock <std::mutex> lock(_mutex);`; `DISALLOW_COPY_AND_ASSIGN(Random);`. CMake commands used here include `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `PseudoRandomPool.h`, `OSRandomGenerator.h`, `../data/FixedSizeData.h`, `../data/Data.h`, `mutex`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `PseudoRandomPool.h`, `OSRandomGenerator.h`, `../data/FixedSizeData.h`, `../data/Data.h`, `mutex`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/Random.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomDataBuffer.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomDataBuffer.cpp

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `RandomDataBuffer.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `RandomDataBuffer.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomDataBuffer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomDataBuffer.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomDataBuffer.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 53 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `RandomDataBuffer`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_RANDOMDATABUFFER_H`. Important declarations or call sites include `RandomDataBuffer();`; `size_t size() const;`; `void get(void *target, size_t bytes);`; `void add(const Data& data);`; `DISALLOW_COPY_AND_ASSIGN(RandomDataBuffer);`; `inline RandomDataBuffer::RandomDataBuffer() : _usedUntil(0), _data(0) {`; `inline size_t RandomDataBuffer::size() const {`; `inline void RandomDataBuffer::get(void *target, size_t numBytes) {`; `ASSERT(size() >= numBytes, "Too many bytes requested. Buffer is smaller.");`; `std::memcpy(target, _data.dataOffset(_usedUntil), numBytes);`. CMake commands used here include `RandomDataBuffer`, `DISALLOW_COPY_AND_ASSIGN`, `ASSERT`, `get`. Primary includes/dependencies visible in the file include `../data/Data.h`, `../assert/assert.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../data/Data.h`, `../assert/assert.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomDataBuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGenerator.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGenerator.cpp

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `RandomGenerator.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `RandomGenerator.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGenerator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGenerator.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGenerator.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 46 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `RandomGenerator`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_RANDOMGENERATOR_H`. Important declarations or call sites include `RandomGenerator();`; `template<size_t SIZE> FixedSizeData<SIZE> getFixedSize();`; `Data get(size_t size);`; `void write(void *target, size_t size);`; `virtual void _get(void *target, size_t bytes) = 0;`; `DISALLOW_COPY_AND_ASSIGN(RandomGenerator);`; `inline RandomGenerator::RandomGenerator() {`; `inline void RandomGenerator::write(void *target, size_t size) {`; `_get(target, size);`; `template<size_t SIZE> inline FixedSizeData<SIZE> RandomGenerator::getFixedSize() {`. CMake commands used here include `RandomGenerator`, `DISALLOW_COPY_AND_ASSIGN`, `_get`. Primary includes/dependencies visible in the file include `../data/FixedSizeData.h`, `../data/Data.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../data/FixedSizeData.h`, `../data/Data.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGenerator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGeneratorThread.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGeneratorThread.cpp

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 34 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `_thread(std::bind(&RandomGeneratorThread::_loopIteration, this), "RandomGeneratorThread") {`; `ASSERT(_maxSize >= _minSize, "Invalid parameters");`; `void RandomGeneratorThread::start() {`; `return _thread.start();`; `bool RandomGeneratorThread::_loopIteration() {`; `_buffer->waitUntilSizeIsLessThan(_minSize);`; `size_t neededRandomDataSize = _maxSize - _buffer->size();`; `ASSERT(_maxSize > _buffer->size(), "This could theoretically fail if another thread refilled the buffer. But we should be the o...`; `Data randomData = _generateRandomData(neededRandomDataSize);`; `_buffer->add(randomData);`. CMake commands used here include `_buffer`, `_minSize`, `_maxSize`, `_thread`, `ASSERT`. Primary includes/dependencies visible in the file include `RandomGeneratorThread.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `RandomGeneratorThread.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGeneratorThread.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGeneratorThread.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGeneratorThread.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 35 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `RandomGeneratorThread`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_RANDOMGENERATORTHREAD_H`. Important declarations or call sites include `RandomGeneratorThread(ThreadsafeRandomDataBuffer *buffer, size_t minSize, size_t maxSize);`; `void start();`; `bool _loopIteration();`; `Data _generateRandomData(size_t size);`; `DISALLOW_COPY_AND_ASSIGN(RandomGeneratorThread);`. CMake commands used here include `RandomGeneratorThread`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `../thread/LoopThread.h`, `ThreadsafeRandomDataBuffer.h`, `vendor_cryptopp/osrng.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../thread/LoopThread.h`, `ThreadsafeRandomDataBuffer.h`, `vendor_cryptopp/osrng.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGeneratorThread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/ThreadsafeRandomDataBuffer.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/ThreadsafeRandomDataBuffer.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 81 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ThreadsafeRandomDataBuffer`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_THREADSAFERANDOMDATABUFFER_H`. Important declarations or call sites include `ThreadsafeRandomDataBuffer();`; `size_t size() const;`; `void get(void *target, size_t numBytes);`; `void add(const Data& data);`; `void waitUntilSizeIsLessThan(size_t numBytes);`; `size_t _get(void *target, size_t bytes);`; `DISALLOW_COPY_AND_ASSIGN(ThreadsafeRandomDataBuffer);`; `inline ThreadsafeRandomDataBuffer::ThreadsafeRandomDataBuffer(): _buffer(), _mutex(), _dataAddedCv(), _dataGottenCv() {`; `inline size_t ThreadsafeRandomDataBuffer::size() const {`; `boost::unique_lock<boost::mutex> lock(_mutex);`. CMake commands used here include `ThreadsafeRandomDataBuffer`, `DISALLOW_COPY_AND_ASSIGN`, `while`, `ASSERT`. Primary includes/dependencies visible in the file include `../data/Data.h`, `../assert/assert.h`, `RandomDataBuffer.h`, `boost/thread.hpp`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../data/Data.h`, `../assert/assert.h`, `RandomDataBuffer.h`, `boost/thread.hpp`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/ThreadsafeRandomDataBuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/diskspace.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/diskspace.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 40 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `statvfs`. Important declarations or call sites include `uint64_t free_disk_space_in_bytes(const bf::path& location) {`; `int result = ::statvfs(location.string().c_str(), &stat);`; `if (0 != result) {`; `throw std::runtime_error("Error calling statvfs(). Errno: " + std::to_string(errno));`; `uint64_t free_disk_space_in_bytes(const bf::path& location) {`; `if (!GetDiskFreeSpaceEx(location.string().c_str(), &freeBytes, nullptr, nullptr)) {`; `throw std::runtime_error("Error calling GetDiskFreeSpaceEx(). Error code: " + std::to_string(GetLastError()));`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `diskspace.h`, `sys/statvfs.h`, `cerrno`, `Windows.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `diskspace.h`, `sys/statvfs.h`, `cerrno`, `Windows.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/diskspace.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/diskspace.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/diskspace.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 15 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_SYSTEM_DISKSPACE_H`. Important declarations or call sites include `uint64_t free_disk_space_in_bytes(const boost::filesystem::path& location);`. Primary includes/dependencies visible in the file include `cstdlib`, `boost/filesystem/path.hpp`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cstdlib`, `boost/filesystem/path.hpp`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/diskspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/env.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/env.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 50 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `void setenv(const char* key, const char* value) {`; `int retval = ::setenv(key, value, 1);`; `if (0 != retval) {`; `throw std::runtime_error("Error setting environment variable. Errno: " + std::to_string(errno));`; `void unsetenv(const char* key) {`; `int retval = ::unsetenv(key);`; `if (0 != retval) {`; `throw std::runtime_error("Error unsetting environment variable. Errno: " + std::to_string(errno));`; `void setenv(const char* key, const char* value) {`; `int retval = _putenv(command.str().c_str());`. CMake commands used here include `if`, `setenv`. Primary includes/dependencies visible in the file include `env.h`, `stdexcept`, `string`, `cerrno`, `cstdlib`, `Windows.h`, `sstream`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `env.h`, `stdexcept`, `string`, `cerrno`, `cstdlib`, `Windows.h`, `sstream`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/env.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/env.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/env.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 11 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_SYSTEM_ENV_H`. Important declarations or call sites include `void setenv(const char* key, const char* value);`; `void unsetenv(const char* key);`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 14 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `int set_filetime(const char *filepath, timespec lastAccessTime, timespec lastModificationTime);`; `int get_filetime(const char *filepath, timespec* lastAccessTime, timespec* lastModificationTime);`. Primary includes/dependencies visible in the file include `ctime`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `ctime`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime_nonwindows.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime_nonwindows.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 39 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `timeval`. Important declarations or call sites include `int set_filetime(const char *filepath, timespec lastAccessTime, timespec lastModificationTime) {`; `TIMESPEC_TO_TIMEVAL(&casted_times[0], &lastAccessTime);`; `TIMESPEC_TO_TIMEVAL(&casted_times[1], &lastModificationTime);`; `int retval = ::utimes(filepath, casted_times.data());`; `if (0 == retval) {`; `int get_filetime(const char *filepath, timespec* lastAccessTime, timespec* lastModificationTime) {`; `int retval = ::stat(filepath, &attrib);`; `if (retval != 0) {`. CMake commands used here include `TIMESPEC_TO_TIMEVAL`, `if`. Primary includes/dependencies visible in the file include `filetime.h`, `utime.h`, `sys/time.h`, `sys/stat.h`, `errno.h`, `array`, `cpp-utils/system/stat.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `filetime.h`, `utime.h`, `sys/time.h`, `sys/stat.h`, `errno.h`, `array`, `cpp-utils/system/stat.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime_nonwindows.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime_windows.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime_windows.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 114 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `OpenFileRAII`. Important declarations or call sites include `FILETIME to_filetime(timespec value) {`; `timespec to_timespec(FILETIME value) {`; `if (ticks >= TICKS_TO_UNIX_EPOCH) { // otherwise out of range`; `:handle(CreateFileA(filepath, access, 0, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr)) {`; `BOOL close() {`; `if (INVALID_HANDLE_VALUE == handle) {`; `BOOL success = CloseHandle(handle);`; `~OpenFileRAII() {`; `close();`; `int set_filetime(const char *filepath, timespec lastAccessTime, timespec lastModificationTime) {`. CMake commands used here include `if`, `OpenFileRAII`, `close`. Primary includes/dependencies visible in the file include `filetime.h`, `Windows.h`, `stdexcept`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `filetime.h`, `Windows.h`, `stdexcept`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime_windows.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/get_total_memory.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/get_total_memory.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 59 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `uint64_t get_total_memory() {`; `size_t size = sizeof(mem);`; `int result = sysctlbyname("hw.memsize", &mem, &size, nullptr, 0);`; `if (0 != result) {`; `throw std::runtime_error("sysctlbyname syscall failed");`; `uint64_t get_total_memory() {`; `long numRAMPages = sysconf(_SC_PHYS_PAGES);`; `long pageSize = sysconf(_SC_PAGESIZE);`; `uint64_t get_total_memory() {`; `status.dwLength = sizeof(status);`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `get_total_memory.h`, `stdexcept`, `string`, `sys/types.h`, `sys/sysctl.h`, `unistd.h`, `Windows.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `get_total_memory.h`, `stdexcept`, `string`, `sys/types.h`, `sys/sysctl.h`, `unistd.h`, `Windows.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/get_total_memory.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/get_total_memory.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/get_total_memory.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 14 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_SYSTEM_GETTOTALMEMORY_H`. Important declarations or call sites include `uint64_t get_total_memory();`. Primary includes/dependencies visible in the file include `cstdint`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cstdint`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/get_total_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/homedir.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/homedir.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 111 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `passwd`, `PathBuffer`. Important declarations or call sites include `bf::path _get_home_directory() {`; `const char* homedir_ = getenv("HOME");`; `if (homedir == "") {`; `struct passwd* pwd = getpwuid(getuid());`; `if (pwd) {`; `if (homedir == "") {`; `throw std::runtime_error("Couldn't determine home directory for user");`; `bf::path _get_appdata_directory() {`; `const char* xdg_data_dir = std::getenv("XDG_DATA_HOME");`; `if (xdg_data_dir != nullptr) {`. CMake commands used here include `if`, `CoTaskMemFree`. Primary includes/dependencies visible in the file include `homedir.h`, `sys/types.h`, `pwd.h`, `Shlobj.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `homedir.h`, `sys/types.h`, `pwd.h`, `Shlobj.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/homedir.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/homedir.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/homedir.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 61 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `FakeHomeDirectoryRAII`, `HomeDirectory`, `FakeTempHomeDirectoryRAII`. Macros/constants: `MESSMER_CPPUTILS_SYSTEM_GETTOTALMEMORY_H`. Important declarations or call sites include `static const boost::filesystem::path &get();`; `static const boost::filesystem::path &getXDGDataDir();`; `HomeDirectory();`; `static HomeDirectory &singleton();`; `DISALLOW_COPY_AND_ASSIGN(HomeDirectory);`; `FakeHomeDirectoryRAII(const boost::filesystem::path &fakeHomeDirectory, const boost::filesystem::path &fakeAppdataDirectory);`; `~FakeHomeDirectoryRAII();`; `DISALLOW_COPY_AND_ASSIGN(FakeHomeDirectoryRAII);`; `FakeTempHomeDirectoryRAII();`; `DISALLOW_COPY_AND_ASSIGN(FakeTempHomeDirectoryRAII);`. CMake commands used here include `HomeDirectory`, `DISALLOW_COPY_AND_ASSIGN`, `FakeHomeDirectoryRAII`, `FakeTempHomeDirectoryRAII`. Primary includes/dependencies visible in the file include `boost/filesystem/path.hpp`, `../macros.h`, `cpp-utils/pointer/unique_ref.h`, `../tempfile/TempDir.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `boost/filesystem/path.hpp`, `../macros.h`, `cpp-utils/pointer/unique_ref.h`, `../tempfile/TempDir.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/homedir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/memory.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/memory.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 25 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `UnswappableAllocator`. Macros/constants: `MESSMER_CPPUTILS_SYSTEM_MEMORY_H`. Important declarations or call sites include `void* allocate(size_t size) override;`; `void free(void* data, size_t size) override;`. Primary includes/dependencies visible in the file include `cstdlib`, `../data/Data.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cstdlib`, `../data/Data.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/memory_nonwindows.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/memory_nonwindows.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 37 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `void* UnswappableAllocator::allocate(size_t size) {`; `void* data = DefaultAllocator().allocate(size);`; `const int result = ::mlock(data, size);`; `if (0 != result) {`; `throw std::runtime_error("Error calling mlock. Errno: " + std::to_string(errno));`; `void UnswappableAllocator::free(void* data, size_t size) {`; `const int result = ::munlock(data, size);`; `if (0 != result) {`; `std::memset(data, 0, size);`; `DefaultAllocator().free(data, size);`. CMake commands used here include `if`, `LOG`, `DefaultAllocator`. Primary includes/dependencies visible in the file include `memory.h`, `sys/mman.h`, `errno.h`, `stdexcept`, `cpp-utils/logging/logging.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `memory.h`, `sys/mman.h`, `errno.h`, `stdexcept`, `cpp-utils/logging/logging.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/memory_nonwindows.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/memory_windows.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/memory_windows.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 51 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `void* UnswappableAllocator::allocate(size_t size) {`; `void* data = ::VirtualAlloc(nullptr, size, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);`; `if (nullptr == data) {`; `throw std::runtime_error("Error calling VirtualAlloc. Errno: " + std::to_string(GetLastError()));`; `const BOOL success = ::VirtualLock(data, size);`; `if (!success) {`; `throw std::runtime_error("Error calling VirtualLock. Errno: " + std::to_string(GetLastError()));`; `void UnswappableAllocator::free(void* data, size_t size) {`; `std::memset(data, 0, size);`; `BOOL success = ::VirtualUnlock(data, size);`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `memory.h`, `Windows.h`, `stdexcept`, `cpp-utils/logging/logging.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `memory.h`, `Windows.h`, `stdexcept`, `cpp-utils/logging/logging.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/memory_windows.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/path.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/path.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 27 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_SYSTEM_PATH_H`. Important declarations or call sites include `inline bool path_is_just_drive_letter(const boost::filesystem::path& path) {`; `return path.has_root_path() && !path.has_root_directory() && !path.has_parent_path();`; `inline constexpr bool path_is_just_drive_letter(const boost::filesystem::path& /*path*/) {`. Primary includes/dependencies visible in the file include `boost/filesystem/path.hpp`, `cpp-utils/macros.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `boost/filesystem/path.hpp`, `cpp-utils/macros.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/stat.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/stat.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 15 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_SYSTEM_STAT_H`, `st_atim`, `st_mtim`, `st_ctim`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/time.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/time.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 22 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `timespec`. Important declarations or call sites include `struct timespec now() {`; `auto now = system_clock::now().time_since_epoch();`; `spec.tv_sec = duration_cast<seconds>(now).count();`. Primary includes/dependencies visible in the file include `time.h`, `chrono`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `time.h`, `chrono`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/time.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/time.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/time.h

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 40 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_SYSTEM_TIME_H`. Important declarations or call sites include `timespec now();`; `inline bool operator<(const timespec &lhs, const timespec &rhs) {`; `inline bool operator>(const timespec &lhs, const timespec &rhs) {`; `return !operator>(lhs, rhs);`; `return !operator<(lhs, rhs);`. Primary includes/dependencies visible in the file include `time.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `time.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempDir.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempDir.cpp

## Purpose
Implements RAII temporary file and directory helpers for tests and transient filesystem work. This specific file has 33 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `: _path(bf::unique_path(bf::temp_directory_path() / "%%%%-%%%%-%%%%-%%%%")) {`; `bf::create_directory(_path);`; `TempDir::~TempDir() {`; `remove();`; `void TempDir::remove() {`; `if (bf::exists(_path)) {`; `bf::remove_all(_path);`; `} catch (const boost::filesystem::filesystem_error &e) {`; `LOG(ERR, "Could not delete tempfile.");`; `const bf::path &TempDir::path() const {`. CMake commands used here include `remove`, `if`, `LOG`. Primary includes/dependencies visible in the file include `TempDir.h`, `../logging/logging.h`.

## Control Flow
Temporary resources are created at construction or factory time and removed by RAII destruction unless moved away or intentionally released.

## State and Persistence Behavior
State is the filesystem path and ownership flag for the temporary resource; the resource itself exists on disk until RAII cleanup.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `TempDir.h`, `../logging/logging.h`.

## Risks and Edge Cases
Temp resource cleanup can fail on open handles or permissions. Path generation must avoid races and predictable names.

## Test Signals
Assert resources exist while owned, disappear after destruction, survive move semantics correctly, and handle nested temp dirs/files.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempDir.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempDir.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempDir.h

## Purpose
Implements RAII temporary file and directory helpers for tests and transient filesystem work. This specific file has 26 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `TempDir`. Macros/constants: `MESSMER_CPPUTILS_TEMPFILE_TEMPDIR_H_`. Important declarations or call sites include `TempDir();`; `~TempDir();`; `const boost::filesystem::path &path() const;`; `void remove();`; `DISALLOW_COPY_AND_ASSIGN(TempDir);`. CMake commands used here include `TempDir`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `boost/filesystem.hpp`, `../macros.h`.

## Control Flow
Temporary resources are created at construction or factory time and removed by RAII destruction unless moved away or intentionally released.

## State and Persistence Behavior
State is the filesystem path and ownership flag for the temporary resource; the resource itself exists on disk until RAII cleanup.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `boost/filesystem.hpp`, `../macros.h`.

## Risks and Edge Cases
Temp resource cleanup can fail on open handles or permissions. Path generation must avoid races and predictable names.

## Test Signals
Assert resources exist while owned, disappear after destruction, survive move semantics correctly, and handle nested temp dirs/files.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempDir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempFile.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempFile.cpp

## Purpose
Implements RAII temporary file and directory helpers for tests and transient filesystem work. This specific file has 48 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `: _path(path) {`; `if (create) {`; `ofstream file(_path.string().c_str());`; `if (!file.good()) {`; `throw std::runtime_error("Could not create tempfile");`; `: TempFile(bf::unique_path(bf::temp_directory_path() / "%%%%-%%%%-%%%%-%%%%"), create) {`; `TempFile::~TempFile() {`; `if (exists()) {`; `remove();`; `} catch (const boost::filesystem::filesystem_error &e) {`. CMake commands used here include `if`, `remove`, `LOG`. Primary includes/dependencies visible in the file include `TempFile.h`, `../logging/logging.h`, `fstream`.

## Control Flow
Temporary resources are created at construction or factory time and removed by RAII destruction unless moved away or intentionally released.

## State and Persistence Behavior
State is the filesystem path and ownership flag for the temporary resource; the resource itself exists on disk until RAII cleanup.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `TempFile.h`, `../logging/logging.h`, `fstream`.

## Risks and Edge Cases
Temp resource cleanup can fail on open handles or permissions. Path generation must avoid races and predictable names.

## Test Signals
Assert resources exist while owned, disappear after destruction, survive move semantics correctly, and handle nested temp dirs/files.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempFile.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempFile.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempFile.h

## Purpose
Implements RAII temporary file and directory helpers for tests and transient filesystem work. This specific file has 30 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `TempFile`. Macros/constants: `MESSMER_CPPUTILS_TEMPFILE_TEMPFILE_H_`. Important declarations or call sites include `explicit TempFile(const boost::filesystem::path &path, bool create = true);`; `explicit TempFile(bool create = true);`; `~TempFile();`; `const boost::filesystem::path &path() const;`; `bool exists() const;`; `void remove();`; `DISALLOW_COPY_AND_ASSIGN(TempFile);`. CMake commands used here include `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `boost/filesystem.hpp`, `../macros.h`.

## Control Flow
Temporary resources are created at construction or factory time and removed by RAII destruction unless moved away or intentionally released.

## State and Persistence Behavior
State is the filesystem path and ownership flag for the temporary resource; the resource itself exists on disk until RAII cleanup.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `boost/filesystem.hpp`, `../macros.h`.

## Risks and Edge Cases
Temp resource cleanup can fail on open handles or permissions. Path generation must avoid races and predictable names.

## Test Signals
Assert resources exist while owned, disappear after destruction, survive move semantics correctly, and handle nested temp dirs/files.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/tempfile/TempFile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils/CaptureStderrRAII.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils/CaptureStderrRAII.h

## Purpose
Provides test-only RAII and expectation helpers for capturing stderr and checking exception behavior. This specific file has 46 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CaptureStderrRAII`. Macros/constants: `MESSMER_CPPUTILS_CAPTURESTDERRRAII_H`. Important declarations or call sites include `CaptureStderrRAII() {`; `_oldBuffer = std::cerr.rdbuf();`; `std::cerr.rdbuf(_buffer.rdbuf());`; `~CaptureStderrRAII() {`; `std::cerr.rdbuf(_oldBuffer);`; `std::string get_stderr() const {`; `return _buffer.str();`; `void EXPECT_MATCHES(const std::string &regex) {`; `EXPECT_TRUE(std::regex_search(get_stderr(), std::regex(regex, std::regex::basic)));`; `DISALLOW_COPY_AND_ASSIGN(CaptureStderrRAII);`. CMake commands used here include `CaptureStderrRAII`, `EXPECT_TRUE`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `cpp-utils/macros.h`, `iostream`, `gmock/gmock.h`, `regex`.

## Control Flow
Test helpers wrap a scope around stderr redirection or exception assertions so tests can express expected failure behavior with minimal boilerplate.

## State and Persistence Behavior
State is scoped to a test and restored in destructors.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `cpp-utils/macros.h`, `iostream`, `gmock/gmock.h`, `regex`.

## Risks and Edge Cases
Test helpers can mask unexpected exceptions if predicates are too broad, and stderr capture must restore descriptors even on failure.

## Test Signals
Validate helper self-tests by capturing known stderr output and matching expected exception types/messages.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils/CaptureStderrRAII.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils/ExpectThrows.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils/ExpectThrows.h

## Purpose
Provides test-only RAII and expectation helpers for capturing stderr and checking exception behavior. This specific file has 32 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Exception`, `Functor`. Macros/constants: `MESSMER_CPPUTILS_EXPECTTHROWS_H`. Important declarations or call sites include `inline void expectThrows(Functor&& functor, const char* expectMessageContains) {`; `std::forward<Functor>(functor)();`; `} catch (const Exception& e) {`; `EXPECT_THAT(e.what(), testing::HasSubstr(expectMessageContains));`; `inline void expectFailsAssertion(Functor&& functor, const char* expectMessageContains) {`; `expectThrows<cpputils::AssertFailed>(std::forward<Functor>(functor), expectMessageContains);`. CMake commands used here include `EXPECT_THAT`, `ADD_FAILURE`. Primary includes/dependencies visible in the file include `gmock/gmock.h`, `cpp-utils/assert/assert.h`.

## Control Flow
Test helpers wrap a scope around stderr redirection or exception assertions so tests can express expected failure behavior with minimal boilerplate.

## State and Persistence Behavior
State is scoped to a test and restored in destructors.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `gmock/gmock.h`, `cpp-utils/assert/assert.h`.

## Risks and Edge Cases
Test helpers can mask unexpected exceptions if predicates are too broad, and stderr capture must restore descriptors even on failure.

## Test Signals
Validate helper self-tests by capturing known stderr output and matching expected exception types/messages.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/testutils/ExpectThrows.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LeftRight.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LeftRight.cpp

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `LeftRight.h`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `LeftRight.h`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LeftRight.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LeftRight.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LeftRight.h

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 162 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `IncrementRAII`, `T`, `LeftRight`, `F`. Important declarations or call sites include `explicit IncrementRAII(std::atomic<int32_t> *counter): _counter(counter) {`; `~IncrementRAII() {`; `DISALLOW_COPY_AND_ASSIGN(IncrementRAII);`; `~LeftRight() {`; `std::unique_lock<std::mutex> lock(_writeMutex);`; `while (_counters[0].load() != 0 || _counters[1].load() != 0) {`; `std::this_thread::yield();`; `auto read(F&& readFunc) const {`; `detail::IncrementRAII _increment_counter(&_counters[_foregroundCounterIndex.load()]); // NOLINT(cppcoreguidelines-pro-bounds-co...`; `if(_inDestruction.load()) {`. CMake commands used here include `DISALLOW_COPY_AND_ASSIGN`, `while`, `if`, `_callWriteFuncOnBackgroundInstance`, `_waitForBackgroundCounterToBeZero`. Primary includes/dependencies visible in the file include `atomic`, `functional`, `mutex`, `thread`, `cpp-utils/macros.h`, `array`, `stdexcept`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `atomic`, `functional`, `mutex`, `thread`, `cpp-utils/macros.h`, `array`, `stdexcept`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

## File-Specific Notes
- The left-right structure provides wait-free reads by duplicating data and using reader counters while writes update both copies under a mutex.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LeftRight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LoopThread.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LoopThread.cpp

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 31 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `: _loopIteration(std::move(loopIteration)), _runningHandle(none), _threadName(std::move(threadName)) {`; `LoopThread::~LoopThread() {`; `if (_runningHandle != none) {`; `stop();`; `void LoopThread::start() {`; `_runningHandle = ThreadSystem::singleton().start(_loopIteration, _threadName);`; `void LoopThread::stop() {`; `if (_runningHandle == none) {`; `throw std::runtime_error("LoopThread is not running");`; `ThreadSystem::singleton().stop(*_runningHandle);`. CMake commands used here include `if`, `stop`. Primary includes/dependencies visible in the file include `LoopThread.h`, `../logging/logging.h`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `LoopThread.h`, `../logging/logging.h`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LoopThread.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LoopThread.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LoopThread.h

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 32 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `destructor`, `LoopThread`. Macros/constants: `MESSMER_CPPUTILS_THREAD_LOOPTHREAD_H`. Important declarations or call sites include `LoopThread(std::function<bool()> loopIteration, std::string threadName);`; `~LoopThread();`; `void start();`; `void stop();`; `DISALLOW_COPY_AND_ASSIGN(LoopThread);`. CMake commands used here include `LoopThread`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `ThreadSystem.h`, `boost/optional.hpp`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `ThreadSystem.h`, `boost/optional.hpp`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/LoopThread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/ThreadSystem.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/ThreadSystem.cpp

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 113 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `ThreadSystem &ThreadSystem::singleton() {`; `ThreadSystem::ThreadSystem(): _runningThreads(), _mutex() {`; `pthread_atfork(&ThreadSystem::_onBeforeFork, &ThreadSystem::_onAfterFork, &ThreadSystem::_onAfterFork);`; `ThreadSystem::Handle ThreadSystem::start(function<bool()> loopIteration, string threadName) {`; `boost::unique_lock<boost::mutex> lock(_mutex);`; `auto thread = _startThread(loopIteration, threadName);`; `return std::prev(_runningThreads.end());`; `void ThreadSystem::stop(Handle handle) {`; `boost::unique_lock<boost::mutex> lock(_mutex);`; `boost::thread thread = std::move(handle->thread);`. CMake commands used here include `pthread_atfork`, `singleton`, `for`, `if`, `while`, `LOG`. Primary includes/dependencies visible in the file include `ThreadSystem.h`, `../logging/logging.h`, `debugging.h`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `ThreadSystem.h`, `../logging/logging.h`, `debugging.h`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

## File-Specific Notes
- Non-Windows builds register `pthread_atfork` hooks that interrupt managed threads before fork and restart them afterward.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/ThreadSystem.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/ThreadSystem.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/ThreadSystem.h

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 48 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ThreadSystem`, `RunningThread`. Macros/constants: `MESSMER_CPPUTILS_THREAD_THREADSYSTEM_H`. Important declarations or call sites include `static ThreadSystem &singleton();`; `Handle start(std::function<bool()> loopIteration, std::string threadName);`; `void stop(Handle handle);`; `ThreadSystem();`; `static void _runThread(std::function<bool()> loopIteration);`; `static void _onBeforeFork();`; `static void _onAfterFork();`; `void _stopAllThreadsForRestart();`; `void _restartAllThreads();`; `boost::thread _startThread(std::function<bool()> loopIteration, const std::string& threadName);`. CMake commands used here include `ThreadSystem`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `../macros.h`, `boost/thread.hpp`, `list`, `functional`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `../macros.h`, `boost/thread.hpp`, `list`, `functional`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/ThreadSystem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging.h

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 21 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_CPPUTILS_DEBUGGING_H`. Important declarations or call sites include `void set_thread_name(const char* name);`; `std::string get_thread_name();`; `std::string get_thread_name(std::thread* thread);`. Primary includes/dependencies visible in the file include `string`, `thread`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `string`, `thread`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging_nonwindows.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging_nonwindows.cpp

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 105 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `OpenFileRAII`. Important declarations or call sites include `void set_thread_name(const char* name) {`; `std::string name_(name);`; `if (name_.size() > MAX_NAME_LEN - 1) {`; `name_.resize(MAX_NAME_LEN - 1);`; `int result = pthread_setname_np(name_.c_str());`; `int result = pthread_setname_np(pthread_self(), name_.c_str());`; `if (0 != result) {`; `throw std::runtime_error("Error setting thread name with pthread_setname_np. Code: " + std::to_string(result));`; `explicit OpenFileRAII(const char* filename) : fd(::open(filename, O_RDONLY | O_CLOEXEC)) {}`; `~OpenFileRAII() {`. CMake commands used here include `if`, `ASSERT`. Primary includes/dependencies visible in the file include `debugging.h`, `stdexcept`, `thread`, `pthread.h`, `cpp-utils/assert/assert.h`, `errno.h`, `fcntl.h`, `unistd.h`, `boost/filesystem/path.hpp`, `sys/types.h`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `debugging.h`, `stdexcept`, `thread`, `pthread.h`, `cpp-utils/assert/assert.h`, `errno.h`, `fcntl.h`, `unistd.h`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging_nonwindows.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging_windows.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging_windows.cpp

## Purpose
Implements threading helpers: a left-right wait-free-read structure, named loop threads, thread-system restart around fork, and platform thread naming. This specific file has 112 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `NameData`, `ModuleHandle`, `Fn`, `APIFunction`. Important declarations or call sites include `~NameData() {`; `if (nullptr != LocalFree(name)) {`; `throw std::runtime_error("Error releasing thread description memory. Error code: " + std::to_string(GetLastError()));`; `ModuleHandle(const char* dll) {`; `bool success = GetModuleHandleExA(0, dll, &module);`; `if (!success) {`; `throw std::runtime_error(string() + "Error loading dll: " + dll + ". Error code: " + std::to_string(GetLastError()));`; `~ModuleHandle() {`; `bool success = FreeLibrary(module);`; `if (!success) {`. CMake commands used here include `if`, `ModuleHandle`, `APIFunction`, `ASSERT`. Primary includes/dependencies visible in the file include `Windows.h`, `debugging.h`, `codecvt`, `cpp-utils/assert/assert.h`.

## Control Flow
Thread helpers start named boost threads, repeatedly invoke a loop callback until it returns false or interruption occurs, and stop/restart managed threads around fork on non-Windows platforms.

## State and Persistence Behavior
ThreadSystem stores a process-wide list of running threads and callbacks so it can interrupt, join, and restart them around fork.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `Windows.h`, `debugging.h`, `codecvt`, `cpp-utils/assert/assert.h`.

## Risks and Edge Cases
Thread interruption and fork restart are timing-sensitive. Callbacks must tolerate interruption points and should not hold locks across fork boundaries.

## Test Signals
Test loop start/stop, no double stop, thread naming, LeftRight concurrent reads/writes, and ThreadSystem fork restart behavior on non-Windows.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/thread/debugging_windows.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type/ValueType.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type/ValueType.cpp

## Purpose
Provides strongly typed value wrappers and hash/order helpers for ID-like primitive values. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `ValueType.h`.

## Control Flow
Value wrappers are inline constexpr-style operators around an underlying scalar; comparison, hashing, and accessors are generated without owning external resources.

## State and Persistence Behavior
Each value object stores only its underlying primitive value.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `ValueType.h`.

## Risks and Edge Cases
Strong typedefs are only as safe as their constructors; exposing the underlying value can reintroduce primitive confusion.

## Test Signals
Compile/run tests should verify equality/order/hash behavior, constexpr construction, and no accidental cross-type comparison.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type/ValueType.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type/ValueType.h -->
# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type/ValueType.h

## Purpose
Provides strongly typed value wrappers and hash/order helpers for ID-like primitive values. This specific file has 263 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `MyIdType`, `ConcreteType`, `UnderlyingType`, `IdValueType`, `must`, `std`, `hash`, `OrderedIdValueType`, `QuantityValueType`, `FlagsValueType`. Macros/constants: `MESSMER_CPPUTILS_VALUETYPE_VALUETYPE_H_`, `DEFINE_HASH_FOR_VALUE_TYPE`. Important declarations or call sites include `*     constexpr explicit MyIdType(uint32_t id): IdValueType(id) {}`; `*   DEFINE_HASH_FOR_VALUE_TYPE(MyIdType);`; `constexpr IdValueType& operator=(IdValueType&& rhs) noexcept(noexcept(*std::declval<UnderlyingType*>() = std::move(rhs.value_))) {`; `value_ = std::move(rhs.value_);`; `constexpr IdValueType& operator=(const IdValueType& rhs) noexcept(noexcept(*std::declval<UnderlyingType*>() = rhs.value_)) {`; `return operator=(IdValueType(rhs));`; `: value_(value) {`; `friend constexpr bool operator==(ConcreteType lhs, ConcreteType rhs) noexcept(noexcept(std::declval<UnderlyingType>() == std::d...`; `friend constexpr bool operator!=(ConcreteType lhs, ConcreteType rhs) noexcept(noexcept(lhs == rhs)) {`; `size_t operator()(ClassName x) const noexcept(noexcept(std::hash<ClassName::underlying_type>()(x.value_))) {   \`. CMake commands used here include `static_assert`. Primary includes/dependencies visible in the file include `functional`, `cpp-utils/assert/assert.h`.

## Control Flow
Value wrappers are inline constexpr-style operators around an underlying scalar; comparison, hashing, and accessors are generated without owning external resources.

## State and Persistence Behavior
Each value object stores only its underlying primitive value.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `functional`, `cpp-utils/assert/assert.h`.

## Risks and Edge Cases
Strong typedefs are only as safe as their constructors; exposing the underlying value can reintroduce primitive confusion.

## Test Signals
Compile/run tests should verify equality/order/hash behavior, constexpr construction, and no accidental cross-type comparison.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cpp-utils/value_type/ValueType.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/CMakeLists.txt

## Purpose
Describes how this source subtree is built, which sources enter the library or executable, and which third-party or sibling CryFS components are linked. This specific file has 25 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
CMake commands used here include `project`, `INCLUDE`, `set`, `add_library`, `target_link_libraries`, `target_enable_style_warnings`, `target_activate_cpp14`, `target_add_boost`, `add_executable`, `set_target_properties`, `install`.

## Control Flow
CMake control is declarative: sources are grouped into targets, include directories are exposed, and link dependencies connect this subtree to Boost, Crypto++, fspp, blockstore, and CryFS components.

## State and Persistence Behavior
No runtime state is stored. The build graph persists only as generated build-system metadata.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Build scripts can silently omit files or platform-specific sources; target/link changes should be validated on Linux and Windows configurations.

## Test Signals
Validate by configuring and building the old-cpp tree on supported platforms, including test targets and platform-specific source selection.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/Cli.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/Cli.cpp

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 58 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `void _showVersion() {`; `void Cli::main(int argc, const char **argv) {`; `_showVersion();`; `ProgramOptions options = Parser(argc, argv).parse();`; `if (!boost::filesystem::exists(options.mountDir())) {`; `throw cryfs::CryfsException("Given mountdir doesn't exist", cryfs::ErrorCode::InaccessibleMountDir);`; `bool immediate = options.immediate();`; `if (options.immediate()) {`; `if (options.immediate()) {`; `if (immediate) {`. CMake commands used here include `_showVersion`, `if`. Primary includes/dependencies visible in the file include `Cli.h`, `fspp/fuse/Fuse.h`, `cryfs-unmount/program_options/Parser.h`, `gitversion/gitversion.h`, `cryfs/impl/CryfsException.h`, `iostream`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `Cli.h`, `fspp/fuse/Fuse.h`, `cryfs-unmount/program_options/Parser.h`, `gitversion/gitversion.h`, `cryfs/impl/CryfsException.h`, `iostream`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/Cli.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/Cli.h -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/Cli.h

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 15 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Cli`. Macros/constants: `MESSMER_CRYFSUNMOUNT_CLI_H`. Important declarations or call sites include `void main(int argc, const char **argv);`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/Cli.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/main_unmount.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/main_unmount.cpp

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 39 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `int main(int argc, const char *argv[]) {`; `if (!IsWindows7SP1OrGreater()) {`; `exit(1);`; `cpputils::showBacktraceOnCrash();`; `cryfs_unmount::Cli().main(argc, argv);`; `catch (const cryfs::CryfsException &e) {`; `if (e.what() != std::string()) {`; `return exitCode(e.errorCode());`; `catch (const std::runtime_error &e) {`; `return exitCode(ErrorCode::UnspecifiedError);`. CMake commands used here include `if`, `exit`, `catch`. Primary includes/dependencies visible in the file include `Windows.h`, `VersionHelpers.h`, `iostream`, `cryfs/impl/CryfsException.h`, `cpp-utils/assert/backtrace.h`, `Cli.h`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `Windows.h`, `VersionHelpers.h`, `iostream`, `cryfs/impl/CryfsException.h`, `cpp-utils/assert/backtrace.h`, `Cli.h`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/main_unmount.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/Parser.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/Parser.cpp

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 131 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `:_options(_argsToVector(argc, argv)) {`; `vector<string> Parser::_argsToVector(int argc, const char **argv) {`; `result.push_back(argv[i]);`; `ProgramOptions Parser::parse() const {`; `po::variables_map vm = _parseOptionsOrShowHelp(_options);`; `if (!vm.count("mount-dir")) {`; `_showHelpAndExit("Please specify a mount directory.", ErrorCode::InvalidArguments);`; `bf::path mountDir = vm["mount-dir"].as<string>();`; `bool immediate = vm.count("immediate");`; `return ProgramOptions(std::move(mountDir), immediate);`. CMake commands used here include `for`, `if`, `_showHelpAndExit`, `catch`, `_showHelp`, `_addAllowedOptions`, `_addPositionalOptionForBaseDir`, `_showVersionAndExit`. Primary includes/dependencies visible in the file include `Parser.h`, `iostream`, `boost/optional.hpp`, `cryfs/impl/config/CryConfigConsole.h`, `cryfs/impl/CryfsException.h`, `cryfs-cli/Environment.h`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `Parser.h`, `iostream`, `boost/optional.hpp`, `cryfs/impl/config/CryConfigConsole.h`, `cryfs/impl/CryfsException.h`, `cryfs-cli/Environment.h`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/Parser.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/Parser.h -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/Parser.h

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 38 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `Parser`. Macros/constants: `MESSMER_CRYFSUNMOUNT_PROGRAMOPTIONS_PARSER_H`. Important declarations or call sites include `Parser(int argc, const char **argv);`; `ProgramOptions parse() const;`; `static std::vector<std::string> _argsToVector(int argc, const char **argv);`; `static std::vector<const char*> _to_const_char_vector(const std::vector<std::string> &options);`; `static void _addAllowedOptions(boost::program_options::options_description *desc);`; `static void _showHelp();`; `[[noreturn]] static void _showHelpAndExit(const std::string& message, cryfs::ErrorCode errorCode);`; `[[noreturn]] static void _showCiphersAndExit(const std::vector<std::string> &supportedCiphers);`; `[[noreturn]] static void _showVersionAndExit();`; `static boost::program_options::variables_map _parseOptionsOrShowHelp(const std::vector<std::string> &options);`. CMake commands used here include `Parser`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `ProgramOptions.h`, `boost/program_options.hpp`, `cryfs/impl/ErrorCodes.h`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `ProgramOptions.h`, `boost/program_options.hpp`, `cryfs/impl/ErrorCodes.h`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/Parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/ProgramOptions.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/ProgramOptions.cpp

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 35 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `_mountDir = bf::absolute(std::move(_mountDir));`. CMake commands used here include `_mountDirIsDriveLetter`, `_immediate`, `if`. Primary includes/dependencies visible in the file include `ProgramOptions.h`, `cstring`, `cpp-utils/assert/assert.h`, `cpp-utils/system/path.h`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `ProgramOptions.h`, `cstring`, `cpp-utils/assert/assert.h`, `cpp-utils/system/path.h`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/ProgramOptions.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/ProgramOptions.h -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/ProgramOptions.h

## Purpose
Implements the `cryfs-unmount` command-line parser and entry path that validates options, calls FUSE unmount, and maps CryFS exceptions to exit codes. This specific file has 36 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ProgramOptions`. Macros/constants: `MESSMER_CRYFSUNMOUNT_PROGRAMOPTIONS_PROGRAMOPTIONS_H`. Important declarations or call sites include `ProgramOptions(boost::filesystem::path mountDir, bool immediate);`; `const boost::filesystem::path &mountDir() const;`; `bool mountDirIsDriveLetter() const;`; `bool immediate() const;`; `DISALLOW_COPY_AND_ASSIGN(ProgramOptions);`. CMake commands used here include `ProgramOptions`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `vector`, `string`, `boost/optional.hpp`, `cpp-utils/macros.h`, `boost/filesystem.hpp`.

## Control Flow
The CLI parses Boost program options, validates mount directory existence/shape, retries immediate unmount when needed, and the process entrypoint maps known CryFS errors to process exit codes.

## State and Persistence Behavior
CLI option objects store parsed mount path and immediate flag. The command does not persist configuration; it changes mount state through FUSE.

## Dependencies and Integration Points
Integrates with Boost.Program_options/Filesystem, fspp FUSE unmounting, CryFS exception/error-code mapping, gitversion reporting, and cpp-utils backtrace support; visible includes are `vector`, `string`, `boost/optional.hpp`, `cpp-utils/macros.h`, `boost/filesystem.hpp`.

## Risks and Edge Cases
Unmount behavior is platform/FUSE dependent. Retrying immediate unmount needs clear error handling so users get correct exit codes for inaccessible or busy mount directories.

## Test Signals
CLI tests should cover help/version, missing mount dir, drive-letter handling, immediate flag parsing, FUSE unmount success/failure, and exception-to-exit-code mapping.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs-unmount/program_options/ProgramOptions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/CachingFsBlobStore.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/CachingFsBlobStore.cpp

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 49 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `optional<unique_ref<FsBlobRef>> CachingFsBlobStore::load(const BlockId &blockId) {`; `auto fromCache = _cache.pop(blockId);`; `if (fromCache != none) {`; `return _makeRef(std::move(*fromCache));`; `auto fromBaseStore = _baseBlobStore->load(blockId);`; `if (fromBaseStore != none) {`; `return _makeRef(std::move(*fromBaseStore));`; `unique_ref<FsBlobRef> CachingFsBlobStore::_makeRef(unique_ref<FsBlob> baseBlob) {`; `auto fileBlob = dynamic_pointer_move<FileBlob>(baseBlob);`; `if (fileBlob != none) {`. CMake commands used here include `if`, `ASSERT`. Primary includes/dependencies visible in the file include `CachingFsBlobStore.h`, `cryfs/impl/filesystem/fsblobstore/FsBlobStore.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `CachingFsBlobStore.h`, `cryfs/impl/filesystem/fsblobstore/FsBlobStore.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

## File-Specific Notes
- `_makeRef` uses `dynamic_pointer_move` to wrap base file, directory, or symlink blobs in the matching cached reference type.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/CachingFsBlobStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/CachingFsBlobStore.h -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/CachingFsBlobStore.h

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 115 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CachingFsBlobStore`. Macros/constants: `MESSMER_CRYFS_FILESYSTEM_CACHINGFSBLOBSTORE_CACHINGFSBLOBSTORE_H`. Important declarations or call sites include `CachingFsBlobStore(cpputils::unique_ref<fsblobstore::FsBlobStore> baseBlobStore);`; `~CachingFsBlobStore();`; `cpputils::unique_ref<FileBlobRef> createFileBlob(const blockstore::BlockId &parent);`; `cpputils::unique_ref<DirBlobRef> createDirBlob(const blockstore::BlockId &parent);`; `cpputils::unique_ref<SymlinkBlobRef> createSymlinkBlob(const boost::filesystem::path &target, const blockstore::BlockId &parent);`; `boost::optional<cpputils::unique_ref<FsBlobRef>> load(const blockstore::BlockId &blockId);`; `void remove(cpputils::unique_ref<FsBlobRef> blob);`; `void remove(const blockstore::BlockId &blockId);`; `uint64_t virtualBlocksizeBytes() const;`; `uint64_t numBlocks() const;`. CMake commands used here include `CachingFsBlobStore`, `DISALLOW_COPY_AND_ASSIGN`, `if`, `remove`. Primary includes/dependencies visible in the file include `cpp-utils/pointer/unique_ref.h`, `cryfs/impl/filesystem/fsblobstore/FsBlobStore.h`, `blockstore/implementations/caching/cache/Cache.h`, `FileBlobRef.h`, `DirBlobRef.h`, `SymlinkBlobRef.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `cpp-utils/pointer/unique_ref.h`, `cryfs/impl/filesystem/fsblobstore/FsBlobStore.h`, `blockstore/implementations/caching/cache/Cache.h`, `FileBlobRef.h`, `DirBlobRef.h`, `SymlinkBlobRef.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/CachingFsBlobStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/DirBlobRef.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/DirBlobRef.cpp

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `DirBlobRef.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `DirBlobRef.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/DirBlobRef.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/DirBlobRef.h -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/DirBlobRef.h

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 112 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `DirBlobRef`. Macros/constants: `MESSMER_CRYFS_FILESYSTEM_CACHINGFSBLOBSTORE_DIRBLOBREF_H`. Important declarations or call sites include `_base(dynamic_cast<fsblobstore::DirBlob*>(baseBlob())) {`; `ASSERT(_base != nullptr, "We just initialized this with a pointer to DirBlob. Can't be something else now.");`; `boost::optional<const Entry&> GetChild(const std::string &name) const {`; `return _base->GetChild(name);`; `boost::optional<const Entry&> GetChild(const blockstore::BlockId &blockId) const {`; `return _base->GetChild(blockId);`; `size_t NumChildren() const {`; `return _base->NumChildren();`; `void RemoveChild(const blockstore::BlockId &blockId) {`; `return _base->RemoveChild(blockId);`. CMake commands used here include `DirBlobRef`, `FsBlobRef`, `_base`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/DirBlob.h`, `fspp/fs_interface/Node.h`, `fspp/fs_interface/Context.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/DirBlob.h`, `fspp/fs_interface/Node.h`, `fspp/fs_interface/Context.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/DirBlobRef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FileBlobRef.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FileBlobRef.cpp

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `FileBlobRef.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `FileBlobRef.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FileBlobRef.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FileBlobRef.h -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FileBlobRef.h

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 58 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `FileBlobRef`. Macros/constants: `MESSMER_CRYFS_FILESYSTEM_CACHINGFSBLOBSTORE_FILEBLOBREF_H`. Important declarations or call sites include `_base(dynamic_cast<fsblobstore::FileBlob*>(baseBlob())) {`; `ASSERT(_base != nullptr, "We just initialized this with a pointer to FileBlob. Can't be something else now.");`; `void resize(fspp::num_bytes_t size) {`; `return _base->resize(size);`; `fspp::num_bytes_t size() const {`; `return _base->size();`; `fspp::num_bytes_t read(void *target, fspp::num_bytes_t offset, fspp::num_bytes_t count) const {`; `return _base->read(target, offset, count);`; `void write(const void *source, fspp::num_bytes_t offset, fspp::num_bytes_t count) {`; `return _base->write(source, offset, count);`. CMake commands used here include `FileBlobRef`, `_base`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/FileBlob.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/FileBlob.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FileBlobRef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FsBlobRef.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FsBlobRef.cpp

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 15 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `FsBlobRef::~FsBlobRef() {`; `if (_baseBlob.is_valid()) {`; `_fsBlobStore->releaseForCache(std::move(_baseBlob));`. CMake commands used here include `if`. Primary includes/dependencies visible in the file include `FsBlobRef.h`, `CachingFsBlobStore.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `FsBlobRef.h`, `CachingFsBlobStore.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

## File-Specific Notes
- The `FsBlobRef` destructor returns a still-valid base blob to `CachingFsBlobStore::releaseForCache`; `releaseBaseBlob` disables that path by moving ownership out.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FsBlobRef.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FsBlobRef.h -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FsBlobRef.h

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 48 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `CachingFsBlobStore`, `FsBlobRef`. Macros/constants: `MESSMER_CRYFS_FILESYSTEM_CACHINGFSBLOBSTORE_FSBLOBREF_H`. Important declarations or call sites include `virtual ~FsBlobRef();`; `virtual const blockstore::BlockId &blockId() const = 0;`; `virtual fspp::num_bytes_t lstat_size() const = 0;`; `const blockstore::BlockId &parentPointer() const {`; `return _baseBlob->parentPointer();`; `void setParentPointer(const blockstore::BlockId &parentBlobId) {`; `return _baseBlob->setParentPointer(parentBlobId);`; `cpputils::unique_ref<fsblobstore::FsBlob> releaseBaseBlob() {`; `return std::move(_baseBlob);`; `FsBlobRef(cpputils::unique_ref<fsblobstore::FsBlob> baseBlob, cachingfsblobstore::CachingFsBlobStore *fsBlobStore): _fsBlobStor...`. CMake commands used here include `FsBlobRef`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `cryfs/impl/filesystem/fsblobstore/FsBlob.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `cryfs/impl/filesystem/fsblobstore/FsBlob.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/FsBlobRef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/SymlinkBlobRef.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/SymlinkBlobRef.cpp

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 2 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Primary includes/dependencies visible in the file include `SymlinkBlobRef.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `SymlinkBlobRef.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

## File-Specific Notes
- This file is intentionally tiny; its main role is to provide the translation unit or include anchor for inline/template definitions in the paired header.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/SymlinkBlobRef.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/SymlinkBlobRef.h -->
# sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/SymlinkBlobRef.h

## Purpose
Wraps the lower-level FsBlobStore with short-lived blob references that return released blobs to an in-memory cache on destruction. This specific file has 42 source lines under `sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `SymlinkBlobRef`. Macros/constants: `MESSMER_CRYFS_FILESYSTEM_CACHINGFSBLOBSTORE_SYMLINKBLOBREF_H`. Important declarations or call sites include `_base(dynamic_cast<fsblobstore::SymlinkBlob*>(baseBlob())) {`; `ASSERT(_base != nullptr, "We just initialized this with a pointer to SymlinkBlob. Can't be something else now.");`; `const boost::filesystem::path &target() const {`; `return _base->target();`; `const blockstore::BlockId &blockId() const override {`; `return _base->blockId();`; `fspp::num_bytes_t lstat_size() const override {`; `return _base->lstat_size();`; `DISALLOW_COPY_AND_ASSIGN(SymlinkBlobRef);`. CMake commands used here include `SymlinkBlobRef`, `_base`, `ASSERT`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/SymlinkBlob.h`.

## Control Flow
Loads first pop a blob from cache, then fall back to the base store. Ref wrappers forward file/dir/symlink operations to the base blob, and their destructor returns still-owned blobs to the cache.

## State and Persistence Behavior
The wrapper owns the base blob store and an in-memory cache keyed by `BlockId`. Blob contents persist through the base store; cache entries are transient and bounded.

## Dependencies and Integration Points
Integrates with `fsblobstore::FsBlobStore`, `FsBlob` subclasses, blockstore `BlockId`, cpp-utils ownership pointers, and cache primitives; visible includes are `FsBlobRef.h`, `cryfs/impl/filesystem/fsblobstore/SymlinkBlob.h`.

## Risks and Edge Cases
Returning blobs to cache in destructors means ownership transfer must be exact. Removing a blob must evict cached copies to avoid stale references.

## Test Signals
Test cache hit/miss, destructor return-to-cache, remove eviction, dynamic ref type selection, parent pointer forwarding, and forwarding of file/dir/symlink operations.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/cryfs/impl/filesystem/cachingfsblobstore/SymlinkBlobRef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/CMakeLists.txt

## Purpose
Describes how this source subtree is built, which sources enter the library or executable, and which third-party or sibling CryFS components are linked. This specific file has 3 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
CMake commands used here include `add_subdirectory`.

## Control Flow
CMake control is declarative: sources are grouped into targets, include directories are exposed, and link dependencies connect this subtree to Boost, Crypto++, fspp, blockstore, and CryFS components.

## State and Persistence Behavior
No runtime state is stored. The build graph persists only as generated build-system metadata.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
Build scripts can silently omit files or platform-specific sources; target/link changes should be validated on Linux and Windows configurations.

## Test Signals
Validate by configuring and building the old-cpp tree on supported platforms, including test targets and platform-specific source selection.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsTest.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsTest.h

## Purpose
Defines reusable typed GoogleTest suites that exercise fspp device, directory, file, symlink, rename, stat, and timestamp behavior against filesystem fixtures. This specific file has 42 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp/fstest` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_FSPP_FSTEST_FSTEST_H_`, `FSPP_ADD_FILESYTEM_TESTS`. Important declarations or call sites include `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppDeviceTest_One,             FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppDeviceTest_Two,             FIXTURE);  \`; `INSTANTIATE_NODE_TEST_SUITE(   FS_NAME, FsppDeviceTest_Timestamps,      FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppDirTest,                    FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppDirTest_Timestamps,         FIXTURE);  \`; `INSTANTIATE_NODE_TEST_SUITE(   FS_NAME, FsppDirTest_Timestamps_Entries, FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppFileTest,                   FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppFileTest_Timestamps,        FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppSymlinkTest,                FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppSymlinkTest_Timestamps,     FIXTURE);  \`. CMake commands used here include `INSTANTIATE_TYPED_TEST_SUITE_P`, `INSTANTIATE_NODE_TEST_SUITE`. Primary includes/dependencies visible in the file include `testutils/FileSystemTest.h`, `FsppDeviceTest.h`, `FsppDirTest.h`, `FsppFileTest.h`, `FsppSymlinkTest.h`, `FsppNodeTest_Rename.h`, `FsppNodeTest_Stat.h`, `FsppOpenFileTest.h`, `FsppDeviceTest_Timestamps.h`, `FsppNodeTest_Timestamps.h`.

## Control Flow
Each typed test constructs fixture files or directories, performs fspp API calls, and asserts POSIX-like results, errors, children, or timestamp changes through shared fixture utilities.

## State and Persistence Behavior
Tests create fixture filesystem state through the fixture device and assert behavior; no production persistence is implemented in these headers.

## Dependencies and Integration Points
Integrates with GoogleTest typed suites, fspp node/device interfaces, errno exceptions, and fixture utilities; visible includes are `testutils/FileSystemTest.h`, `FsppDeviceTest.h`, `FsppDirTest.h`, `FsppFileTest.h`, `FsppSymlinkTest.h`, `FsppNodeTest_Rename.h`, `FsppNodeTest_Stat.h`, `FsppOpenFileTest.h`.

## Risks and Edge Cases
These tests assume POSIX-like semantics and fixture correctness. Flaky timestamp granularity or filesystem-specific behavior can cause false failures.

## Test Signals
These headers are themselves test suites; instantiate them against filesystem fixtures and watch for POSIX errno, directory listing, rename/stat, and timestamp regressions.

## File-Specific Notes
- This is reusable test code rather than production code; its integration point is the fixture type passed to GoogleTest typed suites.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDeviceTest.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDeviceTest.h

## Purpose
Defines reusable typed GoogleTest suites that exercise fspp device, directory, file, symlink, rename, stat, and timestamp behavior against filesystem fixtures. This specific file has 471 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp/fstest` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ConcreteFileSystemTestFixture`, `FsppDeviceTest`, `FsppDeviceTest_One`, `FsppDeviceTest_Two`. Macros/constants: `MESSMER_FSPP_FSTEST_FSPPDEVICETEST_H_`. Important declarations or call sites include `void InitDirStructure() {`; `this->LoadDir("/")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createSymlink("mysymlink", "/symlink/target", fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createDir("mydir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createDir("myemptydir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createAndOpenFile("myfile2", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createSymlink("mysymlink", "/symlink/target", fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createDir("mysubdir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir/mysubdir")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`. CMake commands used here include `TYPED_TEST_SUITE_P`, `TYPED_TEST_P`, `EXPECT_THROW`, `EXPECT_EQ`, `REGISTER_TYPED_TEST_SUITE_P`. Primary includes/dependencies visible in the file include `fspp/fs_interface/FuseErrnoException.h`.

## Control Flow
Each typed test constructs fixture files or directories, performs fspp API calls, and asserts POSIX-like results, errors, children, or timestamp changes through shared fixture utilities.

## State and Persistence Behavior
Tests create fixture filesystem state through the fixture device and assert behavior; no production persistence is implemented in these headers.

## Dependencies and Integration Points
Integrates with GoogleTest typed suites, fspp node/device interfaces, errno exceptions, and fixture utilities; visible includes are `fspp/fs_interface/FuseErrnoException.h`.

## Risks and Edge Cases
These tests assume POSIX-like semantics and fixture correctness. Flaky timestamp granularity or filesystem-specific behavior can cause false failures.

## Test Signals
These headers are themselves test suites; instantiate them against filesystem fixtures and watch for POSIX errno, directory listing, rename/stat, and timestamp regressions.

## File-Specific Notes
- This is reusable test code rather than production code; its integration point is the fixture type passed to GoogleTest typed suites.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDeviceTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDeviceTest_Timestamps.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDeviceTest_Timestamps.h

## Purpose
Defines reusable typed GoogleTest suites that exercise fspp device, directory, file, symlink, rename, stat, and timestamp behavior against filesystem fixtures. This specific file has 50 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp/fstest` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ConcreteFileSystemTestFixture`, `FsppDeviceTest_Timestamps`. Macros/constants: `MESSMER_FSPP_FSTEST_FSPPDEVICETEST_TIMESTAMPS_H_`. Important declarations or call sites include `void Test_Load_While_Loaded() {`; `auto node = this->CreateNode("/mynode");`; `this->device->Load("/mynode");`; `this->EXPECT_OPERATION_UPDATES_TIMESTAMPS_AS("/mynode", operation(), {this->ExpectDoesntUpdateAnyTimestamps});`; `void Test_Load_While_Not_Loaded() {`; `auto node = this->CreateNode("/mynode");`; `oldStat = this->stat(*node);`; `this->ensureNodeTimestampsAreOld(oldStat);`; `this->device->Load("/myfile");`; `auto node = this->device->Load("/mynode");`. CMake commands used here include `EXPECT_EQ`, `REGISTER_NODE_TEST_SUITE`. Primary includes/dependencies visible in the file include `testutils/TimestampTestUtils.h`.

## Control Flow
Each typed test constructs fixture files or directories, performs fspp API calls, and asserts POSIX-like results, errors, children, or timestamp changes through shared fixture utilities.

## State and Persistence Behavior
Tests create fixture filesystem state through the fixture device and assert behavior; no production persistence is implemented in these headers.

## Dependencies and Integration Points
Integrates with GoogleTest typed suites, fspp node/device interfaces, errno exceptions, and fixture utilities; visible includes are `testutils/TimestampTestUtils.h`.

## Risks and Edge Cases
These tests assume POSIX-like semantics and fixture correctness. Flaky timestamp granularity or filesystem-specific behavior can cause false failures.

## Test Signals
These headers are themselves test suites; instantiate them against filesystem fixtures and watch for POSIX errno, directory listing, rename/stat, and timestamp regressions.

## File-Specific Notes
- This is reusable test code rather than production code; its integration point is the fixture type passed to GoogleTest typed suites.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDeviceTest_Timestamps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDirTest.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDirTest.h

## Purpose
Defines reusable typed GoogleTest suites that exercise fspp device, directory, file, symlink, rename, stat, and timestamp behavior against filesystem fixtures. This specific file has 306 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp/fstest` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ConcreteFileSystemTestFixture`, `FsppDirTest`, `Entry`. Macros/constants: `MESSMER_FSPP_FSTEST_FSPPDIRTEST_H_`. Important declarations or call sites include `void InitDirStructure() {`; `this->LoadDir("/")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createDir("mydir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createDir("myemptydir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createAndOpenFile("myfile2", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createDir("mysubdir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir/mysubdir")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir/mysubdir")->createDir("mysubsubdir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `void EXPECT_CHILDREN_ARE(const boost::filesystem::path &path, const std::initializer_list<fspp::Dir::Entry> expected) {`. CMake commands used here include `EXPECT_CHILDREN_ARE`, `EXPECT_UNORDERED_EQ`, `EXPECT_EQ`, `for`, `removeOne`, `if`, `EXPECT_TRUE`, `TYPED_TEST_SUITE_P`, `TYPED_TEST_P`, `FileEntry`, `DirEntry`, `EXPECT_ANY_THROW`.

## Control Flow
Each typed test constructs fixture files or directories, performs fspp API calls, and asserts POSIX-like results, errors, children, or timestamp changes through shared fixture utilities.

## State and Persistence Behavior
Tests create fixture filesystem state through the fixture device and assert behavior; no production persistence is implemented in these headers.

## Dependencies and Integration Points
Integrates with GoogleTest typed suites, fspp node/device interfaces, errno exceptions, and fixture utilities; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
These tests assume POSIX-like semantics and fixture correctness. Flaky timestamp granularity or filesystem-specific behavior can cause false failures.

## Test Signals
These headers are themselves test suites; instantiate them against filesystem fixtures and watch for POSIX errno, directory listing, rename/stat, and timestamp regressions.

## File-Specific Notes
- This is reusable test code rather than production code; its integration point is the fixture type passed to GoogleTest typed suites.

<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDirTest.h -->
