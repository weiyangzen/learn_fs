# sources/distributed-fs/ceph-client/net/atm/addr.h

Purpose: internal header declaring the ATM local address registry interface implemented by `addr.c`.

Important APIs, types, and functions: declares `atm_reset_addr`, `atm_add_addr`, `atm_del_addr`, and `atm_get_addr`, all operating on `struct atm_dev`, `struct sockaddr_atmsvc`, and `enum atm_addr_type_t`.

Control flow: no executable flow. The prototypes define the contract for callers to reset, add, delete, or retrieve per-device ATM addresses.

State and persistence: no state is stored in the header. The state contract is the caller-visible mutation of `atm_dev` address lists.

Dependencies and integration points: includes `<linux/atm.h>` and `<linux/atmdev.h>`, so callers receive ATM socket/device definitions. Used by ATM core files such as `common.c` and ioctl/resource code that need address registry operations.

Risks: since this is a narrow internal header, risk comes from signature drift: changes must be synchronized with `addr.c` and all callers. User pointer annotation on `atm_get_addr` documents that the function performs userspace copy.

Test signals: compile coverage is the main signal; any prototype mismatch will break the ATM composite build. Sparse/usercopy checks should respect the `__user` annotation.
