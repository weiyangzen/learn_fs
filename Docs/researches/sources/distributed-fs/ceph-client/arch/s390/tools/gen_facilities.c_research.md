<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gen_facilities.c -->
# sources/distributed-fs/ceph-client/arch/s390/tools/gen_facilities.c

Purpose: This host tool generates s390 facility-list macros using the Principles of Operation bit numbering scheme for kernel ALS requirements and KVM facility masks.

Important APIs/types/functions: Core data is `struct facility_def` and the `facility_defs[]` table for `FACILITIES_ALS`, `FACILITIES_KVM`, and `FACILITIES_KVM_CPUMODEL`. Helpers are `print_facility_list`, `print_facility_lists`, and `main`.

Control flow: The tool walks each facility bit list until `-1`, maps architectural bit numbers to 64-bit words using most-significant-bit numbering, reallocates the output array when a bit crosses a new doubleword, sets the corresponding bit, and prints `_AC(0x...,UL)` macro initializers inside an include guard. Conditional compilation adds ALS bits according to configured machine-generation features.

State and persistence: Runtime state is a dynamically allocated temporary array per facility definition. Persistent output is the generated `facility-defs.h` header consumed by s390 code.

Dependencies and integration points: It depends on standard C library allocation/stdio/string APIs and kernel build defines passed through `HOSTCFLAGS`. It integrates with s390 CPU feature checks and KVM CPU-model facility masks.

Risks and test signals: Bit-number conversion is the critical contract; reversing bit order or failing to zero newly allocated words would generate invalid masks. Tests include comparing generated macros against known facility bitsets for each `CONFIG_HAVE_MARCH_*` combination, build reproducibility, and KVM guest facility-mask validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gen_facilities.c -->
