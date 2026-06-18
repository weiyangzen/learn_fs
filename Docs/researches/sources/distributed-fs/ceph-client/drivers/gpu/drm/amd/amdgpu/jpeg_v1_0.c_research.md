# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/jpeg_v1_0.c

Purpose: implements JPEG v1.0 decode ring support for early VCN/JPEG hardware. It provides ring packet emission, a local command-stream parser, IRQ fence processing, software init/fini, and a start routine that programs JRBC ring base registers.

Important APIs and functions: exported generation entry points are `jpeg_v1_0_early_init()`, `jpeg_v1_0_sw_init()`, `jpeg_v1_0_sw_fini()`, and `jpeg_v1_0_start()`. Ring callbacks include get/set read/write pointers, start/end packets, fence and IB emission, VM flush/reg-wait/wreg emission, NOP insertion, and begin-use serialization with VCN v1 rings. `jpeg_v1_dec_ring_parse_cs()` validates user packet streams against the v1 register allowlist.

Control flow and state: early init sets one JPEG instance/ring and installs ring/IRQ funcs. Software init registers VCN client source ID 126, initializes a 512-DW `jpeg_dec` ring on MMHUB0, and records internal/external pitch registers. Start optionally programs the ring buffer in non-DPG mode, initializes `ring->wptr`, and patches ring memory with commands used for later submissions. Runtime progress is tracked by hardware JRBC RPTR/WPTR plus amdgpu fence sequence memory.

Dependencies and integration: depends on `amdgpu_jpeg`, `amdgpu_cs`, VCN v1 helpers, SOC15 register accessors, PACKETJ encoding, MMHUB VM flushing, and amdgpu fence/IRQ infrastructure. Begin-use coordinates with VCN v1 decode/encode rings through `vcn1_jpeg1_workaround`.

Risks and test signals: the parser walks IBs in two-DW packets and rejects unexpected resource bits, condition fields, packet types, or registers, so parser coverage is critical. Fence emission warns on 64-bit fence flags and writes duplicate sequence data through GPCOM. Begin-use waits for all VCN v1 rings, so deadlocks or false non-empty fences can block JPEG. Test signals include ring test, IB test, invalid packet rejection, trap IRQ source 126 fence completion, VM flush waits, and suspend/fini ring cleanup.
