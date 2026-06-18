# sources/cloud-native/cri-o/internal/process/defunct_processes.go

Purpose: counts zombie processes by scanning a procfs-like tree and parsing `/proc/[pid]/stat`.

Important APIs/types/functions: `ProcessFS`, `Stat`, `DefunctProcesses`, `DefunctProcessesForPath`, and private `processStats`.

Control flow: opens the process filesystem root, reads directory names, filters numeric names as PIDs, reads each `stat` file, parses command and state, logs and skips per-process read/parse failures, and increments the count when state is `Z`.

State and persistence behavior: read-only filesystem inspection. It does not cache results and does not mutate procfs or process state.

Dependencies and integration points: depends on `os`, `filepath`, `strconv`, `strings`, and logrus. It can be used by node-health or metrics code that needs defunct process counts.

Risks: `/proc/[pid]/stat` command names can contain parentheses; the parser correctly uses the last `)` but still assumes the state byte exists two characters later. Races are expected because processes can exit between directory read and stat read.

Test signals: tests use fixture proc trees for zombie counts, empty process lists, invalid paths, and non-directory errors.
