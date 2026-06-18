# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/wafl/wafl2_4_0_0_sh_mask.h

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
