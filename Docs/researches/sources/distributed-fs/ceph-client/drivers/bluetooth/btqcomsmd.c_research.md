# sources/distributed-fs/ceph-client/drivers/bluetooth/btqcomsmd.c

## Purpose
Implements a Qualcomm WCNSS SMD/RPMSG Bluetooth HCI transport. It opens separate command/event and ACL channels to the remote WCNSS firmware, registers an HCI device on `HCI_SMD`, forwards incoming RPMSG payloads as HCI frames, sends outgoing HCI command/ACL packets over the matching channel, resets the controller during setup, and delegates BD address programming to QCA Rome helpers.

## Important APIs, Types, And Functions
- `struct btqcomsmd` stores the HCI device and the two RPMSG endpoints.
- `btqcomsmd_acl_callback` and `btqcomsmd_cmd_callback` are RPMSG receive callbacks for ACL data and events.
- `btqcomsmd_recv` allocates an skb in IRQ context, assigns HCI packet type, copies payload, and submits it to `hci_recv_frame`.
- `btqcomsmd_send` routes `HCI_ACLDATA_PKT` to `acl_channel` and `HCI_COMMAND_PKT` to `cmd_channel`.
- `btqcomsmd_setup` sends HCI reset and sets `HCI_QUIRK_USE_BDADDR_PROPERTY`; `btqcomsmd_set_bdaddr` calls `qca_set_bdaddr_rome` and sleeps for firmware recovery.
- `btqcomsmd_probe`/`remove` manage endpoint and HCI lifetime.

## Control Flow
Probe obtains the parent WCNSS controller data, opens the ACL and CMD channels, allocates an HCI device, installs callbacks, registers the device, and stores driver data. Incoming RPMSG channel callbacks increment RX byte counts and call the shared receive allocator. Outgoing HCI packets are sent immediately over the selected endpoint and freed only on success. Setup sends a reset to synchronize the controller and marks the BD address as firmware-node-provided. Remove unregisters/frees HCI first, then destroys command and ACL endpoints.

## State And Persistence
State is minimal and persists for platform-device lifetime: two endpoints and one HCI device. The remote firmware owns controller state and packet buffering. HCI stats are updated for RX/TX/errors. BD address persistence is absent on these devices, so the HCI quirk records that the firmware node property should supply it.

## Dependencies And Integration Points
Depends on rpmsg, Qualcomm WCNSS control channel opening, platform/OF matching, Bluetooth HCI core, and `btqca.h` for Rome BD address commands. It integrates with device tree compatible `qcom,wcnss-bt` and parent WCNSS infrastructure that exposes named SMD channels.

## Risks And Edge Cases
Callbacks run in IRQ context and use `GFP_ATOMIC`; allocation failures increment only error stats. `btqcomsmd_send` does not free skb on send failure, relying on caller/error handling expectations. Only command and ACL packet types are supported; SCO/ISO are rejected. Firmware is known to pause after BD address programming, requiring an arbitrary sleep before subsequent commands.

## Test Signals
Probe failure cleanup for first/second channel open and HCI registration, RX event/ACL delivery through both RPMSG callbacks, TX routing and stats for command/ACL packets, unsupported packet rejection, HCI reset during setup, BD address command plus post-command delay, and remove destroying endpoints after HCI unregister.
