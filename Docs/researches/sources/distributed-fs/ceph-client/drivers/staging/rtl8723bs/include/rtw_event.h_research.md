<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_event.h -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_event.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_event.h` defines event IDs, event buffer layout, and small event payload structs used for firmware/driver MLME notifications. The source was reviewed as a complete 96-line header for this research item.

## Important APIs, Types, and Functions

Primary declarations and constants: `enum rtw_event` style event IDs, `struct surveydone_event`, `struct joinbss_event`, `struct stassoc_event`, `struct stadel_event`, and event callback table declarations.

## Control Flow

Firmware or command handlers produce event buffers; MLME event callbacks decode them and update scan, join, station, and power-management state.

## State and Persistence Behavior

Event payloads transiently carry network and station information into MLME state machines.

## Dependencies and Integration Points

Integrated with `rtw_cmd.h`, `rtw_mlme.h`, `rtw_mlme_ext.h`, and C2H/event worker code. This header is part of the Realtek rtl8723bs staging driver include layer. Most declarations are consumed by the SDIO HAL, the OS-dependent netdev glue, and the common transmit, receive, MLME, command, security, and station modules.

## Risks and Edge Cases

Event sizes must match command/event dispatch tables. Bad event ordering can leave MLME state linked or scanning incorrectly.

## Test Signals

Survey done, join result, station association/deletion, C2H event dispatch, and malformed/short event handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/include/rtw_event.h -->
