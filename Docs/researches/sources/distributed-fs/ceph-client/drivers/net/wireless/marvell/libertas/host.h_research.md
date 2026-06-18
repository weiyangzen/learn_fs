# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/host.h

## Purpose
Defines the full-firmware Libertas host/firmware ABI: command ids, return-command conventions, action constants, event codes, packet descriptors, TLV structures, and packed command payloads. It is the common contract used by the core command path, mesh support, and SDIO/SPI/USB transports when building requests and parsing firmware responses.

## Important APIs, Types, And Constants
Important constants include `CMD_RET()`, `CMD_*` command ids, `CMD_ACT_*` actions, power-save actions, SNMP MIB oids, mesh access/config enums, and firmware event ids such as `MACREG_INT_CODE_FIRMWARE_READY`. `struct txpd` and `struct rxpd` are the data-plane descriptors placed before transmitted and received payloads. `struct cmd_header` is the common command header used by all command payloads. The many `cmd_ds_*` packed structs represent firmware commands for scan, association, MAC control, multicast, sleep, power, radio, EEPROM, key material, mesh, forwarding table, wake-on-LAN, and hardware specification.

## Control Flow And State
This header has no executable control flow, but it drives runtime dispatch: transport drivers identify command/data/event packets, core code fills `cmd_header` and command-specific structs, and response paths validate return ids against `CMD_RET(command)`. Fields are explicitly little-endian or big-endian where the firmware ABI requires it.

## Dependencies And Integration
Includes `types.h` and `defs.h`, and depends on Linux 802.11/Ethernet definitions through those headers. It is consumed by `main.c`, `cmd.c`, `rx.c`, `tx.c`, `mesh.c`, and bus-specific files. The packed layout is firmware-visible and should be treated as a binary interface.

## Risks And Test Signals
Primary risks are ABI drift, endian mistakes, variable-length array misuse, and accidental changes to packed structs such as `adhoc_bssdesc`, which explicitly forbids adding fields. Test signals include successful firmware `GET_HW_SPEC`, association/scan command responses, valid RX/TX descriptor parsing, mesh start/stop behavior, and suspend/resume power commands across firmware revisions.
