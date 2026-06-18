## sources/distributed-fs/openafs/src/WINNT/client_exp/volume_inf.h

Purpose: Defines `CVolInfo`, the value object used to move AFS volume status from `gui2fs.cpp` into volume dialogs and property pages.

Important APIs/types: Stores file path/name, volume name, availability string, volume ID, quota, new quota, blocks used, partition size/free, duplicate index, and error message.

Control flow/state: No methods; fields are filled by `GetVolumeInfo`, edited by `CVolumeInfo`, and consumed by `SetVolInfo`.

Dependencies/integration: Requires MFC `CString` and MSVC `unsigned __int64`. Included by `gui2fs.cpp` and `volumeinfo.cpp`.

Risks/tests: Public mutable fields allow inconsistent state, such as an error message with stale quota values. Test duplicate-volume handling and 64-bit formatting/truncation in consumers.
