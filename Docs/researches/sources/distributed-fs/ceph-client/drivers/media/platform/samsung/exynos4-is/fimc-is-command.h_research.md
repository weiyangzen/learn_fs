# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-command.h

## Purpose
`fimc-is-command.h` defines the mailbox command protocol between the host CPU and the FIMC-IS firmware running on the ISP Cortex-A5, plus packed register-layout structures for the shared MCU control mailbox block.

## Important APIs, Types, and Functions
Host-to-IS commands include scenario changes, stream on/off, parameter set/get, tune/status, sensor open/close, power down, setfile address/load, and message test/config commands. IS-to-host commands include sensor count requests, shot/face marks, frame done, AA done, not-ready, and reply done/not-done. `enum fimc_is_scenario` selects preview/capture still/video configurations. `struct is_common_regs` and `struct is_mcuctl_reg` model the common ISSR mailbox and interrupt/control register area.

## Control Flow
There is no executable flow. `fimc-is.c` and `fimc-is-regs.c` write command ids and arguments into `MCUCTL_REG_ISSR(n)` registers using these constants, then signal firmware with an interrupt generation register. The IRQ handler decodes firmware replies using the same constants.

## State and Persistence
No software state is stored here. The packed structures describe volatile MMIO layout and firmware ABI state.

## Dependencies and Integration Points
The header is included by the FIMC-IS core, register, and parameter paths. Its numeric values must match the firmware command-set version `FIMC_IS_COMMAND_VER`.

## Risks and Edge Cases
Any command id or packed layout mismatch breaks host/firmware synchronization. The header provides fixed four-argument common register arrays, while some driver-side structures allow more decoded arguments, so call sites must respect the actual hardware mailbox fields they read.

## Test Signals
Validate firmware boot handshake (`IHC_GET_SENSOR_NUM`), sensor open/close, setfile address/load, mode changes for all scenarios, stream on/off replies, set-parameter completion, not-done error reporting, and register dumps matching the expected ISSR layout.
