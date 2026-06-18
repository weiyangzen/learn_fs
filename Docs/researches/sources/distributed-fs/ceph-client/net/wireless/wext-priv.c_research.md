# sources/distributed-fs/ceph-client/net/wireless/wext-priv.c

Purpose: implements Wireless Extensions private ioctl support for legacy drivers, including private command discovery, argument sizing, userspace copy wrappers, and compat `iw_point` translation.

Important APIs/functions: `iw_handler_get_private()` returns the driver `iw_priv_args` table for `SIOCGIWPRIV`; `ioctl_private_call()` and `compat_private_call()` invoke private handlers. Helpers `get_priv_size()`, `adjust_priv_size()`, `get_priv_descr_and_size()`, and `ioctl_private_iw_point()` compute inline versus extra-buffer payload handling.

Control flow: `SIOCGIWPRIV` validates that private metadata exists and either returns `-E2BIG` with the needed count or copies the table into the core-allocated extra buffer. Private dispatch searches the driver private descriptor matching the command, derives SET or GET payload size, treats fixed arguments fitting in `ifr_name` as inline, otherwise allocates an extra buffer, copies SET data from userspace, calls the driver handler, adjusts variable GET return size, and copies results back.

State and persistence: no durable state is owned here. The code reads driver-provided private descriptor arrays and may trigger `call_commit_handler()` when a private handler returns `-EIWCOMMIT`.

Dependencies and integration: called from `wext-core.c` under RTNL and permission checks. It depends on `net_device->wireless_handlers`, `struct iw_priv_args` encoding, WEXT private ioctl numbering, usercopy helpers, and optional compat support.

Risks and test signals: the private ABI is descriptor-driven and fragile when drivers misdeclare fixed/variable sizes or sub-ioctl names. Tests should cover `SIOCGIWPRIV` sizing hints, inline fixed arguments, pointer payload SET/GET, variable-length GET truncation, invalid or missing descriptors, compat pointer conversion, and commit-handler propagation.
