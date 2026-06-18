<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.c

Purpose: shared MCU message layer for MMIO mt76x02 devices. It sends command SKBs through the MCU TX queue, parses sequence-tagged responses, exposes common function/power/calibration commands, drains response queues, and formats firmware version strings.

Important APIs/types/functions: `mt76x02_mcu_msg_send()`, `mt76x02_mcu_parse_response()`, `mt76x02_mcu_function_select()`, `mt76x02_mcu_set_radio_state()`, `mt76x02_mcu_calibrate()`, `mt76x02_mcu_cleanup()`, and `mt76x02_set_ethtool_fwver()`.

Control flow: send allocates an MCU skb, takes the MCU mutex, assigns nonzero 4-bit sequence, writes FCE command info, queues to `q_mcu[MT_MCUQ_WM]`, then optionally drains responses until the matching sequence arrives or timeout. Calibration on MT76x2E clears and polls a COM register bit around the command.

State and persistence: updates `mcu.msg_seq`, `mcu_timeout`, response queue contents, firmware version in wiphy, and hardware radio/calibration state.

Dependencies/integration: mt76 MCU helpers, MMIO TX queues, mt76x02 DMA bitfields, firmware loaders, PCI watchdog restart, and mt76x2 channel/PHY calibration.

Risks: sequence wrap, stale responses, timeout poisoning through `mcu_timeout`, queue failure while mutex held, and calibration COM-bit polling. Test signals include command timeout/recovery, radio on/off, calibration commands, firmware restart, response sequence mismatch, and cleanup draining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.c -->
