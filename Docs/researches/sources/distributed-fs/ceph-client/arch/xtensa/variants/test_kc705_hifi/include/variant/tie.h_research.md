# sources/distributed-fs/ceph-client/arch/xtensa/variants/test_kc705_hifi/include/variant/tie.h

## Purpose
This generated Xtensa HAL header describes the TIE and coprocessor configuration for the `test_kc705_hifi` variant. C and assembly consumers use it to size save areas, enumerate optional registers, identify coprocessors, and decode instruction lengths for this Xtensa core.

## Important APIs, types, and macros
The header defines coprocessor topology with `XCHAL_CP_NUM`, `XCHAL_CP_MAX`, `XCHAL_CP_MASK`, and `XCHAL_CP_PORT_MASK`. CP1 is `AudioEngineLX` with 184 bytes of save area and 8-byte alignment; CP7 is `XTIOP` with no saved state but a port-coprocessor identity. `XCHAL_NCP_SA_SIZE` is 36 bytes and `XCHAL_TOTAL_SA_SIZE` is 240 bytes. `XCHAL_NCP_SA_LIST(s)` enumerates `threadptr`, `acclo`, `acchi`, `m0` through `m3`, `br`, and `scompare1`. `XCHAL_CP1_SA_LIST(s)` enumerates AudioEngineLX user registers and register files: `ae_ovf_sar`, `ae_bithead`, `ae_ts_fts_bu_bp`, `ae_cw_sd_no`, `ae_cbegin0`, `ae_cend0`, `aed0` through `aed15`, and `u0` through `u3`. Instruction decoding tables are exposed through `XCHAL_OP0_FORMAT_LENGTHS` and `XCHAL_BYTE0_FORMAT_LENGTHS`.

## Control flow
There is no executable control flow. Consumers define `XCHAL_SA_REG` and expand the list macros to generate save routines, debuggers, offset tables, or diagnostics. The order of list entries defines the logical save-area ordering that the assembler file must honor.

## State and persistence behavior
This file is a declarative contract for CPU state. It encodes which registers must be carried across task switches or inspected by tooling and how much memory to reserve. It does not allocate or mutate memory.

## Dependencies and integration points
The header is coupled to `tie-asm.h`, Xtensa HAL include paths, low-level context save/restore code, and debugging tools that understand Xtensa target register numbers. Kernel arch code may use the CP masks to decide whether `CPENABLE` and lazy coprocessor handling are required.

## Risks
Because this is generated hardware metadata, manual edits risk breaking ABI-level assumptions. Inconsistency with assembler macros can cause truncated or misaligned state saves. CP7 has an identity but zero save area, so code must treat the CP mask and save-area list as separate concepts.

## Test signals
Build-time expansion of `XCHAL_SA_REG` users, comparison against generated assembler offsets, Xtensa boot tests with coprocessor state enabled, and debugger/register-list validation are the primary signals. A focused invariant check can verify that NCP plus CP save sizes align to `XCHAL_TOTAL_SA_SIZE`.
