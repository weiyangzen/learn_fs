# sources/distributed-fs/ceph-client/include/linux/wireless.h

## Purpose
`wireless.h` includes the legacy Linux Wireless Extensions uapi and adds compat-mode structure definitions for 32-bit userspace on 64-bit kernels. It supports ioctl/event ABI translation.

## Important APIs, Types, and Functions
The header includes `uapi/linux/wireless.h`. Under `CONFIG_COMPAT`, it defines `struct compat_iw_point`, `struct __compat_iw_event`, and compat event-size constants such as `IW_EV_COMPAT_LCP_LEN`, `IW_EV_COMPAT_POINT_OFF`, `IW_EV_COMPAT_CHAR_LEN`, `IW_EV_COMPAT_UINT_LEN`, `IW_EV_COMPAT_FREQ_LEN`, `IW_EV_COMPAT_PARAM_LEN`, `IW_EV_COMPAT_ADDR_LEN`, `IW_EV_COMPAT_QUAL_LEN`, and `IW_EV_COMPAT_POINT_LEN`.

## Control Flow
Wireless extension ioctl/event handlers use these compat layouts to translate pointer-sized fields and event lengths when servicing compat tasks. Non-compat builds expose only the uapi include.

## State and Persistence
No kernel state is declared here. The structures describe transient ioctl and event buffers passed between kernel and userspace.

## Dependencies and Integration Points
Dependencies include uapi wireless extension definitions, `linux/compat.h`, `IFNAMSIZ`, `iw_freq`, `iw_param`, and `iw_quality`. Integration points include legacy wireless drivers, cfg80211 compatibility paths, ioctl dispatch, and event delivery to userspace tools.

## Risks
Compat structure sizes and offsets are ABI-sensitive. Incorrect pointer translation can corrupt userspace buffers or leak kernel data. Wireless Extensions are legacy, so new code should avoid expanding this ABI. Runtime bounds checking motivated the flexible pointer bytes field and must remain valid.

## Test Signals
Signals include 32-bit wireless-tools on 64-bit kernels, ioctl/event size validation, scan/event delivery through compat paths, and builds with and without `CONFIG_COMPAT`.
