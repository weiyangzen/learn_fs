# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/scan.h

Purpose: Scan state and scan-related API declarations for CW1200.

Important APIs and types: Defines `struct cw1200_scan` with semaphore, work items, cfg80211 request pointer, channel iterator pointers, WSM SSIDs, output power, status, in-progress atomic, direct-probe work, and direct-probe flag. Declares scan entry points and WSM callbacks.

Control flow: Main initialization sets up the work items and semaphore. Mac80211 calls `cw1200_hw_scan`; WSM callbacks call completion/failure functions; TX workaround code schedules `cw1200_probe_work`.

State and persistence: Scan state is per-device and reset across scan operations, not persisted.

Dependencies and integration: Includes `wsm.h` and Linux semaphore support; referenced from `cw1200_common`, `main.c`, `scan.c`, PM, and STA code.

Risks: The structure stores pointers into mac80211 scan requests, so lifetime is tied to scan completion. `scan.lock` is a semaphore rather than a mutex because some flows use trylock and cross-work ownership.

Test signals: Build all callers, then validate scan request lifetime, timeout cleanup, and direct probe interactions.
