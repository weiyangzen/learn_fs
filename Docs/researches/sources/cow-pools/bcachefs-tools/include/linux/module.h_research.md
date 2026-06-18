# File Research: sources/cow-pools/bcachefs-tools/include/linux/module.h

This header stubs Linux module infrastructure for user space. `module_init(initfn)` creates a constructor that calls the init function and BUGs on failure. `module_exit(exitfn)` creates an unused wrapper rather than a destructor.

Module metadata macros are no-ops. Module reference functions are empty or always succeed. It also defines kernel parameter structures and bool parameter setting through `kstrtobool()`.
