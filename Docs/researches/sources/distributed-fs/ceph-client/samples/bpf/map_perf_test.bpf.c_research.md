# sources/distributed-fs/ceph-client/samples/bpf/map_perf_test.bpf.c

Purpose: BPF-side workload for measuring map operation performance across map types.

Important APIs/types/functions: defines multiple maps including hash, percpu hash, lru hash, percpu lru hash, array, lpm trie, hash-of-maps, and lru hash-of-maps; syscall programs attached to getuid/geteuid/getgid and related syscalls stress update/lookup/delete paths.

Control flow: each syscall-attached program loops over keys or entries and performs map operations tailored to one test type. Some programs initialize values, some stress lookups, others exercise LRU or map-in-map behavior.

State and persistence: test maps store counters and synthetic values while the object is loaded. Map-in-map tests reference inner map FDs provided by userspace.

Dependencies and integration: controlled by `map_perf_test_user.c`; requires ksyscall BPF attachment, CO-RE/vmlinux headers, and libbpf skeleton/object loading.

Risks: benchmark results depend on CPU count, kernel map implementation, preallocation, syscall overhead, and verifier loop limits. Test programs deliberately do repeated operations and can add system overhead.

Test signals: userspace benchmark runs each selected test, map FDs are found, syscall triggers execute, and timing output is produced for enabled map types.
