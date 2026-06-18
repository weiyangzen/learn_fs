# sources/distributed-fs/ceph-client/samples/qmi/qmi_sample_client.c

## Purpose

This kernel module is a sample Qualcomm QMI client over QRTR. It discovers the test QMI service, creates one platform device per discovered server, connects a QMI handle to the remote port, and exposes debugfs files that send ping and data transactions.

## Important APIs, Types, and Functions

The file defines QMI TLV structures and `qmi_elem_info` arrays for name, ping request/response, and data request/response messages. `ping_write()` uses a custom response callback path with `qmi_txn_init`, `qmi_send_request`, and `qmi_txn_wait`; `ping_pong_cb()` validates the pong response. `data_write()` allocates request/response buffers, copies user data, sends a data request, and verifies the echoed response decoded by QMI helpers. Driver lifecycle is handled by `qmi_sample_probe()`, `qmi_sample_remove()`, `qmi_sample_new_server()`, `qmi_sample_del_server()`, `qmi_sample_init()`, and `qmi_sample_exit()`.

## Control Flow

Module init creates `/sys/kernel/debug/qmi_sample`, registers a platform driver, initializes `lookup_client`, and calls `qmi_add_lookup()` for `QMI_SERVICE_ID_TEST`. When a server appears, QMI lookup allocates a platform device with a `sockaddr_qrtr` as platform data. Probe initializes a QMI handle, connects its socket, creates a per-server debugfs directory named `node:port`, and installs `data` and `ping` files. Writes to those files synchronously issue QMI transactions and return either bytes accepted or an errno.

## State and Persistence Behavior

Global state is `lookup_client` and `qmi_debug_dir`. Per-server state is `struct qmi_sample`, containing a QMI handle and debugfs dentries. Remote service association persists through the platform device until lookup deletion or module unload. No data is stored beyond in-flight transactions.

## Dependencies and Integration Points

It depends on debugfs, platform bus, QRTR sockets, `linux/soc/qcom/qmi.h`, and a remote QMI test service. It integrates with QMI service discovery through `qmi_ops`.

## Risks and Edge Cases

Debugfs creation errors unwind manually. `qmi_sample_handlers` uses `decoded_size = sizeof(struct test_ping_req_msg_v01)` for a response handler, which is suspicious and worth build/runtime scrutiny. Data writes allocate large request/response objects and truncate input to 8192 bytes. Transaction timeouts return errors after five seconds.

## Test Signals

Load the module on a system with QRTR test service, observe debugfs directories, write to `ping` and `data`, and check dmesg for response validation errors. Build coverage should include QMI and debugfs enabled.
