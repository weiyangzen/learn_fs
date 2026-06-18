# sources/distributed-fs/ceph-client/include/net/netlabel.h

Purpose: Defines the NetLabel kernel API used by LSMs and protocol engines to manage network security labels, domain mappings, CIPSO/CALIPSO DOI configuration, packet/socket label attributes, and caches.

Important APIs/types/functions: Key types are `netlbl_audit`, `netlbl_lsm_cache`, `netlbl_lsm_catmap`, `netlbl_lsm_secattr`, and `netlbl_calipso_ops`. Inline helpers allocate/free/init/destroy secattr caches and sparse category maps. Under `CONFIG_NETLABEL`, APIs configure domain/static/CIPSO/CALIPSO maps, manipulate category maps and bitmaps, set/get/delete labels on sockets, request sockets, connections, and skbs, report skb label errors, check socket locking, invalidate/add caches, start audits, and register CALIPSO operations. Disabled stubs return `-ENOSYS`, neutral values, or no-ops.

Control flow: LSMs build `netlbl_lsm_secattr`, configure mappings through NetLabel generic netlink management, then set labels on sockets or packets. Incoming packets are decoded by protocol engines into secattrs and optionally cached. CALIPSO operations are indirect so IPv6 labeling can be modular.

State and persistence: Mapping tables, DOI definitions, caches, and LSM secattr cache references are runtime kernel state. Secattr structures carry ownership flags for domain/cache/category memory.

Dependencies/integration: Depends on generic netlink, skbuff/socket/request_sock, audit, LSM properties, CIPSO/CALIPSO engines, refcounting, and network namespaces.

Risks/test signals: Watch ownership flags (`FREE_DOMAIN`, `CACHE`, `MLS_CAT`), sparse category map range handling, disabled stub signatures, cache refcount/free callbacks, and socket lock expectations. Test SELinux/Smack labeling, CIPSO/CALIPSO add/remove/map, IPv4/IPv6 skb set/get, cache invalidation, malformed netlink management messages, and module registration/unregistration.
