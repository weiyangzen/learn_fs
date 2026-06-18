# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/abd_impl_os.h

Small libzpool ABD implementation header. It defines no-op critical-section macros for userland ABD operations:
- `abd_enter_critical(flags)`
- `abd_exit_critical(flags)`

The userland implementation does not need kernel-style preemption or pagefault critical sections here.
