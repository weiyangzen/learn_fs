# sources/distributed-fs/coda/coda-src/librepair/repcmds.cc

## Purpose
Non-interactive repair command library for beginning repair sessions, comparing replicas, applying fix files, ending sessions, clearing inconsistencies, and removing inconsistent objects.

## APIs, Types, and Functions
Implements public functions from `repcmds.h`: `BeginRepair()`, `ClearInc()`, `CompareDirs()`, `DoRepair()`, `EndRepair()`, `RemoveInc()`, `dorep()`, and `makedff()`. Helper functions include `findtype()`, `getremovelists()`, `getVolrepNames()`, `compareFids()`, `compareAcl()`, `compareOwner()`, `compareQuotas()`, `compareStatus()`, `compareVV()`, `isLocal()`, and `printAcl()`. It uses pioctls `_VIOC_ENABLEREPAIR`, `_VIOC_REP_CMD`, `_VIOC_REPAIR`, `_VIOC_DISABLEREPAIR`, `_VIOC_SETVV`, and `_VIOCGETVOLSTAT`.

## Control Flow, State, and Persistence
`BeginRepair()` creates a conflict object, gets FID/VV, enables repair expansion, mounts/records RW replicas, starts Venus repair, classifies local/global/server-server mode, and determines file-vs-directory conflict. `CompareDirs()` gathers replica paths, reads Unix directory reps, runs `dirresolve()`, writes per-replica repair actions and optional ACL/mode/owner actions to a fix file, checks version-vector and quota mismatches, and cleans resolver state. `DoRepair()` converts text fix files to internal binary form for directory conflicts, calls `_VIOC_REPAIR`, and reports per-volume return codes. `EndRepair()` optionally commits local/global sessions, disables repair, and frees conflict state. `ClearInc()` compares replicas, clears inconsistency bits in VVs with `_VIOC_SETVV`, and rejects quota differences. `RemoveInc()` generates remove actions for directory conflicts or chooses a replica file for file conflicts, then repairs/clears as needed.

## Dependencies and Integration
Depends on pioctl/kerndep, Venus repair commands, resolver and repair-file APIs (`getunixdirreps()`, `dirresolve()`, `repair_parsefile()`, `repair_putdfile()`), version-vector helpers, volume status, ACL structures, and path/rvol helpers. This is the main programmatic repair workflow used by higher-level repair commands.

## Risks and Test Signals
Risks include fixed 2 KB buffers, many temp files under `/tmp/REPAIR.XXXXXX`, broad global repair side effects, complex cleanup paths, reliance on textual Venus responses, local-replica heuristics, possible allocation cleanup bug in `getVolrepNames()`, and mixed stdout diagnostics from library code. Test signals are begin/end repair pairing, compare fix-file contents, `_VIOC_REPAIR` per-replica status output, VV inconsistency clearing, quota/ACL/mode/owner mismatch detection, and `NNCONFLICTS` handling.
