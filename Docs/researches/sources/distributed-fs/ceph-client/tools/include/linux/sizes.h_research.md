<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sizes.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/sizes.h

## Purpose
`sizes.h` defines common byte-size constants from 1 byte through 4 GiB.

## APIs And Flow
It includes `linux/const.h` and exports `SZ_1` through `SZ_512`, `SZ_1K` through `SZ_512K`, `SZ_1M` through `SZ_512M`, `SZ_1G`, `SZ_2G`, and `SZ_4G`. There is no executable flow.

## State, Dependencies, Risks, Tests
There is no state. The dependency is `_AC` for the 64-bit `SZ_4G` constant. Integration points are memory maps, buffer sizing, and page arithmetic. Risks include signed integer overflow if large constants are used in signed 32-bit expressions and assumptions that `SZ_4G` fits in `unsigned long` on every host. Tests should compile constants in 32-bit and 64-bit builds and use static assertions for expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sizes.h -->
