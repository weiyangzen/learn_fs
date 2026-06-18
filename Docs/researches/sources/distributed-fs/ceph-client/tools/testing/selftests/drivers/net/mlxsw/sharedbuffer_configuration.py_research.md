<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer_configuration.py -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer_configuration.py

Purpose: Python selftest for mlxsw devlink shared-buffer configuration mutability. It randomly changes pool sizes/types, TC bindings, and port-pool thresholds, verifies only intended objects changed, then restores recorded defaults.

Important classes/APIs: `RandomValuePicker`, `RecordValuePicker`, `CommonItem`, `CommonList`, `Pool`, `TcBind`, `PortPool`, `Port`, and list wrappers. Key functions include `run_cmd`, `run_json_cmd`, `log_test`, `get_pools`, `do_check_pools`, `check_pools`, `get_tcbinds`, `do_check_tcbind`, `check_tcbind`, `get_portpools`, `do_check_portpool`, `check_portpool`, `get_ports`, `get_device`, and `test_sb_configuration`.

Control flow: seed is fixed with `random.seed(0)`, first mlxsw Spectrum devlink device is selected, physical ports and pools are enumerated, then each resource class is randomized and restored. Mutable fields are compared via `var_tuple`, while `weak_eq` ignores variable fields to locate the same object after changes.

State/dependencies: modifies devlink SB configuration in-place, then restores it using recorded values. It depends on `devlink -j`, shell commands via `subprocess.check_output`, JSON schema stability, and Spectrum driver presence. Risks include no `finally` restoration on exception, shell=True command construction, hard-coded immutable pool/TC rules, and Python assertion reliance. Test signals are printed `[ OK ]`/`[FAIL]` lines for object existence, exact value matches, and no collateral configuration changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/sharedbuffer_configuration.py -->
