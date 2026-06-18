# subset-b-008301 Research

Grouped research report for the audit-userspace subset. Each marked section is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/lookup_table.c -->
# sources/security-integrity/audit-userspace/lib/lookup_table.c

Purpose: central libaudit lookup bridge between human rule/log names and numeric kernel audit constants. It includes generated table headers and exposes conversion APIs for fields, syscalls, io_uring operations, flags, actions, message types, machine names, ELF audit architecture values, errno names, file types, filesystem types, and permission classes.

Important APIs: `audit_name_to_syscall`, `audit_syscall_to_name`, `audit_name_to_uringop`, `audit_uringop_to_name`, `audit_name_to_msg_type`, `audit_msg_type_to_name`, `audit_name_to_machine`, `audit_machine_to_elf`, `audit_elf_to_machine`, `audit_name_to_errno`, `audit_errno_to_name`, and the field/flag/action/ftype/fstype/perm lookup wrappers. Most call generated `*_s2i` and `*_i2s` functions from `gen_tables.h` output.

Control flow: syscall lookup switches on libaudit machine ids and dispatches to the architecture-specific table; `MACH_IO_URING` dispatches to the io_uring table. Message type lookup first tries the table, then accepts `UNKNOWN[n]` and leading decimal strings as fallbacks. ELF conversion linearly scans `elftab`.

State and persistence: no persistent state. The only state is the static `elftab` table compiled under architecture feature macros. The file changes process-global `errno` before numeric fallbacks and relies on `_audit_elf` elsewhere through consumers, not here.

Dependencies and integration: depends on `libaudit.h`, generated `*_tables.h`, `msg_typetabs.h`, `machinetabs.h`, `optabs.h`, and optional `WITH_ARM`, `WITH_AARCH64`, `WITH_RISCV`, `WITH_IO_URING`, `NO_TABLES`. It is used by rule parsers, auditctl listing, ausearch/aureport interpretation, and tests.

Risks and test signals: correctness depends on generated tables matching kernel UAPI and architecture syscall numbering. `audit_name_to_msg_type` uses bounded local copy but intentionally truncates long `UNKNOWN[]` numbers. `lookup_test.c` is the direct regression signal for bidirectional table coverage and alias exceptions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/lookup_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/machinetab.h -->
# sources/security-integrity/audit-userspace/lib/machinetab.h

Purpose: `_S(machine_id, name)` source table for audit machine aliases. It maps strings such as `i386`, `x86_64`, `ppc64le`, `s390x`, optional ARM/AArch64/RISC-V names, and optional `uring` to libaudit `MACH_*` ids.

Important APIs/types: it does not define functions by itself; it is included by generated lookup code and by `lookup_test.c` with `_S` redefined. The effective APIs are `audit_name_to_machine` and `audit_machine_to_name` in `lookup_table.c`.

Control flow: inclusion-time data expansion only. Ordering matters for reverse lookup because several names map to the same id, so canonical output is the first generated reverse-table match.

State and persistence: no runtime state. Feature macros decide which aliases compile into the binary.

Dependencies and integration: includes `config.h` and depends on `WITH_ARM`, `WITH_AARCH64`, `WITH_IO_URING`, and `WITH_RISCV`. It integrates with ELF architecture translation through `lookup_table.c`'s `elftab`.

Risks and test signals: alias changes can alter printed architecture names. `lookup_test.c` excludes several i386 and ARM aliases when testing reverse lookup because one numeric id has multiple accepted strings.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/machinetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/msg_typetab.h -->
# sources/security-integrity/audit-userspace/lib/msg_typetab.h

Purpose: `_S(audit_type, name)` source table for translating kernel audit record type constants to stable audit log names. It covers user, daemon, syscall, path, SELinux/AppArmor, integrity, anomaly, crypto, virtualization, and newer event types such as `URINGOP`, `OPENAT2`, and device-mapper records.

Important APIs/types: consumed by generated `msg_type_s2i` and `msg_type_i2s`, surfaced as `audit_name_to_msg_type` and `audit_msg_type_to_name`. Commented-out entries document intentionally omitted or daemon-filtered/deprecated types.

Control flow: static table expansion only. The surrounding lookup code falls back to decimal and `UNKNOWN[n]` parsing when this table has no match.

State and persistence: no mutable state. Build-time feature macro `WITH_APPARMOR` controls AppArmor entries.

Dependencies and integration: included by `lookup_table.c` and directly by `lookup_test.c`. Consumers include audit log parsers, rule listing for `msgtype`, and audit report tools.

Risks and test signals: missing new kernel record types cause numeric/unknown output rather than symbolic names. Reverse lookup ambiguity is low because names are unique. `lookup_test.c` verifies every included entry round-trips.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/msg_typetab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/netlink.c -->
# sources/security-integrity/audit-userspace/lib/netlink.c

Purpose: low-level libaudit transport for the kernel audit netlink protocol. It opens/closes `NETLINK_AUDIT`, sends audit requests, receives replies, validates message origin and size, and maps netlink payloads into `struct audit_reply` convenience pointers.

Important APIs: `audit_open`, `audit_close`, `audit_get_reply`, `__audit_send`, and `audit_send`. Internal helpers are `adjust_reply` and `check_ack`.

Control flow: `audit_open` creates a close-on-exec raw netlink socket. `__audit_send` validates fd and payload size, assigns a static sequence number, constructs `struct audit_message`, sends to kernel pid 0, then waits for an ACK through `check_ack`. `audit_get_reply` receives, retries on `EINTR`, rejects spoofed nonzero `nl_pid`, and delegates payload interpretation to `adjust_reply`.

State and persistence: uses a process-local static sequence counter in `__audit_send`; no disk persistence. It mutates `errno` to communicate protocol errors and adjusts pointer fields inside the caller-owned reply structure.

Dependencies and integration: depends on `libaudit.h`, `private.h`, Linux netlink macros, `poll`, `recvfrom`, and `sendto`. Higher-level APIs in libaudit and `auditctl.c` use this file to change kernel audit status and rules.

Risks and test signals: the static sequence counter is not synchronized for concurrent callers. `check_ack` polls up to about 40 seconds and peeks before consuming `NLMSG_ERROR`; behavior depends on kernel ACK timing. Important security checks are NLMSG validation and kernel-origin enforcement. Integration tests require a live audit-capable kernel and privileges.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/optab.h -->
# sources/security-integrity/audit-userspace/lib/optab.h

Purpose: operator lookup table mapping audit comparison constants to rule syntax symbols: `=`, `!=`, `>`, `>=`, `<`, `<=`, `&`, and `&=`.

Important APIs/types: expanded into generated lookup functions and exposed primarily through `audit_operator_to_symbol`; parsing in other libaudit code uses the same constants.

Control flow: static data only. Listing code calls the generated integer-to-string path when printing fields and comparisons.

State and persistence: none.

Dependencies and integration: included by `lookup_table.c`, `auditctl-listing.c` indirectly via libaudit lookup APIs, and `lookup_test.c`.

Risks and test signals: operator constants must match kernel/libaudit rule encoding. `lookup_test.c` checks integer-to-symbol output for every entry.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/optab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/permtab.h -->
# sources/security-integrity/audit-userspace/lib/permtab.h

Purpose: maps audit permission categories to syscall-name sets used by permission-based audit rules. Categories are `AUDIT_PERM_EXEC`, `AUDIT_PERM_WRITE`, `AUDIT_PERM_READ`, and `AUDIT_PERM_ATTR`.

Important APIs/types: consumed by generated `perm_s2i` and `perm_i2s`, surfaced internally as `audit_name_to_perm` and `audit_perm_to_name`.

Control flow: static expansion only. The strings are comma-separated syscall groups used by libaudit rule expansion logic.

State and persistence: none.

Dependencies and integration: documented as sourced from generic audit headers and architecture audit code. Used by libaudit permission parsing and tested by lookup table tests when built.

Risks and test signals: permission groups are policy-sensitive; stale syscall membership can create audit gaps or noisy over-auditing. The direct test signal is lookup round-trip, but semantic completeness must be reviewed against kernel audit permission definitions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/permtab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/ppc_table.h -->
# sources/security-integrity/audit-userspace/lib/ppc_table.h

Purpose: PowerPC syscall number-to-name table for libaudit syscall parsing and printing. It spans legacy calls, modern network/socket calls, io_uring setup calls, landlock, xattr-at, namespace, and recent syscalls through `rseq_slice_yield`.

Important APIs/types: no standalone functions; included by generated `ppc_syscall_s2i` and `ppc_syscall_i2s` used by `audit_name_to_syscall` for `MACH_PPC`, `MACH_PPC64`, and `MACH_PPC64LE`.

Control flow: static `_S(number, name)` expansion. Numeric gaps and reserved comments are intentional ABI records.

State and persistence: no state.

Dependencies and integration: compiled into libaudit unless `NO_TABLES`; included directly by `lookup_test.c`.

Risks and test signals: wrong numbers break audit rule matching on PPC families. Because 32/64 PPC share this table in lookup dispatch, architecture-specific divergences must be handled carefully. `lookup_test.c` checks bidirectional lookups for all entries.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/ppc_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/private.h -->
# sources/security-integrity/audit-userspace/lib/private.h

Purpose: internal libaudit header for hidden APIs, remote auditd message-wrapper protocol constants, endian packing helpers, and shared parser state declarations.

Important APIs/types: defines `hide_t`, `struct auditd_remote_message_wrapper`, `AUDIT_RMW_*` protocol constants, pack/unpack macros, `audit_send`, `__audit_send`, `audit_msg`, `audit_send_user_message`, internal permission lookup prototypes, `_audit_parse_syscall`, and parser globals such as `_audit_permadded`, `_audit_archadded`, `_audit_syscalladded`, `_audit_exeadded`, `_audit_filterfsadded`, and `_audit_elf`.

Control flow: macro-based serialization writes and reads little-endian protocol fields in byte buffers. Function declarations connect libaudit internals and hide selected symbols with `AUDIT_HIDDEN_START/END`.

State and persistence: declares process-global parser flags and current ELF architecture used across audit rule parsing. The remote wrapper protocol carries sequence ids but this header has no storage.

Dependencies and integration: depends on `stdint.h`, `dso.h`, and `libaudit` structures. Used by netlink, lookup, auditctl, auditd remote logging paths, and parser code.

Risks and test signals: macros evaluate arguments directly and assume an `unsigned char *` buffer with enough length. Protocol constants must remain stable for remote auditd compatibility. Parser globals require careful reset between rule lines; `auditctl.c::reset_vars` is the main control signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/riscv32_table.h -->
# sources/security-integrity/audit-userspace/lib/riscv32_table.h

Purpose: RISC-V 32-bit syscall table for libaudit. It reflects the generic syscall base with 32-bit variants such as `fcntl64`, `statfs64`, `truncate64`, time64 syscalls, and current newer syscalls through namespace/list operations.

Important APIs/types: compiled into generated `riscv32_syscall_s2i` and `riscv32_syscall_i2s`, used when `audit_name_to_syscall` receives `MACH_RISCV32`.

Control flow: static `_S` expansions only. Gaps are preserved where the ABI has no auditable entry or a skipped number.

State and persistence: none.

Dependencies and integration: compiled under `WITH_RISCV` and included by `lookup_test.c` when that feature is enabled.

Risks and test signals: the table is new and must track RISC-V UAPI syscall additions closely. Incorrect 32-bit vs 64-bit naming can make `auditctl` load rules that match the wrong syscall number. Lookup tests verify round-trip entries under `WITH_RISCV`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/riscv32_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/riscv64_table.h -->
# sources/security-integrity/audit-userspace/lib/riscv64_table.h

Purpose: RISC-V 64-bit syscall table for libaudit. It maps RISC-V syscall numbers to names, including generic syscalls, RISC-V-specific `riscv_hwprobe` and `riscv_flush_icache`, and modern additions such as `openat2`, `fchmodat2`, `mseal`, `listns`, and `rseq_slice_yield`.

Important APIs/types: feeds generated `riscv64_syscall_s2i` and `riscv64_syscall_i2s` for `MACH_RISCV64`.

Control flow: static include-time expansion, with intentional ABI gaps.

State and persistence: none.

Dependencies and integration: compiled under `WITH_RISCV`, used by `lookup_table.c`, and included by `lookup_test.c`.

Risks and test signals: must stay synchronized with Linux RISC-V syscall numbers; mismatches affect both rule creation and rule listing. Lookup tests validate present entries but not semantic auditability.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/riscv64_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/s390_table.h -->
# sources/security-integrity/audit-userspace/lib/s390_table.h

Purpose: 32-bit s390 syscall table for audit rule parsing and listing. It includes legacy s390 calls, 32-bit uid/gid variants, time64 additions, s390-specific PCI/runtime calls, and modern common syscalls.

Important APIs/types: generates `s390_syscall_s2i` and `s390_syscall_i2s`, selected by `audit_name_to_syscall` for `MACH_S390`.

Control flow: static `_S(number, name)` data expansion with reserved/commented gaps.

State and persistence: none.

Dependencies and integration: compiled into libaudit and included by `lookup_test.c`.

Risks and test signals: s390 has many compatibility and legacy names; stale entries can break 32-bit compatibility auditing. `lookup_test.c` checks bidirectional mapping for all included entries.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/s390_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/s390x_table.h -->
# sources/security-integrity/audit-userspace/lib/s390x_table.h

Purpose: 64-bit s390x syscall table for audit rule parsing and listing. It maps s390x syscall numbers to canonical names and preserves s390-specific calls and ABI gaps.

Important APIs/types: generates `s390x_syscall_s2i` and `s390x_syscall_i2s`, selected by `audit_name_to_syscall` for `MACH_S390X`.

Control flow: static table expansion. Some legacy or nontraditional entries are omitted/commented to avoid reporting them as ordinary syscalls.

State and persistence: none.

Dependencies and integration: used by libaudit lookup dispatch and direct lookup tests.

Risks and test signals: divergence between s390 and s390x numbering makes copy/paste changes risky. `auditctl.c::check_rule_mismatch` specifically compares 64-bit and 32-bit masks for several architectures, including s390x to s390, to warn about unspecified arch rules.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/s390x_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/test/Makefile.am -->
# sources/security-integrity/audit-userspace/lib/test/Makefile.am

Purpose: Automake fragment for libaudit lookup tests.

Important APIs/types: defines `AM_CPPFLAGS` to include the library source, `AM_CFLAGS` with `_GNU_SOURCE`, warning flags, and optional ASAN flags, then registers `lookup_test` as both `check_PROGRAMS` and `TESTS`.

Control flow: build-system only. `lookup_test` links against `${top_builddir}/lib/libaudit.la` and depends on that target.

State and persistence: no runtime state. It affects test artifacts generated by Automake.

Dependencies and integration: integrated into the lib test subdirectory and inherits `HAVE_ASAN`, `WFLAGS`, and top build paths.

Risks and test signals: if libaudit is built without optional architecture tables, conditional test code follows feature macros. The main signal is `make check` executing `lookup_test`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/test/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/test/lookup_test.c -->
# sources/security-integrity/audit-userspace/lib/test/lookup_test.c

Purpose: regression test for libaudit lookup tables and audit logging encoding helpers. It includes table headers directly with `_S` redefined into arrays and verifies numeric-to-string and string-to-numeric conversion paths.

Important APIs/functions: helpers `gen_id`, `TEST_I2S`, `TEST_S2I`, per-table tests for architecture syscall tables, action/error/field/flag/fstype/ftype/machine/message/operator tables, optional io_uring and optional ARM/AArch64/RISC-V tests, `test_audit_logging_encoding`, and `main`.

Control flow: `main` seeds `rand(3)`, runs feature-gated table tests, then encoding tests. Each table test validates every known entry and probes random unknown strings/integers for expected failure values.

State and persistence: no persistent state. Uses deterministic pseudo-random generation to avoid accidental known identifiers in negative tests.

Dependencies and integration: includes `libaudit.h` and many `../*_table.h` files. Built and run by `lib/test/Makefile.am`.

Risks and test signals: random negative tests can theoretically collide, but fixed seed and short iteration count make behavior stable. Several reverse lookup exceptions are explicitly excluded for aliases such as `madvise1`, `EWOULDBLOCK`, `EDEADLOCK`, `loginuid`, and machine aliases.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/test/lookup_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/uringop_table.h -->
# sources/security-integrity/audit-userspace/lib/uringop_table.h

Purpose: maps auditable io_uring operation numbers to operation names. It deliberately includes only io_uring ops considered auditable and points maintainers at kernel `io_uring/opdef.c` audit-skip metadata.

Important APIs/types: feeds generated `uringop_s2i` and `uringop_i2s`, surfaced by `audit_name_to_uringop`, `audit_uringop_to_name`, and auditctl's io_uring rule listing.

Control flow: static table expansion. Missing operation numbers are intentional when kernel marks them non-auditable or they are not listed.

State and persistence: none.

Dependencies and integration: compiled under `WITH_IO_URING`; `auditctl-listing.c` prints io_uring masks via `audit_uringop_to_name`.

Risks and test signals: stale auditability decisions cause rules to reject valid operations or list numbers instead of names. `lookup_test.c` validates table round-trip when io_uring support is enabled.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/uringop_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/x86_64_table.h -->
# sources/security-integrity/audit-userspace/lib/x86_64_table.h

Purpose: x86_64 syscall number table for libaudit. It maps canonical syscall names from `read` through modern entries such as `openat2`, `fchmodat2`, `mseal`, `listns`, and `rseq_slice_yield`.

Important APIs/types: generates `x86_64_syscall_s2i` and `x86_64_syscall_i2s`, selected by `audit_name_to_syscall` for `MACH_86_64`.

Control flow: static `_S` expansion. It intentionally comments nontraditional `uretprobe` and `uprobe` and reserves a range before common additions.

State and persistence: none.

Dependencies and integration: used by auditctl rule parsing/listing, ausearch interpretation, and `lookup_test.c`.

Risks and test signals: x86_64 is a common deployment target, so stale entries have high user impact. `auditctl.c::check_rule_mismatch` warns when names map differently across native and compat arch without explicit `arch=`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/lib/x86_64_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/m4/Makefile.am -->
# sources/security-integrity/audit-userspace/m4/Makefile.am

Purpose: Automake packaging fragment for project m4 macros.

Important APIs/types: sets `CONFIG_CLEAN_FILES`, installs `audit.m4` into `$(datadir)/aclocal` through `dist_m4data_DATA`.

Control flow: build-system only; no runtime behavior.

State and persistence: affects distribution and install artifacts, not program state.

Dependencies and integration: used by the Autotools build so downstream builds can consume audit's aclocal macro.

Risks and test signals: missing `audit.m4` in distribution can break dependent builds. Validation is Automake distribution/install checks rather than runtime tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/m4/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/10-base-config.rules -->
# sources/security-integrity/audit-userspace/rules/10-base-config.rules

Purpose: baseline rule file for systems that want syscall auditing. It deletes existing rules, sets backlog capacity, sets backlog wait time, and chooses audit failure mode.

Important commands: `-D`, `-b 8192`, `--backlog_wait_time 60000`, and `-f 1`.

Control flow: loaded by `auditctl -R` or augenrules in filename order; this file should precede policy files because it resets current rules.

State and persistence: persists only when installed in rules.d and loaded into the kernel audit subsystem. It changes kernel audit backlog/failure configuration.

Dependencies and integration: parsed by `auditctl.c` option handlers for delete-all, backlog, wait time, and failure mode.

Risks and test signals: `-D` removes existing rules, so ordering is critical. Test by loading on an audit-capable host and checking `auditctl -s`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/10-base-config.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/10-no-audit.rules -->
# sources/security-integrity/audit-userspace/rules/10-no-audit.rules

Purpose: performance-oriented policy that disables syscall auditing while leaving hardwired audit events.

Important commands: `-D` clears rules and `-a task,never` suppresses syscall auditing for all tasks.

Control flow: intended as an alternative to `10-base-config.rules` plus normal policy files.

State and persistence: persists through installed rules and kernel task filter state after load.

Dependencies and integration: parsed by auditctl rule setup and sent as a task filter rule.

Risks and test signals: creates major audit coverage gaps by design. Test signal is `auditctl -l` showing the task never rule and absence of syscall rules.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/10-no-audit.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/11-loginuid.rules -->
# sources/security-integrity/audit-userspace/rules/11-loginuid.rules

Purpose: makes loginuid immutable so the audit user id cannot be changed after being set.

Important command: `--loginuid-immutable`, handled by `audit_set_loginuid_immutable`.

Control flow: one command loaded after baseline setup.

State and persistence: sets a kernel audit feature/lock state; changing it may require reboot or feature-specific unlock behavior.

Dependencies and integration: depends on kernel support for audit feature API and `auditctl.c` long option handling.

Risks and test signals: can break workloads that expect to reset loginuid in containers or service managers. `auditctl -s -i` or feature listing verifies state when supported.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/11-loginuid.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/12-cont-fail.rules -->
# sources/security-integrity/audit-userspace/rules/12-cont-fail.rules

Purpose: changes auditctl rules-file load behavior so syntax or unsupported-field errors do not stop immediate processing, but final exit reports failure.

Important command: `-c`.

Control flow: when encountered during `auditctl -R`, `opt_continue` sets `ignore=1` and `continue_error=1`; later errors keep processing and cause a nonzero final result.

State and persistence: process-local auditctl behavior only; no kernel rule state.

Dependencies and integration: meaningful only inside a rules file load path in `auditctl.c::fileopt`.

Risks and test signals: can leave partially loaded rules while still signaling failure. Test by loading a file containing `-c`, a bad rule, and a later valid rule.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/12-cont-fail.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/12-ignore-error.rules -->
# sources/security-integrity/audit-userspace/rules/12-ignore-error.rules

Purpose: changes rules-file loading so auditctl continues across bad rules and exits success.

Important command: `-i`.

Control flow: `opt_ignore` sets `ignore=1`; `fileopt` continues after errors without final failure unless other fatal file errors occur.

State and persistence: process-local loader behavior only.

Dependencies and integration: consumed by `auditctl.c` when reading `-R` files.

Risks and test signals: can hide missing audit coverage on kernels without newer fields. Test with an intentionally unsupported rule and check exit status remains zero.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/12-ignore-error.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/20-dont-audit.rules -->
# sources/security-integrity/audit-userspace/rules/20-dont-audit.rules

Purpose: placeholder for early "do not audit" suppressions. All example rules are commented out.

Important rules: examples suppress cron SELinux subject events, chrony time-adjust syscalls, and `CRYPTO_KEY_USER`.

Control flow: because audit rules are first-match-wins, uncommented suppressions belong early in the rules order.

State and persistence: no effect as shipped because it has zero active rules.

Dependencies and integration: uses normal audit rule syntax if uncommented.

Risks and test signals: uncommenting broad excludes can hide important events. Verify with `auditctl -l` and event generation for the affected source.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/20-dont-audit.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/21-no32bit.rules -->
# sources/security-integrity/audit-userspace/rules/21-no32bit.rules

Purpose: detects use of 32-bit syscall ABI on a 64-bit platform as a possible exploitation signal.

Important rule: `-a always,exit -F arch=b32 -S all -F key=32bit-abi`.

Control flow: loaded as a single exit filter rule.

State and persistence: kernel audit rule state after load.

Dependencies and integration: relies on architecture parsing in libaudit and kernel compat syscall auditing.

Risks and test signals: noisy on systems legitimately running 32-bit binaries; invalid on pure 32-bit systems. Test with a 32-bit executable and search for key `32bit-abi`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/21-no32bit.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/22-ignore-chrony.rules -->
# sources/security-integrity/audit-userspace/rules/22-ignore-chrony.rules

Purpose: suppresses chrony-generated `adjtimex` time-change events for both b64 and b32 architectures.

Important rules: two `never,exit` rules with `auid=unset`, `uid=chrony`, and `subj_type=chronyd_t`.

Control flow: should load before time-change auditing rules so first-match suppression wins.

State and persistence: kernel audit filter state.

Dependencies and integration: assumes chrony user and SELinux type names match the target system.

Risks and test signals: may suppress malicious activity if chrony identity is compromised or labels differ. Validate by observing absence of chrony time-change records while other time-change records remain.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/22-ignore-chrony.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/23-ignore-filesystems.rules -->
# sources/security-integrity/audit-userspace/rules/23-ignore-filesystems.rules

Purpose: suppresses events originating from noisy pseudo filesystems during module load and tracing.

Important rules: `never,filesystem` filters for `fstype=tracefs` and `fstype=debugfs`.

Control flow: early filesystem filter rules reduce later event volume.

State and persistence: kernel filesystem filter state.

Dependencies and integration: depends on `fstype` field lookup from libaudit.

Risks and test signals: can hide activity on debug/tracing filesystems. Test by loading rules and checking `auditctl -l` for filesystem filters.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/23-ignore-filesystems.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-1-create-failed.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-1-create-failed.rules

Purpose: OSPP v4.2 unsuccessful file creation auditing for `open*` with `O_CREAT` and `creat`.

Important rules: 12 b32/b64 rules covering `openat`, `open_by_handle_at`, `open`, and `creat` with exits `-EACCES` and `-EPERM`, user filters `auid>=1000` and `auid!=unset`, key `unsuccessful-create`.

Control flow: should precede broader failed access rules so create failures get the more specific key.

State and persistence: kernel exit filter rules.

Dependencies and integration: syscall numbers and octal argument masks are parsed by auditctl/libaudit.

Risks and test signals: argument positions differ between `open` and `openat`, which this file handles separately. Test with denied create attempts and ausearch key `unsuccessful-create`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-1-create-failed.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-1-create-success.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-1-create-success.rules

Purpose: OSPP successful file creation auditing.

Important rules: six b32/b64 rules for `openat/open_by_handle_at` with `a2&0100`, `open` with `a1&0100`, and `creat`, all with `success=1`, `auid>=1000`, `auid!=unset`, key `successful-create`.

Control flow: loads as specific creation success filters before general successful access rules.

State and persistence: kernel audit exit rules.

Dependencies and integration: relies on arch-specific syscall tables and argument mask parsing.

Risks and test signals: can be high volume on busy systems. Test by creating files as a normal logged-in user and searching `successful-create`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-1-create-success.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-2-modify-failed.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-2-modify-failed.rules

Purpose: OSPP unsuccessful file modification auditing for write-open and truncate operations.

Important rules: 12 b32/b64 rules cover `openat/open_by_handle_at` and `open` with write/truncate masks, plus `truncate` and `ftruncate`, for `-EACCES` and `-EPERM`, key `unsuccessful-modification`.

Control flow: specific failed modification filters should precede broader failed access rules.

State and persistence: kernel exit filters.

Dependencies and integration: depends on correct octal masks and syscall argument positions.

Risks and test signals: broad write-open masks may be noisy. Test denied write/truncate attempts and search key `unsuccessful-modification`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-2-modify-failed.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-2-modify-success.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-2-modify-success.rules

Purpose: OSPP successful file modification auditing.

Important rules: six b32/b64 rules cover write-open variants and truncation with `success=1`, user auid filters, and key `successful-modification`.

Control flow: loads as syscall exit filters after baseline and before broader access success rules.

State and persistence: kernel audit rules.

Dependencies and integration: auditctl parses syscall lists, arch selectors, argument bit masks, and success field.

Risks and test signals: can generate substantial volume for normal writes. Validate by modifying a file as a logged-in user and querying key `successful-modification`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-2-modify-success.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-3-access-failed.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-3-access-failed.rules

Purpose: OSPP unsuccessful file access catch-all for open-like syscalls not already classified as create/modify.

Important rules: four b32/b64 rules for `open`, `openat`, `openat2`, and `open_by_handle_at` with `-EACCES` or `-EPERM`, user auid filters, key `unsuccessful-access`.

Control flow: comments state it must go last among access/create/modify groups to preserve more specific keys.

State and persistence: kernel exit filters.

Dependencies and integration: relies on first-match audit rule behavior and open syscall table entries.

Risks and test signals: if loaded too early it can shadow create/modify failure keys. Test with denied read/open and ausearch key `unsuccessful-access`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-3-access-failed.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-3-access-success.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-3-access-success.rules

Purpose: OSPP successful file access catch-all for open-like syscalls.

Important rules: b32 and b64 rules for `open`, `openat`, `openat2`, and `open_by_handle_at` with `success=1`, user auid filters, key `successful-access`.

Control flow: comments warn it must go last and may generate many events.

State and persistence: kernel exit filters.

Dependencies and integration: parsed by auditctl with syscall and arch lookup support.

Risks and test signals: very high event volume on active systems. Test by opening files and searching key `successful-access`, preferably in a controlled environment.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-3-access-success.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-4-delete-failed.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-4-delete-failed.rules

Purpose: OSPP unsuccessful file deletion/rename auditing.

Important rules: four b32/b64 rules for `unlink`, `unlinkat`, `rename`, and `renameat` with `-EACCES` or `-EPERM`, user auid filters, key `unsuccessful-delete`.

Control flow: loaded as exit filters in the OSPP delete group.

State and persistence: kernel audit rules.

Dependencies and integration: syscall names come from architecture tables.

Risks and test signals: does not include newer `renameat2`; depending on policy expectations that may be a gap. Test denied unlink/rename attempts and search key `unsuccessful-delete`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-4-delete-failed.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-4-delete-success.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-4-delete-success.rules

Purpose: OSPP successful delete/rename auditing.

Important rules: b32 and b64 rules for `unlink`, `unlinkat`, `rename`, and `renameat` with `success=1`, user auid filters, key `successful-delete`.

Control flow: simple exit filters.

State and persistence: kernel audit rules.

Dependencies and integration: auditctl parses syscall lists and success field.

Risks and test signals: may miss `renameat2` if that syscall is used for deletion-like changes. Test with successful unlink and ausearch key `successful-delete`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-4-delete-success.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-5-perm-change-failed.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-5-perm-change-failed.rules

Purpose: OSPP unsuccessful permission and extended-attribute change auditing.

Important rules: four b32/b64 rules for chmod/fchmod/fchmodat/fchmodat2, setxattr/removexattr variants, `setxattrat`, `removexattrat`, and `file_setattr` with `-EACCES` or `-EPERM`, user filters, key `unsuccessful-perm-change`.

Control flow: exit filters grouped by failure code.

State and persistence: kernel audit rules.

Dependencies and integration: depends on syscall availability on the target kernel and architecture.

Risks and test signals: newer syscall names may require new enough audit userspace/kernel; old systems may need `-i` or `-c`. Test denied chmod/xattr operations and key lookup.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-5-perm-change-failed.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-5-perm-change-success.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-5-perm-change-success.rules

Purpose: OSPP successful permission and xattr change auditing.

Important rules: b32 and b64 rules for chmod and xattr modification families with `success=1`, user auid filters, key `successful-perm-change`.

Control flow: loaded as exit rules for success path coverage.

State and persistence: kernel audit rules.

Dependencies and integration: requires syscall tables that include newer `fchmodat2`, `setxattrat`, `removexattrat`, and `file_setattr`.

Risks and test signals: high sensitivity to kernel/userspace version skew. Test with successful chmod/setxattr and search key `successful-perm-change`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-5-perm-change-success.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-6-owner-change-failed.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-6-owner-change-failed.rules

Purpose: OSPP unsuccessful ownership change auditing.

Important rules: four b32/b64 rules for `lchown`, `fchown`, `chown`, `fchownat`, and `file_setattr` with `-EACCES` or `-EPERM`, user filters, key `unsuccessful-owner-change`.

Control flow: exit filters for failure status.

State and persistence: kernel audit rules.

Dependencies and integration: depends on syscall lookup and errno lookup for symbolic failures.

Risks and test signals: `file_setattr` inclusion assumes newer kernel support. Test denied chown operations and search key `unsuccessful-owner-change`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-6-owner-change-failed.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-6-owner-change-success.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42-6-owner-change-success.rules

Purpose: OSPP successful ownership change auditing.

Important rules: b32 and b64 rules for chown family plus `file_setattr` with `success=1`, user filters, key `successful-owner-change`.

Control flow: exit filters loaded in the OSPP owner-change group.

State and persistence: kernel audit rules.

Dependencies and integration: uses auditctl syscall list parsing and auid filters.

Risks and test signals: may be noisy on administrative systems. Test with successful chown as a logged-in administrative user and query key `successful-owner-change`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42-6-owner-change-success.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42.rules -->
# sources/security-integrity/audit-userspace/rules/30-ospp-v42.rules

Purpose: umbrella OSPP v4.2 audit policy profile supplementing the split create/modify/access/delete/permission/owner files. It targets account/group modification, special configuration utilities, session files, audit trail access, MAC policy, and privilege escalation helpers.

Important rules: 72 active rules. Keys include `user-modify`, `group-modify`, `special-config-changes`, `session`, `access-audit-trail`, `MAC-policy`, and `maybe-escalation`.

Control flow: intended to be installed with `10-base-config.rules`, `11-loginuid.rules`, and the split `30-ospp-v42-*` files. It uses b32/b64 pairs for paths and syscall filters.

State and persistence: kernel audit rule state after rules.d load.

Dependencies and integration: relies on auditctl path/dir/perm parsing, arch selectors, auid filters, and first-match ordering.

Risks and test signals: many path rules assume distribution-specific binaries such as `/usr/sbin/unix_chkpwd`, `/usr/bin/pkexec`, and `/usr/bin/systemd-run`. Test by `auditctl -R` on target distro and key-based ausearch checks for representative paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-ospp-v42.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-pci-dss-v31.rules -->
# sources/security-integrity/audit-userspace/rules/30-pci-dss-v31.rules

Purpose: PCI DSS v3.1-oriented audit policy profile covering cardholder data access placeholders, privileged configuration changes, audit trail access, account changes, system objects, time changes, and audit log modification.

Important rules: 46 active rules. Keys include `10.2.1-cardholder-access`, `10.2.2-priv-config-changes`, `10.2.3-access-audit-trail`, `10.2.5.*`, `10.2.7-system-objects`, `10.4.2b-time-change`, and `10.5.5-*`.

Control flow: loaded as a rules.d profile after base configuration. Some sample paths such as `path-to-db` and `path-to-log` are placeholders requiring site customization.

State and persistence: kernel audit rules when loaded.

Dependencies and integration: standard auditctl parser; uses b32/b64 arch pairs, path/dir filters, and syscall filters.

Risks and test signals: placeholder paths must be replaced or rules will not provide intended compliance evidence. Test with `auditctl -R` and targeted operations for time change, audit tool execution, account file changes, and configured data paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-pci-dss-v31.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-stig.rules -->
# sources/security-integrity/audit-userspace/rules/30-stig.rules

Purpose: STIG-oriented audit profile covering time changes, identity files, locale/network identity files, MAC policy, login/session files, permission changes, failed access, mounts, deletes, sudo configuration, and escalation helpers.

Important rules: 52 active rules. Keys include `time-change`, `identity`, `system-locale`, `MAC-policy`, `logins`, `session`, `perm_mod`, `access`, `export`, `delete`, `actions`, and `maybe-escalation`.

Control flow: intended with `10-base-config.rules` and `99-finalize.rules`; comments describe assumptions about UID_MIN, root login, and possible local narrowing.

State and persistence: kernel audit rules after load.

Dependencies and integration: parsed by auditctl and relies on path existence/meaning across distributions.

Risks and test signals: broad `dir=/etc` and access rules can be noisy. Some optional login/session watches are commented. Test with representative file changes and check ausearch keys.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/30-stig.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/31-privileged.rules -->
# sources/security-integrity/audit-userspace/rules/31-privileged.rules

Purpose: template for generating privileged command audit rules from setuid files and file capabilities.

Important rules: no active rules. Comments provide `find`, `awk`, and `filecap` pipelines that emit b64 rules with key `privileged`.

Control flow: site administrators generate concrete path rules and usually add b32 equivalents.

State and persistence: no effect as shipped.

Dependencies and integration: generated output uses standard auditctl path/perm/auid syntax.

Risks and test signals: stale generated lists miss newly installed privileged binaries; generated rules are distro/local-state dependent. Test by regenerating on the target system and executing a known privileged binary.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/31-privileged.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/32-power-abuse.rules -->
# sources/security-integrity/audit-userspace/rules/32-power-abuse.rules

Purpose: detects root browsing user home directories when the login audit uid belongs to a normal user.

Important rule: `-a always,exit -F dir=/home -F uid=0 -F auid>=1000 -F auid!=unset -C auid!=obj_uid -F key=power-abuse`.

Control flow: one exit filter using inter-field comparison.

State and persistence: kernel audit rule state.

Dependencies and integration: requires audit interfield comparison parsing via `audit_rule_interfield_comp_data`.

Risks and test signals: can be noisy for legitimate support/admin work and may miss non-`/home` user directories. Test by root accessing another user's home and searching `power-abuse`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/32-power-abuse.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/40-local.rules -->
# sources/security-integrity/audit-userspace/rules/40-local.rules

Purpose: empty local customization anchor for site-specific watches after packaged policy rules.

Important rules: no active rules; comments show path and directory examples.

Control flow: filename positions local additions around the middle/end of the rule set.

State and persistence: no effect until edited locally.

Dependencies and integration: standard auditctl syntax.

Risks and test signals: packaged updates should preserve local intent only if admins manage this file appropriately. Test any added local rule with `auditctl -l` and event generation.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/40-local.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/41-containers.rules -->
# sources/security-integrity/audit-userspace/rules/41-containers.rules

Purpose: logs container creation and configuration-related namespace operations.

Important rules: b32/b64 `clone` rules with namespace flag mask `a0&0x7C020000` key `container-create`, and b32/b64 `unshare,setns` rules key `container-config`.

Control flow: syscall exit filters.

State and persistence: kernel audit rules.

Dependencies and integration: architecture syscall tables and argument bit-test parsing.

Risks and test signals: clone flag masks may not cover all container runtimes or newer clone3 paths. Test by starting a container and searching container keys.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/41-containers.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/42-injection.rules -->
# sources/security-integrity/audit-userspace/rules/42-injection.rules

Purpose: detects ptrace tracing and injection-like operations.

Important rules: active b64 broad `ptrace` tracing rule, plus b32/b64 argument-specific rules for `PTRACE_POKETEXT`, `PTRACE_POKEDATA`, and `PTRACE_POKEUSER` style values with keys `code-injection`, `data-injection`, and `register-injection`.

Control flow: syscall exit filters with argument equality.

State and persistence: kernel audit rules.

Dependencies and integration: parsed through syscall and argument field support.

Risks and test signals: debugging and observability tools can generate legitimate events; the b32 broad tracing rule is commented. Test with controlled ptrace operations and key searches.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/42-injection.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/43-module-load.rules -->
# sources/security-integrity/audit-userspace/rules/43-module-load.rules

Purpose: audits kernel module insertion and removal through syscalls rather than program watches.

Important rules: b32/b64 `init_module,finit_module` key `module-load`; b32/b64 `delete_module` key `module-unload`.

Control flow: syscall exit filters.

State and persistence: kernel audit rules.

Dependencies and integration: requires architecture syscall mappings.

Risks and test signals: may miss module activity performed before audit rules are loaded. Test with controlled module load/unload and search the module keys.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/43-module-load.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/44-installers.rules -->
# sources/security-integrity/audit-userspace/rules/44-installers.rules

Purpose: audits execution of common software installer/package tools.

Important rules: 14 b32/b64 path execution rules for `dnf-3`, `yum`, `pip`, `npm`, `cpan`, `gem`, and `luarocks`, key `software-installer`.

Control flow: path/perm execution filters.

State and persistence: kernel audit rules.

Dependencies and integration: assumes installer paths under `/usr/bin`; auditctl path and perm parsing.

Risks and test signals: misses tools at alternate paths or package managers not listed. Test by executing a listed installer and searching key `software-installer`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/44-installers.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/70-einval.rules -->
# sources/security-integrity/audit-userspace/rules/70-einval.rules

Purpose: debugging profile to find programs making syscalls with invalid parameters.

Important rules: suppresses b64 `rt_sigreturn`, then audits all syscalls with `exit=-EINVAL` and key `einval-retcode`.

Control flow: late rules intended for troubleshooting rather than production.

State and persistence: kernel audit rules.

Dependencies and integration: uses errno name parsing and broad `-S all`.

Risks and test signals: extremely noisy and may affect performance. Test with a controlled invalid syscall and search `einval-retcode`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/70-einval.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/71-networking.rules -->
# sources/security-integrity/audit-userspace/rules/71-networking.rules

Purpose: simple network connection visibility rule.

Important rule: b64 `accept,connect` exit rule with key `external-access`.

Control flow: single syscall filter.

State and persistence: kernel audit rule state.

Dependencies and integration: x86_64/b64-focused as shipped; no b32 equivalent.

Risks and test signals: very broad network activity logging and incomplete cross-arch coverage. Test with outbound connect or inbound accept and search key `external-access`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/71-networking.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/99-finalize.rules -->
# sources/security-integrity/audit-userspace/rules/99-finalize.rules

Purpose: finalization hook to make audit configuration immutable after all rules load.

Important rules: `-e 2` is present but commented out.

Control flow: filename places it at the end so immutability, if enabled, happens after all rule additions.

State and persistence: no effect as shipped; uncommenting sets kernel audit immutable mode until reboot.

Dependencies and integration: parsed by auditctl enabled flag handler.

Risks and test signals: enabling immutable mode prevents later rule changes and can disrupt automation. Test only with reboot access; verify with `auditctl -s`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/99-finalize.rules -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/Makefile.am -->
# sources/security-integrity/audit-userspace/rules/Makefile.am

Purpose: Automake distribution/install fragment for packaged audit rules.

Important APIs/types: `EXTRA_DIST` lists all shipped `.rules` files plus `README-rules`; `rulesdir = $(datadir)/audit-rules`; `dist_rules_DATA = $(EXTRA_DIST)`.

Control flow: build-system only. Distribution and install targets copy the rule templates to the audit rules data directory.

State and persistence: affects installed package contents, not runtime state.

Dependencies and integration: integrated with Autotools packaging and depends on all listed files existing.

Risks and test signals: adding a rule file without updating this list omits it from distribution/install. Test with `make distcheck` or install tree inspection.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/rules/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/Makefile.am -->
# sources/security-integrity/audit-userspace/src/Makefile.am

Purpose: Automake build definition for audit-userspace command binaries.

Important targets: builds `auditd`, `auditctl`, `aureport`, and `ausearch`; defines source lists, PIE/RELRO flags for auditd/auditctl, headers, subdirectory `test`, and `libev/libev.a` helper target.

Control flow: build-system only. `auditctl_SOURCES` includes `auditctl.c`, `auditctl-llist.c`, `delete_all.c`, and `auditctl-listing.c`; `auditctl_LDADD` links libaudit, auparse, and common libraries.

State and persistence: no runtime state; controls build/install artifacts.

Dependencies and integration: depends on generated config, libaudit, auparse, audisp, common, libev, optional listener support, pthread/math/GSS/libwrap for auditd.

Risks and test signals: source list drift breaks builds or omits files from binaries. Test with full Autotools build and `make check`.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl-listing.c -->
# sources/security-integrity/audit-userspace/src/auditctl-listing.c

Purpose: formats kernel audit status and rule-list replies for `auditctl -s` and `auditctl -l`, including interpreted field/syscall names and watch syntax reconstruction.

Important APIs/functions: `audit_print_init`, `audit_print_reply`, `key_match`; internal helpers `is_watch`, `print_arch`, `print_syscall`, `print_field_cmp`, `print_rule`, `get_enable`, and `get_failure`.

Control flow: list replies are buffered into a local linked list after optional key filtering. On `NLMSG_DONE`, the socket is closed and buffered rules are printed. Rule printing detects watch-style rules, prints action/filter/arch/syscalls, then iterates fields with special handling for string buffers, keys, perms, args, errno exits, fstypes, loginuid/session unset, and interfield comparisons.

State and persistence: static `auparse_state_t *au`, static list `l`, and `printed` state persist within the process. `_audit_elf` is reset/used to interpret syscall names by architecture.

Dependencies and integration: depends on libaudit lookup APIs, `auditctl-llist`, auparse interpretation helpers, `key` and `interpret` globals from `auditctl.c`, and optional io_uring constants.

Risks and test signals: buffer offset accounting for string fields must match kernel `audit_rule_data` layout. Listing output can change with table aliases. Exercise with `auditctl -l`, `auditctl -l -i`, `auditctl -l -k key`, and rules containing watches, dir filters, comparisons, and argument filters.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl-listing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl-listing.h -->
# sources/security-integrity/audit-userspace/src/auditctl-listing.h

Purpose: public header within the auditctl binary for rule/status listing helpers.

Important APIs/types: declares `audit_print_init`, `audit_print_reply`, and `key_match`, and includes `libaudit.h` for `struct audit_reply` and `struct audit_rule_data`.

Control flow: none; declaration-only header.

State and persistence: none.

Dependencies and integration: included by `auditctl.c` and implemented by `auditctl-listing.c`.

Risks and test signals: prototype drift breaks auditctl build. Build auditctl and exercise list/status commands.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl-listing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl-llist.c -->
# sources/security-integrity/audit-userspace/src/auditctl-llist.c

Purpose: minimal singly linked list used by auditctl listing code to store copies of kernel rule data before printing.

Important APIs/functions: `list_create`, `list_first`, `list_last`, `list_next`, `list_append`, and `list_clear`.

Control flow: append allocates a node, optionally deep-copies a rule payload of caller-provided size, links at current tail, and makes the new node current. Clear walks all nodes, freeing copied rule data and nodes.

State and persistence: state is held in caller-owned `llist` structures; no globals or disk persistence.

Dependencies and integration: depends on `auditctl-llist.h` and `struct audit_rule_data`. Used by `auditctl-listing.c` for `AUDIT_LIST_RULES` buffering.

Risks and test signals: append assumes `l->cur` is the tail when list is nonempty; callers must use append consistently. Allocation failure returns 1. Test through `auditctl -l` with many rules and memory-checking builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl-llist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl-llist.h -->
# sources/security-integrity/audit-userspace/src/auditctl-llist.h

Purpose: type and function declarations for auditctl's local rule linked list.

Important APIs/types: defines `lnode` with `struct audit_rule_data *r`, `size`, and `next`; defines `llist` with `head`, `cur`, and `cnt`; declares list manipulation functions and inline `list_get_cur`.

Control flow: none in header except the trivial current-node accessor.

State and persistence: caller-owned in-memory list state only.

Dependencies and integration: includes `config.h`, `sys/types.h`, and `libaudit.h`; used by `auditctl-listing.c`.

Risks and test signals: no ownership annotations beyond comments; misuse can leak or double-free copied rule data. Build plus listing tests cover normal usage.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl-llist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl.c -->
# sources/security-integrity/audit-userspace/src/auditctl.c

Purpose: command-line tool for controlling Linux audit: status, rule loading, rule listing/deletion, watches, backlog/failure settings, user messages, loginuid immutability, auditd signals, and rules-file processing.

Important APIs/functions: `main`, `setopt`, `handle_option`, option handlers `opt_*`, `fileopt`, `handle_request`, `get_reply`, `reset_vars`, `audit_rule_setup`, `audit_setup_watch_name`, `audit_setup_perms`, `check_rule_mismatch`, `send_signal`, `report_status`, and optional `parse_io_uring`.

Control flow: `main` validates arguments/root capability, chooses direct CLI or `-R` file load, initializes netlink/rule state, parses options with `getopt_long`, then sends requests or reads replies. `fileopt` opens a regular non-world-writable file, tokenizes lines with escaped-space preprocessing, resets parser globals per line, parses options, and handles each request. `handle_request` sends add/delete rule operations, defaulting missing non-task syscalls to `all`, retries legacy watch rules with `AUDIT_WATCH`, and closes the audit fd unless listing is still active.

State and persistence: process globals track fd, key buffer, add/delete/action state, ignore/continue behavior, interpretation mode, and `rule_new`. It also resets libaudit parser globals such as `_audit_elf` between rules. Kernel audit subsystem state is changed through netlink; rules-file changes persist only in the kernel until reboot/reload unless the file remains installed.

Dependencies and integration: depends on libaudit rule APIs, netlink transport, `auditctl-listing`, `delete_all_rules`, aucommon messaging, syscall table lookup, kernel feature macros, and optional pidfd syscalls for safer auditd signaling.

Risks and test signals: complex global state makes reset correctness critical for `-R` loads. Path validation rejects relative paths but only warns on `..` and wildcards. `process_key_option` enforces key length and separator restrictions. Version skew can make newer fields/syscalls fail unless `-i`/`-c` is used. Test with CLI status/list/add/delete, rules-file loading with comments/escapes/errors, watch rules, key filtering, immutable-mode handling, and auditd signal paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/src/auditctl.c -->
