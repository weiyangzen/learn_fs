# subset-b-009396 Research

Grouped research report for the requested source files. Each source section is wrapped in the exact reconciliation markers required by the research cron.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/crypto.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/crypto.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for Linux crypto Kconfig fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 133 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables broad crypto API coverage: user crypto API, AEAD/hash/skcipher/RNG APIs, generic algorithms, compression transforms, hardware crypto, and arch-optimized implementations guarded by version/arch/sanitizer predicates.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., v7., linux-next, x86_64, arm64, arm, riscv, s390, kmsan.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- crypto algorithm availability churn, architecture-specific acceleration, sanitizer exclusions, and removal windows that can break generated kernel configs.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/crypto.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/debug.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/debug.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for auxiliary debug Kconfig fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 46 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: turns on non-critical bug detectors such as DEBUG_VM, debug objects, hung-task/lockup helpers, page poisoning, dynamic debug, context tracking, and page-table checking while adding panic_on_warn to the kernel command line.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., x86_64, arm, s390, nonoise, optional.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- higher false-positive/noise risk and boot/performance regressions from debug checks, especially across s390, arm, and version-gated options.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/debug.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/filesystems.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/filesystems.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for filesystem coverage fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 171 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables many disk, network, flash, stacked, and legacy filesystems plus their ACL/security/compression/debug knobs, while disabling debug options known to produce inactionable reports.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., v7., arm64, arm.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- filesystem image corruption reports, deprecated/removed filesystems, arm64_gce exclusions, and Kconfig option churn.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/filesystems.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/hamradio.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/hamradio.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for amateur radio networking fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 8 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables HAMRADIO, AX.25, NET/ROM, ROSE, MKISS, 6PACK, and BPQETHER protocol/device coverage.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: none beyond fragment inclusion.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- removed subsystem/version gating and noisy legacy networking surface.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/hamradio.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kasan.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/kasan.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for KASAN/UBSAN sanitizer fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 24 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables KASAN modes, page-owner support, SLUB RCU debugging, and selected UBSAN checks while disabling UBSAN classes that are noisy or ineffective for syzbot.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., arm64, arm, riscv, s390.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- compiler/version architecture predicates, sanitizer overhead, and deliberate UBSAN exclusions.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kasan.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kasan_panic_on_write.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/kasan_panic_on_write.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for KASAN bad-write panic command-line fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 1 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: appends kasan.fault=panic_on_write and kasan_multi_shot to panic only on bad writes while still reporting bad reads.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: kasan.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- depends on command-line merging and KASAN runtime semantics.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kasan_panic_on_write.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kasan_sw.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/kasan_sw.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for arm64 software-tag KASAN fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 2 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: selects KASAN with KASAN_SW_TAGS for tag-based software instrumentation.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: none beyond fragment inclusion.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- must be included only where the architecture/toolchain supports software tags.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kasan_sw.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kcsan.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/kcsan.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for KCSAN race detector fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 14 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables KCSAN, self-tests, watchpoint counts, randomized skip/delay settings, and reporting policy for value-changing races.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5..
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- race detector overhead, self-test noise, and version-gated permissive behavior.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kcsan.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kexec.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/kexec.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for crash-kexec slim-kernel fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 2 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables CRASH_DUMP and PROC_VMCORE for kernels intended to be booted through kexec -p.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: none beyond fragment inclusion.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- minimal dependency surface; correctness depends on including this only for kexec/crash-dump lanes.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kexec.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kfence.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/kfence.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for KFENCE memory detector fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 5 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables KFENCE with static keys and explicit sampling/object-count/stress settings.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: none beyond fragment inclusion.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- sample interval and object count trade off bug-finding signal against runtime cost.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kfence.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kmemleak.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/kmemleak.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for kmemleak fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 3 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables DEBUG_KMEMLEAK, disables automatic scanning, and raises the mem pool size.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: none beyond fragment inclusion.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- requires out-of-band scan control; pool exhaustion can hide leak signal.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kmemleak.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kmsan.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/kmsan.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for KMSAN sanitizer fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: kernel, compiler, config.
- It contains 82 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: forces clang, enables KMSAN and panic-on-report, and weak-disables many incompatible subsystems, drivers, crypto accelerators, and stack/unwinder options.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v6., kmsan, weak.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- very high compatibility risk with MTD, HDA, hardening, stack protector, ORC unwinder, and x86 optimized crypto.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/kmsan.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/linux-next.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/linux-next.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for linux-next kernel selector. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: kernel, config.
- It contains 2 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: points instances at linux-next-history next-20260520 and weakly sets hung-task/softlockup panic knobs to integer values.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: linux-next, weak.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- date-tag freshness and Kconfig type changes across next snapshots.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/linux-next.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/linux-upstream.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/linux-upstream.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for mainline kernel selector. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: kernel, config.
- It contains 1 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: points upstream instances at Torvalds linux v7.1-rc4 and weakly sets BOOTPARAM_HUNG_TASK_PANIC to the integer form.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v7., weak.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- tag advancement and Kconfig y/n-to-int compatibility.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/linux-upstream.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/lockdep.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/lockdep.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for lock dependency debug fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 17 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables LOCKDEP, PROVE_LOCKING/RCU, atomic-sleep checks, lock allocation tracking, and larger lockdep table bit widths.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., arm64, arm, preempt_rt.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- memory/boot cost and arch-specific breakage, especially arm and arm64 full configs.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/lockdep.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/lockup.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/lockup.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for soft lockup panic fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 1 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: weakly enables BOOTPARAM_SOFTLOCKUP_PANIC except on s390 to normalize crash detection.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: s390, weak, override.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- kernel option type transition and architecture support variance.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/lockup.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/lsm.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/lsm.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for common LSM/integrity/audit fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 31 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables SECURITY, network/path hooks, TOMOYO/Yama/SafeSetID/Landlock/Lockdown, integrity/IMA/EVM, audit, and optional BPF LSM.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., baseline, optional.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- policy restrictions can block fuzzing; dependencies on BPF and keyring options.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/lsm.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/maintained.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/maintained.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for public-reporting hygiene fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 1 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: disables BLK_DEV_WRITE_MOUNTED for instances that report to public mailing lists.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: none beyond fragment inclusion.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- reduces inactionable mounted-device filesystem reports but changes block-device write behavior.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/maintained.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/media.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/media.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for media subsystem fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 17 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables media core, USB camera, test drivers, vivid/vimc/vim2m/vicodec and disables PCI camera autoselection.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5..
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- test-driver availability and version gating around v5.8/v5.11.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/media.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/mte.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/mte.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for arm64 hardware tag KASAN fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 2 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables KASAN with KASAN_HW_TAGS for MTE-style hardware tag checking.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: none beyond fragment inclusion.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- only valid on supporting arm64 hardware/emulation and compiler/kernel combinations.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/mte.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/net-extra.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/net-extra.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for extra/esoteric networking fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 195 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: adds TIPC, SCTP/DCCP, batman-adv, OVS, bridge/ebtables/ipsets/IPVS, PPP/ATM/WAN/6LoWPAN/802.15.4/USBIP/ISDN/RXRPC/MPLS coverage.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., v7., s390, preempt_rt.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- legacy protocol removals, PREEMPT_RT exclusions, and slower qemu boot/runtime cost.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/net-extra.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/net.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/net.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for core networking fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 521 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables core sockets, TCP/IP/IPv6, XFRM/IPsec, netfilter/nftables/iptables, routing, sched/cls/act, tunnels, veth/virtio, CAN/NFC/RDMA and many net devices while disabling most hardware vendors.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., v7., x86_64, arm64, arm, s390, kmsan, preempt_rt, onlynet.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- large Kconfig surface with many version, arch, PREEMPT_RT, KMSAN, and device availability constraints.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/net.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/partitions.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/partitions.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for partition parser fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 24 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables advanced partition table formats for legacy Unix, Acorn, Amiga, Atari, Mac, BSD, Solaris, LDM, SGI, SUN, KARMA, SYSV68, and cmdline parsers.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: none beyond fragment inclusion.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- mostly parser-surface risk from malformed disk images.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/partitions.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/riscv64.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/riscv64.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for riscv64 arch fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: shell, config.
- It contains 5 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: runs defconfig and kvm_guest.config, extends command line, enables BINFMT_FLAT, and gates old RISCV_BASE_PMU.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., baseline.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- arch support gaps and removed perf implementation before v5.18.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/riscv64.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/rust.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/rust.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for Rust-for-Linux fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 9 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: overrides RUST on and enables Rust debug/assertion/hardening options plus Rust abstractions and null block driver.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v6., baseline, override.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- requires Rust-capable toolchain and version-gated kernel Rust features.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/rust.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/s390.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/s390.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for s390 arch fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: shell, config.
- It contains 5 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: runs defconfig/kvm_guest.config, disables builtin CMDLINE, lengthens RCU stalls, and gates old compat support.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v6., x86_64, s390, override.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- s390 lacks CMDLINE support used heavily elsewhere, so command-line-dependent fragments may not apply.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/s390.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/selinux.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/selinux.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for SELinux-specific LSM fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 7 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: turns off AppArmor/Smack, enables SELinux develop mode/default security, and sets an LSM ordering string including selinux.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: none beyond fragment inclusion.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- LSM ordering and security xattr behavior affect filesystem and reporting outcomes.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/selinux.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/smack.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/smack.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for Smack-specific LSM fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 7 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: turns off SELinux/AppArmor, enables Smack/netfilter/EVM extra xattrs/default security, and sets the Smack LSM ordering string.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: baseline, onlyusb.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- baseline/onlyusb exclusions and xattr/EVM interactions.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/smack.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/sound.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/sound.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for sound subsystem fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 41 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables ALSA/OSS compatibility, sequencer, dummy/loopback/virtio/HDA/USB audio, MIDI gadget, and optional sound debug validation.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., riscv, s390, kmsan, nonoise, optional.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- HDA disabled by KMSAN and sound debug can be noisy on riscv/s390/nonoise.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/sound.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-5.15.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-5.15.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for stable 5.15 kernel selector. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: kernel.
- It contains 0 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: points instances at linux-stable v5.15.165.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5..
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- must match fragment version predicates and stable branch support.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-5.15.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-5.4.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-5.4.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for stable 5.4 kernel selector. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: kernel.
- It contains 0 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: points instances at linux-stable v5.4.72.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5..
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- older Kconfig surface lacks many newer options and needs version guards.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-5.4.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-6.1.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-6.1.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for stable 6.1 kernel selector. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: kernel.
- It contains 0 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: points instances at linux-stable v6.1.106.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v6..
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- must reconcile 6.1-era option renames/removals.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-6.1.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-6.6.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-6.6.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for stable 6.6 kernel selector. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: kernel.
- It contains 0 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: points instances at linux-stable v6.6.93.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v6..
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- stable-6.6-specific exclusions appear in debug and subsystem fragments.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/stable-6.6.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/subsystems.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/subsystems.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for broad subsystem coverage fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 539 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables the main syzkaller-testable kernel surface: IPC, timers, cgroups, KVM, modules, block, memory, PCI, MTD, storage, input, TTY, DRM, USB, DMA/IOMMU/VFIO/virtio/vhost, staging/android, fs core, keyrings, thermal, DAMON, SMB server, PREEMPT_RT and io_uring experiments.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., v7., linux-next, x86_64, arm64, arm, riscv, s390, kmsan, preempt_rt.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- largest fragment with heavy cross-arch, version, sanitizer, and PREEMPT_RT interactions.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/subsystems.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/timeouts_emu.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/timeouts_emu.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for emulated target timeout fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 4 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: appends slower qemu command-line timeouts and lower virtual device counts, sets RCU stall timeout to 300, hung task timeout to 420, and zeroes expedited RCU timeout on newer kernels.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., x86_64, kmsan, kcsan, nonoise.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- timeout ordering affects deduplication and no-output classification on slow emulated arches.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/timeouts_emu.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/timeouts_native.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/timeouts_native.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for native target timeout fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 4 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: appends native-timeout command line with larger virtual-device counts and documents strict ordering of RCU, softlockup, hung task, workqueue, netdev, and no-output detection.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., kmsan, kcsan, nonoise.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- changing values can cause duplicate or misclassified hang bugs.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/timeouts_native.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/unmaintained.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/unmaintained.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for non-public-reporting fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 3 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: keeps fuzzing unmaintained surfaces such as XFS v4 support and x86 floppy without reporting them to LKML.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: upstream, x86_64.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- deliberately separates useful fuzzing from inactionable public reports.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/unmaintained.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/usb.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/usb.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for USB-only instance fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 6 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables USB support/gadget/raw gadget/dummy HCD and disables GadgetFS/configfs for focused USB fuzzing.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., baseline.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- depends on raw gadget availability and avoids alternate gadget APIs.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/usb.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/wireless.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/wireless.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for wireless fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: config.
- It contains 54 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: enables cfg80211/mac80211, hwsim, virtual wifi, selected ath/carl9170 drivers, WWAN/MHI, and disables most vendor families.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., arm64, arm.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- arm64_gce hardware driver exclusions and removed WiMAX/RNDIS options.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/wireless.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/x86_64.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/x86_64.yml Research

## Purpose
This file is a syzkaller dashboard Linux configuration bit for x86_64 architecture fragment. It is consumed through `dashboard/config/linux/main.yml` include predicates and contributes kernel, shell, compiler, command-line, or Kconfig settings to selected syzbot instances.

## Important data and APIs
- Top-level keys present: shell, config.
- It contains 33 list entries under the YAML fragment grammar used by syzkaller dashboard config generation.
- Entry forms include plain symbols (`CONFIG_FOO=y` semantics), explicit values (`FOO: value`), disabled values (`FOO: n`), command-line appends via `CMDLINE`, and predicates such as version/architecture/sanitizer/reporting selectors.
- Main coverage intent: runs x86_64 defconfig/allyes/kvm_guest fragments, appends root/console/vsyscall/NUMA/KVM/media/netrom/rose command-line values, enables compat, x86 CPU/MSR/CPUID/paravirt, Intel net and QEMU boot support.

## Control flow and integration
`main.yml` selects this bit when an instance's tag set satisfies the include predicate. Later fragments override earlier ones, so this file's order in `main.yml` matters when it disables or refines symbols enabled by broader fragments. Version and negative predicates gate settings before the generated kernel `.config` is built.

## State and persistence
The file has no runtime state. Its persistent effect is declarative: generated configs, kernel command lines, selected compiler, shell preparation commands, or kernel repository/tag choices. Any changed symbol can alter dashboard instance behavior until the fragment is updated again.

## Dependencies and integration points
- Depends on the dashboard config parser's fragment grammar and predicate vocabulary.
- Integrates with Linux Kconfig names that change across kernel versions.
- Observed gating signals in this file include: v5., v6., x86_64, baseline, optional, override.
- For command-line entries, integration also depends on architecture support for builtin command lines.

## Risks and edge cases
- command-line length, LLVM x32 limitations, KMSAN exclusions, and x86 option churn.
- Incorrect version predicates can make old or next kernels fail config generation.
- Cross-fragment overrides can silently weaken intended coverage if include order changes.
- Enabling debug/sanitizer/subsystem options can increase boot time, memory use, or report noise.

## Test signals
Useful validation is generated-kernel-config diffing for every instance that includes this bit, `olddefconfig`/build success across gated kernel tags, and syzbot boot smoke tests that verify command-line and detector behavior. For this research pass, the source was read directly and no build was run.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/x86_64.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/main.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/main.yml Research

## Purpose
This is the central Linux dashboard instance matrix. It maps named syzbot managers to tag lists and maps config bit files to predicates controlling when those bits are included.

## Important data and APIs
- `instances` defines concrete dashboard manager names such as upstream KASAN/KMSAN/KCSAN, architecture variants, stable branches, Android, and ChromeOS lanes.
- `includes` lists fragment files from `bits/` in deterministic order. Later includes may override earlier config choices.
- The file contains about 105 instance entries and 64 include entries in the local YAML list format.

## Control flow
The dashboard config tooling reads an instance's tag list, walks `includes` top to bottom, and includes each fragment whose predicate list matches. Tags encode kernel tree, architecture, timeout model, compiler, LSM, sanitizer, reporting policy, and reduced/baseline/onlynet/onlyusb variants.

## State and persistence
No runtime state is stored here, but this file persistently defines all generated Linux dashboard configs. Updating an instance tag or include predicate changes future generated kernel configs and can alter syzbot coverage or public reporting.

## Dependencies and integration points
It depends on every referenced `bits/*.yml` file, the dashboard config parser, Linux Kconfig, syz-ci manager naming, and kernel tree selectors. Comments document known upstream breakage and coverage tradeoffs such as arm lockdep, hamradio removal, and full arm64 configs for `syz-check`.

## Risks
The main risks are include-order regressions, tag typos that drop critical fragments, unintentional public reporting from unmaintained surfaces, and stale stable/next tags. Instance names are integration contracts with dashboard and syz-ci deployments.

## Test signals
Validation should parse all instances, assert all referenced fragment files exist, generate configs for every manager, and boot-smoke representative managers. This research pass read the file directly and did not run dashboard config generation.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/main.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/openbsd/recreate.sh -->
# sources/test-tools/syzkaller/dashboard/config/openbsd/recreate.sh Research

## Purpose
This Bash script rebuilds the `ci-openbsd` Google Cloud instance image used by syzkaller OpenBSD CI. It creates a fresh OpenBSD GCE image, recreates the VM with the old IP and service account, rewrites SSH host keys, uploads worker disk/key artifacts, wires userspace directories, and reboots.

## Important commands and variables
- Uses `TODAY`, `SYZ_DIR`, `ZONE`, `INSTANCE`, `HOST`, `IP`, `SERVICE_ACCOUNT`, and `IMAGE` to derive cloud resource names.
- Calls `tools/create-openbsd-gce-ci.sh` and `tools/create-openbsd-vmm-worker.sh`.
- Uses `gcloud compute instances describe/delete/create`, `gcloud compute images delete/create`, and `gcloud storage cp`.
- Uses `ssh`/`scp` to halt/reboot and install worker artifacts.

## Control flow
The script verifies it is inside a syzkaller tree, discovers the current VM IP and service account, builds a tarball image, uploads it to GCS, halts and deletes/recreates image and VM resources, rewrites `~/.ssh/known_hosts`, builds worker artifacts, copies them to `/syzkaller/userspace`, creates a multicore userspace symlink set, then reboots. `set -eux` makes command failures stop execution except where explicit `|| true` handles expected missing resources.

## State and persistence
Persistent state lives in GCP images, VM instance metadata/disks/IPs, public GCS objects, local `known_hosts`, and remote `/syzkaller/userspace*` directories. The script drops generated files in the current directory.

## Dependencies and integration points
Depends on GCloud CLI auth for project `syzkaller`, SSH config/key material, GCE networking, `genisoimage`, `growisofs`, qemu/kvm, expect, and syzkaller tool scripts. It integrates with dashboard OpenBSD overlays and CI workers.

## Risks
It is destructive to the named VM/image, rewrites `~/.ssh/known_hosts`, assumes GCP project resource names and IP are reusable, and can leave partial cloud resources if interrupted after deletion. Running outside a temp directory may clutter the caller's current directory.

## Test signals
Dry-run style validation is limited because commands are side-effectful. Safer checks are shell syntax validation, confirming GCloud auth/project access, verifying tool scripts and artifacts exist, and post-run SSH/worker boot checks. No destructive command was run for this research.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/openbsd/recreate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/dashapi/ai.go -->
# sources/test-tools/syzkaller/dashboard/dashapi/ai.go Research

## Purpose
This file extends the dashboard API client with AI-agent job polling, trajectory logging, and AI-assisted external report command/poll/confirmation endpoints.

## Important APIs and types
- AI job flow: `AIJobPollReq`, `AIWorkflow`, `AIJobPollResp`, `AIJobDoneReq`, `AITrajectoryReq`, plus `Dashboard.AIJobPoll`, `AIJobDone`, and `AITrajectoryLog`.
- External report flow: `SendExternalCommandReq` with mutually exclusive `Upstream`, `Reject`, `Unreject`, or `Comment` commands; `PollExternalReportReq/Resp`; `ReportPollResult`; `NewReportResult`; `ReplyResult`; and `ConfirmPublishedReq`.
- `ErrReportNotFound` maps a dashboard string error in `SendExternalCommandResp.Error` to a typed Go sentinel.

## Control flow
Each method is a thin wrapper around `Dashboard.Query`, supplying a method string such as `ai_job_poll`, `ai_report_command`, or `ai_confirm_report`. `AIReportCommand` adds one semantic step: after transport success, it converts the response error string `report not found` into `ErrReportNotFound`.

## State and persistence
No local state is stored. Job state, trajectories, report publication state, patch metadata, and external IDs live on the dashboard service. Request/response structs are JSON-encoded by `dashapi.go`.

## Dependencies and integration points
Depends on `pkg/aflow/ai` for workflow and fixes-tag types, `pkg/aflow/trajectory` for spans, and the base dashboard client transport. It integrates AI agents, Lore/email patch workflows, and dashboard reporting entities.

## Risks
`Args` and `Results` use `map[string]any`, so schema errors are detected only at runtime by the server or consumers. The request requires only one command pointer to be set but this invariant is not enforced client-side. String matching for `ErrReportNotFound` is fragile if the server text changes.

## Test signals
Tests should cover method strings, JSON compatibility, the one-command invariant, and `ErrReportNotFound` mapping. No dedicated tests were present in this file; existing transport behavior is inherited from `dashapi.go`.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/dashapi/ai.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/dashapi/dashapi.go -->
# sources/test-tools/syzkaller/dashboard/dashapi/dashapi.go Research

## Purpose
Package `dashapi` defines the wire data model and HTTP client used by syzkaller components to communicate with the dashboard. It covers build upload, builder polling, jobs, crashes, repros, reporting, bug lists, discussions, coverage, manager stats, assets, bug loading, email sending, and shared recipient/status enums.

## Important APIs and types
- Client construction: `Dashboard`, `DashboardOpts`, `UserAgent`, `New`, `NewCustom`, `RequestCtor`, `RequestDoer`, and `RequestLogger`. Empty API keys trigger ambient GCE bearer-token auth through `pkg/auth`.
- Build/commit flow: `Build`, `Commit`, `UploadBuild`, `BuilderPoll`, `CommitPoll`, and `UploadCommits`.
- Job flow: `JobResetReq`, `JobPollReq`, `ManagerJobs.Any`, `JobPollResp`, `JobDoneReq`, `JobType`, `JobDoneFlags.String`, `JobPoll`, `JobDone`, and `JobReset`.
- Crash/repro flow: `Crash`, `ReportCrash`, `CrashID`, `NeedRepro`, `ReportFailedRepro`, `LogToRepro`, and `ReproTaskDone`.
- Reporting model: `BugReport`, `ReportElements`, `BugSubsystem`, `Asset`, `BisectResult`, `BugListReport`, `BugUpdate`, `BugNotification`, discussion structs, `TestPatchRequest`, manager stats, assets, bug loaders, and email request types.
- Transport core: `Dashboard.Query` and `queryImpl`.

## Control flow
Most exported methods build a request struct, call `Query` with a dashboard method string, and return the decoded response. `Query` logs requests/replies when configured, calls `queryImpl`, invokes an error handler on failure, and retries failed API calls up to three times with one-second sleeps. `queryImpl` zeroes non-nil reply pointers, constructs a multipart POST to `<Addr>/api`, writes `client`, `key`, `method`, and gzipped JSON `payload`, sends it through the configured doer, checks for HTTP 200, and JSON-decodes the response body into `reply`.

## State and persistence
The client stores only endpoint, key, injected constructor/doer/logger/error handler, and optionally an auth token cache hidden in the wrapped doer. Persistent dashboard state is remote: builds, bugs, crashes, jobs, reports, assets, discussions, coverage, and emails. `queryImpl` intentionally resets reply values before decoding to avoid stale fields after partial JSON updates.

## Dependencies and integration points
Depends on Go standard packages for HTTP, multipart, gzip, JSON, reflection, mail addresses, and timing, plus `github.com/google/syzkaller/pkg/auth`. The structs are compatibility contracts with dashboard server handlers and syz-ci/reporting clients; comments warn that asset type strings must not change because DB content depends on them.

## Risks
The transport retries all errors, which can duplicate side effects if the server performed an action but returned an error or the response was lost. Requests have no explicit context/timeout at this layer. Reflection requires `reply` to be a pointer and only catches misuse at runtime. Multipart/gzip JSON is a custom protocol that must stay in lockstep with the server. Some fields are deprecated but retained for compatibility, increasing schema complexity.

## Test signals
Unit tests should exercise constructor options, request encoding, retry behavior, reply zeroing, non-200 response errors, bearer-token wrapping, and JSON compatibility. The adjacent test currently checks `UserAgent` option handling. This research pass did not run Go tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/dashapi/dashapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/dashapi/dashapi_test.go -->
# sources/test-tools/syzkaller/dashboard/dashapi/dashapi_test.go Research

## Purpose
This Go test verifies option handling in `dashapi.New`, specifically whether a custom `UserAgent` option alters the request constructor embedded in `Dashboard`.

## Important APIs
- `TestNewOpts` defines table cases for no options and a custom user agent.
- It constructs `Dashboard` with optional `UserAgent`, invokes `dash.ctor`, and checks the `User-Agent` header.

## Control flow
For each subtest, the code builds an option slice, calls `New`, fails on unexpected constructor error, creates a sample GET request, and compares the header against the expected string.

## State and persistence
No persistent state. It uses in-memory request construction with `bytes.NewBuffer`.

## Dependencies and integration points
Depends on `testing`, `bytes`, and the client constructor in `dashapi.go`. It provides direct regression coverage for the option path that wraps `http.NewRequest`.

## Risks
Coverage is narrow: it does not verify `NewCustom`, bearer auth, transport encoding, retry behavior, or default HTTP behavior. The error message's wanted value is hardcoded to the custom-agent text even in the no-option case, though the comparison remains correct.

## Test signals
Running `go test ./dashboard/dashapi` would execute this table test and compile the dashboard API structs. This research pass did not run tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/dashapi/dashapi_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/docs/docs.go -->
# sources/test-tools/syzkaller/docs/docs.go Research

## Purpose
Package `docs` exposes selected Markdown documentation as embedded strings for LLM-oriented agent flows in `pkg/aflow`.

## Important APIs
- `ProgramSyntax string` embeds `program_syntax.md`.
- `SyscallDescriptionsSyntax string` embeds `syscall_descriptions_syntax.md`.
- Uses Go `//go:embed` with a blank import of `embed`.

## Control flow
There is no runtime control flow beyond compile-time embedding. Importers read the exported string variables directly.

## State and persistence
The embedded content is fixed at build time. Changes to the Markdown files require rebuilding downstream binaries to update the strings.

## Dependencies and integration points
Depends on the Go embed toolchain and the two Markdown files existing in the same package directory. Integrates with `pkg/aflow` consumers that need prompt/reference text.

## Risks
Missing embedded files break compilation. Large documentation changes can affect binary size and prompt behavior.

## Test signals
Go build of the package verifies embed paths. Unit tests for aflow prompt construction would catch accidental empty or stale content; no Go tests were run in this pass.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/docs/docs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/docs/fuchsia/setup.sh -->
# sources/test-tools/syzkaller/docs/fuchsia/setup.sh Research

## Purpose
This Bash helper sets up, builds, runs, and nominally updates syzkaller for Fuchsia. It expects absolute syzkaller and Fuchsia checkout paths and creates `workdir.fuchsia` under the syzkaller tree.

## Important functions
- `die`, `usage`, and `preflight` handle user errors and check `go`, syzkaller, and Fuchsia directories.
- `build` configures Fuchsia `core.x64` with syzkaller/fuzzing bundles and KASAN, builds it, then builds syzkaller for `TARGETOS=fuchsia TARGETARCH=amd64`.
- `run` locates product bundle images with `ffx`, injects SSH authorized keys into a ZBI, copies FXFS, writes a `syz-manager` JSON config, extends `PATH` for QEMU, and launches `bin/syz-manager`.
- `update_syscall_definitions` is currently a TODO that exits before extraction.

## Control flow
`main` parses optional `-d`, requires exactly three positional arguments, initializes `workdir`, then dispatches `build`, `run`, or `update`; all unknown commands show usage. Strict shell options make most failures abort immediately.

## State and persistence
The script writes `workdir.fuchsia/fx-syz-manager-config.json` and `out/x64/syzdeps` copies inside the Fuchsia checkout. It relies on Fuchsia `fx`/`ffx` state and SSH key config.

## Dependencies and integration points
Depends on Go, Fuchsia `fx`/`ffx`, qemu prebuilts, syzkaller Makefile targets, and Fuchsia product bundle image names. The generated manager config integrates with syzkaller's qemu VM backend.

## Risks
Global variables are intentionally loose per TODOs, absolute path requirements are not deeply normalized, `update` is nonfunctional, and the run path depends on current Fuchsia product config. Writing JSON via shell interpolation assumes paths do not contain problematic characters.

## Test signals
Useful checks are `setup.sh help`, `build` completion, `ffx config check-ssh-keys`, and a successful `syz-manager` launch. This research pass did not run the script.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/docs/fuchsia/setup.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/allocator.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/allocator.h Research

## Purpose
This vendored FlatBuffers header defines the abstract FlatBuffers allocator interface used by `vector_downward` and builders. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `Allocator::allocate`, `deallocate`, and default `reallocate_downward` with protected `memcpy_downward`.
- Direct includes observed: #include "flatbuffers/base.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: memory ownership, downward growth copying, allocator/deallocator pairing.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/allocator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/array.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/array.h Research

## Purpose
This vendored FlatBuffers header provides `flatbuffers::Array<T, length>` accessors for fixed-size arrays embedded in serialized structs. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `Get`, `operator[]`, iterators, `GetEnum`, `Mutate`, `CopyFromSpan`, `make_span`, byte spans, and raw cast helpers.
- Direct includes observed: #include <cstdint>, #include <memory>, #include "flatbuffers/base.h", #include "flatbuffers/stl_emulation.h", #include "flatbuffers/vector.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: endianness, aliasing, bounds asserts, raw casts, and mutation of serialized data.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/base.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/base.h Research

## Purpose
This vendored FlatBuffers header centralizes FlatBuffers platform/compiler feature detection, endian helpers, scalar typedefs, and low-level serialization utilities. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: version macros, endian detection, `uoffset_t`/`voffset_t`, `EndianScalar`, `ReadScalar`, `WriteScalar`, `PaddingBytes`, range helpers, and alignment verification.
- Direct includes observed: #include <stdlib.h>, #include <crtdbg.h>, #include <assert.h>, #include FLATBUFFERS_ASSERT_INCLUDE, #include <cstdint>, #include <cstddef>, #include <cstdlib>, #include <cstring>.
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: portability across compilers/architectures, strict aliasing/UBSAN, big-endian handling, and ABI-sensitive typedef sizes.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/buffer.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/buffer.h Research

## Purpose
This vendored FlatBuffers header defines offset wrappers and root/buffer access helpers for serialized FlatBuffers. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `Offset`, `Offset64`, `IndirectHelper`, `GetBufferIdentifier`, `BufferHasIdentifier`, `GetRoot`, `GetMutableRoot`, and size-prefixed variants.
- Direct includes observed: #include <algorithm>, #include "flatbuffers/base.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: unchecked pointer arithmetic, root validity, endian assumptions, and identifier misuse.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/buffer_ref.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/buffer_ref.h Research

## Purpose
This vendored FlatBuffers header provides a lightweight non-owning typed buffer/length wrapper with optional free-on-destroy behavior. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `BufferRef<T>` fields `buf`, `len`, `must_free`, plus `GetRoot` and `Verify`.
- Direct includes observed: #include "flatbuffers/base.h", #include "flatbuffers/verifier.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: lifetime ownership ambiguity, `free` vs allocator mismatch, and verifier coverage.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/buffer_ref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/code_generator.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/code_generator.h Research

## Purpose
This vendored FlatBuffers header declares the abstract code-generation plugin interface used by flatc backends. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `CodeGenOptions`, `CodeGenerator::Status`, `GenerateCode` overloads, `GenerateCodeString`, make rule/grpc/root-file hooks, language capability queries.
- Direct includes observed: #include <string>, #include "flatbuffers/idl.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: interface compatibility for generators and status/error propagation.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/code_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/code_generators.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/code_generators.h Research

## Purpose
This vendored FlatBuffers header contains helper classes for code generator implementations. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `CodeWriter`, `BaseGenerator`, `CommentConfig`, `GenComment`, `FloatConstantGenerator` variants, and `JavaCSharpMakeRule`.
- Direct includes observed: #include <map>, #include <sstream>, #include "flatbuffers/idl.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: template replacement correctness, namespace/file-name generation, and floating constant rendering across languages.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/code_generators.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/default_allocator.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/default_allocator.h Research

## Purpose
This vendored FlatBuffers header implements the default heap allocator and null-allocator helper functions. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `DefaultAllocator`, `Allocate`, `Deallocate`, and `ReallocateDownward`.
- Direct includes observed: #include "flatbuffers/allocator.h", #include "flatbuffers/base.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: new/delete[] pairing, temporary allocator objects, and custom allocator fallback behavior.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/default_allocator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/detached_buffer.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/detached_buffer.h Research

## Purpose
This vendored FlatBuffers header implements an owning movable finished-buffer handle returned by builders. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `DetachedBuffer` constructors, move operations, destructor, `data`, `size`, `destroy`, and `reset`.
- Direct includes observed: #include "flatbuffers/allocator.h", #include "flatbuffers/base.h", #include "flatbuffers/default_allocator.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: move-only lifetime, owned allocator deletion, and deallocation with original reserved size.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/detached_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/file_manager.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/file_manager.h Research

## Purpose
This vendored FlatBuffers header declares an abstract file read/write interface for generator code paths. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `FileManager::SaveFile` and `LoadFile`.
- Direct includes observed: #include <set>, #include <string>, #include "flatbuffers/util.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: implementation-defined persistence semantics and copy prevention.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/file_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flatbuffer_builder.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/flatbuffer_builder.h Research

## Purpose
This vendored FlatBuffers header implements `FlatBufferBuilderImpl`, the core C++ FlatBuffers serialization builder. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: builder construction/reset/release, alignment, scalar/offset/struct/table/vector/string creation, vtable deduplication, required-field checks, finish/size-prefix, sorted vector helpers, 64-bit offset support, and temporary pointer helpers.
- Direct includes observed: #include <algorithm>, #include <cstdint>, #include <functional>, #include <initializer_list>, #include <type_traits>, #include "flatbuffers/allocator.h", #include "flatbuffers/array.h", #include "flatbuffers/base.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: nested object asserts, vtable duplication, offset overflow, 32/64-bit region ordering, unfinished buffer access, allocator ownership, and pointer invalidation.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flatbuffer_builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flatbuffers.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/flatbuffers.h Research

## Purpose
This vendored FlatBuffers header umbrella header and utility surface for FlatBuffers C++ users. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: includes core headers, `GetBufferStartFromRootPointer`, size-prefixed length helpers, `NativeTable`, resolver/rehasher function types, `IsFieldPresent`, enum lookup, struct alignment macros, reflection type metadata, and version string.
- Direct includes observed: #include <algorithm>, #include "flatbuffers/array.h", #include "flatbuffers/base.h", #include "flatbuffers/buffer.h", #include "flatbuffers/buffer_ref.h", #include "flatbuffers/detached_buffer.h", #include "flatbuffers/flatbuffer_builder.h", #include "flatbuffers/stl_emulation.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: umbrella dependency bloat, unsafe root-start recovery on corrupt data, field presence/default semantics, and compiler packing assumptions.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flatbuffers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flatc.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/flatc.h Research

## Purpose
This vendored FlatBuffers header declares the `flatc` compiler front-end option model and orchestration class. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `FlatCOptions`, `FlatCOption`, `FlatCompiler::RegisterCodeGenerator`, `Compile`, usage helpers, command-line parsing, parser loading, binary schema handling, annotation, validation, conform parser, and code generation.
- Direct includes observed: #include <functional>, #include <limits>, #include <list>, #include <memory>, #include <string>, #include "flatbuffers/code_generator.h", #include "flatbuffers/flatbuffers.h", #include "flatbuffers/idl.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: command-line option validation, generator registration conflicts, filesystem side effects, and parser/conformance compatibility.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flatc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flex_flat_util.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/flex_flat_util.h Research

## Purpose
This vendored FlatBuffers header bridges flatbuffer vectors containing nested flexbuffers to flexbuffer verification. In syzkaller it lives under the executor include tree and supports generated/embedded FlatBuffers use without depending on a system installation.

## Important APIs, types, and functions
- Main surface: `flexbuffers::VerifyNestedFlexBuffer`.
- Direct includes observed: #include "flatbuffers/flatbuffers.h", #include "flatbuffers/flexbuffers.h".
- The file is header-only or declaration-only and participates in the `flatbuffers` or `flexbuffers` namespace API surface.

## Control flow
Control flow is mostly inline/template driven. Callers instantiate templates or call inline helpers; generated FlatBuffers code and builder/parser code compose these primitives. Assertions guard invalid construction order, bounds, alignment, or unsupported operations, while verifier-facing paths return booleans rather than throwing.

## State and persistence
State is either caller-owned serialized memory, builder-owned downward-growing buffers, allocator-owned heap regions, or generator/parser option structures. No independent persistent storage is created by this header, except where abstractions such as file managers or compiler options are implemented elsewhere.

## Dependencies and integration points
Integrates with neighboring FlatBuffers headers in the same vendored include tree and with generated code produced from schemas. In the executor context, ABI stability, endian conversion, allocator behavior, and verifier correctness are more important than application-level business logic.

## Risks and edge cases
- Key risks: nested null handling and sharing verifier reuse tracking with flexbuffers.
- Many helpers rely on `FLATBUFFERS_ASSERT`; release builds may not stop misuse.
- Pointer reinterpretation, raw buffer offsets, and in-place mutation require validated buffers and correct lifetimes.
- Because this is vendored third-party API surface, local changes can desynchronize generated code expectations.

## Test signals
Useful validation is compiling executor/generated FlatBuffers consumers, running upstream FlatBuffers unit tests where available, and verifier tests over malformed buffers. This research pass read the header directly and did not run C++ tests.

<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flex_flat_util.h -->
