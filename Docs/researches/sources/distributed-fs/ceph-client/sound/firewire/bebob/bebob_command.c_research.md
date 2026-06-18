# sources/distributed-fs/ceph-client/sound/firewire/bebob/bebob_command.c

Purpose: implements AV/C audio selector and BridgeCo extension command helpers used for BeBoB clock routing, plug discovery, stream format discovery, channel mapping, and vendor quirks.

Important APIs/functions: `avc_audio_set_selector`, `avc_audio_get_selector`, `avc_bridgeco_get_plug_type`, `avc_bridgeco_get_plug_ch_count`, `avc_bridgeco_get_plug_ch_pos`, `avc_bridgeco_get_plug_section_type`, `avc_bridgeco_get_plug_input`, and `avc_bridgeco_get_plug_strm_fmt`.

Control flow and state: each helper builds an AV/C command buffer, calls `fcp_avc_transaction`, checks response length/status (`NOT IMPLEMENTED`, `REJECTED`, `IN TRANSITION`), extracts the requested field, and frees temporary memory. It maintains no persistent state; callers own retry policy and interpretation.

Dependencies/integration: depends on `fcp_avc_transaction`, BridgeCo address fill helpers, and standard AV/C response codes. It feeds `bebob_stream.c` discovery and vendor files such as M-Audio/Terratec/Yamaha. Risks include fixed command lengths, variable FCP response length handling, strict response byte masks, and transient `-EAGAIN` behavior. Test signals are successful plug type/count/channel/format reads on supported devices and graceful `-ENOSYS`/`-EINVAL` for unsupported command variants.
