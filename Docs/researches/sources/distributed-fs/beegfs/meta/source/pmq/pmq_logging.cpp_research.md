## sources/distributed-fs/beegfs/meta/source/pmq/pmq_logging.cpp

Purpose: implements PMQ logging. In normal BeeGFS metadata-server builds it forwards messages to the BeeGFS `Logger`; in `PMQ_TEST` builds it buffers formatted messages in a local blocking ring for tests or standalone consumers.

Important APIs and types: `Log_Buffer` owns a 1024-message circular buffer, mutex, and two condition variables. `pmq_write_log_message`, `pmq_read_log_message`, `pmq_try_read_log_message`, and timeout read functions expose low-level message transport. `log_msg_printfv`, `log_msg_printf`, `pmq_msg_ofv`, and `pmq_msg_of` format severity, message body, optional errno text, and source location.

Control flow: callers use macros from `pmq_logging.hpp` to create `PMQ_Msg_Options`; `pmq_msg_ofv` formats a `Log_Message`. In integrated mode, it maps PMQ debug/info/warn/error to BeeGFS log priorities and calls `Logger::log`. In test mode, it applies `PMQ_LOG_LEVEL`, prefixes severity text, appends newline, and writes into `global_log_buffer`.

State and persistence behavior: logging state is process-local. `global_log_buffer` persists only for the process lifetime and can block writers when full in test mode.

Dependencies and integration points: depends on `pmq_common.hpp` for allocation and profiled mutex/condition macros, and on BeeGFS `Logger` outside test builds. Errno text uses `strerror_r` with GNU/XSI branches.

Risks: test-mode logging can block indefinitely if no reader drains the fixed ring. Integrated mode does not perform the same local log-level early return as test mode. `log_msg_printfv` clamps `msg->size` after `vsnprintf`, which avoids overflow but truncates silently.

Test signals: tests should cover severity mapping, errno formatting under GNU and XSI `strerror_r`, blocking/try/timeout reads, truncation to `Log_Message` capacity, and compile behavior for `PMQ_TEST` without `PMQ_LOG_LEVEL`.
