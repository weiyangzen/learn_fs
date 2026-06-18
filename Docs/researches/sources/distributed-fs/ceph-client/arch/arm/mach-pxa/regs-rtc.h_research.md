<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-rtc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-rtc.h

Purpose: PXA real-time clock register and status bit definitions.

Important definitions: `RCNR`, `RTAR`, `RTSR`, `RTTR`, `PIAR`, periodic interrupt enable/status bits, HZ interrupt enable/status, and alarm enable/status bits.

Control flow and integration: RTC platform devices in `devices.c` expose the same resource range; RTC drivers use these register macros where direct mach access is needed.

State and persistence: RTC count/alarm/trim/status are hardware state, potentially battery-backed depending on board.

Dependencies: includes `pxa-regs.h`.

Risks and test signals: alarm and HZ status bits may require correct write-clear semantics in users. Test RTC read/set, alarm wake, periodic interrupt behavior, and resource registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/regs-rtc.h -->
