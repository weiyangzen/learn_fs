<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode_api.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode_api.h

## Purpose

`xe_pcode_api.h` is the internal register and command definition map for PCODE firmware mailboxes, power setup, thermal info, late binding, frequency config, fan control, scratch breadcrumbs, and PCIe capability reporting.

## Important Definitions

The header defines `PCODE_MAILBOX`, `PCODE_DATA0`, `PCODE_DATA1`, mailbox ready and field masks, status/error codes, min-frequency table commands, dGFX init status commands, power-limit commands and fixed-point fields, thermal info subcommands, late-binding capability/version fields, frequency config command/subdomain fields, fan count read command, scratch register layout, boot failure states, auxiliary info fields, and `BMG_PCIE_CAP` link downgrade bits.

## Control Flow and State

This header has no executable control flow. It encodes the ABI used by `xe_pcode.c` and higher-level feature modules to construct PCODE mailbox commands and decode replies. The persistent state represented by these constants is in PCODE firmware and MMIO registers.

## Dependencies and Integration Points

It includes `regs/xe_reg_defs.h` for `XE_REG`, `REG_BIT`, and field-mask helpers. It is marked internal to `xe_pcode` but is included by the public header for the `PCODE_MBOX()` macro and by feature code that needs command constants.

## Risks and Test Signals

Incorrect bitfields directly corrupt firmware commands or reply decoding. Test signals include mailbox command construction tests, power/thermal/frequency feature validation against known firmware replies, and compile-time checks when new PCODE commands are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pcode_api.h -->
