## sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_util.c

Purpose: provides geometry-aware helpers shared by CFI command-set and probe drivers. It builds command words and command addresses for arbitrary bank width/interleave/device type combinations, enters and exits CFI query mode, reads primary/alternate extended query tables, applies fixup tables, and iterates variable erase regions for lock/erase-style operations.

Important APIs, types, and functions: exported helpers include `cfi_udelay()`, `cfi_build_cmd_addr()`, `cfi_build_cmd()`, `cfi_merge_status()`, `cfi_send_gen_cmd()`, `cfi_qry_present()`, `cfi_qry_mode_on()`, `cfi_qry_mode_off()`, `cfi_read_pri()`, `cfi_fixup()`, and `cfi_varsize_frob()`.

Control flow: command helpers compute bus-scaled offsets and replicate command/status patterns across interleaved chips. Query-mode entry tries multiple known vendor command sequences, including Intel, ST M29DW, old SST, and SST39VF640xB variants, then verifies `QRY`. `cfi_read_pri()` switches into query mode, copies a requested extended table, and switches back to read mode. `cfi_varsize_frob()` validates erase-region alignment, then calls a caller-supplied block callback across chips and regions.

State and persistence: this file owns no long-lived state. It mutates flash mode transiently and uses `cfi_private` geometry and IDs to build commands and apply special reset behavior for ST M29W128G-like parts.

Dependencies and integration points: consumed by CFI probes, Intel/AMD/ST command sets, and FWH lock fixups. It depends on `map_info` accessors, CFI endian conversion macros, XIP helpers, and MTD erase-region metadata.

Risks: small geometry mistakes broadcast wrong commands to every interleaved chip. Query entry intentionally sends several vendor-specific sequences, so false positives or side effects on odd parts are possible. `cfi_varsize_frob()` assumes the request is non-empty and begins inside a valid region.

Test signals: command address/word correctness for x8/x16/x32 and interleave 1/2/4/8, successful query-mode entry for Intel/ST/SST variants, clean query-mode exit, fixup execution by mfr/id, and range operations over mixed erase-region maps without off-by-one region advances.
