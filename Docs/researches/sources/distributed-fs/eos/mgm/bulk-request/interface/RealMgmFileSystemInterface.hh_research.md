## sources/distributed-fs/eos/mgm/bulk-request/interface/RealMgmFileSystemInterface.hh

Purpose: declares the production implementation of `IMgmFileSystemInterface` backed by `XrdMgmOfs`.

Important APIs: implements every interface method and stores `XrdMgmOfs* mMgmOfs`. The destructor is trivial and does not own the MGM object.

Integration: constructed where MGM prepare/query operations need the real filesystem facade. Risks are raw pointer lifetime and tight compile dependency on `mgm/ofs/XrdMgmOfs.hh`. Test signals should validate forwarding only where wrapper behavior is non-trivial, such as host fallback and report-record guard.
