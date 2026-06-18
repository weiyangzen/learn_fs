# sources/distributed-fs/ceph-client/arch/s390/kernel/nospec-sysfs.c

Purpose: provides s390 CPU vulnerability sysfs strings for Spectre v1 and v2.

Important APIs: `cpu_show_spectre_v1()` always reports `__user` pointer sanitization. `cpu_show_spectre_v2()` reports etokens when facility 156 is present, execute trampolines when expolines are active, limited branch prediction when `nobp` is active, otherwise vulnerable.

Control flow and state: stateless display functions read mitigation state through `test_facility(156)`, `nospec_uses_trampoline()`, and `nobp_enabled()`.

Dependencies and integration: called by generic CPU vulnerability sysfs code and depends on mitigation policy set in `nospec-branch.c`.

Risks and test signals: reporting must track actual mitigation policy. Test combinations of boot parameters, CPU facilities, expoline config, and expected contents of `/sys/devices/system/cpu/vulnerabilities/spectre_v1` and `spectre_v2`.
