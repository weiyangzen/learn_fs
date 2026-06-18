<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/Makefile -->
# sources/distributed-fs/ceph-client/net/netlabel/Makefile

## Purpose
`net/netlabel/Makefile` defines the object composition for the NetLabel subsystem.

## Important APIs, Types, and Functions
The Makefile always includes base objects `netlabel_user.o`, `netlabel_kapi.o`, `netlabel_domainhash.o`, and `netlabel_addrlist.o`, management object `netlabel_mgmt.o`, protocol objects `netlabel_unlabeled.o` and `netlabel_cipso_v4.o`, and conditionally includes `netlabel_calipso.o` when `CONFIG_IPV6` is enabled after `subst m,y`.

## Control Flow, State, and Persistence
There is no runtime control flow. The build state determines which object files become part of the NetLabel built-in object list. IPv6 controls CALIPSO inclusion.

## Dependencies and Integration Points
This file integrates NetLabel source units with kbuild and mirrors the Kconfig boolean nature by using `obj-y`. It binds address-list, domain-hash, management, unlabeled, CIPSO, and CALIPSO implementation files into one subsystem.

## Risks and Test Signals
Risks include missing object additions when new NetLabel source files are introduced, CALIPSO being absent in non-IPv6 builds, and assuming modular object behavior. Tests should cover builds with IPv6 enabled/disabled, symbol availability for all listed objects, and dependency changes in Kconfig reflected here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netlabel/Makefile -->
