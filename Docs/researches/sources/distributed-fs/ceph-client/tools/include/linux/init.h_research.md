<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/init.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/init.h

## Purpose
`init.h` provides a minimal user-space replacement for kernel init/exit annotations and boot-parameter registration structures.

## APIs And Flow
It defines no-op `__init`, `__exit`, `__initconst`, `__meminit`, `__meminitdata`, `__refdata`, and `__initdata`, plus `__section()`, `struct obs_kernel_param`, `__setup_param()`, `__setup()`, and `early_param()`. Setup macros emit static strings and `obs_kernel_param` records into `.init.setup`; there is no runtime parser in this header.

## State, Dependencies, Risks, Tests
State is generated object-file sections rather than heap or global runtime state. It depends on `linux/compiler.h` for `__used`, `__aligned`, and related attributes. Risks are linker-section mismatch with tools that expect kernel boot-param layouts and the fact that most kernel section lifetime semantics are intentionally erased. Tests should compile users with normal and early params and inspect object sections or linker maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/init.h -->
