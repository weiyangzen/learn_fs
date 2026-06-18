# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/goya/goyaP.h

## Purpose

`goyaP.h` is the private header for the Goya ASIC driver implementation. It collects Goya-specific queue counts, timeout constants, memory maps, virtual-address ranges, capability bits, the ASIC-private state structure, and cross-file function prototypes used by `goya.c`, `goya_hwmgr.c`, and `goya_coresight.c`.

## Important APIs, Types, And Data

- Queue topology constants define 5 completion queues, 5 external DMA hardware queues, 1 CPU queue, 9 internal MME/TPC queues, and 6 MSI-X interrupt IDs.
- Timeout constants include QMAN fence/stop waits, CoreSight wait, and CPU communication timeout.
- Default operating constants include enabled TPC mask, high PLL default, max/default DC power, default 4 GiB DRAM size, card name, and max pending command submissions.
- DRAM layout reserves contiguous ranges for CPU firmware image, MMU page tables, the DRAM default page, and MMU cache management, with compile-time validation that driver-reserved DRAM stays below the 512 MiB user base.
- SRAM layout reserves QMAN packet queues for MME and TPC0-7, with compile-time validation against `GOYA_KMD_SRAM_RESERVED_SIZE_FROM_START`.
- Virtual address definitions separate host PMMU space, DDR DMMU space, and a fixed CPU-accessible-memory virtual address.
- `HW_CAP_*` flags track initialized hardware areas such as PLL, DDR, MME, CPU, DMA, MSI-X, CPU queue, MMU, golden registers, TPC MBIST, and TPC.
- `struct goya_work_freq` wraps delayed frequency work with its `hl_device`.
- `struct goya_device` holds the Goya-private runtime state: hardware queue lock, delayed work pointer, saved PLL clock values, DDR BAR cached base, event counters, initialized capability bitmap, CPU-MMU-mapping flag, current PLL profile, and PM management profile.
- Prototypes expose initialization, queue setup, security/error ack, doorbell/PQE/EQ operations, context switch, debugfs I2C/LED hooks, queue tests, CPU messaging, sensors, power, PLL/sysfs, CoreSight, suspend/resume, event handling, CB parser helpers, DMA pool helpers, heartbeat, time, and frequency operations.

## Control Flow

This header does not implement control flow, but it defines the contracts that shape control flow in the other Goya files. `goya.c` owns lifecycle and queue/MMU/firmware paths; `goya_hwmgr.c` implements the PLL and device attribute prototypes; `goya_coresight.c` implements debug and halt prototypes; shared helpers use `struct goya_device` through `hdev->asic_specific`.

## State And Persistence Behavior

The header declares all persistent Goya software state in `struct goya_device`. `hw_cap_initialized` is the main guard against duplicate hardware programming across init/reset phases. `events_stat` and `events_stat_aggregate` preserve per-event accounting. `ddr_bar_cur_addr` persists the current inbound DDR BAR base used by BAR-windowed register/PTE access. Clock and PM profile fields persist user/sysfs power-management choices until reset or driver teardown.

Memory-map constants encode persistent ABI expectations between host driver, device firmware, MMU, and user-visible memory ranges. Compile-time checks protect invalid queue counts, pending-CS sizing, DRAM reservation size, CPU-accessible memory size, and SRAM driver reservation layout.

## Dependencies And Integration Points

The header includes the user ABI (`habanalabs_accel.h`), firmware boot interface, common Habanalabs core header, Goya packet definitions, Goya hardware constants, async event IDs, and firmware interface definitions. It is the coupling point between Goya source files and the generic driver types such as `struct hl_device`, `struct hl_ctx`, `struct hl_cs_parser`, `struct hl_eq_entry`, `struct hl_bd`, `struct hl_debug_params`, and sensor/power enums.

## Risks And Edge Cases

- Constants here are hardware ABI: incorrect queue counts, address ranges, or timeout values can break register programming in `goya.c`.
- The compile-time assertions are important guardrails; changing memory sizes without updating firmware/MMU expectations can overlap user memory or reserved SRAM.
- The shared `struct goya_device` fields are touched from init, IRQ, sysfs, delayed work, reset, and command paths; any future field added here should consider locking and reset semantics.
- `DMA_MAX_TRANSFER_SIZE` is `U32_MAX`, which matches packet transfer-size limits and informs SG coalescing in `goya.c`.

## Test Signals

Header-level validation comes from build-time assertions, successful compilation against all Goya C files, correct struct layout use through `hdev->asic_specific`, and runtime tests that exercise each declared callback through `goya_funcs`. Changes to memory maps should be paired with queue initialization, MMU mapping, and firmware boot tests.
