<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-dbc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psp-dbc.h

Purpose: defines the userspace ioctl ABI for AMD Dynamic Boost Control through the Platform Security Processor.

Important APIs and types: fixed sizes define nonce, signature, and UID buffers. `struct dbc_user_nonce`, `struct dbc_user_setuid`, and `struct dbc_user_param` are packed ioctl payloads for nonce exchange, UID programming, and parameter get/set. `DBCIOCNONCE`, `DBCIOCUID`, and `DBCIOCPARAM` use ioctl type `'D'`. `enum dbc_cmd_msg` identifies Fmax cap, power cap, graphics mode, current temperature, min/max limits, and current SoC power queries.

Control flow: userspace requests a nonce, optionally authenticates, sets a UID once, then sends signed parameter commands. The PSP validates signatures/state and returns parameter values or updated signatures.

State and persistence: PSP/driver state includes nonce validity, UID programming, mailbox state, and dynamic boost parameters. UID is documented as set once until reboot; boost limits affect platform power/performance until changed/reset.

Dependencies and integration points: depends on Linux types and ioctl macros through consumers. Integrates with AMD PSP mailbox driver, firmware authentication, power management, and platform tuning tools.

Risks and test signals: risks include authentication bypass, replayed nonce/signature, packed-struct ABI mistakes, mailbox recovery races, and unsafe power cap values. Test nonce one-shot vs authenticated reuse, UID set-once enforcement, signature failure, invalid message IDs, timeout/busy paths, and parameter bound checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-dbc.h -->
