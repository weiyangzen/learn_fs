<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/spectral_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/spectral_common.h

Purpose: Defines common userspace-facing FFT spectral sample formats for ath drivers.

Important APIs/types/functions: Provides bin-count constants, `enum ath_fft_sample_type`, `struct fft_sample_tlv`, `struct fft_sample_ht20`, `struct fft_sample_ht20_40`, `struct fft_sample_ath10k`, and `struct fft_sample_ath11k`.

Control flow: No executable flow; drivers fill packed TLV records and expose them through debugfs or similar spectral scan interfaces.

State and persistence: Defines packed binary layouts with fixed and flexible sample data. No runtime state.

Dependencies and integration points: Shared by ath spectral scan producers and userspace parsers; endian annotations indicate wire format.

Risks and test signals: Risk is ABI breakage if fields before type/length are changed or if flexible bin lengths are misreported. Test signals are userspace spectral capture parsing for HT20, HT20/40, ath10k, and ath11k samples, including endian and length checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/spectral_common.h -->
