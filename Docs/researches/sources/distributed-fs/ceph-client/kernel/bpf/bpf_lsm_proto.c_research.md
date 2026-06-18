# sources/distributed-fs/ceph-client/kernel/bpf/bpf_lsm_proto.c

## Purpose
`bpf_lsm_proto.c` supplies a strong prototype definition for the `mmap_file` BPF LSM hook. Its purpose is not custom runtime behavior, but precise BTF metadata: the `file__nullable` parameter name marks the `struct file *` argument as nullable for verifier argument checking.

## Important APIs, Types, and Functions
The only function is `int bpf_lsm_mmap_file(struct file *file__nullable, unsigned long reqprot, unsigned long prot, unsigned long flags)`. It returns `0`, matching the default allow result for this hook. The `__nullable` suffix is the important contract because BTF-aware verifier code recognizes the suffix and treats the pointer as `PTR_MAYBE_NULL`.

## Control Flow
The weak `bpf_lsm_mmap_file()` generated in `bpf_lsm.c` would otherwise define the hook. This file provides a strong definition with the same symbol name, overriding the weak one at link time. BPF LSM programs attached to `mmap_file` therefore see a context where the file pointer may be NULL and must check it before dereference.

## State and Persistence Behavior
There is no owned state and no persistence. The function has no side effects and always returns success; the lasting effect is compile-time/link-time BTF metadata used by verifier policy.

## Dependencies and Integration Points
The file includes `<linux/fs.h>` for `struct file` and `<linux/bpf_lsm.h>` for BPF LSM declarations. It integrates with the broader `bpf_lsm.c` hook table because the same symbol appears in BTF ID sets such as `bpf_lsm_hooks` and `sleepable_lsm_hooks`. It also relies on the verifier's suffix-based nullable-argument handling.

## Risks
The main risk is prototype drift from the real LSM hook signature. If `mmap_file` arguments change and this strong definition is not updated exactly, BTF attachment or trampoline setup can become incorrect. Renaming or dropping the `__nullable` suffix would silently weaken verifier null-safety requirements. Returning a different default would change security semantics for unattached/default paths.

## Test Signals
Useful tests attach a BPF LSM program to `mmap_file` and verify that dereferencing `file` without a NULL check is rejected while a checked dereference is accepted. Build and BTF validation should confirm that the strong symbol replaces the weak definition and retains the expected function prototype.
