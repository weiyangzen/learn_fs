# sources/distributed-fs/openafs/src/WINNT/client_creds/ipaddrchg.c

Purpose: monitors IP address changes and prompts for AFS tokens when network connectivity appears and valid tokens are missing or expired.

Important APIs/functions: `ObtainTokensFromUserIfNeeded`, `GetNumOfIpAddrs`, `IpAddrChangeMonitor`, `IpAddrChangeMonitorInit`, plus local service/token/time helpers. Optional `USE_FSPROBE` code sketches fileserver probing but is not active by default.

Control flow: `IpAddrChangeMonitorInit` spawns a monitor thread. The thread blocks on `NotifyAddrChange`, compares valid IP address counts before/after, waits briefly, then calls `ObtainTokensFromUserIfNeeded`. That helper checks the AFS service, asks the UI to start it if needed, resolves root-cell config, checks current token expiry, probes KDC reachability, attempts KFW renewal, and posts `WM_OBTAIN_TOKENS` if user input is still needed.

State/persistence: no persistent writes. Uses process messages (`WM_START_SERVICE`, `WM_OBTAIN_TOKENS`) and current token cache. Allocates root cell with `GlobalAlloc` and transfers ownership to the window message receiver on prompt.

Dependencies/integration: depends on IP Helper API, KFW, OpenAFS token/config APIs, Windows SCM, `creds.cpp`, and `window.cpp` custom messages.

Risks: monitor thread runs indefinitely with no shutdown path. The root-cell pointer is cast through `long`, unsafe on 64-bit. Token probing may attempt fake authentication in non-KFW mode. Comments note missing mutex protection around prompt decisions.

Test signals: address add/remove events, service stopped path, root cell unavailable, KDC unreachable, expired token renewal, message ownership/freeing, and 64-bit pointer correctness.
