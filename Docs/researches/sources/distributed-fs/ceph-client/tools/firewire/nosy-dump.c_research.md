<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.c -->
# sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.c

Purpose: Userspace decoder/logger for the `/dev/nosy` FireWire snoop driver, supporting packet, transaction, and statistics views plus replay from captured binary logs.

Important APIs/types/functions: CLI options are defined with `popt`. Transaction state uses `struct subaction` and `struct link_transaction` from `nosy-dump.h`, stored in `pending_transaction_list`. Core functions include `subaction_create()`, `link_transaction_lookup()`, `handle_request_packet()`, `handle_response_packet()`, `handle_packet()`, `decode_link_packet()`, `print_packet()`, `print_stats()`, terminal mode helpers, and `main()`.

Control flow: Live mode opens `/dev/nosy`, configures noncanonical stdin, applies a tcode filter with `NOSY_IOC_FILTER`, starts capture with `NOSY_IOC_START`, then polls the device and stdin. Replay mode reads records from an input file. Packet view decodes each packet immediately; transaction view assembles requests/responses by node and tlabel before protocol decoding; stats view updates counters periodically.

State and persistence: Runtime state includes global options, pending transaction lists, terminal attributes, stats counters, and output file handles. Persistent state is optional binary capture output containing length-prefixed packet records.

Dependencies/integration: Depends on Linux FireWire constants, `nosy-user.h` ioctls from the driver include path, libpopt, terminal APIs, and the FCP decoder. It integrates directly with the kernel nosy driver and FireWire packet formats.

Risks/tests: Risks include raw packet length trust, bitfield/endian assumptions, terminal restoration on abrupt exit, infinite pending transaction growth for incomplete captures, and limited transaction decoding because `handle_transaction()` currently returns after FCP handling. Test signals are live capture, replay input, `--hex`, `--stats`, `--transaction`, iso/cycle filters, SIGINT behavior, and malformed/short packet logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/nosy-dump.c -->
