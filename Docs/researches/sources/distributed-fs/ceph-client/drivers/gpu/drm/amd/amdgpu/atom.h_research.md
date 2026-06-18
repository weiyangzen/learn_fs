# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/atom.h

## Purpose
This header defines the legacy ATOM BIOS interpreter API, ROM/table constants, operand encodings, workspace identifiers, IIO opcodes, and the `card_info`/`atom_context` structures shared by the parser, interpreter, and ATOMBIOS display helpers.

## Important APIs, types, and functions
Constants define BIOS magic values and offsets, ATOM ROM command/data pointers, common command/data table indexes, command-table metadata offsets, opcode count/EOT opcode, switch/case magic, operand source classes, source alignments, workspace pseudo-registers, indirect-I/O opcodes, I/O modes, and string buffer lengths.

`struct card_info` supplies driver callbacks for MM register, MC register, and PLL register reads/writes and carries the DRM device pointer. `struct atom_context` stores the card, mutex, BIOS pointer, command/data table offsets, IIO table, current data block, scratch FB base, division/multiply results, I/O attributes, register block, shift, compare flags, I/O mode, scratch pointer/size, and VBIOS metadata strings.

The public API declares parsing, command execution, ASIC init, destruction, and command/data table header parsing. It also includes `atom-types.h`, `atombios.h`, and `ObjectID.h`, making generated ATOM structures available to includers.

## Control flow
The header itself is declarative. Runtime users create an `atom_context` with `amdgpu_atom_parse()`, run command tables with `amdgpu_atom_execute_table()`, query table revisions with parse-header helpers, and free with `amdgpu_atom_destroy()`.

## State and persistence behavior
`atom_context` is long-lived driver state tied to a parsed VBIOS image. Its mutex protects mutable interpreter fields. Scratch memory is caller-provided through the context and is used by command execution.

## Dependencies
It depends on Linux integer types, DRM forward declaration, generated ATOM headers, ObjectID definitions, and AMDGPU code that fills `card_info` callbacks.

## Integration points
All legacy ATOMBIOS display helpers depend on this header for command-table constants and parameter structures. ASIC init and VBIOS metadata reporting also depend on the context.

## Risks and edge cases
The header exposes many low-level mutable fields, so consumers can accidentally bypass interpreter invariants. Include order matters for generated ATOM structures. Constants must remain synchronized with ATOM firmware format; incorrect offsets break parser safety.

## Test signals
Compile coverage across ATOMBIOS helpers, fake-card interpreter tests, and parser tests over known VBIOS images validate this interface.
