# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgs8gxx_priv.h

## Purpose
`lgs8gxx_priv.h` defines private runtime state and bit masks used by the LGS8Gxx family driver.

## Important APIs, Types, and Functions
`struct lgs8gxx_state` contains the I2C adapter, config pointer, DVB frontend, and current guard interval. Macros define detected transmission-parameter fields: sub-carrier modulation (`SC_*`), FEC rate (`LGS_FEC_*`), time interleave (`TIM_*`), control frame (`CF_*`), guard interval (`GI_*`), and TS output flags (`TS_*`).

## Control Flow
The C file uses these masks when interpreting auto-detected parameters, applying the LGS8913 time-interleaver fix, setting guard interval trials, and configuring MPEG/TS output registers.

## State and Persistence
`curr_gi` is software state used mainly by LGS8913 signal-strength scanning. All other macros describe volatile register bitfields.

## Dependencies and Integration Points
It is private to `lgs8gxx.c` and relies on public `struct lgs8gxx_config` from `lgs8gxx.h`.

## Risks and Edge Cases
The guard-interval constants are register encodings, not human-readable interval values; the C file translates them to 420/595/945 for `curr_gi`. Misusing these constants outside their register context would create wrong scan lengths or TS settings.

## Test Signals
Auto-detect should report and apply each guard interval, LGS8913 detected-parameter correction should preserve expected CF/SC/FEC fields, and TS mode bits should produce the configured serial/parallel clock behavior.
