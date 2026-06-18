# sources/distributed-fs/ceph-client/arch/x86/kernel/fpu/xstate.c

## Purpose
Implements x86 XSAVE/XRSTOR state discovery, sizing, initialization, UABI conversion, dynamic xstate permissioning, XFD-driven fpstate growth, and coredump/proc reporting for extended FPU state. It is central to boot-time FPU capability selection and runtime management of AVX, AVX-512, PKRU, CET, AMX tile state, APX, and KVM guest supervisor state.

## Important APIs, Types, And State
Key exported or integration APIs include `cpu_has_xfeatures()`, `fpu__init_cpu_xstate()`, `fpu__init_system_xstate()`, `fpu__resume_cpu()`, `get_xsave_addr()`, `get_xsave_addr_user()`, `copy_xstate_to_uabi_buf()`, `copy_uabi_from_kernel_to_xstate()`, `copy_sigframe_from_user_to_xstate()`, `xsaves()`, `xrstors()`, `fpstate_clear_xstate_component()`, `__xfd_enable_feature()`, `xfd_enable_feature()`, `xstate_get_guest_group_perm()`, `fpu_xstate_prctl()`, and optional `proc_pid_arch_status()` / ELF coredump note writers. Persistent global tables cache `xstate_offsets[]`, `xstate_sizes[]`, `xstate_flags[]`, and `xfeature_uncompact_order[]` after CPUID enumeration. It mutates global FPU configs (`fpu_kernel_cfg`, `fpu_user_cfg`, `guest_default_cfg`) and per-task/group permission and fpstate buffers.

## Control Flow
Boot flow starts in `fpu__init_system_xstate()`: it enumerates CPUID xstate leaves, filters features against normal CPU feature bits and XSAVES/XFD support, computes default host/user/guest masks, enables OSXSAVE via `fpu__init_cpu_xstate()`, caches component layout, validates hardware-reported sizes against C structs, updates ptrace regset sizing, initializes `init_fpstate`, and sets `X86_FEATURE_OSXSAVE`. Per-CPU resume restores XCR0, IA32_XSS, and XFD. UABI output builds uncompacted user buffers from compacted kernel state, filling init or zero state when components are absent; UABI input validates headers, MXCSR reserved bits, user feature masks, copies components back, and preserves supervisor bits. Dynamic permission flow uses `arch_prctl()` through `fpu_xstate_prctl()`, validates signal altstack capacity, updates per-process permission masks, then XFD faults call `__xfd_enable_feature()` to allocate a larger `fpstate`.

## Dependencies And Integration Points
Depends on CPUID leaves `CPUID_LEAF_XSTATE` and tile leaves, CR4 OSXSAVE, XCR0, IA32_XSS, IA32_XFD, x86 signal/ptrace regsets, KVM guest FPU state, pkeys/PKRU, coredump note emission, `/proc/<pid>/arch_status`, and static keys for dynamic state sizing. KVM relies on `get_xsave_addr()`, `fpstate_clear_xstate_component()`, and guest permission export.

## Risks And Test Signals
High-risk areas are ABI layout stability, compacted vs uncompacted offset calculation, stale PKRU handling, XFD/fpstate races, supervisor state masking, and AMX/APX struct-size checks. Test signals include boot logs for enabled xfeatures and context size, ptrace/signal XSAVE round trips, AMX permission and altstack failure cases, XFD fault enablement, KVM guest xstate tests, coredump `NT_X86_XSAVE_LAYOUT`, suspend/resume FPU state restoration, and warnings from `XSTATE_WARN_ON()` or xsave fault paths.
