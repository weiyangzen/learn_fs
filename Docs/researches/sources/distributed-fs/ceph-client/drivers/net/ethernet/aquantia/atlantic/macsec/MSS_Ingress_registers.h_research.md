# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/macsec/MSS_Ingress_registers.h

## Purpose
This header defines MACsec ingress register addresses and bitfield views for ingress control and LUT access.

## Important APIs, types, and functions
Address macros cover `MSS_INGRESS_CTL_REGISTER_ADDR`, ingress LUT address/control registers, and ingress LUT data control base. Structs include `mss_ingress_ctl_register`, `mss_ingress_lut_addr_ctl_register`, and `mss_ingress_lut_ctl_register`.

## Control flow
The header has no executable code. `macsec_api.c` uses it to select ingress pre-control, pre-classification, SA key, SC/SA, post-classification, post-control, and MIB tables, then triggers LUT read/write operations. Counter clearing toggles `clear_count` in the ingress control register.

## State and persistence
The described state persists in MACsec ingress hardware registers. Control fields include soft reset, point-to-point mode, SCI creation, drop policy, ICV checking, SecTAG removal, global validation mode, counter/global-time clear bits, and ICV length mode.

## Dependencies and integration points
This file is paired with egress register definitions and consumed by the MACsec API layer. It relies on the caller to perform MDIO access under the shared MDIO semaphore.

## Risks
Reserved fields and bitfield ordering must be preserved. Incorrect `lut_select` values can target the wrong ingress table. The control register has security-sensitive validation/drop/remove-SecTAG behavior, so any future writer must avoid accidental read-modify-write loss.

## Test signals
Ingress table programming, validation/drop behavior, SecTAG removal behavior, ingress counter reads/clears, and MDIO traces confirm correct use of these definitions.
