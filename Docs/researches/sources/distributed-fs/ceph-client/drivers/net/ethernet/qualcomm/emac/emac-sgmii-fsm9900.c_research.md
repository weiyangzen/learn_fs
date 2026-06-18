<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-fsm9900.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-fsm9900.c

## Purpose
`emac-sgmii-fsm9900.c` contains the FSM9900-specific internal SGMII/SerDes initialization sequence for the Qualcomm EMAC driver. It programs PCS, QSERDES PLL, CDR, TX, and RX analog/digital tuning registers, starts the SerDes engine, waits for the reset state machine to report ready, and masks SGMII interrupts before the common EMAC SGMII layer enables runtime handling.

## Important APIs, Types, and Functions
- `struct emac_reg_write` is a local offset/value pair used to describe ordered hardware programming tables.
- `emac_reg_write_all()` writes one table to a supplied MMIO base with `writel()`.
- `physical_coding_sublayer_programming[]`, `sysclk_refclk_setting[]`, `pll_setting[]`, `cdr_setting[]`, and `tx_rx_setting[]` are static register programming sequences for the FSM9900 SerDes.
- `emac_sgmii_init_fsm9900()` is the exported initializer called through `struct sgmii_ops` selected by `emac_sgmii_config()`.

## Control Flow
Initialization is strictly linear: program PCS power/CDR/lane settings, set reference clock and PLL controls, program CDR and TX/RX tuning, assert `SERDES_START`, then poll `EMAC_QSERDES_COM_RESET_SM` up to `SERDES_START_WAIT_TIMES` with `usleep_range(100, 200)`. If the `READY` bit never appears, the function logs a netdev error and returns `-EIO`; otherwise it masks all SGMII interrupts and returns success.

## State and Persistence
All persistent state is in hardware registers under `adpt->phy.base`. The programming tables are immutable kernel data. No driver memory is allocated here, and no software state survives except the configured hardware state.

## Dependencies and Integration Points
The file depends on `emac.h` for shared SGMII register offsets such as wrapper CSR and lane status names, and on Linux I/O/polling helpers. It integrates with `emac-sgmii.c` via `emac_sgmii_init_fsm9900()` and with platform matching for `"qcom,fsm9900-emac-sgmii"`.

## Risks and Edge Cases
- Register constants are hardware-revision-specific; a stale table can leave the SerDes unable to lock.
- The ready poll has a fixed short retry loop, so slow hardware bring-up manifests as probe/open failure.
- The function assumes `phy->base` is valid and mapped by the common SGMII configuration path.
- Interrupts are masked at the end; later common open/link-change code must clear and enable only when ready.

## Test Signals
Useful signals are successful EMAC probe on FSM9900, no `"ser/des failed to start"` logs, stable link-up after `emac_sgmii_link_init()`, and absence of SGMII decode-error reset loops under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii-fsm9900.c -->
