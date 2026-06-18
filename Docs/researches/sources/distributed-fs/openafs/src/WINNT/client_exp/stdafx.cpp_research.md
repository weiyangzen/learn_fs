## sources/distributed-fs/openafs/src/WINNT/client_exp/stdafx.cpp

Purpose: Provides the translation unit for the MFC precompiled header used by the Explorer extension project.

Important APIs/functions: It includes `stdafx.h`, Winsock headers, and core AFS configuration headers but defines no functions.

Control flow/state: No runtime control flow or state. Its role is build-time compilation acceleration and include consistency.

Dependencies/integration: Depends on MFC, Winsock, OpenAFS `afsconfig.h`, `param.h`, `roken.h`, and `stds.h`.

Risks/tests: Include order is important because Winsock must precede conflicting Windows socket declarations. Test clean builds with and without precompiled headers and both debug/release configurations.
