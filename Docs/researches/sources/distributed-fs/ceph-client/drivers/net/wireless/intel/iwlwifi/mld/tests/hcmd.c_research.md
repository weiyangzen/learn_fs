# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tests/hcmd.c

Purpose: Verifies firmware host-command name metadata used by iwlwifi MLD debug/dispatch paths.

Important APIs and functions: `test_hcmd_names_sorted()` checks every populated command-name array is sorted by command ID. `test_hcmd_names_for_rx()` checks every MLD RX handler command ID resolves to a known command string through `iwl_get_cmd_string()`.

Control flow: The suite iterates exported `iwl_mld_groups` and `iwl_mld_rx_handlers`, using a synthetic `iwl_trans` command-group config for name lookup.

State and persistence: No persistent state. A stack `iwl_trans` is enough for command string lookup.

Dependencies and integration points: Imports the `EXPORTED_FOR_KUNIT_TESTING` namespace, depends on exported command group arrays and RX handler tables from production MLD code, and uses KUnit assertions.

Risks: The tests catch sortedness and unknown names but not semantic correctness of names or handler command IDs. Arrays hidden behind config conditionals may need build-variant coverage.

Test signals: KUnit should fail if new RX handlers lack command names or command arrays are appended out of order.
