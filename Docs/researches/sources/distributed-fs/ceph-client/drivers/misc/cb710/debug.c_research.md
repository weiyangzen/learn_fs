# sources/distributed-fs/ceph-client/drivers/misc/cb710/debug.c

Purpose: provides optional CB710 register dump support for developer debugging.

Important APIs, types, and functions: `cb710_dump_regs(struct cb710_chip *chip, unsigned select)` is exported when this file is built. Macro templates generate 8-bit, 16-bit, and 32-bit register readers and dumpers. The `allow[]` bitmap controls which register offsets are safe to read; `prefix[]` labels 16-byte blocks as MMC, MS, or SM related.

Control flow: `cb710_dump_regs()` normalizes the requested block/access masks, then performs selected reads at requested widths and emits formatted `dev_dbg()` lines. The generated readers skip disallowed offsets and the dumpers print `x` placeholders for skipped registers.

State and persistence: no persistent state is kept; each dump snapshots MMIO registers into stack arrays before logging.

Dependencies and integration points: depends on `linux/cb710.h`, MMIO accessors, and `CONFIG_CB710_DEBUG` object inclusion. It is intended for use by CB710 child/core debug paths.

Risks: reading device registers can have side effects, so the `allow[]` mask is a safety boundary. Incorrect select masks could produce excessive logs. Formatting uses fixed-size stack buffers sized for current dump layouts.

Test signals: debug build should link `cb710_dump_regs()`. Runtime signal is readable, aligned register dumps under `dynamic_debug`/`dev_dbg()` without touching disallowed registers.
