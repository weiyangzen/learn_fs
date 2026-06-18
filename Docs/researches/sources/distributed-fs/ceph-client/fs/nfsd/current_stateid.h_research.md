## sources/distributed-fs/ceph-client/fs/nfsd/current_stateid.h

Purpose: declares helpers for NFSv4 current stateid propagation within a compound request. Setters record current stateid from OPEN/OPEN_DOWNGRADE/LOCK/CLOSE results; getters supply it to operations such as DELEGRETURN, FREE_STATEID, SETATTR, CLOSE, LOCKU, READ, and WRITE.

There is no implementation in this header. State lives in `struct nfsd4_compound_state` and operation unions from `xdr4.h`, allowing later operations in the same COMPOUND to use the special current-stateid value. Dependencies include NFSD state management and NFSv4 XDR operation definitions. Risks include using stale current stateid after errors, missing propagation for new operations, and mismatched operation union fields. Test signals: NFSv4 COMPOUND sequences that use current stateid after OPEN/LOCK, invalid current-stateid ordering, READ/WRITE with current stateid, and close/downgrade state transitions.
