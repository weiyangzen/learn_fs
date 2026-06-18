# sources/distributed-fs/ceph-client/kernel/Makefile

## Purpose
This Makefile controls which core kernel objects and subdirectories are built for the kernel tree snapshot under `sources/distributed-fs/ceph-client/kernel`. It is the integration point that wires core process, scheduling, audit, accounting, tracing, crash, module, namespace, BPF, sanitizer, and generated-header components into Kbuild based on configuration symbols.

## Important build entries
The base `obj-y` list includes core always-built objects such as `fork.o`, `exit.o`, `softirq.o`, `workqueue.o`, `pid.o`, `cred.o`, `async.o`, and others. Subdirectories such as `sched/`, `locking/`, `power/`, `printk/`, `irq/`, `rcu/`, `livepatch/`, `liveupdate/`, `dma/`, `entry/`, and `unwind/` are always included, while `module/`, `futex/`, `cgroup/`, `time/`, `trace/`, `events/`, and debug/test directories are gated by config.

The files in this work item are selected here: `async.o` is in the core `obj-y`, `acct.o` is built under `CONFIG_BSD_PROCESS_ACCT`, `audit.o` and `auditfilter.o` under `CONFIG_AUDIT`, and `auditsc.o audit_watch.o audit_fsnotify.o audit_tree.o` under `CONFIG_AUDITSYSCALL`.

## Control flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_*)` lines to build a composite object list. Conditional instrumentation variables tune compiler flags per object. Later rules generate embedded config and kernel header archive artifacts: `config_data.gz` from `$(KCONFIG_CONFIG)` and `kheaders_data.tar.xz` from generated source/object header lists and checksum files.

## State and generated artifacts
The Makefile does not maintain runtime state, but it defines build outputs and clean targets. Generated files include `config_data`, `config_data.gz`, `kheaders_data.tar.xz`, `kheaders-srclist`, `kheaders-objlist`, and `kheaders.md5`; `clean-files` removes the kheaders helper lists/checksum.

## Dependencies and integration points
It depends on Kbuild variables and macros such as `obj-y`, `obj-$()`, `targets`, `FORCE`, `if_changed`, `filechk`, compiler option probes, and sanitizer/instrumentation variables. It integrates with config symbols, architecture include paths via `SRCARCH`, generated include directories, and `gen_kheaders.sh`.

## Risks and invariants
Build selection mistakes can silently omit required core services or compile objects under the wrong config. Audit has a split dependency: base audit logging/filtering requires `CONFIG_AUDIT`, while syscall auditing and path watches require `CONFIG_AUDITSYSCALL`; moving these incorrectly would create unresolved symbols or missing behavior. Instrumentation exclusions are also important: softirq, extable, kcov, and kstack erase are deliberately excluded from specific sanitizers/tracers to avoid recursion, unsafe instrumentation, or noisy coverage.

## Test signals
The best tests are config matrix builds: audit on/off, auditsyscall on/off, BSD accounting on/off, tracing/KCOV/KASAN/KCSAN combinations, modules on/off, and IKHEADERS on/off. Build logs should show expected objects included and generated header/config targets rebuilt when inputs change.
