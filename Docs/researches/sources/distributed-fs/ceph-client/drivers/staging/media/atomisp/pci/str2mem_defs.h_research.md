# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/str2mem_defs.h

## Purpose
Defines register ids, command bitfields, and alignment for the AtomISP stream-to-memory hardware block.

## Important APIs, Types, and Functions
Macros define command/status masks such as `_STR2MEM_CRUN_BIT`, `_STR2MEM_CMD_BITS`, `_STR2MEM_COUNT_BITS`, block/packet/byte command encodings, register ids for reset, endian, bit swapping, sync levels, read-post-write sync, dual-byte input, statistics update, and `_STR2MEM_REG_ALIGN`.

## Control Flow
No runtime flow. Hardware access code uses these constants to program or interpret stream-to-memory registers.

## State and Persistence Behavior
The constants encode persistent hardware register ABI.

## Dependencies and Integration Points
No includes. Integrated by low-level AtomISP input or test-stream paths that configure stream-to-memory movement.

## Risks
Typos or bit changes can corrupt command construction. The guard macro name uses `_ST2MEM_DEFS_H`, while the file is `str2mem_defs.h`, so include uniqueness relies on that exact historical spelling.

## Test Signals
Register programming tests should confirm generated commands have expected command/count bits and register ids align to hardware documentation.
