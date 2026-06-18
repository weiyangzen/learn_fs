# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/mc5.c

## Purpose

`mc5.c` initializes and handles interrupts for the Chelsio T3 MC5 TCAM block used by the TCP offload engine for connection/filter/server/routing lookup state. It detects TCAM part type and size, programs TCAM command registers for supported IDT parts, clears and masks TCAM arrays, partitions TCAM regions, enables parity/MBus mode, and escalates fatal MC5 parity errors to adapter reset.

## Important APIs, types, and functions

- TCAM command helpers: `mc5_cmd_write()`, `dbgi_wr_data3()`, and `mc5_write()` issue DBGI-mode TCAM commands and wait for completion through MC5 response status.
- Array initialization: `init_mask_data_array()` clears data array entries, initializes mask array entries, and applies special masks at the server/routing region boundary.
- Part-specific setup: `init_idt52100()` configures IDT 75P52100 latency, command opcodes, DBGI mode, LAR, SSRs, GMRs, SCR, and arrays. `init_idt43102()` configures IDT 75N43102 latency, commands, GMRs, SCR, and arrays.
- Mode switching: `mc5_dbgi_mode_enable()` puts MC5 into DBGI mode for direct TCAM programming; `mc5_dbgi_mode_disable()` restores M-Bus mode with compare/parity settings.
- Public init: `t3_mc5_init()` validates requested server/filter/route counts, resets TCAM, writes routing/filter/server partition registers, enables parity, selects part-specific init, and restores M-Bus mode.
- Interrupt handling: `t3_mc5_intr_handler()` reads MC5 interrupt cause, logs and increments stats for parity/search/region/unknown-command conditions, calls `t3_fatal_err()` on fatal parity classes, and clears causes.
- Preparation: `t3_mc5_prep()` reads `A_MC5_DB_CONFIG`, derives part type and TCAM size, adjusts for 144-bit mode, and stores adapter/mode/type/size in `struct mc5`.

## Control flow

`t3_mc5_prep()` runs during adapter preparation to populate static MC5 metadata from hardware registers. Later, `t3_mc5_init()` is called once protocol/offload sizing is known. It rejects unsupported route counts and overcommitted TCAM partition requests, resets the TCAM and waits for `F_TMRDY`, writes region boundary registers from the top of TCAM downward, primes DBGI address high registers to zero, enters DBGI mode, invokes the setup routine matching `mc5->part_type`, then exits DBGI mode. The part setup routines program different IDT command encodings and global mask registers but share the array clearing/masking helper.

During runtime, MC5 interrupts are delivered to `t3_mc5_intr_handler()`. Nonfatal counters are accumulated in `mc5->stats`; fatal parity causes trigger `t3_fatal_err()` on the adapter, which leads to traffic suspension and reset handling in `cxgb3_main.c`.

## State and persistence behavior

Software state lives in `struct mc5` fields supplied by `common.h`: adapter pointer, mode, part type, TCAM size, parity-enabled flag, and stats counters. Hardware state includes TCAM command registers, mask/data arrays, GMR/SCR/LAR/SSR registers, region boundary registers, parity and M-Bus configuration, and interrupt cause bits. All state is volatile hardware/driver runtime state; no disk persistence is involved.

## Dependencies and integration points

`mc5.c` includes `common.h` for adapter/MC5 types and hardware helper functions, and `regs.h` for MC5 register offsets/bitfields. It integrates with adapter initialization in lower-level common code and with fatal error handling in `cxgb3_main.c` via `t3_fatal_err()`. It also supports user-visible filter/server sizing controlled by `cxgb3_main.c` sysfs attributes before full initialization.

## Risks and edge cases

- Only part types `IDT75P52100` and `IDT75N43102` are supported; unknown TCAM types cause `-EINVAL`.
- `init_mask_data_array()` iterates over the entire TCAM in 72-bit units, so initialization time scales with TCAM size and any timeout leaves partially initialized arrays.
- `mc5_write()` returns `-1` rather than a standard errno on timeout; callers convert some but not all failures to `-EIO`.
- Region boundaries are calculated from `tcam_size - nroutes - nfilters - nservers`; wrong counts can overlap server/filter/route/TID spaces and break offload.
- Fatal parity errors immediately escalate to adapter fatal error handling. Tests that inject parity must expect reset side effects.
- `t3_mc5_prep()` indexes `tcam_part_size` by `G_TMPARTSIZE(cfg)` with fixed known encodings; unexpected register values can misrepresent capacity.

## Test signals

Validation should cover both supported TCAM part types, 72-bit and 144-bit modes, boundary validation for `nservers`, `nfilters`, and `nroutes`, TCAM reset timeout, DBGI write timeout, full array initialization, unsupported part handling, interrupt counters for every cause bit, fatal parity escalation, and user sysfs changes to filter/server counts before full init.
