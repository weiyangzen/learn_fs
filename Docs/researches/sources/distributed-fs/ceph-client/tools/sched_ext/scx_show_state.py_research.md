# sources/distributed-fs/ceph-client/tools/sched_ext/scx_show_state.py

Purpose: drgn script that prints core sched_ext kernel state from a live kernel or dump.

Important APIs, types, and functions: imports `drgn` and relies on drgn's global `prog` object. Helper functions `read_int()`, `read_atomic()`, `read_static_key()`, and `state_str()` read symbols such as `scx_enable_state_var`, `__scx_enabled`, `__scx_switched_all`, and `scx_enable_state_str`. `err()` exists for fatal reporting but is unused in the current file.

Control flow: after helper definitions, the script reads `scx_root` and the enable-state atomic. It prints the active ops name when `scx_root` is non-null, followed by enabled/switching/switched state, decoded enable state, aborting flag, bypass depth, rejected count, and enable sequence.

State and persistence: the script has no persistent state; it reads kernel globals at one instant. Atomic counters are read through their internal `counter` fields, and static keys through `key.enabled.counter`.

Dependencies and integration points: requires drgn, matching kernel debug symbols, and sched_ext symbols. It integrates with sched_ext debugging by exposing kernel-private state without requiring a purpose-built kernel interface.

Risks: the script is fragile to kernel symbol or type layout changes. It assumes `prog` contains named globals and that `scx_enable_state_str[state]` is valid. It does not catch missing-symbol exceptions or validate state bounds.

Test signals: running under drgn on a kernel with sched_ext should print all fields. A disabled system should show empty `ops`; an attached scheduler should show its `ops.name`.
