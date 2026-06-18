# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_ctl.c

Purpose: this file implements SNIC control-plane requests that are sent over the normal firmware work queue, primarily link events and exchange-version negotiation.

Important APIs, types, and functions: `snic_handle_link()` reads link status/down counts and currently asserts not implemented for non-DAS link handling. `snic_ver_enc()` converts dotted driver version text to a 32-bit firmware value. `snic_queue_exch_ver_req()` allocates an untagged request, encodes `SNIC_REQ_EXCH_VER`, adds it to `spl_cmd_list`, and queues it. `snic_io_exch_ver_cmpl_handler()` decodes firmware version, host id, max concurrent I/O, max SGs, max I/O size, max targets, I/O timeout, and adjusts `shost` limits. `snic_get_conf()` synchronously retries exchange-version up to three times with a stack completion.

Control flow: probe calls `snic_get_conf()` after queues and interrupts are enabled. That function clears `fwinfo`, installs a completion pointer under `snic_lock`, delays for hardware resource initialization, queues exchange-version, waits up to two seconds per attempt, and clears the wait pointer on success or final failure. The completion handler runs from firmware CQ interrupt context, fills `fwinfo`, completes the waiter, and releases the untagged request.

State and persistence: `snic->fwinfo` is the key mutable state. Untagged control requests live on `snic->spl_cmd_list` until completion or cleanup. Link status is cached in `snic->link_status` and `link_down_cnt`.

Dependencies and integration: uses `snic_req_init()`, `snic_handle_untagged_req()`, `snic_queue_wq_desc()`, `snic_release_untagged_req()`, firmware wire structs from `snic_fwint.h`, and vNIC notify helpers.

Risks: link handling intentionally calls `SNIC_ASSERT_NOT_IMPL(1)` for non-DAS events. Exchange-version failure blocks probe. Completion assumes returned `hid` matches config and adjusts SCSI limits at runtime. The version parser returns `-1` for invalid strings, which is then cast to `u32` in the request field.

Test signals: probe should show exchange-version completion and populated firmware limits. Tests should cover ignored first exchange request, firmware max SG smaller/larger than driver max, zero or invalid firmware version response, and link event interrupts.
