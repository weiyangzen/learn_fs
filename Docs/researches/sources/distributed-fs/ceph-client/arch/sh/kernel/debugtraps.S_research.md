# sources/distributed-fs/ceph-client/arch/sh/kernel/debugtraps.S

Purpose: defines the SH debug trap dispatch table for `trapa` values 0x30 through 0x3f.

Important APIs and control flow: `debug_trap_table` is a 16-entry data table consumed by `entry-common.S` `debug_trap`. Most entries point to `debug_trap_handler`, while 0x3c dispatches to `breakpoint_trap_handler`, 0x3d to `singlestep_trap_handler` or debug fallback, 0x3e to `bug_trap_handler`, and 0x3f to `sh_bios_handler` or debug fallback depending on config.

State, dependencies, and risks: state is static table layout; dependencies are trap handler symbols emitted by traps, kgdb, hw-breakpoint, and optional SH BIOS support. The table position and trap-number arithmetic must stay in sync with entry assembly. Test signals are kgdb breakpoint/single-step, BUG trap reporting, BIOS earlyprintk/debug delegation, and fallback debug trap behavior when optional configs are disabled.
