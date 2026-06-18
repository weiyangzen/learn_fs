# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3_cleaner_shader.h

Purpose: embeds the precompiled GC 9.4.3 cleaner shader as a static `u32` machine-code array for inclusion by `gfx_v9_4_3.c`.

Important APIs/types/functions: defines `static const u32 gfx_9_4_3_cleaner_shader_hex[]`. There are no functions or include guards; the file is intended to be included by a single C translation unit needing the static array.

Control flow: no host-side control flow. The array content corresponds to the assembly in `gfx_v9_4_3_cleaner_shader.asm`; runtime control occurs on the GPU when the ring emits `PACKET3_RUN_CLEANER_SHADER`.

State and persistence behavior: the array is read-only driver text/data. During `gfx_v9_4_3_sw_init`, the driver stores a pointer and size into `adev->gfx.cleaner_shader_ptr` and `adev->gfx.cleaner_shader_size`; `hw_init` uploads it into GPU-visible cleaner-shader memory if the feature is enabled.

Dependencies and integration points: depends on `u32` being defined by including AMDGPU/Linux headers before this file. Integrated directly by `gfx_v9_4_3.c`, which gates use to GC 9.4.3/9.4.4 and sufficiently new MEC firmware.

Risks and test signals: because the blob is static machine code, source/hex drift is the main maintainability risk. There is no local metadata for ASIC, wave size, or checksum, so validation relies on external build review and hardware tests. Test signals are successful compilation, correct `sizeof()` used for upload, valid cleaner-shader GPU address passed through KIQ resources, and successful register/LDS scrubbing without queue hangs.
