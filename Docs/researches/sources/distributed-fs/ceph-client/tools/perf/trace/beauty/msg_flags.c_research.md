# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/msg_flags.c

Purpose: Formats socket message flags for send/recv style syscalls.

Important APIs/types/functions: `syscall_arg__scnprintf_msg_flags` recognizes many `MSG_*` constants, including local fallbacks for newer flags such as `MSG_ZEROCOPY`, `MSG_SPLICE_PAGES`, and `MSG_CMSG_CLOEXEC`.

Control flow: Zero flags print as `NONE`. A macro-driven sequence appends known flags and clears them from the working value; leftover bits are appended as hex.

State and persistence: Stateless formatting only.

Dependencies and integration points: Depends on `<sys/socket.h>` and perf trace `SCA_MSG_FLAGS` binding.

Risks: Manual ordering can affect output expectations. New kernel flags need local fallback constants or generated support to avoid pure hex output on older build hosts.

Test signals: Trace send/recv syscalls with no flags, common flags, and unknown bits; verify prefix behavior and hex fallback.
