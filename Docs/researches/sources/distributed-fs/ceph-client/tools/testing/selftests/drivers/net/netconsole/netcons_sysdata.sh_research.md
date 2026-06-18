<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_sysdata.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_sysdata.sh

Purpose: validates netconsole extended sysdata fields for CPU number, task name, kernel release, msgid, and interaction with userdata.

Important functions/APIs: setters/unsetters for `cpu_nr_enabled`, `taskname_enabled`, `release_enabled`, `msgid_enabled`; validators `validate_sysdata`, `validate_release`, `validate_no_sysdata`; `runtest`; helper calls `check_for_dependencies`, `check_for_taskset`, `set_network`, `create_dynamic_target`, `set_user_data`, and UDP listener helpers.

Control flow: creates dynamic target, then runs three captures. Test 1 enables sysdata fields and sends from a random CPU with `taskset`; Test 2 adds userdata while sysdata remains enabled; Test 3 disables sysdata and verifies none of the fields are present. Each test writes to `/dev/kmsg`, waits for capture, and greps expected fields.

State/dependencies: configfs sysdata/userdata toggles, random CPU selection, `taskset`, `/tmp` capture files, socat process. Risks include random CPU greater than allowed cpuset, grep format assumptions, release field timing, and cleanup of captures/socat on validator failure. Test signals are field presence/absence and matching CPU/task/release/msgid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_sysdata.sh -->
