# sources/distributed-fs/ceph-client/drivers/nfc/port100.c

## Purpose
`port100.c` is a USB driver for Sony Port-100/RCS380 NFC readers. It binds Sony USB IDs, speaks the Port-100 extended frame protocol over bulk endpoints, and registers a `nfc_digital_dev` with the kernel digital NFC stack for reader and target-mode operations.

## Important APIs, types, and functions
- `struct port100` owns the USB device/interface, input/output URBs, command completion work, selected command type, and the single in-flight `struct port100_cmd`.
- `struct port100_frame` and `struct port100_ack_frame` model Sony wire frames; helpers such as `port100_tx_frame_init()`, `port100_tx_frame_finish()`, `port100_rx_frame_is_valid()`, and `port100_rx_frame_is_ack()` enforce start-frame, length-checksum, data-checksum, and postamble conventions.
- `port100_send_cmd_async()` is the central command launcher. It wraps a caller payload in a Port-100 frame, allocates a response buffer, installs callbacks, submits the OUT URB, and starts waiting for ACK then response on the IN URB.
- `port100_in_configure_hw()`, `port100_in_send_cmd()`, `port100_tg_configure_hw()`, `port100_tg_send_cmd()`, `port100_listen_mdaa()`, `port100_switch_rf()`, and `port100_abort_cmd()` implement `struct nfc_digital_ops`.
- Static RF/framing tables (`in_rf_settings`, `tg_rf_settings`, `in_protocols`, `tg_protocols`) translate digital-core technologies/framings into Port-100 proprietary settings.

## Control flow
Probe finds USB bulk endpoints, allocates URBs, negotiates a supported command type, logs firmware version, allocates/registers the digital NFC device, and then the digital core drives operations through `port100_digital_ops`. A command follows a strict sequence: build extended frame, submit OUT URB, submit IN URB for ACK, resubmit IN URB for the command response, validate the response command code, and finish in `cmd_complete_work`. Synchronous helpers wait on a completion wrapper around the async callback.

Reader mode configures RF and protocol tables, prepends timeouts to `IN_COMM_RF`, and strips status/collision fields from responses. Target mode builds `TG_COMM_RF` headers, supports MDAA activation checks, and handles target activation masks differently for command type 0 and 1. RF-off calls `port100_abort_cmd()` first, sending a Port-100 ACK frame that cancels the last issued device command and killing the IN URB.

## State and persistence
State is in memory only: command type, one outstanding command, URBs, cancel flag/completion, and registered digital device. There is no persistent storage or firmware file use. The digital stack serializes commands, so the driver only protects the OUT URB and cancellation path with `out_urb_lock`.

## Dependencies and integration points
The file depends on USB core, `net/nfc/digital.h`, sk_buffs, workqueues, and the NFC digital core. It supports Jewel, MIFARE, Felica, NFC-DEP, ISO14443 A/B protocols. USB IDs cover Sony RCS380S and RCS380P.

## Risks
Frame parsing trusts the declared datalen after validation and relies on response buffers sized to `PORT100_FRAME_MAX_PAYLOAD_LEN`. Cancellation merges repeated ACK-cancel attempts through `cmd_cancel`, so races around RF-off and command completion are concentrated there. `port100_get_command_type_mask()` and firmware-version helpers return zero on allocation/command failure, which collapses detailed failure causes during probe. Target-mode parsing assumes responses are at least the proprietary header size; malformed short responses are partially checked but target response length validation is less explicit than reader mode.

## Test signals
Useful tests include USB probe/remove with both product IDs, command type negotiation fallback from type 1 to type 0, checksum rejection for malformed frames, ACK timeout/cancel behavior, RF on/off during an outstanding command, reader exchanges across all configured framings, target-mode MDAA activation timeout handling, and disconnect while a command completion work item is pending.
