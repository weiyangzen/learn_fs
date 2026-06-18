<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/cfi.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/cfi.h

## Purpose
`mtd/cfi.h` defines Common Flash Interface data structures and helpers for probing and controlling NOR flash chips through MTD map drivers and CFI command sets.

## Important APIs, Types, and Functions
It defines interleave helpers (`cfi_interleave*`, `cfi_interleave_supported()`), CFI device/interface constants, query structs (`cfi_ident`, `cfi_extquery`, Intel/AMD/Atmel PRI structs, OTP/block/region programming info), command-set IDs (`P_ID_*`), mode constants, and `struct cfi_private`. Functional APIs include `cfi_build_cmd_addr()`, `cfi_build_cmd()`, `cfi_merge_status()`, `cfi_send_gen_cmd()`, `cfi_read_query()`, `cfi_read_query16()`, `cfi_udelay()`, query-mode helpers, `cfi_read_pri()`, `struct cfi_fixup`, manufacturer IDs, `cfi_fixup()`, `varsize_frob_t`, and `cfi_varsize_frob()`.

## Control Flow and State
Probe code enters CFI query mode, reads query bytes/words through `map_read()`, converts endianness with map swap settings, identifies command sets and geometry, applies fixups, and initializes `struct cfi_private` with chip count, command set setup, manufacturer/device IDs, erase command, chip shift, quirks, and per-chip `flchip` state. Runtime operations build interleaved commands and send generic command sequences to one or more chips.

## State and Persistence Behavior
Runtime CFI state lives in `struct cfi_private` and per-chip `flchip` records. Persistent data is the NOR flash contents and hardware CFI query data. Fixups alter runtime interpretation, not flash contents by themselves.

## Dependencies and Integration Points
It depends on delay/interrupt helpers, MTD flashchip/map APIs, CFI endianness helpers, XIP annotations, and MTD command-set drivers for Intel/AMD/Jedec-style chips.

## Risks
Interleave and bank-width errors send commands to wrong lanes. Endianness conversion is hardware-dependent. Flexible query structs contain non-host-ordered fields and variable tails. Missing `CONFIG_MTD_CFI_Ix` support triggers a BUG path. Fixups can mask hardware quirks but also misconfigure erase/program behavior.

## Test Signals
Probe NOR devices with x8/x16/x32 interleaves, big/little/host endian maps, Intel and AMD command sets, XIP query-mode paths, erase/write/read tests, CFI fixup coverage, and unsupported interleave builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/cfi.h -->
