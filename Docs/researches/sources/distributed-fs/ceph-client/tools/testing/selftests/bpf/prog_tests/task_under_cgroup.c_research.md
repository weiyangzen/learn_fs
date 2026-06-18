# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_under_cgroup.c

Purpose: checks task-under-cgroup detection from LSM and TP_BTF programs. It uses `test_task_under_cgroup` skeleton and cgroup `/foo`.

Control flow joins cgroup `/foo`, opens skeleton, seeds rodata `local_pid`, BSS `remote_pid`, and rodata cgroup id, loads, attaches LSM first, attaches TP_BTF second so LSM observes that attach path, forks a child to trigger task activity, detaches, and verifies `remote_pid` changed from local pid. State is cgroup fd/id, BSS remote pid, rodata local pid/cgid, LSM and trace links, and child process. Dependencies are cgroup helper setup, LSM BPF support, TP_BTF attach support, and fork/wait. Risks include a suspicious assertion pattern around `test__join_cgroup` that treats negative fd as OK, environment cgroup setup, and attach order sensitivity. Test signals are successful skeleton load/attachments, child fork/wait, and final `remote_pid != local_pid`.
