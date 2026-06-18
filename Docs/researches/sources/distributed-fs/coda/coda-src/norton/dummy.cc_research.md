# sources/distributed-fs/coda/coda-src/norton/dummy.cc

Purpose: supplies server-global symbols and aborting stubs needed to link Norton tools against libraries that normally expect a full file-server runtime.

APIs/state: defines `AllowResolution`, `DumpVM`, vnode cache sizing globals, `CodaSrvIp`, and `NullVV`. `PollAndYield`, `Die`, and `GetFsObj` assert if called, except `Die` prints first.

Dependencies and risks: depends on vnode/list types and Coda assertions. This intentionally narrows usable code paths: if linked libraries unexpectedly require server object lookup or polling, Norton aborts instead of pretending success. Tests should ensure normal Norton commands do not hit these stubs.
