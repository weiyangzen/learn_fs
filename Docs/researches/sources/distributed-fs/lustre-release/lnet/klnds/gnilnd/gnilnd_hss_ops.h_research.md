# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_hss_ops.h

## Purpose

`gnilnd_hss_ops.h` defines optional hardware supervisory-system/RCA integration helpers for gnilnd. When `GNILND_USE_RCA` is enabled, it exposes heartbeat and NID/NIC translation wrappers around Cray RCA APIs while preserving type checks against gnilnd/LNet expectations.

## Important APIs, Types, And Functions

Under `GNILND_USE_RCA`:

- Includes `<krca_lib.h>` for RCA types and translation functions.
- Declares external `send_hb_2_l0()` because it is not exported through a normal header.
- `kgnilnd_hw_hb()` sends a hardware heartbeat to L0 via `send_hb_2_l0()`.
- `kgnilnd_nid_to_nicaddrs(rca_nid_t nid, int numnic, nic_addr_t *nicaddrs)` type-checks RCA NID/NIC types against `__u32`, calls `krca_nid_to_nicaddrs()`, logs the translation, and returns the RCA result.
- `kgnilnd_nicaddr_to_nid(nic_addr_t nicaddr, rca_nid_t *nid)` type-checks and calls `krca_nicaddr_to_nid()`.
- `kgnilnd_setup_nic_translation(__u32 device_id)` currently returns 0.

When `GNILND_USE_RCA` is not defined, this header contributes only include guards; fallback implementations must come from other platform headers or conditional build paths.

## Control Flow

The wrappers are simple inline calls. The only branching is compile-time: RCA support either exposes heartbeat/translation functions or omits them. `kgnilnd_nid_to_nicaddrs()` logs every translation at `D_NETTRACE` level.

## State And Persistence Behavior

No local state is stored. RCA translation and heartbeat side effects occur in external HSS/RCA subsystems. The setup hook is currently a no-op, so no translation cache or persistent mapping is initialized here.

## Dependencies And Integration Points

This header depends on Linux `typecheck`, RCA headers/types/functions when enabled, libcfs/Lustre debug macros, and `__u32`. `gnilnd_conn.c` uses `kgnilnd_nid_to_nicaddrs()` before binding active datagram endpoints; `gnilnd_cb.c` uses `kgnilnd_hw_hb()` in long scheduler busy loops to avoid heartbeat failure while the thread is doing continuous work.

## Risks And Edge Cases

- The direct `extern void send_hb_2_l0(void)` binds to a symbol described as not exported in a normal way. Kernel API drift or symbol visibility changes can break builds.
- Type checks ensure compile-time compatibility with `__u32`, but runtime translation can still fail or return zero/negative values; active connection setup treats that as `-ESRCH`.
- Non-RCA builds need alternate definitions for the heartbeat and translation functions. Missing fallback coverage would appear as link or compile failures in platform combinations.
- The setup hook returning success without work can hide platforms that need real NIC translation initialization.

## Test Signals

- Compile both RCA and non-RCA configurations to ensure the expected functions are available through the platform include chain.
- Mock or fail RCA translation to verify active dgram posting handles no NIC address cleanly.
- Scheduler stress tests on RCA-enabled systems should verify repeated `kgnilnd_hw_hb()` calls do not regress heartbeat behavior.
- NID/NIC translation tests should compare RCA results with expected LNet NID address mapping for local and remote Gemini/Cray nodes.
