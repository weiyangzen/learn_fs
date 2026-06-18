<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2432.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2432.c

## Purpose
`emac-sgmii-qdf2432.c` provides the QDF2432-specific SGMII v2 lane and PCS programming sequence for Qualcomm EMAC. It is similar to the QDF2400 initializer but uses QDF2432 register offsets and tuned values.

## Important APIs, Types, and Functions
- Local `struct emac_reg_write` and `emac_reg_write_all()` implement table-driven register writes.
- `sgmii_laned[]` configures UCDR gains, signal detect, TX margin/pre/post, CML/mixer/VGA, band/rate, lane mode, RX path, and RSM bypasses.
- `physical_coding_sublayer_programming[]` powers the PCS and enables receive equalization.
- `emac_sgmii_init_qdf2432()` is selected for DT compatible `"qcom,qdf2432-emac-sgmii"` or ACPI `_HRV == 1`/missing `_HRV`.

## Control Flow
The function writes PCS and digital lane tables, clears PCS reset, starts the lane reset state machine, polls for `SGMII_PHY_LN_LANE_STATUS & BIT(1)`, logs and returns `-EIO` on timeout, disables loopback/BIST/CDR test registers, masks SGMII interrupts, and returns success.

## State and Persistence
State is only MMIO hardware state. The code has no locks or allocations. The configured lane state can be destroyed by hardware reset and restored by the common reset path invoking this initializer.

## Dependencies and Integration Points
It depends on the common EMAC/Sgmii headers for adapter and shared v2 offsets. It integrates with `emac-sgmii.c` through `qdf2432_ops`, ACPI matching of `QCOM8071`, and DT matching of the internal PHY node.

## Risks and Edge Cases
- Older QDF2432 ACPI tables may omit `_HRV`; the common matcher treats that as QDF2432, so this initializer must remain the conservative default.
- The code assumes both PCS and digital lane mappings are valid.
- Hardware-specific magic values need board/revision validation; failures often collapse into only the final ready timeout.

## Test Signals
The expected signs are successful initialization on QDF2432, stable SGMII lock and autonegotiation, no repeated decode-error interrupts, and working MAC reset/reinit after link faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2432.c -->
