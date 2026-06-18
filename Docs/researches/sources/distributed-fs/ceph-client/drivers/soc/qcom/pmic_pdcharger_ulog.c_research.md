<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.c -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.c

Purpose: debugging rpmsg driver that periodically requests PMIC ChargerPD ulog text and emits each log line through a tracepoint. It is intentionally not auto-loaded through a module device table.

Important APIs/types/functions: `struct pmic_pdcharger_ulog` holds the rpmsg device and delayed work. `struct pmic_pdcharger_ulog_hdr`, `get_ulog_req_msg`, and `get_ulog_resp_msg` define the GLINK/rpmsg message format. Internal functions are `pmic_pdcharger_ulog_write_async()`, `pmic_pdcharger_ulog_request()`, `pmic_pdcharger_ulog_work()`, `pmic_pdcharger_ulog_handle_message()`, `pmic_pdcharger_ulog_rpmsg_callback()`, probe, and remove. `CREATE_TRACE_POINTS` includes `pmic_pdcharger_ulog.h` to instantiate `trace_pmic_pdcharger_ulog_msg()`.

Control flow: rpmsg probe allocates state, initializes delayed work, stores drvdata, and immediately sends a `GET_CHG_ULOG_REQ` with `MAX_ULOG_SIZE`. The rpmsg callback reads the opcode; for `GET_CHG_ULOG_REQ` responses it schedules the next request after one second and parses the response buffer into newline-separated trace messages. Remove cancels delayed work. Unknown opcodes are logged as errors.

State and persistence: the only runtime state is the rpmsg pointer and delayed polling work. Firmware log contents are transient; the driver does not store them, exposing them only as trace events. The response buffer is forcibly NUL-terminated at `MAX_ULOG_SIZE - 1` before line splitting.

Dependencies and integration: depends on rpmsg channel `PMIC_LOGS_ADSP_APPS`, Linux tracepoint infrastructure, and the local trace header. It includes PDR and debugfs headers but does not use them directly. Lack of `MODULE_DEVICE_TABLE` is intentional so users load it manually for debugging.

Risks and test signals: `pmic_pdcharger_ulog_rpmsg_callback()` dereferences the message header without checking `len >= sizeof(*hdr)`, so truncated rpmsg packets can read beyond the provided buffer. Request messages assign `log_size` without endian conversion while the header uses little-endian fields; this should match firmware expectations or be corrected. `pmic_pdcharger_ulog_request()` return value is ignored on probe. Test signals include manual module load, initial request success, one-second polling cadence, full 8192-byte response parsing, newline tokenization into trace events, remove cancellation, unknown opcode handling, and truncated packet robustness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.c -->
