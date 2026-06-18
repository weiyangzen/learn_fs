<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/Kconfig -->
# sources/distributed-fs/ceph-client/block/partitions/Kconfig

## Purpose
`partitions/Kconfig` declares build-time configuration options for partition table parsers. It lets kernels include common MSDOS/GPT support by default and optional foreign/legacy formats when `PARTITION_ADVANCED` or architecture defaults request them.

## Important APIs, Types, and Functions
This is Kconfig data, not C code. Key symbols include `PARTITION_ADVANCED`, `ACORN_PARTITION` and its subformats, `AIX_PARTITION`, `OSF_PARTITION`, `AMIGA_PARTITION`, `ATARI_PARTITION`, `IBM_PARTITION`, `MAC_PARTITION`, `MSDOS_PARTITION`, BSD/Minix/Solaris/Unixware subpartition options, `LDM_PARTITION`, `LDM_DEBUG`, `SGI_PARTITION`, `ULTRIX_PARTITION`, `SUN_PARTITION`, `KARMA_PARTITION`, `EFI_PARTITION`, `SYSV68_PARTITION`, `CMDLINE_PARTITION`, and `OF_PARTITION`.

## Control Flow
The file controls which parser objects appear in `partitions/Makefile` and therefore which entries are compiled into the `check_part[]` probe order in `core.c`. Several options default to `y` on matching architectures, while `EFI_PARTITION` and `MSDOS_PARTITION` default to `y` generally. `EFI_PARTITION` selects `CRC32`; `OF_PARTITION` depends on `OF`; MSDOS subpartition features depend on `MSDOS_PARTITION`.

## State and Persistence Behavior
Kconfig choices persist in the kernel build configuration, not at runtime. They determine the kernel’s ability to recognize partition formats and can affect bootability or device enumeration on systems using uncommon labels.

## Dependencies and Integration Points
This file integrates Kconfig with parser C files and the top-level block configuration. It must stay consistent with Makefile object names and `core.c` conditional parser declarations. Help text references relevant admin documentation for LDM and command-line partitioning.

## Risks and Edge Cases
Disabling default parsers can make disks invisible at boot. Enabling too many legacy probes can increase false-positive risk, which is mitigated by parser order in `core.c`. Subpartition options require parent parser support. Architecture defaults need care when architectures are removed or renamed.

## Test Signals
Build matrices with `PARTITION_ADVANCED` on/off, architecture default configs, `EFI_PARTITION=n`, `MSDOS_PARTITION=n`, and dependency checks via `make olddefconfig` or Kconfig warnings are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/Kconfig -->
