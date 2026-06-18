# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom.c

## Purpose

`atom.c` implements the Radeon driver's AtomBIOS command-table interpreter. It validates and indexes an AtomBIOS image, executes command bytecode against GPU register, PLL, memory-controller, parameter-space, workspace, and firmware scratch targets, and exposes helper routines for command/data table header parsing and firmware scratch allocation. In normal driver flow, this file is the low-level execution engine behind ASIC init, clock/power/display setup tables, hardware I2C, DisplayPort AUX, and other Radeon AtomBIOS consumers.

## Important APIs, Types, and Functions

- `atom_exec_context`: per-command-table execution frame. It carries the global `struct atom_context`, parameter-space (`ps`) and workspace (`ws`) arrays, parameter-space shift derived from the table header, bytecode start offset, jump-loop tracking fields, and an `abort` flag.
- `atom_parse(struct card_info *card, void *bios)`: allocates an `atom_context`, verifies BIOS/ATI/ATOM signatures, records master command/data table offsets, indexes indirect I/O tables, and logs the AtomBIOS name string.
- `atom_execute_table(struct atom_context *ctx, int index, uint32_t *params, int params_size)`: public serialized table execution API. It locks `scratch_mutex`, then calls `atom_execute_table_scratch_unlocked`.
- `atom_execute_table_scratch_unlocked(...)`: resets mutable interpreter globals (`data_block`, `reg_block`, `fb_base`, `io_mode`, `divmul`) under `ctx->mutex` and executes a command table. It leaves scratch serialization to the caller.
- `atom_execute_table_locked(...)`: core bytecode loop. It decodes a command-table header, allocates table workspace, fetches opcodes, dispatches through `opcode_table`, stops on `ATOM_OP_EOT` or invalid/zero opcode, and aborts on detected runaway jumps.
- Operand helpers: `atom_get_src_int`, `atom_get_src`, `atom_get_dst`, `atom_put_dst`, and skip/direct variants decode AtomBIOS operand encodings, perform little-endian BIOS reads, preserve partial destination fields, and route reads/writes to the correct backend.
- `atom_iio_execute` and `atom_index_iio`: interpret firmware-defined indirect I/O microprograms and build an index of available indirect I/O methods from the data table.
- Opcode handlers: arithmetic/logical (`atom_op_add`, `and`, `or`, `xor`, `sub`, `mul`, `div`, `mask`, `clear`), shifts (`shift_left`, `shift_right`, `shl`, `shr`), control flow (`compare`, `test`, `jump`, `switch`, `calltable`, `eot`), state setters (`setport`, `setregblock`, `setfbbase`, `setdatablock`), waits/debug outputs (`delay`, `postcard`, `beep`), and unimplemented placeholders (`repeat`, `savereg`, `restorereg`, `debug`).
- `atom_asic_init`: builds the init parameter space from firmware-info default SCLK/MCLK values, executes the `ASIC_Init` command table, and on pre-R600 hardware optionally executes the fan-control table.
- `atom_parse_data_header` and `atom_parse_cmd_header`: validate master table entries and return size/revision/start metadata for data and command tables.
- `atom_allocate_fb_scratch`: reads `VRAM_UsageByFirmware`, falls back to a 20 KiB scratch area, allocates zeroed scratch memory, and records `scratch_size_bytes`.
- `atom_destroy`: frees the indirect-I/O index and context. The scratch buffer allocated by `atom_allocate_fb_scratch` is not freed here in this version and must be owned elsewhere or represents a leak risk.

## Control Flow

Parsing starts in `atom_parse`: after allocation it checks `ATOM_BIOS_MAGIC`, ATI magic at `ATOM_ATI_MAGIC_PTR`, and ATOM ROM magic through `ATOM_ROM_TABLE_PTR`. It then stores the command and data master table offsets, calls `atom_index_iio` on the indirect-I/O data area, extracts a printable BIOS name, and returns the context. The caller initializes the context mutexes outside this file.

Execution starts at `atom_execute_table`, which serializes firmware scratch use with `scratch_mutex`. `atom_execute_table_scratch_unlocked` then serializes interpreter state with `ctx->mutex`, resets global execution state, and enters `atom_execute_table_locked`. The locked executor uses the master command table entry for `index`, reads table length/workspace/parameter-space metadata, initializes an `atom_exec_context`, allocates per-table workspace if requested, and repeatedly fetches one opcode byte from BIOS memory. Each valid opcode maps through `opcode_table` to a handler and an argument family such as register, parameter space, workspace, framebuffer scratch, PLL, or memory controller. Handlers advance the bytecode pointer through operands and may mutate the pointer for jumps, switches, or nested command-table calls.

Operand control flow is centralized. Source reads decode an argument kind and alignment field from the attribute byte. Register operands are offset by `ctx->reg_block` and routed through memory-mapped, PCI, SYSIO, or indirect-I/O mode. Parameter-space reads use `get_unaligned_le32` to avoid unaligned access faults. Workspace reads return either table-local `ws` entries or special global pseudo-registers such as quotient/remainder, data pointer, shift masks, framebuffer window, attributes, and register pointer. ID operands read from the current `data_block`; framebuffer operands access `ctx->scratch` at `fb_base`; PLL and MC operands call the driver callbacks. Destination writes reverse the same routing while preserving unaffected bit fields through saved full-width values.

Control-flow opcodes depend on `ctx->cs_equal` and `ctx->cs_above`, set by compare/test handlers. `atom_op_jump` computes whether a conditional branch should be taken, updates `ptr`, and tracks repeated jumps to the same target. If the same target is observed for more than five seconds, execution sets `abort`, causing the next loop iteration to fail with `-EINVAL`. `atom_op_calltable` recursively executes another command table with a shifted view of the current parameter space and propagates failure by setting the caller's abort flag.

## State and Persistence Behavior

Most state is transient per invocation, but `struct atom_context` persists across the driver's lifetime. Persistent fields include BIOS pointer, table offsets, indirect-I/O index, scratch pointer/size, register/data/framebuffer base selectors, division/multiplication results, condition flags, I/O mode, shift value, and driver callbacks. Before normal command execution, `atom_execute_table_scratch_unlocked` resets the mutable interpreter selectors and arithmetic result registers, limiting state carryover between tables.

Parameter space is supplied by the caller and can be modified by bytecode through `ATOM_ARG_PS` destinations. Table-local workspace is newly allocated per command table and freed before return. Scratch framebuffer memory is context-wide and shared by tables; public execution serializes it with `scratch_mutex`, while some specialized callers use `atom_execute_table_scratch_unlocked` only after taking that mutex themselves. Hardware state persists through callback writes to GPU registers, I/O registers, PLLs, and memory-controller registers.

Debug behavior is controlled by the global `atom_debug` integer and `ATOM_DEBUG` compile-time macro. Debug indentation uses the file-scope `debug_depth`, which is adjusted during nested table execution while the interpreter mutex is held.

## Dependencies and Integration Points

- Kernel/DRM services: allocation (`kzalloc_obj`, `kcalloc`, `kzalloc`, `kfree`), delays (`udelay`, `mdelay`, `msleep`), `drm_can_sleep`, logging (`pr_info`, `DRM_ERROR`, `DRM_DEBUG`), unaligned reads, jiffies loop timing, and mutexes initialized by Radeon device setup.
- Radeon device integration: `ctx->card->dev->dev_private` is cast to `struct radeon_device` for family-specific behavior in indirect I/O and ASIC initialization. `card_info` callbacks perform the actual register, I/O register, PLL, and memory-controller accesses.
- AtomBIOS definitions: `atom.h` provides constants and public context declarations; `atom-bits.h` provides BIOS byte/word/dword access macros; `atom-names.h` provides debug name arrays; `atom-types.h`, `atombios.h`, and `ObjectID.h` provide firmware table structures and master-table index helpers.
- Driver entry points: `radeon_device.c` calls `atom_parse` and initializes `ctx->mutex`/`ctx->scratch_mutex`; `atombios_i2c.c` and `atombios_dp.c` can lock `scratch_mutex` and use the scratch-unlocked execution path; broader Radeon AtomBIOS code calls table execution and table-header helpers.

## Risks and Edge Cases

- BIOS bounds are mostly trusted. Bytecode pointer arithmetic, master-table offsets, indirect-I/O table walking, and command/data header parsing do not consistently validate offsets against the actual BIOS image length.
- The indirect-I/O writer indexes `ctx->iio[gctx->io_mode & 0xFF]` while diagnostics use `& 0x7F`; because IIO modes are encoded with bit `0x80`, `& 0xFF` can address entries 128..255 instead of the intended method number. This may be intentional if indexed that way by firmware, but it differs from read-side lookup and the error message.
- Framebuffer scratch bounds check uses `>` instead of `>=`, so an access exactly at `scratch_size_bytes` can pass even though the indexed 32-bit word begins out of range. It also assumes `fb_base` is word-aligned.
- `atom_index_iio` walks until the first non-`ATOM_IIO_START` and does not check opcode bounds before indexing `atom_iio_len[CU8(base)]`.
- `atom_execute_table_locked` allocates `kcalloc(4, ws, GFP_KERNEL)`, which yields the requested byte count but is argument-order unusual compared with `kcalloc(ws, sizeof(u32), ...)`; reviewers should verify this remains intentional and not confused in future edits.
- Several opcodes are logged as unimplemented (`repeat`, `savereg`, `restorereg`, `debug`). Firmware requiring them will not get full behavior.
- Division by zero is handled by zeroing quotient/remainder, which may mask malformed firmware inputs.
- `atom_destroy` does not free `ctx->scratch`; ownership may be external in this snapshot, but any lifecycle change should confirm scratch memory is released exactly once.
- Table execution can sleep for millisecond delays if allowed by `drm_can_sleep`; callers must not invoke sleeping paths from atomic contexts unless firmware only requests microsecond or busy delays.

## Test Signals

- Parse-path tests should cover invalid BIOS magic, invalid ATI magic, invalid ATOM magic, absent indirect-I/O allocation, and name strings without NUL termination.
- Header-helper tests should cover present and absent command/data master entries, optional output pointers, and little-endian size/revision extraction.
- Interpreter tests should exercise representative opcodes for register/PS/WS/FB/PLL/MC operands, partial-width alignment preservation, parameter-space mutation, nested `CALLTABLE`, condition flag behavior, jump/switch target handling, and unimplemented opcode logging.
- State tests should assert that `atom_execute_table` serializes `scratch_mutex`, resets global selectors/results between invocations, and frees per-table workspace on success and abort.
- Robustness tests or fuzzing against synthetic BIOS bytecode should target out-of-range PS/WS/FB access, bad indirect-I/O opcodes, malformed switch cases, invalid opcodes, repeated jumps, and command/data table offsets near image boundaries.
- Hardware-integration signals include successful `atom_asic_init` on supported boards, expected register callback sequences for known AtomBIOS tables, pre-R600 fan-control invocation, and no lockdep warnings when I2C/DP paths share scratch execution.
