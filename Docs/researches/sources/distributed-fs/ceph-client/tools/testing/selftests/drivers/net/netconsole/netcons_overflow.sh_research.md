<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_overflow.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_overflow.sh

Purpose: tests netconsole userdata capacity limit enforcement.

Important functions/APIs: `MAX_USERDATA_ITEMS=256`, `create_userdata_max_entries`, `verify_entry_limit`, plus helper calls `check_for_dependencies`, `set_network`, `create_dynamic_target`, `set_user_data`, and cleanup.

Control flow: creates a dynamic target, creates 256 userdata entries successfully by changing `USERDATA_KEY`, then attempts to create one more directory under configfs and expects failure.

State/dependencies: configfs userdata directories, dynamic netconsole target, netdevsim network. Risks include hard-coded limit drift, pre-existing userdata entries affecting count, and direct mkdir bypassing helper validation. Test signals are no failure while creating max entries and failure when exceeding the limit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_overflow.sh -->
