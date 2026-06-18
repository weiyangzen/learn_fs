# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_channel.c

Purpose: defines vidtv's hardcoded channel abstraction and builds PSI/SI table inputs from channels. The current implementation creates an audio-only Beethoven channel with an S302M encoder, PAT/PMT/SDT/EIT/NIT entries, and service descriptors.

Important APIs/types/functions: exported functions are `vidtv_channel_s302m_init()`, `vidtv_channel_si_init()`, `vidtv_channel_si_destroy()`, `vidtv_channels_init()`, and `vidtv_channels_destroy()`. Internal helpers clone/concatenate channel EIT events, SDT services, PAT programs, match PMT sections to channels, build NIT service lists, and destroy encoder chains.

Control flow: channel init allocates a `struct vidtv_channel`, duplicates the service name, creates SDT service plus service descriptor, PAT program, PMT stream plus registration descriptor for S302M, initializes the S302M encoder, and creates an EIT event plus short-event descriptor. `vidtv_channel_si_init()` creates PAT and SDT tables, concatenates programs/services/events from all channels, builds a service list for NIT, creates NIT and EIT tables, assigns program/service/event lists, creates PMT sections for each PAT entry, and attaches cloned stream descriptors to matching PMTs. Destructors walk allocated linked lists and call PSI/encoder destroy functions.

State and persistence: channel state lives under `m->channels` in the mux and owns linked PSI fragments plus encoder chains. SI table state lives under `m->si` until mux destruction.

Dependencies and integration points: relies on `vidtv_psi` constructors/destructors and descriptor cloning, `vidtv_s302m_encoder_init()`, and mux fields such as transport stream ID, network ID/name, PCR PID, and device for warnings.

Risks: error paths are allocation-heavy and must avoid leaks/double frees across partially built linked lists. `vidtv_channel_build_service_list()` uses `s->descriptor->type` inside a descriptor loop instead of `desc->type`, so additional descriptor chains could be mishandled. `vidtv_channel_pat_prog_cat_into_new()` adds a NIT PAT entry after the loop but does not check the return value. Only one hardcoded channel exists, limiting coverage of multi-channel concatenation unless tests add more channels.

Test signals: load/start stream and verify PAT/PMT/SDT/NIT/EIT packets, KASAN/leak checks on mux init failure injection, multi-channel test injection for concatenation, and DVB userspace scans seeing the Beethoven service/event metadata.
