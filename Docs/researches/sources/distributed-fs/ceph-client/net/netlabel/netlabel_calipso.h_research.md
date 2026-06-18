# sources/distributed-fs/ceph-client/net/netlabel/netlabel_calipso.h

## Purpose
Private NetLabel CALIPSO interface declaration. It documents the userspace Generic Netlink payload contract and declares the internal CALIPSO wrappers consumed by management, KAPI, and domain-hash code.

## Important APIs, Types, And Functions
Defines `NLBL_CALIPSO_C_*` commands for `ADD`, `REMOVE`, `LIST`, and `LISTALL`, plus `NLBL_CALIPSO_A_DOI` and `NLBL_CALIPSO_A_MTYPE` attributes. Declares `netlbl_calipso_genl_init()` conditionally on IPv6, DOI lifecycle functions, socket/request/sk_buff label functions, `calipso_optptr()`, `calipso_getattr()`, and CALIPSO cache helpers.

## Control Flow
This header is declarative, but it encodes the netlink contract: DOI and mapping type are required for add, DOI is required for remove/list, and dump replies expose DOI/type tuples. When `CONFIG_IPV6` is disabled, `netlbl_calipso_genl_init()` becomes an inline success path so global NetLabel init can proceed without a CALIPSO family.

## State And Persistence Behavior
No state is stored here. The declarations imply externally managed DOI reference ownership: callers that receive a DOI from `calipso_doi_getdef()` must release it with `calipso_doi_putdef()`.

## Dependencies And Integration Points
Includes `net/netlabel.h` and `net/calipso.h`. It is the bridge between NetLabel code and the IPv6 CALIPSO implementation, letting NetLabel build even when CALIPSO packet support is provided elsewhere or compiled out.

## Risks And Test Signals
Risks are contract drift between documented netlink attributes and `netlabel_calipso.c`, missing IPv6 guard coverage, and misuse of DOI references by callers. Test signals include compile coverage with IPv6 enabled and disabled, netlink policy conformance, and sparse/lockdep checks at call sites.
