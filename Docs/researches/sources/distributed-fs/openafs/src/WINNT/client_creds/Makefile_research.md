# sources/distributed-fs/openafs/src/WINNT/client_creds/Makefile

Purpose: legacy Windows makefile for building `afscreds.exe`, the OpenAFS credentials/tray utility.

Important build inputs: object list includes UI tabs, wizard, drive-map, credential, tray, window, checklist, and support modules. Libraries include Win32 UI/COM/network libraries plus `libafstokens.lib` and `libafsconf.lib` from `$(AFSCLIENTROOT)\obj\afsd`.

Control flow: default `all` links `$(TARGET)` from `$(OBJS)`; pattern rules compile `.cpp` and `.rc` files; `clean` deletes local build artifacts.

State/persistence: no runtime persistence, but build configuration hardcodes `AFSCLIENTROOT = q:\afs\client`, debug flags (`-Zi -Od -DDEBUG -D_DEBUG -DDBG`), C++ exception support (`-GX`), and `STRICT`.

Dependencies/integration: relies on Microsoft `win32.mak`, `MSTOOLS`, resource compiler variables, and OpenAFS client library outputs. Links GUI subsystem flags through `guilflags`.

Risks: hardcoded root and debug-only flags make this unsuitable for modern reproducible builds without adaptation. `wsock32.lib` and older toolchain assumptions indicate pre-Visual Studio project age.

Test signals: clean build with expected `AFSCLIENTROOT`, link resolution for token/config libraries, and resource inclusion in `afscreds.res`.
