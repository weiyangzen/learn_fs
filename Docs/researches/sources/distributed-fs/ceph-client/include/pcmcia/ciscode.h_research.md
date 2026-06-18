# sources/distributed-fs/ceph-client/include/pcmcia/ciscode.h

## Purpose

`ciscode.h` provides legacy PCMCIA manufacturer and product ID constants used by drivers and matching tables for known cards.

## Important APIs, types, and functions

The file contains `MANFID_*` and `PRODID_*` macros for vendors and products such as 3Com, Accton, Adaptec, Fujitsu, IBM, Intel, KME, Linksys, Megahertz, Motorola, Nokia, Olicom, Quatech, SMC, Socket, TDK, Xircom, and others. There are no types or functions.

## Control flow

There is no control flow. PCMCIA drivers or match tables compare CIS manufacturer/card IDs against these constants.

## State and persistence behavior

The header owns no state. Constants represent card identity values read from CIS tuples.

## Dependencies and integration points

It has no includes beyond guards and integrates with PCMCIA device ID tables, CIS parsing results, and legacy driver quirks.

## Risks and test signals

Risks include duplicate vendor IDs, product ID typos, and relying only on numeric IDs when product strings or fake CIS overrides are needed. Tests should validate known-card match tables, module alias generation, and behavior for devices with shared manufacturer IDs.
