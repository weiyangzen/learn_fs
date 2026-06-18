# sources/distributed-fs/coda/coda-src/norton/Makefile.am

Purpose: automake recipe for the Norton server recovery tools. Under `BUILD_SERVER`, it builds `libnorton.la`, the interactive `norton` binary, the `norton-reinit` dump/load tool, and installs the `reinit` script/manpage.

Integration: `libnorton` contains setup, command, volume, vnode, directory, RVM heap, and recoverable-storage helpers. `norton` adds `norton.cc`, `norton.h`, and server dummy stubs; `norton-reinit` links reinit logic and the same stubs. Link dependencies span resolution, volume, volutil, version vectors, partition, ACL, directory, util, rwcdb, base, RVM/RPC2, readline, and termcap.

Risks/test signals: a visible missing line-continuation before one include path can affect generated Makefiles depending on automake parsing. Build coverage is the main signal; runtime tests require real Coda RVM state.
