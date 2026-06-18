# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/cmd.c

Purpose: Implements wl1251 firmware command mailbox operations and high-level command builders for ACX configure/interrogate, RX/TX data path control, join, power-save mode, templates, scan, and scan timeout.

Important APIs, types, and functions: `wl1251_cmd_send()` is the low-level command path. `wl1251_cmd_interrogate()` and `wl1251_cmd_configure()` wrap ACX reads/writes. Other commands include `wl1251_cmd_vbm`, `wl1251_cmd_data_path_rx`, `wl1251_cmd_data_path_tx`, `wl1251_cmd_join`, `wl1251_cmd_ps_mode`, `wl1251_cmd_template_set`, `wl1251_cmd_scan`, and `wl1251_cmd_trigger_scan_to`.

Control flow: `wl1251_cmd_send()` writes a command buffer to `wl->cmd_box_addr`, triggers `INTR_TRIG_CMD`, polls `ACX_REG_INTERRUPT_NO_CLEAR` until `WL1251_ACX_INTR_CMD_COMPLETE` or timeout, and ACKs completion. ACX interrogate writes an ACX header command then reads the full response back from the mailbox. Scan/join/template helpers allocate packed command structs, fill firmware fields, send the command, and in scan's case read back and validate command status.

State and persistence: Mutates firmware command mailbox and command status. Uses `wl->cmd_box_addr`, `wl->bssid`, `wl->rx_config`, `wl->rx_filter`, and scan/join inputs. No on-disk persistence.

Dependencies and integration points: Depends on memory/register IO, ACX structs/IDs, command IDs from `cmd.h`, power-save constants, cfg80211 channels, and wl1251 core state.

Risks: Polling command completion sleeps in 1 ms increments and can block callers for up to 2 seconds. Buffers must be DMA-compatible and 4-byte aligned. Some fields such as BSSID are reversed for firmware layout. Scan warns but still allocates a fixed max-channel command; callers must respect channel limits.

Test signals: Command timeout/ACK handling, ACX status validation, join on IBSS/BSS, scan completion after `CMD_SCAN`, template truncation at 300 bytes, and RX/TX data path enable/disable around boot and suspend.
