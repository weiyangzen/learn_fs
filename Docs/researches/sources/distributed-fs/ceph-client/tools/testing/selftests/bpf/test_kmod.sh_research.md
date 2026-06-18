# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmod.sh

## Research

This shell harness runs BPF selftests that require a special kernel module under `test_kmods/`, then unloads the module afterward. It is primarily a build/load/test orchestration script.

The script enables `set -e` and computes paths relative to the selftests BPF directory. It builds the module by invoking `make` in `test_kmods`, then attempts to load it with `modprobe -q bpf_testmod`. If loading fails, it prints a skip-style message and exits with code `4`. The normal path runs `./test_progs` with `-t module_attach,ksyms_module,kfunc_call,kfunc_call/module,attach_probe` and finally unloads `bpf_testmod`.

State side effects include building kernel module artifacts in the module test directory, loading `bpf_testmod` into the running kernel, creating module sysfs and BTF entries, and running test programs that attach BPF programs to module functions, kfuncs, ksyms, and probes. There is no durable repository state except build outputs.

Dependencies include kernel headers/build tree compatibility, root privileges, `make`, `modprobe`, `rmmod`, the test module source, `test_progs`, and kernel support for BPF module attach/kfunc/module BTF features. Risks include cleanup gaps if `test_progs` fails before `rmmod`, interference from an already loaded module, and environment-specific skips when module loading is disabled. Test signals are the module build/load exit status and the selected `test_progs` subtest results.
