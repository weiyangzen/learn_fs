<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/killer.cpp -->
## sources/distributed-fs/openafs/src/WINNT/install/NSIS/killer.cpp

Purpose: NSIS helper that enumerates running processes by executable name and terminates matching processes, including support for old NT4 and 16-bit WOW task enumeration.

Important APIs, types, and functions: `EnumProcs` abstracts process enumeration using PSAPI on NT4 and Toolhelp32 on Win9x/newer NT. It dynamically loads `PSAPI.DLL`, `VDMDBG.DLL`, or `Kernel32.DLL` functions. `Enum16` bridges NTVDM task enumeration. `MyProcessEnumerator` compares process names to global `strProcessName`, opens matching processes with `PROCESS_ALL_ACCESS`, and calls `TerminateProcess`. `main` copies the requested process name and starts enumeration.

Control flow and state: The utility sets a global target process name from `argv[1]`. Enumeration invokes the callback for every process and optional 16-bit tasks. Matching is case-insensitive exact executable-name comparison.

Persistence and dependencies: No persistent storage, but it forcibly changes system runtime state by terminating processes. Depends on process enumeration APIs, dynamic libraries, and sufficient privileges.

Integration points: NSIS uninstall/install scripts can use it to stop AFS tools before replacing files.

Risks: Uses `TerminateProcess` rather than graceful shutdown, risking data loss. `PROCESS_ALL_ACCESS` can fail under modern privilege/UAC settings. It closes `hProcess` even when `OpenProcess` returns null. Library-free logic can double-free `hInstLib` on some paths. Old OS branches are obsolete and lightly guarded. Process-name matching may kill unrelated programs with the same executable name.

Test signals: Enumerate on supported Windows versions, target a harmless process, verify no crash on access-denied processes, validate no double-free with instrumentation, and confirm installer scripts avoid broad names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/install/NSIS/killer.cpp -->
