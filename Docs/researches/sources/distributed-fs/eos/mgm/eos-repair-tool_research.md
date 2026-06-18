<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/eos-repair-tool -->
# sources/distributed-fs/eos/mgm/eos-repair-tool

## Purpose

`eos-repair-tool` is an interactive Perl terminal helper for operators repairing EOS fsck findings. It fetches or reads fsck reports, groups logical filenames by fsck tag, displays file diagnostics, and issues EOS CLI repair commands such as verify, adjustreplica, drop, and bulk set operations.

## Important APIs, Types, and Functions

The script uses `Term::ReadKey` in cbreak mode and drives the external `eos -b` CLI. Top-level actions are `r` to write `/tmp/eos.fsck.report`, `f` to load `/tmp/eos.fsck.report` and `/tmp/eos.external.lfn`, `p` to process already loaded sets, `u` to disable/enable fsck collection, and `s` to show fsck status. Inner actions include next/previous navigation, `a`/`A` adjust replica, `v`/`V` verify checksum, `c`, `C`, `X` verify plus checksum/size commit variants, `d` drop a selected replica, `D` try automatic bad-size replica drops, `E` rescan and retain only still-bad files, `e` export the current set, and `y` show checksum-attribute checks.

## Control Flow

The script loops forever clearing the screen, reading one command key, and branching with independent `if` statements. Report loading parses whitespace-separated `key=value` tokens and splits `lfn=` lists by comma into `$lfnhash->{tag}->{lfn}`. Processing presents available tag sets, lets the user select one by numeric key, then loops over LFNs, running `eos file info` and `eos file check` before accepting repair commands.

## State and Persistence Behavior

Runtime state is held in Perl hashes and arrays. Persistent side effects are all external: `/tmp/eos.fsck.report`, optional `/tmp/eos.external.lfn`, `/tmp/eos.set.lfn`, and repair mutations made through the EOS MGM CLI. Terminal mode is restored to normal at script exit.

## Dependencies and Integration Points

The tool depends on Perl, `Term::ReadKey`, a working `eos` client, shell utilities such as `clear`, `grep`, and `unlink`, and an operator with authority to run file repair commands. It complements the C++ fsck engine by providing a human-guided workflow over `eos fsck report` and `eos file check`.

## Risks and Edge Cases

The parser is fragile for quoted values containing spaces. Many shell commands interpolate LFNs directly, so special characters in paths can break commands or create injection risk. The `D` branch contains apparent Perl bugs where `hash->` is used without `$`, and `%$hash` data is not reset per file. Numeric set selection is not validated. Bulk actions can drop or rewrite replicas across an entire set with minimal confirmation.

## Test Signals

Smoke tests can run against mocked `eos` commands and sample fsck report lines. Operator tests should verify parsing of multi-LFN reports, set selection, export output, rescan filtering, terminal mode restoration after quit, and dry-run review of every bulk command path before production use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/eos-repair-tool -->
