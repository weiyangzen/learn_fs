# sources/distributed-fs/ceph-client/tools/testing/selftests/prctl/config

Purpose: kselftest config fragment requesting anonymous VMA naming support.

Important APIs/types/functions: contains `CONFIG_ANON_VMA_NAME=y`.

Control flow: none.

State and persistence behavior: no runtime state; informs kernel config requirements.

Dependencies and integration points: paired with `set-anon-vma-name-test.c`.

Risks and test signals: without this kernel option, anonymous VMA name prctl behavior may be unavailable.
