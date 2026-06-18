# sources/distributed-fs/ceph-client/drivers/s390/char/zcore.c

Purpose: zfcp/nvme/eckd dump support module that exposes HSA memory access and re-IPL controls for creating dumps after an s390 dump IPL.

Important APIs/types/functions: defines `memcpy_hsa_iter`, `memcpy_hsa_kernel`, `init_cpu_info`, `release_hsa`, debugfs file ops for `reipl` and `hsa`, `check_sdias`, `zcore_reipl_init`, reboot/panic notifier `zcore_reboot_and_on_panic_handler`, and init `zcore_init`.

Control flow: init runs only for dump IPL without oldmem data, initializes SCLP SDIAS, verifies HSA size, checks the dumped system was 64-bit, copies boot CPU registers from HSA, loads and validates saved IPL parameter block and OS info flags, creates debugfs `zcore/reipl` and `zcore/hsa`, and registers reboot/panic notifiers. HSA copy reads pages through `sclp_sdias_copy` under a mutex and streams into an iterator.

State and persistence: tracks HSA availability, saved IPL block page, debugfs dentries, OS info flags, and a single aligned page buffer protected by mutex. Writing `0` to debugfs `hsa` releases HSA through diag308; reboot/panic also releases it.

Dependencies and integration: depends on SCLP SDIAS, diag308 IPL/release calls, lowcore offsets, save_area register plumbing, debugfs, panic/reboot notifiers, checksum helpers, `memcpy_real`, and dump IPL metadata in `ipl_info`.

Risks: HSA copy is explicitly not reentrant; releasing HSA is irreversible for dump extraction. Corrupted OS info/IPIB data is tolerated in places but bad checksum disables re-IPL block use. Module refuses 32-bit dumped systems for the 64-bit dump tool.

Test signals: dump IPL boot paths for FCP/NVMe/ECKD, debugfs hsa read/write, HSA memory copy through iterator, checksum failure handling, reipl write invoking correct diag308 subcode, and notifier release on panic/reboot.
