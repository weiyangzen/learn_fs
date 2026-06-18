# sources/distributed-fs/ceph-client/drivers/bluetooth/virtio_bt.c

## Purpose
Implements a generic virtio Bluetooth HCI driver. It maps HCI packets to two virtqueues, registers an HCI device with optional vendor-specific setup behavior, and supports virtio feature bits for vendor HCI, Microsoft extensions, AOSP extensions, and v2 config layout.

## Important APIs, Types, And Functions
`struct virtio_bluetooth` stores the virtio device, TX/RX virtqueues, RX work item, and HCI device. Core helpers are `virtbt_add_inbuf()`, `virtbt_open_vdev()`, `virtbt_close_vdev()`, `virtbt_send_frame()`, `virtbt_rx_work()`, `virtbt_tx_done()`, `virtbt_rx_done()`, `virtbt_probe()`, and `virtbt_remove()`. Vendor setup functions include Zephyr build-info/BDADDR, Intel read-version/BDADDR, Realtek ROM-version, and a generic reset shutdown callback.

## Control Flow
Probe requires `VIRTIO_F_VERSION_1`, checks that the config type is primary, allocates state, finds TX/RX virtqueues, allocates and configures an HCI device, applies optional vendor setup callbacks and quirks based on virtio config, registers the HCI device, marks the virtio device ready, and posts the initial RX buffer. Sending prepends the HCI packet type and queues the skb as an outbuf. RX completion schedules work, which gets one used RX buffer, validates length and packet type/header size, hands valid frames to `hci_recv_frame()`, replenishes the RX buffer, and kicks the RX queue.

## State And Persistence
State is volatile: virtqueue buffers, pending RX work, and HCI device metadata. Vendor features are read from virtio configuration and reflected in HCI callbacks/quirks. No state is persisted.

## Dependencies And Integration Points
The driver binds to `VIRTIO_ID_BT`, uses UAPI `virtio_bt` config/vendor constants, the virtio queue API, and Bluetooth core HCI registration. It also integrates with Zephyr, Intel, and Realtek vendor HCI command conventions when the device advertises vendor HCI support.

## Risks And Test Signals
Risks include failing to replenish RX buffers, accepting malformed virtqueue lengths, feature/config version mismatches, missing cleanup on probe error, and vendor-specific setup commands blocking registration. Test signals include virtio probe/remove cycles, frame loopback through TX/RX queues, malformed packet rejection logs, vendor feature negotiation, and HCI registration with correct bus type and quirks.
