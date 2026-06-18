# sources/distributed-fs/ceph-client/drivers/i3c/master/mipi-i3c-hci/hci_quirks.c

## Purpose

`hci_quirks.c` contains hardware-specific register programming for AMD MIPI I3C HCI platforms. It adjusts open-drain/push-pull timing registers and response-buffer threshold behavior when matching quirks are set.

## Important APIs, Types, and Functions

- AMD timing constants program 9 MHz-related values into `HCI_SCL_I3C_OD_TIMING` and `HCI_SCL_I3C_PP_TIMING`.
- `amd_set_od_pp_timing(struct i3c_hci *hci)` writes OD/PP timing registers and sets the SDA hold/switch delay timing field to the maximum TX hold value.
- `amd_set_resp_buf_thld(struct i3c_hci *hci)` accesses `QUEUE_THLD_CTRL` through the core register helper and clears the response-buffer threshold field.

## Control Flow

Core initialization calls `amd_set_od_pp_timing()` after reset/init if `HCI_QUIRK_OD_PP_TIMING` is set. Bus init calls `amd_set_resp_buf_thld()` if `HCI_QUIRK_RESP_BUF_THLD` is set, after backend initialization has made PIO registers available.

## State and Persistence Behavior

The functions directly mutate hardware registers. The timing values are not cached in software and must be reapplied after resets, which core does during init/resume through the quirk path.

## Dependencies and Integration Points

The file depends on `hci.h` for controller state and is selected through ACPI match data in `core.c` for AMD IDs. It assumes the relevant AMD register offsets are valid for matched hardware.

## Risks and Edge Cases

These writes are platform-specific and bypass generic capability-derived timing calculation. `amd_set_resp_buf_thld()` assumes the AMD threshold register is reachable at the hard-coded core-space offset. Register offsets must track vendor hardware revisions.

## Test Signals

On AMD-matched systems, verify timing registers after probe and resume, response threshold behavior with one response available, and no register writes on non-quirked platforms. Regression tests should cover ACPI quirk matching.
