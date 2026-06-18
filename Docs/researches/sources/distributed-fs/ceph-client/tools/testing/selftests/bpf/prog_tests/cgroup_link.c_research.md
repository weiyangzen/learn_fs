# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/cgroup_link.c

## Purpose
This serial test validates link-based cgroup program attachment, effective program queries, link update, mixing with legacy attaches, and detach behavior in nested cgroup hierarchies.

## APIs, Types, and Functions
It uses `test_cgroup_link.skel.h`, `bpf_program__attach_cgroup`, `bpf_link__destroy`, `bpf_link_update`, `bpf_link_get_info_by_fd`, `bpf_prog_query`, `bpf_prog_attach`, `bpf_prog_detach2`, and cgroup helpers. `ping_and_check` resets skeleton counters, runs `ping`, and checks primary/alternate program invocation counts.

## Control Flow
The test creates four nested cgroups, joins the deepest, attaches one link at each level, and verifies traffic sees all effective programs. It queries local and effective attach state, destroys the bottom link, mixes in a legacy multi attach, reattaches a link, exercises link update to an alternate program, validates link info, and cleans up both link and legacy attachments.

## State, Dependencies, and Integration
State includes nested cgroup FDs, BPF links, optional legacy attachment, skeleton BSS counters, and loopback traffic. Cleanup destroys live links, detaches legacy program when used, closes cgroups, and resets cgroup environment.

## Risks and Test Signals
Signals are invocation counters, query counts/IDs, link info fields, and update results. Risks include ping availability, effective cgroup ordering changes, and interactions between link-based and legacy attach APIs.
