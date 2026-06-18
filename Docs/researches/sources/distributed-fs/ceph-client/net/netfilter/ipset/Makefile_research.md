# sources/distributed-fs/ceph-client/net/netfilter/ipset/Makefile

## Purpose

This Makefile builds the IP set core and selected set-type modules. It is intentionally compact because most type behavior is in individual modules and generic template headers.

## Important Build Rules

`ip_set-y := ip_set_core.o ip_set_getport.o pfxlen.o` builds the core `ip_set` module from the nfnetlink management code, layer-4 port extraction helpers, and prefix-length helpers. `obj-$(CONFIG_IP_SET) += ip_set.o` emits the core. Bitmap modules map directly to `ip_set_bitmap_ip.o`, `ip_set_bitmap_ipmac.o`, and `ip_set_bitmap_port.o`.

Hash modules map to their configured type objects, including `ip_set_hash_ip.o`, `ip_set_hash_ipmac.o`, `ip_set_hash_ipmark.o`, `ip_set_hash_ipport.o`, `ip_set_hash_ipportip.o`, `ip_set_hash_ipportnet.o`, `ip_set_hash_mac.o`, `ip_set_hash_net.o`, `ip_set_hash_netport.o`, `ip_set_hash_netiface.o`, `ip_set_hash_netnet.o`, and `ip_set_hash_netportnet.o`. `IP_SET_LIST_SET` builds `ip_set_list_set.o`.

## Control Flow And State

Kbuild evaluates `obj-$(CONFIG_...)` to decide which objects are built in or modular. There is no runtime state in the Makefile, but it defines the module boundaries used by module autoloading. The core module always includes `ip_set_getport.o`, even if a port-specific set type is not selected, because exported helpers may be shared by configured types.

## Dependencies And Integration

The file must match `ipset/Kconfig` and the source files present in the directory. It integrates with the parent netfilter Makefile through `obj-$(CONFIG_IP_SET) += ipset/` and with module aliases in each type source, such as `ip_set_hash:ip` or `ip_set_bitmap:port`.

## Risks

A missing build mapping makes a configured type unavailable. A stale mapping causes build failures if a source file is moved or removed. Because `ip_set-y` composes the core module, adding shared helpers without updating this list can create unresolved symbols in type modules.

## Test Signals

Build with all ipset options as modules and built-ins. Confirm `modprobe ip_set`, `modprobe ip_set_hash_ip`, `modprobe ip_set_bitmap_ip`, and related aliases work. Runtime `ipset create` commands for every configured type should trigger module loading and successful nfnetlink type registration.
