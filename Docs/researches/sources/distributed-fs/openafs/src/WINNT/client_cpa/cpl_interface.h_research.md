# sources/distributed-fs/openafs/src/WINNT/client_cpa/cpl_interface.h

Purpose: declares the single exported Control Panel entry point `CPlApplet` with C linkage for the OpenAFS client applet.

Important APIs/types: wraps `LONG APIENTRY CPlApplet(HWND hwndCPl, UINT uMsg, LONG lParam1, LONG lParam2)` in `extern "C"` when compiled as C++ so the symbol name matches the Control Panel loader contract.

Control flow: no runtime flow is implemented here; it provides the ABI boundary consumed by `cpl_interface.cpp` and Windows `control.exe`.

State/persistence: none.

Dependencies/integration: assumes Windows header types and calling conventions are visible before or through the includer. It is the integration contract between the CPL module and the shell/control panel host.

Risks: because this header contains no include guard, repeated inclusion would redeclare the same prototype but not generally break C/C++ compilation. ABI correctness depends on retaining `APIENTRY` and C linkage.

Test signals: build/link checks should confirm the exported name is available to the `.cpl`; runtime smoke tests should load the applet from Control Panel.
