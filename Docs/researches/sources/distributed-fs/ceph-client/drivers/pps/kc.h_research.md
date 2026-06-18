# sources/distributed-fs/ceph-client/drivers/pps/kc.h

Purpose: private header that abstracts PPS kernel consumer support behind `CONFIG_NTP_PPS`.

Important APIs: declarations for `pps_kc_bind()`, `pps_kc_remove()`, and `pps_kc_event()` when enabled; inline stubs returning `-EOPNOTSUPP` or doing nothing otherwise.

Control flow/state: compile-time selection only. PPS core can call these helpers unconditionally, while builds without kernel PPS consumer support keep the char-device API available but reject kernel-consumer binding.

Dependencies/integration: includes `linux/pps_kernel.h` and `linux/errno.h`; included by `kapi.c`, `kc.c`, and `pps.c`.

Risks/test signals: verify non-`CONFIG_NTP_PPS` builds compile and `PPS_KC_BIND` returns `-EOPNOTSUPP`; enabled builds link to `kc.o`; source removal calls are harmless in both modes.
