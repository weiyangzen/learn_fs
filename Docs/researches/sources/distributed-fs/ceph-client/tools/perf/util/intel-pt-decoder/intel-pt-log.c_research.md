# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-log.c

Purpose: optional debug logging backend for Intel PT decoding. It prints decoded packets, decoded instructions, and formatted messages either to stdout, to a named log file, or into an in-memory circular buffer that can be dumped on error.

Important APIs and types: global state includes `intel_pt_enable_logging`, file pointer `f`, `log_name`, dump-on-error settings, and `struct log_buf`. Public functions enable/disable logging, set log name, expose the file pointer, dump buffered logs, and emit packet/instruction/message records through `__intel_pt_log*` functions.

Control flow: logging macros in the header guard calls with `intel_pt_enable_logging`. First real log lazily opens the backend. If dump-on-error is enabled, `fopencookie()` routes writes into `log_buf__write()`; `intel_pt_log_dump_buf()` flushes and writes the circular buffer to the backend. Packet/instruction printers format raw bytes plus decoder descriptions.

State and persistence: logging is process-global, not per decoder. File-backed logs persist as `<name>.log`; buffered logs persist only until dumped or closed. `intel_pt_log_disable()` flushes but does not close the file.

Dependencies and integration: uses packet and instruction description helpers, stdio, GNU `fopencookie`, and Linux allocation helpers. Integrated throughout `intel-pt-decoder.c`.

Risks: global state is not thread-safe; `intel_pt_log_set_name()` uses `strncpy` plus `strcat` and assumes enough NUL termination from the static zeroed buffer; repeated enable/open behavior can retain an old file pointer. Circular buffer drops partial first lines after wrap.

Test signals: logging disabled no-op behavior, file-name creation, packet/instruction formatting, circular wrap and dump behavior, and error-path dump-on-error tests.
