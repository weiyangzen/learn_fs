# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3av.h

Purpose: This header defines the PS3 AV backend command ABI: command IDs, video/audio/HDMI constants, event/status bits, packet structures, and high-level command helper declarations for video and audio mode control.

Important APIs/types/functions: It defines `PS3AV_VERSION`, command IDs for AV init/finalize, hardware config, monitor info, events, mute, video color-space/mode/format/pitch, audio mode/mute/control, and AVB parameter batches. It encodes port/head counts, event bits, video modes, color spaces, audio layouts, sampling rates, HDMI/DVI flags, region/default modes, `enum ps3av_mode_num`, send/reply headers, monitor info structures, packet structures for every command class, `struct ps3av_pkt_avb_param`, `ps3av_mode_cs_info`, status codes, and helper APIs such as `ps3av_set_hdr`, `ps3av_do_pkt`, `ps3av_cmd_init`, mode/mute/audio helpers, monitor info query, auto-mode selection, and resolution conversion.

Control flow: Callers build typed packets, fill headers with `ps3av_set_hdr`, send them through `ps3av_do_pkt`, and interpret backend status codes. High-level helpers generate packet payloads for video/color/audio configuration and batch them via AVB param when needed. Mode selection can use monitor info, region flags, and automatic resolution masks.

State and persistence: Header-defined packet layouts describe data exchanged with the AV backend over PS3 communication channels. Persistent state lives in the backend/driver: current mode, monitor info, audio channel-status data, mute state, and event subscription.

Dependencies and integration points: It depends on Linux integer typedefs and integrates PS3 AV setting drivers with VUART/syscon/backend firmware, framebuffer/video mode setup, HDMI/AVMULTI/SPDIF ports, audio drivers, monitor EDID-like data, and user-visible mode selection.

Risks and test signals: Packet structure sizes and packing are firmware ABI. Several constants warn not to use backend AV values directly but convert from video values. Flexible audio blocks and AVB variable buffer layout require careful bounds checks. Tests should cover command packet size/version fields, monitor info parsing, all supported video modes/regions, HDMI/DVI flags, audio channel layouts, mute/unmute paths, event enable/disable, and backend error status mapping.
