<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/rtc_cmos_setup.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/rtc_cmos_setup.c

Purpose: Registers a PC-style `rtc_cmos` platform device on PowerPC systems with a compatible CMOS RTC node.

Important APIs/types/functions: Main function is initcall `add_rtc()`.

Control flow: Finds compatible `pnpPNP,b00`, translates its IO resource, verifies it matches hard-coded `RTC_PORT(0)`, optionally adds fixed IRQ 8 when an i8259-compatible interrupt controller is present, and registers `rtc_cmos`.

State and persistence: No global state; the platform device and resources persist after registration.

Dependencies and integration points: Depends on OF address parsing, `asm/mc146818rtc.h` port constants, i8259/CHRP compatible nodes, platform bus, and the generic `rtc_cmos` driver.

Risks: Hard-coded IRQ 8 is correct only for the legacy i8259 numbering assumption described in the comments. If firmware reports a different RTC IO base, the driver refuses to instantiate.

Test signals: CHRP/PReP boot with CMOS RTC, missing interrupt controller node, IO base mismatch, and `rtc_cmos` driver binding.

Source read size: 70 lines, 1645 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/rtc_cmos_setup.c -->
