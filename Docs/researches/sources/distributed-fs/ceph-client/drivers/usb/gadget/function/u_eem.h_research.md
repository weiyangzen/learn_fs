## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_eem.h

Purpose: defines option storage for the CDC EEM Ethernet gadget function.

Important APIs and types:
- `struct f_eem_opts` mirrors the ECM/subset option pattern: `usb_function_instance`, associated `net_device`, `bound`, `bind_count`, `lock`, and `refcnt`.

Control flow and integration:
- The EEM function uses this object as its configfs instance state, borrowing or registering a `u_ether` netdev and using bind counters to coordinate multi-configuration binding.
- EEM-specific framing is handled by the function driver through `struct gether` wrap/unwrap hooks declared in `u_ether.h`.

State and persistence:
- Kernel-resident configfs instance state; no on-disk persistence.
- `net` points to the Ethernet-over-USB link that outlives individual `usb_function` allocations for the same instance.

Dependencies:
- USB composite APIs and the EEM function implementation's use of `u_ether`.

Risks:
- As with ECM, stale `bound`/`bind_count` state risks netdev lifecycle imbalance.
- EEM framing depends on correct wrap/unwrap configuration outside this header.

Test signals:
- Configfs bind/unbind cycles for EEM with traffic through the created netdev.
- Multi-configuration binding should not produce duplicate network interfaces for one options instance.
