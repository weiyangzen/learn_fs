## sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uac_common.h

Purpose: provides the shared UAC constant used by UAC1, UAC2, and `u_audio` configuration structures.

Important APIs and types:
- `UAC_MAX_RATES` is defined as 10, the maximum number of configurable sample rates in the fixed arrays used by UAC1/UAC2/audio options.

Control flow and integration:
- Headers `u_audio.h`, `u_uac1.h`, and `u_uac2.h` include this file to size capture/playback sample-rate arrays.
- Parser/store code in UAC function implementations must enforce this bound and zero-terminate arrays.

State and persistence:
- No runtime state. It is a compile-time contract.

Dependencies:
- None beyond include guards.

Risks:
- Increasing the constant changes struct layout and configfs ABI expectations inside the kernel build.
- Missing zero terminators in arrays of this size can cause readers to scan stale values until they hit an incidental zero.

Test signals:
- Configfs tests should write exactly 1, `UAC_MAX_RATES`, and too many rates, verifying validation and descriptor generation.
