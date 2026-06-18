# sources/distributed-fs/ceph-client/include/uapi/linux/ipmi.h

## Purpose
`ipmi.h` defines the multi-user IPMI character-device ABI for sending commands, receiving responses/events, registering command handlers, and configuring per-interface address, LUN, timing, and maintenance behavior.

## Important APIs, Types, and Functions
Address overlays include `ipmi_addr`, `ipmi_system_interface_addr`, `ipmi_ipmb_addr`, `ipmi_ipmb_direct_addr`, and `ipmi_lan_addr`. Message types are `ipmi_msg` for userspace pointers and `kernel_ipmi_msg` for kernel pointers. Request/receive structures include `ipmi_req`, `ipmi_req_settime`, and `ipmi_recv`. Ioctls include send, timed send, receive/truncating receive, register/unregister command, channel-scoped registration, event subscription, get/set channel address and LUN, legacy address/LUN controls, timing parameters, and maintenance mode.

## Control Flow
Userspace opens an IPMI device, sends an addressed message with a `msgid`, waits via poll/select, then receives matching responses or async events. Registration ioctls route incoming commands to specific users. The driver handles retries, timeout responses, event-queue polling, and lower-interface routing.

## State and Persistence
Open-file users have queues and registrations. Interface-wide state includes source address, LUN, timing parameters, event handling, and maintenance mode. BMC event state is external and periodically drained by the driver.

## Dependencies and Integration Points
It includes `ipmi_msgdefs.h` and `<linux/compiler.h>`. It integrates with IPMI system interfaces, IPMB/LAN channels, BMC event queues, poll/select, and server management tools.

## Risks and Test Signals
Tests should validate user pointers, address length/type matching, response correlation by `msgid`, timeout completion codes, event fanout, registration conflicts, channel masks, and receive truncation semantics. ABI risk is pointer-bearing structs and global interface controls that affect all users.
