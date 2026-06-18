# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_read_macros.c

## Purpose
Tests BPF CORE/probe read macros for kernel and user memory, including a flavored/shuffled user struct.

## Important APIs, types, and functions
Uses `test_core_read_macros.skel.h`, local `callback_head` and `callback_head___shuffled`, skeleton BSS pointers/embedded structs, and tracepoint attach. The test seeds kernel-side BSS structs and user-space local structures, then checks output fields.

## Control flow and state
The skeleton is opened/loaded, BSS `my_pid` and input pointers/fields are initialized, the skeleton attaches, a tracepoint is triggered by sleep, and BSS outputs are compared to constants. User pointers reference stack locals during the attached interval only.

## Dependencies and integration points
Depends on generated BPF programs, user memory read support, kernel memory read helpers, and CO-RE field flavor matching. Integrated as `test_core_read_macros()`.

## Risks and test signals
Stack lifetime and pointer validity are important. Passing signals are exact output constants for kernel probe/core and user probe/core read paths.
