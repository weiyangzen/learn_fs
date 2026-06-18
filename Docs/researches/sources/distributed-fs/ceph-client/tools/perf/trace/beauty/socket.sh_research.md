# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/socket.sh

Purpose: Generates socket protocol and socket level lookup tables.

Important APIs/types/functions: It emits `socket_ipproto[]`, `socket_level[]`, and `DEFINE_STRARRAY(socket_level, "SOL_")`.

Control flow: With optional UAPI and beauty header directories, it parses enum-style `IPPROTO_* = number` entries from `linux/in.h` and `SOL_*` decimal defines from `include/linux/socket.h`, sorts both numerically, and prints arrays.

State and persistence: stdout-only generator.

Dependencies and integration points: Output is included by `socket.c`.

Risks: It only accepts decimal `SOL_*` values and enum formatting for IP protocols. Architecture special cases are handled in the C consumer rather than this generator.

Test signals: Regenerate and confirm common protocols and levels; compile and trace socket calls.
