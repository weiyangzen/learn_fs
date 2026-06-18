<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/ifs.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/ifs.h

## Purpose
Shared IFS documentation and internal ABI. It defines the hardware MSR layouts, test types, runtime data structures, and cross-file function declarations.

## Important APIs, Types, And Data
The header documents firmware file layout and sysfs workflow. It defines MSR addresses for SAF, SBAF, Array BIST, status, copy, and control registers. Bitfield unions include `ifs_scan_hashes_status`, `ifs_chunks_auth_status`, `ifs_scan`, `ifs_status`, `ifs_array`, `ifs_sbaf`, and `ifs_sbaf_status`. `struct ifs_data` stores loaded firmware state and last test result. `struct ifs_device` combines capabilities, MSR selectors, runtime data, and miscdevice.

## Control Flow And Integration
Inline helpers recover `ifs_data`, `ifs_test_caps`, and `ifs_test_msrs` from a miscdevice-backed sysfs device. `load.c` uses the firmware/MSR definitions, `runtest.c` uses activation/status unions, `sysfs.c` exposes `ifs_load_firmware()` and `do_core_test()`, and `core.c` fills generation data.

## State And Persistence
The header owns no storage except declarations. It defines persistent in-memory status fields surfaced through sysfs: loaded batch, image version, pass/fail/untested status, hardware details, chunk count, and SBAF max bundle.

## Dependencies And Integration Points
Depends on Linux device and miscdevice APIs plus x86 MSR constants. Firmware path and sysfs names are part of the user-facing contract.

## Risks And Test Signals
Risks include C bitfield layout assumptions matching hardware MSR encoding, generation-specific field width changes, and user ABI drift. Test with compiler builds, real hardware MSR decode, firmware loads for gen0/gen2, and sysfs documentation consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/ifs.h -->
