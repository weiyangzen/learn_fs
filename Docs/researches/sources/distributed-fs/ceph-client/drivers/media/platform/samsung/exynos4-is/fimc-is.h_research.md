# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is.h

## Purpose
`fimc-is.h` is the central internal header for the Exynos4x12 FIMC-IS driver. It defines firmware filenames, memory layout, clock ids, driver state bits, autofocus state enums, firmware/memory/setfile/command/config structures, the main `struct fimc_is`, MMIO accessors, memory barriers, parameter dirty-bit helpers, and core function prototypes.

## Important APIs, Types, and Functions
Important constants include `FIMC_IS_DRV_NAME`, firmware and setfile filenames, firmware load/power timeouts, sensor count, CPU memory size, debug/shared/region offsets, firmware metadata lengths, firmware size bounds, and ISP clock frequencies. Key enums define `ISS_CLK_*` ids and `IS_ST_*` state bits. Key structures include `struct fimc_is_firmware`, `struct fimc_is_memory`, `struct i2h_cmd`, `struct h2i_cmd`, `struct fimc_is_setfile`, `struct chain_config`, and `struct fimc_is`. Inline helpers include `fimc_isp_to_is()`, `__get_curr_is_config()`, `fimc_is_mem_barrier()`, `fimc_is_set_param_bit()`, `fimc_is_set_param_ctrl_cmd()`, `mcuctl_read/write()`, and `pmuisp_read/write()`.

## Control Flow
The header does not own top-level flow, but its inline helpers are used throughout the driver. Register helpers perform raw MMIO reads/writes against mapped MCUCTL and PMU bases. Parameter helpers mark dirty bits in the active `chain_config`. `fimc_is_mem_barrier()` enforces ordering before firmware consumes shared memory.

## State and Persistence
`struct fimc_is` defines the persistent in-kernel state for one platform device lifetime. State bits represent firmware power, sensor open, setfile loaded, init done, stream on/off, mode changes, command completion, zoom, and sub-IP power. Firmware memory and shared parameter pointers are valid only after successful asynchronous firmware allocation.

## Dependencies and Integration Points
The header includes clock, platform, spinlock, V4L2 controls, vb2, ISP subdevice, command, sensor, parameter, and register headers. It binds FIMC-IS core code to ISP video/control, sensor lookup, register mailbox, and parameter update modules.

## Risks and Edge Cases
The main struct mixes sleepable mutex-protected state, spinlock-protected IRQ/MMIO state, firmware-owned DMA memory, and async firmware-loading state; callers must respect locking and readiness. Dirty-bit operations assume `config_index` is valid. MMIO accessors do no range checking. Firmware memory offsets are hard-coded ABI values and must fit inside the allocated CPU memory.

## Test Signals
Compile coverage across all FIMC-IS modules, state-bit transitions during firmware boot and stream commands, MMIO register traces, parameter dirty-bit marking, memory barrier placement before mailbox commands, debug/shared-region offsets, and cleanup after partial probe failures are the main validation signals.
