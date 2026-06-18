# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/nx_huge_pages_test.sh

Purpose: Provides privileged setup and cleanup for `nx_huge_pages_test`. It configures KVM NX hugepage module parameters, ensures enough 2MB HugeTLB pages, runs the binary with and without `CAP_SYS_BOOT`, and restores host settings afterward.

Important APIs/types/functions: Shell variables capture original `/sys/module/kvm/parameters/nx_huge_pages`, recovery ratio, recovery period, and HugeTLB count. `do_sudo()` abstracts root versus sudo execution; `sudo_echo()` writes sysfs values; `NXECUTABLE` points to the compiled test binary.

Control flow: The script checks sudo/root access, writes test values to KVM parameters and HugeTLB count, optionally grants `cap_sys_boot+ep` to the binary for the permission-positive case, runs the binary with magic token `887563923` and reclaim period 100 ms, removes the capability, then runs the permission-negative case when not root. A cleanup block restores all saved sysfs values and exits with the test result.

State and persistence behavior: Temporarily mutates host KVM module parameters, host HugeTLB pool size, and possibly file capabilities on the test executable. Cleanup restores original sysfs values and removes the added capability in the non-root positive path.

Dependencies and integration points: Depends on root or sudo, writable sysfs KVM parameters, HugeTLB sysfs, Linux file capabilities via `setcap`, and the compiled `nx_huge_pages_test` binary.

Risks and maintenance notes: This script modifies host-wide KVM settings; failure before cleanup could leave changed parameters, though the subshell cleanup path restores after the main run. Systems without sudo or setcap skip relevant cases. The file has a minor comment typo in the SPDX line but shell execution is unaffected.

Test signals: Passing wrapper execution means the C test ran under controlled NX hugepage/reclaim/HugeTLB settings and both permission paths were exercised where possible. Failures can reflect environment setup issues rather than KVM behavior.
