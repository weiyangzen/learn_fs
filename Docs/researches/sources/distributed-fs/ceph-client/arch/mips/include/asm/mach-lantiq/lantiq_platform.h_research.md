<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq_platform.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq_platform.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq_platform.h` declares board, firmware, memory, and platform-data contracts for `mach-lantiq`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 1 macros including `_LANTIQ_PLATFORM_H__`; 2 structs: `ltq_eth_data`, `sockaddr`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `ltq_eth_data`, `sockaddr` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are `linux/socket.h`. Major macro families are `_LANTIQ (1)`. Typed contracts include `ltq_eth_data`, `sockaddr`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is machine setup code, boot parameter parsing, platform device registration, board identification, and firmware handoff.

## Risks
layout drift between firmware, board files, and consumers can cause wrong memory maps, device registration, or machine identity; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-lantiq/lantiq_platform.h -->
