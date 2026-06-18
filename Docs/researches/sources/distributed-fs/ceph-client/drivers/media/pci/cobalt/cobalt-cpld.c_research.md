<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.c

Purpose: Provides Cobalt CPLD access, board status reporting, and programmable HSMA output clock setup through the CPLD/SI570-style oscillator registers.

Important APIs/functions: `cobalt_cpld_status()` reads CPLD revision and prints supported revision 3/4/5 status via `cpld_info_ver3()`. `cobalt_cpld_set_freq()` finds a valid oscillator multiplier, computes RFREQ/hsdiv/n1 register values, writes SI570 registers, triggers the write/reset sequence, verifies readback, and returns whether the requested output frequency is in range. Internal helpers `cpld_read()` and `cpld_write()` use Cobalt bus accessors.

Control flow: Status is invoked from V4L2 log-status. Output streaming calls `cobalt_cpld_set_freq()` before programming the HSMA output sync generator. Frequency programming searches the multiplier table for a DCO within 4.85-5.67 GHz with minimal remainder error, writes six oscillator registers, toggles clock-control bits, and retries readback mismatch up to three times.

State/persistence: CPLD and oscillator register values persist in hardware while powered/configured. Driver software keeps no cache. Status reads board serial, program revision, temperatures, and voltage ADC values.

Dependencies/integration: Uses `cobalt_bus_read32()`/`cobalt_bus_write32()` from `cobalt-driver.h`, Cobalt logging macros, and Cobalt output setup in `cobalt-v4l2.c`.

Risks: Large hard-coded multiplier table and timing-sensitive write/reset sequence. `cobalt_cpld_set_freq()` returns true even after all retries are exhausted, as long as a candidate frequency was found, so readback failure is only logged/debugged. Voltage conversions are integer approximations.

Test signals: V4L2 log-status CPLD output, output streaming at common HDMI pixel clocks, invalid pixelclock rejection, oscillator register readback, retry logging, and scope/monitor validation of HSMA clock frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-cpld.c -->
