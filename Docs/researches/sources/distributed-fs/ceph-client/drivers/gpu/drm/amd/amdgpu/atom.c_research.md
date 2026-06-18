# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atom.c

## Purpose
This file implements the legacy ATOM BIOS bytecode interpreter and parser used by AMDGPU to run firmware command tables for ASIC initialization and display programming. It validates ROM headers, indexes command/data/IIO tables, interprets ATOM opcodes, accesses device registers through driver callbacks, manages interpreter scratch/workspace state, and extracts VBIOS identity strings.

## Important APIs, types, and functions
The public functions are `amdgpu_atom_parse()`, `amdgpu_atom_execute_table()`, `amdgpu_atom_asic_init()`, `amdgpu_atom_destroy()`, `amdgpu_atom_parse_data_header()`, and `amdgpu_atom_parse_cmd_header()`. `amdgpu_atom_debug` controls verbose interpreter logging.

`atom_exec_context` carries one command-table invocation: parameter-space pointer/size, workspace pointer/size, parameter shift, command start offset, last jump tracking, and abort flag. `atom_iio_execute()` interprets indirect-I/O mini-programs for ATOM IIO ports. `atom_get_src_int()`, `atom_get_dst()`, `atom_put_dst()`, and skip/direct helpers implement operand decoding for registers, parameter space, workspace, scratch FB, immediate values, PLL, MC, and data-table offsets.

The opcode table maps ATOM bytecodes to functions for move, arithmetic, bitwise operations, shifts, compares/tests, jumps, switch, delay, calltable, set data block, set register block, set port, mask, debug, processds, and 32-bit multiply/divide. Unimplemented save/restore/repeat opcodes log messages. `amdgpu_atom_execute_table_locked()` performs the actual command walk and loop-abort handling; `amdgpu_atom_execute_table()` serializes execution with `ctx->mutex` and resets global interpreter state before entry.

Parser helpers include `atom_index_iio()`, VBIOS name/date/part-number/version/build extraction helpers, and `atom_print_vbios_info()`.

## Control flow
Parsing allocates an `atom_context`, validates BIOS, ATI, and ATOM magic strings, reads master command/data table offsets, indexes IIO methods, optionally reads firmware revision, extracts VBIOS metadata, prints summary info, and returns the context. Command execution locks the context, resets mutable interpreter globals, reads command table metadata, allocates workspace if needed, then repeatedly fetches opcodes from BIOS memory until invalid opcode or EOT. Opcode handlers mutate the instruction pointer, state registers, workspace/parameter memory, scratch memory, and hardware via callback reads/writes. Jump handling detects repeated jumps stuck longer than 20 seconds and aborts the table.

## State and persistence behavior
Persistent state lives in `atom_context`: BIOS pointer, table offsets, IIO table index, interpreter globals, scratch pointer/size, mutex, and VBIOS strings. Each command allocates transient workspace, uses caller-provided parameter storage, and can mutate hardware registers, PLL registers, MC registers, scratch memory, and context globals. The mutex serializes command execution because those globals are shared per context.

## Dependencies
The interpreter depends on ATOM generated type/name/bit headers, unaligned little-endian helpers, DRM logging/utilities, AMDGPU core, driver-supplied `card_info` register/PLL/MC callbacks, Linux memory allocation, delay, jiffies, and string helpers.

## Integration points
Display code uses this interpreter through ATOM command tables for CRTC, DP, encoder, PLL, power-gating, spread-spectrum, and AUX operations. ASIC initialization calls `amdgpu_atom_asic_init()`. Header parsers are used by many ATOMBIOS helper files to select parameter structure revisions.

## Risks and edge cases
The interpreter consumes untrusted or corrupted BIOS data with limited bounds checking; bad offsets can drive reads outside intended ROM memory. Scratch FB bounds checks use `>` rather than `>=`, which deserves care at exact-size boundaries. IIO index checks use both `0x7F` and `0xFF` masks in different paths. Several opcode paths are unimplemented. Parameter-space writes use little-endian conversion and unaligned reads, so caller buffer sizing matters. Long-running loops are detected only when repeatedly jumping to the same target and after a wall-clock timeout. Hardware callbacks can execute arbitrary register side effects from firmware bytecode.

## Test signals
Useful tests include parsing valid/invalid ROM headers, executing known ATOM command snippets, operand decoding for every storage class and alignment, workspace and parameter bounds, IIO mini-program indexing, timeout behavior, nested calltable failure propagation, VBIOS metadata extraction, and fuzzing corrupted table offsets/opcodes under a fake `card_info`.
