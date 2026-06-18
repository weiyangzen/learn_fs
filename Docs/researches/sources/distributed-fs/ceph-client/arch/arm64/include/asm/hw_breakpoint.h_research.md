## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hw_breakpoint.h

Purpose: declares arm64 hardware breakpoint/watchpoint data structures, register encodings, and perf/ptrace integration hooks.

Important APIs/types/functions: defines `struct arch_hw_breakpoint_ctrl`, `struct arch_hw_breakpoint`, privilege/type/length constants, kernel step states, max BRP/WRP counts, debug register accessor macros, `encode_ctrl_reg`, `decode_ctrl_reg`, breakpoint parse/install/uninstall/read/slot APIs, thread-switch copy hooks, `get_num_brps`, `get_num_wrps`, and CPU suspend debug restore hook.

Control flow: perf/ptrace config is parsed into architecture breakpoint state, installed into debug registers, handled on exceptions, and restored across context switches and suspend.

State and persistence: breakpoint/watchpoint registers are CPU-local hardware state; per-task breakpoint state lives in perf/ptrace structures.

Dependencies and integration: depends on cputype/cpufeature/sysreg/virt and integrates perf, ptrace, debug monitors, exception handling, and CPU PM.

Risks: privilege or length encoding mistakes can miss watchpoints or trap in the wrong context. Test signals are perf hw_breakpoint tests, ptrace watchpoint tests, KVM/hyp mode checks, CPU hotplug, and suspend/resume with active breakpoints.
