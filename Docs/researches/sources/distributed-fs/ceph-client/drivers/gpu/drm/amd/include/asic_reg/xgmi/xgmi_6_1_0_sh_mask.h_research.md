# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/xgmi/xgmi_6_1_0_sh_mask.h

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
