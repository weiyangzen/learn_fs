# sources/distributed-fs/ceph-client/include/linux/reset/bcm63xx_pmb.h

Purpose: this header provides inline Broadcom BCM63xx Processor Monitor Bus helpers shared by SMP and reset code.

Important APIs/types/functions: register offsets and bits cover `PMB_CTRL`, start/timeout/slave-error/busy/read/write fields, write/read data registers, timeout register, and bus ID shift. Inline APIs are `__bpcm_do_op()`, `bpcm_rd()`, and `bpcm_wr()`.

Control flow: `bpcm_wr()` writes data to `PMB_WR_DATA`, then calls `__bpcm_do_op()` with write opcode. `bpcm_rd()` issues a read operation and then reads `PMB_RD_DATA`. `__bpcm_do_op()` builds a command with start bit, address, offset shifted by word, and operation type, writes it to the master control register, then polls for completion up to 1000 microsecond delays, returning `0`, `-EIO`, or `-ETIMEDOUT`.

State and persistence: no kernel state is stored. The PMB master registers and target BPCM registers hold hardware state.

Dependencies and integration points: uses MMIO `readl`/`writel`, microsecond delay, error codes, and reset/SMP Broadcom platform code.

Risks: offset is divided by four, so callers must pass byte offsets. `bpcm_rd()` reads data even if `__bpcm_do_op()` failed, so callers must check return before trusting `*val`. Polling delays can be problematic in atomic or timing-sensitive contexts. Test signals include successful read/write of known BPCM registers, timeout/error paths, and reset-controller behavior on BCM63xx hardware.
