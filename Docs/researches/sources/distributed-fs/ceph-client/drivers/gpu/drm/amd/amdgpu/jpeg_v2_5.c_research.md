# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v2_5.c

Purpose: implements JPEG v2.5/v2.6 IP blocks, adding up to two hardware instances, harvesting detection, per-instance doorbells, v2.6-specific start/end deepsleep packets, and RAS poison interrupt/status support.

Important APIs and functions: exports `jpeg_v2_5_ip_block` and `jpeg_v2_6_ip_block`. Main lifecycle functions are shared between the two versions. Per-instance helpers start/stop individual JPEG engines, manage clock gating, read/write ring pointers using `ring->me`, and reset a single ring by stopping/starting its instance. RAS helpers query v2.6 JPEG0/JPEG1 poison status and install `adev->jpeg.ras`.

Control flow and state: early init sets two potential instances and reads `mmCC_UVD_HARVESTING` to mark disabled engines in `adev->jpeg.harvest_config`, returning `-ENOENT` if both are harvested. SW init registers decode and poison IRQs per live instance, initializes rings named `jpeg_dec_N`, selects MMHUB based on IP version, and sets doorbell offsets `+ 8 * i`. Start/stop and idle/wait loops skip harvested instances. `cur_state` is block-wide even though operations loop instances.

Dependencies and integration: depends on VCN 2.5 offsets/masks, VCN 2.0 IRQ source IDs, shared v2.0 packet helpers, amdgpu RAS/JPEG helpers, NBIO doorbell ranges, and SOC15 register accessors.

Risks and test signals: global `cur_state` for multiple instances can obscure partial failures. `wait_for_idle()` correctly returns first wait failure; interrupt routing maps IH client VCN/VCN1 to instance 0/1. RAS poison IRQ setup is unconditional in sw init, but hw fini only puts it when RAS is supported. Test signals include harvested-instance skip behavior, two-instance decode interrupts, v2.6 deepsleep start/end packets, ring reset on one instance, RAS poison query, and sysfs reset mask creation.
