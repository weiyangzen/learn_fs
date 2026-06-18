# sources/distributed-fs/ceph-client/net/psp/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_INET_PSP`, the bool option for kernel PSP Security Protocol support.

## Important APIs, types, and functions
There are no C APIs here. The important configuration interface is `INET_PSP`, which depends on `INET` and selects `SKB_DECRYPTED`, `SKB_EXTENSIONS`, and `SOCK_VALIDATE_XMIT`.

## Control flow and state
When enabled, Kbuild includes the PSP core object aggregate from the Makefile. The selected symbols enable skb extension and transmit-validation infrastructure required by PSP.

## Dependencies and integration points
The option enables networking core PSP support, generic netlink controls, socket association logic, and driver-facing PSP device registration APIs. Help text links to the PSP architecture specification.

## Risks and edge cases
Because PSP changes TCP packet encapsulation/decapsulation behavior and exposes netlink controls, enabling it changes networking security surface. Missing selects would cause build or runtime failures around skb metadata and decrypted-state handling.

## Test signals
Build with `INET_PSP=y` and disabled. Verify selected dependencies, generic netlink family presence, and driver-facing symbol availability.
