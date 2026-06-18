# `sources/distributed-fs/ceph-client/include/linux/if_tun.h`

Purpose: internal TUN/TAP access helpers and XDP pointer tagging utilities for the universal TUN driver.

Important APIs/types/functions: `TUN_XDP_FLAG`, `TUN_MSG_UBUF`, `TUN_MSG_PTR`, `struct tun_msg_ctl`, `tun_get_socket`, `tun_get_tx_ring`, `tun_is_xdp_frame`, `tun_xdp_to_ptr`, `tun_ptr_to_xdp`, and `tun_ptr_free`.

Control flow and state: inline helpers encode XDP-frame pointers by setting low bit `TUN_XDP_FLAG`, decode by masking it off, and provide disabled-config stubs returning errors or nulls. Persistent queue state is external to this header.

Dependencies/integration: depends on UAPI TUN and virtio-net headers, optional `CONFIG_TUN`, `struct file`, socket, ptr ring, and XDP frame types.

Risks: pointer tagging assumes XDP frame alignment leaves the low bit clear; callers must distinguish user-buffer vs pointer message types; disabled-config stubs must be handled; `tun_ptr_free` must match the pointer kind.

Test signals: TUN/TAP open and socket retrieval, TX ring access, XDP frame enqueue/free, pointer tag round-trips, disabled-config builds, and virtio-net header interoperability.
