# sources/distributed-fs/ceph-client/tools/testing/selftests/nci/nci_dev.c

Purpose: Exercises the Linux NFC/NCI stack through the virtual NCI device. It verifies device initialization/deinitialization, polling, target activation, AF_NFC raw socket connection, and Type 4 Tag read exchanges for both NCI 1.0 and NCI 2.0 command sequences.

Important APIs/types/functions: Uses generic netlink (`NETLINK_GENERIC`, `CTRL_CMD_GETFAMILY`, NFC generic netlink commands), `/dev/virtual_nci`, `IOCTL_GET_NCIDEV_IDX`, AF_NFC `SOCK_SEQPACKET` sockets, and kselftest harness fixtures. Helpers include `create_nl_socket()`, `send_cmd_mt_nla()`, `get_family_id()`, `send_cmd_with_idx()`, `get_nci_devid()`, `get_dev_enable_state()`, version-specific virtual-device responders (`virtual_dev_open*`, `virtual_deinit*`), polling helpers, tag discovery helpers, `read_write_nci_cmd()`, `read_tag()`, and `disconnect_tag()`.

Control flow: Fixture setup opens a generic netlink socket, resolves the NFC family and multicast group, opens `/dev/virtual_nci`, subscribes to events, gets the virtual device index, asserts the device is down, starts a responder thread, and sends `NFC_CMD_DEV_UP`. The responder reads exact NCI reset/init/discovery-map commands from the virtual device and writes canned responses. Tests then query state (`init`), start/stop polling (`start_poll`), simulate RF activation and Type 4 Tag APDU reads (`t4t_tag_read`), and explicitly power the device down (`deinit`). Teardown powers down the device if still open and closes descriptors.

State and persistence behavior: Fixture state tracks `virtual_nci_fd`, generic netlink socket, family id, pid, device index, protocol mask, NCI version, and whether the device is open. Kernel state under test includes NFC device powered state, poll state, target records, and AF_NFC socket lifecycle. No persistent files are written.

Dependencies and integration points: Requires `CONFIG_NFC`, `CONFIG_NFC_NCI`, `CONFIG_NFC_VIRTUAL_NCI`, NFC generic netlink, `/dev/virtual_nci`, pthreads, and kselftest harness. Integrates UAPI structures from `<linux/nfc.h>` and generic netlink headers.

Risks: The test uses exact byte-for-byte NCI command expectations, so benign kernel protocol changes can break it. Generic netlink attribute parsing is manual and lightly bounds-checked. Several helper functions return `0` on family lookup failure even though valid family id zero is unlikely; assertions only compare against `-1`. Thread status is cast through `void **`, which is conventional in this test but type-fragile. Closing `virtual_nci_fd` to test closed-device behavior leaves fixture teardown to handle `-1`.

Test signals: Passing assertions show device power transitions, NCI 1.0/2.0 startup handshakes, polling start/stop commands, target discovery, AF_NFC connect, APDU request/response flow, and down-state behavior. Failures identify mismatched NCI bytes, missing virtual device support, generic netlink errors, or unexpected powered state.
