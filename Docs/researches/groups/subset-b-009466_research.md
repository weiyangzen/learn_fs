# Research Group subset-b-009466

Grouped research for RISC-V V-extension instruction YAML schemas under `sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V`. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vremu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vremu.vv.yaml

## Purpose

`vremu.vv` defines a RISC-V V-extension remainder instruction for the ifuzz instruction generator.
The file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit fields,
access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vremu.vv` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 100010-----------010-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `MVV_VAADDU`, `MVV_VAADD`, `MVV_VASUBU`,
`MVV_VASUB`, `MVV_VMUL`, `MVV_VMULH`, `MVV_VMULHU`, `MVV_VMULHSU`, `MVV_VDIVU`, `MVV_VDIV`, and 2
more; this file selects the label matching `vremu.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `illegal_normal`, `init_masked_result`, `read_vmask`, `read_vreg`,
`write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include division-by-zero and signed overflow remainder cases must match the
ISA's special return values.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, zero divisor, unsigned
and signed operands, minimum signed value divided by -1.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vremu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vremu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vremu.vx.yaml

## Purpose

`vremu.vx` defines a RISC-V V-extension remainder instruction for the ifuzz instruction generator.
The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit fields,
access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vremu.vx` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 100010-----------110-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `MVX_VAADDU`, `MVX_VAADD`, `MVX_VASUBU`,
`MVX_VASUB`, `MVX_VSLIDE1UP`, `MVX_VSLIDE1DOWN`, `MVX_VMUL`, `MVX_VMULH`, `MVX_VMULHU`,
`MVX_VMULHSU`, and 4 more; this file selects the label matching `vremu.vx` through the fixed
encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include division-by-zero and signed overflow remainder cases must match the
ISA's special return values.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, zero divisor, unsigned
and signed operands, minimum signed value divided by -1.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vremu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgather.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgather.vi.yaml

## Purpose

`vrgather.vi` defines a RISC-V V-extension vector gather instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vrgather.vi` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 001100-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VSLIDEUP`, `VI_VSLIDEDOWN`,
`VI_VRGATHER`; this file selects the label matching `vrgather.vi` through the fixed encoding
pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`get_sew_pow`, `get_vlen_pow`, `illegal_normal`, `init_masked_result`, `read_vmask`, `read_vreg`,
`write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include out-of-range indices must return zero and illegal overlap with `vd`
must be detected.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, in-range and out-of-
range indices, destination overlap rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgather.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgather.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgather.vv.yaml

## Purpose

`vrgather.vv` defines a RISC-V V-extension vector gather instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vrgather.vv` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 001100-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vrgather.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include out-of-range indices must return zero and illegal overlap with `vd`
must be detected.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, in-range and out-of-
range indices, destination overlap rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgather.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgather.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgather.vx.yaml

## Purpose

`vrgather.vx` defines a RISC-V V-extension vector gather instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vrgather.vx` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 001100-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VSLIDEUP`, `VX_VSLIDEDOWN`,
`VX_VRGATHER`; this file selects the label matching `vrgather.vx` through the fixed encoding
pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`get_sew_pow`, `get_vlen_pow`, `illegal_normal`, `init_masked_result`, `read_vmask`, `read_vreg`,
`write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include out-of-range indices must return zero and illegal overlap with `vd`
must be detected.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, in-range and out-of-
range indices, destination overlap rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgather.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgatherei16.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgatherei16.vv.yaml

## Purpose

`vrgatherei16.vv` defines a RISC-V V-extension vector gather instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vrgatherei16.vv` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 001110-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vrgatherei16.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include out-of-range indices must return zero and illegal overlap with `vd`
must be detected.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, in-range and out-of-
range indices, destination overlap rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrgatherei16.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrsub.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrsub.vi.yaml

## Purpose

`vrsub.vi` defines a RISC-V V-extension reverse subtract instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vrsub.vi` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 000011-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `True`.

The embedded Sail block dispatches over `funct6` labels `VI_VADD`, `VI_VRSUB`, `VI_VAND`, `VI_VOR`,
`VI_VXOR`, `VI_VSADDU`, `VI_VSADD`, `VI_VSLL`, `VI_VSRL`, `VI_VSRA`, and 2 more; this file selects
the label matching `vrsub.vi` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `signed_saturation`, `unsigned_saturation`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the main risk is schema drift between the opcode pattern, assembly
operands, and shared Sail helper assumptions.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrsub.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrsub.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrsub.vx.yaml

## Purpose

`vrsub.vx` defines a RISC-V V-extension reverse subtract instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vrsub.vx` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 000011-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `True`.

The embedded Sail block dispatches over `funct6` labels `VX_VADD`, `VX_VSUB`, `VX_VRSUB`, `VX_VAND`,
`VX_VOR`, `VX_VXOR`, `VX_VSADDU`, `VX_VSADD`, `VX_VSSUBU`, `VX_VSSUB`, and 10 more; this file
selects the label matching `vrsub.vx` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`,
`read_vmask`, `read_vreg`, `signed_saturation`, `unsigned_saturation`, and 1 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the main risk is schema drift between the opcode pattern, assembly
operands, and shared Sail helper assumptions.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vrsub.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs1r.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs1r.v.yaml

## Purpose

`vs1r.v` defines a RISC-V V-extension whole-register store instruction for the ifuzz generator. The
YAML maps the assembler form `vs3, (xs1)` to its opcode fields and, where present, delegates
behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vs1r.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1)`.

The decoder key is `encoding.match: 000000101000-----000-----0100111` with variables `xs1@19-15`,
`vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local Sail control flow beyond the schema fields. The instruction can still be assembled
or decoded by metadata-driven tooling, but semantic execution is not described in this YAML.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs1r.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs2r.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs2r.v.yaml

## Purpose

`vs2r.v` defines a RISC-V V-extension whole-register store instruction for the ifuzz generator. The
YAML maps the assembler form `vs3, (xs1)` to its opcode fields and, where present, delegates
behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vs2r.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1)`.

The decoder key is `encoding.match: 001000101000-----000-----0100111` with variables `xs1@19-15`,
`vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local Sail control flow beyond the schema fields. The instruction can still be assembled
or decoded by metadata-driven tooling, but semantic execution is not described in this YAML.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs2r.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs4r.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs4r.v.yaml

## Purpose

`vs4r.v` defines a RISC-V V-extension whole-register store instruction for the ifuzz generator. The
YAML maps the assembler form `vs3, (xs1)` to its opcode fields and, where present, delegates
behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vs4r.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1)`.

The decoder key is `encoding.match: 011000101000-----000-----0100111` with variables `xs1@19-15`,
`vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local Sail control flow beyond the schema fields. The instruction can still be assembled
or decoded by metadata-driven tooling, but semantic execution is not described in this YAML.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs4r.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs8r.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs8r.v.yaml

## Purpose

`vs8r.v` defines a RISC-V V-extension whole-register store instruction for the ifuzz generator. The
YAML maps the assembler form `vs3, (xs1)` to its opcode fields and, where present, delegates
behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vs8r.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1)`.

The decoder key is `encoding.match: 111000101000-----000-----0100111` with variables `xs1@19-15`,
`vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local Sail control flow beyond the schema fields. The instruction can still be assembled
or decoded by metadata-driven tooling, but semantic execution is not described in this YAML.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vs8r.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsadd.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsadd.vi.yaml

## Purpose

`vsadd.vi` defines a RISC-V V-extension saturating add instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsadd.vi` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 100001-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VADD`, `VI_VRSUB`, `VI_VAND`, `VI_VOR`,
`VI_VXOR`, `VI_VSADDU`, `VI_VSADD`, `VI_VSLL`, `VI_VSRL`, `VI_VSRA`, and 2 more; this file selects
the label matching `vsadd.vi` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `signed_saturation`, `unsigned_saturation`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include saturation and fixed-point rounding behavior can diverge from hardware
if sign extension or increment selection is wrong.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, positive and negative
overflow, rounding-mode-sensitive fixed-point cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsadd.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsadd.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsadd.vv.yaml

## Purpose

`vsadd.vv` defines a RISC-V V-extension saturating add instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsadd.vv` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 100001-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vsadd.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include saturation and fixed-point rounding behavior can diverge from hardware
if sign extension or increment selection is wrong.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, positive and negative
overflow, rounding-mode-sensitive fixed-point cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsadd.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsadd.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsadd.vx.yaml

## Purpose

`vsadd.vx` defines a RISC-V V-extension saturating add instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsadd.vx` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 100001-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VADD`, `VX_VSUB`, `VX_VRSUB`, `VX_VAND`,
`VX_VOR`, `VX_VXOR`, `VX_VSADDU`, `VX_VSADD`, `VX_VSSUBU`, `VX_VSSUB`, and 10 more; this file
selects the label matching `vsadd.vx` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`,
`read_vmask`, `read_vreg`, `signed_saturation`, `unsigned_saturation`, and 1 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include saturation and fixed-point rounding behavior can diverge from hardware
if sign extension or increment selection is wrong.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, positive and negative
overflow, rounding-mode-sensitive fixed-point cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsadd.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsaddu.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsaddu.vi.yaml

## Purpose

`vsaddu.vi` defines a RISC-V V-extension saturating add instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsaddu.vi` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 100000-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VADD`, `VI_VRSUB`, `VI_VAND`, `VI_VOR`,
`VI_VXOR`, `VI_VSADDU`, `VI_VSADD`, `VI_VSLL`, `VI_VSRL`, `VI_VSRA`, and 2 more; this file selects
the label matching `vsaddu.vi` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `signed_saturation`, `unsigned_saturation`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include saturation and fixed-point rounding behavior can diverge from hardware
if sign extension or increment selection is wrong.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, positive and negative
overflow, rounding-mode-sensitive fixed-point cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsaddu.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsaddu.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsaddu.vv.yaml

## Purpose

`vsaddu.vv` defines a RISC-V V-extension saturating add instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsaddu.vv` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 100000-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vsaddu.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include saturation and fixed-point rounding behavior can diverge from hardware
if sign extension or increment selection is wrong.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, positive and negative
overflow, rounding-mode-sensitive fixed-point cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsaddu.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsaddu.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsaddu.vx.yaml

## Purpose

`vsaddu.vx` defines a RISC-V V-extension saturating add instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsaddu.vx` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 100000-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VADD`, `VX_VSUB`, `VX_VRSUB`, `VX_VAND`,
`VX_VOR`, `VX_VXOR`, `VX_VSADDU`, `VX_VSADD`, `VX_VSSUBU`, `VX_VSSUB`, and 10 more; this file
selects the label matching `vsaddu.vx` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`,
`read_vmask`, `read_vreg`, `signed_saturation`, `unsigned_saturation`, and 1 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include saturation and fixed-point rounding behavior can diverge from hardware
if sign extension or increment selection is wrong.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, positive and negative
overflow, rounding-mode-sensitive fixed-point cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsaddu.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsbc.vvm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsbc.vvm.yaml

## Purpose

`vsbc.vvm` defines a RISC-V V-extension subtract-with-borrow instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, v0` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsbc.vvm` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, v0`.

The decoder key is `encoding.match: 0100100----------000-----1010111` with variables `vs2@24-20`,
`vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VVMS_VADC`, `VVMS_VSBC`; this file selects
the label matching `vsbc.vvm` through the fixed encoding pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`illegal_vd_masked`, `init_masked_result`, `read_vmask_carry`, `read_vreg`, `write_vreg`.

## Control Flow

Execution uses the carry-mask path rather than normal element masking: it rejects masked
destination-register overlap with `illegal_vd_masked`, reads borrow bits from `v0` through
`read_vmask_carry`, initializes all lanes as active, subtracts `vs1` and the borrow bit from `vs2`,
writes `vd`, and clears `vstart`.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include borrow bits are read from `v0`, not the normal mask path, and
destination-mask overlap is illegal.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, borrow mask lanes from
v0, vd mask-register overlap rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsbc.vvm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsbc.vxm.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsbc.vxm.yaml

## Purpose

`vsbc.vxm` defines a RISC-V V-extension subtract-with-borrow instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, v0` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsbc.vxm` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, v0`.

The decoder key is `encoding.match: 0100100----------100-----1010111` with variables `vs2@24-20`,
`xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VXMS_VADC`, `VXMS_VSBC`; this file selects
the label matching `vsbc.vxm` through the fixed encoding pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_scalar`, `get_sew`,
`illegal_vd_masked`, `init_masked_result`, `read_vmask_carry`, `read_vreg`, `write_vreg`.

## Control Flow

Execution uses the carry-mask path rather than normal element masking: it rejects masked
destination-register overlap with `illegal_vd_masked`, reads borrow bits from `v0` through
`read_vmask_carry`, initializes all lanes as active, subtracts `vs1` and the borrow bit from `vs2`,
writes `vd`, and clears `vstart`.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include borrow bits are read from `v0`, not the normal mask path, and
destination-mask overlap is illegal.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, borrow mask lanes from
v0, vd mask-register overlap rejection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsbc.vxm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse16.v.yaml

## Purpose

`vse16.v` defines a RISC-V V-extension unit-stride element store instruction for the ifuzz
generator. The YAML maps the assembler form `vs3, (xs1), vm` to its opcode fields and, where
present, delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vse16.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 000000-00000-----101-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_store`, `process_vsseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse32.v.yaml

## Purpose

`vse32.v` defines a RISC-V V-extension unit-stride element store instruction for the ifuzz
generator. The YAML maps the assembler form `vs3, (xs1), vm` to its opcode fields and, where
present, delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vse32.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 000000-00000-----110-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_store`, `process_vsseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse64.v.yaml

## Purpose

`vse64.v` defines a RISC-V V-extension unit-stride element store instruction for the ifuzz
generator. The YAML maps the assembler form `vs3, (xs1), vm` to its opcode fields and, where
present, delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vse64.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 000000-00000-----111-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_store`, `process_vsseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse8.v.yaml

## Purpose

`vse8.v` defines a RISC-V V-extension unit-stride element store instruction for the ifuzz generator.
The YAML maps the assembler form `vs3, (xs1), vm` to its opcode fields and, where present, delegates
behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vse8.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 000000-00000-----000-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_store`, `process_vsseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vse8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetivli.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetivli.yaml

## Purpose

`vsetivli` is a RISC-V vector instruction definition for Set the vtype and vl CSRs, and write the
new value of vl into rd. It is encoded as an ifuzz instruction schema entry with assembly operands
`xd, uimm, vtypei`.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsetivli` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `xd, uimm, vtypei`.

The decoder key is `encoding.match: 11---------------111-----1010111` with variables `vtypei@29-20`,
`uimm@19-15`, `xd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_sew_pow`, `get_vlen_pow`.

## Control Flow

Execution decodes the requested `vtype` from either immediates or a source register, validates
SEW/LMUL support, computes `VLMAX`, chooses `vl` from AVL strip-mining rules, writes `vtype` and
`vl`, optionally writes `rd`, clears `vstart`, and retires. Illegal or unsupported settings set
`vill` and zero `vl` instead of producing lane operations.

## State and Persistence Behavior

This instruction mutates architectural vector CSRs: `vtype`, `vl`, and `vstart`, and writes the
selected integer destination register. It does not persist filesystem state. Its result changes the
shape and masking behavior of subsequent vector instructions.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, vector
CSR and strip-mining helper state. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include AVL/VLMAX corner cases, reserved `vtype` bits, and `rd=x0`/`rs1=x0`
keep-vl behavior are easy to model incorrectly.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, reserved vtype
encodings, AVL values 0, VLMAX, VLMAX+1, and at least 2*VLMAX, rd/xs1 zero-register combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetivli.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetvl.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetvl.yaml

## Purpose

`vsetvl` is a RISC-V vector instruction definition for Set the vtype and vl CSRs, and write the new
value of vl into rd. It is encoded as an ifuzz instruction schema entry with assembly operands `xd,
xs1, xs2`.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsetvl` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `xd, xs1, xs2`.

The decoder key is `encoding.match: 1000000----------111-----1010111` with variables `xs2@24-20`,
`xs1@19-15`, `xd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VSETVLI`, `VSETVL`; this file selects the
label matching `vsetvl` through the fixed encoding pattern.

Important model helper dependencies include `get_lmul_pow`, `get_sew_pow`, `get_vlen_pow`.

## Control Flow

Execution decodes the requested `vtype` from either immediates or a source register, validates
SEW/LMUL support, computes `VLMAX`, chooses `vl` from AVL strip-mining rules, writes `vtype` and
`vl`, optionally writes `rd`, clears `vstart`, and retires. Illegal or unsupported settings set
`vill` and zero `vl` instead of producing lane operations.

## State and Persistence Behavior

This instruction mutates architectural vector CSRs: `vtype`, `vl`, and `vstart`, and writes the
selected integer destination register. It does not persist filesystem state. Its result changes the
shape and masking behavior of subsequent vector instructions.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, vector
CSR and strip-mining helper state. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include AVL/VLMAX corner cases, reserved `vtype` bits, and `rd=x0`/`rs1=x0`
keep-vl behavior are easy to model incorrectly.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, reserved vtype
encodings, AVL values 0, VLMAX, VLMAX+1, and at least 2*VLMAX, rd/xs1 zero-register combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetvl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetvli.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetvli.yaml

## Purpose

`vsetvli` is a RISC-V vector instruction definition for Set the vtype and vl CSRs, and write the new
value of vl into rd. It is encoded as an ifuzz instruction schema entry with assembly operands `xd,
xs1, vtypei`.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsetvli` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `xd, xs1, vtypei`.

The decoder key is `encoding.match: 0----------------111-----1010111` with variables `vtypei@30-20`,
`xs1@19-15`, `xd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VSETVLI`, `VSETVL`; this file selects the
label matching `vsetvli` through the fixed encoding pattern.

Important model helper dependencies include `get_lmul_pow`, `get_sew_pow`, `get_vlen_pow`.

## Control Flow

Execution decodes the requested `vtype` from either immediates or a source register, validates
SEW/LMUL support, computes `VLMAX`, chooses `vl` from AVL strip-mining rules, writes `vtype` and
`vl`, optionally writes `rd`, clears `vstart`, and retires. Illegal or unsupported settings set
`vill` and zero `vl` instead of producing lane operations.

## State and Persistence Behavior

This instruction mutates architectural vector CSRs: `vtype`, `vl`, and `vstart`, and writes the
selected integer destination register. It does not persist filesystem state. Its result changes the
shape and masking behavior of subsequent vector instructions.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, vector
CSR and strip-mining helper state. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include AVL/VLMAX corner cases, reserved `vtype` bits, and `rd=x0`/`rs1=x0`
keep-vl behavior are easy to model incorrectly.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, reserved vtype
encodings, AVL values 0, VLMAX, VLMAX+1, and at least 2*VLMAX, rd/xs1 zero-register combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsetvli.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf2.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf2.yaml

## Purpose

`vsext.vf2` defines a RISC-V V-extension sign-extension instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vm` to an opcode pattern, operand bit fields,
access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsext.vf2` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, vm`.

The decoder key is `encoding.match: 010010------00111010-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VEXT2_ZVF2`, `VEXT2_SVF2`; this file
selects the label matching `vsext.vf2` through the fixed encoding pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`illegal_variable_width`, `init_masked_result`, `read_vmask`, `read_vreg`, `valid_reg_overlap`,
`write_vreg`.

## Control Flow

Execution reads a narrower source vector using the fractional width implied by the suffix, checks
variable-width legality and overlap, initializes masked results from the old destination, then zero-
or sign-extends each active source element into the current SEW before writing `vd`.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
variable-width legality and register-overlap helpers. The schema is consumed with neighboring
V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and
helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include fractional LMUL, narrow source register grouping, and destination
overlap constraints are legality-sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, vf2/vf4/vf8 legality
across SEW, sign-bit propagation, register overlap failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf4.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf4.yaml

## Purpose

`vsext.vf4` defines a RISC-V V-extension sign-extension instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vm` to an opcode pattern, operand bit fields,
access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsext.vf4` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, vm`.

The decoder key is `encoding.match: 010010------00101010-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VEXT4_ZVF4`, `VEXT4_SVF4`; this file
selects the label matching `vsext.vf4` through the fixed encoding pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`illegal_variable_width`, `init_masked_result`, `read_vmask`, `read_vreg`, `valid_reg_overlap`,
`write_vreg`.

## Control Flow

Execution reads a narrower source vector using the fractional width implied by the suffix, checks
variable-width legality and overlap, initializes masked results from the old destination, then zero-
or sign-extends each active source element into the current SEW before writing `vd`.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
variable-width legality and register-overlap helpers. The schema is consumed with neighboring
V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and
helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include fractional LMUL, narrow source register grouping, and destination
overlap constraints are legality-sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, vf2/vf4/vf8 legality
across SEW, sign-bit propagation, register overlap failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf8.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf8.yaml

## Purpose

`vsext.vf8` defines a RISC-V V-extension sign-extension instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vm` to an opcode pattern, operand bit fields,
access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsext.vf8` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, vm`.

The decoder key is `encoding.match: 010010------00011010-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VEXT8_ZVF8`, `VEXT8_SVF8`; this file
selects the label matching `vsext.vf8` through the fixed encoding pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`illegal_variable_width`, `init_masked_result`, `read_vmask`, `read_vreg`, `valid_reg_overlap`,
`write_vreg`.

## Control Flow

Execution reads a narrower source vector using the fractional width implied by the suffix, checks
variable-width legality and overlap, initializes masked results from the old destination, then zero-
or sign-extends each active source element into the current SEW before writing `vd`.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
variable-width legality and register-overlap helpers. The schema is consumed with neighboring
V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and
helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include fractional LMUL, narrow source register grouping, and destination
overlap constraints are legality-sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, vf2/vf4/vf8 legality
across SEW, sign-bit propagation, register overlap failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsext.vf8.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslide1down.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslide1down.vx.yaml

## Purpose

`vslide1down.vx` defines a RISC-V V-extension vector slide instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vslide1down.vx` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 001111-----------110-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `MVX_VAADDU`, `MVX_VAADD`, `MVX_VASUBU`,
`MVX_VASUB`, `MVX_VSLIDE1UP`, `MVX_VSLIDE1DOWN`, `MVX_VMUL`, `MVX_VMULH`, `MVX_VMULHU`,
`MVX_VMULHSU`, and 4 more; this file selects the label matching `vslide1down.vx` through the fixed
encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include source/destination overlap, first/last element handling, and out-of-
range slide distances are sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, zero and large slide
offsets, boundary element insertion, overlap rejection where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslide1down.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslide1up.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslide1up.vx.yaml

## Purpose

`vslide1up.vx` defines a RISC-V V-extension vector slide instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vslide1up.vx` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 001110-----------110-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `MVX_VAADDU`, `MVX_VAADD`, `MVX_VASUBU`,
`MVX_VASUB`, `MVX_VSLIDE1UP`, `MVX_VSLIDE1DOWN`, `MVX_VMUL`, `MVX_VMULH`, `MVX_VMULHU`,
`MVX_VMULHSU`, and 4 more; this file selects the label matching `vslide1up.vx` through the fixed
encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include source/destination overlap, first/last element handling, and out-of-
range slide distances are sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, zero and large slide
offsets, boundary element insertion, overlap rejection where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslide1up.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslidedown.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslidedown.vi.yaml

## Purpose

`vslidedown.vi` defines a RISC-V V-extension vector slide instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vslidedown.vi` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 001111-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VSLIDEUP`, `VI_VSLIDEDOWN`,
`VI_VRGATHER`; this file selects the label matching `vslidedown.vi` through the fixed encoding
pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`get_sew_pow`, `get_vlen_pow`, `illegal_normal`, `init_masked_result`, `read_vmask`, `read_vreg`,
`write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include source/destination overlap, first/last element handling, and out-of-
range slide distances are sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, zero and large slide
offsets, boundary element insertion, overlap rejection where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslidedown.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslidedown.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslidedown.vx.yaml

## Purpose

`vslidedown.vx` defines a RISC-V V-extension vector slide instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vslidedown.vx` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 001111-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VSLIDEUP`, `VX_VSLIDEDOWN`,
`VX_VRGATHER`; this file selects the label matching `vslidedown.vx` through the fixed encoding
pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`get_sew_pow`, `get_vlen_pow`, `illegal_normal`, `init_masked_result`, `read_vmask`, `read_vreg`,
`write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include source/destination overlap, first/last element handling, and out-of-
range slide distances are sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, zero and large slide
offsets, boundary element insertion, overlap rejection where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslidedown.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslideup.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslideup.vi.yaml

## Purpose

`vslideup.vi` defines a RISC-V V-extension vector slide instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vslideup.vi` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 001110-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VSLIDEUP`, `VI_VSLIDEDOWN`,
`VI_VRGATHER`; this file selects the label matching `vslideup.vi` through the fixed encoding
pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`get_sew_pow`, `get_vlen_pow`, `illegal_normal`, `init_masked_result`, `read_vmask`, `read_vreg`,
`write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include source/destination overlap, first/last element handling, and out-of-
range slide distances are sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, zero and large slide
offsets, boundary element insertion, overlap rejection where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslideup.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslideup.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslideup.vx.yaml

## Purpose

`vslideup.vx` defines a RISC-V V-extension vector slide instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vslideup.vx` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 001110-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VSLIDEUP`, `VX_VSLIDEDOWN`,
`VX_VRGATHER`; this file selects the label matching `vslideup.vx` through the fixed encoding
pattern.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew`,
`get_sew_pow`, `get_vlen_pow`, `illegal_normal`, `init_masked_result`, `read_vmask`, `read_vreg`,
`write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. For slide/gather
forms, the active-lane expression either shifts element indices by an immediate or scalar amount,
reads a selected source index, returns zero for out-of-range indices, and checks illegal
source/destination overlap where the ISA forbids in-place operation.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet,
VLEN/VLMAX index calculation helpers. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include source/destination overlap, first/last element handling, and out-of-
range slide distances are sensitive.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, zero and large slide
offsets, boundary element insertion, overlap rejection where applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vslideup.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsll.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsll.vi.yaml

## Purpose

`vsll.vi` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsll.vi` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 100101-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VADD`, `VI_VRSUB`, `VI_VAND`, `VI_VOR`,
`VI_VXOR`, `VI_VSADDU`, `VI_VSADD`, `VI_VSLL`, `VI_VSRL`, `VI_VSRA`, and 2 more; this file selects
the label matching `vsll.vi` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `signed_saturation`, `unsigned_saturation`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsll.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsll.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsll.vv.yaml

## Purpose

`vsll.vv` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsll.vv` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 100101-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vsll.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsll.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsll.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsll.vx.yaml

## Purpose

`vsll.vx` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsll.vx` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 100101-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VADD`, `VX_VSUB`, `VX_VRSUB`, `VX_VAND`,
`VX_VOR`, `VX_VXOR`, `VX_VSADDU`, `VX_VSADD`, `VX_VSSUBU`, `VX_VSSUB`, and 10 more; this file
selects the label matching `vsll.vx` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`,
`read_vmask`, `read_vreg`, `signed_saturation`, `unsigned_saturation`, and 1 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsll.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsm.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsm.v.yaml

## Purpose

`vsm.v` defines a RISC-V V-extension mask store instruction for the ifuzz generator. The YAML maps
the assembler form `vs3, (xs1)` to its opcode fields and, where present, delegates behavior to the
shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsm.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1)`.

The decoder key is `encoding.match: 000000101011-----000-----0100111` with variables `xs1@19-15`,
`vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_num_elem`, `illegal_vd_unmasked`, `process_vm`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsm.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsmul.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsmul.vv.yaml

## Purpose

`vsmul.vv` defines a RISC-V V-extension saturating multiply instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsmul.vv` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 100111-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vsmul.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include saturation and fixed-point rounding behavior can diverge from hardware
if sign extension or increment selection is wrong.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, positive and negative
overflow, rounding-mode-sensitive fixed-point cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsmul.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsmul.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsmul.vx.yaml

## Purpose

`vsmul.vx` defines a RISC-V V-extension saturating multiply instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsmul.vx` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 100111-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VADD`, `VX_VSUB`, `VX_VRSUB`, `VX_VAND`,
`VX_VOR`, `VX_VXOR`, `VX_VSADDU`, `VX_VSADD`, `VX_VSSUBU`, `VX_VSSUB`, and 10 more; this file
selects the label matching `vsmul.vx` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`,
`read_vmask`, `read_vreg`, `signed_saturation`, `unsigned_saturation`, and 1 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include saturation and fixed-point rounding behavior can diverge from hardware
if sign extension or increment selection is wrong.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, positive and negative
overflow, rounding-mode-sensitive fixed-point cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsmul.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei16.v.yaml

## Purpose

`vsoxei16.v` defines a RISC-V V-extension ordered indexed store instruction for the ifuzz generator.
The YAML maps the assembler form `vs3, (xs1), vs2, vm` to its opcode fields and, where present,
delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxei16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 000011-----------101-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_indexed_store`, `process_vsxseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei32.v.yaml

## Purpose

`vsoxei32.v` defines a RISC-V V-extension ordered indexed store instruction for the ifuzz generator.
The YAML maps the assembler form `vs3, (xs1), vs2, vm` to its opcode fields and, where present,
delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxei32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 000011-----------110-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_indexed_store`, `process_vsxseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei64.v.yaml

## Purpose

`vsoxei64.v` defines a RISC-V V-extension ordered indexed store instruction for the ifuzz generator.
The YAML maps the assembler form `vs3, (xs1), vs2, vm` to its opcode fields and, where present,
delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxei64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 000011-----------111-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_indexed_store`, `process_vsxseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei8.v.yaml

## Purpose

`vsoxei8.v` defines a RISC-V V-extension ordered indexed store instruction for the ifuzz generator.
The YAML maps the assembler form `vs3, (xs1), vs2, vm` to its opcode fields and, where present,
delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxei8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 000011-----------000-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_indexed_store`, `process_vsxseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei16.v.yaml

## Purpose

`vsoxseg2ei16.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg2ei16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 001011-----------101-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei32.v.yaml

## Purpose

`vsoxseg2ei32.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg2ei32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 001011-----------110-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei64.v.yaml

## Purpose

`vsoxseg2ei64.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg2ei64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 001011-----------111-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei8.v.yaml

## Purpose

`vsoxseg2ei8.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg2ei8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 001011-----------000-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg2ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei16.v.yaml

## Purpose

`vsoxseg3ei16.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg3ei16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 010011-----------101-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei32.v.yaml

## Purpose

`vsoxseg3ei32.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg3ei32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 010011-----------110-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei64.v.yaml

## Purpose

`vsoxseg3ei64.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg3ei64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 010011-----------111-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei8.v.yaml

## Purpose

`vsoxseg3ei8.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg3ei8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 010011-----------000-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg3ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei16.v.yaml

## Purpose

`vsoxseg4ei16.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg4ei16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 011011-----------101-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei32.v.yaml

## Purpose

`vsoxseg4ei32.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg4ei32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 011011-----------110-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei64.v.yaml

## Purpose

`vsoxseg4ei64.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg4ei64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 011011-----------111-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei8.v.yaml

## Purpose

`vsoxseg4ei8.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg4ei8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 011011-----------000-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg4ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei16.v.yaml

## Purpose

`vsoxseg5ei16.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg5ei16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 100011-----------101-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei32.v.yaml

## Purpose

`vsoxseg5ei32.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg5ei32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 100011-----------110-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei64.v.yaml

## Purpose

`vsoxseg5ei64.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg5ei64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 100011-----------111-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei8.v.yaml

## Purpose

`vsoxseg5ei8.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg5ei8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 100011-----------000-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg5ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei16.v.yaml

## Purpose

`vsoxseg6ei16.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg6ei16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 101011-----------101-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei32.v.yaml

## Purpose

`vsoxseg6ei32.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg6ei32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 101011-----------110-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei64.v.yaml

## Purpose

`vsoxseg6ei64.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg6ei64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 101011-----------111-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei8.v.yaml

## Purpose

`vsoxseg6ei8.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg6ei8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 101011-----------000-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg6ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei16.v.yaml

## Purpose

`vsoxseg7ei16.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg7ei16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 110011-----------101-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei32.v.yaml

## Purpose

`vsoxseg7ei32.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg7ei32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 110011-----------110-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei64.v.yaml

## Purpose

`vsoxseg7ei64.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg7ei64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 110011-----------111-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei8.v.yaml

## Purpose

`vsoxseg7ei8.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg7ei8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 110011-----------000-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg7ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei16.v.yaml

## Purpose

`vsoxseg8ei16.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg8ei16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 111011-----------101-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei32.v.yaml

## Purpose

`vsoxseg8ei32.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg8ei32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 111011-----------110-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei64.v.yaml

## Purpose

`vsoxseg8ei64.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg8ei64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 111011-----------111-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei8.v.yaml

## Purpose

`vsoxseg8ei8.v` is a compact instruction-schema entry for a RISC-V V-extension ordered indexed
segment store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vs2,
vm`, privilege/access metadata, and binary encoding bits for ifuzz generation even though this file
does not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsoxseg8ei8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vs2, vm`.

The decoder key is `encoding.match: 111011-----------000-----0100111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsoxseg8ei8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vi.yaml

## Purpose

`vsra.vi` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsra.vi` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 101001-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VADD`, `VI_VRSUB`, `VI_VAND`, `VI_VOR`,
`VI_VXOR`, `VI_VSADDU`, `VI_VSADD`, `VI_VSLL`, `VI_VSRL`, `VI_VSRA`, and 2 more; this file selects
the label matching `vsra.vi` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `signed_saturation`, `unsigned_saturation`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vv.yaml

## Purpose

`vsra.vv` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsra.vv` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 101001-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vsra.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vx.yaml

## Purpose

`vsra.vx` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsra.vx` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 101001-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VADD`, `VX_VSUB`, `VX_VRSUB`, `VX_VAND`,
`VX_VOR`, `VX_VXOR`, `VX_VSADDU`, `VX_VSADD`, `VX_VSSUBU`, `VX_VSSUB`, and 10 more; this file
selects the label matching `vsra.vx` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`,
`read_vmask`, `read_vreg`, `signed_saturation`, `unsigned_saturation`, and 1 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsra.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsrl.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsrl.vi.yaml

## Purpose

`vsrl.vi` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsrl.vi` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 101000-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VADD`, `VI_VRSUB`, `VI_VAND`, `VI_VOR`,
`VI_VXOR`, `VI_VSADDU`, `VI_VSADD`, `VI_VSLL`, `VI_VSRL`, `VI_VSRA`, and 2 more; this file selects
the label matching `vsrl.vi` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `signed_saturation`, `unsigned_saturation`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsrl.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsrl.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsrl.vv.yaml

## Purpose

`vsrl.vv` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsrl.vv` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 101000-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vsrl.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsrl.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsrl.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsrl.vx.yaml

## Purpose

`vsrl.vx` defines a RISC-V V-extension shift instruction for the ifuzz instruction generator. The
file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit fields, access
policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsrl.vx` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 101000-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VADD`, `VX_VSUB`, `VX_VRSUB`, `VX_VAND`,
`VX_VOR`, `VX_VXOR`, `VX_VSADDU`, `VX_VSADD`, `VX_VSSUBU`, `VX_VSSUB`, and 10 more; this file
selects the label matching `vsrl.vx` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`,
`read_vmask`, `read_vreg`, `signed_saturation`, `unsigned_saturation`, and 1 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsrl.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse16.v.yaml

## Purpose

`vsse16.v` defines a RISC-V V-extension strided element store instruction for the ifuzz generator.
The YAML maps the assembler form `vs3, (xs1), xs2, vm` to its opcode fields and, where present,
delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsse16.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1), xs2, vm`.

The decoder key is `encoding.match: 000010-----------101-----0100111` with variables `vm@25-25`,
`xs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_store`, `process_vssseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse32.v.yaml

## Purpose

`vsse32.v` defines a RISC-V V-extension strided element store instruction for the ifuzz generator.
The YAML maps the assembler form `vs3, (xs1), xs2, vm` to its opcode fields and, where present,
delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsse32.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1), xs2, vm`.

The decoder key is `encoding.match: 000010-----------110-----0100111` with variables `vm@25-25`,
`xs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_store`, `process_vssseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse64.v.yaml

## Purpose

`vsse64.v` defines a RISC-V V-extension strided element store instruction for the ifuzz generator.
The YAML maps the assembler form `vs3, (xs1), xs2, vm` to its opcode fields and, where present,
delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsse64.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1), xs2, vm`.

The decoder key is `encoding.match: 000010-----------111-----0100111` with variables `vm@25-25`,
`xs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_store`, `process_vssseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse8.v.yaml

## Purpose

`vsse8.v` defines a RISC-V V-extension strided element store instruction for the ifuzz generator.
The YAML maps the assembler form `vs3, (xs1), xs2, vm` to its opcode fields and, where present,
delegates behavior to the shared Sail store helpers used by the vector model.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsse8.v` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vs3, (xs1), xs2, vm`.

The decoder key is `encoding.match: 000010-----------000-----0100111` with variables `vm@25-25`,
`xs2@24-20`, `xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

Important model helper dependencies include `get_lmul_pow`, `get_num_elem`, `get_sew_pow`,
`illegal_store`, `process_vssseg`.

## Control Flow

Execution derives EEW, EMUL, element count, and field count from the encoding and current vector
type, rejects illegal store layouts, then delegates the actual memory walk to a shared helper such
as `process_vsseg`, `process_vsm`, or an indexed-store routine. The helper is responsible for mask
handling, address formation, and the architectural store side effects.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet, shared
vector memory helpers for element, mask, indexed, or segment stores. The schema is consumed with
neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand
names, and helper assumptions must remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include EEW/EMUL/nfield legality, masked memory side effects, address
calculation, and precise traps are mostly hidden behind helper calls or absent in metadata-only
entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, masked-off lanes
causing no memory write, misaligned/page-crossing addresses, segment field-count and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsse8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e16.v.yaml

## Purpose

`vsseg2e16.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg2e16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 001000-00000-----101-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e32.v.yaml

## Purpose

`vsseg2e32.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg2e32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 001000-00000-----110-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e64.v.yaml

## Purpose

`vsseg2e64.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg2e64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 001000-00000-----111-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e8.v.yaml

## Purpose

`vsseg2e8.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg2e8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 001000-00000-----000-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg2e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e16.v.yaml

## Purpose

`vsseg3e16.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg3e16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 010000-00000-----101-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e32.v.yaml

## Purpose

`vsseg3e32.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg3e32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 010000-00000-----110-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e64.v.yaml

## Purpose

`vsseg3e64.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg3e64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 010000-00000-----111-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e8.v.yaml

## Purpose

`vsseg3e8.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg3e8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 010000-00000-----000-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg3e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e16.v.yaml

## Purpose

`vsseg4e16.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg4e16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 011000-00000-----101-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e32.v.yaml

## Purpose

`vsseg4e32.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg4e32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 011000-00000-----110-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e64.v.yaml

## Purpose

`vsseg4e64.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg4e64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 011000-00000-----111-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e8.v.yaml

## Purpose

`vsseg4e8.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg4e8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 011000-00000-----000-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg4e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e16.v.yaml

## Purpose

`vsseg5e16.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg5e16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 100000-00000-----101-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e32.v.yaml

## Purpose

`vsseg5e32.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg5e32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 100000-00000-----110-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e64.v.yaml

## Purpose

`vsseg5e64.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg5e64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 100000-00000-----111-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e8.v.yaml

## Purpose

`vsseg5e8.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg5e8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 100000-00000-----000-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg5e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e16.v.yaml

## Purpose

`vsseg6e16.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg6e16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 101000-00000-----101-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e32.v.yaml

## Purpose

`vsseg6e32.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg6e32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 101000-00000-----110-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e64.v.yaml

## Purpose

`vsseg6e64.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg6e64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 101000-00000-----111-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e8.v.yaml

## Purpose

`vsseg6e8.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg6e8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 101000-00000-----000-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg6e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e16.v.yaml

## Purpose

`vsseg7e16.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg7e16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 110000-00000-----101-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e32.v.yaml

## Purpose

`vsseg7e32.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg7e32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 110000-00000-----110-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e64.v.yaml

## Purpose

`vsseg7e64.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg7e64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 110000-00000-----111-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e8.v.yaml

## Purpose

`vsseg7e8.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg7e8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 110000-00000-----000-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg7e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e16.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e16.v.yaml

## Purpose

`vsseg8e16.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg8e16.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 111000-00000-----101-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e16.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e32.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e32.v.yaml

## Purpose

`vsseg8e32.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg8e32.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 111000-00000-----110-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e32.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e64.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e64.v.yaml

## Purpose

`vsseg8e64.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg8e64.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 111000-00000-----111-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e64.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e8.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e8.v.yaml

## Purpose

`vsseg8e8.v` is a compact instruction-schema entry for a RISC-V V-extension unit-stride segment
store metadata form. It preserves the assembler spelling, operand order `vs3, (xs1), vm`,
privilege/access metadata, and binary encoding bits for ifuzz generation even though this file does
not include executable operation semantics.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vsseg8e8.v` with `kind:
instruction`, `definedBy.extension.name: V`, and assembly `vs3, (xs1), vm`.

The decoder key is `encoding.match: 111000-00000-----000-----0100111` with variables `vm@25-25`,
`xs1@19-15`, `vs3@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The `operation()` block is empty, so the file contributes declarative instruction metadata rather
than a local executable model body.

## Control Flow

There is no local control-flow model in this file. Downstream ifuzz tooling consumes the YAML as
declarative instruction metadata; execution semantics must come from a shared model, a generated
decoder table, or another schema entry for the same store family.

## State and Persistence Behavior

The YAML itself is static metadata. At modeled execution time the instruction reads vector
registers, scalar address registers, mask state, and vector CSRs, then persists its architectural
effect through memory stores. Store ordering, masking, and exception behavior are delegated to
shared vector memory helpers.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, shared vector memory helpers for element,
mask, indexed, or segment stores. The schema is consumed with neighboring V-extension YAMLs in
`pkg/ifuzz/riscv64/gen/inst/V`, so duplicate encodings, operand names, and helper assumptions must
remain consistent across the generated instruction set.

## Risks and Edge Cases

Risks and edge cases include the empty `operation()` block means semantic coverage depends on
external shared definitions or decoder-only use; EEW/EMUL/nfield legality, masked memory side
effects, address calculation, and precise traps are mostly hidden behind helper calls or absent in
metadata-only entries.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic,
masked-off lanes causing no memory write, misaligned/page-crossing addresses, segment field-count
and EEW variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vsseg8e8.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssra.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssra.vi.yaml

## Purpose

`vssra.vi` defines a RISC-V V-extension rounding shift instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vssra.vi` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 101011-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VADD`, `VI_VRSUB`, `VI_VAND`, `VI_VOR`,
`VI_VXOR`, `VI_VSADDU`, `VI_VSADD`, `VI_VSLL`, `VI_VSRL`, `VI_VSRA`, and 2 more; this file selects
the label matching `vssra.vi` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `signed_saturation`, `unsigned_saturation`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssra.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssra.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssra.vv.yaml

## Purpose

`vssra.vv` defines a RISC-V V-extension rounding shift instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vssra.vv` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 101011-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vssra.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssra.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssra.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssra.vx.yaml

## Purpose

`vssra.vx` defines a RISC-V V-extension rounding shift instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, xs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vssra.vx` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, xs1, vm`.

The decoder key is `encoding.match: 101011-----------100-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `xs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VX_VADD`, `VX_VSUB`, `VX_VRSUB`, `VX_VAND`,
`VX_VOR`, `VX_VXOR`, `VX_VSADDU`, `VX_VSADD`, `VX_VSSUBU`, `VX_VSSUB`, and 10 more; this file
selects the label matching `vssra.vx` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_scalar`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`,
`read_vmask`, `read_vreg`, `signed_saturation`, `unsigned_saturation`, and 1 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssra.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssrl.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssrl.vi.yaml

## Purpose

`vssrl.vi` defines a RISC-V V-extension rounding shift instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, imm, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vssrl.vi` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, imm, vm`.

The decoder key is `encoding.match: 101010-----------011-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `imm@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VI_VADD`, `VI_VRSUB`, `VI_VAND`, `VI_VOR`,
`VI_VXOR`, `VI_VSADDU`, `VI_VSADD`, `VI_VSLL`, `VI_VSRL`, `VI_VSRA`, and 2 more; this file selects
the label matching `vssrl.vi` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_shift_amount`, `illegal_normal`, `init_masked_result`, `read_vmask`,
`read_vreg`, `signed_saturation`, `unsigned_saturation`, `write_vreg`.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssrl.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssrl.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssrl.vv.yaml

## Purpose

`vssrl.vv` defines a RISC-V V-extension rounding shift instruction for the ifuzz instruction
generator. The file binds the assembler form `vd, vs2, vs1, vm` to an opcode pattern, operand bit
fields, access policy, and Sail semantics used to model vector execution.

## Important APIs, Types, and Functions

The exported schema object is the YAML instruction record named `vssrl.vv` with `kind: instruction`,
`definedBy.extension.name: V`, and assembly `vd, vs2, vs1, vm`.

The decoder key is `encoding.match: 101010-----------000-----1010111` with variables `vm@25-25`,
`vs2@24-20`, `vs1@19-15`, `vd@11-7`.

Access metadata marks `s=always`, `u=always`, `vs=always`, `vu=always` and `data_independent_timing`
is `False`.

The embedded Sail block dispatches over `funct6` labels `VV_VADD`, `VV_VSUB`, `VV_VAND`, `VV_VOR`,
`VV_VXOR`, `VV_VSADDU`, `VV_VSADD`, `VV_VSSUBU`, `VV_VSSUB`, `VV_VSMUL`, and 11 more; this file
selects the label matching `vssrl.vv` through the fixed encoding pattern.

Important model helper dependencies include `get_fixed_rounding_incr`, `get_lmul_pow`,
`get_num_elem`, `get_sew`, `get_sew_pow`, `get_shift_amount`, `get_vlen_pow`, `illegal_normal`,
`init_masked_result`, `read_vmask`, `read_vreg`, `signed_saturation`, and 2 more.

## Control Flow

The Sail body computes active vector shape from `vtype` state, performs legality checks, reads masks
and operands, initializes inactive/tail destination elements, updates active lanes, writes the
destination or memory side effect, clears `vstart`, and returns `RETIRE_SUCCESS`. The per-lane
operation is selected by a `funct6` match arm shared with related vector arithmetic encodings, so
this YAML's fixed opcode bits are what bind the generic Sail block to the specific instruction
mnemonic.

## State and Persistence Behavior

The file is static generator input. The Sail semantics read current vector CSRs and source
registers, preserve inactive/tail elements according to `init_masked_result`, write the vector
destination register, and reset `vstart` to zero on successful retirement. No host-side persistence
is performed.

## Dependencies and Integration Points

Integration points are `inst_schema.json#`, the RISC-V V extension instruction generator, the
decoder/assembler tables built from `encoding.match`, the embedded RISCV Sail model snippet. The
schema is consumed with neighboring V-extension YAMLs in `pkg/ifuzz/riscv64/gen/inst/V`, so
duplicate encodings, operand names, and helper assumptions must remain consistent across the
generated instruction set.

## Risks and Edge Cases

Risks and edge cases include shift amount masking, arithmetic sign fill, and rounding increment
rules are width-dependent.

## Test Signals

Useful test signals are schema validation against `schemas/inst_schema.json`, decoder round-trips
from assembly operands to the declared match pattern, ifuzz generation including this mnemonic, Sail
execution traces for masked and unmasked lanes across SEW/LMUL combinations, shift amounts above
SEW, signed high-bit inputs, rounding increment cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/V/vssrl.vv.yaml -->
