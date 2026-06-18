# subset-b-003484 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/wafl/wafl2_4_0_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/wafl/wafl2_4_0_0_sh_mask.h

### Purpose
`wafl2_4_0_0_sh_mask.h` is a generated AMDGPU register-field header for the WAFL 2.4.0.0 PCS GOPX1 error-status register. It gives the driver named bit shifts and masks for decoding WAFL physical coding sublayer link errors reported through `PCS_GOPX1_0_PCS_GOPX1_PCS_ERROR_STATUS`.

### Important APIs, Types, And Functions
The file exports only preprocessor constants. The API surface is the paired `PCS_GOPX1_0_PCS_GOPX1_PCS_ERROR_STATUS__<field>__SHIFT` and `..._MASK` macros used by `SOC15_REG_FIELD()`. Fields cover single-bit error indicators such as `DataLossErr`, `TrainingErr`, `CRCErr`, `BERExceededErr`, `TxMetaDataErr`, replay-buffer parity, data parity, replay FIFO overflow/underflow, elastic FIFO overflow, deskew, startup and recovery timeout/attempt failures, plus `ClearBERAccum` and the 8-bit `BERAccumulator` in bits 31:24.

### Control Flow
There is no executable control flow in the header. At compile time the macros expand into field metadata. Runtime flow is in `amdgpu_xgmi.c`: WAFL status register addresses are read from SMN, and the resulting status words are decoded by iterating `wafl_pcs_ras_fields`, whose entries are built with these field names.

### State, Persistence, And Dependencies
The header stores no software state and has no persistence behavior. Live state is the WAFL PCS hardware status register, including sticky or hardware-cleared error bits depending on the register semantics. It depends on `wafl2_4_0_0_smn.h` for the base SMN address and on SOC15 field helpers that expect the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming pattern.

### Integration Points
`amdgpu_xgmi.c` includes this file and builds WAFL RAS field descriptors for Vega20/Arcturus-era links. The fields feed XGMI hive/link diagnostics and RAS reporting alongside the companion XGMI PCS fields. The SMN address arrays use two WAFL instances by adding `0x100000` to the base address from the SMN header.

### Risks
The main risk is field drift against hardware. A wrong shift or mask can mislabel a link failure, hide a real error, or make RAS counters unreliable. `ClearBERAccum` shares the same register as status fields, so any caller that writes a full register value instead of a targeted bit update could accidentally clear or disturb error state. The WAFL register layout resembles XGMI 4.0.0 but uses different register names, so cross-family copy/paste can compile while reporting the wrong link block.

### Test Signals
Useful signals include successful AMDGPU builds for code including `amdgpu_xgmi.c`, XGMI/WAFL RAS logs that name expected WAFL PCS fields, SMN readback on affected ASICs showing bits decoded consistently with injected or observed link faults, and static checks that each `SOC15_REG_FIELD(PCS_GOPX1_0_PCS_GOPX1_PCS_ERROR_STATUS, ...)` reference has both shift and mask definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/wafl/wafl2_4_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/wafl/wafl2_4_0_0_smn.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/wafl/wafl2_4_0_0_smn.h

### Purpose
`wafl2_4_0_0_smn.h` defines the SMN address for the WAFL 2.4.0.0 PCS GOPX1 error-status register used by AMDGPU XGMI/WAFL RAS handling. Its single exported address, `smnPCS_GOPX1_0_PCS_GOPX1_PCS_ERROR_STATUS`, points at `0x11cf0210`.

### Important APIs, Types, And Functions
The only functional export is the `smnPCS_GOPX1_0_PCS_GOPX1_PCS_ERROR_STATUS` macro. It is consumed as a raw SMN address, not as a SOC15 offset/base-index pair. There are no C types, functions, structs, or inline helpers.

### Control Flow
The header has no runtime control flow. Runtime code in `amdgpu_xgmi.c` places this base address and a second instance at base plus `0x100000` into WAFL PCS status arrays. XGMI RAS logic later walks those arrays, reads the status registers, and decodes the status bits with `wafl2_4_0_0_sh_mask.h`.

### State, Persistence, And Dependencies
No software state is stored. The addressed hardware register contains live or sticky WAFL PCS status. The header depends on the SMN access path used by AMDGPU and on exact pairing with the matching shift/mask header; the address has meaning only for ASIC generations whose WAFL block matches this generated map.

### Integration Points
`amdgpu_xgmi.c` includes this file for Vega20 and Arcturus WAFL status arrays. Those arrays integrate with XGMI hive management and RAS error reporting by giving the driver the addresses of the per-link WAFL PCS status registers.

### Risks
An incorrect SMN address sends diagnostics to the wrong register, which can produce false clean status, false link errors, or reads of unrelated hardware state. Instance addressing is derived by arithmetic on this base, so the base must stay aligned with the documented WAFL register aperture. The similarly named Aldebaran WAFL constants are locally defined in `amdgpu_xgmi.c`, so mixing the generated 2.4.0.0 address with newer layouts is a concrete maintenance risk.

### Test Signals
Signals include compile coverage of `amdgpu_xgmi.c`, successful SMN reads from `0x11cf0210` and `0x11df0210` on supported hardware, RAS output that reports WAFL PCS errors only on the expected links, and hardware register dumps matching the generated address map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/wafl/wafl2_4_0_0_smn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_4_0_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_4_0_0_sh_mask.h

### Purpose
`xgmi_4_0_0_sh_mask.h` is a generated AMDGPU register-field header for the XGMI 4.0.0 PCS GOPX16 error-status register. It defines bit shifts and masks for decoding link-level XGMI PCS failures from `XGMI0_PCS_GOPX16_PCS_ERROR_STATUS`.

### Important APIs, Types, And Functions
The exported API is a set of `XGMI0_PCS_GOPX16_PCS_ERROR_STATUS__<field>__SHIFT` and `..._MASK` macros. The fields cover data loss, training failure, CRC and BER threshold errors, transmit metadata, replay-buffer parity, data parity, replay FIFO overflow and underflow, elastic FIFO overflow, deskew, data-startup limit, flow-control initialization timeout, recovery timeout, ready-serial timeout and attempt failures, recovery attempt and relock failures, `ClearBERAccum`, and the top-byte `BERAccumulator`.

### Control Flow
There is no control flow in the header. Consumers expand these macros through SOC15 helpers. In `amdgpu_xgmi.c`, the `xgmi_pcs_ras_fields` table binds human-readable RAS names to these generated field definitions, and later XGMI error paths use that table to interpret status values read from SMN.

### State, Persistence, And Dependencies
The header stores no state. Hardware state resides in the XGMI PCS status registers addressed by `xgmi_4_0_0_smn.h`; status bits may represent accumulated link health until cleared by hardware-defined mechanisms. The header depends on the generated naming convention required by `SOC15_REG_FIELD()` and on exact alignment with XGMI 4.0.0 register documentation.

### Integration Points
`amdgpu_xgmi.c` includes this file with `xgmi_4_0_0_smn.h`. The field definitions are used for XGMI PCS RAS reporting on Vega20 and Arcturus style links. Address arrays in that code cover two Vega20 XGMI links and six Arcturus link instances by adding fixed aperture offsets to the SMN base.

### Risks
Incorrect bit definitions compromise RAS quality and can direct debugging toward the wrong link failure mode. The register includes both status and `ClearBERAccum`, so write paths need to avoid broad read-modify-write operations that could clear accumulated BER data unintentionally. The XGMI 4.0.0 layout is narrower than XGMI 6.1.0; using the wrong header would miss newer flow-control, replay-timeout, sync-header, link-subchannel, and command-packet error bits.

### Test Signals
Signals include successful compilation of all `SOC15_REG_FIELD(XGMI0_PCS_GOPX16_PCS_ERROR_STATUS, ...)` entries, RAS logs that correctly distinguish CRC, BER, training, and recovery failures, link-fault injection or hardware error campaigns that set expected bits, and static checks confirming masks match their shifts and do not overlap unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_4_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_4_0_0_smn.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_4_0_0_smn.h

### Purpose
`xgmi_4_0_0_smn.h` defines the SMN address of the XGMI 4.0.0 PCS GOPX16 error-status register. The single exported macro, `smnXGMI0_PCS_GOPX16_PCS_ERROR_STATUS`, is the address anchor used by AMDGPU to read XGMI PCS link error status.

### Important APIs, Types, And Functions
The header exports `smnXGMI0_PCS_GOPX16_PCS_ERROR_STATUS` with value `0x11af0210`. There are no functions or types. Consumers use the macro as an absolute SMN address and derive additional instances by adding fixed offsets.

### Control Flow
No control flow is present in this header. At runtime, `amdgpu_xgmi.c` places the base address into XGMI PCS status register arrays, derives further link addresses with additions such as `+ 0x100000`, `+ 0x500000`, and higher instance offsets, reads those registers through SMN accessors, and decodes fields with `xgmi_4_0_0_sh_mask.h`.

### State, Persistence, And Dependencies
The header contains no mutable state and does not persist data. The referenced hardware register contains the link status. Correct operation depends on the AMDGPU SMN read path, the XGMI IP version selection in `amdgpu_xgmi.c`, and the companion shift/mask header.

### Integration Points
The direct integration point is `amdgpu_xgmi.c`, where the address is used for Vega20 and Arcturus XGMI PCS status arrays. The arrays feed RAS reporting and multi-GPU XGMI hive diagnostics.

### Risks
Address drift is high impact because every decoded field would then come from the wrong hardware location. Derived instance addresses amplify a wrong base address across multiple links. The header is generation-specific; newer XGMI 6.x handling uses local SMN constants and the XGMI 6.1.0 mask header, so broad reuse of this address beyond its intended IP block is risky.

### Test Signals
Signals include compile coverage of XGMI RAS code, SMN register dumps showing `0x11af0210` and derived addresses correspond to PCS error-status registers, correct per-link RAS attribution on multi-link GPUs, and absence of SMN access faults on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_4_0_0_smn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_6_1_0_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_6_1_0_sh_mask.h

### Purpose
`xgmi_6_1_0_sh_mask.h` is a generated field-definition header for the XGMI 6.1.0 `PCS_XGMI3X16_PCS_ERROR_STATUS` register. It describes a newer XGMI3X16 PCS error-status layout with individual bits for flow-control, FIFO, replay, sync-header, timeout, sublink, and command-packet faults.

### Important APIs, Types, And Functions
The header exports `PCS_XGMI3X16_PCS_ERROR_STATUS__<field>__SHIFT` and `..._MASK` macros. Compared with XGMI 4.0.0, it adds fields such as `FlowCtrlAckErr`, `RxFifoUnderflowErr`, `RxFifoOverflowErr`, `TxVcidDataErr`, `FlowCtrlCRCErr`, `ReplayAttemptErr`, `SyncHdrErr`, `TxReplayTimeoutErr`, `RxReplayTimeoutErr`, `LinkSubTxTimeoutErr`, `LinkSubRxTimeoutErr`, and `RxCMDPktErr`. The defined bits occupy positions 0 through 28, with no exported BER accumulator field in the top byte.

### Control Flow
There is no executable logic in the header. `amdgpu_xgmi.c` uses these macros in `xgmi3x16_pcs_ras_fields`, and the runtime RAS path reads PCS status registers, applies each field mask, and emits the matching RAS text for set bits. The same error names also align with the `xgmi_v6_4_0_ras_error_code_ext` string table for machine-check/RAS code interpretation.

### State, Persistence, And Dependencies
The header holds no state. The state is in live XGMI3X16 PCS status registers, and in related non-correctable mask registers defined locally in `amdgpu_xgmi.c`. The header depends on SOC15 field macro naming and on local SMN constants in the consumer because this subset does not include a generated `xgmi_6_1_0_smn.h`.

### Integration Points
The direct consumer is `amdgpu_xgmi.c`, where Aldebaran and XGMI 6.4 paths use XGMI3X16 status addresses and these field descriptors. The definitions support RAS diagnostics, XGMI hive management, link health reporting, and interpretation of PCS-related MCA/RAS errors.

### Risks
Because each bit maps to a precise protocol fault, stale masks can lead to wrong RAS classification and wasted hardware triage. The layout differs from older XGMI 4.0.0: bit 7 is `TxVcidDataErr` rather than older transmit metadata naming, bits 2-4 and 14/16-28 have new meanings, and the old `ClearBERAccum`/`BERAccumulator` definitions are absent. Treating this register like the older layout would silently drop many error classes or misreport them.

### Test Signals
Signals include successful builds of `amdgpu_xgmi.c`, RAS logs for Aldebaran/XGMI 6.x hardware that include the new XGMI3X16 field names, validation that MCA extended error codes line up with these bit positions, hardware fault-injection or lab link-error tests for FIFO/flow-control/replay categories, and static mask/shift consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_6_1_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-bits.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-bits.h

### Purpose
`atom-bits.h` provides small little-endian BIOS buffer access helpers for the AMD ATOM BIOS interpreter and related ATOMBIOS parsing code. It centralizes byte, 16-bit, 32-bit, and string pointer reads from raw VBIOS memory.

### Important APIs, Types, And Functions
The file defines `get_u8(void *bios, int ptr)`, `get_u16(void *bios, int ptr)`, and `get_u32(void *bios, int ptr)` as static inline readers. `get_u16` composes two bytes in little-endian order, and `get_u32` composes two little-endian 16-bit values. It also defines context-sensitive macros: `U8`, `U16`, and `U32` read through `ctx->ctx->bios` for an `atom_exec_context`; `CU8`, `CU16`, and `CU32` read through `ctx->bios` for a direct `atom_context`; and `CSTR(ptr)` returns a `char *` into `ctx->bios`.

### Control Flow
The helpers themselves are straight-line loads and shifts. They sit on hot interpreter paths in `amdgpu/atom.c`: command-table execution reads opcodes with `CU8`, resolves table offsets with `CU16`, decodes instruction operands with `U8`/`U16`, and navigates ATOM ROM metadata and strings with `CSTR`. Related ATOMBIOS display files include the header for the same raw-buffer access pattern.

### State, Persistence, And Dependencies
No state is stored and no persistence occurs. The macros assume the caller has a variable named `ctx` with either an execution context or an atom context, so the API is intentionally lexical rather than type-safe. The helpers depend on fixed-width integer typedefs being visible through surrounding includes and on the ATOM BIOS data being little-endian.

### Integration Points
The primary integration points are `amdgpu/atom.c`, `amdgpu/amdgpu_atombios.c`, `amdgpu/atombios_dp.c`, and `amdgpu/atombios_crtc.c`. In `atom.c`, these helpers support BIOS validation, command/data table indexing, indirect I/O bytecode execution, opcode fetch, operand decode, VBIOS version/build string extraction, and firmware information parsing.

### Risks
The helpers perform unchecked pointer arithmetic into the BIOS buffer. If offsets are corrupt or not validated by callers, reads can go outside the mapped VBIOS image. The macros are tied to a local variable named `ctx`, so they are easy to misuse in a function with the wrong context type. They also manually assemble little-endian values and do not consult `ATOM_BIG_ENDIAN`, so callers must not use them as generic host-endian structure accessors.

### Test Signals
Signals include ATOM BIOS parser tests or boot coverage across GPUs with valid and malformed VBIOS images, successful execution of command tables without out-of-bounds reports under KASAN/UBSAN, correct VBIOS part/build/version strings in logs, display bring-up paths that parse DP/CRTC ATOM tables correctly, and compiler coverage for both `U*` and `CU*` macro contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-names.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-names.h

### Purpose
`atom-names.h` supplies optional debug name tables for the AMD ATOM BIOS interpreter. When `ATOM_DEBUG` is enabled, it maps ATOM opcode numbers, command table indexes, and I/O space identifiers to readable strings for debug logs.

### Important APIs, Types, And Functions
Under `#ifdef ATOM_DEBUG`, the header defines `ATOM_OP_NAMES_CNT` as `123` and initializes `atom_op_names[]`, defines `ATOM_TABLE_NAMES_CNT` as `74` and initializes `atom_table_names[]`, and defines `ATOM_IO_NAMES_CNT` as `5` and initializes `atom_io_names[]`. Without `ATOM_DEBUG`, the three count macros are all `0` and no arrays are emitted. The file includes `atom.h` for opcode/table constants but defines no functions or structs.

### Control Flow
There is no runtime control flow in this header, but the compile-time branch changes what debug data exists. In `amdgpu/atom.c`, `ATOM_DEBUG` is defined before including this header, so command execution can print `atom_op_names[op]` when `op < ATOM_OP_NAMES_CNT`. The runtime print path is gated by `amdgpu_atom_debug`, so the arrays are present for debugging but only used when debug output is enabled.

### State, Persistence, And Dependencies
The arrays are static file-local data in each translation unit that includes the header with `ATOM_DEBUG` set. They persist for the lifetime of the module but hold only constant string pointers. The header depends on `atom.h` and on the arrays staying synchronized with the interpreter's opcode numbering and ATOM table indexes.

### Integration Points
The direct integration point is `amdgpu/atom.c`, where the opcode names annotate interpreter traces such as command-table execution offsets. The table and I/O names are available for related ATOM debug output in the same translation unit if used by debug paths.

### Risks
The count values and initializer order must track the opcode and table definitions. If new opcodes are added without updating the table, debug traces can print numeric fallbacks or misleading names. Because the arrays are declared `static char *` rather than `static const char * const`, accidental mutation would be possible inside the translation unit, though current use treats them as read-only debug labels. Including this header with `ATOM_DEBUG` in many C files would duplicate the static arrays.

### Test Signals
Signals include builds with and without `ATOM_DEBUG`, enabling `amdgpu_atom_debug` and confirming opcode traces match executed ATOM bytecode, bounds checks where opcodes at or above `ATOM_OP_NAMES_CNT` print numeric fallbacks, and review checks that opcode/table count constants stay aligned with `atom.h` and the interpreter dispatch table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-names.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-types.h

### Purpose
`atom-types.h` provides legacy ATOM BIOS type aliases and an endianness macro used by AMDGPU ATOMBIOS structures and power-management table code. It bridges ATOM BIOS naming conventions to Linux fixed-width integer types.

### Important APIs, Types, And Functions
The header defines `USHORT` as `uint16_t`, `ULONG` as `uint32_t`, and `UCHAR` as `uint8_t`. It also defines `ATOM_BIG_ENDIAN` to `1` when `__BIG_ENDIAN` is defined and to `0` otherwise, unless a prior include has already defined `ATOM_BIG_ENDIAN`. There are no functions.

### Control Flow
There is no executable control flow. Compile-time preprocessor flow decides the value of `ATOM_BIG_ENDIAN`. Other headers, especially `atombios.h`, use that macro in `#if ATOM_BIG_ENDIAN` blocks to select structure bitfield layouts or endian-sensitive declarations.

### State, Persistence, And Dependencies
The header stores no runtime state and performs no persistence. It depends on fixed-width integer types being available from prior includes such as Linux type headers. Its definitions influence the layout of ATOM BIOS structure declarations at compile time, not runtime data.

### Integration Points
`amdgpu/atom.h` includes this header, and several powerplay hardware-manager files include it directly, including `hwmgr_ppt.h`, `smu8_hwmgr.c`, `smu10_hwmgr.c`, and `pppcielanes.c`. Through `atombios.h`, the `ATOM_BIG_ENDIAN` setting affects many BIOS table structures and firmware table parsing paths.

### Risks
The aliases are legacy names that can obscure signedness and width if mixed with normal kernel types, but they map to explicit fixed-width types. The larger risk is endianness detection: if `__BIG_ENDIAN` is not the right compiler signal in a build environment, `ATOM_BIG_ENDIAN` may select the wrong bitfield layout. Because the macro can be pre-defined before this header, include order or build flags can intentionally or accidentally override it.

### Test Signals
Signals include compile coverage on little-endian and big-endian configurations where available, structure layout checks for `atombios.h` definitions, successful parsing of ATOM powerplay and firmware tables, and build checks for all direct include users that rely on `USHORT`, `ULONG`, `UCHAR`, or `ATOM_BIG_ENDIAN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-types.h -->
