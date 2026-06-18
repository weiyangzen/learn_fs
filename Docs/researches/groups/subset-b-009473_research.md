<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vv.yaml

## Purpose
`vwsll.vv.yaml` is a riscv-unified-db instruction descriptor for the `Zvbb` vector bit-manipulation instruction `vwsll.vv`. It describes the vector-vector widening shift-left logical form with assembly operands `vd, vs2, vs1, vm`.

## Important APIs, Types, And Functions
The file is declarative input for `pkg/ifuzz/riscv64/gen/gen.go`. The consumed API surface is `kind: instruction`, `name`, `encoding.match`, `encoding.variables`, and `access.u`/`access.vu`. Its 32-bit match string is `110101-----------000-----1010111`; variable fields are `vm` bit 25, `vs2` bits 24-20, `vs1` bits 19-15, and `vd` bits 11-7.

## Control Flow, State, Dependencies, Risks, And Tests
Generation discovers the YAML through `filepath.WalkDir`, unmarshals it with `gopkg.in/yaml.v3`, converts the fixed bits into an opcode/mask, and emits one `riscv64.Insn` if the match has exactly 32 characters and all locations parse as `hi-lo` ranges. The descriptor has no runtime state; its persisted effect is one generated table entry with `AsUInt32` equal to the opcode and `Priv` false because U/VU access is allowed. It integrates with `riscv64.Register`, `ParseInsn`, and generic ifuzz tests through the generated package import. Risks are mostly schema loss: extension gating, `data_independent_timing: true`, and the empty `operation()` block are not preserved by the generator. Test signals should assert generated presence, field order, mask/opcode matching, and decode round trips for randomized variable fields.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vx.yaml

## Purpose
`vwsll.vx.yaml` describes the `Zvbb` vector-scalar widening shift-left logical instruction `vwsll.vx`. Its assembly form is `vd, vs2, xs1, vm`, so it pairs a vector source with an integer scalar shift operand.

## Important APIs, Types, And Functions
The descriptor feeds the same `instYAML` path as other RISC-V YAML files. The generator consumes the instruction name, 32-bit match string `110101-----------100-----1010111`, and variables `vm` at bit 25, `vs2` at bits 24-20, `xs1` at bits 19-15, and `vd` at bits 11-7. Access is allowed in S/U/VS/VU modes.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` walks this file, parses fixed `1`/`0` bits into `OpcodeMask`/`Opcode`, expands variable locations into `InsnField` entries, and serializes the resulting `Insn` into `generated/insns.go`. The YAML itself has no mutable state or persistence beyond that generated descriptor. Runtime integration is through global RISC-V registration and `ParseInsn` scanning templates by mask. The important risk is operand-shape correctness: a mistaken `xs1` field would make the scalar form collide semantically with `vwsll.vv`, even though decode would still match an opcode. The generator also ignores `data_independent_timing` and the empty operation body. Tests should compare the `.vx` opcode against the `.vv` form, verify the `xs1` field name and position, and confirm fixed bits survive encode/decode.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbb/vwsll.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vv.yaml

## Purpose
`vclmul.vv.yaml` describes the `Zvbc` vector carry-less multiply instruction in vector-vector form. It gives ifuzz a descriptor for generating and decoding the base low-part polynomial multiply opcode.

## Important APIs, Types, And Functions
The consumed fields are `kind: instruction`, `name: vclmul.vv`, assembly `vd, vs2, vs1, vm`, match `001100-----------010-----1010111`, and variables `vm`, `vs2`, `vs1`, and `vd`. The file marks all privilege modes as `always` and declares data-independent timing, but the current generator uses only U/VU access for `Priv`.

## Control Flow, State, Dependencies, Risks, And Tests
During generation, the 32-bit match contributes fixed opcode bits while each YAML location becomes one `riscv64.InsnField`. The descriptor persists only via the generated `Insn` table; there is no direct runtime state. It integrates with vector-crypto descriptors near the tail of `generated/insns.go`, with `Register` appending the table to the `iset` registry. Risks include loss of crypto-extension metadata, no semantic validation from the empty `operation()` block, and possible decode ambiguity if future descriptors share the same fixed mask. Tests should verify that `vclmul.vv` appears with `OpcodeMask` derived from the fixed match bits, that `vm` is a one-bit field, and that `ParseInsn` recognizes representative encodings without confusing it with `vclmulh.vv`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vx.yaml

## Purpose
`vclmul.vx.yaml` is the `Zvbc` vector-scalar carry-less multiply descriptor. Its assembly `vd, vs2, xs1, vm` distinguishes it from the vector-vector form by using an integer scalar operand.

## Important APIs, Types, And Functions
The descriptor is consumed by the RISC-V generator as data. Its fixed match is `001100-----------110-----1010111`; declared variable ranges are `vm` 25-25, `vs2` 24-20, `xs1` 19-15, and `vd` 11-7. `data_independent_timing` is true, and S/U/VS/VU access is always allowed.

## Control Flow, State, Dependencies, Risks, And Tests
Generation turns the match pattern into a mask/opcode pair and serializes an `Insn` with these fields into `generated/insns.go`. Runtime decode then depends on the generated template order and `(value & OpcodeMask) == Opcode`. The YAML has no local state; persistence is generated Go source. Dependencies are the unified-db schema, YAML unmarshalling, the `serializer` package, and the `riscv64.Insn` type. Risks center on scalar field naming, ignored extension constraints, and empty semantic text. Test signals should include generated-table checks for `xs1`, `.vx`/.`vv` opcode separation, and decode samples that vary `vm`, `vs2`, `xs1`, and `vd` while preserving fixed bits.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmul.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vv.yaml

## Purpose
`vclmulh.vv.yaml` describes the high-part vector-vector carry-less multiply instruction from `Zvbc`. It complements `vclmul.vv` by selecting the high result half through different fixed opcode bits.

## Important APIs, Types, And Functions
The key consumed fields are `name: vclmulh.vv`, assembly `vd, vs2, vs1, vm`, match `001101-----------010-----1010111`, and variables `vm`, `vs2`, `vs1`, and `vd` with standard vector arithmetic positions. Access modes are all `always`.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` treats this as a valid 32-bit instruction, builds mask/opcode values, parses each `hi-lo` location into `InsnField`, and writes an `Insn` literal. There is no runtime state in the YAML; generated registration is the only persistent behavior. Integration is with the RISC-V generated package, `riscv64.ParseInsn`, and generic ifuzz decode checks. The main risks are collision with `vclmul.vv` if the high/low fixed bits drift, ignored semantic and extension data, and lack of operand constraints beyond raw bit extraction. Tests should assert separate generated opcodes for `vclmul` and `vclmulh`, correct field order, and successful decode of representative high-part encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vx.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vx.yaml

## Purpose
`vclmulh.vx.yaml` is the vector-scalar high-part carry-less multiply descriptor for `Zvbc`. It exposes the scalar `xs1` operand variant to the RISC-V ifuzz table.

## Important APIs, Types, And Functions
The generator consumes match `001101-----------110-----1010111` and variables `vm` bit 25, `vs2` bits 24-20, `xs1` bits 19-15, and `vd` bits 11-7. Its access block keeps it non-privileged for ifuzz purposes.

## Control Flow, State, Dependencies, Risks, And Tests
The descriptor is read, unmarshaled, validated for 32-bit match length, and converted into an `Insn` literal with fixed mask/opcode and variable fields. Runtime behavior is indirect through generated registration; `Encode` emits `AsUInt32`, while parsing extracts operands by `extractBits`. Risks include the generator ignoring architecture-level scalar/vector constraints, data-independent timing, and future schema fields, plus decode ambiguity if masks overlap. Tests should cover presence in `generated/insns.go`, the `xs1` field, high-vs-low opcode distinction, and parse/encode stability for values that vary each declared operand bitfield.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvbc/vclmulh.vx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfncvtbf16.f.f.w.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfncvtbf16.f.f.w.yaml

## Purpose
`vfncvtbf16.f.f.w.yaml` describes the `Zvfbfmin` narrowing conversion from wider floating-point vector elements to bfloat16. It gives ifuzz coverage for the BF16 vector conversion opcode.

## Important APIs, Types, And Functions
The descriptor has assembly `vd, vs2, vm`, match `010010------11101001-----1010111`, and variables `vm` at bit 25, `vs2` at bits 24-20, and `vd` at bits 11-7. Unlike the crypto integer descriptors, it marks `data_independent_timing: false`, although this is not emitted into generated Go.

## Control Flow, State, Dependencies, Risks, And Tests
Generation accepts the 32-bit match, converts fixed bits to `OpcodeMask`/`Opcode`, and writes an `Insn` with three fields. The source has no state; its persistent footprint is the generated descriptor and registration side effect. Dependencies include the riscv-unified-db schema and the RISC-V generator. Risks include ignored floating-point rounding/exception semantics, ignored timing metadata, and no semantic `operation()` content for future differential tests. Tests should verify the generated entry has mask `4228903039` shape for OPFVF unary-style encodings, includes only `vm`, `vs2`, and `vd`, and decodes representative BF16 narrowing opcodes without colliding with other `vfncvt.*` forms.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfncvtbf16.f.f.w.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfwcvtbf16.f.f.v.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfwcvtbf16.f.f.v.yaml

## Purpose
`vfwcvtbf16.f.f.v.yaml` describes the `Zvfbfmin` widening conversion from bfloat16 vector elements to wider floating-point elements. It is the widening counterpart to the BF16 narrowing descriptor.

## Important APIs, Types, And Functions
The generator consumes `name: vfwcvtbf16.f.f.v`, assembly `vd, vs2, vm`, fixed match `010010------01101001-----1010111`, and variables `vm`, `vs2`, and `vd`. Access is allowed for S/U/VS/VU, so the generated entry is non-privileged.

## Control Flow, State, Dependencies, Risks, And Tests
The file enters the RISC-V table through `WalkDir`, YAML unmarshalling, `buildInsn`, and serialization. No local state exists; generated Go is the durable output. It integrates with `generated/insns.go`, `riscv64.Register`, `ParseInsn`, and tests that decode registered RISC-V instructions. Risks are similar to other data descriptors: BF16 semantic details, floating-point status effects, and `data_independent_timing: false` are not represented in `Insn`. The fixed bits must stay distinct from the generic `vfwcvt.f.f.v`. Tests should assert generated presence, three-field layout, opcode separation from non-BF16 conversion descriptors, and decode stability across operand bit variations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfmin/vfwcvtbf16.f.f.v.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vf.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vf.yaml

## Purpose
`vfwmaccbf16.vf.yaml` describes the `Zvfbfwma` vector-scalar widening fused multiply-accumulate instruction using bfloat16 inputs. It introduces a floating scalar operand `fs1`.

## Important APIs, Types, And Functions
The descriptor declares assembly `vd, fs1, vs2, vm`, match `111011-----------101-----1010111`, and fields `vm` 25-25, `vs2` 24-20, `fs1` 19-15, and `vd` 11-7. Its access block makes the generated instruction non-privileged.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` turns this descriptor into an `Insn` with a fixed mask/opcode and four operand fields. Runtime integration is via generated registration and template matching in `ParseInsn`; encoding emits the fixed representative opcode because generated descriptors have `Generator: nil`. The YAML carries no mutable state. Risks include lost floating-point accumulation semantics, rounding/status behavior, BF16 extension requirements, and the difference between scalar `fs1` and vector `vs1` variants. Tests should compare `.vf` against `.vv`, verify the `fs1` field name, and ensure parse/decode coverage for representative BF16 WMA encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vv.yaml

## Purpose
`vfwmaccbf16.vv.yaml` describes the vector-vector BF16 widening fused multiply-accumulate instruction from `Zvfbfwma`. It is the all-vector companion of the `.vf` descriptor.

## Important APIs, Types, And Functions
The generator reads match `111011-----------001-----1010111` and variables `vm`, `vs2`, `vs1`, and `vd`. Assembly is `vd, vs1, vs2, vm`; the variable list orders `vs2` before `vs1` according to encoding position, which is the order persisted into `Insn.Fields`.

## Control Flow, State, Dependencies, Risks, And Tests
The descriptor is converted by `buildInsn` into a static generated `Insn`. There is no state beyond generated Go source and init-time registration into `iset.Arches`. Dependencies are unified-db YAML, `yaml.v3`, `serializer`, and the RISC-V runtime descriptor types. Risks include operand-order confusion between assembly order and bitfield order, ignored BF16 arithmetic semantics, and no generated randomization of operands beyond the fixed opcode template. Tests should verify field order, opcode distinction from `.vf`, non-privileged registration, and decode results for encodings with varied `vm`, `vs2`, `vs1`, and `vd`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvfbfwma/vfwmaccbf16.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vghsh.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vghsh.vv.yaml

## Purpose
`vghsh.vv.yaml` describes the `Zvkg` vector GHASH instruction. It provides ifuzz with a vector-vector crypto descriptor for GHASH state update style operations.

## Important APIs, Types, And Functions
The descriptor declares assembly `vd, vs2, vs1`, match `1011001----------010-----1110111`, and fields `vs2` 24-20, `vs1` 19-15, and `vd` 11-7. There is no `vm` variable in this encoding. Access is always allowed in S/U/VS/VU, and `data_independent_timing` is true.

## Control Flow, State, Dependencies, Risks, And Tests
Generation builds a static descriptor with `OpcodeMask` reflecting the fixed vector-crypto opcode and fields for the three vector registers. Runtime state is limited to the registered generated table. Integration points are `generated/insns.go`, `riscv64.Register`, and `ParseInsn`. Risks include missing crypto semantic modeling, no enforcement of vector element group constraints, and the generator ignoring extension grouping and timing metadata. Tests should assert absence of `vm`, correct field names and lengths, generated opcode/mask stability, and decode separation from `vgmul.vv`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vghsh.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vgmul.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vgmul.vv.yaml

## Purpose
`vgmul.vv.yaml` describes the `Zvkg` vector GCM multiply instruction. It is a compact two-operand vector crypto descriptor with assembly `vd, vs2`.

## Important APIs, Types, And Functions
The fixed match is `1010001-----10001010-----1110111`. Variables are only `vs2` at bits 24-20 and `vd` at bits 11-7; bits 19-15 and other fields are fixed by the match. Access is unrestricted for the generator's privilege model.

## Control Flow, State, Dependencies, Risks, And Tests
The RISC-V generator emits one `Insn` if the 32-character match and two variable ranges parse successfully. The YAML has no state; it persists as a generated Go descriptor. At runtime, `ParseInsn` extracts only `vs2` and `vd` from matched values. Risks include accidental introduction of a variable where the architecture reserves fixed bits, ignored crypto operation semantics, and decode-order sensitivity if another descriptor overlaps the mask. Tests should verify exactly two fields, fixed reserved bits, generated presence, and successful decode of the representative opcode in the generated table.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkg/vgmul.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vs.yaml

## Purpose
`vaesdf.vs.yaml` describes the `Zvkned` vector AES decrypt final round in vector-scalar-group style form. Its assembly lists `vd, vs2`, with remaining selector bits fixed.

## Important APIs, Types, And Functions
The descriptor uses match `1010011-----00001010-----1110111` and variables `vs2` 24-20 and `vd` 11-7. It has unrestricted access and data-independent timing metadata.

## Control Flow, State, Dependencies, Risks, And Tests
Generation parses the descriptor into a two-field static `Insn`; no YAML state exists after generation. It integrates with the generated RISC-V package and the runtime mask-matching parser. Risks are primarily semantic loss: final-round AES behavior, vector grouping constraints, and timing flags are not emitted. Because many AES descriptors differ only in fixed bits, mask/opcode drift can silently decode as the wrong round form. Tests should compare `.vs` and `.vv` AES decrypt-final entries, confirm two-field layout, and decode representative opcodes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vv.yaml

## Purpose
`vaesdf.vv.yaml` describes the `Zvkned` vector AES decrypt final round vector-vector encoding. It sits beside the `.vs` form with a different fixed opcode prefix.

## Important APIs, Types, And Functions
The file declares match `1010001-----00001010-----1110111`, variables `vs2` and `vd`, and S/U/VS/VU access as `always`. Its operation block is empty, so the generator only persists encoding metadata.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` accepts the file as a 32-bit instruction and emits an `Insn` that `Register` later installs globally. There is no local persistence beyond generated Go. Dependencies are YAML unmarshalling, unified-db schema conventions, and the RISC-V ifuzz runtime. Risks include `.vv`/`.vs` confusion, loss of AES final-round semantics, and no validation of architectural operand restrictions. Tests should assert generated presence, correct two-register field list, opcode difference from `vaesdf.vs`, and successful `ParseInsn` extraction of `vs2`/`vd`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdf.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vs.yaml

## Purpose
`vaesdm.vs.yaml` describes the `Zvkned` vector AES decrypt middle-round instruction in `.vs` form. It contributes one AES decrypt-middle opcode to the generated RISC-V table.

## Important APIs, Types, And Functions
The match string is `1010011-----00000010-----1110111`; variables are `vs2` bits 24-20 and `vd` bits 11-7. Access is allowed in all listed privilege modes and data-independent timing is true.

## Control Flow, State, Dependencies, Risks, And Tests
The descriptor is parsed by `gen.go`, serialized into `generated/insns.go`, and consumed at runtime by `ParseInsn` through mask matching. It has no own state or persistence. Integration depends on the generated package being imported so `init` calls `Register`. Risks include middle-vs-final round fixed-bit mistakes, ignored AES semantic details, and no generated operand legality checks. Test signals should include opcode comparison with `vaesdf.vs`, `.vv`/`.vs` separation, generated field count checks, and representative decode samples.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vv.yaml

## Purpose
`vaesdm.vv.yaml` describes the vector-vector AES decrypt middle round from `Zvkned`.

## Important APIs, Types, And Functions
The consumed encoding is `1010001-----00000010-----1110111`, with variables `vs2` 24-20 and `vd` 11-7. The descriptor is non-privileged under the generator because U/VU access is not `never`.

## Control Flow, State, Dependencies, Risks, And Tests
The generation path walks, unmarshals, validates, builds, and serializes this descriptor into an `Insn` literal. Runtime decode scans the generated templates and extracts the two operands with `extractBits`. There is no state in the YAML itself. Risks include overlap with neighboring AES descriptors, loss of timing and extension metadata, and no operation semantics for deeper validation. Tests should verify table presence, correct opcode/mask values, decode separation from decrypt-final/encrypt-middle entries, and stable operand extraction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesdm.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vs.yaml

## Purpose
`vaesef.vs.yaml` describes the `Zvkned` vector AES encrypt final round in `.vs` form.

## Important APIs, Types, And Functions
It defines match `1010011-----00011010-----1110111` and variables `vs2` 24-20 and `vd` 11-7. The generator also sees `name: vaesef.vs`, `kind: instruction`, and always-allowed U/VU access.

## Control Flow, State, Dependencies, Risks, And Tests
Generation converts the fixed bits to `OpcodeMask`/`Opcode` and writes a generated two-field `Insn`. Runtime behavior comes from registration and mask-based parsing; the YAML has no mutable state. Dependencies include unified-db YAML shape, `yaml.v3`, and the RISC-V ifuzz runtime. Risks include confusion between encrypt/decrypt and final/middle fixed-bit groups, ignored AES semantics, and absence of vector legality constraints. Tests should compare against `vaesem.vs` and `vaesdf.vs`, assert exact field layout, and run decode checks for representative encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vv.yaml

## Purpose
`vaesef.vv.yaml` describes the vector-vector AES encrypt final round descriptor from `Zvkned`.

## Important APIs, Types, And Functions
The relevant encoding data is match `1010001-----00011010-----1110111`, variables `vs2` and `vd`, and all access modes `always`. The empty operation block is not consumed by the current generator.

## Control Flow, State, Dependencies, Risks, And Tests
The file becomes a static `Insn` after the generator walks and parses it; registration then places the generated descriptor set under `iset.ArchRiscv64`. It has no standalone state. Risks include subtle fixed-bit drift among AES forms, ignored semantic metadata, and no operand constraints beyond raw register fields. Test signals should include generated presence, two-field decode extraction, `.vv`/`.vs` opcode difference, and parse coverage alongside `vaesem.vv`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesef.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vs.yaml

## Purpose
`vaesem.vs.yaml` describes the `Zvkned` vector AES encrypt middle round in `.vs` form.

## Important APIs, Types, And Functions
The file provides match `1010011-----00010010-----1110111`, fields `vs2` 24-20 and `vd` 11-7, and access metadata that maps to non-privileged generated output.

## Control Flow, State, Dependencies, Risks, And Tests
`gen.go` uses the YAML to emit one generated `Insn`; the descriptor has no runtime state except generated registration. Its integration points are the generated table, `riscv64.ParseInsn`, and generic ifuzz decode tests. Risks include wrong AES round classification due to fixed-bit mistakes, ignored data-independent timing, and absent semantic checks. Tests should verify the generated `vaesem.vs` entry is distinct from `vaesef.vs` and `vaesdm.vs`, contains exactly `vs2` and `vd`, and decodes representative values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vv.yaml

## Purpose
`vaesem.vv.yaml` describes the vector-vector AES encrypt middle round for `Zvkned`.

## Important APIs, Types, And Functions
It has match `1010001-----00010010-----1110111` and variable ranges for `vs2` and `vd`. The YAML name and `kind` drive generated instruction naming and inclusion.

## Control Flow, State, Dependencies, Risks, And Tests
The descriptor is read by the generator, serialized into `generated/insns.go`, and consumed through init-time registration. No local state persists. The important dependency is the simple 32-bit match parser, which rejects non-`0`/`1`/`-` characters and malformed ranges. Risks include overlap with other AES descriptors and missing semantic validation. Tests should check generated table presence, opcode separation from final/decrypt forms, operand extraction, and decode consistency.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesem.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf1.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf1.vi.yaml

## Purpose
`vaeskf1.vi.yaml` describes the `Zvkned` AES key-schedule helper form with an immediate operand. It contributes the first key-schedule descriptor to ifuzz.

## Important APIs, Types, And Functions
The assembly is `vd, vs2, imm`, match `1000101----------010-----1110111`, and variables are `vs2` 24-20, `imm` 19-15, and `vd` 11-7. Access is unrestricted for generated privilege classification.

## Control Flow, State, Dependencies, Risks, And Tests
The generator parses the immediate field as a normal five-bit `InsnField`; it does not model valid round ranges. Runtime parse extracts `vs2`, `imm`, and `vd` from any matching value. State is limited to generated Go source and global registration. Risks include invalid immediate values being fuzzed, ignored AES key-schedule semantics, and possible confusion with `vaeskf2.vi`. Tests should assert field names, immediate width, opcode separation from `vaeskf2.vi`, and representative decode behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf1.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf2.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf2.vi.yaml

## Purpose
`vaeskf2.vi.yaml` describes the second `Zvkned` AES key-schedule immediate descriptor.

## Important APIs, Types, And Functions
The descriptor uses match `1010101----------010-----1110111`, variables `vs2`, `imm`, and `vd`, and assembly `vd, vs2, imm`. The generator emits `imm` as a five-bit operand field.

## Control Flow, State, Dependencies, Risks, And Tests
The file follows the normal YAML-to-`Insn` path and has no independent runtime state. It integrates through the generated descriptor table and `ParseInsn`. Risks are invalid immediate generation, ignored key-schedule round semantics, and fixed-bit confusion with `vaeskf1.vi`. Tests should verify generated presence, field order, immediate extraction, and opcode difference between the two key-schedule forms.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaeskf2.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesz.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesz.vs.yaml

## Purpose
`vaesz.vs.yaml` describes `vaesz.vs`, the `Zvkned` vector AES round-zero instruction. Its long name explicitly identifies it as "Vector AES round zero".

## Important APIs, Types, And Functions
The descriptor provides match `1010011-----00111010-----1110111`, variables `vs2` and `vd`, and always-allowed access modes. It is a two-field descriptor like many AES round forms.

## Control Flow, State, Dependencies, Risks, And Tests
Generation serializes this YAML into a generated `Insn`; runtime registration and parsing are inherited from the RISC-V backend. The file has no local state. Risks include fixed-bit overlap with other AES `.vs` forms, ignored AES round-zero semantics, and no operation snippet to compare against architecture behavior. Tests should assert the generated entry exists with only `vs2` and `vd`, is distinct from decrypt/encrypt final/middle forms, and decodes representative round-zero opcodes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvkned/vaesz.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ch.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ch.vv.yaml

## Purpose
`vsha2ch.vv.yaml` describes the `Zvknha` SHA-2 choose helper instruction in vector-vector form.

## Important APIs, Types, And Functions
The file declares assembly `vd, vs2, vs1`, match `1011101----------010-----1110111`, and variables `vs2`, `vs1`, and `vd`. There is no mask field. Access modes are all `always`.

## Control Flow, State, Dependencies, Risks, And Tests
The generator emits a three-field `Insn` and the runtime parser later extracts operands by bit ranges. The YAML has no persistence beyond generated source. Integration is through the generated RISC-V package and `iset` registration. Risks include lack of SHA-2 semantic modeling, no vector shape constraints, and confusion with `vsha2cl.vv` or `vsha2ms.vv` if fixed bits drift. Tests should verify field layout, generated opcode/mask, and decode separation across the three SHA-2 helpers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ch.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2cl.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2cl.vv.yaml

## Purpose
`vsha2cl.vv.yaml` describes the `Zvknha` SHA-2 choose/low companion helper in vector-vector form.

## Important APIs, Types, And Functions
The consumed match is `1011111----------010-----1110111`; variables are `vs2` 24-20, `vs1` 19-15, and `vd` 11-7. The descriptor is non-privileged and marked data-independent timing.

## Control Flow, State, Dependencies, Risks, And Tests
Generation creates a static descriptor; runtime integration is through generated registration and mask matching. No local state persists. Risks are fixed-bit mixups among SHA-2 helpers, ignored timing/extension metadata, and no semantic validation. Tests should assert correct three-register fields, opcode separation from `vsha2ch.vv`, and decode of representative encodings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2cl.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ms.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ms.vv.yaml

## Purpose
`vsha2ms.vv.yaml` describes the `Zvknha` SHA-2 message-schedule helper instruction.

## Important APIs, Types, And Functions
Its assembly is `vd, vs2, vs1`, fixed match `1011011----------010-----1110111`, and variables are `vs2`, `vs1`, and `vd`. Access is all modes `always`.

## Control Flow, State, Dependencies, Risks, And Tests
The file is converted into a generated `Insn` with three operand fields. Runtime decode uses the generated template; there is no YAML state. Dependencies are the RISC-V generator and runtime descriptor package. Risks include absent SHA schedule semantics, no element-width constraints, and overlap with other SHA helper masks. Tests should check generated presence, field order, opcode distinction from `vsha2ch`/`vsha2cl`, and parse extraction of all three fields.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvknha/vsha2ms.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3c.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3c.vi.yaml

## Purpose
`vsm3c.vi.yaml` describes an SM3 compression helper instruction. Although it lives under `gen/inst/Zvks`, its `definedBy` extension is `Zvksh`.

## Important APIs, Types, And Functions
The descriptor uses assembly `vd, vs2, imm`, match `1010111----------010-----1110111`, and variables `vs2` 24-20, `imm` 19-15, and `vd` 11-7.

## Control Flow, State, Dependencies, Risks, And Tests
Generation treats the immediate as an unconstrained five-bit `InsnField` and emits a static descriptor. The file has no state apart from generated Go output and registration. Integration is with the vector crypto tail of `generated/insns.go`. Risks include directory/extension naming mismatch, ignored SM3 immediate validity constraints, and absent semantic operation data. Tests should assert generated field layout, immediate extraction, non-privileged classification, and decode separation from SM4 key and SM3 message expansion descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3c.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3me.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3me.vv.yaml

## Purpose
`vsm3me.vv.yaml` describes the SM3 message-expansion helper. It is also defined by `Zvksh` while stored under the `Zvks` descriptor directory.

## Important APIs, Types, And Functions
The match is `1000001----------010-----1110111`, with variables `vs2`, `vs1`, and `vd`. Assembly is `vd, vs2, vs1`.

## Control Flow, State, Dependencies, Risks, And Tests
The RISC-V generator emits one three-field descriptor and the runtime parser later extracts all three register operands. No state exists in the YAML. Risks include extension-directory mismatch for tooling that assumes path equals `definedBy`, ignored SM3 semantics, and no operand legality checking. Tests should cover generated presence, field order, opcode difference from `vsm3c.vi`, and decode round trips.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm3me.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4k.vi.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4k.vi.yaml

## Purpose
`vsm4k.vi.yaml` describes the SM4 key-schedule helper instruction. It is defined by `Zvksed` and uses an immediate operand.

## Important APIs, Types, And Functions
The match string is `1000011----------010-----1110111`; variables are `vs2` 24-20, `imm` 19-15, and `vd` 11-7. Access is all modes `always`.

## Control Flow, State, Dependencies, Risks, And Tests
Generation emits a static `Insn` with an unconstrained five-bit immediate. Runtime integration is through the generated table and RISC-V mask matching. The YAML has no local state. Risks include invalid immediate values, ignored SM4 key-schedule semantics, and extension metadata not surviving into generated descriptors. Tests should verify field names, immediate width, generated opcode, and separation from `vsm4r` round descriptors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4k.vi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vs.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vs.yaml

## Purpose
`vsm4r.vs.yaml` describes an SM4 round instruction in `.vs` form, defined by `Zvksed`.

## Important APIs, Types, And Functions
The descriptor provides match `1010011-----10000010-----1110111` and variables `vs2` and `vd`. The generator uses these to create a two-field non-privileged `Insn`.

## Control Flow, State, Dependencies, Risks, And Tests
The file follows the standard YAML generation path and has no independent state. Runtime decode is mask-based after generated registration. Risks include `.vs`/`.vv` opcode confusion, ignored SM4 semantic constraints, and loss of extension metadata. Tests should assert correct two-field layout, opcode difference from `vsm4r.vv`, and successful representative decode.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vv.yaml -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vv.yaml

## Purpose
`vsm4r.vv.yaml` describes the SM4 round instruction in vector-vector form. Its `definedBy` uses `anyOf` with `Zvks` and `Zvksed`.

## Important APIs, Types, And Functions
The consumed encoding is match `1010001-----10000010-----1110111`, variables `vs2` and `vd`, and all access modes `always`. The current generator does not model the `anyOf` extension expression.

## Control Flow, State, Dependencies, Risks, And Tests
Generation serializes this as a normal two-field descriptor; runtime integration is generated registration plus `ParseInsn`. The source has no state. Risks include losing the `anyOf` extension relationship, `.vv`/`.vs` fixed-bit mixups, and no SM4 semantic validation. Tests should check generated presence, two-field layout, opcode distinction from `vsm4r.vs`, and decode coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/gen/inst/Zvks/vsm4r.vv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/empty.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/empty.go

## Purpose
`empty.go` is a minimal placeholder package file for `pkg/ifuzz/riscv64/generated`. Its comment says it exists to keep builds working when `insns.go` is excluded by build tags.

## Important APIs, Types, And Functions
The file declares only `package generated` and no functions, variables, or types. It contains the normal syzkaller copyright header and no build tag of its own.

## Control Flow
There is no executable control flow. Its value is package existence: when `generated/insns.go` is excluded by `// go:build !codeanalysis`, this file can still provide a compilable package.

## State, Dependencies, Integration, Risks, And Tests
The file has no state, persistence, imports, or runtime side effects. It integrates with Go build constraints and the `pkg/ifuzz` blank import of generated architecture packages. The risk is behavioral absence: under `codeanalysis`, the generated `init()` that registers RISC-V instructions does not run, so code-analysis builds should not assume RISC-V descriptors are registered. Tests are mostly build signals: package compilation with and without the `codeanalysis` tag and import paths that reference `riscv64/generated`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/empty.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go

## Purpose
`insns.go` is the generated RISC-V 64 instruction descriptor table for syzkaller's instruction fuzzer. It imports `pkg/ifuzz/riscv64` with a dot import, registers the generated descriptors from `init`, and defines `insns_riscv64` as the static source of instruction masks, opcodes, fields, privilege flags, and fixed representative encodings.

## Important APIs, Types, And Functions
The file exposes `func init()` and `var insns_riscv64 = []*Insn{...}`. `init` calls `Register(insns_riscv64)`. The generated slice contains 1,182 unique instruction descriptors, each an `*riscv64.Insn` literal with `Name`, `OpcodeMask`, `Opcode`, optional `Fields`, `AsUInt32`, optional `Priv`, and `Generator: nil`. Field names include scalar registers (`xs1`, `xs2`, `xd`), floating registers (`fs1`, `fs2`, `fd`), vector registers (`vs1`, `vs2`, `vs3`, `vd`), immediates, `vm`, rounding modes, and split immediates such as `imm_31_25`/`imm_11_7`. Four entries are marked privileged in the generated table by the generator's access rule.

## Control Flow
The only direct control flow is package initialization. A blank import of this generated package runs `init`, which calls `riscv64.Register`. Registration appends pseudo instructions, indexes every descriptor into `iset.ModeInsns`, stores the resulting `InsnSet` in `iset.Arches[iset.ArchRiscv64]`, and stores these generated descriptors in `templates` for parsing. Encode paths for generated descriptors emit the four-byte little-endian `AsUInt32`; decode paths call `ParseInsn`, which scans `templates` in order and checks `(value & OpcodeMask) == Opcode`.

## State and Persistence Behavior
The file is generated source, not hand-maintained logic. Its runtime persistence is global in-process registration in `iset.Arches` and package-level `riscv64.templates`. The descriptor literals are static. Build state matters: the file is guarded by `// go:build !codeanalysis`, and `empty.go` is the fallback package file when this table is excluded.

## Dependencies and Integration Points
The file depends on `github.com/google/syzkaller/pkg/ifuzz/riscv64` for descriptor types and `Register`. It is generated by `pkg/ifuzz/riscv64/gen/gen.go` from YAML under `gen/inst`. It integrates with generic ifuzz architecture selection, RISC-V parsing, `riscv64_test.go`, and descriptor-specific YAML such as the vector crypto and BF16 entries in this work item. The last part of the table includes the listed `vwsll`, `vclmul`, BF16, AES, SHA, SM3, and SM4 vector descriptors.

## Risks and Edge Cases
Descriptor order is semantically important because parsing returns the first matching template. The generator currently preserves only encoding, field list, name, and coarse privilege state; extension conditions, timing flags, semantic operation snippets, operand legality, and immediate ranges are absent. Generated `Encode` emits fixed representative opcodes rather than randomizing fields, limiting generation diversity. Manual edits would be overwritten by `go generate`. Build-tag exclusion can hide RISC-V registration in code-analysis builds.

## Test Signals
Strong signals are `go generate` diffs, generated entry counts, table presence checks for representative extensions, and decode round trips through `riscv64.ParseInsn` and `InsnSet.Decode`. `riscv64_test.go` exercises representative base and CSR-like encodings; adding samples for vector crypto/BF16 descriptors would catch mask drift in this tail of the table. Tests should also verify privileged classification for access-restricted YAML and ensure no accidental descriptor overlap changes parse results.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/generated/insns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/pseudo.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/pseudo.go

## Purpose
`pseudo.go` is the RISC-V backend's placeholder for pseudo instructions. The package comment identifies it as the pseudo-instruction list for `riscv64`.

## Important APIs, Types, And Functions
The file declares `var pseudo = []*Insn{}`. There are no generator functions, pseudo encoders, or helper APIs yet. The variable is package-private but consumed by `Register` in `riscv64.go`.

## Control Flow
No code runs in this file directly. During `Register`, the generated instruction slice is appended with `pseudo...`. Because the slice is empty, registration currently installs only generated descriptors.

## State and Persistence Behavior
The empty slice is static process state. It does not persist externally and currently adds no generated bytes. If future pseudo instructions are added, they will become part of the registered `InsnSet` and can provide custom `Generator` functions used by `Insn.Encode`.

## Dependencies and Integration Points
The file depends only on the local `Insn` type. Its integration point is `Register`, which appends pseudo descriptors before indexing mode/type information. It mirrors other architecture backends that use pseudo instructions to generate executable snippets or setup code.

## Risks and Test Signals
The present risk is coverage absence rather than behavior: RISC-V has no pseudo sequences for setup, traps, or richer fuzzing. Future additions must set `Pseudo: true`, provide a non-nil `Generator`, and avoid corrupting generated-template parsing because `templates` intentionally remains the generated-only slice. Tests should check that pseudo instructions appear in `GetInsns` but are not parsed as fixed templates unless explicitly intended.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/pseudo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/riscv64.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/riscv64.go

## Purpose
`riscv64.go` is the runtime implementation for syzkaller's RISC-V ifuzz backend. It defines descriptor types, registration, encoding, decoding, and template-based parsing for generated RISC-V instructions.

## Important APIs, Types, And Functions
Key types are `InsnField`, `Insn`, and `InsnSet`. `Register` installs generated plus pseudo descriptors into the generic `iset` registry. `InsnSet.GetInsns` returns mode/type indexed instructions. `Insn.Info` reports name, `ModeLong64`, pseudo status, and privilege. `Insn.Encode` emits pseudo-generated bytes or a four-byte little-endian `AsUInt32`. `InsnSet.Decode` validates at least four bytes, reads a little-endian opcode, and delegates to `ParseInsn`. `ParseInsn`, `matchesValue`, and `initFromValue` implement mask-based decode and operand extraction.

## Control Flow
Generated package initialization calls `Register`. Registration appends `pseudo`, indexes instructions with `modeInsns.Add`, stores the resulting set under `iset.ArchRiscv64`, and stores generated templates for parsing. Decode reads one 32-bit instruction and returns length 4 on success. `ParseInsn` scans templates in order, copies the first matching descriptor, fills `Operands` using `extractBits`, and returns an `unknown` instruction with an error if nothing matches.

## State and Persistence Behavior
Runtime state is global: `iset.Arches[iset.ArchRiscv64]` and package-level `templates`. There is no disk persistence. The static generated table and import side effects determine availability; without the generated package import, parsing has no templates.

## Dependencies and Integration Points
The file depends on `encoding/binary`, `fmt`, `math/rand`, and `pkg/ifuzz/iset`. It integrates with generated descriptors, `pseudo.go`, `util.go`, generic ifuzz generation/decode tests, and architecture registration. `DecodeExt` explicitly reports no external decoder.

## Risks and Test Signals
Risks include first-match ambiguity for overlapping masks, fixed representative encoding that does not randomize descriptor fields, global registration order dependence, and limited 32-bit-only decode. `Decode` ignores the requested mode beyond the architecture set. Tests should cover short input errors, unknown opcodes, operand extraction, generated descriptor registration, and parse order for overlapping masks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/riscv64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util.go

## Purpose
`util.go` contains the RISC-V backend's bitfield extraction helper used when parsed instructions populate operand values.

## Important APIs, Types, And Functions
The single function is `extractBits(from uint32, start, size uint) uint32`. `start` is the high bit index in little-endian bit numbering and `size` is the field width. The function builds a mask `(1 << size) - 1`, shifts `from` right by `start - size + 1`, and returns the masked value.

## Control Flow
There is no branching. `riscv64.Insn.initFromValue` calls this helper for every `InsnField` in a matched template, appending extracted operands in field order.

## State, Dependencies, Integration, Risks, And Tests
The helper is pure and has no dependencies or persistence. It integrates with `ParseInsn` and generated field definitions, including split immediates and vector operands. Risks include unsigned arithmetic underflow if callers pass `size > start+1`, and shift/mask corner cases for wide fields. Current use is safe for generated `hi-lo` ranges where `hi >= lo`, but malformed manual descriptors could panic or produce invalid shifts. `util_test.go` covers zero-size fields, single-bit extraction, mid-word ranges, and RISC-V register fields from an encoded `add` sample.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util_test.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util_test.go

## Purpose
`util_test.go` verifies the RISC-V bit extraction helper that underpins operand decoding from generated templates.

## Important APIs, Types, And Functions
It defines helper `extractBitsOne(t, from, start, size, expect)` and test `TestExtractBits`. The helper calls `extractBits` and fails with a formatted message when the result differs from expectation.

## Control Flow
`TestExtractBits` checks zero-width extraction on zero and all-ones values, iterates every bit position 0 through 31 for one-bit extraction, verifies several ranges from `0xf0f0f0f0`, and then validates `xs2`, `xs1`, and `xd` extraction from a concrete RISC-V R-type `add`-shaped value.

## State, Dependencies, Integration, Risks, And Tests
The test uses only Go's `testing` package and local helper code. It has no persistence. It integrates directly with `util.go` and indirectly protects `ParseInsn` operand extraction. The main gap is that it does not test full-width 32-bit extraction, invalid `start`/`size` combinations, split-field recomposition, or generated descriptor parsing end to end. Its existing signals are useful for off-by-one errors in the `start - size + 1` shift formula and for confirming that generated field conventions match RISC-V bit positions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64_test.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/riscv64_test.go

## Purpose
`riscv64_test.go` contains package-level tests and debug print helpers for the RISC-V ifuzz backend. It validates that representative RISC-V opcodes can be parsed and decoded through the registered architecture set.

## Important APIs, Types, And Functions
`PrintInsnRv` formats a parsed `riscv64.Insn` with operand names, widths, and values. `parseAndPrintRv` calls `riscv64.ParseInsn`. `TestSomethingRv` parses a handful of hard-coded instruction words. `TestSumRv` parses hex/opcode pairs with assembly comments. `decodeRvText` repeatedly calls `InsnSet.Decode` over byte slices. `TestDecodeSamplesRv` hex-decodes sample byte strings and decodes them through `iset.Arches["riscv64"]`.

## Control Flow
The tests rely on generated package registration having populated `iset.Arches`. Decode samples are little-endian byte streams; `decodeRvText` advances by the size returned from `Decode`, which should be 4 for every RISC-V instruction. Parse helpers print decoded fields but generally do not assert instruction names.

## State and Dependencies
The tests depend on `encoding/binary`, `encoding/hex`, `fmt`, `strconv`, `testing`, `pkg/ifuzz/iset`, and `pkg/ifuzz/riscv64`. They mutate no persistent state, but they rely on global architecture registration.

## Risks and Test Signals
The tests are useful smoke coverage for parsing and registered decode, but many checks are print-only and would not fail on wrong names if parsing succeeds. They cover base integer, CSR/time, trap, multiplication/division, and memory-like samples, not the vector crypto/BF16 descriptors in this work item. Stronger tests would assert returned names and operands, include unknown/short input errors, and add representative generated vector-extension opcodes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/riscv64_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/decode.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/x86/decode.go

## Purpose
`decode.go` implements the x86 ifuzz instruction-length decoder and optional external XED decoder hook. It aims to avoid failing on correct instructions, while accepting that it can falsely decode some incorrect byte sequences.

## Important APIs, Types, And Functions
The main method is `func (insnset *InsnSet) Decode(mode iset.Mode, text []byte) (int, error)`. It also defines package variable `XedDecode func(mode iset.Mode, text []byte) (int, error)`, prefix maps `prefixes32` and `prefixes64`, and `func (insnset *InsnSet) DecodeExt(mode, text)` for XED integration.

## Control Flow
`Decode` rejects zero-length input, initializes operand/immediate/displacement/address sizes by mode, detects VEX/XOP prefixes with special LDS/LES/POP exclusions, or consumes legacy prefixes while adjusting sizes for `0x66`, `0x67`, and REX.W. It then scans `insnset.Insns`, filtering by mode, VEX presence/map, prefix restrictions, opcode bytes, optional short-register opcode (`Srm`), ModRM constraints, SIB/displacement length, immediate lengths, and suffix bytes. On the first match it returns the decoded byte length; otherwise it returns `unknown instruction`.

## State and Persistence Behavior
There is no disk persistence. Runtime state is the global `XedDecode` hook and static prefix maps. Decode does not mutate instruction descriptors; it only consumes the registered `InsnSet`.

## Dependencies and Integration Points
The file depends on `fmt` and `pkg/ifuzz/iset`. It integrates with generated x86 descriptors, x86 `Insn` metadata, the generic ifuzz decoder interface, and optional XED-backed differential/external decoding through `DecodeExt`.

## Risks and Test Signals
The function is intentionally heuristic and complex. Risks include decode-order ambiguity, prefix handling mistakes, VEX/XOP false positives, ModRM/SIB displacement length bugs, mode-size mistakes, and accepting invalid instruction streams. `DecodeExt` returns a sentinel success length of zero when XED is enabled but no text is provided, which callers must interpret carefully. Tests should cover prefix-only errors, truncated VEX/ModRM/SIB/immediate paths, REX/operand-size interactions, XED hook behavior, and known byte sequences across 16/32/64-bit modes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/decode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/encode.go -->
# sources/test-tools/syzkaller/pkg/ifuzz/x86/encode.go

## Purpose
`encode.go` implements random x86 instruction encoding for ifuzz descriptors. It turns an `Insn` template plus an `iset.Config` and RNG into bytes, including prefixes, opcodes, ModRM/SIB, displacement, immediates, and suffixes.

## Important APIs, Types, And Functions
The main API is `func (insn *Insn) Encode(cfg *iset.Config, r *rand.Rand) []byte`. It calls `cfg.IsCompatible`, pseudo `generator` functions, and `generateArg` for displacement/immediate bytes. It reads many `Insn` metadata fields: `Vex`, `VexMap`, `VexL`, `VexP`, `VexNoR`, `Rexw`, `Prefix`, `No66Prefix`, `NoRepPrefix`, `Mem32`, `Opcode`, `Srm`, `Modrm`, `Reg`, `Rm`, `Mod`, `NoSibDisp`, `Avx2Gather`, `Imm`, `Imm2`, and `Suffix`.

## Control Flow
The method panics if the instruction is incompatible with the requested mode, delegates pseudo instructions, initializes size defaults by mode, and then branches between legacy and VEX/XOP encodings. Legacy encoding may add random harmless prefixes, required prefixes, and optional REX; prefixes update operand/address/immediate sizes. VEX encoding constructs three-byte prefixes with randomized or constrained R/X/B/W/L/pp/vvvv fields. The encoder then appends opcode bytes, encodes `Srm` or full ModRM, optionally emits SIB and displacement bytes, appends immediate operands after translating sentinel sizes (`-1`, `-2`, `-3`), and finally appends suffix bytes.

## State and Persistence Behavior
The function has no persistent state but consumes RNG state heavily, so output is deterministic only for a fixed `rand.Rand` seed and descriptor. It does not mutate descriptors, except through local variables. Panics are used for impossible mode/compatibility errors.

## Dependencies and Integration Points
The file depends on `math/rand` and `pkg/ifuzz/iset`. It integrates with x86 descriptor generation, pseudo instruction generators, the x86 decoder, and generic ifuzz generation loops. The Intel/AMD manual comment documents the architectural basis for the encoding rules.

## Risks and Test Signals
Risks include generating prefixes that alter semantics unexpectedly, incorrect size recalculation for `0x66`/`0x67`/REX.W, VEX bit inversion mistakes, invalid AVX2 gather register combinations, and ModRM/SIB displacement edge cases. Random generation can hide rare failures without deterministic seeds. Tests should round-trip encoded bytes through `Decode`, compare selected cases with XED when available, cover all modes and sentinel immediate sizes, and include gather-specific register exclusion checks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/ifuzz/x86/encode.go -->
