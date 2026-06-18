# sources/distributed-fs/openafs/src/WINNT/tests/torture/include/ResolveLocker.h

Purpose: public header for a locker attach/detach helper library used by the Windows torture environment.

Important APIs and types: `USER_OPTIONS` captures attach/detach settings, including Hesiod output, mount type, UNC behavior, host/user/password, disk drive, locker/submount names, path update flags, force dismount, and output controls. It declares `attach(USER_OPTIONS, int addtoPath, int addtoFront, char *appName)` and `detach(USER_OPTIONS, int DeleteFromPath, char *appName)`.

Control flow: none in this header; callers populate `USER_OPTIONS` and invoke the library.

State and persistence: state is passed by value in `USER_OPTIONS`. The implementation is expected to alter drive mappings, submounts, and optionally PATH entries.

Dependencies and integration: integrates with the MIT-style locker model referenced by `nb_Attach`, `nb_Detach`, and `nb_SetLocker`.

Risks and test signals: fixed-size credential/path buffers require bounded copying by the implementation. Test signals should include correct attach/detach behavior, expected drive/UNC mappings, and path update side effects.
