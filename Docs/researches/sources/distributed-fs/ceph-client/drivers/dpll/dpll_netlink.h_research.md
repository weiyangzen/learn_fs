# sources/distributed-fs/ceph-client/drivers/dpll/dpll_netlink.h

## Purpose
This small internal header declares the DPLL netlink notification helpers implemented in `dpll_netlink.c` and used by the core framework when DPLL devices or pins are created or deleted.

## Important APIs
It exposes `dpll_device_create_ntf()`, `dpll_device_delete_ntf()`, `dpll_pin_create_ntf()`, and `dpll_pin_delete_ntf()`. Change-notification helpers are exported directly from the C file and are not declared here.

## Control flow and integration
Callers include DPLL core registration paths. Each function updates core-side notification state and sends a generic-netlink multicast event through `dpll_nl_family`.

## State, dependencies, risks, and tests
The header owns no state and relies on forward declarations from included DPLL core types at the use site. The main risk is declaration drift if notification entry points change. Build coverage of DPLL core plus creation/deletion monitor tests provide the relevant signal.
