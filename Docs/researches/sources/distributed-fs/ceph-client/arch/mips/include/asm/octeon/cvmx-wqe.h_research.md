# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-wqe.h

Purpose: defines the OCTEON work queue entry (WQE) format used by POW, PIP, packet receive, and software-submitted work paths.

Important APIs/types/functions: `OCT_TAG_TYPE_STRING` maps tag types to names. The large decode union at the top captures hardware receive classification and error bits for IP and non-IP packets, including VLAN, port/PKND, checksum/error flags, broadcast/multicast, fragmentation, and buffer count. Other key types are `union cvmx_pip_wqe_word0`, `union cvmx_wqe_word0`, `union cvmx_wqe_word1`, and `struct cvmx_wqe`. Accessors `cvmx_wqe_get_port`, `cvmx_wqe_set_port`, `cvmx_wqe_get_grp`, `cvmx_wqe_set_grp`, `cvmx_wqe_get_qos`, and `cvmx_wqe_set_qos` hide layout differences.

Control flow: packet hardware fills WQE fields, POW schedules the entry, and software reads/updates metadata through direct fields and accessors. Accessors branch on `octeon_has_feature(OCTEON_FEATURE_CN68XX_WQE)` where CN68XX-style WQE layouts differ for port/group/qos placement.

State and persistence: WQE instances are in memory and represent live packet/work metadata. They are not durable, but correctness is critical while POW owns or schedules the entry. Some fields are hardware-written and should not be casually overwritten.

Dependencies and integration points: includes `cvmx-packet.h`; relies on tag-type values from `cvmx-pow.h` and feature detection from `octeon-feature.h`/model headers. `cvmx-pow.h` uses `struct cvmx_wqe` for work requests and submissions. Network receive/transmit and packet classification code consume decode/error fields.

Risks: bitfield layouts are endian- and model-dependent. CN68XX WQE differences require accessors; direct field access can break on those chips. Hardware and software share ownership of fields at different times, so missing `CVMX_SYNCWS` before POW submission can expose stale data. The decode union contains many error conditions that callers must interpret correctly to avoid accepting malformed packets.

Test signals: packet receive tests should verify WQE port/group/qos accessors on CN68XX and non-CN68XX models, VLAN/error decode, buffer count handling, and POW submit/request round trips. Compile coverage should include both endian bitfield modes.
