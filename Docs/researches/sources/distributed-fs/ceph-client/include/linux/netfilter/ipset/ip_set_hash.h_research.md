# sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_hash.h

## Purpose
This header supplies default sizing parameters for hash-based ipset implementations.

## Important APIs, Types, and Functions
Constants are `IPSET_DEFAULT_HASHSIZE` 1024, `IPSET_MIMINAL_HASHSIZE` 64, `IPSET_DEFAULT_MAXELEM` 65536, `IPSET_DEFAULT_PROBES` 4, and `IPSET_DEFAULT_RESIZE` 100. The misspelling `MIMINAL` is part of the exposed macro name.

## Control Flow
Hash set implementations use these defaults during create-attribute parsing and resize/probing decisions. There are no functions.

## State and Persistence
No state is declared. Constants shape in-memory hash table allocation and growth.

## Dependencies and Integration Points
It includes the uapi hash ipset header and integrates with hash set type modules.

## Risks
Defaults affect memory consumption and lookup performance. Changing them can alter userspace-visible behavior and stress resize paths. Consumers must preserve the existing macro spelling.

## Test Signals
Create hash sets with omitted and explicit sizing attributes, fill to `maxelem`, trigger collision/probe and resize behavior, and validate memory use under default and minimum hash sizes.
