## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/adreno/adreno_gpu.h

### Purpose
`adreno_gpu.h` is the common Adreno interface shared by generation-specific MSM GPU drivers. It declares GPU identity tables, quirk bits, firmware slots, common runtime state, generation predicates, ringbuffer packet emitters, register-protection encoders, and prototypes implemented by `adreno_gpu.c`.

### Important APIs, Types, And Functions
Key types are `enum adreno_family`, `struct adreno_gpu_funcs`, `struct adreno_info`, `struct adreno_gpulist`, `struct adreno_protect`, register-list wrapper structs, `struct adreno_gpu`, `struct adreno_ocmem`, and `struct adreno_platform_config`. Important macros include `ADRENO_FW_*`, `ADRENO_QUIRK_*`, `ADRENO_CHIP_IDS()`, `DECLARE_ADRENO_GPULIST()`, `ADRENO_SPEEDBINS()`, `DECLARE_ADRENO_PROTECT()`, `ADRENO_IDLE_TIMEOUT`, `spin_until()`, `ADRENO_VM_START`, PM4 packet helpers, `PKT4()`, `PKT7()`, and `gpu_poll_timeout()`.

### Control Flow
The header is primarily declarative. Generation-specific drivers fill `struct adreno_info` tables with chip IDs, firmware names, GMEM size, quirks, function tables, zap firmware, inactive period, optional a6xx metadata, speedbins, and preemption record sizing. Probe passes `struct adreno_platform_config` to common init, and runtime code uses inline predicates such as `adreno_is_a650_family()`, `adreno_is_a7xx()`, and `adreno_has_rgmu()` to select generation-specific behavior.

### State, Persistence, And Dependencies
`struct adreno_gpu` embeds `struct msm_gpu` and persists chip identity, firmware location and firmware handles, UBWC configuration, register offset tables, GMU wrapper state, ray-tracing capability, UCHE trap base, and fault-coredump completion. The header depends on Linux firmware/iopoll/UBWC headers, `msm_gpu.h`, and generated Adreno XML packet/register definitions.

### Integration Points
Generation drivers include this header to bind their `msm_gpu_funcs` into `adreno_gpu_funcs`, emit CP packets into ringbuffers, define protected register ranges, identify GPU revisions, and call common firmware, VM, fault, OCMEM, debug, and initialization helpers. UAPI-facing code uses `ADRENO_CHIPID_FMT` and `ADRENO_CHIPID_ARGS()` to expose chip IDs in the format expected by crash/debug tools.

### Risks
Many inline predicates compare only `info->revn` or the first chip ID; table mistakes can route a GPU through the wrong generation path. `spin_until()` is a busy loop with a one-second timeout, so it should stay on short hardware waits. Packet helpers call `adreno_wait_ring()` before writing but assume correct dword counts. The `ADRENO_PROTECT_RDONLY()` macro appears to lack an operator between `(1 << 29)` and the following shifted size expression, making compile coverage important if that macro is used.

### Test Signals
Compile tests across all enabled Adreno generations are essential because this header is macro-heavy. Runtime signals include correct GPU family detection for chip IDs, PM4 packet parity values for type4/type7 packets, ring space waits under wrap-around, register-protection encodings for aligned ranges, firmware-slot selection for pre-a6xx and a6xx+ devices, and UAPI chip/revision reporting for speedbin-based entries.
