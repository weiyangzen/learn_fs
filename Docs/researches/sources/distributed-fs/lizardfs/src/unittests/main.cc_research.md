# sources/distributed-fs/lizardfs/src/unittests/main.cc

Purpose: Common GoogleTest main for LizardFS unit tests.

Important APIs/types/functions: `main`; `testing::InitGoogleTest`; `RUN_ALL_TESTS`; `setupApplicationName`; `setup_local_empty_lizardfs_info`.

Control flow: Initializes application name and local LizardFS info, initializes GTest, and runs all tests.

State and persistence: Process initialization only. It may set common application metadata for logging/config behavior.

Dependencies and integration: Linked into test binaries needing a standard main. Depends on GTest and common setup functions.

Risks and test signals: Minimal risk. Any setup side effects apply to every test binary using this main.
