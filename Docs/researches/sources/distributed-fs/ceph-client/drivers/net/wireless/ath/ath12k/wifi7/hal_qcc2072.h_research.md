# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/hal_qcc2072.h

## Purpose

`hal_qcc2072.h` is the small public interface for the QCC2072 Wi-Fi 7 HAL implementation. It exposes the QCC2072 register table, operation table, and RX descriptor offset helpers to common ath12k code.

## Important APIs

- `extern const struct ath12k_hw_regs qcc2072_regs;`
- `extern const struct hal_ops hal_qcc2072_ops;`
- `ath12k_hal_rx_desc_get_mpdu_start_offset_qcc2072()`
- `ath12k_hal_rx_desc_get_msdu_end_offset_qcc2072()`

## Control Flow Role

The header has no runtime control flow. It allows `hal.c` to reference QCC2072 ops/registers in `ath12k_wifi7_hw_ver_map` and allows other code to query QCC2072 descriptor offsets without exposing the full implementation.

## State and Persistence

The exported globals are immutable configuration. The offset helpers return compile-time layout offsets from `struct hal_rx_desc_qcc2072`, which are used to interpret persistent DMA descriptor memory.

## Dependencies and Integration Points

It includes `../hal.h` and the Wi-Fi 7 `hal.h`, so it depends on common HAL types and the shared Wi-Fi 7 register/API contract. It is consumed by `hal.c` and implemented by `hal_qcc2072.c`.

## Risks

- The header lacks its own include guard, unlike `hal_qcn9274.h`; repeated inclusion currently depends on included headers being safe.
- Exposed offset helpers must stay synchronized with `struct hal_rx_desc_qcc2072`; stale offsets would break descriptor parsing.
- Because this header only exports a minimal surface, any new QCC2072-specific helper needed by shared code must be added deliberately rather than relying on static functions in the `.c` file.

## Test Signals

Build tests should include repeated inclusion and all QCC2072 call sites. Runtime signals are indirect: successful QCC2072 HAL selection, descriptor offset consumers parsing correct MPDU start/MSDU end locations, and RX traffic without descriptor misalignment symptoms.
