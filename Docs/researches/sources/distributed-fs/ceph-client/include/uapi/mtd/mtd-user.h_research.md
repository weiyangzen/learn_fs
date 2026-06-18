<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-user.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-user.h

## Purpose
Provides the libc-facing compatibility include for MTD userspace by including `mtd-abi.h` and defining the historical typedef aliases such as `mtd_info_t` and `erase_info_t`.

## Important APIs, Types, and Functions
Read coverage: 33 lines and 1242 bytes. Visible type families include typedef mtd_info_t, typedef erase_info_t, typedef region_info_t, typedef nand_oobinfo_t, typedef nand_ecclayout_t. Important macros/constants include __MTD_USER_H__. Explicit ioctl-style command names include none.

## Control Flow
No control flow exists. Userspace includes this wrapper and receives the canonical MTD ABI definitions plus old typedef names expected by existing tools.

## State and Persistence Behavior
No state is defined here; all persistent flash state and ioctl payloads are inherited from `mtd-abi.h`.

## Dependencies and Integration Points
It directly depends on `mtd-abi.h` and integrates with mtd-utils and older applications that still compile against typedef names rather than struct tags. Direct includes are #include <mtd/mtd-abi.h>.

## Risks and Edge Cases
The main risk is accidental removal or renaming of compatibility typedefs, which would break source compatibility even though the binary ABI lives in `mtd-abi.h`.

## Test Signals
Compile representative old mtd-utils sources against the header, verify typedef names resolve, and run the broader `mtd-abi.h` ioctl tests for behavioral coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/mtd-user.h -->
