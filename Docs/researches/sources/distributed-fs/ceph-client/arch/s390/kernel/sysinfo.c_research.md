## sources/distributed-fs/ceph-client/arch/s390/kernel/sysinfo.c

Purpose: Exposes s390 STSI machine, CPU, LPAR, topology, and VM information through `/proc/sysinfo`, `/proc/service_levels`, debugfs raw STSI files, and delay-loop calibration.

Important APIs and functions: Proc renderers `stsi_1_1_1()`, `stsi_15_1_x()`, `stsi_1_2_2()`, `stsi_2_2_2()`, `stsi_3_2_2()`, `sysinfo_show()`, service-level registration APIs `register_service_level()` and `unregister_service_level()`, `s390_adjust_jiffies()`, `calibrate_delay()`, and debugfs `STSI_FILE()` wrappers.

Control flow: `/proc/sysinfo` allocates one page, queries maximum STSI level, and conditionally emits machine, topology, CPU, LPAR, and VM blocks, translating EBCDIC/UTF-8 names as needed. Service levels are protected by an rwsem-backed list and, on z/VM, include `QUERY CPLEVEL` output. Delay calibration reads CPU capability with STSI and performs FPU conversion for the special capability encoding. Debugfs allocates a page on open, fills it with one STSI block, and exposes raw bytes.

State and persistence: Owns `topology_max_mnest`, `service_level_list`, `service_level_sem`, the optional VM service-level item, and debugfs/proc registrations. Runtime output reflects firmware/hypervisor STSI state.

Dependencies and integration: Uses STSI instruction wrappers, EBCDIC conversion, topology storage, CPCMD for z/VM, kernel FPU helpers, procfs/debugfs, and exported service-level APIs for other s390 components.

Risks and test signals: Risks include encoding conversion errors, capability arithmetic, raw STSI access permissions, and list lifetime around service-level unregister. Test signals include `/proc/sysinfo`, `/proc/service_levels`, debugfs `stsi/*`, z/VM service output, topology fields, and BogoMIPS recalculation after capacity changes.
