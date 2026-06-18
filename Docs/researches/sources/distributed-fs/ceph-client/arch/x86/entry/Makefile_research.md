<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/entry/Makefile

Purpose: This Makefile controls the build of x86 low-level entry code, syscall support, vDSO/vsyscall subdirectories, preemption thunks, FRED entry code, and IA32 compatibility entry code.

Important APIs/types/functions: It disables KASAN, UBSAN, and KCOV instrumentation for the directory. It removes ftrace flags from syscall objects, adds `-fno-stack-protector` to syscall C objects and FRED C entry code, builds `entry.o`, `entry_$(BITS).o`, and `syscall_$(BITS).o`, and conditionally adds `thunk.o`, `entry_64_fred.o`, `entry_fred.o`, `entry_64_compat.o`, and `syscall_32.o`.

Control flow: Kbuild evaluates architecture bitness and config symbols. The resulting object list determines whether 32-bit or 64-bit entry assembly is built, whether FRED support is present, and whether IA32 emulation adds compatibility paths.

State and persistence: It has no runtime state. It persists build policy that keeps entry code free of instrumentation that would be unsafe in noinstr/entry contexts.

Dependencies and integration points: It integrates with top-level x86 Kbuild, vDSO and vsyscall subdirectories, syscall C files, preemption thunk code, FRED config, and IA32 emulation.

Risks and test signals: Incorrect instrumentation flags can introduce calls or stack protector references into early entry paths where they are unsafe. Tests should include x86 32-bit and 64-bit builds, FRED-enabled builds, IA32 emulation builds, objtool/noinstr validation, and checking that syscall objects remain free of ftrace and stack protector instrumentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/Makefile -->
