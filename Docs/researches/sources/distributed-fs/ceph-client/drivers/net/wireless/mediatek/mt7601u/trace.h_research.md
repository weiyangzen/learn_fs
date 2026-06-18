# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/trace.h

Purpose: Declares MT7601U tracepoints for register access, USB URBs, MCU messages, vendor requests, EEPROM reads, RF/BBP access, temperature and frequency calibration, RX/TX descriptors, TX DMA/status, RX DMA aggregation, and key operations.

Important APIs and types: Defines reusable event classes such as `dev_reg_evtu`, `dev_rf_reg_evt`, `dev_bbp_reg_evt`, and `dev_simple_evt`. Events include `reg_read`, `reg_write`, `mt_submit_urb`, `mt_mcu_msg_send`, `mt_vend_req`, `ee_read`, `rf_read`, `rf_write`, `bbp_read`, `bbp_write`, `temp_mode`, `read_temp`, `freq_cal_adjust`, `freq_cal_offset`, `mt_rx`, `mt_tx`, `mt_tx_dma_done`, `mt_tx_status_cleaned`, `mt_tx_status`, `mt_rx_dma_aggr`, `set_key`, and `set_shared_key`.

Control flow: Tracepoints are passive callsite hooks. The header records selected arguments into trace entries with `TP_fast_assign` and formats them using `TP_printk`. `trace_mt_submit_urb_sync()` creates a stack `urb` shim to reuse the URB event for synchronous bulk transfers.

State and persistence: Trace events snapshot transient values: wiphy name, registers, descriptor fields, skb/station pointers, MCU checksum, firmware response state, and calibration values. They do not mutate driver state.

Dependencies and integration points: Includes `linux/tracepoint.h`, `mt7601u.h`, and `mac.h`; sets `TRACE_SYSTEM mt7601u`; includes `trace/define_trace.h` under the expected trace include path. Used across USB, MCU, PHY, RX, TX, EEPROM, and key code.

Risks: Tracepoint structs copy driver descriptors; changes to descriptor definitions must keep trace fields valid. The `mt_mcu_msg_send` event casts `skb->data` to `u32 *`, so callers must ensure command skb data is at least a descriptor word and aligned enough for the architecture or use-safe access. High-frequency tracing can add overhead if enabled.

Test signals: Enable each event under tracefs while exercising probe, register reads/writes, scan/channel changes, TX/RX, key setup, and calibration. Build tests catch stale field names after descriptor changes.
