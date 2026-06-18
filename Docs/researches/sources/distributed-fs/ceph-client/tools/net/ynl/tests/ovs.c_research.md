# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ovs.c

Purpose: C selftest for Open vSwitch datapath generated YNL bindings, covering create, get, dump, and cleanup.

Important APIs/functions: fixture opens `ynl_ovs_datapath_family` and tracks `dp_name`. `ovs_print_datapath()` validates datapath name and header ifindex and prints pid/cache fields. `TEST_F(ovs, crud)` creates datapath `ynl-test`, gets it by name, verifies the returned name, dumps all datapaths, and confirms the new one appears.

Control flow/state: teardown deletes `self->dp_name` if set, using generated delete request helpers. Request and response objects are heap allocated through generated alloc/free APIs. Kernel OVS datapath state is persistent until teardown.

Dependencies/integration: includes `ovs_datapath-user.h`, YNL runtime, kselftest harness, and requires Open vSwitch kernel support/module with sufficient privileges.

Risks/test signals: if creation succeeds but teardown cannot allocate/delete, state may remain. Strong signals include fixed-header parsing (`dp_ifindex`), string setters, CRUD operation tables, and dump list iteration.
