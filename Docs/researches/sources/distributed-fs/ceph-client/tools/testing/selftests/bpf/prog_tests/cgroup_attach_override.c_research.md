# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_attach_override.c

## Purpose
This serial test validates `BPF_F_ALLOW_OVERRIDE` behavior for cgroup skb programs. It checks that child cgroup programs can override parent decisions and that effective program execution changes as programs are attached/detached through a hierarchy.

## APIs, Types, and Functions
It hand-loads small cgroup skb programs with `prog_load(int verdict)`, using raw BPF instructions that return allow or deny. The test uses cgroup helpers, `bpf_prog_attach`, `bpf_prog_detach2`, `bpf_prog_query`, and loopback `ping` as traffic.

## Control Flow
The test sets up a nested cgroup hierarchy, attaches allow and deny programs with override flags at different levels, joins the deepest cgroup, runs pings, and observes whether traffic succeeds according to the closest overriding program. It also queries effective program counts/IDs and detaches programs to validate fallback to parent behavior.

## State, Dependencies, and Integration
State is cgroup hierarchy and loaded program FDs. It integrates with legacy cgroup attach APIs rather than skeletons. Cleanup closes all FDs and resets the cgroup environment.

## Risks and Test Signals
The main signal is ping success/failure plus effective query results. Risks include timing/availability of `ping`, cgroup hierarchy setup, and kernel changes to override semantics or query ordering.
