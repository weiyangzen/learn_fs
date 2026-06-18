# sources/distributed-fs/openafs/src/WINNT/afsreg/test/getifinfo.c

## Purpose
Manual test utility for `syscfg_GetIFInfo`. It prints detected usable IPv4 addresses and subnet masks for the local machine.

## Important APIs, Types, And Functions
The file defines fixed arrays `addrs`, `masks`, `mtus`, and `flags` with `MAXIPADDRS` capacity, plus `main` that calls `syscfg_GetIFInfo`, converts host-order addresses back to dotted decimal with `htonl` and `inet_ntoa`, and prints the results.

## Control Flow
The program initializes `rxi_numNetAddrs` to 16, calls the system-configuration API, reports failure if it returns negative, otherwise prints the number of usable addresses and iterates the filled entries.

## State And Persistence
No persistent state is changed. It reads host network configuration indirectly through `syscfg_GetIFInfo` and writes output to stdout.

## Dependencies And Integration Points
It includes WinSock2 and `WINNT/syscfg.h`, and links with the syscfg implementation and networking libraries. It provides a quick runtime signal for the registry/IP-helper code.

## Risks And Test Signals
The file uses old-style `main` without an explicit return type and has an accidental nested comment opener near the header comment, both compile-style risks depending on compiler strictness. Runtime test signal is the printed interface list compared against `ipconfig`/adapter configuration.
