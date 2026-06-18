# sources/distributed-fs/openafs/src/WINNT/client_exp/PropVolume.h

Purpose: declares the AFS volume property page class.

Important APIs/types: `CPropVolume` derives from `PropertyPage` and overrides `PropPageProc`.

Control flow: no implementation; all behavior is in `PropVolume.cpp`.

State/persistence: no additional fields beyond base property page state.

Dependencies/integration: depends on resource IDs and `PropBase.h`.

Risks: minimal class surface, but behavior depends heavily on base fields being initialized by the creator.

Test signals: construction and property sheet callback routing for selected AFS paths.
