# sources/distributed-fs/ceph-client/drivers/media/tuners/fc0013-priv.h

Purpose: private header for FC0013 logging macros and private state. It defines `err`, `info`, and `warn` printk wrappers with `fc0013` prefix and `struct fc0013_priv` containing I2C adapter, address, dual-master flag, crystal frequency, and cached frequency/bandwidth.

No control flow is present beyond macro expansion. The implementation uses this state for raw I2C transfers, PLL math, VHF/UHF/GPS path selection, and DVB getter ops.

Dependencies are kernel printk levels and public FC0013/FC001x types included by the C file. Risks: macros redefine common names (`err`, `info`, `warn`) after `#undef`, so include ordering matters; `xtal_freq` is stored as `u8` rather than enum; cached frequency/bandwidth are only updated on successful tuning. Test signals: compile with warning macro users, attach/release memory checks, and getter-before-tune behavior.
