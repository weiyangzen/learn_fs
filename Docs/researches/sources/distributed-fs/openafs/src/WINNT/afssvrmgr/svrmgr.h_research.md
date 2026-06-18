# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svrmgr.h

Purpose: central umbrella header for AFS Server Manager, defining common constants, persistent preference structs, globals, includes, and core lifecycle helpers.

Important API/types: defines registry locations, size constants, pending fileset suffixes, `CHILDTAB`, `DISPLAYINFO`, `SERVER_PREF`, `SERVICE_PREF`, `AGGREGATE_PREF`, `FILESET_PREF`, `ICONVIEW`, `GLOBALS`, and `GLOBALS_RESTORED`. Declares global `g` and `gr`, plus `Quit`, `PumpMessage`, and `StartThread`.

Control flow contract: most source files include this header to share app state, resource IDs, task interfaces, help helpers, and preference structures. Preference version macros (`wVerSERVER_PREF`, etc.) are used by save/restore helpers to validate persisted binary blobs.

State and persistence: the structs here are the durable state model: global window/view preferences in `GLOBALS_RESTORED`, and per-object alert/view/status preferences on server/service/aggregate/fileset identities. Registry keys are under `HKCU`.

Dependencies/integration: includes `windows.h`, `AfsAppLib.h`, `AfsClass.h`, resource/help headers, and major manager modules. It later includes `task.h` and `helpfunc.h`, making it a broad dependency root.

Risks/test signals: binary persistence structs are versioned but layout changes can break old settings if versions are not bumped. Header breadth increases coupling and rebuild scope. Tests should check default initialization, restore fallback when versions mismatch, and object preference save/load compatibility.
