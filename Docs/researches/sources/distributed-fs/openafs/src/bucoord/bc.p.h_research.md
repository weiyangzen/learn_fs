# sources/distributed-fs/openafs/src/bucoord/bc.p.h

`bc.p.h` is the template for generated `bc.h`, defining core backup coordinator configuration and scheduling data structures. It models database/tape hosts, global config, volume sets, volume entries, concrete volumes to dump, dump schedules, and queued dump/restore tasks.

Important types include `bc_hostEntry`, `bc_config`, `bc_opstatus`, `bc_volumeSet`, `bc_volumeEntry`, `bc_volumeDump`, `bc_dumpSchedule`, and `bc_dumpTask`. Constants define config file names (`dbasehosts`, `tapehosts`, `dumpschedule`, `volumeset`), `VSFLAG_TEMPORARY`, `BC_MAXSIMDUMPS`, `BC_MAXPORTS`, and an empty `afs_dprintf` macro.

There is no runtime control flow in this file, but its structures carry persistent config parsed from bucoord text files and runtime job state used to initiate dump/restore operations. Dependencies include `budb_client.h`, `afsutil.h`, stdio conditionals, string, socket address types, and generated error content added when `bc.h` is produced.

Risks include pointer ownership across config structures, fixed port-count limits, fields marked obsolete/unused, generated-header drift, and no active debug logging due to `afs_dprintf` being compiled away. Test signals include parsing/saving config text, dump schedule parent/child construction, temporary volume set lifecycle, and dump task execution with multiple port offsets.
