# sources/distributed-fs/ceph-client/arch/s390/kvm/priv.c

## Purpose
Emulates or routes privileged s390 instructions intercepted from a KVM guest. It covers facility lazy-enablement, clock/prefix/control-register handling, storage keys, I/O instruction exits, AP crypto queue instructions, PSW loading, STSI/STFL/STIDP, CMMA ESSA/PFMF, TPROT, and opcode group dispatchers.

## Important APIs, Types, And Functions
External entry points include `is_valid_psw()`, `kvm_s390_handle_aa()`, `kvm_s390_handle_e3()`, `kvm_s390_handle_b2()`, `kvm_s390_handle_b9()`, `kvm_s390_handle_lpsw()`, `kvm_s390_handle_lctl()`, `kvm_s390_handle_stctl()`, `kvm_s390_handle_eb()`, `kvm_s390_handle_e5()`, `kvm_s390_handle_01()`, and `kvm_s390_skey_check_enable()`. Major static handlers include `handle_set_clock()`, `handle_set_prefix()`, `handle_iske()/rrbe()/sske()`, `handle_tpi()/tsch()/io_inst()`, `handle_pqap()`, `handle_lpswe()/lpswey()`, `handle_stsi()`, `handle_pfmf()`, `handle_essa()`, `handle_lctlg()/stctg()`, `handle_tprot()`, and `handle_sckpf()/ptff()`.

## Control Flow And State
Dispatch starts from opcode-group handlers keyed by `ipa` or `ipb` low bits. Each handler validates privilege state, operand alignment, facility availability, and guest memory access. Guest memory faults are converted with `kvm_s390_inject_prog_cond()` when appropriate; some instructions exit to userspace via `-EOPNOTSUPP` or `-EREMOTE` with populated `vcpu->run` payloads. Lazy enablement sets SIE control bits and rewinds the PSW for retry. Storage-key and CMMA paths update gmap/DAT state under MMU locks, top up MMU caches on `-ENOMEM`, and may modify guest registers or condition codes.

## Dependencies And Integration
Depends on gaccess, gmap/DAT helpers, KVM interrupt injection, AP crypto hooks, SCLP/facility bits, lowcore layouts, tracepoints, sysinfo/STSI, and userspace KVM exits for channel I/O and user STSI.

## Risks And Test Signals
Risks are precise architecture semantics: wrong condition codes, PSW advancement, low-address protection, DAT/IPTE locking, facility masking, PV SIDA behavior for STSI, and incorrect userspace exit payloads. Useful signals include s390 KVM selftests, guest boot with channel I/O, storage-key/CMMA tests, AP/VFIO tests, protected guest STSI, tracepoint coverage, and lockdep.
