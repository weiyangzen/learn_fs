# sources/distributed-fs/ceph-client/net/netlabel/netlabel_mgmt.h

## Purpose
Private ABI declaration for the NetLabel management Generic Netlink family and shared configured-protocol counter.

## Important APIs, Types, And Functions
Defines management commands for add/remove/listall/default operations, protocol enumeration, and version query. Defines attributes for domain, protocol, version, CIPSO DOI, CALIPSO DOI, IPv4/IPv6 addresses and masks, address selector nesting, selector list nesting, and family. Declares `netlbl_mgmt_genl_init()` and `netlabel_mgmt_protocount`.

## Control Flow
No executable control flow. The comments specify required request and reply payloads, including how selector-list mappings differ from direct protocol mappings and how default operations can optionally target a family.

## State And Persistence Behavior
The header exposes `netlabel_mgmt_protocount`, a global atomic used to decide whether NetLabel is enabled. Command/attribute enum values are persistent userspace ABI.

## Dependencies And Integration Points
Includes `net/netlabel.h` and atomic primitives. Used by management implementation, KAPI enable checks, DOI handlers, and unlabeled static-label code.

## Risks And Test Signals
Risks include ABI drift, misspelled/documented selector requirements diverging from code, and protocol count misuse by non-management components. Test signals are userspace compatibility, netlink policy coverage, and compile checks across IPv6 configurations.
