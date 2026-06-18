<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/dump_psb.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/dump_psb.c

## Purpose
Legacy AMD PowerNow! PSB scanner/decoder. It mmaps the BIOS memory region 0xc0000-0xfffff from `/dev/mem`, searches for `AMDK7PNOW!`, decodes PSB/PST packed structures, and prints frequencies/voltages from FID/VID tables.

## Important APIs, Types, And Functions
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## Control Flow
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## State And Persistence
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## Dependencies And Integration Points
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## Risks And Edge Cases
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.

## Test Signals
Control flow parses `-h`, `-r`, and `-n`, maps memory, scans every 16 bytes, and decodes matching PST records filtered by optional CPUID. State is read-only physical memory mapping. Dependencies are `/dev/mem`, root, x86 BIOS layout, packed struct assumptions, and getopt_long. Risks include no `MAP_FAILED` check before scanning, direct indexing into FID/VID tables without bounds checks, obsolete firmware formats, and low-memory access blocked by modern kernels. Test signals are help, permission failure, sample PSB blob decoding, invalid `-n/-r`, and running under kernels with strict devmem.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/dump_psb.c -->
