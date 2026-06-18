# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal.h

## Purpose

`hal.h` is the common Wi-Fi 7 HAL register/mask/API contract. It defines BAR-relative register addresses, chip-register-table access macros, SRNG field masks, WBM cookie-conversion masks, REO command/update flags, REO status structures, and prototypes for the common functions implemented by `hal.c` and `hal_rx.c`.

## Important APIs and Types

- Register address macros cover WCSS UMAC REO/TCL/WBM, CE bases, TCL rings, REO rings, CE rings, WBM idle/release rings, PPE rings, and shadow registers.
- Register-table indirection macros, such as `HAL_TCL1_RING_BASE_LSB(hal)` and `HAL_REO1_QDESC_ADDR(hal)`, dereference `hal->regs` so common code can work across QCN9274, IPQ5332/IPQ5424, QCC2072, and WCN7850-style layouts.
- Offset macros such as `HAL_TCL1_RING_MSI1_BASE_LSB_OFFSET(hal)` derive per-ring register offsets from the base LSB register.
- Field masks define ring size, address MSBs, entry size, MSI enable/swap, host/FW swap, data TLV swap, interrupt thresholds, REO misc controls, cookie conversion, WBM idle-list mode, and queue LUT control.
- REO command flag macros (`HAL_REO_CMD_FLG_*`) and update masks (`HAL_REO_CMD_UPD0_*`, `HAL_REO_CMD_UPD1_*`, `HAL_REO_CMD_UPD2_*`) mirror the hardware command descriptor fields encoded in `hal_rx.c`.
- Status types include `struct hal_reo_status`, nested status payloads for queue stats, flush queue/cache, unblock cache, timeout list, and descriptor threshold reached.
- Exported prototypes include common HAL init/setup helpers, CE descriptor helpers, WBM idle-list helpers, REO LUT helpers, and `ath12k_wifi7_hal_reo_qdesc_size()`.

## Control Flow Role

This header does not execute control flow directly, but it determines how implementation files compute register addresses and encode/decode hardware command/status fields. The common ring setup code in `hal.c` uses this header to calculate target registers and enable bits. The REO command/status code in `hal_rx.c` uses the command flags and status structures here to provide a hardware-independent status shape to upper DP code.

## State and Persistence

`hal.h` defines no storage. It describes state that persists in hardware registers, DMA descriptors, and driver-owned status structures. The most important persistent state surfaces are shadow register slots, HP/TP register values, cookie-conversion enablement, REO queue descriptors, and `struct hal_reo_status` values returned to higher layers.

## Dependencies and Integration Points

The header includes ath12k core/common HAL headers and Wi-Fi 7 descriptor headers: `../core.h`, `../hal.h`, `hal_desc.h`, `hal_tx.h`, `hal_rx.h`, and `hal_rx_desc.h`. It is included by common and chip-specific HAL implementations and by DP code that needs Wi-Fi 7-specific REO status or ring helpers.

## Risks

- Macros are tightly coupled to hardware register layouts. Incorrect values can silently direct MMIO writes to unrelated blocks.
- `HAL_REO_CMD_UPD*` masks must stay aligned with the hardware descriptor masks in `hal_desc.h`; divergence would update the wrong queue fields.
- `HAL_RX_REO_QUEUE_INFO2_MSDU_COUNT` is written as `(31, 7)` rather than a `GENMASK`, which is suspicious and should be checked before use.
- Several register macros dereference `hal->regs`; any chip register table member left undefined can cause invalid MMIO programming if the common helper still uses it.
- Fixed constants such as cookie partition MSBs and default REO timeouts are policy baked into the HAL and need hardware/firmware agreement.

## Test Signals

Build coverage should include all files using these macros with sparse/endian warnings enabled. Runtime validation should compare ring register programming against chip documentation, exercise REO queue update/status commands, verify cookie conversion and shadow registers, and run traffic on every supported hardware revision using this header.
