# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgrp_kfunc.c

## Purpose
Validates cgroup kfunc acquire/release, map retention, ancestor lookup, ID lookup, and namespace behavior. It also runs negative verifier cases from `cgrp_kfunc_failure`.

## Important APIs, types, and functions
Uses `cgrp_kfunc_success.skel.h`, `cgrp_kfunc_failure.skel.h`, cgroup helpers, `unshare(CLONE_NEWCGROUP)`, `fork()`, and `bpf_prog_test_run_opts()`. `open_load_cgrp_kfunc_skel()` sets target PID before load. `run_success_test()` attaches a named program and triggers mkdir/remove of a test cgroup. `test_cgrp_from_id_ns()` forks, joins a cgroup, unshares cgroup namespace, runs a BPF program directly, and communicates result over a pipe.

## Control flow and state
The top-level test sets up a cgroup environment, loops over success program names, then runs a namespace subtest and generated failure tests. State is held in skeleton BSS (`pid`, `err`, `invocations`), cgroup directories, child process state, and pipe FDs. Cleanup removes cgroups and destroys skeletons.

## Dependencies and integration points
Requires cgroup namespace support, cgroup helper environment, generated success/failure BPF objects, and the selftest harness. `env.has_testmod` is not used here; coverage is focused on core cgroup kfuncs.

## Risks and test signals
Fork/namespace setup can fail under restricted privileges. Passing signals are one invocation after cgroup mkdir/rmdir, zero BSS error, successful direct program run inside cgroup namespace, and expected failures from `RUN_TESTS(cgrp_kfunc_failure)`.
