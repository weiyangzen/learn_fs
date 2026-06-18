# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/segment_regs.c

## Purpose
This file exposes Book3S 32-bit segment register contents through debugfs. It decodes the 16 segment registers into user/kernel virtual segments, keys, device mappings, no-execute state, and VSID values.

## Important APIs, Types, And Functions
Key functions are `seg_show()`, `sr_show()`, and `sr_init()`. `DEFINE_SHOW_ATTRIBUTE(sr)` provides seq-file operations.

## Control Flow
`sr_init()` registers `arch_debugfs_dir/segment_registers`. Reading the file calls `sr_show()`, which prints user segments up to aligned `TASK_SIZE`, then kernel segments through register 15. `seg_show()` reads each segment register with `mfsr(i << 28)` and decodes key bits, device-vs-VSID format, and no-execute bit.

## State And Persistence
No persistent runtime state is owned. Output reflects live segment register values at read time.

## Dependencies And Integration Points
It depends on debugfs, seq_file availability through included headers, `TASK_SIZE`, `ALIGN`, `SZ_256M`, `mfsr()`, and `arch_debugfs_dir`. The ptdump Makefile builds it for Book3S32 ptdump debugfs.

## Risks And Test Signals
Risks include incorrect user/kernel split for unusual `TASK_SIZE`, misdecoding device segment fields, and reading unsupported segment registers on the wrong MMU family. Test signals include debugfs reads on Book3S32 and comparison with expected segment setup during boot.
