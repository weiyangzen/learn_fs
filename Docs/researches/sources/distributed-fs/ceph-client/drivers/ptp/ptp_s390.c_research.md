# sources/distributed-fs/ceph-client/drivers/ptp/ptp_s390.c

Purpose: registers s390 architecture PTP clocks backed by the STCKE/TOD clock and the physical clock queried with PTFF QPT. These clocks are read-only references for s390 environments rather than steerable PHCs.

Important APIs/types/functions: globals `ptp_stcke_clock` and `ptp_qpt_clock` store the two registered PHCs. `ptp_s390_stcke_gettime()` requires `stp_enabled()`, calls `store_tod_clock_ext()`, and converts extended TOD to Unix `timespec64`. `ptp_s390_qpt_gettime()` calls `ptff(..., PTFF_QPT)`. `ptp_s390_getcrosststamp()` wraps `get_device_system_crosststamp()` with `s390_arch_ptp_get_crosststamp()`, which reports `CSID_S390_TOD`. Adjustment and settime callbacks return `-EOPNOTSUPP`.

Control flow: module init registers `"s390 STCKE Clock"` first, then `"s390 Physical Clock"`; if the second registration fails, the first is unregistered. Runtime reads convert TOD values relative to `TOD_UNIX_EPOCH`. Crosstimestamp is available only when STP is enabled.

State and persistence: no adjustable or persistent state. The module only stores registered clock pointers.

Dependencies and integration: depends on s390 STP/TOD architecture APIs, PTP core, and `ptp_private.h` for module-private PTP declarations. Userspace sees two PTP devices when registration succeeds.

Risks and test signals: STCKE read and crosstimestamp return unsupported when STP is disabled, but QPT read does not perform the same check. Conversion correctness depends on TOD epoch constants and nanosecond conversion helpers. Test module load/unload, both PHC names, STP enabled/disabled behavior, `PTP_SYS_OFFSET_PRECISE` for STCKE, and repeated QPT reads.
