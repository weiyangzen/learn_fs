# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/fw-api.h

## Purpose

`fw-api.h` is the umbrella firmware API header for the iwlwifi MVM implementation. It centralizes inclusion of all MVM firmware command, notification, and data-structure headers so implementation files can include one stable header for firmware ABI definitions.

## Important APIs, Types, And Functions

The file defines no functions or data structures itself. Its important API surface is the include set: TDLS, MAC configuration, offload, context, time-event, datapath, PHY/config/system/alive/binding/command headers, coexistence, D3, filter, LED, MAC, NVM/regulatory, PHY context, power, rate scaling, RX, scan, smart FIFO, station, stats, location, TX, and RFI firmware APIs.

## Control Flow

There is no runtime control flow. Compile-time control is a conventional include guard `__fw_api_h__` wrapping the firmware API include list.

## State And Persistence

No state is declared or persisted. The header only exposes type and constant definitions from lower-level firmware API headers to source files that include it.

## Dependencies And Integration Points

This header is included by files such as `mac-ctxt.c` that need many firmware command layouts. It is tightly coupled to the `drivers/net/wireless/intel/iwlwifi/mvm/fw/api/` header tree and acts as an internal ABI aggregation point between MVM driver code and firmware command definitions.

## Risks And Edge Cases

- Include-order changes can expose missing dependencies in individual firmware API headers.
- Adding broad includes here increases rebuild scope and may hide which specific API a source file actually uses.
- Removing a header can break distant MVM sources that relied on the umbrella include instead of direct includes.

## Test Signals

The main signal is compile coverage of MVM sources that include `fw-api.h`. Header hygiene can be checked by building with warnings enabled and by ensuring firmware command users still resolve all structures, constants, and enum values after include changes.
