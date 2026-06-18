# sources/distributed-fs/ceph-client/arch/s390/include/asm/ipl.h

Purpose: This header defines s390 Initial Program Load and re-IPL data structures, dump-type detection, IPL reports, and DIAG 308 restart/load operations.

Important APIs/types/functions: `struct ipl_parameter_block`, IPL length constants, `struct save_area` helpers, `s390_reset_system()`, `ipl_block_get_ascii_vmparm()`, `enum ipl_type`, global `ipl_info`, `setup_ipl()`, `set_os_info_reipl_block()`, `is_ipl_type_dump()`, IPL report component/certificate APIs, `enum diag308_subcode`, `diag308()`, `store_status()`, and `lgr_info_log()` are the exposed surface.

Control flow: Boot code parses the IPL parameter block into `ipl_info`, optionally builds OS-info re-IPL data, and kexec/dump paths build IPL reports by adding loaded components and certificates. Re-IPL/reset uses DIAG 308 subcodes against prepared parameter blocks.

State and persistence: Persistent state includes global `ipl_info`, lowcore IPL pointers, `ipl_report` lists, the IPL parameter block page, and OS-info re-IPL data used by later dump or reboot tools.

Dependencies and integration points: It depends on lowcore, CIO device identifiers, setup/parmarea definitions, UAPI IPL block layouts, kexec buffers, and firmware DIAG 308 semantics.

Risks and test signals: Packed layout and length constants must match firmware. Tests should cover CCW/FCP/NVMe/ECKD/NSS boots, dump IPL detection, kexec_file component reports, certificate handling, DIAG 308 store/set/load paths, and reboot after crash dump.
