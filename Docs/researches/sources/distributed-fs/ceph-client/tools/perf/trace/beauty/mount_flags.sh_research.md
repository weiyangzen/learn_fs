# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/mount_flags.sh

Purpose: Generates the `MS_*` mount flag string array.

Important APIs/types/functions: It parses `mount.h` from the beauty UAPI copy and emits `static const char *mount_flags[]`, supporting both numeric constants and `(1<<n)` forms.

Control flow: The first pipeline handles decimal definitions, filters out mask/magic/noisy constants, sorts numerically, and indexes zero specially. The second pipeline handles shift-expression definitions.

State and persistence: Stateless stdout generation.

Dependencies and integration points: Output is included by `mount_flags.c`; it requires `grep`, `sed`, `sort`, and `xargs`.

Risks: Hex constants in `mount.h` are not handled by the first regex. If a semantic flag is filtered by the broad `(MSK|VERBOSE|MGC_VAL)` exclusion it will not be shown.

Test signals: Regenerate and verify entries for common flags such as `MS_RDONLY`, `MS_NOSUID`, and `MS_BIND`; compile the consumer.
