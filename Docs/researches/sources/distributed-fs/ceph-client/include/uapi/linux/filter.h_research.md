# sources/distributed-fs/ceph-client/include/uapi/linux/filter.h

This UAPI header defines classic Linux socket filter structures and macros. It is the userspace ABI for attaching classic BPF programs via `SO_ATTACH_FILTER` and related socket/filter interfaces.

Important exports include `BPF_MAJOR_VERSION`, `BPF_MINOR_VERSION`, `struct sock_filter`, `struct sock_fprog`, `BPF_RVAL`, `BPF_A`, misc op macros `BPF_MISCOP`, `BPF_TAX`, `BPF_TXA`, initializer macros `BPF_STMT` and `BPF_JUMP`, `BPF_MEMWORDS`, ancillary data offsets `SKF_AD_*`, and negative offset spaces `SKF_NET_OFF`/`SKF_LL_OFF`.

Control flow is attach-and-evaluate: userspace provides an array of `sock_filter` instructions; kernel validates/translates them, attaches the filter to a socket or packet path, and runs it on packets to return accept length or reject. State is attached to the socket or filter object; scratch memory is per evaluation. There is no persistence beyond fd/filter lifetime.

Dependencies include `linux/compiler.h`, `linux/types.h`, `linux/bpf_common.h`, socket options, packet capture paths, and cBPF/eBPF translation/JIT infrastructure. Integration points are tcpdump/libpcap, seccomp’s related BPF heritage, socket filters, packet sockets, and network receive paths.

Risks include verifier gaps, incorrect ancillary offset handling, signed/negative offset mistakes, JIT/interpreter divergence, and ABI mismatch with BSD-compatible filter definitions. Test signals include classic BPF selftests, libpcap/tcpdump attach tests, JIT vs interpreter equivalence, malformed program rejection, and ancillary data filter tests.
