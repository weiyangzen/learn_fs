<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundcard.h -->
# sources/distributed-fs/ceph-client/include/linux/soundcard.h

Purpose: This compatibility header wraps the OSS soundcard UAPI and defines native-endian sample format aliases for kernel users.

Important APIs/types/functions: It includes architecture byte order and `uapi/linux/soundcard.h`, then maps `AFMT_S16_NE` to `AFMT_S16_BE` or `AFMT_S16_LE` depending on byte order.

Control flow: No executable control flow; preprocessor selection fails the build if neither big-endian nor little-endian is known.

State and persistence: No state.

Dependencies/integration: Used by OSS-compatible audio drivers and user/kernel shared format definitions. Relies on architecture byte-order macros.

Risks and test signals: Main risk is wrong endian detection causing sample format mismatch. Test with big-endian and little-endian build coverage and OSS format negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundcard.h -->
