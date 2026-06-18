# sources/distributed-fs/ceph-client/drivers/platform/mellanox/mlxbf-tmfifo-regs.h

## Purpose
Register-layout header for the BlueField TMFIFO driver. It defines TX/RX data, status, and control offsets and bit fields for legacy BlueField layouts and BlueField-3 split-resource layouts.

## Important APIs, Types, And Constants
Constants describe TX/RX `DATA`, `STS`, and `CTL` offsets, FIFO count masks, low/high watermark fields, max-entry fields, reset values, and BF3-specific offsets. The driver uses `MLXBF_TMFIFO_*__COUNT_MASK` to read FIFO occupancy, `*_CTL__MAX_ENTRIES_MASK` to size queues, and `*_CTL__LWM/HWM_MASK` to program interrupt thresholds.

## Control Flow
No executable control flow exists here. `mlxbf-tmfifo.c` chooses either legacy offsets or BF3 offsets based on ACPI UID, then performs `readq()` and `writeq()` against the defined locations.

## State, Dependencies, Integration, Risks, Tests
The header represents the hardware ABI. It depends on Linux `types.h` and `bits.h` for fixed-width and `GENMASK_ULL` helpers. Integration is direct with TMFIFO MMIO and interrupt watermark programming. Risks are layout drift between SoC generations, incorrect masks causing wrong FIFO capacity or watermarks, and duplicated RX/TX data offsets in legacy resources that rely on caller resource selection. Test signals include BF3 UID mapping, FIFO size discovery, threshold writes, occupancy reads, and compile-time use by the TMFIFO driver.
