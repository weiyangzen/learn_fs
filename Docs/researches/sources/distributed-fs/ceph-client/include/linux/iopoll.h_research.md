# sources/distributed-fs/ceph-client/include/linux/iopoll.h

Purpose: This header provides generic polling macros for repeatedly executing an operation or reading an MMIO value until a condition becomes true or a timeout expires.

Important APIs, types, and functions: Generic macros are `poll_timeout_us` and `poll_timeout_us_atomic`. Read wrappers include `read_poll_timeout`, `read_poll_timeout_atomic`, `readx_poll_timeout`, `readx_poll_timeout_atomic`, and typed MMIO helpers for `readb/readw/readl/readq` and relaxed variants.

Control flow: Non-atomic polling computes an absolute `ktime` deadline, optionally sleeps before the first operation, executes `op`, checks `cond`, checks timeout, sleeps between iterations, and calls `cpu_relax`. Atomic polling uses `udelay` and an approximate remaining-nanoseconds counter rather than timekeeping, making it usable while timekeeping is suspended.

State and persistence: No state persists beyond local macro temporaries. The last read value is stored in the caller-supplied variable even on timeout.

Dependencies and integration points: Depends on kernel time, delay, errno, CPU relax, and MMIO accessors from `io.h`. Used broadly by device drivers waiting for hardware bits.

Risks: Macros evaluate operation and condition in caller context, so side effects must be deliberate. Sleeping variants must not be used in atomic context when delay or timeout can sleep. A zero timeout means never timeout. Atomic timeout underestimates wall-clock time.

Test signals: Test immediate success, timeout, sleep-before-read, zero-timeout loops with external completion, atomic and non-atomic contexts, relaxed accessors, readq availability, and preservation of the last read value on timeout.
