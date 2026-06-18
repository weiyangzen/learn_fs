# sources/distributed-fs/ceph-client/arch/s390/kernel/nospec-branch.c

Purpose: controls s390 Spectre v2 branch prediction mitigations, including limited branch prediction (`nobp`), expoline enable/disable, automatic detection, status reporting, and runtime reversion of expoline call/return sites.

Important APIs and state: global `nobp` and, with `CONFIG_EXPOLINE`, `nospec_disable` represent selected mitigations. Early parameters include `nobp=`, `nospec`, `nospectre_v2`, and `spectre_v2=on/off/auto`. Runtime hooks include `nospec_auto_detect()`, `nospec_init_branches()`, and `nospec_revert()`.

Control flow: early params set policy based on user input, compiler expoline support, facility 82/156, and global CPU mitigation mode. Reporting prints active etokens, execute trampolines, or limited branch prediction. Reversion scans offset tables, recognizes `brcl`/`brasl` calls into expoline thunks, verifies thunk `exrl` and branch-register layout, then patches the call site to direct branch/basr plus NOP.

Dependencies and integration: used by module finalization for `.s390_indirect*` and `.s390_return*` sections, by boot init for built-in nospec sections, and by sysfs vulnerability reporting.

Risks and test signals: patch recognition must be exact to avoid corrupting text. Test boot params, facility 156 machines, expoline compiler vs non-expoline builds, module loading with nospec sections, and `/sys/devices/system/cpu/vulnerabilities/spectre_v2`.
