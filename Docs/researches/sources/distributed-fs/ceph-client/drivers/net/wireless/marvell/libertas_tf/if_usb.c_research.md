# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/if_usb.c

## Purpose
Implements USB transport and firmware loading for the mac80211/thinfirm Libertas 8388 driver. It mirrors much of the full Libertas USB Boot2 protocol but routes normal data, command responses, and events into `lbtf_*` thinfirm core callbacks.

## Important APIs And Functions
`if_usb_probe()` finds endpoints, allocates RX/TX/CMD URBs and output buffer, then calls `lbtf_add_card()` with `if_usb_ops`. `if_usb_ops` provides `hw_host_to_card`, `hw_prog_firmware`, and `hw_reset_device`. Firmware paths include `if_usb_prog_firmware()`, `if_usb_receive_fwload()`, `if_usb_send_fw_pkt()`, `if_usb_issue_boot_command()`, `check_fwfile_format()`, and `if_usb_fw_timeo()`. Runtime paths include `if_usb_receive()`, `process_cmdtypedata()`, `process_cmdrequest()`, `if_usb_host_to_card()`, `usb_tx_block()`, and `if_usb_submit_rx_urb()`.

## Control Flow And State
Probe creates transport state but the thinfirm core owns startup through `hw_prog_firmware`. Firmware download requests `lbtf_fw_name`, validates block format, submits an RX URB for Boot2 responses, retries boot commands, sends sequenced firmware blocks, handles CRC feedback, waits on `fw_wq`, kills the firmware RX URB, releases firmware, and then calls `if_usb_setup_firmware()`. Normal receive parses the 4-byte type header: data is passed to `lbtf_rx()`, command responses are copied into `priv->cmd_resp_buff` and signaled with `lbtf_cmd_response_rx()`, and indications become TX feedback or beacon-sent notifications. It uses separate `tx_urb` for data and `cmd_urb` for commands.

## Dependencies And Integration
Depends on Linux USB and firmware APIs plus `libertas_tf.h` command/mac80211 core. Exposes module parameter `fw_name` and declares `MODULE_FIRMWARE("lbtf_usb.bin")`.

## Risks And Test Signals
Risks include missing URB anchoring compared with full USB driver, static firmware reset retry count, command/data URB reuse while prior transfers are pending, firmware load error paths that still call setup after `release_fw`, and lack of suspend/resume support. Test signals include firmware request by parameter name, Boot2 response handling, CRC retry, firmware-ready wait, command response processing, data RX into mac80211, TX feedback/beacon events, disconnect reset, and module unload cleanup.
