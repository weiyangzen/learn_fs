# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_4_0_0_sh_mask.h

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
