## sources/distributed-fs/ceph-client/arch/s390/kernel/sthyi.c

Purpose: Implements native or emulated Store Hypervisor Information (`STHYI`) support and the `s390_sthyi` syscall. It returns a one-page machine/partition capacity report for CP and IFL processors, using firmware instructions directly when facility 74 exists or synthesizing the data from STSI, DIAG 204, and DIAG 224 otherwise.

Important APIs and functions: `sthyi_fill()` is exported for in-kernel users; `SYSCALL_DEFINE4(s390_sthyi)` exposes the syscall. Internal builders include `fill_hdr()`, `fill_stsi_*()`, `diag204_get_data()`, `fill_diag()`, `lpar_cpu_inf()`, `fill_diag_mac()`, `sthyi()`, and cache helpers.

Control flow: `sthyi_fill()` serializes callers with `sthyi_mutex`, initializes a page cache, refreshes it when older than one second, and copies cached content to the caller. Native mode zeroes the page and issues the STHYI instruction. Emulated mode reads DIAG 204 extended data, allocates a DIAG 224 CPU-type page, fills header, machine, and partition sections, sets validity/unavailable flags, scales caps, and caches the result. The syscall validates function code and flags, copies the page and optional return code to user space.

State and persistence: The file owns `sthyi_cache`, valid for `HZ` jiffies, and protects it with `sthyi_mutex`. Output validity is represented by bit fields in the generated STHYI sections rather than by failing every partial data source.

Dependencies and integration: Uses SCLP CPC names, STSI sysinfo blocks, DIAG 204/224 hypervisor data, EBCDIC constants for CP/IFL, facility probing, syscall/user-copy helpers, and exported kernel API consumers.

Risks and test signals: Risks include stale cached topology/capacity data, DIAG 204 busy handling, integer scaling of caps/weights, and partial validity-bit semantics. Test signals include syscall return values for unsupported function codes, native versus emulated hosts, cache behavior under DIAG busy, z/VM/LPAR partition data correctness, and user-copy fault handling.
