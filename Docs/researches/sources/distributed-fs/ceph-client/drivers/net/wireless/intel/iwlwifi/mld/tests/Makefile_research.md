# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/Makefile

Purpose: Builds the `iwlmld-tests` KUnit module when `CONFIG_IWLWIFI_KUNIT_TESTS` is enabled.

Important APIs and files: Aggregates `module.o`, `hcmd.o`, `utils.o`, `link.o`, `rx.o`, `agg.o`, and `link-selection.o`; adds the parent MLD directory to include paths; and registers `iwlmld-tests.o` as the config-selected object.

Control flow and integration: Kbuild compiles these test objects into one module that imports iwlwifi namespaces and runs KUnit suites registered by each source file.

State and persistence: No runtime state beyond Kbuild object membership.

Dependencies: Depends on KUnit, iwlwifi KUnit exports, and the parent MLD source include path.

Risks: New test files must be added to `iwlmld-tests-y` or they will silently not run. Include path drift can hide dependency problems.

Test signals: `CONFIG_IWLWIFI_KUNIT_TESTS=y/m` should build this module and list all suites in KUnit output.
