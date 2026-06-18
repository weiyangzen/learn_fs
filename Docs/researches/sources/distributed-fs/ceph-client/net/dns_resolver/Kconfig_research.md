# sources/distributed-fs/ceph-client/net/dns_resolver/Kconfig

## Purpose
This Kconfig file defines the `DNS_RESOLVER` tristate option for the kernel DNS resolver key type.

## Important APIs, Types, And Functions
The single option is `config DNS_RESOLVER`, labelled "DNS Resolver support". It depends on `KEYS`, can be built in or as module `dns_resolver`, and documents the userspace request-key upcall helper.

## Control Flow
When selected, the build includes `net/dns_resolver/` and enables DNS lookup upcalls through the kernel key retention service. Consumers such as CIFS and AFS can request keys of type `dns_resolver`.

## State And Persistence
The Kconfig option has no runtime state. It controls whether the module/key type exists in the kernel build.

## Dependencies And Integration Points
The explicit dependency is `KEYS`; practical integration is with `/sbin/dns.resolver`, `/etc/request-key.conf`, CIFS, AFS, and `Documentation/networking/dns_resolver.rst`.

## Risks And Edge Cases
Enabling this without a matching userspace helper means DNS lookups fail at runtime despite the kernel type existing. If built as a module, consumers need module loading to work.

## Test Signals
Build tests should cover `DNS_RESOLVER=y`, `m`, and disabled configurations, plus runtime request-key upcalls for CIFS/AFS style descriptions.
