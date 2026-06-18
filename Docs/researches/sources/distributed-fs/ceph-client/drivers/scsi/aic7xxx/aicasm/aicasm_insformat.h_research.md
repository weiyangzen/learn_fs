# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_insformat.h

Purpose: binary instruction layout definitions for the AIC7xxx sequencer assembler. It maps assembler semantic fields into endian-sensitive 32-bit instruction encodings and defines opcode constants used by grammar formatting functions.

Important APIs and types: defines `struct ins_format1` through `struct ins_format6` for 8-bit ALU, shift/rotate, branch, 16-bit ALU, 16-bit branch, and far branch formats. `union ins_formats` overlays these formats with raw bytes and integer access. `struct instruction` stores an encoded instruction, source line, optional patch label, and queue linkage. Opcode macros include `AIC_OP_OR`, `AND`, `XOR`, `ADD`, `ADC`, `ROL`, `BMOV`, `MVI16`, branch opcodes, pseudo shift/rotate opcodes, 16-bit opcodes, far branch opcodes, and `AIC_OP_CMPXCHG`.

Control flow role: `aicasm_gram.y` allocates `struct instruction` objects and fills the appropriate bitfield format in `format_1_instr()`, `format_2_instr()`, and `format_3_instr()`. `aicasm.c` later emits `format.bytes[]` in host-endian-aware order to generated C output and listings.

State and persistence: each instruction object carries the generated encoding and metadata needed for listings and backpatching. No global state is defined here.

Dependencies and integration: includes `<asm/byteorder.h>` and uses `__LITTLE_ENDIAN` to choose bitfield ordering. It depends on queue macros indirectly through `STAILQ_ENTRY` availability from including contexts and on `struct symbol` forward visibility through included assembler headers.

Risks: C bitfield layout is compiler- and endian-sensitive; the code mitigates endian order but still assumes compatible compiler behavior. Opcode constants must match sequencer hardware. Emission order must stay synchronized with bitfield definitions. Incorrect parity bit use affects downloaded constants.

Test signals: assemble small opcode fixtures and compare exact bytes on little- and big-endian hosts, validate branch address field limits, compare generated shipped sequencer headers, and build with compilers used for kernel host tools.
