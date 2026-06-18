<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/target.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/target.h

## Purpose
`target.h` defines target memory/register addresses, bit masks, host-interest layout offsets, board data sizes, virtual-to-physical address macros, and debug log structures shared by ath6kl boot, diagnostic, firmware-log, SDIO, and recovery code.

## Important APIs, Types, And Constants
Board size constants distinguish AR6003 and AR6004 board and extended-board data. Register constants cover reset, CPU/system sleep, LPO calibration, GPIO pins, interrupt status/enable registers, counters, mailbox window data/address registers, scratch area, base addresses, and an analog PLL register with unknown real name.

`SM()` and `MS()` pack/unpack bitfields using matching `_S` shift constants. `struct host_interest` is a packed offset-only ABI description of the firmware host-interest area, with fields for app host area, failure state, debug log header, option flags, board data addresses, UART/refclock settings, reserved RAM, mailbox block size and yield limit, extended board data, reset flags, test app flags, testscript location, and more. `HI_ITEM()` produces offsets into that ABI.

Mode/submode constants encode firmware interface mode, P2P submode, VIF count, and bridge/MAC-address option shifts. `TARG_VTOP()` maps AR6003 virtual addresses by masking and leaves AR6004 addresses unchanged. `struct ath6kl_dbglog_buf` and `struct ath6kl_dbglog_hdr` describe firmware debug log rings.

## Control Flow
This header has no runtime flow by itself, but its constants drive flow in several files. `init.c` writes sleep, clock, GPIO, board, app-start, and host-interest fields during boot. `main.c` uses host-interest offsets and debug log structures to read firmware logs. `sdio.c` uses window and counter addresses for diagnostic access and BMI credits.

## State And Persistence
The header models persistent firmware ABI state in target RAM but stores no state itself. The most important persistence rule is structural: `struct host_interest` positions must remain stable across firmware revisions because host code computes offsets rather than sharing C instances with firmware.

## Dependencies And Integration Points
It integrates with `core.h` target type/version definitions, BMI/diagnostic operations, firmware binaries, and bus backends. Any change here can affect boot across SDIO and USB because both use the same host-interest and diagnostic abstractions.

## Risks
ABI drift is the primary risk. Reordering or resizing `struct host_interest` fields would break firmware communication. Endianness matters for debug log structures but host-interest offsets are raw 32-bit target fields. `TARG_VTOP()` returns zero for unknown target types, which can silently convert invalid target types into address zero if callers do not validate first.

## Test Signals
Validation signals are indirect: successful board upload, WMI ready event, firmware log extraction, diagnostic reads/writes, BMI mailbox credit behavior, and reset behavior. Tests should compare offsets against firmware documentation or known-good builds and exercise AR6003 versus AR6004 address conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/target.h -->
