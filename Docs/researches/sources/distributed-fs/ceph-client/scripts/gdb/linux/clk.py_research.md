# sources/distributed-fs/ceph-client/scripts/gdb/linux/clk.py

Purpose: Adds GDB commands/functions for inspecting Linux common clock framework state.

Important APIs/classes: `clk_core_for_each_child()` walks clock child hlists. `LxClkSummary` command prints a tree similar to debugfs `clk_summary`. `LxClkCoreLookup` function returns a `struct clk_core` by name.

Control flow: `lx-clk-summary` checks for `clk_root_list`, prints headers, then recursively emits root and orphan clock subtrees with enable/prepare/protect counts, rate, and `(c)` marker for cached rates. `$lx_clk_core_lookup(name)` recursively searches root and orphan lists.

State/persistence: Registers one GDB command and one GDB convenience function at import. No persistent cache beyond `CachedType`.

Dependencies/integration: GDB Python API, `linux.utils`, `linux.lists`, generated `constants.LX_CLK_GET_RATE_NOCACHE`, and kernel `struct clk_core` lists.

Risks: Requires CONFIG_COMMON_CLK-era symbols and struct fields. Output rate may be cached/stale by design. Recursive traversal assumes valid list topology.

Test signals: Kernels with registered clocks, no clocks, orphan clocks, cached-rate flags, and lookup of existing/missing clock names.
