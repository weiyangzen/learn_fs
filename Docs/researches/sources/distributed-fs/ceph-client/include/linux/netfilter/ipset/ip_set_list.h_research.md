# sources/distributed-fs/ceph-client/include/linux/netfilter/ipset/ip_set_list.h

## Purpose
This header supplies size limits for list-based ipset implementations.

## Important APIs, Types, and Functions
It defines `IP_SET_LIST_DEFAULT_SIZE` 8, `IP_SET_LIST_MIN_SIZE` 4, and `IP_SET_LIST_MAX_SIZE` 65536. There are no functions or structs.

## Control Flow
List set create paths use these constants to validate or default requested list capacity.

## State and Persistence
No state is declared. Constants constrain runtime list set storage.

## Dependencies and Integration Points
It includes the uapi list ipset header and is consumed by list set type implementations.

## Risks
Boundary validation must reject under-minimum and over-maximum sizes. Large lists can have lookup and dump costs.

## Test Signals
Create list sets with absent, minimum, below-minimum, maximum, and above-maximum size attributes; test add/delete/list behavior near capacity.
