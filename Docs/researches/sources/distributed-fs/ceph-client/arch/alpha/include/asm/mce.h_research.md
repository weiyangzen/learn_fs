# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/mce.h

This header defines common Alpha machine-check logout structures. `struct el_common` is the shared logout header with size, retry/second-error flags, processor/system offsets, code, and revision. EV5 and EV6 structures then describe processor-specific uncorrectable machine-check frames with PAL temps, exception state, cache/ECC/interface status, addresses, syndromes, and control registers.

There is no control flow. State is binary machine-check data supplied by PAL/firmware and consumed by error handlers. Integration is with platform-specific error headers and machine-check decoding/reporting. Risks are structure packing/layout fidelity, differing PAL revisions, and correct interpretation of retry/second-error bits. Tests are compile coverage, synthetic frame decode tests, and hardware error logs where available.
