# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/masklog.c

## Purpose
`masklog.c` implements runtime-controllable OCFS2/O2CB logging masks. It stores allow/deny bitsets, formats log messages through `printk`, and exposes each mask bit under `/sys/fs/o2cb/logmask`.

## Important APIs, types, and functions
Global exported state is `mlog_and_bits` and `mlog_not_bits`. Public functions are `__mlog_printk`, `mlog_sys_init`, and `mlog_sys_shutdown`. Internal helpers parse/format mask state (`mlog_mask_show`, `mlog_mask_store`) and sysfs attributes (`mlog_show`, `mlog_store`).

## Control flow
Initialization populates the default attribute list from `mlog_attrs`, attaches a `logmask` kset under the supplied O2CB kset, and registers sysfs files. Reads return `allow`, `deny`, or `off`; writes accept those strings to update the global bitsets. The `mlog` macro in the header filters constant masks before calling `__mlog_printk`, which chooses severity and prefixes process, pid, CPU, function, and line.

## State and persistence behavior
All log masks are runtime-only global bitsets. Defaults allow errors and notices. Changes through sysfs do not persist across module unload/reboot unless userspace reapplies them.

## Dependencies and integration points
It depends on sysfs/kset APIs, kernel printk formatting, task identity, and `masklog.h` macros. Nearly all OCFS2 cluster code uses `mlog` for diagnostics, and `sys.c` owns the parent O2CB sysfs kset.

## Risks and test signals
Risks include unsynchronized global bit updates, mask table mismatch when adding bits, noisy console output if broad masks are enabled, and string parsing accepting prefixes. Test signals include sysfs allow/deny/off writes for every declared mask, debug-mask builds, default error/notice logging, and module shutdown unregistering the kset cleanly.
