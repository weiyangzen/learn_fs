# sources/distributed-fs/ceph-client/arch/m68k/sun3/prom/init.c

## Purpose

initializes Sun-3 PROM access structures and captures firmware entry points for later boot services

## Important APIs, Types, and Functions

Source read size: 36 lines, 821 bytes. Includes: `linux/kernel.h`, `linux/init.h`, `asm/openprom.h`,
`asm/oplib.h`. Defined functions: `prom_init`. Types visible in this file: `linux_romvec`,
`linux_nodeops`, `prom_major_version`.

## Control Flow and Behavior

prom_init() style logic records ROM vectors, initializes console/service hooks, and makes PROM calls
available to platform setup

## State and Persistence

persistent state is the global PROM vector table pointer and derived oplib state

## Dependencies and Integration Points

integrates with Sun-3 head code, openprom/oplib headers, early console, reboot, and IDPROM access

## Risks and Test Signals

wrong vector addresses break every firmware call; early boot console and reboot/halt tests are
signals
