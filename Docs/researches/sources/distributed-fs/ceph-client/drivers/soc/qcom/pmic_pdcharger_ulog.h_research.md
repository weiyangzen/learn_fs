<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.h -->
# sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.h

Purpose: tracepoint definition header for the PMIC ChargerPD ulog debug driver. It defines the `pmic_pdcharger_ulog_msg` event that carries one parsed firmware log line.

Important APIs/types/functions: the sole trace event is `TRACE_EVENT(pmic_pdcharger_ulog_msg, TP_PROTO(char *msg), TP_ARGS(msg), TP_STRUCT__entry(__string(msg, msg)), TP_fast_assign(__assign_str(msg)), TP_printk("%s", __get_str(msg)))`. The header also sets `TRACE_SYSTEM`, `TRACE_INCLUDE_PATH`, and `TRACE_INCLUDE_FILE` and includes `<trace/define_trace.h>` outside the include guard as required by Linux tracepoint conventions.

Control flow: there is no normal function flow. When included with `CREATE_TRACE_POINTS` in `pmic_pdcharger_ulog.c`, this header creates the tracepoint definition; other inclusions would provide declarations.

State and persistence: tracepoint instances copy the string into the trace ring buffer via `__string`/`__assign_str`. Persistence is limited to the kernel tracing buffer configured by the user.

Dependencies and integration: depends on Linux tracepoint infrastructure and the `.c` file's `CREATE_TRACE_POINTS` include pattern. The event name is consumed by ftrace/perf/trace-cmd users who enable `pmic_pdcharger_ulog:pmic_pdcharger_ulog_msg`.

Risks and test signals: trace headers are sensitive to include guard and `TRACE_INCLUDE_*` correctness; wrong values break trace generation or module build. Test signals are successful module build, presence of the event under tracing events, and emitted log lines matching tokens parsed by `pmic_pdcharger_ulog_handle_message()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/qcom/pmic_pdcharger_ulog.h -->
