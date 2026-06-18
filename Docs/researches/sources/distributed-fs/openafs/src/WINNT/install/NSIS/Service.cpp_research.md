<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/Service.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/Service.cpp

Purpose: Small NSIS helper executable to create or delete a Windows service for OpenAFS components.

Important APIs, types, and functions: `main` opens the Service Control Manager, creates a service with `CreateService` unless the first argument starts with `u`/`U`, and deletes a service with `OpenService` plus `DeleteService` for uninstall mode. It treats paths ending in `sys` as `SERVICE_FILE_SYSTEM_DRIVER` with demand start; otherwise it creates an auto-start own-process service.

Control flow and state: Arguments are interpreted as install mode `ServiceName ServicePath DisplayName` or uninstall mode using `argv[2]` as service name. The created service uses `SERVICE_ERROR_IGNORE` and no dependencies/account/password.

Persistence and dependencies: Persists SCM service entries. Depends on administrative privileges and Win32 service APIs.

Integration points: Used by NSIS scripts to install `TransarcAFSDaemon`, drivers, or related services.

Risks: The argument count check says fewer than three args but usage text names four tokens; install mode dereferences `argv[3]`. It calls `CloseServiceHandle(hService)` twice and may call it on an uninitialized/null handle. `stricmp(argv[2] + strlen(argv[2]) - 3, "sys")` underflows for short paths. Error reporting is minimal and install failures may still return 0.

Test signals: Create/delete service in a disposable VM, short path argument handling, driver-vs-service classification, insufficient arguments, and handle-checking under Application Verifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/Service.cpp -->
