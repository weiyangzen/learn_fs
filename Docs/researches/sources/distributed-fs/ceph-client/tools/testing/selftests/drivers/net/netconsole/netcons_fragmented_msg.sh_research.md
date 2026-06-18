<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_fragmented_msg.sh -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_fragmented_msg.sh

Purpose: validates netconsole fragmentation and receiver-side reconstruction behavior for long messages and long userdata, with and without release-version appending.

Important functions/APIs: `header_to_regex`, `extract_msg`, `validate_fragmented_result`; helper calls `check_for_dependencies`, `set_network`, `create_dynamic_target`, `set_user_data`, `disable_release_append`, `listen_port_and_save_to`, `wait_local_port_listen`, and cleanup.

Control flow: configures netconsole with long userdata, sends an oversized message to `/dev/kmsg`, captures fragments, strips generated `ncfrag` headers, and verifies body plus userdata. Then disables release append and repeats with a smaller but still fragmented message.

State/dependencies: dynamic target, userdata configfs, `/tmp/$TARGET`, socat listener, printk level. Risks include regex fragility around header format, not explicitly cleaning between two captures, and fragmented UDP timing. Test signals are reconstructed message body and userdata presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netconsole/netcons_fragmented_msg.sh -->
