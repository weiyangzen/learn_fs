# sources/distributed-fs/ceph-client/tools/perf/builtin.h

### Purpose
`builtin.h` is the common declaration point for perf builtin command entry functions and build-feature reporting helpers. It lets the command dispatcher call each builtin without exposing implementation headers.

### Important APIs, Types, And Functions
`struct feature_status` describes a build option by display name, macro, help tip, and builtin status. `supported_features[]` and `feature_status__printf()` are used by `perf version`. The rest of the header declares help helpers and `cmd_*()` entry points for perf subcommands such as `record`, `stat`, `trace`, `script`, `daemon`, and `kwork`.

### Control Flow
This header has no runtime control flow, but its declarations define the contract used by `perf.c`'s `commands[]` table. Each `cmd_*()` accepts the conventional `(int argc, const char **argv)` pair and returns an exit status.

### State And Persistence
Only external feature metadata is declared. No state is defined in this header.

### Dependencies And Integration Points
It integrates all builtin implementations with the central dispatcher and completion/listing paths. Conditional compilation happens in `perf.c`, while this header exposes all possible command signatures.

### Risks
Adding/removing a builtin requires keeping this header, the implementation, build files, and `perf.c` command table aligned. A stale declaration will fail at build/link time or hide a command from dispatch.

### Test Signals
Build coverage is the main signal. Runtime checks are `perf --list-cmds`, command help routing, and executing newly added commands.
