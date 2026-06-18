<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_occ.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_occ.sh

Purpose: validates reference counting of mlxsw single-rate policer resources when tc filters create, share, and delete police actions.

Important functions/APIs: topology helpers `h1_create`, `switch_create`, `setup_prepare`, `cleanup`; `tc_police_occ_get`; `tc_police_occ_test`. Uses `devlink_resource_occ_get global_policers single_rate_policers` and `tc filter flower skip_sw action police`.

Control flow: records initial policer occupancy, adds a rule with a unique policer and expects +1, deletes it and expects baseline, then adds two filters sharing `index 10`, confirms occupancy stays +1 until the last reference is removed.

State/dependencies: clsact qdisc, police actions, devlink resource occupancy. Risks include shared action index collisions with pre-existing actions and changed policer accounting. Test signals are exact occupancy comparisons after each add/delete step.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/mlxsw/tc_police_occ.sh -->
