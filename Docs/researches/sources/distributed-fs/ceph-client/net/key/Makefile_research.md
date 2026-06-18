# sources/distributed-fs/ceph-client/net/key/Makefile

## Purpose
Builds the PF_KEY key management socket implementation when enabled.

## Important APIs, types, and functions
The Makefile rule is `obj-$(CONFIG_NET_KEY) += af_key.o`, tying `CONFIG_NET_KEY` to the `af_key` object.

## Control flow
No runtime control flow. Kbuild includes or omits `af_key.o` according to the configuration.

## State and persistence behavior
No runtime state. It affects only build composition.

## Dependencies and integration points
Integrates the networking key-management subsystem with the kernel build. PF_KEY is commonly used by IPsec/XFRM key management, making this build switch relevant to the neighboring XFRM files in this work item.

## Risks and test signals
Risks are limited to build configuration and unresolved object dependencies. Test `CONFIG_NET_KEY=m/y/n` builds and IPsec key-management users that expect PF_KEY sockets when enabled.
