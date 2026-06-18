# sources/distributed-fs/ceph-client/drivers/net/dsa/microchip/ksz_ptp.h

## Purpose
`ksz_ptp.h` declares the optional PTP and hardware timestamping interface for the KSZ DSA driver. It provides the real data structure and function prototypes when `CONFIG_NET_DSA_MICROCHIP_KSZ_PTP` is enabled, and no-op or NULL stubs when it is disabled.

## Important APIs, Types, and Functions
With PTP enabled, the header defines `KSZ_PTP_N_GPIO`, `enum ksz_ptp_tou_mode`, and `struct ksz_ptp_data` containing `ptp_clock_info`, the registered `ptp_clock`, two pin descriptors, locks, cached clock time, TOU mode, and periodic-output state. It declares PHC registration, timestamp info, hwtstamp get/set, TX/RX timestamp hooks, deferred transmit, and IRQ setup/free functions.

## Control Flow
The header controls compile-time integration. `ksz_common.c` can unconditionally name the PTP callbacks in `ksz_switch_ops`; when PTP support is disabled, callbacks that DSA should omit are defined as `NULL`, while setup/free routines compile to success/no-op stubs.

## State and Persistence
When enabled, PTP state is embedded in `struct ksz_device` through this header. When disabled, only a mutex-containing placeholder `struct ksz_ptp_data` remains so common structures still compile. No persistence is provided here.

## Dependencies and Integration Points
The enabled path depends on `linux/ptp_clock_kernel.h`, DSA switch objects, hwtstamp config types, skb types, and kthread work. It is included by `ksz_common.h` so the common device structure can embed PTP data.

## Risks and Edge Cases
The disabled build path replaces function identifiers with `NULL` macros for DSA callbacks, so callers outside DSA setup must avoid invoking those macros as functions. Structure layout differs substantially between enabled and disabled configurations, which makes conditional compilation boundaries important.

## Test Signals
Build both PTP-enabled and PTP-disabled kernels. In the disabled build, probe should not attempt PHC registration and DSA timestamp callbacks should be absent. In the enabled build, all prototypes should resolve to `ksz_ptp.c` and the runtime tests from that implementation should pass.
