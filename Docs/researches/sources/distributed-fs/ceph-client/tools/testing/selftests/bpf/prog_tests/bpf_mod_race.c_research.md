# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/bpf_mod_race.c

## Purpose
This serial selftest constructs a verifier/module lifetime race around `btf_try_get_module()` while `bpf_testmod` is still in `MODULE_STATE_COMING`. It verifies that BPF programs referring to module ksyms or kfuncs fail to load with `ENXIO` instead of taking references to an uninitialized module that could later be freed.

## Important APIs, Types, And Functions
Key pieces are `struct test_config`, `enum bpf_test_state`, atomic global `state`, `load_module_thread()`, `sys_userfaultfd()`, `test_setup_uffd()`, `test_bpf_mod_race_config()`, `ksym_config`, `kfunc_config`, and `serial_test_bpf_mod_race()`. It uses `mmap()`, `userfaultfd`, `UFFDIO_API`, `UFFDIO_REGISTER`, pthreads, `load_bpf_testmod()`, `unload_bpf_testmod()`, `kern_sync_rcu()`, and skeletons `bpf_mod_race`, `ksym_race`, and `kfunc_call_race`.

## Control Flow
For each config, the test maps a faulting page, unloads `bpf_testmod`, loads and attaches an fmod_ret BPF program configured to fault on that page during module init, registers the address with userfaultfd, and starts a module-loading thread. Once the BPF program is known to be blocked in the page fault and the module is still initializing, the test attempts to load either a ksym-using or kfunc-using program. Correct behavior is load failure with `ENXIO`; then closing userfaultfd unblocks module loading so the injected error frees the module path safely.

## State And Persistence Behavior
State spans an atomic test-state enum, skeleton BSS/data fields, a userfaultfd registration, a thread running module load, and the loaded/unloaded `bpf_testmod` kernel module. Cleanup restores `bpf_testmod`, destroys skeletons, waits for RCU, unmaps memory, and resets the atomic state.

## Dependencies And Integration Points
It requires `bpf_testmod`, userfaultfd support, module loading permissions, pthreads, fmod_ret program attachment, BTF/kfunc/ksym verifier paths, and the selftest helper library. It directly integrates with kernel module lifecycle and verifier module-reference handling.

## Risks And Edge Cases
This is timing- and privilege-sensitive. Failure to observe the block, userfaultfd restrictions, blocked module thread cleanup, or exact verifier errno changes can affect results. The test intentionally handles the dangerous success case by closing userfaultfd, waiting for the injected failure path, syncing RCU, and destroying the unexpectedly loaded skeleton.

## Test Signals
Passing signals are module load blocking before init completes, a userfaultfd page-fault event, failed ksym/kfunc program load with `errno == ENXIO`, `res_try_get_module == false`, module-load thread ending in `TS_MODULE_LOAD_FAIL`, successful RCU sync, and successful restoration of `bpf_testmod`.
