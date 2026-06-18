# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_cmds.c

## Purpose
`hfi_cmds.c` constructs firmware command packets for system and session operations. It hides HFI version differences for property packetization, validates many enum-like values, computes packet sizes for flexible-array payloads, and converts driver descriptors into wire-format HFI packets.

## Important APIs And Functions
- Versioning: `pkt_set_version()`.
- System packets: `pkt_sys_init()`, `pkt_sys_pc_prep()`, `pkt_sys_idle_indicator()`, `pkt_sys_debug_config()`, `pkt_sys_coverage_config()`, `pkt_sys_ubwc_config()`, `pkt_sys_set_resource()`, `pkt_sys_unset_resource()`, `pkt_sys_ping()`, `pkt_sys_power_control()`, `pkt_sys_ssr_cmd()`, `pkt_sys_image_version()`.
- Session lifecycle and buffer packets: `pkt_session_init()`, `pkt_session_cmd()`, `pkt_session_set_buffers()`, `pkt_session_unset_buffers()`, `pkt_session_etb_decoder()`, `pkt_session_etb_encoder()`, `pkt_session_ftb()`, sequence-header, flush, get-property, and set-property helpers.
- Version-specific property builders: `pkt_session_get_property_1x/3xx()` and `pkt_session_set_property_1x/3xx/4xx/6xx()`.

## Control Flow
Callers allocate packet storage, then call a packet helper to fill headers, session IDs, sizes, and property payloads. Session IDs and resource handles are generated with `hash32_ptr(cookie)`. ETB/FTB helpers map `hfi_frame_data` fields into compressed or uncompressed packet layouts. Buffer set/unset uses different payload shapes for output/output2 buffers, which carry `hfi_buffer_info`, versus other buffer types, which carry address arrays.

Property setting dispatches by global `hfi_ver`: 1xx handles the base set, 3xx overrides changed packet layouts, 4xx adds work mode/video-core/HDR10/QP-range differences and rejects unsupported properties, and 6xx adds constraints, HEIC quality, and work-route properties before falling back. Many properties validate allowed modes and return `-EINVAL`, `-ERANGE`, or `-ENOTSUPP`.

## State And Persistence
The only module state is static `hfi_ver`, set at HFI creation from SoC resource data. Packet helpers otherwise write caller-provided packet memory and do not persist data.

## Dependencies And Integration Points
- Uses HFI packet structs from `hfi_cmds.h`, property structs/constants from `hfi_helper.h`, and version enum from `hfi.h`.
- Lower transport code sends these packets to firmware queues.
- Helpers, controls, PM, and core code indirectly rely on these builders through `hfi_ops`.

## Risks And Edge Cases
- Packet size calculations must exactly match flexible payload content; mistakes can cause firmware parser failures or memory corruption.
- `hash32_ptr()` session IDs can theoretically collide, though low probability; message demux relies on the same hash.
- Global `hfi_ver` assumes one active HFI packet version process-wide; multiple Venus devices with different HFI versions would be risky.
- Some unsupported properties intentionally return `-ENOTSUPP`; callers must tolerate version differences.
- QP range packing validates only 8-bit values before duplicating into I/P/B fields.

## Test Signals
- Firmware command/response success for core init, session init/start/stop, ETB/FTB, flush, buffer set/unset, and property programming.
- Version matrix tests on HFI 1xx/3xx/4xx/6xx hardware or emulation.
- Negative tests for invalid flush modes, SSR types, rate-control modes, intra-refresh modes, QP ranges, and unsupported properties.
