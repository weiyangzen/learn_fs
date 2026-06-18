# sources/distributed-fs/ceph-client/net/dns_resolver/Makefile

## Purpose
This Makefile wires the DNS resolver implementation into the kernel build.

## Important APIs, Types, And Functions
`obj-$(CONFIG_DNS_RESOLVER) += dns_resolver.o` builds the composite object when enabled. `dns_resolver-y := dns_key.o dns_query.o` links the key type and query upcall implementation into that object.

## Control Flow
Kbuild includes the directory based on `CONFIG_DNS_RESOLVER`, then compiles and links the two implementation files as one built-in object or module.

## State And Persistence
No runtime state is present; this is purely build metadata.

## Dependencies And Integration Points
The file depends on the Kconfig symbol and Kbuild composite-object conventions. The resulting object exports `dns_query()` and registers the `dns_resolver` key type through the implementation files.

## Risks And Edge Cases
Adding new DNS resolver source files requires updating `dns_resolver-y`; otherwise code may compile in isolation but not link into the module.

## Test Signals
Kbuild smoke tests for built-in and module configurations should verify both `dns_key.o` and `dns_query.o` are included.
