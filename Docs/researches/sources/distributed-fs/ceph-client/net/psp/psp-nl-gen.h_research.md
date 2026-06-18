# sources/distributed-fs/ceph-client/net/psp/psp-nl-gen.h

## Purpose
`psp-nl-gen.h` is the generated header for the PSP generic netlink family. It declares policies, operation callback prototypes, multicast group indexes, and the external family object.

## Important APIs, types, and functions
The header declares `psp_keys_nl_policy`, pre/post callbacks `psp_device_get_locked()`, `psp_assoc_device_get_locked()`, and `psp_device_unlock()`, command handlers for device get/set, key rotate, RX/TX association, and stats get/dump, plus `enum { PSP_NLGRP_MGMT, PSP_NLGRP_USE }` and `extern struct genl_family psp_nl_family`.

## Control flow and state
There is no runtime control flow. The declarations connect generated op-table entries in `psp-nl-gen.c` with implementation functions in `psp_nl.c` and registration in `psp_main.c`.

## Dependencies and integration points
The header includes generic netlink and UAPI PSP definitions. It is included by `psp_main.c` and implementation files that need the family or policy declarations.

## Risks and edge cases
Like the generated C file, it should not be edited directly. Prototype drift from implementations or YAML regeneration can break builds or ABI behavior. Multicast group enum ordering must match the generated family group array.

## Test signals
Build coverage catches prototype mismatches. Regeneration tests should compare generated output. Runtime netlink tests validate that callback implementations line up with declared command handlers.
