<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/nmi.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/nmi.h

## Purpose
`nmi.h` is an empty file in this tools include tree.

## APIs And Flow
It exports no include guard, macros, types, or functions. There is no control flow.

## State, Dependencies, Risks, Tests
There is no state or dependency. Its role is effectively as a path placeholder for source imports that include NMI support conditionally elsewhere. Risks are that direct inclusion may not be protected against repeated reads and any future use of NMI watchdog or backtrace APIs will fail to compile. Test signal is compile coverage of current consumers and a check that no symbol from this header is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/nmi.h -->
