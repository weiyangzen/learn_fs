<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vhost_net_test.c -->
# sources/distributed-fs/ceph-client/tools/virtio/vhost_net_test.c

## Purpose

Exercises `/dev/vhost-net` using a TAP device and raw packet socket. It verifies TX and RX packet movement through vhost-net with selectable virtio features and interrupt behavior.

## Important APIs, Types, and Functions

Source size: 532 lines, 11699 bytes. Functions/classes: tun_alloc, vdev_create_socket, vdev_send_packet, vq_notify, vhost_vq_setup, vq_reset, vq_info_add, vdev_info_init, wait_for_interrupt, verify_res_buf, run_tx_test, while, if, while, if, run_rx_test, while, if, plus 5 more. Includes: getopt.h, limits.h, string.h, poll.h, sys/eventfd.h, stdlib.h, assert.h, unistd.h, sys/ioctl.h, sys/stat.h, sys/types.h, fcntl.h, stdbool.h, linux/vhost.h, linux/if.h, linux/if_tun.h, linux/in.h, linux/if_packet.h, plus 2 more. Macros/defines: _GNU_SOURCE, HDR_LEN, TEST_BUF_LEN, TEST_PTYPE, DESC_NUM.

## Control Flow and Data Flow

The program creates a TAP with vnet headers, opens an AF_PACKET socket, prepares a loopback Ethernet payload, opens `/dev/vhost-net`, installs the memory table and feature bits, attaches queue backends, then runs TX by adding outbufs and RX by adding inbufs plus sending packets into the TAP.

## State and Persistence Behavior

`struct vdev_info` stores the virtio device, two queues, TAP/socket metadata, MAC address, test/result buffers, and vhost memory. Each `vq_info` tracks started/completed counts and eventfds.

## Dependencies and Integration Points

This file is integrated at `sources/distributed-fs/ceph-client/tools/virtio`. It depends on the adjacent Linux source tree, generated build outputs, or runtime devices implied by its includes and neighboring Makefiles. Its outputs are consumed by the rvgen monitor generator, virtio/vhost userspace tests, initramfs build pipeline, drgn diagnostics, WMI sample tool, or common KVM core according to its directory.

## Risks and Edge Cases

Requires privileges, `/dev/net/tun`, `/dev/vhost-net`, and a usable networking namespace. Hardcoded packet type and one-buffer-at-a-time loops make it a correctness smoke test more than a full throughput tool.

## Test Signals

Run with event index, indirect, virtio-1 toggles, delayed interrupts, and varied buffer counts; verify payload bytes and lengths for both TX and RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/virtio/vhost_net_test.c -->
