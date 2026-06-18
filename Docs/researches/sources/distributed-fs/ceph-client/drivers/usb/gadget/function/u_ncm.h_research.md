## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_ncm.h

Purpose: defines configfs option storage for the CDC NCM Ethernet gadget function.

Important APIs and types:
- `struct f_ncm_opts` embeds `usb_function_instance`, associated `net_device`, `bind_count`, configfs/OS descriptor group pointers, `ncm_os_desc`, `ncm_ext_compat_id`, `lock`, `refcnt`, and `max_segment_size`.

Control flow and integration:
- NCM configfs setup uses this state to expose networking attributes plus OS descriptors.
- Bind consumes `max_segment_size` and NCM OS descriptor fields while `u_ether` handles the underlying netdev and fixed-size transfer behavior.

State and persistence:
- Per-instance in-memory state; `net` and OS descriptor groups persist while the configfs function exists.

Dependencies:
- USB composite, configfs group types, USB OS descriptor support, and `u_ether`.

Risks:
- NCM fixed IN/OUT transfer sizing must match the `u_ether` `is_fixed` / fixed length fields configured by the NCM implementation.
- Incorrect OS descriptor strings can affect Windows binding.
- `max_segment_size` needs validation against MTU/NCM descriptor limits.

Test signals:
- Enumerate NCM on Linux and Windows-compatible hosts, verify OS descriptors, segment size, and high-throughput traffic.
- Rebind with different `max_segment_size` before active use and confirm configfs rejects live mutation.
