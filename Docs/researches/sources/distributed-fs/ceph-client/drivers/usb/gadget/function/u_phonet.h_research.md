## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/u_phonet.h

Purpose: declares the Phonet USB gadget utility interface and option state.

Important APIs and types:
- `struct f_phonet_opts` embeds `usb_function_instance`, tracks whether the function is `bound`, and points to its `net_device`.
- Declares `gphonet_setup_default()`, `gphonet_set_gadget()`, `gphonet_register_netdev()`, and `gphonet_cleanup()`.

Control flow and integration:
- The Phonet function creates or receives a netdev through `gphonet_setup_default()`, associates it with the gadget, registers it, and cleans it up on instance teardown.
- It parallels `u_ether` patterns but targets Nokia Phonet networking rather than Ethernet framing.

State and persistence:
- In-memory options state per function instance, with netdev lifetime coordinated by bind/unbind.

Dependencies:
- USB composite, CDC constants, and Phonet network implementation outside this header.

Risks:
- Fewer synchronization fields than Ethernet option structs; implementation must externally protect configfs/bind state if mutable.
- Bound/netdev ownership must be unambiguous to avoid netdev leaks.

Test signals:
- Bind Phonet gadget, verify netdev registration and gadget parent assignment, then unbind/cleanup under traffic if supported.
