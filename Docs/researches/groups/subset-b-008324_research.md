# subset-b-008324 Research
<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/UtilsTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/UtilsTest.cpp

Purpose: This test suite verifies `cryfs-cli/program_options/utils.h`, especially `splitAtDoubleDash`, which divides CLI arguments into CryFS-owned options and passthrough options after a `--` separator.

Important APIs/types/functions: It uses `ProgramOptionsTestBase`, `splitAtDoubleDash`, and argument vectors containing short options, long options, positional options, and one or more double-dash separators. Direct tests: ProgramOptionsUtilsTest.SplitAtDoubleDash_ZeroOptions; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneShortOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneLongOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OnePositionalOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneShortOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneLongOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_OnePositionalOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_DoubleDash_OneShortOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_DoubleDash_OneLongOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_DoubleDash_OnePositionalOption.

Control flow: Each `TEST_F` constructs an input vector, calls the split utility, and checks both returned vectors with `EXPECT_VECTOR_EQ`. The cases cover empty input, separator at beginning/end/middle, options on either side, and preservation of positional strings.

State and persistence behavior: The utility and tests are pure in-memory argument processing; there is no filesystem or process state.

Dependencies and integration points: The split behavior feeds CryFS CLI option parsing, where arguments before `--` are interpreted by CryFS and arguments after it are passed to lower-level mount/FUSE handling.

Risks: Incorrect separator handling can make CryFS consume FUSE options or can pass CryFS-specific flags through to the wrong layer. Edge cases around repeated or terminal separators are especially sensitive for command compatibility.

Test signals: Primary signals are ProgramOptionsUtilsTest.SplitAtDoubleDash_ZeroOptions; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneShortOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneLongOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OnePositionalOption; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneShortOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_OneLongOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_OnePositionalOption_DoubleDash; ProgramOptionsUtilsTest.SplitAtDoubleDash_DoubleDash_OneShortOption. Assertion/mocking density: none visible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/UtilsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/testutils/ProgramOptionsTestBase.h -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/testutils/ProgramOptionsTestBase.h

Purpose: This header provides `ProgramOptionsTestBase`, a small Google Test base fixture for command-line program-option tests. Its main job is a reusable vector comparison helper for argument-list assertions.

Important APIs/types/functions: It includes `gtest/gtest.h`, derives `ProgramOptionsTestBase` from `::testing::Test`, and exposes `EXPECT_VECTOR_EQ`, which checks vector sizes and then compares each indexed element.

Control flow: Tests subclass the fixture, build expected and actual vectors, and call `EXPECT_VECTOR_EQ`; the helper first verifies cardinality, then loops through the expected vector to produce per-position equality failures.

State and persistence behavior: There is no persistent state. The only state is local vector data supplied by each test case.

Dependencies and integration points: The helper is consumed by `UtilsTest.cpp` and any other CLI option parser tests that need stable assertions on `std::vector<std::string>` results.

Risks: If vector sizes differ, the loop still uses the expected vector's size, so callers depend on Google Test failure reporting rather than early return. The helper is intentionally narrow and does not provide diff-style diagnostics.

Test signals: Fixture users get direct size equality and element-by-element equality checks for parsed argument vectors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/program_options/testutils/ProgramOptionsTestBase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/testutils/CliTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/testutils/CliTest.cpp

Purpose: This translation unit includes `CliTest.h` so the CLI test fixture header is compiled as part of the test target. It does not add behavior beyond forcing compile/link validation for the header-only fixture methods.

Important APIs/types/functions: The only dependency is `CliTest.h`; all fixture APIs are defined inline in that header.

Control flow: Build flow includes this file in the test executable, which compiles the fixture definitions and catches missing includes or incompatible inline code.

State and persistence behavior: No runtime state is created here.

Dependencies and integration points: It connects the CLI fixture header to the CMake source list and Google Test executable.

Risks: Because behavior lives in the header, test coverage depends on downstream test files actually using the fixture.

Test signals: Successful compilation is the main signal from this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/testutils/CliTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/testutils/CliTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/testutils/CliTest.h

Purpose: This header defines `CliTest`, a rich Google Test fixture for end-to-end CryFS CLI tests. It provides temporary basedir/mountdir/config paths, fake home-directory behavior, mock console state, fake HTTP version-checking, mount/unmount helpers, and process-level execution helpers.

Important APIs/types/functions: It includes `cryfs-cli/Cli.h`, `VersionChecker`, `FakeHttpClient`, subprocess and tempfile utilities, Dokan/FUSE unmount support, and `TestWithFakeHomeDirectory`. Important methods include `run`, `run_filesystem`, `EXPECT_EXIT_WITH_HELP_MESSAGE`, `_unmount`, `_exit`, `_createDir`, and `_testFs`.

Control flow: A test constructs the fixture, invokes `run` with CLI arguments, and the helper drives `Cli` while collecting exit code, stdout/stderr, logging, mount lifecycle, and fake network responses. Filesystem-oriented tests can call `run_filesystem` to start a mounted filesystem and synchronize startup with condition barriers.

State and persistence behavior: The fixture owns temp directories/files for basedir, mountdir, config, local state, and mount lifecycle. It also mutates fake home-directory state and can launch subprocess/unmount activity, so cleanup and teardown ordering matter.

Dependencies and integration points: This is the main integration harness for CryFS CLI, console I/O, version checking, local state, mount setup, and platform-specific unmount behavior.

Risks: CLI tests using this fixture can be timing-sensitive around mount startup and unmount. Platform differences between Dokan and FUSE, process exit handling, and fake HTTP state can affect determinism.

Test signals: Expected exit codes, help text, mounted filesystem availability, unmount completion, fake HTTP calls, and temp path side effects are the observable signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs-cli/testutils/CliTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/CMakeLists.txt

Purpose: This CMake file defines the `cryfs-test` test executable for the CryFS legacy C++ tree. It enumerates the test sources in this subtree, links the executable to the production libraries and Google Test support, registers it with CTest, and applies the repository's C++14 and style-warning helpers.

Important APIs/types/functions: The important build APIs are `project`, `set(SOURCES)`, `add_executable`, `target_link_libraries`, `add_test`, `target_enable_style_warnings`, and `target_activate_cpp14`. The source list is the integration surface: changing it determines which config, filesystem, local-state, fspp interface, and FUSE adapter tests actually run.

Control flow: Configure-time evaluation collects the listed sources into one executable target, then target creation and link steps bind it to the relevant production library. Test execution is delegated to CTest through the `add_test` registration.

State and persistence behavior: The file persists no runtime state. Its state effect is build-system state: generated target metadata, dependency edges, compiler mode, warning policy, and CTest registration in the build directory.

Dependencies and integration points: It integrates this test subtree with `my-gtest-main`, `googletest`, and the matching production libraries. It is the bridge between individual source files and CI/test runners.

Risks: Missing a source in `SOURCES` silently removes coverage from the executable. A stale link library or C++ standard setting can mask source-level correctness by preventing the tests from building.

Test signals: A successful configure/build produces the `cryfs-test` executable, and a successful CTest invocation proves all listed source files compiled and linked into the expected test target.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CompatibilityTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CompatibilityTest.cpp

Purpose: This file verifies that historical CryFS config blobs, encoded as hex fixtures for older versions and ciphers, can still be decrypted and loaded with the current config code.

Important APIs/types/functions: Includes: gtest/gtest.h, vector, boost/filesystem.hpp, cpp-utils/data/Data.h, vendor_cryptopp/hex.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/tempfile/TempFile.h, cryfs/impl/config/CryConfigFile.h, cryfs/impl/config/CryPresetPasswordBasedKeyProvider.h, plus 1 more. Classes/fixtures: CryConfigCompatibilityTest. Helper functions: loadConfigFromHex, storeHexToFile, hexToBinary. Direct tests: CryConfigCompatibilityTest.v0_8_1_with_aes_256_gcm; CryConfigCompatibilityTest.v0_8_1_with_serpent_128_cfb.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: It writes binary config data from hex into a temporary file, then loads that file through `CryConfigFile` using a preset password-derived key provider. Persistent state is the temp config file representing legacy on-disk format.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: The test relies on fixed legacy hex fixtures and exact password/cipher compatibility. It is strong for known historical formats but not exhaustive for every old config variant.

Test signals: Primary signals are CryConfigCompatibilityTest.v0_8_1_with_aes_256_gcm; CryConfigCompatibilityTest.v0_8_1_with_serpent_128_cfb. Assertion/mocking density: EXPECT_EQ x4.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CompatibilityTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryCipherTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryCipherTest.cpp

Purpose: This file locks down cipher lookup, supported cipher-name enumeration, warning metadata, and encryption-key sizing for CryFS block ciphers.

Important APIs/types/functions: Includes: gtest/gtest.h, gmock/gmock.h, cryfs/impl/config/CryCipher.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h, cpp-utils/data/DataFixture.h, cpp-utils/random/Random.h. Classes/fixtures: CryCipherTest. Helper functions: EXPECT_FINDS_CORRECT_CIPHERS, EXPECT_FINDS_CORRECT_CIPHER, _loadBlock. Direct tests: CryCipherTest.FindsCorrectCipher; CryCipherTest.SupportedCipherNamesContainsACipher; CryCipherTest.ThereIsACipherWithoutWarning; CryCipherTest.ThereIsACipherWithIntegrityWarning; CryCipherTest.EncryptionKeyHasCorrectSize_448; CryCipherTest.EncryptionKeyHasCorrectSize_256; CryCipherTest.EncryptionKeyHasCorrectSize_128.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: No durable state is written; it checks static cipher registry metadata and encrypt/decrypt sizing with in-memory blocks and random keys.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Cipher registry changes can break compatibility or user-facing defaults. Tests focus on registered ciphers and metadata, not full cryptanalytic behavior.

Test signals: Primary signals are CryCipherTest.FindsCorrectCipher; CryCipherTest.SupportedCipherNamesContainsACipher; CryCipherTest.ThereIsACipherWithoutWarning; CryCipherTest.ThereIsACipherWithIntegrityWarning; CryCipherTest.EncryptionKeyHasCorrectSize_448; CryCipherTest.EncryptionKeyHasCorrectSize_256; CryCipherTest.EncryptionKeyHasCorrectSize_128. Assertion/mocking density: EXPECT_EQ x5, EXPECT_NE x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryCipherTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigConsoleTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigConsoleTest.cpp

Purpose: This file tests the interactive/noninteractive console layer that chooses ciphers, block sizes, and missing-block integrity policy during config creation.

Important APIs/types/functions: Includes: gtest/gtest.h, gmock/gmock.h, cryfs/impl/config/CryConfigConsole.h, cryfs/impl/config/CryCipher.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/io/NoninteractiveConsole.h, ../../impl/testutils/MockConsole.h. Classes/fixtures: CryConfigConsoleTest, CryConfigConsoleTest_Cipher, CryConfigConsoleTest_Cipher_Choose. Helper functions: CryConfigConsoleTest, EXPECT_DONT_SHOW_WARNING, EXPECT_SHOW_WARNING. Direct tests: CryConfigConsoleTest_Cipher.AsksForCipher; CryConfigConsoleTest_Cipher.ChooseDefaultCipher; CryConfigConsoleTest_Cipher.ChooseDefaultCipherWhenNoninteractiveEnvironment; CryConfigConsoleTest_Cipher.AsksForBlocksize; CryConfigConsoleTest_Cipher.AsksForMissingBlockIsIntegrityViolation; CryConfigConsoleTest_Cipher.ChooseDefaultBlocksizeWhenNoninteractiveEnvironment; CryConfigConsoleTest_Cipher_Choose.ChoosesCipherCorrectly.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is mock-console expectation state plus chosen config values returned from console helper methods. No config file is persisted directly here.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Exact prompt flow can be brittle, but the brittleness is useful because these prompts are user-facing setup contracts.

Test signals: Primary signals are CryConfigConsoleTest_Cipher.AsksForCipher; CryConfigConsoleTest_Cipher.ChooseDefaultCipher; CryConfigConsoleTest_Cipher.ChooseDefaultCipherWhenNoninteractiveEnvironment; CryConfigConsoleTest_Cipher.AsksForBlocksize; CryConfigConsoleTest_Cipher.AsksForMissingBlockIsIntegrityViolation; CryConfigConsoleTest_Cipher.ChooseDefaultBlocksizeWhenNoninteractiveEnvironment; CryConfigConsoleTest_Cipher_Choose.ChoosesCipherCorrectly. Assertion/mocking density: EXPECT_EQ x4, EXPECT_CALL x14.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigConsoleTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigCreatorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigCreatorTest.cpp

Purpose: This file tests `CryConfigCreator`, the component that creates new CryFS configs from command options, console answers, defaults, local state, and version information.

Important APIs/types/functions: Includes: gtest/gtest.h, gmock/gmock.h, cryfs/impl/config/CryConfigCreator.h, cryfs/impl/config/CryCipher.h, cpp-utils/crypto/symmetric/ciphers.h, ../../impl/testutils/MockConsole.h, ../../impl/testutils/TestWithFakeHomeDirectory.h, cpp-utils/io/NoninteractiveConsole.h, gitversion/gitversion.h, plus 1 more. Classes/fixtures: CryConfigCreatorTest. Helper functions: CryConfigCreatorTest, AnswerNoToDefaultSettings, AnswerYesToDefaultSettings. Direct tests: CryConfigCreatorTest.DoesAskForCipherIfNotSpecified; CryConfigCreatorTest.DoesNotAskForCipherIfSpecified; CryConfigCreatorTest.DoesNotAskForCipherIfUsingDefaultSettings; CryConfigCreatorTest.DoesNotAskForCipherIfNoninteractive; CryConfigCreatorTest.DoesAskForBlocksizeIfNotSpecified; CryConfigCreatorTest.DoesNotAskForBlocksizeIfSpecified; CryConfigCreatorTest.DoesNotAskForBlocksizeIfNoninteractive; CryConfigCreatorTest.DoesNotAskForBlocksizeIfUsingDefaultSettings; CryConfigCreatorTest.DoesAskWhetherMissingBlocksAreIntegrityViolationsIfNotSpecified; CryConfigCreatorTest.DoesNotAskWhetherMissingBlocksAreIntegrityViolationsIfSpecified_True; CryConfigCreatorTest.DoesNotAskWhetherMissingBlocksAreIntegrityViolationsIfSpecified_False; CryConfigCreatorTest.DoesNotAskWhetherMissingBlocksAreIntegrityViolationsIfNoninteractive.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: It writes temp config/local-state data through a fake home directory, tracks generated filesystem IDs, stores version strings, and verifies whether prompts are skipped or required.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Creation behavior combines CLI flags, interactive defaults, noninteractive mode, and local-state writes; regressions can silently produce incompatible filesystems.

Test signals: Primary signals are CryConfigCreatorTest.DoesAskForCipherIfNotSpecified; CryConfigCreatorTest.DoesNotAskForCipherIfSpecified; CryConfigCreatorTest.DoesNotAskForCipherIfUsingDefaultSettings; CryConfigCreatorTest.DoesNotAskForCipherIfNoninteractive; CryConfigCreatorTest.DoesAskForBlocksizeIfNotSpecified; CryConfigCreatorTest.DoesNotAskForBlocksizeIfSpecified; CryConfigCreatorTest.DoesNotAskForBlocksizeIfNoninteractive; CryConfigCreatorTest.DoesNotAskForBlocksizeIfUsingDefaultSettings. Assertion/mocking density: EXPECT_EQ x4, EXPECT_CALL x11.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigCreatorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigFileTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigFileTest.cpp

Purpose: This file tests encrypted config-file creation, loading, saving, wrong-password failure, and persistence of individual `CryConfig` fields.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/CryConfigFile.h, cpp-utils/tempfile/TempFile.h, cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h, ../../impl/testutils/FakeCryKeyProvider.h, boost/optional/optional_io.hpp. Classes/fixtures: CryConfigFileTest. Helper functions: CryConfigFileTest, Config, CreateAndLoadEmpty, Create, Load, CreateWithCipher. Direct tests: CryConfigFileTest.DoesntLoadIfWrongPassword; CryConfigFileTest.RootBlob_Init; CryConfigFileTest.RootBlob_CreateAndLoad; CryConfigFileTest.RootBlob_SaveAndLoad; CryConfigFileTest.EncryptionKey_Init; CryConfigFileTest.EncryptionKey_CreateAndLoad; CryConfigFileTest.EncryptionKey_SaveAndLoad; CryConfigFileTest.Cipher_Init; CryConfigFileTest.Cipher_CreateAndLoad; CryConfigFileTest.Cipher_SaveAndLoad; CryConfigFileTest.Version_Init; CryConfigFileTest.Version_CreateAndLoad.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: It writes real temporary config files and reloads them with fake key providers. Persistent fields under test include root blob, encryption key, cipher, version, created/opened versions, filesystem ID, block size, and integrity policy.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Serialization and encryption bugs here affect every mounted filesystem because config files are the root of key and format metadata.

Test signals: Primary signals are CryConfigFileTest.DoesntLoadIfWrongPassword; CryConfigFileTest.RootBlob_Init; CryConfigFileTest.RootBlob_CreateAndLoad; CryConfigFileTest.RootBlob_SaveAndLoad; CryConfigFileTest.EncryptionKey_Init; CryConfigFileTest.EncryptionKey_CreateAndLoad; CryConfigFileTest.EncryptionKey_SaveAndLoad; CryConfigFileTest.Cipher_Init. Assertion/mocking density: EXPECT_EQ x20.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigFileTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigLoaderTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigLoaderTest.cpp

Purpose: This file exercises load-or-create behavior for CryFS configs, including wrong passwords, cipher mismatch, config mutation on open, version upgrade checks, filesystem ID/local-state validation, and access modes.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/CryConfigLoader.h, cryfs/impl/config/CryPresetPasswordBasedKeyProvider.h, ../../impl/testutils/MockConsole.h, ../../impl/testutils/TestWithFakeHomeDirectory.h, cpp-utils/tempfile/TempFile.h, cpp-utils/random/Random.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/data/DataFixture.h, plus 6 more. Classes/fixtures: FakeRandomGenerator, CryConfigLoaderTest. Helper functions: FakeRandomGenerator, _get, keyProvider, loader, Create, LoadOrCreate, Load, expectLoadingModifiesFile, expectLoadingDoesntModifyFile, CreateWithRootBlob, plus 8 more. Direct tests: CryConfigLoaderTest.CreatesNewIfNotExisting; CryConfigLoaderTest.DoesntCrashIfExisting; CryConfigLoaderTest.DoesntLoadIfWrongPassword; CryConfigLoaderTest.DoesntLoadIfDifferentCipher; CryConfigLoaderTest.DoesntLoadIfDifferentCipher_Noninteractive; CryConfigLoaderTest.DoesLoadIfSameCipher; CryConfigLoaderTest.DoesLoadIfSameCipher_Noninteractive; CryConfigLoaderTest.RootBlob_Load; CryConfigLoaderTest.RootBlob_Create; CryConfigLoaderTest.EncryptionKey_Load; CryConfigLoaderTest.EncryptionKey_Load_whenKeyChanged_thenFails; CryConfigLoaderTest.EncryptionKey_Create.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: It owns a temporary config file and local-state directory under a fake home, writes configs with controlled random encryption keys, mutates on-disk config data, and compares file bytes before/after load.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: This is a high-blast-radius loader: incorrect behavior can corrupt configs, miss incompatible versions, or wrongly accept a filesystem from another basedir.

Test signals: Primary signals are CryConfigLoaderTest.CreatesNewIfNotExisting; CryConfigLoaderTest.DoesntCrashIfExisting; CryConfigLoaderTest.DoesntLoadIfWrongPassword; CryConfigLoaderTest.DoesntLoadIfDifferentCipher; CryConfigLoaderTest.DoesntLoadIfDifferentCipher_Noninteractive; CryConfigLoaderTest.DoesLoadIfSameCipher; CryConfigLoaderTest.DoesLoadIfSameCipher_Noninteractive; CryConfigLoaderTest.RootBlob_Load. Assertion/mocking density: EXPECT_EQ x19, ASSERT_EQ x3, EXPECT_THROW x1, EXPECT_TRUE x15, EXPECT_FALSE x2, EXPECT_CALL x9, EXPECT_NE x3, ASSERT_TRUE x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigLoaderTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigTest.cpp

Purpose: This file tests the in-memory `CryConfig` data model and its serialize/deserialize behavior for all config fields.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/CryConfig.h, cpp-utils/data/DataFixture.h, cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h. Classes/fixtures: CryConfigTest. Helper functions: SaveAndLoad. Direct tests: CryConfigTest.RootBlob_Init; CryConfigTest.RootBlob; CryConfigTest.RootBlob_AfterMove; CryConfigTest.RootBlob_AfterCopy; CryConfigTest.RootBlob_AfterSaveAndLoad; CryConfigTest.EncryptionKey_Init; CryConfigTest.EncryptionKey; CryConfigTest.EncryptionKey_AfterMove; CryConfigTest.EncryptionKey_AfterCopy; CryConfigTest.EncryptionKey_AfterSaveAndLoad; CryConfigTest.Cipher_Init; CryConfigTest.Cipher.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is mostly in-memory, with save/load round trips through serialized config data to verify persistence semantics after copy and move operations.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Optional-field and move/copy behavior must remain stable because config file code stores and retrieves these values across versions.

Test signals: Primary signals are CryConfigTest.RootBlob_Init; CryConfigTest.RootBlob; CryConfigTest.RootBlob_AfterMove; CryConfigTest.RootBlob_AfterCopy; CryConfigTest.RootBlob_AfterSaveAndLoad; CryConfigTest.EncryptionKey_Init; CryConfigTest.EncryptionKey; CryConfigTest.EncryptionKey_AfterMove. Assertion/mocking density: EXPECT_EQ x41.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryPasswordBasedKeyProviderTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryPasswordBasedKeyProviderTest.cpp

Purpose: This file tests the interactive password-based key provider, including double-entry confirmation for new filesystems and single password prompt for existing filesystems.

Important APIs/types/functions: Includes: cryfs/impl/config/CryPasswordBasedKeyProvider.h, gmock/gmock.h, ../../impl/testutils/MockConsole.h, cpp-utils/data/DataFixture.h. Classes/fixtures: MockCallable, MockKDF, CryPasswordBasedKeyProviderTest. Helper functions: CryPasswordBasedKeyProviderTest. Direct tests: CryPasswordBasedKeyProviderTest.requestKeyForNewFilesystem; CryPasswordBasedKeyProviderTest.requestKeyForExistingFilesystem.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State consists of mock console password answers, mock KDF calls, and deterministic derived key data. No files are persisted.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Prompt sequencing and retry behavior are security-sensitive because weak or mismatched password handling affects filesystem access.

Test signals: Primary signals are CryPasswordBasedKeyProviderTest.requestKeyForNewFilesystem; CryPasswordBasedKeyProviderTest.requestKeyForExistingFilesystem. Assertion/mocking density: EXPECT_EQ x4, EXPECT_CALL x6.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryPasswordBasedKeyProviderTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryPresetPasswordBasedKeyProviderTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryPresetPasswordBasedKeyProviderTest.cpp

Purpose: This file tests the noninteractive preset-password key provider for new and existing filesystems.

Important APIs/types/functions: Includes: cryfs/impl/config/CryPresetPasswordBasedKeyProvider.h, gmock/gmock.h, ../../impl/testutils/MockConsole.h, cpp-utils/data/DataFixture.h. Classes/fixtures: MockKDF. Helper functions: none visible. Direct tests: CryPresetPasswordBasedKeyProviderTest.requestKeyForNewFilesystem; CryPresetPasswordBasedKeyProviderTest.requestKeyForExistingFilesystem.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is deterministic password input and mock KDF output; no console prompts or files are used.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: The provider bypasses confirmation prompts by design, so tests must ensure it still derives the same key material used by the interactive path.

Test signals: Primary signals are CryPresetPasswordBasedKeyProviderTest.requestKeyForNewFilesystem; CryPresetPasswordBasedKeyProviderTest.requestKeyForExistingFilesystem. Assertion/mocking density: EXPECT_EQ x4, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryPresetPasswordBasedKeyProviderTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/CryConfigEncryptorFactoryTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/CryConfigEncryptorFactoryTest.cpp

Purpose: This file tests the encryptor factory that builds config encryptors from a CryFS key provider and validates same/new encryptor decryptability and wrong-key failure.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/crypto/CryConfigEncryptorFactory.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/data/DataFixture.h, ../../../impl/testutils/FakeCryKeyProvider.h, cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h. Classes/fixtures: CryConfigEncryptorFactoryTest. Helper functions: none visible. Direct tests: CryConfigEncryptorFactoryTest.EncryptAndDecrypt_SameEncryptor; CryConfigEncryptorFactoryTest.EncryptAndDecrypt_NewEncryptor; CryConfigEncryptorFactoryTest.DoesntDecryptWithWrongKey; CryConfigEncryptorFactoryTest.DoesntDecryptWithWrongKey_EmptyData; CryConfigEncryptorFactoryTest.DoesntDecryptInvalidData.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: It uses in-memory plaintext/ciphertext and fake key providers; no durable state is written.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Factory/key-provider wiring errors can make existing configs undecryptable or accept corrupted data.

Test signals: Primary signals are CryConfigEncryptorFactoryTest.EncryptAndDecrypt_SameEncryptor; CryConfigEncryptorFactoryTest.EncryptAndDecrypt_NewEncryptor; CryConfigEncryptorFactoryTest.DoesntDecryptWithWrongKey; CryConfigEncryptorFactoryTest.DoesntDecryptWithWrongKey_EmptyData; CryConfigEncryptorFactoryTest.DoesntDecryptInvalidData. Assertion/mocking density: EXPECT_EQ x5.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/CryConfigEncryptorFactoryTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/CryConfigEncryptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/CryConfigEncryptorTest.cpp

Purpose: This file tests the full config encryptor that combines outer key-configuration encryption with inner payload encryption and selected cipher metadata.

Important APIs/types/functions: Includes: gtest/gtest.h, cpp-utils/data/DataFixture.h, cpp-utils/crypto/symmetric/ciphers.h, cryfs/impl/config/crypto/CryConfigEncryptor.h, boost/optional/optional_io.hpp. Classes/fixtures: CryConfigEncryptorTest. Helper functions: makeEncryptor, changeInnerCipherFieldTo, _derivedKey, _kdfParameters, _outerEncryptor, _decryptInnerConfig, _encryptInnerConfig. Direct tests: CryConfigEncryptorTest.EncryptAndDecrypt_Data_AES; CryConfigEncryptorTest.EncryptAndDecrypt_Data_Twofish; CryConfigEncryptorTest.EncryptAndDecrypt_Cipher_AES; CryConfigEncryptorTest.EncryptAndDecrypt_Cipher_Twofish; CryConfigEncryptorTest.EncryptAndDecrypt_EmptyData; CryConfigEncryptorTest.InvalidCiphertext; CryConfigEncryptorTest.DoesntEncryptWhenTooLarge; CryConfigEncryptorTest.EncryptionIsFixedSize; CryConfigEncryptorTest.SpecifiedInnerCipherIsUsed.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is serialized encrypted data, KDF parameters, derived keys, and optional inner config fields in memory.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Size limits, fixed-size ciphertext expectations, and inner-cipher selection are compatibility-critical for persisted config files.

Test signals: Primary signals are CryConfigEncryptorTest.EncryptAndDecrypt_Data_AES; CryConfigEncryptorTest.EncryptAndDecrypt_Data_Twofish; CryConfigEncryptorTest.EncryptAndDecrypt_Cipher_AES; CryConfigEncryptorTest.EncryptAndDecrypt_Cipher_Twofish; CryConfigEncryptorTest.EncryptAndDecrypt_EmptyData; CryConfigEncryptorTest.InvalidCiphertext; CryConfigEncryptorTest.DoesntEncryptWhenTooLarge; CryConfigEncryptorTest.EncryptionIsFixedSize. Assertion/mocking density: EXPECT_EQ x9, EXPECT_THROW x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/CryConfigEncryptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/inner/ConcreteInnerEncryptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/inner/ConcreteInnerEncryptorTest.cpp

Purpose: This file tests a concrete inner encryptor for config payload data across AES/Twofish paths, empty data, wrong cipher names, invalid ciphertext, size limits, and fixed encrypted size.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/crypto/inner/ConcreteInnerEncryptor.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/data/DataFixture.h, boost/optional/optional_io.hpp. Classes/fixtures: ConcreteInnerEncryptorTest. Helper functions: makeInnerEncryptor. Direct tests: ConcreteInnerEncryptorTest.EncryptAndDecrypt_AES; ConcreteInnerEncryptorTest.EncryptAndDecrypt_Twofish; ConcreteInnerEncryptorTest.EncryptAndDecrypt_EmptyData; ConcreteInnerEncryptorTest.DoesntDecryptWithWrongCipherName; ConcreteInnerEncryptorTest.InvalidCiphertext; ConcreteInnerEncryptorTest.DoesntEncryptWhenTooLarge; ConcreteInnerEncryptorTest.EncryptionIsFixedSize.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: All state is in-memory plaintext, ciphertext, cipher names, and keys.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Inner encryptor regressions can invalidate config payloads even when outer key wrapping succeeds.

Test signals: Primary signals are ConcreteInnerEncryptorTest.EncryptAndDecrypt_AES; ConcreteInnerEncryptorTest.EncryptAndDecrypt_Twofish; ConcreteInnerEncryptorTest.EncryptAndDecrypt_EmptyData; ConcreteInnerEncryptorTest.DoesntDecryptWithWrongCipherName; ConcreteInnerEncryptorTest.InvalidCiphertext; ConcreteInnerEncryptorTest.DoesntEncryptWhenTooLarge; ConcreteInnerEncryptorTest.EncryptionIsFixedSize. Assertion/mocking density: EXPECT_EQ x7, EXPECT_THROW x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/inner/ConcreteInnerEncryptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/inner/InnerConfigTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/inner/InnerConfigTest.cpp

Purpose: This file tests serialization of inner config metadata, especially encrypted data and cipher-name fields.

Important APIs/types/functions: Includes: gtest/gtest.h, cpp-utils/data/DataFixture.h, cryfs/impl/config/crypto/inner/InnerConfig.h, boost/optional/optional_io.hpp. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: InnerConfigTest.SomeValues; InnerConfigTest.DataEmpty; InnerConfigTest.CipherNameEmpty; InnerConfigTest.DataAndCipherNameEmpty; InnerConfigTest.InvalidSerialization.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is in-memory serialized/deserialized `InnerConfig` values, including empty-field cases and invalid serialization input.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Field absence/emptiness semantics must remain stable for config compatibility.

Test signals: Primary signals are InnerConfigTest.SomeValues; InnerConfigTest.DataEmpty; InnerConfigTest.CipherNameEmpty; InnerConfigTest.DataAndCipherNameEmpty; InnerConfigTest.InvalidSerialization. Assertion/mocking density: EXPECT_EQ x9.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/inner/InnerConfigTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/outer/OuterConfigTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/outer/OuterConfigTest.cpp

Purpose: This file tests serialization of outer config metadata, including encrypted inner data and KDF/key-configuration data.

Important APIs/types/functions: Includes: gtest/gtest.h, cpp-utils/data/DataFixture.h, cryfs/impl/config/crypto/outer/OuterConfig.h, boost/optional/optional_io.hpp. Classes/fixtures: OuterConfigTest. Helper functions: kdfParameters. Direct tests: OuterConfigTest.SomeValues; OuterConfigTest.DataEmpty; OuterConfigTest.KeyConfigEmpty; OuterConfigTest.DataAndKeyConfigEmpty; OuterConfigTest.InvalidSerialization.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is serialized/deserialized `OuterConfig` values with optional empty data/key-config combinations.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Outer config parsing is the first compatibility gate for encrypted config files.

Test signals: Primary signals are OuterConfigTest.SomeValues; OuterConfigTest.DataEmpty; OuterConfigTest.KeyConfigEmpty; OuterConfigTest.DataAndKeyConfigEmpty; OuterConfigTest.InvalidSerialization. Assertion/mocking density: EXPECT_EQ x9.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/outer/OuterConfigTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/outer/OuterEncryptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/outer/OuterEncryptorTest.cpp

Purpose: This file tests the outer encryptor that wraps inner config data with password-derived key information and enforces invalid-data/size/fixed-size behavior.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/crypto/outer/OuterEncryptor.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/data/DataFixture.h, boost/optional/optional_io.hpp. Classes/fixtures: OuterEncryptorTest. Helper functions: kdfParameters, makeOuterEncryptor. Direct tests: OuterEncryptorTest.EncryptAndDecrypt; OuterEncryptorTest.EncryptAndDecrypt_EmptyData; OuterEncryptorTest.InvalidCiphertext; OuterEncryptorTest.DoesntEncryptWhenTooLarge; OuterEncryptorTest.EncryptionIsFixedSize.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: All state is in-memory plaintext, ciphertext, KDF parameters, and derived keys.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Outer encryption failure prevents all config loading, while lax invalid-ciphertext handling could accept corrupt config files.

Test signals: Primary signals are OuterEncryptorTest.EncryptAndDecrypt; OuterEncryptorTest.EncryptAndDecrypt_EmptyData; OuterEncryptorTest.InvalidCiphertext; OuterEncryptorTest.DoesntEncryptWhenTooLarge; OuterEncryptorTest.EncryptionIsFixedSize. Assertion/mocking density: EXPECT_EQ x5, EXPECT_THROW x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/outer/OuterEncryptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryFsTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryFsTest.cpp

Purpose: This file tests that a newly created CryFS root directory can be reloaded after closing and that loading an existing filesystem does not mutate the config file.

Important APIs/types/functions: Includes: gtest/gtest.h, cpp-utils/tempfile/TempDir.h, cpp-utils/tempfile/TempFile.h, cpp-utils/pointer/cast.h, cryfs/impl/filesystem/CryDevice.h, cryfs/impl/filesystem/CryDir.h, cryfs/impl/filesystem/CryFile.h, cryfs/impl/filesystem/CryOpenFile.h, ../testutils/MockConsole.h, plus 5 more. Classes/fixtures: CryFsTest. Helper functions: CryFsTest, loadOrCreateConfig, failOnIntegrityViolation. Direct tests: CryFsTest.CreatedRootdirIsLoadableAfterClosing; CryFsTest.LoadingFilesystemDoesntModifyConfigFile.

Control flow: Fixture setup creates or loads a CryFS config/device, test code performs filesystem operations, and assertions verify node state, file contents, config bytes, or thrown errno exceptions.

State and persistence behavior: It uses temp basedir/config paths, fake home directory, mock console, `CryConfigLoader`, and `CryDevice`. The config file contents are persistent test state and are compared before/after loading.

Dependencies and integration points: It integrates CryFS filesystem objects with config loading, key providers, fake home/local-state helpers, cpp-utils temp files, and fspp interface expectations.

Risks: A load path that rewrites configs unnecessarily can cause noisy metadata changes or compatibility problems.

Test signals: Primary signals are CryFsTest.CreatedRootdirIsLoadableAfterClosing; CryFsTest.LoadingFilesystemDoesntModifyConfigFile. Assertion/mocking density: EXPECT_EQ x1, EXPECT_TRUE x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryFsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryNodeTest_Rename.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryNodeTest_Rename.cpp

Purpose: This file tests CryFS node rename behavior for files, directories, and symlinks, including block cleanup and parent pointer updates.

Important APIs/types/functions: Includes: gtest/gtest.h, testutils/CryTestBase.h, cryfs/impl/filesystem/CryOpenFile.h. Classes/fixtures: CryNodeTest_Rename. Helper functions: none visible. Direct tests: CryNodeTest_Rename.DoesntLeaveBlocksOver; CryNodeTest_Rename.Overwrite_DoesntLeaveBlocksOver; CryNodeTest_Rename.UpdatesParentPointers_File; CryNodeTest_Rename.UpdatesParentPointers_Dir; CryNodeTest_Rename.UpdatesParentPointers_Symlink.

Control flow: Fixture setup creates or loads a CryFS config/device, test code performs filesystem operations, and assertions verify node state, file contents, config bytes, or thrown errno exceptions.

State and persistence behavior: It uses `CryTestBase` to create real encrypted filesystem nodes in a temp basedir. Persistent state includes directory entries, node metadata, file blocks, and symlink targets.

Dependencies and integration points: It integrates CryFS filesystem objects with config loading, key providers, fake home/local-state helpers, cpp-utils temp files, and fspp interface expectations.

Risks: Rename bugs can orphan blocks, lose data, or leave parent pointers inconsistent after move/overwrite operations.

Test signals: Primary signals are CryNodeTest_Rename.DoesntLeaveBlocksOver; CryNodeTest_Rename.Overwrite_DoesntLeaveBlocksOver; CryNodeTest_Rename.UpdatesParentPointers_File; CryNodeTest_Rename.UpdatesParentPointers_Dir; CryNodeTest_Rename.UpdatesParentPointers_Symlink. Assertion/mocking density: EXPECT_EQ x4, EXPECT_TRUE x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryNodeTest_Rename.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryNodeTest_RenameNested.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryNodeTest_RenameNested.cpp

Purpose: This file parameterizes nested rename paths to verify valid moves succeed and invalid self/descendant moves fail with FUSE errno semantics.

Important APIs/types/functions: Includes: gtest/gtest.h, testutils/CryTestBase.h, cryfs/impl/filesystem/CryDir.h, cryfs/impl/filesystem/CryFile.h, cryfs/impl/filesystem/CryOpenFile.h, fspp/fs_interface/FuseErrnoException.h, boost/algorithm/string/predicate.hpp. Classes/fixtures: CryNodeTest_RenameNested. Helper functions: SourceDirs, DestDirs, CreateDirs, create_path_if_not_exists, expect_rename_succeeds, expect_rename_fails. Direct tests: CryNodeTest_RenameNested.Rename.

Control flow: Fixture setup creates or loads a CryFS config/device, test code performs filesystem operations, and assertions verify node state, file contents, config bytes, or thrown errno exceptions.

State and persistence behavior: It creates source/destination directory trees through `CryTestBase`; state is temp CryFS node hierarchy and parent-child metadata.

Dependencies and integration points: It integrates CryFS filesystem objects with config loading, key providers, fake home/local-state helpers, cpp-utils temp files, and fspp interface expectations.

Risks: Nested rename is prone to cycles, partial moves, and path normalization mistakes.

Test signals: Primary signals are CryNodeTest_RenameNested.Rename. Assertion/mocking density: ASSERT_EQ x1, ASSERT_TRUE x2, ASSERT_FALSE x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryNodeTest_RenameNested.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/FileSystemTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/FileSystemTest.cpp

Purpose: This file adapts the generic fspp filesystem test suite to CryFS by providing a `CryFsTestFixture` implementation backed by a real `CryDevice`.

Important APIs/types/functions: Includes: fspp/fstest/FsTest.h, cpp-utils/tempfile/TempFile.h, cpp-utils/io/NoninteractiveConsole.h, cryfs/impl/filesystem/CryDevice.h, cryfs/impl/config/CryConfigLoader.h, cryfs/impl/config/CryPresetPasswordBasedKeyProvider.h, ../testutils/MockConsole.h, ../testutils/TestWithFakeHomeDirectory.h. Classes/fixtures: CryFsTestFixture. Helper functions: failOnIntegrityViolation, CryFsTestFixture, createDevice. Direct tests: none.

Control flow: Fixture setup creates or loads a CryFS config/device, test code performs filesystem operations, and assertions verify node state, file contents, config bytes, or thrown errno exceptions.

State and persistence behavior: It creates temp basedir/config state, fake home local-state, and a CryFS device used by inherited generic filesystem tests.

Dependencies and integration points: It integrates CryFS filesystem objects with config loading, key providers, fake home/local-state helpers, cpp-utils temp files, and fspp interface expectations.

Risks: Fixture wiring must match the generic fspp expectations; otherwise broad filesystem conformance coverage may give misleading failures.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: EXPECT_TRUE x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/FileSystemTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/testutils/CryTestBase.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/testutils/CryTestBase.cpp

Purpose: This source includes `CryTestBase.h` to compile the filesystem test fixture into the `cryfs-test` target. The fixture implementation is inline in the header, so this file mainly anchors the header in the build.

Important APIs/types/functions: The only visible dependency is `CryTestBase.h`.

Control flow: Build control flow compiles the header-defined fixture through this translation unit.

State and persistence behavior: No additional runtime state is introduced here.

Dependencies and integration points: It connects the CryFS filesystem fixture to the CMake test executable.

Risks: Behavioral regressions are caught through tests that inherit `CryTestBase`, not directly through this source.

Test signals: Successful compilation plus downstream fixture use are the signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/testutils/CryTestBase.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/testutils/CryTestBase.h -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/testutils/CryTestBase.h

Purpose: `CryTestBase` is the reusable fixture for CryFS filesystem tests. It creates a temporary basedir, temporary config file, fake home directory, mock console, key provider, config file, and root `CryDir` so tests can manipulate files, directories, and symlinks through CryFS objects.

Important APIs/types/functions: It uses `CryDevice`, `CryDir`, `CryNode`, `CryOpenFile`, `CryPresetPasswordBasedKeyProvider`, `SCrypt::TestSettings`, `TempFile`, and `TestWithFakeHomeDirectory`. Helper methods include `CreateFile`, `CreateDir`, `CreateSymlink`, `Exists`, `configFile`, and `failOnIntegrityViolation`.

Control flow: The constructor builds/load-or-creates a config, opens a CryFS device, obtains the root directory, and exposes helper wrappers that forward to the CryFS filesystem API. Tests inherit the fixture and directly create or inspect nodes under `_root`.

State and persistence behavior: Persistent test state lives in temp basedir/config paths and local-state home metadata. Runtime state includes the open device, root directory, derived key, and mock console expectations.

Dependencies and integration points: It binds configuration loading, key derivation, local state, and filesystem object APIs into one fixture used by rename, filesystem, and fs-interface integration tests.

Risks: Shared fixture setup means failures in config/key loading can cascade across many filesystem tests. Because it opens real CryFS objects, cleanup and temp directory isolation are important.

Test signals: Downstream tests observe node creation, existence checks, parent pointer updates, config file stability, and absence of integrity violations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/testutils/CryTestBase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/localstate/BasedirMetadataTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/localstate/BasedirMetadataTest.cpp

Purpose: This file tests basedir-to-filesystem-ID metadata validation in the CryFS local-state directory.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/localstate/BasedirMetadata.h, cryfs/impl/localstate/LocalStateDir.h, cryfs/impl/config/CryConfig.h, cpp-utils/tempfile/TempDir.h, ../testutils/TestWithFakeHomeDirectory.h. Classes/fixtures: BasedirMetadataTest. Helper functions: none visible. Direct tests: BasedirMetadataTest.givenEmptyState_whenCalled_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledForDifferentBasedir_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledWithSameId_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledWithDifferentId_thenFails; BasedirMetadataTest.givenStateWithUpdatedBasedir_whenCalledWithSameId_thenSucceeds; BasedirMetadataTest.givenStateWithUpdatedBasedir_whenCalledWithDifferentId_thenFails.

Control flow: The fixture creates a temporary local-state directory, performs metadata reads/writes through production local-state APIs, and asserts success or failure for specific basedir/filesystem-ID combinations.

State and persistence behavior: It writes local-state metadata under a temp fake home and compares behavior for empty state, same basedir/same ID, same basedir/different ID, and updated basedir metadata.

Dependencies and integration points: It integrates `LocalStateDir`, metadata wrappers, `CryConfig` filesystem IDs, temp directories, and fake home-directory behavior.

Risks: Incorrect basedir metadata can allow accidentally mounting a basedir with the wrong filesystem identity or can reject valid moves.

Test signals: Primary signals are BasedirMetadataTest.givenEmptyState_whenCalled_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledForDifferentBasedir_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledWithSameId_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledWithDifferentId_thenFails; BasedirMetadataTest.givenStateWithUpdatedBasedir_whenCalledWithSameId_thenSucceeds; BasedirMetadataTest.givenStateWithUpdatedBasedir_whenCalledWithDifferentId_thenFails. Assertion/mocking density: EXPECT_TRUE x4, EXPECT_FALSE x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/localstate/BasedirMetadataTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/localstate/LocalStateMetadataTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/localstate/LocalStateMetadataTest.cpp

Purpose: This file tests `LocalStateMetadata` persistence, loading, updating, and lookup behavior for CryFS local state.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/localstate/LocalStateMetadata.h, cpp-utils/tempfile/TempDir.h, fstream, cpp-utils/data/DataFixture.h. Classes/fixtures: LocalStateMetadataTest. Helper functions: none visible. Direct tests: LocalStateMetadataTest.myClientId_ValueIsConsistent; LocalStateMetadataTest.myClientId_ValueIsRandomForNewClient; LocalStateMetadataTest.myClientId_TakesLegacyValueIfSpecified; LocalStateMetadataTest.encryptionKeyHash_whenLoadingWithSameKey_thenDoesntCrash; LocalStateMetadataTest.encryptionKeyHash_whenLoadingWithDifferentKey_thenCrashes.

Control flow: The fixture creates a temporary local-state directory, performs metadata reads/writes through production local-state APIs, and asserts success or failure for specific basedir/filesystem-ID combinations.

State and persistence behavior: It uses temp directories and fake home state to persist local-state files, then reloads or updates metadata values.

Dependencies and integration points: It integrates `LocalStateDir`, metadata wrappers, `CryConfig` filesystem IDs, temp directories, and fake home-directory behavior.

Risks: Local-state corruption or path identity drift affects filesystem safety checks and user-specific metadata.

Test signals: Primary signals are LocalStateMetadataTest.myClientId_ValueIsConsistent; LocalStateMetadataTest.myClientId_ValueIsRandomForNewClient; LocalStateMetadataTest.myClientId_TakesLegacyValueIfSpecified; LocalStateMetadataTest.encryptionKeyHash_whenLoadingWithSameKey_thenDoesntCrash; LocalStateMetadataTest.encryptionKeyHash_whenLoadingWithDifferentKey_thenCrashes. Assertion/mocking density: EXPECT_EQ x2, EXPECT_THROW x1, EXPECT_NE x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/localstate/LocalStateMetadataTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/FakeCryKeyProvider.h -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/FakeCryKeyProvider.h

Purpose: This header defines a fake `CryKeyProvider` for config-file tests. It supplies deterministic key material without prompting a console or running a real password flow.

Important APIs/types/functions: It depends on the CryFS key-provider interface and cpp-utils data/key types. The fixture exposes a simple provider object whose request methods return preconfigured keys.

Control flow: Tests instantiate the fake provider, pass it into `CryConfigFile` or encryptor helpers, and then load/create encrypted configs using stable key bytes.

State and persistence behavior: The provider stores only in-memory key data. Persistence happens in the config files under test, not in the helper itself.

Dependencies and integration points: It integrates config-file encryption/decryption tests with the production key-provider abstraction while avoiding console/KDF costs.

Risks: Because it bypasses password prompts and KDF behavior, it should only be used where deterministic key material is the point of the test.

Test signals: Callers observe successful config encryption/decryption with the expected key and failure when a different key provider is used.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/FakeCryKeyProvider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/MockConsole.h -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/MockConsole.h

Purpose: This header provides `MockConsole` and the `TestWithMockConsole` fixture mixin for tests that verify interactive CryFS prompts and console output.

Important APIs/types/functions: It uses Google Mock to mock console methods such as line input, password input, yes/no prompts, and output streams. The helper returns shared mock console instances for config and CLI tests.

Control flow: A test installs expectations on the mock console, invokes the target component, and then Google Mock verifies prompt order, prompt text, returned answers, and warnings.

State and persistence behavior: Console state is in-memory mock expectation state. It does not persist files, but it often controls whether production code creates or mutates config/local-state files.

Dependencies and integration points: This mock is central to `CryConfigConsole`, `CryConfigCreator`, `CryConfigLoader`, password key-provider, and filesystem tests that need deterministic interactive behavior.

Risks: Tests can become brittle if they assert exact prompt wording. Missing expectations can also hide unexpected console calls depending on mock strictness.

Test signals: Expected prompt calls, output calls, and absence/presence of warning messages are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/MockConsole.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/MockCryKeyProvider.h -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/MockCryKeyProvider.h

Purpose: This header defines a Google Mock implementation of the CryFS key-provider interface. It lets tests assert exactly when new or existing filesystem keys are requested and which key data is returned.

Important APIs/types/functions: It mocks `CryKeyProvider` methods for new and existing filesystems and uses cpp-utils data/key types in return values.

Control flow: Tests configure `EXPECT_CALL` on the mock provider, execute config loading or encryption code, and verify the key request path taken by the production component.

State and persistence behavior: The mock stores expectation state only. Any persistent effects come from config files that receive the mocked key material.

Dependencies and integration points: It integrates key-provider contract tests with `CryConfigFile`, config loaders, and encryptor factories.

Risks: It verifies interaction shape rather than cryptographic strength; tests that need real KDF coverage should use password-based providers instead.

Test signals: Google Mock call counts, selected provider method, and returned key bytes drive pass/fail behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/MockCryKeyProvider.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/TestWithFakeHomeDirectory.h -->
# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/TestWithFakeHomeDirectory.h

Purpose: This fixture mixin redirects CryFS tests to a fake home directory. It isolates local-state metadata and user-specific config from the developer or CI machine.

Important APIs/types/functions: It uses cpp-utils temp directories and home-directory override helpers to install and restore a test home path.

Control flow: A fixture inherits this mixin, setup installs the fake home directory before production code resolves user paths, and teardown restores the original home behavior.

State and persistence behavior: It creates temporary filesystem state that stands in for the user's home directory. CryFS local-state files written during tests are confined there.

Dependencies and integration points: The mixin is used by config loader/creator, local-state, CLI, and filesystem tests that touch `LocalStateDir` or home-derived paths.

Risks: Failure to restore the home override could contaminate later tests; order of fixture construction matters for code that resolves paths in constructors.

Test signals: Tests can assert local-state files under the fake home path and avoid interacting with real user state.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/testutils/TestWithFakeHomeDirectory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/CMakeLists.txt

Purpose: This CMake file defines the `fspp-test` test executable for the CryFS legacy C++ tree. It enumerates the test sources in this subtree, links the executable to the production libraries and Google Test support, registers it with CTest, and applies the repository's C++14 and style-warning helpers.

Important APIs/types/functions: The important build APIs are `project`, `set(SOURCES)`, `add_executable`, `target_link_libraries`, `add_test`, `target_enable_style_warnings`, and `target_activate_cpp14`. The source list is the integration surface: changing it determines which config, filesystem, local-state, fspp interface, and FUSE adapter tests actually run.

Control flow: Configure-time evaluation collects the listed sources into one executable target, then target creation and link steps bind it to the relevant production library. Test execution is delegated to CTest through the `add_test` registration.

State and persistence behavior: The file persists no runtime state. Its state effect is build-system state: generated target metadata, dependency edges, compiler mode, warning policy, and CTest registration in the build directory.

Dependencies and integration points: It integrates this test subtree with `my-gtest-main`, `googletest`, and the matching production libraries. It is the bridge between individual source files and CI/test runners.

Risks: Missing a source in `SOURCES` silently removes coverage from the executable. A stale link library or C++ standard setting can mask source-level correctness by preventing the tests from building.

Test signals: A successful configure/build produces the `fspp-test` executable, and a successful CTest invocation proves all listed source files compiled and linked into the expected test target.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/DeviceTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/DeviceTest.cpp

Purpose: This file tests fspp device/filesystem interface behavior at the root abstraction level.

Important APIs/types/functions: Includes: fspp/fs_interface/Device.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none.

Control flow: Google Test fixtures instantiate interface implementations or mocks, call the interface methods under test, and assert returned values, propagated exceptions, or metadata fields.

State and persistence behavior: These tests are primarily in-memory interface/fixture checks. Any filesystem-like state is represented by mocks or lightweight test objects rather than durable files.

Dependencies and integration points: These interface tests sit below the FUSE adapter tests and above concrete filesystem implementations such as CryFS, keeping the fspp abstraction contract explicit.

Risks: Interface drift can break both FUSE adapters and real filesystem backends even if individual implementations still compile.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: none visible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/DeviceTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/DirTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/DirTest.cpp

Purpose: This file tests fspp directory interface behavior, including child listing and directory-specific operations.

Important APIs/types/functions: Includes: fspp/fs_interface/Dir.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none.

Control flow: Google Test fixtures instantiate interface implementations or mocks, call the interface methods under test, and assert returned values, propagated exceptions, or metadata fields.

State and persistence behavior: These tests are primarily in-memory interface/fixture checks. Any filesystem-like state is represented by mocks or lightweight test objects rather than durable files.

Dependencies and integration points: These interface tests sit below the FUSE adapter tests and above concrete filesystem implementations such as CryFS, keeping the fspp abstraction contract explicit.

Risks: Interface drift can break both FUSE adapters and real filesystem backends even if individual implementations still compile.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: none visible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/DirTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/FileTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/FileTest.cpp

Purpose: This file tests fspp file interface behavior and file-open/read/write/truncate integration points.

Important APIs/types/functions: Includes: fspp/fs_interface/File.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none.

Control flow: Google Test fixtures instantiate interface implementations or mocks, call the interface methods under test, and assert returned values, propagated exceptions, or metadata fields.

State and persistence behavior: These tests are primarily in-memory interface/fixture checks. Any filesystem-like state is represented by mocks or lightweight test objects rather than durable files.

Dependencies and integration points: These interface tests sit below the FUSE adapter tests and above concrete filesystem implementations such as CryFS, keeping the fspp abstraction contract explicit.

Risks: Interface drift can break both FUSE adapters and real filesystem backends even if individual implementations still compile.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: none visible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/FileTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/NodeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/NodeTest.cpp

Purpose: This file tests common fspp node interface behavior such as stat metadata, names, and type-specific expectations shared by files, directories, and devices.

Important APIs/types/functions: Includes: fspp/fs_interface/Node.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none.

Control flow: Google Test fixtures instantiate interface implementations or mocks, call the interface methods under test, and assert returned values, propagated exceptions, or metadata fields.

State and persistence behavior: These tests are primarily in-memory interface/fixture checks. Any filesystem-like state is represented by mocks or lightweight test objects rather than durable files.

Dependencies and integration points: These interface tests sit below the FUSE adapter tests and above concrete filesystem implementations such as CryFS, keeping the fspp abstraction contract explicit.

Risks: Interface drift can break both FUSE adapters and real filesystem backends even if individual implementations still compile.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: none visible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/NodeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/OpenFileTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/OpenFileTest.cpp

Purpose: This file tests fspp `OpenFile` behavior for read/write/truncate/flush/sync style operations exposed through an opened file object.

Important APIs/types/functions: Includes: fspp/fs_interface/OpenFile.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none.

Control flow: Google Test fixtures instantiate interface implementations or mocks, call the interface methods under test, and assert returned values, propagated exceptions, or metadata fields.

State and persistence behavior: These tests are primarily in-memory interface/fixture checks. Any filesystem-like state is represented by mocks or lightweight test objects rather than durable files.

Dependencies and integration points: These interface tests sit below the FUSE adapter tests and above concrete filesystem implementations such as CryFS, keeping the fspp abstraction contract explicit.

Risks: Interface drift can break both FUSE adapters and real filesystem backends even if individual implementations still compile.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: none visible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fs_interface/OpenFileTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/BasicFuseTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/BasicFuseTest.cpp

Purpose: This file verifies basic FUSE mount/test-harness behavior for the fspp adapter, ensuring a temporary FUSE filesystem can be mounted and interacted with through the shared `FuseTest` infrastructure.

Important APIs/types/functions: Includes: ../testutils/FuseTest.h. Classes/fixtures: none visible. Direct tests: BasicFuseTest.setupAndTearDown.

Control flow: The test creates a temporary mounted filesystem backed by `MockFilesystem`, performs simple operations through the mount point, and relies on the FUSE thread fixture for startup/shutdown.

State and persistence behavior: State includes a temporary mount directory, FUSE thread lifecycle, and mock filesystem expectations. No durable state should survive teardown.

Dependencies and integration points: It validates the common harness used by every fspp FUSE operation test.

Risks: FUSE availability, mount timing, and teardown behavior are environmental risks that can affect the whole suite.

Test signals: Primary signals are BasicFuseTest.setupAndTearDown. Assertion/mocking density: none visible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/BasicFuseTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/FilesystemTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/FilesystemTest.cpp

Purpose: This file tests fspp FUSE `Filesystem` adapter wiring at a broader level than single-operation tests. It verifies context propagation and operation forwarding between mounted POSIX calls and the mocked filesystem implementation.

Important APIs/types/functions: Includes: fspp/fuse/Filesystem.h. Classes/fixtures: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: Tests mount a `MockFilesystem`, perform filesystem calls through the mount directory, and assert the adapter invokes the expected mock methods with correct context and parameters.

State and persistence behavior: Runtime state is the temporary mount, FUSE thread, context captured from the request, and mock expectation state. No persistent files should remain outside temp dirs.

Dependencies and integration points: This is the integration layer between POSIX/FUSE calls and the fspp `Filesystem` interface.

Risks: Context forwarding and method dispatch bugs can make operation-specific tests pass in isolation while real mounted behavior is wrong.

Test signals: Primary signals are fixture/helper behavior rather than direct TEST macros. Assertion/mocking density: none visible.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/FilesystemTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/TimestampTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/TimestampTest.cpp

Purpose: This file tests timestamp conversion/rounding behavior in the fspp FUSE layer.

Important APIs/types/functions: Includes: ../testutils/FuseTest.h, gmock/gmock.h. Classes/fixtures: none visible. Direct tests: FuseTimestampTest.whenCalledWithoutAnyAtimeFlag_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithNoatimeFlag_thenHasNoatimeBehavior; FuseTimestampTest.whenCalledWithStrictatimeFlag_thenHasStrictatimeBehavior; FuseTimestampTest.whenCalledWithRelatimeFlag_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithAtimeFlag_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithNodiratimeFlag_thenHasNoatimeBehavior; FuseTimestampTest.whenCalledWithAtimeAtimeFlag_withCsv_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithAtimeAtimeFlag_withSeparateFlags_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithAtimeNoatimeFlag_withCsv_thenFails; FuseTimestampTest.whenCalledWithAtimeNoatimeFlag_withSeparateFlags_thenFails; FuseTimestampTest.whenCalledWithAtimeRelatimeFlag_withCsv_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithAtimeRelatimeFlag_withSeparateFlags_thenHasRelatimeBehavior.

Control flow: Tests pass timestamp values through FUSE/stat-related code paths and assert seconds/nanoseconds fields are preserved or converted as expected.

State and persistence behavior: State is in-memory timestamp structs and stat buffers; no disk persistence is required.

Dependencies and integration points: Timestamp behavior feeds `lstat`, `fstat`, and `utimens` adapter tests.

Risks: Timestamp truncation or field mixups create subtle metadata regressions visible to applications.

Test signals: Primary signals are FuseTimestampTest.whenCalledWithoutAnyAtimeFlag_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithNoatimeFlag_thenHasNoatimeBehavior; FuseTimestampTest.whenCalledWithStrictatimeFlag_thenHasStrictatimeBehavior; FuseTimestampTest.whenCalledWithRelatimeFlag_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithAtimeFlag_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithNodiratimeFlag_thenHasNoatimeBehavior; FuseTimestampTest.whenCalledWithAtimeAtimeFlag_withCsv_thenHasRelatimeBehavior; FuseTimestampTest.whenCalledWithAtimeAtimeFlag_withSeparateFlags_thenHasRelatimeBehavior. Assertion/mocking density: EXPECT_EQ x36.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/TimestampTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/FuseAccessErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/FuseAccessErrorTest.cpp

Purpose: This file tests fspp FUSE access checks, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseAccessTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseAccessErrorTest. Helper functions: none visible. Direct tests: FuseAccessErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for access checks to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseAccessErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/FuseAccessErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/FuseAccessFilenameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/FuseAccessFilenameTest.cpp

Purpose: This file tests fspp FUSE access checks, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseAccessTest.h. Classes/fixtures: FuseAccessFilenameTest. Helper functions: none visible. Direct tests: FuseAccessFilenameTest.AccessFile; FuseAccessFilenameTest.AccessFileNested; FuseAccessFilenameTest.AccessFileNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for access checks to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseAccessFilenameTest.AccessFile; FuseAccessFilenameTest.AccessFileNested; FuseAccessFilenameTest.AccessFileNested2. Assertion/mocking density: EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/FuseAccessFilenameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/FuseAccessModeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/FuseAccessModeTest.cpp

Purpose: This file tests fspp FUSE access checks, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseAccessTest.h. Classes/fixtures: FuseAccessModeTest. Helper functions: none visible. Direct tests: FuseAccessModeTest.AccessFile.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for access checks to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseAccessModeTest.AccessFile. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/FuseAccessModeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/testutils/FuseAccessTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/testutils/FuseAccessTest.cpp

Purpose: This file provides the shared FUSE access checks test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseAccessTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for access checks.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/testutils/FuseAccessTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/testutils/FuseAccessTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/testutils/FuseAccessTest.h

Purpose: This file provides the shared FUSE access checks test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h. Classes/fixtures: FuseAccessTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for access checks.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/access/testutils/FuseAccessTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/closeFile/FuseCloseTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/closeFile/FuseCloseTest.cpp

Purpose: This file tests fspp FUSE close-file handling, focusing on close-file forwarding from POSIX close to the fspp close method.

Important APIs/types/functions: Includes: ../../testutils/FuseTest.h, ../../testutils/OpenFileHandle.h, condition_variable. Classes/fixtures: Barrier, FuseCloseTest. Helper functions: Barrier, WaitAtMost, Release, OpenAndCloseFile, OpenFile, CloseFile. Direct tests: FuseCloseTest.CloseFile.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for close-file handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseCloseTest.CloseFile. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/closeFile/FuseCloseTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenErrorTest.cpp

Purpose: This file tests fspp FUSE create-and-open handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseCreateAndOpenTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseCreateAndOpenErrorTest. Helper functions: none visible. Direct tests: FuseCreateAndOpenErrorTest.ReturnNoError; FuseCreateAndOpenErrorTest.ReturnError.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for create-and-open handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseCreateAndOpenErrorTest.ReturnNoError; FuseCreateAndOpenErrorTest.ReturnError. Assertion/mocking density: EXPECT_EQ x2, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenFileDescriptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenFileDescriptorTest.cpp

Purpose: This file tests fspp FUSE create-and-open handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseCreateAndOpenTest.h. Classes/fixtures: FuseCreateAndOpenFileDescriptorTest. Helper functions: CreateAndOpenAndReadFile, CreateAndOpenFile, ReadFile. Direct tests: FuseCreateAndOpenFileDescriptorTest.TestReturnedFileDescriptor.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for create-and-open handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseCreateAndOpenFileDescriptorTest.TestReturnedFileDescriptor. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenFileDescriptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenFilenameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenFilenameTest.cpp

Purpose: This file tests fspp FUSE create-and-open handling, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseCreateAndOpenTest.h. Classes/fixtures: FuseCreateAndOpenFilenameTest. Helper functions: none visible. Direct tests: FuseCreateAndOpenFilenameTest.CreateAndOpenFile; FuseCreateAndOpenFilenameTest.CreateAndOpenFileNested; FuseCreateAndOpenFilenameTest.CreateAndOpenFileNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for create-and-open handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseCreateAndOpenFilenameTest.CreateAndOpenFile; FuseCreateAndOpenFilenameTest.CreateAndOpenFileNested; FuseCreateAndOpenFilenameTest.CreateAndOpenFileNested2. Assertion/mocking density: EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenFilenameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenFlagsTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenFlagsTest.cpp

Purpose: This file tests fspp FUSE create-and-open handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseCreateAndOpenTest.h. Classes/fixtures: FuseCreateAndOpenFlagsTest. Helper functions: none visible. Direct tests: FuseCreateAndOpenFlagsTest.testFlags.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for create-and-open handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseCreateAndOpenFlagsTest.testFlags. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/FuseCreateAndOpenFlagsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/testutils/FuseCreateAndOpenTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/testutils/FuseCreateAndOpenTest.cpp

Purpose: This file provides the shared FUSE create-and-open handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseCreateAndOpenTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for create-and-open handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/testutils/FuseCreateAndOpenTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/testutils/FuseCreateAndOpenTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/testutils/FuseCreateAndOpenTest.h

Purpose: This file provides the shared FUSE create-and-open handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseCreateAndOpenTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for create-and-open handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/createAndOpenFile/testutils/FuseCreateAndOpenTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/FuseFdatasyncErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/FuseFdatasyncErrorTest.cpp

Purpose: This file tests fspp FUSE fdatasync handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseFdatasyncTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFdatasyncErrorTest. Helper functions: none visible. Direct tests: FuseFdatasyncErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for fdatasync handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFdatasyncErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/FuseFdatasyncErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/FuseFdatasyncFileDescriptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/FuseFdatasyncFileDescriptorTest.cpp

Purpose: This file tests fspp FUSE fdatasync handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseFdatasyncTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFdatasyncFileDescriptorTest. Helper functions: none visible. Direct tests: FuseFdatasyncFileDescriptorTest.FileDescriptorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for fdatasync handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFdatasyncFileDescriptorTest.FileDescriptorIsCorrect. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/FuseFdatasyncFileDescriptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/testutils/FuseFdatasyncTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/testutils/FuseFdatasyncTest.cpp

Purpose: This file provides the shared FUSE fdatasync handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseFdatasyncTest.h, fcntl.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for fdatasync handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/testutils/FuseFdatasyncTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/testutils/FuseFdatasyncTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/testutils/FuseFdatasyncTest.h

Purpose: This file provides the shared FUSE fdatasync handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseFdatasyncTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for fdatasync handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fdatasync/testutils/FuseFdatasyncTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/FuseFlushErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/FuseFlushErrorTest.cpp

Purpose: This file tests fspp FUSE flush handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseFlushTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFlushErrorTest. Helper functions: none visible. Direct tests: FuseFlushErrorTest.ReturnErrorFromFlush.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for flush handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFlushErrorTest.ReturnErrorFromFlush. Assertion/mocking density: EXPECT_EQ x2, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/FuseFlushErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/FuseFlushFileDescriptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/FuseFlushFileDescriptorTest.cpp

Purpose: This file tests fspp FUSE flush handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseFlushTest.h. Classes/fixtures: FuseFlushFileDescriptorTest. Helper functions: none visible. Direct tests: FuseFlushFileDescriptorTest.FlushOnCloseFile.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for flush handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFlushFileDescriptorTest.FlushOnCloseFile. Assertion/mocking density: EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/FuseFlushFileDescriptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/testutils/FuseFlushTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/testutils/FuseFlushTest.cpp

Purpose: This file provides the shared FUSE flush handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseFlushTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for flush handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/testutils/FuseFlushTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/testutils/FuseFlushTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/testutils/FuseFlushTest.h

Purpose: This file provides the shared FUSE flush handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseFlushTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for flush handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/flush/testutils/FuseFlushTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/FuseFstatErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/FuseFstatErrorTest.cpp

Purpose: This file tests fspp FUSE file-descriptor stat handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseFstatTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFstatErrorTest. Helper functions: none visible. Direct tests: FuseFstatErrorTest.ReturnedErrorCodeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for file-descriptor stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFstatErrorTest.ReturnedErrorCodeIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/FuseFstatErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/FuseFstatParameterTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/FuseFstatParameterTest.cpp

Purpose: This file tests fspp FUSE file-descriptor stat handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseFstatTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFstatParameterTest. Helper functions: CallFstat. Direct tests: FuseFstatParameterTest.FileDescriptorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for file-descriptor stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFstatParameterTest.FileDescriptorIsCorrect. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/FuseFstatParameterTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/testutils/FuseFstatTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/testutils/FuseFstatTest.cpp

Purpose: This file provides the shared FUSE file-descriptor stat handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseFstatTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for file-descriptor stat handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/testutils/FuseFstatTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/testutils/FuseFstatTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/testutils/FuseFstatTest.h

Purpose: This file provides the shared FUSE file-descriptor stat handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseFstatTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for file-descriptor stat handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fstat/testutils/FuseFstatTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/FuseFsyncErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/FuseFsyncErrorTest.cpp

Purpose: This file tests fspp FUSE fsync handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseFsyncTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFsyncErrorTest. Helper functions: none visible. Direct tests: FuseFsyncErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for fsync handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFsyncErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/FuseFsyncErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/FuseFsyncFileDescriptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/FuseFsyncFileDescriptorTest.cpp

Purpose: This file tests fspp FUSE fsync handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseFsyncTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFsyncFileDescriptorTest. Helper functions: none visible. Direct tests: FuseFsyncFileDescriptorTest.FileDescriptorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for fsync handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFsyncFileDescriptorTest.FileDescriptorIsCorrect. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/FuseFsyncFileDescriptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/testutils/FuseFsyncTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/testutils/FuseFsyncTest.cpp

Purpose: This file provides the shared FUSE fsync handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseFsyncTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for fsync handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/testutils/FuseFsyncTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/testutils/FuseFsyncTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/testutils/FuseFsyncTest.h

Purpose: This file provides the shared FUSE fsync handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseFsyncTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for fsync handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/fsync/testutils/FuseFsyncTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/FuseFTruncateErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/FuseFTruncateErrorTest.cpp

Purpose: This file tests fspp FUSE file-descriptor truncate handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseFTruncateTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFTruncateErrorTest. Helper functions: none visible. Direct tests: FuseFTruncateErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for file-descriptor truncate handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFTruncateErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/FuseFTruncateErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/FuseFTruncateFileDescriptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/FuseFTruncateFileDescriptorTest.cpp

Purpose: This file tests fspp FUSE file-descriptor truncate handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseFTruncateTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseFTruncateFileDescriptorTest. Helper functions: none visible. Direct tests: FuseFTruncateFileDescriptorTest.FileDescriptorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for file-descriptor truncate handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFTruncateFileDescriptorTest.FileDescriptorIsCorrect. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/FuseFTruncateFileDescriptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/FuseFTruncateSizeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/FuseFTruncateSizeTest.cpp

Purpose: This file tests fspp FUSE file-descriptor truncate handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseFTruncateTest.h. Classes/fixtures: FuseFTruncateSizeTest. Helper functions: none visible. Direct tests: FuseFTruncateSizeTest.FTruncateFile.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for file-descriptor truncate handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseFTruncateSizeTest.FTruncateFile. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/FuseFTruncateSizeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/testutils/FuseFTruncateTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/testutils/FuseFTruncateTest.cpp

Purpose: This file provides the shared FUSE file-descriptor truncate handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseFTruncateTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for file-descriptor truncate handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/testutils/FuseFTruncateTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/testutils/FuseFTruncateTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/testutils/FuseFTruncateTest.h

Purpose: This file provides the shared FUSE file-descriptor truncate handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseFTruncateTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for file-descriptor truncate handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/ftruncate/testutils/FuseFTruncateTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatErrorTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseLstatTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseLstatErrorTest. Helper functions: none visible. Direct tests: FuseLstatErrorTest.ReturnNoError; FuseLstatErrorTest.ReturnError.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatErrorTest.ReturnNoError; FuseLstatErrorTest.ReturnError. Assertion/mocking density: EXPECT_EQ x2, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatPathParameterTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatPathParameterTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseLstatTest.h. Classes/fixtures: FuseLstatPathParameterTest. Helper functions: none visible. Direct tests: FuseLstatPathParameterTest.PathParameterIsCorrectRoot; FuseLstatPathParameterTest.PathParameterIsCorrectSimpleFile; FuseLstatPathParameterTest.PathParameterIsCorrectSimpleDir; FuseLstatPathParameterTest.PathParameterIsCorrectNestedFile; FuseLstatPathParameterTest.PathParameterIsCorrectNestedDir.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatPathParameterTest.PathParameterIsCorrectRoot; FuseLstatPathParameterTest.PathParameterIsCorrectSimpleFile; FuseLstatPathParameterTest.PathParameterIsCorrectSimpleDir; FuseLstatPathParameterTest.PathParameterIsCorrectNestedFile; FuseLstatPathParameterTest.PathParameterIsCorrectNestedDir. Assertion/mocking density: EXPECT_CALL x5.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatPathParameterTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnAtimeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnAtimeTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseLstatReturnTest.h, cpp-utils/system/stat.h. Classes/fixtures: FuseLstatReturnATimeTest. Helper functions: set. Direct tests: FuseLstatReturnATimeTest.ReturnedFileAtimeIsCorrect; FuseLstatReturnATimeTest.ReturnedDirAtimeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatReturnATimeTest.ReturnedFileAtimeIsCorrect; FuseLstatReturnATimeTest.ReturnedDirAtimeIsCorrect. Assertion/mocking density: EXPECT_EQ x4.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnAtimeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnCtimeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnCtimeTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseLstatReturnTest.h, cpp-utils/system/stat.h. Classes/fixtures: FuseLstatReturnCtimeTest. Helper functions: set. Direct tests: FuseLstatReturnCtimeTest.ReturnedFileCtimeIsCorrect; FuseLstatReturnCtimeTest.ReturnedDirCtimeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatReturnCtimeTest.ReturnedFileCtimeIsCorrect; FuseLstatReturnCtimeTest.ReturnedDirCtimeIsCorrect. Assertion/mocking density: EXPECT_EQ x4.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnCtimeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnGidTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnGidTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseLstatReturnTest.h. Classes/fixtures: FuseLstatReturnGidTest. Helper functions: set. Direct tests: FuseLstatReturnGidTest.ReturnedFileGidIsCorrect; FuseLstatReturnGidTest.ReturnedDirGidIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatReturnGidTest.ReturnedFileGidIsCorrect; FuseLstatReturnGidTest.ReturnedDirGidIsCorrect. Assertion/mocking density: EXPECT_EQ x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnGidTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnModeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnModeTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseLstatReturnTest.h. Classes/fixtures: FuseLstatReturnModeTest. Helper functions: CallLstatWithValue, CallLstatWithImpl. Direct tests: FuseLstatReturnModeTest.ReturnedModeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatReturnModeTest.ReturnedModeIsCorrect. Assertion/mocking density: EXPECT_EQ x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnModeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnMtimeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnMtimeTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseLstatReturnTest.h, cpp-utils/system/stat.h. Classes/fixtures: FuseLstatReturnMtimeTest. Helper functions: set. Direct tests: FuseLstatReturnMtimeTest.ReturnedFileMtimeIsCorrect; FuseLstatReturnMtimeTest.ReturnedDirMtimeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatReturnMtimeTest.ReturnedFileMtimeIsCorrect; FuseLstatReturnMtimeTest.ReturnedDirMtimeIsCorrect. Assertion/mocking density: EXPECT_EQ x4.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnMtimeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnNlinkTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnNlinkTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseLstatReturnTest.h. Classes/fixtures: FuseLstatReturnNlinkTest. Helper functions: set. Direct tests: FuseLstatReturnNlinkTest.ReturnedFileNlinkIsCorrect; FuseLstatReturnNlinkTest.ReturnedDirNlinkIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatReturnNlinkTest.ReturnedFileNlinkIsCorrect; FuseLstatReturnNlinkTest.ReturnedDirNlinkIsCorrect. Assertion/mocking density: EXPECT_EQ x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnNlinkTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnSizeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnSizeTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseLstatReturnTest.h. Classes/fixtures: FuseLstatReturnSizeTest. Helper functions: set. Direct tests: FuseLstatReturnSizeTest.ReturnedFileSizeIsCorrect; FuseLstatReturnSizeTest.ReturnedDirSizeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatReturnSizeTest.ReturnedFileSizeIsCorrect; FuseLstatReturnSizeTest.ReturnedDirSizeIsCorrect. Assertion/mocking density: EXPECT_EQ x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnSizeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnUidTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnUidTest.cpp

Purpose: This file tests fspp FUSE path stat handling, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseLstatReturnTest.h. Classes/fixtures: FuseLstatReturnUidTest. Helper functions: set. Direct tests: FuseLstatReturnUidTest.ReturnedFileUidIsCorrect; FuseLstatReturnUidTest.ReturnedDirUidIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path stat handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseLstatReturnUidTest.ReturnedFileUidIsCorrect; FuseLstatReturnUidTest.ReturnedDirUidIsCorrect. Assertion/mocking density: EXPECT_EQ x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/FuseLstatReturnUidTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/testutils/FuseLstatReturnTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/testutils/FuseLstatReturnTest.h

Purpose: This file provides the shared FUSE path stat handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseLstatTest.h. Classes/fixtures: FuseLstatReturnTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for path stat handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/testutils/FuseLstatReturnTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/testutils/FuseLstatTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/testutils/FuseLstatTest.cpp

Purpose: This file provides the shared FUSE path stat handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseLstatTest.h. Classes/fixtures: none visible. Helper functions: CallLstatWithImpl. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for path stat handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/testutils/FuseLstatTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/testutils/FuseLstatTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/testutils/FuseLstatTest.h

Purpose: This file provides the shared FUSE path stat handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: string, functional, sys/stat.h, ../../../testutils/FuseTest.h. Classes/fixtures: FuseLstatTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for path stat handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/lstat/testutils/FuseLstatTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/FuseMkdirDirnameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/FuseMkdirDirnameTest.cpp

Purpose: This file tests fspp FUSE directory creation, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseMkdirTest.h. Classes/fixtures: FuseMkdirDirnameTest. Helper functions: none visible. Direct tests: FuseMkdirDirnameTest.Mkdir; FuseMkdirDirnameTest.MkdirNested; FuseMkdirDirnameTest.MkdirNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for directory creation to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseMkdirDirnameTest.Mkdir; FuseMkdirDirnameTest.MkdirNested; FuseMkdirDirnameTest.MkdirNested2. Assertion/mocking density: EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/FuseMkdirDirnameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/FuseMkdirErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/FuseMkdirErrorTest.cpp

Purpose: This file tests fspp FUSE directory creation, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseMkdirTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseMkdirErrorTest. Helper functions: none visible. Direct tests: FuseMkdirErrorTest.NoError; FuseMkdirErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for directory creation to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseMkdirErrorTest.NoError; FuseMkdirErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x2, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/FuseMkdirErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/FuseMkdirModeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/FuseMkdirModeTest.cpp

Purpose: This file tests fspp FUSE directory creation, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseMkdirTest.h. Classes/fixtures: FuseMkdirModeTest. Helper functions: none visible. Direct tests: FuseMkdirModeTest.Mkdir.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for directory creation to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseMkdirModeTest.Mkdir. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/FuseMkdirModeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/testutils/FuseMkdirTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/testutils/FuseMkdirTest.cpp

Purpose: This file provides the shared FUSE directory creation test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseMkdirTest.h. Classes/fixtures: none visible. Helper functions: Invoke. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for directory creation.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/testutils/FuseMkdirTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/testutils/FuseMkdirTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/testutils/FuseMkdirTest.h

Purpose: This file provides the shared FUSE directory creation test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h. Classes/fixtures: FuseMkdirTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for directory creation.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/mkdir/testutils/FuseMkdirTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenErrorTest.cpp

Purpose: This file tests fspp FUSE open-file handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseOpenTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseOpenErrorTest. Helper functions: none visible. Direct tests: FuseOpenErrorTest.ReturnNoError; FuseOpenErrorTest.ReturnError.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for open-file handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseOpenErrorTest.ReturnNoError; FuseOpenErrorTest.ReturnError. Assertion/mocking density: EXPECT_EQ x2, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenFileDescriptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenFileDescriptorTest.cpp

Purpose: This file tests fspp FUSE open-file handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseOpenTest.h. Classes/fixtures: FuseOpenFileDescriptorTest. Helper functions: OpenAndReadFile, OpenFile, ReadFile. Direct tests: FuseOpenFileDescriptorTest.TestReturnedFileDescriptor.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for open-file handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseOpenFileDescriptorTest.TestReturnedFileDescriptor. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenFileDescriptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenFilenameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenFilenameTest.cpp

Purpose: This file tests fspp FUSE open-file handling, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseOpenTest.h. Classes/fixtures: FuseOpenFilenameTest. Helper functions: none visible. Direct tests: FuseOpenFilenameTest.OpenFile; FuseOpenFilenameTest.OpenFileNested; FuseOpenFilenameTest.OpenFileNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for open-file handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseOpenFilenameTest.OpenFile; FuseOpenFilenameTest.OpenFileNested; FuseOpenFilenameTest.OpenFileNested2. Assertion/mocking density: EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenFilenameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenFlagsTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenFlagsTest.cpp

Purpose: This file tests fspp FUSE open-file handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseOpenTest.h. Classes/fixtures: FuseOpenFlagsTest. Helper functions: none visible. Direct tests: FuseOpenFlagsTest.testFlags.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for open-file handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseOpenFlagsTest.testFlags. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/FuseOpenFlagsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/testutils/FuseOpenTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/testutils/FuseOpenTest.cpp

Purpose: This file provides the shared FUSE open-file handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseOpenTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for open-file handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/testutils/FuseOpenTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/testutils/FuseOpenTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/testutils/FuseOpenTest.h

Purpose: This file provides the shared FUSE open-file handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseOpenTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for open-file handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/openFile/testutils/FuseOpenTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadErrorTest.cpp

Purpose: This file tests fspp FUSE read handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseReadTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseReadErrorTest. Helper functions: SetUp. Direct tests: FuseReadErrorTest.ReturnErrorOnFirstReadCall; FuseReadErrorTest.ReturnErrorOnSecondReadCall.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for read handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseReadErrorTest.ReturnErrorOnFirstReadCall; FuseReadErrorTest.ReturnErrorOnSecondReadCall. Assertion/mocking density: EXPECT_EQ x3, EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadFileDescriptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadFileDescriptorTest.cpp

Purpose: This file tests fspp FUSE read handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseReadTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseReadFileDescriptorTest. Helper functions: none visible. Direct tests: FuseReadFileDescriptorTest.FileDescriptorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for read handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseReadFileDescriptorTest.FileDescriptorIsCorrect. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadFileDescriptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadOverflowTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadOverflowTest.cpp

Purpose: This file tests fspp FUSE read handling, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseReadTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseReadOverflowTest. Helper functions: SetUp. Direct tests: FuseReadOverflowTest.ReadMoreThanFileSizeFromBeginning; FuseReadOverflowTest.ReadMoreThanFileSizeFromMiddle.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for read handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseReadOverflowTest.ReadMoreThanFileSizeFromBeginning; FuseReadOverflowTest.ReadMoreThanFileSizeFromMiddle. Assertion/mocking density: EXPECT_EQ x2, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadOverflowTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadReturnedDataTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadReturnedDataTest.cpp

Purpose: This file tests fspp FUSE read handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: cpp-utils/data/DataFixture.h, cpp-utils/data/Data.h, ../../testutils/InMemoryFile.h, testutils/FuseReadTest.h, cpp-utils/pointer/unique_ref.h, fspp/fs_interface/FuseErrnoException.h, tuple, cstdlib. Classes/fixtures: FuseReadReturnedDataTest. Helper functions: fileSize. Direct tests: FuseReadReturnedDataTest.ReturnedDataRangeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for read handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseReadReturnedDataTest.ReturnedDataRangeIsCorrect. Assertion/mocking density: EXPECT_TRUE x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/FuseReadReturnedDataTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/testutils/FuseReadTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/testutils/FuseReadTest.cpp

Purpose: This file provides the shared FUSE read handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseReadTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for read handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/testutils/FuseReadTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/testutils/FuseReadTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/testutils/FuseReadTest.h

Purpose: This file provides the shared FUSE read handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseReadTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for read handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/read/testutils/FuseReadTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirDirnameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirDirnameTest.cpp

Purpose: This file tests fspp FUSE directory enumeration, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseReadDirTest.h. Classes/fixtures: FuseReadDirDirnameTest. Helper functions: none visible. Direct tests: FuseReadDirDirnameTest.ReadRootDir; FuseReadDirDirnameTest.ReadDir; FuseReadDirDirnameTest.ReadDirNested; FuseReadDirDirnameTest.ReadDirNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for directory enumeration to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseReadDirDirnameTest.ReadRootDir; FuseReadDirDirnameTest.ReadDir; FuseReadDirDirnameTest.ReadDirNested; FuseReadDirDirnameTest.ReadDirNested2. Assertion/mocking density: EXPECT_CALL x4.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirDirnameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirErrorTest.cpp

Purpose: This file tests fspp FUSE directory enumeration, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseReadDirTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseReadDirErrorTest. Helper functions: none visible. Direct tests: FuseReadDirErrorTest.NoError; FuseReadDirErrorTest.ReturnedErrorCodeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for directory enumeration to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseReadDirErrorTest.NoError; FuseReadDirErrorTest.ReturnedErrorCodeIsCorrect. Assertion/mocking density: EXPECT_EQ x2, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirReturnTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirReturnTest.cpp

Purpose: This file tests fspp FUSE directory enumeration, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseReadDirTest.h, cpp-utils/pointer/unique_ref.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseReadDirReturnTest. Helper functions: LARGE_DIR, testDirEntriesAreCorrect. Direct tests: FuseReadDirReturnTest.ReturnedDirEntriesAreCorrect; FuseReadDirReturnTest.ReturnedDirEntriesAreCorrect_LargeDir1000; FuseReadDirReturnTest.DISABLED_ReturnedDirEntriesAreCorrect_LargeDir1000000.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for directory enumeration to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseReadDirReturnTest.ReturnedDirEntriesAreCorrect; FuseReadDirReturnTest.ReturnedDirEntriesAreCorrect_LargeDir1000; FuseReadDirReturnTest.DISABLED_ReturnedDirEntriesAreCorrect_LargeDir1000000. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/FuseReadDirReturnTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/testutils/FuseReadDirTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/testutils/FuseReadDirTest.cpp

Purpose: This file provides the shared FUSE directory enumeration test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseReadDirTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for directory enumeration.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/testutils/FuseReadDirTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/testutils/FuseReadDirTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/testutils/FuseReadDirTest.h

Purpose: This file provides the shared FUSE directory enumeration test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, dirent.h, fspp/fs_interface/Dir.h. Classes/fixtures: FuseReadDirTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for directory enumeration.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/readDir/testutils/FuseReadDirTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/FuseRenameErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/FuseRenameErrorTest.cpp

Purpose: This file tests fspp FUSE rename handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseRenameTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseRenameErrorTest. Helper functions: none visible. Direct tests: FuseRenameErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for rename handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseRenameErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/FuseRenameErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/FuseRenameFilenameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/FuseRenameFilenameTest.cpp

Purpose: This file tests fspp FUSE rename handling, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseRenameTest.h. Classes/fixtures: FuseRenameFilenameTest. Helper functions: none visible. Direct tests: FuseRenameFilenameTest.RenameFileRootToRoot; FuseRenameFilenameTest.RenameFileRootToNested; FuseRenameFilenameTest.RenameFileNestedToRoot; FuseRenameFilenameTest.RenameFileNestedToNested; FuseRenameFilenameTest.RenameFileNestedToNested2; FuseRenameFilenameTest.RenameFileNestedToNested_DifferentFolder; FuseRenameFilenameTest.RenameDirRootToRoot; FuseRenameFilenameTest.RenameDirRootToNested; FuseRenameFilenameTest.RenameDirNestedToRoot; FuseRenameFilenameTest.RenameDirNestedToNested; FuseRenameFilenameTest.RenameDirNestedToNested2; FuseRenameFilenameTest.RenameDirNestedToNested_DifferentFolder.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for rename handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseRenameFilenameTest.RenameFileRootToRoot; FuseRenameFilenameTest.RenameFileRootToNested; FuseRenameFilenameTest.RenameFileNestedToRoot; FuseRenameFilenameTest.RenameFileNestedToNested; FuseRenameFilenameTest.RenameFileNestedToNested2; FuseRenameFilenameTest.RenameFileNestedToNested_DifferentFolder; FuseRenameFilenameTest.RenameDirRootToRoot; FuseRenameFilenameTest.RenameDirRootToNested. Assertion/mocking density: EXPECT_CALL x12.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/FuseRenameFilenameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/testutils/FuseRenameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/testutils/FuseRenameTest.cpp

Purpose: This file provides the shared FUSE rename handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseRenameTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for rename handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/testutils/FuseRenameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/testutils/FuseRenameTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/testutils/FuseRenameTest.h

Purpose: This file provides the shared FUSE rename handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h. Classes/fixtures: FuseRenameTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for rename handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rename/testutils/FuseRenameTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/FuseRmdirDirnameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/FuseRmdirDirnameTest.cpp

Purpose: This file tests fspp FUSE directory removal, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseRmdirTest.h. Classes/fixtures: FuseRmdirDirnameTest. Helper functions: none visible. Direct tests: FuseRmdirDirnameTest.Rmdir; FuseRmdirDirnameTest.RmdirNested; FuseRmdirDirnameTest.RmdirNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for directory removal to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseRmdirDirnameTest.Rmdir; FuseRmdirDirnameTest.RmdirNested; FuseRmdirDirnameTest.RmdirNested2. Assertion/mocking density: EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/FuseRmdirDirnameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/FuseRmdirErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/FuseRmdirErrorTest.cpp

Purpose: This file tests fspp FUSE directory removal, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseRmdirTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseRmdirErrorTest. Helper functions: none visible. Direct tests: FuseRmdirErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for directory removal to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseRmdirErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/FuseRmdirErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/testutils/FuseRmdirTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/testutils/FuseRmdirTest.cpp

Purpose: This file provides the shared FUSE directory removal test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseRmdirTest.h. Classes/fixtures: none visible. Helper functions: Invoke. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for directory removal.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/testutils/FuseRmdirTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/testutils/FuseRmdirTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/testutils/FuseRmdirTest.h

Purpose: This file provides the shared FUSE directory removal test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h. Classes/fixtures: FuseRmdirTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for directory removal.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/rmdir/testutils/FuseRmdirTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsErrorTest.cpp

Purpose: This file tests fspp FUSE filesystem-stat reporting, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseStatfsTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseStatfsErrorTest. Helper functions: none visible. Direct tests: FuseStatfsErrorTest.ReturnNoError; FuseStatfsErrorTest.ReturnError.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for filesystem-stat reporting to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseStatfsErrorTest.ReturnNoError; FuseStatfsErrorTest.ReturnError. Assertion/mocking density: EXPECT_EQ x2, EXPECT_CALL x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBavailTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBavailTest.cpp

Purpose: This file tests fspp FUSE filesystem-stat reporting, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseStatfsReturnTest.h. Classes/fixtures: FuseStatfsReturnBavailTest. Helper functions: set. Direct tests: FuseStatfsReturnBavailTest.ReturnedBavailIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for filesystem-stat reporting to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseStatfsReturnBavailTest.ReturnedBavailIsCorrect. Assertion/mocking density: EXPECT_EQ x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBavailTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBfreeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBfreeTest.cpp

Purpose: This file tests fspp FUSE filesystem-stat reporting, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseStatfsReturnTest.h. Classes/fixtures: FuseStatfsReturnBfreeTest. Helper functions: set. Direct tests: FuseStatfsReturnBfreeTest.ReturnedBfreeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for filesystem-stat reporting to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseStatfsReturnBfreeTest.ReturnedBfreeIsCorrect. Assertion/mocking density: EXPECT_EQ x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBfreeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBlocksTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBlocksTest.cpp

Purpose: This file tests fspp FUSE filesystem-stat reporting, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseStatfsReturnTest.h. Classes/fixtures: FuseStatfsReturnBlocksTest. Helper functions: set. Direct tests: FuseStatfsReturnBlocksTest.ReturnedBlocksIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for filesystem-stat reporting to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseStatfsReturnBlocksTest.ReturnedBlocksIsCorrect. Assertion/mocking density: EXPECT_EQ x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBlocksTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBsizeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBsizeTest.cpp

Purpose: This file tests fspp FUSE filesystem-stat reporting, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseStatfsReturnTest.h. Classes/fixtures: FuseStatfsReturnBsizeTest. Helper functions: set. Direct tests: FuseStatfsReturnBsizeTest.ReturnedBsizeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for filesystem-stat reporting to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseStatfsReturnBsizeTest.ReturnedBsizeIsCorrect. Assertion/mocking density: EXPECT_EQ x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnBsizeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnFfreeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnFfreeTest.cpp

Purpose: This file tests fspp FUSE filesystem-stat reporting, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseStatfsReturnTest.h. Classes/fixtures: FuseStatfsReturnFfreeTest. Helper functions: set. Direct tests: FuseStatfsReturnFfreeTest.ReturnedFfreeIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for filesystem-stat reporting to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseStatfsReturnFfreeTest.ReturnedFfreeIsCorrect. Assertion/mocking density: EXPECT_EQ x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnFfreeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnFilesTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnFilesTest.cpp

Purpose: This file tests fspp FUSE filesystem-stat reporting, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseStatfsReturnTest.h. Classes/fixtures: FuseStatfsReturnFilesTest. Helper functions: set. Direct tests: FuseStatfsReturnFilesTest.ReturnedFilesIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for filesystem-stat reporting to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseStatfsReturnFilesTest.ReturnedFilesIsCorrect. Assertion/mocking density: EXPECT_EQ x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnFilesTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnNamemaxTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnNamemaxTest.cpp

Purpose: This file tests fspp FUSE filesystem-stat reporting, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: testutils/FuseStatfsReturnTest.h. Classes/fixtures: FuseStatfsReturnNamemaxTest. Helper functions: set. Direct tests: FuseStatfsReturnNamemaxTest.ReturnedNamemaxIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for filesystem-stat reporting to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseStatfsReturnNamemaxTest.ReturnedNamemaxIsCorrect. Assertion/mocking density: EXPECT_EQ x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/FuseStatfsReturnNamemaxTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/testutils/FuseStatfsReturnTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/testutils/FuseStatfsReturnTest.h

Purpose: This file provides the shared FUSE filesystem-stat reporting test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseStatfsTest.h. Classes/fixtures: FuseStatfsReturnTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for filesystem-stat reporting.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/testutils/FuseStatfsReturnTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/testutils/FuseStatfsTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/testutils/FuseStatfsTest.cpp

Purpose: This file provides the shared FUSE filesystem-stat reporting test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseStatfsTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for filesystem-stat reporting.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/testutils/FuseStatfsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/testutils/FuseStatfsTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/testutils/FuseStatfsTest.h

Purpose: This file provides the shared FUSE filesystem-stat reporting test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: string, functional, ../../../testutils/FuseTest.h. Classes/fixtures: FuseStatfsTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for filesystem-stat reporting.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/statfs/testutils/FuseStatfsTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/FuseTruncateErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/FuseTruncateErrorTest.cpp

Purpose: This file tests fspp FUSE path truncate handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseTruncateTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseTruncateErrorTest. Helper functions: none visible. Direct tests: FuseTruncateErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path truncate handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseTruncateErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/FuseTruncateErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/FuseTruncateFilenameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/FuseTruncateFilenameTest.cpp

Purpose: This file tests fspp FUSE path truncate handling, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseTruncateTest.h. Classes/fixtures: FuseTruncateFilenameTest. Helper functions: none visible. Direct tests: FuseTruncateFilenameTest.TruncateFile; FuseTruncateFilenameTest.TruncateFileNested; FuseTruncateFilenameTest.TruncateFileNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path truncate handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseTruncateFilenameTest.TruncateFile; FuseTruncateFilenameTest.TruncateFileNested; FuseTruncateFilenameTest.TruncateFileNested2. Assertion/mocking density: EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/FuseTruncateFilenameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/FuseTruncateSizeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/FuseTruncateSizeTest.cpp

Purpose: This file tests fspp FUSE path truncate handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseTruncateTest.h. Classes/fixtures: FuseTruncateSizeTest. Helper functions: none visible. Direct tests: FuseTruncateSizeTest.TruncateFile.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for path truncate handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseTruncateSizeTest.TruncateFile. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/FuseTruncateSizeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/testutils/FuseTruncateTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/testutils/FuseTruncateTest.cpp

Purpose: This file provides the shared FUSE path truncate handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseTruncateTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for path truncate handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/testutils/FuseTruncateTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/testutils/FuseTruncateTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/testutils/FuseTruncateTest.h

Purpose: This file provides the shared FUSE path truncate handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h. Classes/fixtures: FuseTruncateTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for path truncate handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/truncate/testutils/FuseTruncateTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/FuseUnlinkErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/FuseUnlinkErrorTest.cpp

Purpose: This file tests fspp FUSE unlink handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseUnlinkTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseUnlinkErrorTest. Helper functions: none visible. Direct tests: FuseUnlinkErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for unlink handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseUnlinkErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/FuseUnlinkErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/FuseUnlinkFilenameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/FuseUnlinkFilenameTest.cpp

Purpose: This file tests fspp FUSE unlink handling, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseUnlinkTest.h. Classes/fixtures: FuseUnlinkFilenameTest. Helper functions: none visible. Direct tests: FuseUnlinkFilenameTest.Unlink; FuseUnlinkFilenameTest.UnlinkNested; FuseUnlinkFilenameTest.UnlinkNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for unlink handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseUnlinkFilenameTest.Unlink; FuseUnlinkFilenameTest.UnlinkNested; FuseUnlinkFilenameTest.UnlinkNested2. Assertion/mocking density: EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/FuseUnlinkFilenameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/testutils/FuseUnlinkTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/testutils/FuseUnlinkTest.cpp

Purpose: This file provides the shared FUSE unlink handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseUnlinkTest.h. Classes/fixtures: none visible. Helper functions: Invoke. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for unlink handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/testutils/FuseUnlinkTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/testutils/FuseUnlinkTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/testutils/FuseUnlinkTest.h

Purpose: This file provides the shared FUSE unlink handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h. Classes/fixtures: FuseUnlinkTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for unlink handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/unlink/testutils/FuseUnlinkTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/FuseUtimensErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/FuseUtimensErrorTest.cpp

Purpose: This file tests fspp FUSE timestamp update handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseUtimensTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseUtimensErrorTest. Helper functions: none visible. Direct tests: FuseUtimensErrorTest.ReturnedErrorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for timestamp update handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseUtimensErrorTest.ReturnedErrorIsCorrect. Assertion/mocking density: EXPECT_EQ x1, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/FuseUtimensErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/FuseUtimensFilenameTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/FuseUtimensFilenameTest.cpp

Purpose: This file tests fspp FUSE timestamp update handling, focusing on path/name parameter forwarding from POSIX calls to the fspp mock filesystem.

Important APIs/types/functions: Includes: testutils/FuseUtimensTest.h. Classes/fixtures: FuseUtimensFilenameTest. Helper functions: none visible. Direct tests: FuseUtimensFilenameTest.UtimensFile; FuseUtimensFilenameTest.UtimensFileNested; FuseUtimensFilenameTest.UtimensFileNested2; FuseUtimensFilenameTest.UtimensDir; FuseUtimensFilenameTest.UtimensDirNested; FuseUtimensFilenameTest.UtimensDirNested2.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for timestamp update handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseUtimensFilenameTest.UtimensFile; FuseUtimensFilenameTest.UtimensFileNested; FuseUtimensFilenameTest.UtimensFileNested2; FuseUtimensFilenameTest.UtimensDir; FuseUtimensFilenameTest.UtimensDirNested; FuseUtimensFilenameTest.UtimensDirNested2. Assertion/mocking density: EXPECT_CALL x6.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/FuseUtimensFilenameTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/FuseUtimensTimeParameterTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/FuseUtimensTimeParameterTest.cpp

Purpose: This file tests fspp FUSE timestamp update handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseUtimensTest.h. Classes/fixtures: FuseUtimensTimeParameterTest. Helper functions: none visible. Direct tests: FuseUtimensTimeParameterTest.Utimens.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for timestamp update handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseUtimensTimeParameterTest.Utimens. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/FuseUtimensTimeParameterTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/testutils/FuseUtimensTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/testutils/FuseUtimensTest.cpp

Purpose: This file provides the shared FUSE timestamp update handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseUtimensTest.h, cpp-utils/system/filetime.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for timestamp update handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/testutils/FuseUtimensTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/testutils/FuseUtimensTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/testutils/FuseUtimensTest.h

Purpose: This file provides the shared FUSE timestamp update handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h. Classes/fixtures: FuseUtimensTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for timestamp update handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/utimens/testutils/FuseUtimensTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteDataTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteDataTest.cpp

Purpose: This file tests fspp FUSE write handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: cpp-utils/data/DataFixture.h, testutils/FuseWriteTest.h, ../../testutils/InMemoryFile.h, fspp/fs_interface/FuseErrnoException.h, tuple, cstdlib. Classes/fixtures: FuseWriteDataTest. Helper functions: fileSize. Direct tests: FuseWriteDataTest.DataWasCorrectlyWritten; FuseWriteDataTest.RestOfFileIsUnchanged.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for write handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseWriteDataTest.DataWasCorrectlyWritten; FuseWriteDataTest.RestOfFileIsUnchanged. Assertion/mocking density: EXPECT_TRUE x4, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteDataTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteErrorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteErrorTest.cpp

Purpose: This file tests fspp FUSE write handling, focusing on errno propagation from `FuseErrnoException` or failing backend calls.

Important APIs/types/functions: Includes: testutils/FuseWriteTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseWriteErrorTest. Helper functions: SetUp. Direct tests: FuseWriteErrorTest.ReturnErrorOnFirstWriteCall; FuseWriteErrorTest.ReturnErrorOnSecondWriteCall.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for write handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseWriteErrorTest.ReturnErrorOnFirstWriteCall; FuseWriteErrorTest.ReturnErrorOnSecondWriteCall. Assertion/mocking density: EXPECT_EQ x3, EXPECT_CALL x3.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteErrorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteFileDescriptorTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteFileDescriptorTest.cpp

Purpose: This file tests fspp FUSE write handling, focusing on argument forwarding and boundary handling for modes, flags, descriptors, sizes, times, or data buffers.

Important APIs/types/functions: Includes: testutils/FuseWriteTest.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseWriteFileDescriptorTest. Helper functions: none visible. Direct tests: FuseWriteFileDescriptorTest.FileDescriptorIsCorrect.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for write handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseWriteFileDescriptorTest.FileDescriptorIsCorrect. Assertion/mocking density: EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteFileDescriptorTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteOverflowTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteOverflowTest.cpp

Purpose: This file tests fspp FUSE write handling, focusing on return-value translation, buffer contents, stat fields, or overflow/short I/O behavior.

Important APIs/types/functions: Includes: cpp-utils/data/DataFixture.h, testutils/FuseWriteTest.h, ../../testutils/InMemoryFile.h, fspp/fs_interface/FuseErrnoException.h. Classes/fixtures: FuseWriteOverflowTest, FuseWriteOverflowTestWithNonemptyFile, FuseWriteOverflowTestWithEmptyFile. Helper functions: FuseWriteOverflowTestWithNonemptyFile, FuseWriteOverflowTestWithEmptyFile. Direct tests: FuseWriteOverflowTestWithNonemptyFile.WriteMoreThanFileSizeFromBeginning; FuseWriteOverflowTestWithNonemptyFile.WriteMoreThanFileSizeFromMiddle; FuseWriteOverflowTestWithNonemptyFile.WriteAfterFileEnd; FuseWriteOverflowTestWithEmptyFile.WriteToBeginOfEmptyFile; FuseWriteOverflowTestWithEmptyFile.WriteAfterFileEnd.

Control flow: The test configures `MockFilesystem` expectations, mounts a temporary FUSE filesystem with `FuseTest`/operation-specific helpers, performs the corresponding POSIX call, and checks the returned value, errno, mock arguments, or output buffer/stat structure.

State and persistence behavior: Runtime state is the temporary mount, mock filesystem expectation state, POSIX descriptors when needed, errno, and operation-specific buffers or structs. File contents are usually modeled by in-memory helper data rather than durable storage.

Dependencies and integration points: It connects Linux/POSIX syscall semantics for write handling to the fspp `Filesystem` interface and validates the adapter contract used by real CryFS mounts.

Risks: Adapter mistakes can swap paths, descriptors, modes, sizes, or errno values. Parameterized errno and boundary-value tests reduce risk but still rely on the shared fixture behaving correctly.

Test signals: Primary signals are FuseWriteOverflowTestWithNonemptyFile.WriteMoreThanFileSizeFromBeginning; FuseWriteOverflowTestWithNonemptyFile.WriteMoreThanFileSizeFromMiddle; FuseWriteOverflowTestWithNonemptyFile.WriteAfterFileEnd; FuseWriteOverflowTestWithEmptyFile.WriteToBeginOfEmptyFile; FuseWriteOverflowTestWithEmptyFile.WriteAfterFileEnd. Assertion/mocking density: EXPECT_EQ x5, EXPECT_TRUE x7, EXPECT_CALL x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/FuseWriteOverflowTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/testutils/FuseWriteTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/testutils/FuseWriteTest.cpp

Purpose: This file provides the shared FUSE write handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: FuseWriteTest.h. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for write handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/testutils/FuseWriteTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/testutils/FuseWriteTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/testutils/FuseWriteTest.h

Purpose: This file provides the shared FUSE write handling test fixture/helper for fspp. It hides mount setup, POSIX syscall invocation, descriptor opening, and error capture so focused tests can assert one parameter or result dimension at a time.

Important APIs/types/functions: Includes: ../../../testutils/FuseTest.h, ../../../testutils/OpenFileHandle.h. Classes/fixtures: FuseWriteTest. Helper functions: none visible. Direct tests: none; helper fixture used by operation-specific tests.

Control flow: A concrete test inherits this fixture, configures `MockFilesystem` expectations, calls the helper that performs the real POSIX/FUSE operation against `TempTestFS::mountDir`, and then inspects return values or `errno` captured by the helper.

State and persistence behavior: State includes a temporary mount directory, optional `OpenFileHandle` descriptors, mock expectation state, errno/result structs, and any in-memory file data created by the test. Teardown should unmount and release descriptors.

Dependencies and integration points: It integrates operation-specific tests with `FuseTest`, `OpenFileHandle`, POSIX syscalls, and the fspp `Filesystem` mock method for write handling.

Risks: A helper bug can invalidate many narrow tests for the same operation. Descriptor lifetime and errno reset order are particularly important for reliable error assertions.

Test signals: Successful helpers assert zero errno and expected byte/count results; error helpers preserve the exact errno returned through the FUSE adapter.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/fuse/write/testutils/FuseWriteTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/impl/FuseOpenFileListTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/impl/FuseOpenFileListTest.cpp

Purpose: This file tests `FuseOpenFileList`, the table that maps FUSE file-handle IDs to live `OpenFile` objects.

Important APIs/types/functions: Includes: gtest/gtest.h, gmock/gmock.h, fspp/impl/FuseOpenFileList.h, stdexcept. Classes/fixtures: MockOpenFile. Helper functions: MockOpenFile, open, check. Direct tests: FuseOpenFileListTest.EmptyList1; FuseOpenFileListTest.EmptyList2; FuseOpenFileListTest.InvalidId; FuseOpenFileListTest.Open1AndGet; FuseOpenFileListTest.Open2AndGet; FuseOpenFileListTest.Open3AndGet; FuseOpenFileListTest.GetClosedItemOnEmptyList; FuseOpenFileListTest.GetClosedItemOnNonEmptyList; FuseOpenFileListTest.CloseOnEmptyList1; FuseOpenFileListTest.CloseOnEmptyList2; FuseOpenFileListTest.RemoveInvalidId.

Control flow: Tests add/open objects, retrieve them by ID, remove/close them, and assert object identity or thrown exceptions for invalid/removed IDs.

State and persistence behavior: Runtime state is the open-file list, generated IDs, stored unique pointers, and removed/closed slots. There is no disk persistence.

Dependencies and integration points: The container under test supports FUSE adapter handle management, so it integrates with open/close/read/write operation paths indirectly.

Risks: Bad handle allocation/removal can return wrong open files to later FUSE calls or leak handles.

Test signals: Primary signals are FuseOpenFileListTest.EmptyList1; FuseOpenFileListTest.EmptyList2; FuseOpenFileListTest.InvalidId; FuseOpenFileListTest.Open1AndGet; FuseOpenFileListTest.Open2AndGet; FuseOpenFileListTest.Open3AndGet; FuseOpenFileListTest.GetClosedItemOnEmptyList; FuseOpenFileListTest.GetClosedItemOnNonEmptyList. Assertion/mocking density: EXPECT_EQ x2, EXPECT_TRUE x1, EXPECT_FALSE x1.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/impl/FuseOpenFileListTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/impl/IdListTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/fspp/impl/IdListTest.cpp

Purpose: This file tests `IdList`, a generic ID-to-object container used by fspp internals.

Important APIs/types/functions: Includes: gtest/gtest.h, fspp/impl/IdList.h, stdexcept. Classes/fixtures: MyObj. Helper functions: MyObj, add, check, checkConst. Direct tests: IdListTest.EmptyList1; IdListTest.EmptyList2; IdListTest.InvalidId; IdListTest.GetRemovedItemOnEmptyList; IdListTest.GetRemovedItemOnNonEmptyList; IdListTest.RemoveOnEmptyList1; IdListTest.RemoveOnEmptyList2; IdListTest.RemoveInvalidId; IdListTest.Add1AndGet; IdListTest.Add2AndGet; IdListTest.Add3AndGet; IdListTest.Add3AndConstGet.

Control flow: Tests add/open objects, retrieve them by ID, remove/close them, and assert object identity or thrown exceptions for invalid/removed IDs.

State and persistence behavior: Runtime state is the ID list, object ownership, active/removed slots, and exception behavior for invalid IDs. There is no disk persistence.

Dependencies and integration points: The container under test supports FUSE adapter handle management, so it integrates with open/close/read/write operation paths indirectly.

Risks: ID reuse and invalid-ID handling are foundational for higher-level FUSE handle maps.

Test signals: Primary signals are IdListTest.EmptyList1; IdListTest.EmptyList2; IdListTest.InvalidId; IdListTest.GetRemovedItemOnEmptyList; IdListTest.GetRemovedItemOnNonEmptyList; IdListTest.RemoveOnEmptyList1; IdListTest.RemoveOnEmptyList2; IdListTest.RemoveInvalidId. Assertion/mocking density: EXPECT_EQ x2.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/fspp/impl/IdListTest.cpp -->
