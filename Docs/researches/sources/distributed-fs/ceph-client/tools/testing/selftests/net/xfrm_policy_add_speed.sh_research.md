# sources/distributed-fs/ceph-client/tools/testing/selftests/net/xfrm_policy_add_speed.sh

Purpose: XFRM policy insertion performance and scalability smoke test. It inserts growing batches of IPv4 block policies and verifies the kernel reports the same number inserted.

Important APIs/functions: `do_dummies4()` generates `ip xfrm policy add ... action block` commands with nested loops over source/destination prefixes. `do_bench()` writes a batch file, times `ip -batch`, counts generated policies, and compares with `ip xfrm policy show | grep "action block" | wc -l`.

Control flow: creates one namespace, then tests batch sizes 100, 1000, 10000, and up to 100000 unless `KSFT_MACHINE_SLOW=yes`, where max is 10000. Each batch flushes existing policies before generating a new set and times insertion with a 4-minute timeout.

State and persistence: one temporary namespace and one temp batch file; cleanup deletes namespace and file. XFRM policies are ephemeral.

Dependencies and integration: requires root, iproute2 xfrm, timeout utility, and `lib.sh`. Intended as speed/regression telemetry rather than strict threshold benchmark.

Risks: no fixed performance threshold, only timeout and count mismatch. Large batches can be resource-intensive. Random-free deterministic generation may still stress memory/time.

Test signals: prints insertion count and elapsed ms; nonzero if timeout/cancel or policy count mismatch occurs.
