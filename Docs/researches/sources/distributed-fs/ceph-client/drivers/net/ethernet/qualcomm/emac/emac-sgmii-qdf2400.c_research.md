<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2400.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2400.c

## Purpose
`emac-sgmii-qdf2400.c` programs the QDF2400 SGMII v2 PHY and per-lane digital block used by the Qualcomm EMAC driver. It configures lane CDR, signal detect, TX drive, band/rate, receiver path, reset state machine bypasses, PCS power, and loopback disablement.

## Important APIs, Types, and Functions
- `struct emac_reg_write` and `emac_reg_write_all()` provide table-driven MMIO programming.
- `sgmii_laned[]` defines the QDF2400 digital lane sequence.
- `physical_coding_sublayer_programming[]` defines common PCS power/CDR/lane control values.
- `emac_sgmii_init_qdf2400()` is the hardware-specific initializer selected by ACPI `_HRV == 2`.

## Control Flow
The initializer writes PCS settings to `phy->base`, writes lane settings to `phy->digital`, clears `EMAC_SGMII_PHY_RESET_CTRL`, starts the lane reset state machine through `SGMII_LN_RSM_START`, and polls `SGMII_PHY_LN_LANE_STATUS` for bit 1. On timeout it returns `-EIO`; otherwise it disables digital and SerDes loopback registers and masks all SGMII interrupts.

## State and Persistence
State is held in hardware registers reached through `adpt->phy.base` and `adpt->phy.digital`. There is no allocation or mutable static state. The initialized state persists until reset, power loss, or reprogramming by `emac_sgmii_common_reset()`.

## Dependencies and Integration Points
The file includes `emac.h` for shared SGMII v2 offsets such as `SGMII_LN_RSM_START`, `SGMII_PHY_LN_LANE_STATUS`, and BIST/CDR registers. It is called from `emac-sgmii.c` through the ACPI-selected `qdf2400_ops`.

## Risks and Edge Cases
- `phy->digital` must be mapped; the QDF2400 path depends on resource index 1 being present.
- Several offsets differ from QDF2432 despite similar code; copying tables between revisions is risky.
- The multicast-style write loop ignores readback, so only the final ready poll catches a broad class of bad programming.
- Loopback registers are written through `phy_regs` using shared lane offsets; incorrect resource layout would silently target wrong registers.

## Test Signals
Probe/open success on QDF2400 ACPI systems, absence of `"SGMII failed to start"`, valid link negotiation through the common layer, and no decode-error-triggered SGMII resets are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-qdf2400.c -->
