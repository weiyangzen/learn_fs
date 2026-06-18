# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxbf_gige/mlxbf_gige_intr.c

## Purpose
`mlxbf_gige_intr.c` handles the BlueField GigE interrupt lines: error/status, receive packet, and LLU/PLU events.

## Important APIs, Types, and Functions
Local handlers are `mlxbf_gige_error_intr()`, `mlxbf_gige_rx_intr()`, and `mlxbf_gige_llu_plu_intr()`. Public helpers are `mlxbf_gige_request_irqs()` and `mlxbf_gige_free_irqs()`.

## Control Flow and State
Open calls `mlxbf_gige_request_irqs()`, which requests error, RX, then LLU/PLU IRQs and unwinds in reverse on failure. The error handler reads `MLXBF_GIGE_INT_STATUS`, increments software stats for asserted error bits, clears all asserted error bits except the RX receive-packet bit, and returns handled. The RX handler relies on hardware auto-masking the receive interrupt and schedules NAPI; polling later clears the mask bit. The LLU/PLU handler currently only acknowledges as handled.

## Dependencies and Integration Points
The file depends on Linux IRQ APIs, MMIO status registers, NAPI scheduling through `priv->napi`, and the stats fields exported through netdev and ethtool paths.

## Risks and Test Signals
Risks include clearing the RX bit from the wrong context, missing an error bit in stats, IRQ request unwind bugs, scheduling NAPI after stop, and an intentionally empty LLU/PLU handler masking future event needs. Test signals are interrupt request/free on open/close, RX interrupt-to-NAPI flow, induced TX/RX/SW/HW error status bits, IRQ storm absence, and stats increments visible through ethtool.
