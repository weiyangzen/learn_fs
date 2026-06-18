<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.h

## Purpose
Defines DWMAC5/EQoS 5.x registers and bit fields for safety, RX parser, PPS, VLAN fail queueing, and FPE interrupt enable, plus prototypes for DWMAC5 extension functions.

## Important APIs, Types, And Functions
Key macros include safety status/control registers (`MAC_DPP_FSM_INT_STATUS`, `MTL_ECC_CONTROL`, `DMA_SAFETY_INT_STATUS`), RX parser control/internal-access fields, PPS control/target/interval/width helpers, VLAN fail queue register fields, and `GMAC_INT_FPE_EN`. Function prototypes expose safety config/status/dump, RX parser config, and flexible PPS config.

## Control Flow
No runtime flow exists. The C implementation uses these macros to program and decode DWMAC5 hardware blocks.

## State And Persistence
No state is stored in the header. The defined registers represent hardware state for safety, parser table control, and PPS outputs.

## Dependencies And Integration Points
Used by `dwmac5.c` and `dwmac4_core.c`; depends on STMMAC types for safety cfg/stats, TC entries, and PPS cfg.

## Risks
PPS bit helper macros construct per-index fields inside a shared register; index range must be validated by callers/capabilities. Safety bits are tightly coupled to hardware ASP levels. RX parser internal-access fields require strict busy polling in users.

## Test Signals
DWMAC510 build coverage, safety feature tests, RX parser filter programming, VLAN fail queue behavior, PPS output configuration, and FPE interrupt enable paths validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac5.h -->
