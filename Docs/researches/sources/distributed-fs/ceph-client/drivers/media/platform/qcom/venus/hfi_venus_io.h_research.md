# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_venus_io.h

This header defines Venus hardware register offsets, bit masks, base offsets, and timeouts used by the HFI transport and PM helpers. It is the register ABI for CPU control/status, interrupt controller, wrapper, VBIF, vcodec power, TrustZone wrapper, and always-on wrapper blocks.

Important groups include VBIF halt registers, CPU CS queue/control registers (`VIDC_CTRL_INIT`, `CPU_CS_SCIACMDARG*`, `SFR_ADDR`, `UC_REGION_*`), soft interrupt registers, wrapper interrupt status/mask/clear registers, CPU halt/status/reset registers, memory protection range registers, v4 vcodec power registers, v6 core power registers, TrustZone CPU status/reset registers, and AON MVP NOC LPI registers.

Control flow is external. `hfi_venus.c` uses these constants to boot firmware, signal host-to-controller interrupts, clear firmware interrupts, halt AXI for powerdown, poll idle/PC-ready status, and read hardware version. `pm_helpers.c` uses vcodec power-control/status offsets for v3/v4 core power sequencing.

The header has no persistent state. Dependencies are Linux bit macros and exact SoC register maps. Integration points are all low-level hardware access paths in Venus HFI and PM code.

Risks are severe because wrong offsets or masks can hang hardware or break suspend/resume. Generation-specific constants are easy to misuse: v6 and v4-lite soft interrupt and watchdog bits differ from older cores. Test signals include successful boot register programming, interrupt delivery/clearing, AXI halt polling, vcodec power-domain transitions, runtime suspend/resume, and hardware-version logging.
