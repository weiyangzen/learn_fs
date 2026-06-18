# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_legacy.c

Purpose: this file preserves the raw NAND legacy-controller path used when a controller does not implement `exec_op`. It supplies default byte/buffer I/O callbacks, legacy command sequencing for small and large page devices, ready/busy polling, and default hook validation.

Important APIs, types, and functions: `nand_legacy_set_defaults()`, `nand_legacy_adjust_cmdfunc()`, and `nand_legacy_check_hooks()` are the exported setup helpers for legacy drivers. `nand_wait_ready()` and the internal `nand_wait()` implement ready/status polling. `nand_command()` and `nand_command_lp()` translate generic NAND commands into CLE/ALE cycles through `chip->legacy.cmd_ctrl`. The default 8-bit and 16-bit read/write callbacks use `readb/readw`, `iowrite*_rep`, and `ioread*_rep`.

Control flow: controller setup calls the defaults unless `nand_has_exec_op()` is true. Command flow latches commands, emits column and row address cycles, handles bus-width column adjustment, and then either returns immediately for commands with explicit busy handling or waits using `dev_ready`, status reads, fixed command delays, and tWB/tCCS delays. Large-page handling emulates OOB reads as `READ0` with an OOB column and issues `READSTART` or `RNDOUTSTART` where required.

State and persistence: the file mutates only `struct nand_chip` callback pointers and options-derived behavior. Runtime state is hardware line state behind the controller callbacks plus the MTD `oops_panic_write` flag, which switches waits to polling loops that touch the watchdog instead of scheduling.

Dependencies and integration points: this code depends on `internals.h`, legacy `struct nand_chip.legacy` hooks, MTD geometry, jiffies/delay helpers, soft-lockup watchdog handling, and raw NAND operation helpers such as `nand_status_op()` and `nand_read_data_op()`.

Risks: legacy callbacks require `cmd_ctrl` and correct IO addresses; a missing hook fails attach. Timing fallback paths assume `chip_delay` and `dev_ready` reflect board behavior. 16-bit byte writes intentionally zero/ignore upper bus bits, which can expose controller-specific assumptions. Command/address sequences are compatibility-sensitive because many old board drivers depend on this path.

Test signals: exercise a legacy-only controller through ID read, reset, page/OOB read, page program, erase, random column read/write, 8-bit and 16-bit bus modes, no-R/B polling fallback, panic/oops write waits, and large-page command adjustment.
