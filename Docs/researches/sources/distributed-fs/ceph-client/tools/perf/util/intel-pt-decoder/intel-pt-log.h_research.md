# sources/distributed-fs/ceph-client/tools/perf/util/intel-pt-decoder/intel-pt-log.h

Purpose: declares Intel PT logging controls and provides low-overhead logging macros that compile into cheap enabled checks.

Important APIs and types: declares `intel_pt_log_fp()`, `intel_pt_log_enable()`, `intel_pt_log_disable()`, `intel_pt_log_set_name()`, `intel_pt_log_dump_buf()`, packet and instruction logging functions, and formatted `__intel_pt_log()`. Macros `intel_pt_log`, `intel_pt_log_packet`, `intel_pt_log_insn`, and `intel_pt_log_insn_no_data` call the backing functions only when `intel_pt_enable_logging` is true. Inline helpers log common "at", "to", and variable messages.

Control flow: decoder code invokes macros freely; when disabled, only a boolean branch is paid. When enabled, work is delegated to `intel-pt-log.c`.

State and persistence: declares external global `intel_pt_enable_logging`; actual file/buffer state is in the C file.

Dependencies and integration: includes Linux compiler attributes for printf checking and standard integer formatting macros. It is included by the packet/instruction decoder logging paths and main PT decoder.

Risks: macros evaluate arguments only when enabled, which is intended but can hide side effects if callers pass expressions with side effects. Global logging configuration applies to all decoders.

Test signals: compile-time printf attribute warnings, disabled macro side-effect expectations, and integration tests confirming logs appear only after enable.
