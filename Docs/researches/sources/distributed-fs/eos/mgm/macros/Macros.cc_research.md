# sources/distributed-fs/eos/mgm/macros/Macros.cc

Purpose: provides function equivalents for selected MGM OFS macros: namespace path mapping and proc-request access checks. These functions make macro behavior reusable from non-OFS command paths such as HTTP/WebDAV and proc command implementations.

Important APIs and functions: `NamespaceMap(std::string& path, const char* ininfo, const VirtualIdentity& vid)` unescapes or curl-decodes a path, honors token path replacement for `/zteos64:`, applies `gOFS->PathRemap` unless `eos.prefix` is present, rejects CR/LF for non-root users by clearing the path, and applies `eos.prefix=` or `eos.lfn=` opaque overrides outside `/proc/`. `ProcBounceIllegalNames` converts an empty mapped path into `EILSEQ` and an operator-facing error string. `ProcBounceNotAllowed` checks `Access` allow lists under `Access::gAccessMutex` and rejects unauthorized user/group/host/domain identities with `EACCES`.

Control flow: proc and WebDAV callers first map the path, then call bounce helpers. The access helper allows uid 0-3 unless other conditions require checking, then verifies allowed users, groups, hosts, and user-at-domain. A separate domain check rejects when allowed domains are configured, `-` is not present, and the caller domain is not listed.

State and persistence behavior: no local persistent state. Behavior depends on global `gOFS`, path remap configuration, token contents, and static access allow-list sets. It mutates only the input path and output error/errno fields.

Dependencies and integration points: depends on `mgm/macros/Macros.hh`, `mgm/access/Access.hh`, `XrdOucEnv`, `VirtualIdentity`, `StringConversion`, and global `XrdMgmOfs`. Callers include `mgm/http/webdav/PropFindResponse.cc`, `mgm/proc/IProcCommand.cc`, and `mgm/proc/user/RmCmd.cc`.

Risks and test signals: `NamespaceMap` assumes `gOFS` is valid for `PathRemap`; unlike the macro, the function body does not guard every use. CR/LF rejection is represented as an empty path, so an originally empty path and an illegal path are indistinguishable to `ProcBounceIllegalNames`. Opaque parsing trusts `XrdOucEnv` values and should be tested for unusual `eos.prefix` and `eos.lfn` combinations. There is no direct unit-test hit in the observed sweep; tests should cover token remap, encoded paths, prefix/lfn precedence, `/proc/` exclusion, CR/LF rejection for root versus non-root, and allow-list combinations.
