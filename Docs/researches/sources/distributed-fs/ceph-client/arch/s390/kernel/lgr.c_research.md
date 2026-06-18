# sources/distributed-fs/ceph-client/arch/s390/kernel/lgr.c

Purpose: detects and logs Linux Guest Relocation-relevant machine identity changes using facility and STSI data.

Important APIs and state: `struct lgr_info` stores STFL facility bits, system level, CEC, LPAR, and up to two z/VM nesting levels. `lgr_info_log()` is exported GPL and records changes to s390 debug feature data. Static state includes a page-aligned STSI buffer, last/current snapshots, debug feature handle, and a deferrable timer.

Control flow: `lgr_info_get()` clears the snapshot, stores facility bits, determines STSI level, and fills level-specific fields while converting EBCDIC to ASCII. `lgr_info_log()` uses a trylock, compares current vs previous snapshots, and writes changed records to s390dbf. A timer calls this every 30 minutes after `lgr_init()` records the initial state.

Dependencies and integration: uses `stfle`, `stsi`, EBCDIC conversion, s390 debug feature views, timers, and is called by kdump/kexec paths to log relocation state before reset.

Risks and test signals: STSI failures leave partial zero fields; trylock can skip concurrent logs. Test debugfs/s390dbf output, timer firing, manual calls around guest relocation, VM nesting truncation, and EBCDIC field conversion.
