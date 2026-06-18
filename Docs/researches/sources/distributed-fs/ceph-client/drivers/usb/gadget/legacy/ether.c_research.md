# sources/distributed-fs/ceph-client/drivers/usb/gadget/legacy/ether.c

## Purpose

`ether.c` implements the legacy `g_ether` ethernet gadget. It provides CDC ECM, CDC subset/gether, CDC EEM, and optionally RNDIS configurations depending on Kconfig, controller capability, and module parameters.

## Important APIs, Types, and Functions

Core functions are `eth_bind()`, `eth_do_config()`, `rndis_do_config()`, `eth_unbind()`, and `has_rndis()`. It uses function instances for `"ecm"`, `"eem"`, `"geth"`, and `"rndis"`, gether helpers for MAC addresses, queue multiplier, netdev registration, and RNDIS netdev sharing through `rndis_borrow_net()`.

## Control Flow

Bind chooses the primary non-RNDIS mode: EEM if requested, ECM if the UDC supports it, otherwise CDC subset/gether. It obtains that function instance, applies ethernet module parameters, and, when RNDIS is compiled in, registers the shared netdev, obtains a RNDIS instance, borrows the same netdev, updates product IDs, and exposes two configurations with RNDIS first. It then allocates strings, optional OTG descriptor, adds RNDIS config if present, and adds the ethernet config. Config callbacks instantiate and add the selected function.

## State and Persistence Behavior

State is global per module: function instances/functions, static descriptors, `use_eem`, optional OTG descriptor, and network module parameters. The lower-level gether/netdev layer owns packet queues, MAC state, and link lifecycle. No persistent storage is used.

## Dependencies and Integration Points

The file depends on libcomposite, Linux networking, `u_ether`, `u_ecm`, `u_gether`, `u_eem`, optional `u_rndis`/`rndis`, and gadget capability detection. Host integration varies by configuration: CDC ECM/EEM, subset/SAFE, or RNDIS.

## Risks and Test Signals

Risks include mode-selection differences across UDCs, shared-netdev ownership when RNDIS and ECM/subset coexist, cleanup when one config add fails, host-driver compatibility tied to vendor/product IDs, and `use_eem` changing expected descriptors. Tests should cover ECM-capable and non-ECM controllers, EEM module parameter, RNDIS and non-RNDIS builds, MAC parameter validation, simultaneous host network traffic, config switching, OTG descriptors, and unload after interface up/down cycles.
