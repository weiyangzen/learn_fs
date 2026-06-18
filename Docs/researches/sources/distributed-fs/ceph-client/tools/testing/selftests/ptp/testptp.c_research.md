# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/testptp.c

Purpose: userspace exerciser for the Linux PTP hardware clock ioctl and POSIX clock interfaces. It supports querying capabilities, setting and adjusting PHC time/frequency, timestamp events, periodic outputs, pin configuration, PPS, system/PHC offset measurements, cross timestamps, and event-channel masks.

Important APIs and functions: uses `linux/ptp_clock.h` ioctls including `PTP_CLOCK_GETCAPS`, `PTP_EXTTS_REQUEST{,2}`, `PTP_PIN_GETFUNC/SETFUNC`, `PTP_PEROUT_REQUEST2`, `PTP_ENABLE_PPS`, `PTP_SYS_OFFSET`, `PTP_SYS_OFFSET_EXTENDED`, `PTP_SYS_OFFSET_PRECISE`, `PTP_MASK_CLEAR_ALL`, and `PTP_MASK_EN_SINGLE`. Helpers include `get_clockid()`, `ppb_to_scaled_ppm()`, `pctns()`, `do_flag_test()`, and `usage()`.

Control flow: parse options, open the PTP device read-write or read-only, derive dynamic clockid from fd, then execute each requested operation sequentially. Many operations print perror on failure but continue to allow multi-operation diagnostics.

State and persistence: can modify PHC time, frequency, phase, pin functions, periodic outputs, PPS, and mask state. Channel mask mode waits for user input before exiting.

Dependencies and integration: depends on PTP char device support, kernel UAPI headers, libc time APIs, and often root or device permissions.

Risks and test signals: this is a manual diagnostic and not strictly pass/fail for every operation. Some options intentionally change clocks and may affect attached hardware. Output text is the primary signal for shell wrappers and users.
