# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/pwrseq.h

## Purpose

`pwrseq.h` describes RTL8188EE hardware power-state transitions in the `struct wlan_pwr_cfg` macro format consumed by the shared rtlwifi power-sequence parser. It documents the six hardware states and defines step counts, transition command macros, external arrays, and NIC-flow aliases.

## Important APIs, Types, And Constants

The transition macros include `RTL8188EE_TRANS_CARDEMU_TO_ACT`, `RTL8188EE_TRANS_ACT_TO_CARDEMU`, `RTL8188EE_TRANS_CARDEMU_TO_SUS`, `RTL8188EE_TRANS_SUS_TO_CARDEMU`, `RTL8188EE_TRANS_CARDEMU_TO_CARDDIS`, `RTL8188EE_TRANS_CARDDIS_TO_CARDEMU`, `RTL8188EE_TRANS_CARDEMU_TO_PDN`, `RTL8188EE_TRANS_PDN_TO_CARDEMU`, `RTL8188EE_TRANS_ACT_TO_LPS`, `RTL8188EE_TRANS_LPS_TO_ACT`, and `RTL8188EE_TRANS_END`. Each entry encodes register offset, cut/fab/interface masks, base address, command type, bit mask, and value. Extern declarations expose the arrays defined in `pwrseq.c`, and `RTL8188EE_NIC_*` aliases provide the names used by hardware code.

## Control Flow

The header itself does not execute; it expands into data initializers. At runtime `rtl_hal_pwrseqcmdparsing()` walks the generated arrays. Write commands update registers, polling commands wait for masked values, delay commands sleep for microseconds or milliseconds, and `PWR_CMD_END` terminates a flow.

## State And Persistence Behavior

The macro arrays encode transitions that persist in hardware power state: enabling/disabling WL suspend, resetting BB/MAC, pausing TX, polling TX queues idle, switching TSF/BB clocks, setting RPWM for SDIO/USB/PCIe, entering low-power state, and driving power-down bits. They do not allocate driver state themselves.

## Dependencies And Integration Points

The header depends on `../pwrseqcmd.h` for command constants and masks. It is included by `pwrseq.c` to instantiate arrays and by `hw.c` through flow aliases used during MAC init and adapter poweroff. Although many entries include USB/SDIO masks, this RTL8188EE PCIe driver selects PCIe-specific behavior through parser interface masks.

## Risks And Test Signals

The macros contain hardware-document magic values; small edits can make the NIC fail to wake, sleep, or power down. Step-count definitions must stay aligned with macro entry counts and extern array sizes. Comments mention RTL8723 in the include guard and PCIe section despite RTL8188EE content, which is cosmetic but can confuse maintenance. Tests should parse every alias flow with PCIe masks, validate that each reaches `RTL8188EE_TRANS_END`, and run suspend/resume, IPS, LPS, NIC enable, and NIC disable cycles on hardware.
