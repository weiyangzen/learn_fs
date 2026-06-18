<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi_regs.h

## Purpose
`intel_sbi_regs.h` defines MMIO register addresses and bitfields for the display Sideband Interface plus commonly used sideband offsets for spread-spectrum clocking and DBUF configuration.

## Important APIs, Types, And Functions
This header is macro-only. It defines `SBI_ADDR`, `SBI_DATA`, `SBI_CTL_STAT`, address/data/command/status masks, destination encodings for ICLK and MPHY, operation encodings, response/status values, and sideband offsets such as `SBI_SSCDIVINTPHASE`, `SBI_SSCDIVINTPHASE6`, `SBI_SSCDITHPHASE`, `SBI_SSCCTL`, `SBI_SSCCTL6`, `SBI_SSCAUXDIV6`, `SBI_DBUFF0`, and `SBI_GEN0`.

## Control Flow
There is no executable control flow. `intel_sbi.c` uses the command/status macros to drive transactions, while refclock code uses the offset and field macros to update specific sideband registers.

## State And Persistence Behavior
The macros describe hardware-visible state. Values written through SBI persist in the target sideband registers until changed by software, firmware, reset, or power transitions.

## Dependencies And Integration Points
The header includes `intel_display_reg_defs.h` for `_MMIO`, `REG_BIT`, `REG_GENMASK`, and field helpers. It is included by `intel_sbi.c`, PCH refclock code, GVT MMIO tables, and virtualization handlers.

## Risks
Incorrect operation/destination encoding can make all SBI transactions fail or access the wrong sideband target. Several older field macros use raw shifts rather than `REG_FIELD_PREP`, so callers must avoid mixing pre-shifted and unshifted values incorrectly.

## Test Signals
Signals include successful SBI read/write transactions, correct SSC/refclock programming, no `SBI_RESPONSE_FAIL` logs, and GVT register emulation coverage for the defined MMIO registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi_regs.h -->
