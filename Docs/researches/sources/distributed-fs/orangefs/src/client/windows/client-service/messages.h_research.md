# sources/distributed-fs/orangefs/src/client/windows/client-service/messages.h

## Purpose
`messages.h` is a generated Microsoft Message Compiler/ETW header for the OrangeFS Windows client provider. It gives service code macros for registering an ETW provider and writing info/error events.

## Important APIs, Types, And Functions
The provider is `OrangeFS-Client-Provider` with GUID `cd75d1d2-a19b-4c81-a8a9-629fcd2fd998`. It defines channel `WINEVENT_CHANNEL_GLOBAL_APPLICATION`, descriptors `INFO_EVENT` and `ERROR_EVENT`, provider context `PROVIDER_GUID_Context`, registration macros `EventRegisterOrangeFS_Client_Provider` and `EventUnregisterOrangeFS_Client_Provider`, enabled checks, and write macros `EventWriteINFO_EVENT` and `EventWriteERROR_EVENT`.

## Control Flow
Service startup calls the register macro through `init_event_log`; shutdown calls unregister. Error reporting calls `EventWriteERROR_EVENT(message)`. Generated helpers manage enable callbacks, event bit masks, provider registration handles, and `EVENT_DATA_DESCRIPTOR` packing for a single ANSI string payload.

## State And Persistence
Runtime ETW state is held in global generated context variables and registration handles. Events are persisted/consumed by Windows ETW/Event Log infrastructure, not by this file.

## Dependencies And Integration Points
The header depends on Windows ETW headers such as `wmistr.h`, `evntrace.h`, and `evntprov.h`. `service-main.c` includes it for event registration and error logging.

## Risks And Test Signals
The file is generated; manual edits risk divergence from the manifest. The write template uses `strlen` on the message pointer and emits `"NULL"` when absent. If the provider is not registered, writes become effectively no-ops. Tests in `client-test` do not validate ETW emission; service startup/error tests or Event Viewer inspection would be needed.
