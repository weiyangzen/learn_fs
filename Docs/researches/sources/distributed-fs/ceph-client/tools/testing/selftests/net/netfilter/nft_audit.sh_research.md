## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/nft_audit.sh

Purpose: validates audit records emitted by nftables operations, checking operation names and aggregated entry counts for table, chain, rule, set, element, counter, quota, reset, flush, and delete paths.

Important APIs and tools: uses `nft`, `unshare -n`, compiled `./audit_logread`, temp files, shell process substitution, `diff`, `sed`, and audit daemon detection through `/var/run/auditd.pid`.

Control flow: skips if auditd is active or nft lacks reset support. It re-execs in a new net namespace, starts `audit_logread` to normalize audit output, then `do_test()` drains prior logs, executes a command, waits briefly, summarizes adjacent audit lines with the same prefix/suffix by adding `entries=`, and diffs against the expected string. The script builds nft state progressively across add/set/reset/delete scenarios, including bulk 500-rule/object cases, handle-based rule deletes, set element resets/deletes, and table flushes.

State and persistence: temp rule/log files and audit PID registration; trap kills audit reader and removes files. It globally manipulates audit enabled/PID via helper, so it skips when auditd owns audit. Dependencies are audit kernel support, privileges, recent nft, and exact audit message schema. Risks include races with other nft/audit activity, fixed sleep for log delivery, and `RC--` producing negative failure count. Test signal is per-command OK/FAIL diff and final `RC`.
