# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/severity.c

Purpose: grades MCE records into recovery, keep, deferred, uncorrected, action-required, or panic severities.

Important APIs and flow: Intel-compatible grading is table-driven through `severities[]`; first matching rule wins using status masks, MCG status masks, software error recovery availability, exception context, CPU model/stepping, and bank ranges. `error_context()` classifies user, kernel, or recoverable-kernel context, using exception-table fixup types and instruction decoding to identify copy-from-user accesses. AMD/Hygon grading in `mce_severity_amd()` follows PPR-style logic: PCC panics, deferred errors are deferred, corrected errors are kept, overflow without recovery panics, lack of SUCCOR panics, and unrecoverable kernel context panics. `mce_severity()` dispatches by vendor. Debugfs `severities-coverage` reports and resets which Intel rules have been exercised.

State and persistence: mutates `m->kflags` for recoverable kernel/copyin paths and records debugfs coverage bits in the severity table. No persistence beyond runtime.

Dependencies and integration: central to `machine_check_poll()` and `do_machine_check()`, and depends on memory failure configuration, exception tables, instruction decoder, CPU model IDs, and common `mca_cfg`.

Risks and test signals: rule ordering is safety-critical; a too-low severity can allow corruption, while a too-high severity panics unnecessarily. Signals include injection coverage for table rules, copy-from-user recovery tests, memory_failure-enabled/disabled builds, AMD deferred/SUCCOR cases, and debugfs coverage.
