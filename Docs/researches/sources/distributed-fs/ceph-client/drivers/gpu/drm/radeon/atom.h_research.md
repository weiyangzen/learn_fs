# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom.h

## Purpose

`atom.h` is the public interface and constant map for the Radeon AtomBIOS interpreter. It defines BIOS signature offsets, command/data table indices, command-table header offsets, operand and workspace encodings, indirect-I/O opcodes, I/O mode values, the hardware callback structure used by the interpreter, the persistent AtomBIOS context, and the external functions consumed by the rest of the Radeon driver.

## Important APIs, Types, and Definitions

- BIOS and ROM constants: `ATOM_BIOS_MAGIC`, `ATOM_ATI_MAGIC_PTR`, `ATOM_ATI_MAGIC`, `ATOM_ROM_TABLE_PTR`, `ATOM_ROM_MAGIC`, `ATOM_ROM_MAGIC_PTR`, and command/data pointer offsets define the fixed positions used by `atom_parse` to validate and locate AtomBIOS tables.
- Command table indices: `ATOM_CMD_INIT`, `ATOM_CMD_SETSCLK`, `ATOM_CMD_SETMCLK`, `ATOM_CMD_SETPCLK`, and `ATOM_CMD_SPDFANCNTL` name commonly executed firmware command tables.
- Data table and firmware-info offsets: `ATOM_DATA_FWI_PTR`, `ATOM_DATA_IIO_PTR`, `ATOM_FWI_DEFSCLK_PTR`, `ATOM_FWI_DEFMCLK_PTR`, `ATOM_FWI_MAXSCLK_PTR`, and `ATOM_FWI_MAXMCLK_PTR` define where initialization clocks and indirect-I/O descriptions are read.
- Command-table layout constants: `ATOM_CT_SIZE_PTR`, `ATOM_CT_WS_PTR`, `ATOM_CT_PS_PTR`, `ATOM_CT_PS_MASK`, and `ATOM_CT_CODE_PTR` describe per-command table metadata used before opcode execution.
- Opcode/encoding constants: `ATOM_OP_CNT`, `ATOM_OP_EOT`, `ATOM_CASE_MAGIC`, `ATOM_CASE_END`, `ATOM_ARG_*`, `ATOM_SRC_*`, `ATOM_WS_*`, `ATOM_IIO_*`, and `ATOM_IO_*` define the bytecode vocabulary interpreted by `atom.c`.
- `struct card_info`: adapter from the AtomBIOS interpreter to the Radeon device. It stores the DRM device and callback pointers for register, I/O register, memory-controller, and PLL reads/writes.
- `struct atom_context`: persistent interpreter state. It owns the callback adapter, mutexes, BIOS pointer, master table offsets, indirect-I/O index, mutable table execution registers/selectors, scratch buffer metadata, and arithmetic/condition state.
- Exported interpreter functions: `atom_parse`, `atom_execute_table`, `atom_execute_table_scratch_unlocked`, `atom_asic_init`, `atom_destroy`, `atom_parse_data_header`, `atom_parse_cmd_header`, and `atom_allocate_fb_scratch`.
- Hardware I2C declarations: `radeon_atom_hw_i2c_xfer` and `radeon_atom_hw_i2c_func` expose AtomBIOS-backed I2C operations to adapter setup code.

## Control Flow and API Contract

Consumers create a `struct card_info` with hardware callbacks, pass it with the BIOS image to `atom_parse`, initialize the returned context locks, optionally allocate firmware scratch with `atom_allocate_fb_scratch`, then execute firmware command tables through `atom_execute_table` or helper paths such as `atom_asic_init`. Other Radeon modules can inspect firmware table metadata through `atom_parse_data_header` and `atom_parse_cmd_header` without manually decoding master tables.

The two execution APIs signal an important locking distinction. `atom_execute_table` is the normal public wrapper that serializes shared scratch usage with `scratch_mutex`. `atom_execute_table_scratch_unlocked` still takes `ctx->mutex` for interpreter state, but assumes the caller already owns or does not need scratch serialization. This supports code paths such as hardware I2C and DisplayPort that need to hold scratch locking around multiple firmware interactions.

The header intentionally includes `atom-types.h`, `atombios.h`, and `ObjectID.h` at the end so users of `atom.h` also see AtomBIOS table structures and object identifiers used with the helper APIs.

## State and Persistence Behavior

`struct atom_context` persists for the Radeon device lifetime. Its immutable-ish fields after parse include `card`, `bios`, `cmd_table`, `data_table`, and the `iio` lookup table. Its mutable fields are part of interpreter execution: `data_block`, `fb_base`, `divmul`, `io_attr`, `reg_block`, `shift`, `cs_equal`, `cs_above`, `io_mode`, and scratch buffer fields. `mutex` protects interpreter state during table execution, while `scratch_mutex` protects the shared scratch region and firmware operations that rely on it.

`struct card_info` persists as the callback bridge. The interpreter assumes all function pointers are valid when bytecode touches that address space; the header does not provide optionality flags or fallback behavior.

## Dependencies and Integration Points

- Depends on Linux mutex and fixed-width type definitions via `<linux/mutex.h>` and `<linux/types.h>`.
- Uses DRM's `struct drm_device` through a forward declaration included from the DRM headers indirectly by consumers.
- Integrates tightly with `atom.c`, `atombios_i2c.c`, DisplayPort helpers, Radeon device initialization, and broader `atombios` table parsing.
- The callback signatures require hardware backends to use 32-bit addresses and values for MMIO, indirect I/O, memory-controller, and PLL spaces.
- The global `atom_debug` symbol can be modified by driver/module code to enable verbose interpreter traces compiled under `ATOM_DEBUG`.

## Risks and Edge Cases

- The ABI is very stateful: callers must initialize both mutexes after `atom_parse`, provide complete callback sets, and respect scratch locking semantics. The header does not enforce these requirements at compile time.
- `struct atom_context` exposes mutable interpreter internals to any including file. Direct external mutation can break execution ordering, condition codes, or register/data base selection.
- Many constants encode firmware bytecode semantics. Changing values or command indices would silently break AtomBIOS compatibility.
- `scratch_size_bytes` and `scratch` are stored here, but ownership and teardown are not self-documenting in the header. This increases risk of leaks or double frees when lifecycle code changes.
- `ATOM_OP_CNT` and `ATOM_OP_EOT` must stay synchronized with the opcode table in `atom.c` and debug names in `atom-names.h`.

## Test Signals

- Build coverage should include all modules that include `atom.h` to catch signature drift in callback prototypes and exported functions.
- Integration tests should verify that `radeon_device` setup initializes `mutex` and `scratch_mutex` before any table execution.
- Locking tests should cover both normal `atom_execute_table` callers and scratch-unlocked callers that manually hold `scratch_mutex`.
- Firmware parsing tests should use the constants in this header to construct minimal valid and invalid AtomBIOS images.
- API compatibility checks should flag changes to `struct card_info`, `struct atom_context`, command/data indices, operand encodings, and opcode counts because these are cross-file contracts with firmware and driver consumers.
