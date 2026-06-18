# sources/distributed-fs/ceph-client/net/nfc/digital.h

## Purpose

`digital.h` is the private header for the NFC Digital Protocol stack. It declares command types, protocol constants, CRC helpers, command-queue APIs, initiator polling APIs, target listen APIs, NFC-DEP data exchange entry points, and shared data-exchange callback state.

## Important APIs, Types, and Functions

Important definitions include `DIGITAL_CMD_IN_SEND`, `DIGITAL_CMD_TG_SEND`, `DIGITAL_CMD_TG_LISTEN`, `DIGITAL_CMD_TG_LISTEN_MDAA`, `DIGITAL_CMD_TG_LISTEN_MD`, maximum digital header/CRC lengths, NFC-DEP SENS/SEL constants, and driver CRC capability macros.

`struct digital_data_exch` stores an NFC core data-exchange callback and context. Declared functions include `digital_skb_alloc()`, `digital_send_cmd()`, `digital_poll_next_tech()`, initiator technology probes, target discovery, ISO-DEP SOD helpers, NFC-DEP ATR/DEP request/responses, target listen handlers, and generic CRC helpers.

## Control Flow

The header ties `digital_core.c`, `digital_dep.c`, and `digital_technology.c` together. Inline wrappers route initiator send, target send, and target listen operations into the common command queue. CRC inline wrappers bind CRC-A, CRC-B, CRC-F, or no-CRC behavior to the generic `digital_skb_add_crc()` and `digital_skb_check_crc()`.

## State and Persistence Behavior

The header itself owns no state, but it defines constants and callback/context shapes used by persistent `struct nfc_digital_dev` state: current CRC handlers, RF technology, command queue, DEP payload/chaining state, and data-exchange callbacks.

## Dependencies and Integration Points

It depends on public NFC headers, digital driver APIs, `crc-ccitt`, and `crc-itu-t`. It is the shared contract between the digital core, protocol activation logic, technology polling/listening code, and lower-level NFC digital drivers.

## Risks and Edge Cases

CRC helper selection must match RF technology and driver capabilities. Command type constants must match `digital_wq_cmd()` dispatch. Header and tailroom constants influence skb allocation in `nfc_digital_allocate_device()`; underestimating them can corrupt packet construction.

## Test Signals

Build `CONFIG_NFC_DIGITAL` with drivers that both do and do not advertise CRC offload. Exercise initiator and target paths for NFC-A, NFC-B, NFC-F, ISO15693, ISO-DEP, and NFC-DEP to verify the declared cross-file APIs remain consistent.
