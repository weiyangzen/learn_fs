# sources/distributed-fs/ceph-client/tools/net/ynl/tests/devlink.c

Purpose: C kselftest for generated devlink YNL bindings. It validates dump and info-get paths against available devlink devices, usually provided by the netdevsim wrapper.

Important APIs/functions: fixture `devlink` opens `ynl_sock_create(&ynl_devlink_family, NULL)` and destroys it. `TEST_F(devlink, dump)` calls `devlink_get_dump()`, iterates with `ynl_dump_foreach`, and verifies `bus_name` and `dev_name` lengths. `TEST_F(devlink, info)` allocates `devlink_info_get_req`, sets bus/dev name, calls `devlink_info_get()`, checks driver name and prints running firmware versions.

Control flow/state: tests skip if dumps are empty. Request objects and response/list objects are allocated and freed with generated helpers. The socket holds any YNL error state used in failure logs.

Dependencies/integration: includes `devlink-user.h`, `ynl.h`, and kselftest harness. Shell wrapper `devlink.sh` creates netdevsim before running this binary.

Risks/test signals: depends on at least one devlink-capable device. It checks presence metadata and nested multi-attr parsing for firmware versions. Failures usually indicate generated request setters, dump list parsing, string allocation, or devlink kernel support regressions.
