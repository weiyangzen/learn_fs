# sources/distributed-fs/ceph-client/tools/perf/tests/bp_account.c

Purpose: `bp_account.c` validates hardware breakpoint/watchpoint slot accounting when a watchpoint is modified into an instruction breakpoint.

Important APIs and state: `__event` creates `PERF_TYPE_BREAKPOINT` events through `sys_perf_event_open`; `wp_event` and `bp_event` select watchpoint or breakpoint setup. Detection helpers count available slots, check `PERF_EVENT_IOC_MODIFY_ATTRIBUTES`, and discover whether watchpoints and breakpoints share slots. The suite is `"Breakpoint accounting"`.

Control flow: unsupported architectures skip. The test detects watchpoint count, breakpoint count, modify-attributes support, and shared-slot behavior. It fills watchpoint slots, modifies the first event into a breakpoint, and when slots are separate, creates one more watchpoint to verify accounting was released or reclassified correctly.

State and persistence: state is kernel perf event file descriptors and debug-register allocation. All opened fds are closed.

Dependencies, integration, risks, and tests: it depends on hardware breakpoint support, perf_event permissions, default breakpoint length helpers, and architecture behavior. Risks include environment-specific slot counts, unsupported PowerPC/S390 paths, and failures when security policy blocks perf_event_open. Test signals are successful slot detection, successful modify ioctl, and no failed watchpoint creation after modification.
