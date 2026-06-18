# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/psp_responder.c

Purpose: Remote-side helper used by `psp.py` to accept TCP data connections, create PSP associations through YNL, exchange SPI/key material with the client, count received bytes, and expose a simple control protocol.

Important APIs/types/functions: Defines `struct opts`, global quit flag, PSP version descriptors, `conn_setup_psp`, `handle_cmd`, `spawn_server`, `run_responder`, `parse_cmd_opts`, `psp_dev_set_ena`, and `main`. Uses sockets, `poll`, `accept`, `send`, `recv`, YNL generated PSP APIs, and ifindex/port command options.

Control flow: Main parses port/ifindex, opens a YNL PSP socket, enables PSP versions, opens a server socket, and processes commands from the Python control connection. Commands select clear or PSP connection mode, close current data socket, report received length, or exit. PSP mode accepts a data socket, creates Rx assoc, exchanges keys with the client, creates Tx assoc, and then accumulates received data.

State and persistence: Holds server and data sockets, accumulated receive offset in a static buffer, selected PSP versions, and device PSP enablement. All state is process-local and should end with the helper.

Dependencies and integration: Compiles against kernel selftest YNL support and PSP generated headers. It is deployed/run by `NetDrvEpEnv.remote.deploy("psp_responder")`.

Risks: Static receive buffer/offset require careful reset across connections. The control protocol is binary/string and must match `psp.py`. Socket and YNL errors must be reported back as `ack`/`err` or the Python side can hang.

Test signals: Correct behavior is listening on the requested port, acknowledging commands, returning received byte counts, performing PSP key exchange/associations, and exiting cleanly on `exit`.
