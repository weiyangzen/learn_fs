# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/pwrseq.h

Purpose: `pwrseq.h` defines the RTL8723A hardware power-state transition scripts and aliases them to RTL8723 NIC flow names for PCIe use.

Important APIs/data: it documents hardware states POFF, PDN, CARDEMU, ACT, LPS, and SUS. Transition macros encode CARDEMU-to-ACT, ACT-to-CARDEMU, CARDEMU-to-SUS, SUS-to-CARDEMU, card-disable/card-enable, CARDEMU-to-PDN, PDN-to-CARDEMU, ACT-to-LPS, LPS-to-ACT, and `TRANS_END`. It declares all arrays defined in `pwrseq.c` and aliases them as `RTL8723_NIC_PWR_ON_FLOW`, `RTL8723_NIC_RF_OFF_FLOW`, `RTL8723_NIC_DISABLE_FLOW`, `RTL8723_NIC_ENABLE_FLOW`, `RTL8723_NIC_SUSPEND_FLOW`, `RTL8723_NIC_RESUME_FLOW`, `RTL8723_NIC_PDN_FLOW`, `RTL8723_NIC_LPS_ENTER_FLOW`, and `RTL8723_NIC_LPS_LEAVE_FLOW`.

Control flow: the macros are interpreted by `rtl_hal_pwrseqcmdparsing`. Commands perform writes, polling, and delays across MAC, SDIO, USB, and PCI interface masks, though this driver uses the PCI path. LPS entry stops PCIe DMA, pauses TX, polls TX-empty counters, gates BB/MAC clocks, resets MAC TRX, and responds TxOK. LPS leave writes RPWM, delays, switches TSF clocking, enables BB clock and WMAC TRX, and clears TX pause.

State and persistence: state is encoded as immutable command data. Executing it changes hardware power, clock, reset, DMA, TX pause, suspend, and RPWM registers.

Dependencies/integration: includes common `pwrseqcmd.h` and is used by `pwrseq.c` and `hw.c`. Interface masks allow shared definitions across PCI/USB/SDIO, even where this driver is PCI.

Risks: register offsets and bit meanings are hardware-specific and hard to validate statically. Typos in comments and transition names are harmless, but an incorrect command can cause probe or power-save hangs. The card-enable array declaration size references ACT-to-CARDEMU and CARDEMU-to-PDN step counts even though the initializer uses CARDDIS-to-CARDEMU plus CARDEMU-to-ACT, so maintainers should verify capacity if editing.

Test signals: power sequencing should be validated through repeated probe/remove, IPS/LPS cycles, hardware RF-kill, suspend/resume where applicable, and logs from power-sequence polling failures.
