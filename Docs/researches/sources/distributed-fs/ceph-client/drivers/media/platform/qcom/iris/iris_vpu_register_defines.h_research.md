# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_register_defines.h

## Purpose
`iris_vpu_register_defines.h` defines register offsets and bit masks for Iris VPU controller, CPU, wrapper, trust-zone wrapper, AON, interrupt, reset, clock, and NOC low-power control blocks. It is the hardware address contract consumed by `iris_vpu_common.c` and related platform code.

## Important Constants
- Base offsets: `VCODEC_BASE_OFFS`, `CPU_BASE_OFFS`, `WRAPPER_BASE_OFFS`, `WRAPPER_TZ_BASE_OFFS`, `AON_BASE_OFFS`, and `AON_MVP_NOC_RESET`.
- Interrupt registers and masks: `CPU_CS_A2HSOFTINTCLR`, `CPU_CS_H2XSOFTINTEN`, `CPU_IC_SOFTINT`, `WRAPPER_INTR_STATUS`, `WRAPPER_INTR_MASK`, and bit masks for A2H/A2H watchdog.
- Power/clock/reset controls: `CPU_CS_X2RPMH`, `WRAPPER_DEBUG_BRIDGE_LPI_CONTROL/STATUS`, `WRAPPER_IRIS_CPU_NOC_LPI_CONTROL/STATUS`, `WRAPPER_TZ_CTL_AXI_CLOCK_CONFIG`, `WRAPPER_TZ_QNS4PDXFIFO_RESET`, `WRAPPER_CORE_CLOCK_CONFIG`.
- AON/NOC low-power and reset controls: `AON_WRAPPER_MVP_NOC_LPI_CONTROL`, `AON_WRAPPER_MVP_NOC_LPI_STATUS`, `AON_WRAPPER_MVP_NOC_RESET_REQ/ACK`, and status bits `NOC_LPI_STATUS_DONE`, `DENY`, `ACTIVE`.

## Control Flow And Integration
The file has no executable control flow. Callers add these offsets to an MMIO base and use `readl/writel` to drive firmware boot, interrupt clearing, low-power handshakes, debug-bridge control, CPU reset, and clock halt sequences.

## State And Persistence
No software state is stored. The constants identify device register state that persists only as hardware register values across power/reset transitions.

## Dependencies
Depends on `BIT()` and kernel integer macro context. It is included by Iris VPU common code and must match the register map of supported Iris VPU generations.

## Risks
- Incorrect offsets or bit masks can wedge the VPU, fail boot, mask interrupts, or break power-collapse handshakes.
- Register naming mixes wrapper and trust-zone wrapper spaces; callers must choose the proper base for their generation.
- Some status bits are reused in polling conditions; bad polarity assumptions can cause false success or timeout.

## Test Signals
Useful signals include successful firmware boot, host-to-firmware interrupt delivery, watchdog interrupt detection, suspend/resume low-power entry, and no timeout logs from NOC/debug-bridge polling.
