# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_dump.h

## Purpose
Provides the static register-dump metadata used by `bnx2x_ethtool.c` for ethtool register dumps and preset dumps. It describes supported chip masks, path markers, dump headers, regular register ranges, idle-check register ranges, CAM/windowed register descriptors, paged register selectors, and per-chip/per-preset register counts.

## Important APIs, Types, and Functions
The key exported-to-translation-unit definitions are `struct dump_header`, `struct reg_addr`, and `struct wreg_addr`. `BNX2X_DUMP_VERSION`, `DUMP_CHIP_E1`, `DUMP_CHIP_E1H`, `DUMP_CHIP_E2`, `DUMP_CHIP_E3A0`, `DUMP_CHIP_E3B0`, `DUMP_PATH_0`, `DUMP_PATH_1`, `NUM_PRESETS`, and `NUM_CHIPS` define the dump ABI consumed by ethtool users.

The large static tables are `reg_addrs`, `idle_reg_addrs`, chip-specific `wreg_addr_*` descriptors, `page_vals_e2/e3`, `page_write_regs_e2/e3`, `page_read_regs_e2/e3`, and `dump_num_registers`. `REGS_COUNT` and `IDLE_REGS_COUNT` wrap table sizes for the reader implementation.

## Control Flow
This header has no executable control flow except static initializers. Its data controls ethtool dump iteration in `bnx2x_ethtool.c`: chip/preset masks filter entries, `size` controls how many DWORDs are read from each base address, paged arrays define write-selector/read-window sequences for E2/E3, and `dump_num_registers[chip][preset]` is used to pre-size user buffers and advance output pointers.

## State and Persistence Behavior
All state is immutable static metadata compiled into the driver. Runtime dump state is produced by `bnx2x_ethtool.c` into user buffers and is not persisted here. The dump header written to userspace includes the preset, dump version, chip type, and path metadata so external decoders can interpret the raw register stream.

## Dependencies and Integration Points
`bnx2x_ethtool.c` includes this header directly and uses the tables in `get_regs_len`, `get_regs`, `set_dump`, `get_dump_flag`, and `get_dump_data`. The register addresses and masks must match the `bnx2x` hardware register map, the `REG_RD`/`REG_WR` access model, and any external diagnostic tooling that decodes `BNX2X_DUMP_VERSION` streams.

## Risks
The highest risk is table drift: a wrong register address, size, chip mask, preset mask, or count can cause invalid GRC reads, truncated dumps, oversized userspace reads, or false parity/GRC timeout reports. The implementation intentionally disables parity attentions around dumps because some reads can touch never-written registers; adding entries without understanding that behavior can create noisy or unsafe diagnostics. The `dump_num_registers` matrix must remain synchronized with the actual table expansion for every chip and preset.

## Test Signals
Validation signals include `ethtool -d` on E1/E1H/E2/E3A0/E3B0 hardware, preset-specific dump requests through `ETHTOOL_GET_DUMP_DATA`, matching output lengths against `get_regs_len`/`get_dump_flag`, absence of unhandled parity attentions after dump, and comparison of dump streams against known-good decoder expectations.
