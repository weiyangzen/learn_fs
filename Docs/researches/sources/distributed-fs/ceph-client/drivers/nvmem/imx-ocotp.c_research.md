<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp.c -->
# sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp.c

## Purpose
Provides NVMEM access to i.MX6/7/8 OCOTP fuse boxes, including read support, controlled one-word write support, SoC-specific timing, banked addressing, and MAC-address post-processing.

## Important APIs, Types, And Functions
`struct ocotp_params` captures register count, bank addressing, timing callback, and control bit masks. `imx_ocotp_wait_for_busy()`, `imx_ocotp_clr_err_if_set()`, `imx_ocotp_read()`, `imx_ocotp_write()`, `imx_ocotp_set_imx6_timing()`, and `imx_ocotp_set_imx7_timing()` implement hardware access. SoC match tables select parameter sets for i.MX6, i.MX7, and i.MX8 variants, including i.MX8MP alternate control bits.

## Control Flow
Probe maps the controller, obtains the clock, selects parameters, configures legacy fixed OF cells, clears any stale error bit, and registers NVMEM. Reads enable the clock, wait for idle, read shadow/fuse words into a rounded temporary buffer, clear the error bit on read-locked sentinel values, and return the requested bytes. Writes require one aligned word, enable the clock, program timing, wait idle, set address and unlock code, write data registers in banked or non-banked order, wait for completion, delay, reload shadow registers, and return the byte count.

## State And Persistence
Runtime state includes MMIO base, clock, SoC parameters, config pointer, and a global mutex. OTP contents are permanent; shadow registers are reloaded after writes to synchronize runtime reads.

## Dependencies And Integration Points
Depends on platform/OF matching, clocks, MMIO access, NVMEM provider core, fixed OF cells, and Ethernet MAC helper conventions. Consumers use cells for IDs, MAC addresses, calibration, and boot configuration.

## Risks
OTP writes are irreversible and require precise timing. Banked i.MX7 writes depend on writing DATA0 last to trigger programming. Read-locked words set error bits that must be cleared or later operations fail. Static config mutation and global mutex are acceptable for usual single-controller systems but are notable for multi-instance scenarios. Some parameter sets lack a write timing callback, so write use must match supported hardware behavior.

## Test Signals
Read across unaligned byte ranges, read locked words, MAC-address cell reversal, write rejection for unaligned or non-word requests, successful sacrificial word programming, shadow reload completion, timing values across clock rates, and all supported compatible strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvmem/imx-ocotp.c -->
