<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Kconfig

## Purpose
Defines Kconfig symbols for NVMEM layout parser modules that discover cells from structured data stored inside an NVMEM provider.

## Important APIs, Types, And Functions
`NVMEM_LAYOUTS` is a hidden OF-dependent symbol. Under the layout menu it defines `NVMEM_LAYOUT_SL28_VPD`, `NVMEM_LAYOUT_ONIE_TLV`, and `NVMEM_LAYOUT_U_BOOT_ENV`, selecting CRC helpers and generic network utilities as needed.

## Control Flow
The top-level NVMEM Kconfig sources this file. When layouts are enabled, users can select parser modules; selected symbols control objects in `layouts/Makefile`.

## State And Persistence
No runtime state. It controls compile-time availability and module construction.

## Dependencies And Integration Points
Depends on OF because layouts are discovered from `nvmem-layout` DT nodes. It integrates with CRC8/CRC32 libraries and the U-Boot environment parser.

## Risks
Missing helper selections break module builds; too-broad layout availability could bind to malformed DT descriptions. Symbols must stay aligned with layout driver source files and compatible strings.

## Test Signals
Kconfig allmodconfig coverage, individual module builds, OF-disabled builds where `NVMEM_LAYOUTS` is unavailable, and verification that each selected layout has a matching Makefile object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/layouts/Kconfig -->
