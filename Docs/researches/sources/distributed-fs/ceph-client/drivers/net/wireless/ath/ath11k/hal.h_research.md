# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/hal.h

## Purpose
`hal.h` is the central ath11k hardware-abstraction contract for SRNG rings, REO command/state objects, ring register offsets, and common descriptor helpers. It does not implement hardware access directly; instead it names the register layout and public HAL APIs used by data path, copy engine, WMI/HTT transport setup, and hardware-specific ops. Most constants are tied to Qualcomm Wi-Fi UMAC blocks: TCL, REO, WBM, CE, RXDMA, LMAC rings, shadow registers, MSI pointer registers, and DSCP/TID tables.

## Important APIs, types, and data
Key exported types are `struct hal_srng`, `struct hal_srng_params`, `struct hal_srng_config`, `struct ath11k_hal_reo_cmd`, `struct hal_reo_status`, and `struct ath11k_hal`. `struct hal_srng` persists per-ring runtime state: ring id, physical/virtual ring base, entry size, interrupt thresholds, MSI address/data, flags, spinlock, register bases, timestamps, direction, source head/reap/tail tracking, or destination tail/head tracking. `struct ath11k_hal` owns the full `srng_list`, the SRNG config table, the remote/write ring pointer DMA regions, REO blocking resource state, shadow register addresses, and lock class keys.

The public API surface includes REO queue descriptor sizing/setup, REO command ring initialization, WBM idle list setup, link descriptor address setting, CE descriptor helpers, SRNG setup/init/deinit/access/read/write helper operations, SRNG shadow configuration, and debug dumping. Ring type and ring id enums define the mapping from driver concepts (`HAL_TCL_DATA`, `HAL_REO_DST`, `HAL_RXDMA_BUF`, `HAL_CE_SRC`, etc.) to hardware ring id ranges.

## Control flow
This header has no executable control flow. It defines the constants and prototypes used by `hal.c`, `hal_rx.c`, `hal_tx.c`, DP RX/TX, CE, and hardware setup code. Register macros often dereference `ab->hw_params.regs`, so the same code can target multiple ath11k chips with different register offsets.

## State and persistence behavior
Persistent runtime state described here is in memory or DMA memory owned by the driver and device. Important mutable state includes SRNG pointer state, shadow pointer memory, `avail_blk_resource`/`current_blk_index`, and per-ring locks. There is no filesystem persistence.

## Dependencies and integration points
`hal.h` depends on `hal_desc.h` and `rx_desc.h`, Linux kernel bit helpers, DMA types, and `struct ath11k_base` hardware parameters. Integration points include DP ring setup, CE descriptor sizing, REO queue/TID setup, REO command processing, MSI/shadow register handling, and hardware register programming.

## Risks
Incorrect register offsets, ring ids, bit masks, or sizes can cause DMA corruption, wedged rings, interrupt storms, or packet loss. Chip-parametric register macros require complete `hw_params.regs` initialization. SRNG state must be accessed through the lock and begin/end protocol. BA window and PN constants must stay aligned with descriptor fields in `hal_desc.h`.

## Test signals
Successful HAL/SRNG setup, clean boot, DP RX/TX traffic, REO command completion, MSI/interrupt delivery, monitor captures, suspend/resume, and sane SRNG debug dumps are the main signals. Compile coverage catches prototype drift, but hardware traffic is needed for register correctness.
