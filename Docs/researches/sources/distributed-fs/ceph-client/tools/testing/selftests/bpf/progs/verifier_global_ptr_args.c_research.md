# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_global_ptr_args.c

## Purpose

`verifier_global_ptr_args.c` tests verifier checking of global subprogram pointer argument tags and flavors. It focuses on trusted, nullable, refcounted, untrusted, user-memory, and read-only cast pointer semantics when global functions are called from BPF programs.

## Important APIs, Types, and Functions

The file includes BTF, tracing, CO-RE, `xdp_metadata.h`, and kfunc declarations. It uses task helpers and kfuncs such as `bpf_get_current_task_btf`, `bpf_task_acquire`, `bpf_task_release`, `bpf_core_cast`, `bpf_rdonly_cast`, and `bpf_copy_from_user_task`. Programs attach to tp_btf, kprobe, uprobe, and task_newtask sections. Global subprograms encode contracts such as trusted nullable task, trusted non-null task, pointer flavor, acquire/release, untrusted, and memory-tagged arguments.

## Control Flow

Top-level programs obtain task pointers or external context pointers, then call global subprograms with either correct or intentionally wrong annotations. Success cases pass nullable pointers only to nullable prototypes, non-null trusted pointers after proper checks or acquisition, and untrusted pointers to untrusted-only prototypes. Failure cases pass scalar or nullable pointers where non-null trusted pointers are required, release non-refcounted pointers, combine invalid argument tags, or pass incompatible pointer types.

## State and Persistence Behavior

No persistent maps are declared. Runtime state centers on pointer provenance, nullability, trustedness, flavor, and reference ownership. Refcounted task pointers acquired by kfuncs must be released, while borrowed current-task pointers must not be treated as releasable references.

## Dependencies and Integration Points

The file integrates with global subprogram verification, BTF type-tag parsing, task kfuncs, CO-RE casts, and helper argument checking. It is a regression suite for verifier call-boundary type checking, not for runtime data processing.

## Risks and Test Signals

Risks include allowing untrusted pointers into trusted prototypes, losing nullable information at global-call boundaries, or mishandling refcount ownership. Test signals are expected verifier messages about validating specific subprograms, caller invalid arguments, trusted pointer register types, release requirements, and incompatible tag combinations.
