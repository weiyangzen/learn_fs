# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/main.sh

## Purpose

`main.sh` is the cpufreq selftest entrypoint. It parses requested test mode, validates runtime prerequisites, runs the selected cpufreq scenario, captures logs, and emits KTAP output.

## Important APIs, Types, and Functions

It sources `cpu.sh`, `cpufreq.sh`, `governor.sh`, `module.sh`, `special-tests.sh`, and `../kselftest/ktap_helpers.sh`. Important functions are `helpme()`, `prerequisite()`, `parse_arguments()`, `do_test()`, `clear_dumps()`, and `dmesg_dumps()`.

## Control Flow

The script prints KTAP header, parses `-t`, `-o`, `-d`, and `-g`, sets a plan of 1, checks root/sysfs/cpufreq prerequisites, clears output files, pipes the selected test through `tee`, propagates failure from the pipeline, dumps cpufreq-related and full dmesg logs, then emits one passing KTAP test.

## State and Persistence Behavior

It initializes global `SYSFS`, `CPUROOT`, `CPUFREQROOT`, `FUNC`, `OUTFILE`, `DRIVER_MOD`, and `GOVERNOR_MOD`. It writes `${OUTFILE}.txt`, `${OUTFILE}.dmesg_cpufreq.txt`, and `${OUTFILE}.dmesg_full.txt`.

## Dependencies and Integration Points

It depends on root, sysfs, cpufreq sysfs, taskset, KTAP helpers, and all sourced scripts. It integrates with kselftest as the single `TEST_PROGS` executable for the cpufreq suite.

## Risks and Edge Cases

Most modes are intrusive: hotplug, governor shuffling, suspend/hibernate, and module insertion/removal can perturb a running system. If no CPU is cpufreq-managed, non-module modes fail. The script uses Bash pipeline status to preserve test failure after `tee`.

## Test Signals

The primary signal is one KTAP pass/fail for completion, with detailed stdout and dmesg artifacts for diagnosis. Mode dispatch failures produce `ktap_exit_fail_msg`.
