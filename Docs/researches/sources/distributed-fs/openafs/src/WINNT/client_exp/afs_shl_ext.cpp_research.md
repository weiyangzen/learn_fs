# sources/distributed-fs/openafs/src/WINNT/client_exp/afs_shl_ext.cpp

Purpose: MFC DLL application and COM self-registration implementation for the OpenAFS Explorer shell extension.

Important APIs/functions: `CAfsShlExt` constructor, `InitInstance`, `DllGetClassObject`, `DllCanUnloadNow`, `WideCharToLocal`, `DoRegCLSID`, `DllRegisterServer`, `DoValueDelete`, and `DllUnregisterServer`.

Control flow: app construction starts Winsock. Initialization loads localized resources, registers OLE factories, and sets help path. COM exports delegate to MFC. Registration writes CLSID `InprocServer32` entries, threading model, shell icon overlay identifiers, approved shell-extension entries, context menu handlers, info-tip handler, and property sheet handlers for files/drives/directories. Unregistration removes corresponding keys/values.

State/persistence: persistent effects are registry writes under HKCR and HKLM. `DllCanUnloadNow` intentionally returns `S_FALSE`, keeping the extension loaded to avoid reload issues.

Dependencies/integration: depends on MFC OLE factories, Explorer shell extension registry contracts, OpenAFS resource/help modules, WinSock, `afsreg`, and architecture-specific interface IIDs.

Risks: `DoRegCLSID` closes the passed root key handle even when it is a predefined key. `DoValueDelete` opens a subkey but deletes values against the root key, likely wrong. Registration duplicates some work and requires elevation for HKLM/HKCR. Permanent `S_FALSE` can keep stale code loaded.

Test signals: regsvr32 register/unregister on 32/64-bit, registry keys/values correctness, Explorer context/property/overlay loading, localized resource loading, and unload behavior after Explorer restart.
