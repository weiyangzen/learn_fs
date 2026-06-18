# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-streams.c

## Purpose
This file sets up, registers, starts, stops, and tears down all ivtv V4L2 stream nodes. It maps ivtv stream types to video/radio/VBI devices, buffer/DMA policy, capture/decode firmware setup, VBI setup, passthrough mode, and shared capture/decode counters.

## Important APIs, Types, and Functions
Public functions are `ivtv_streams_setup`, `ivtv_streams_register`, `ivtv_streams_cleanup`, `ivtv_start_v4l2_encode_stream`, `ivtv_stop_v4l2_encode_stream`, `ivtv_start_v4l2_decode_stream`, `ivtv_stop_v4l2_decode_stream`, `ivtv_stop_all_captures`, and `ivtv_passthrough_mode`. Important internals include the V4L2 fops tables, `ivtv_stream_info`, `ivtv_stream_init`, `ivtv_prep_dev`, `ivtv_reg_dev`, `ivtv_vbi_setup`, and `ivtv_setup_v4l2_decode_stream`.

## Control Flow
Setup prepares each stream device according to capability flags and user buffer sizing, allocates queue/DMA buffers, and later registers V4L2 minors. Encoder start initializes firmware DMA block size, digitizer quirks, VBI config, program index memory, MPEG controls, subdevice streaming, interrupt masks, and starts the requested firmware capture subtype. Decode start initializes audio/display/prebuffer/VBI extraction/source settings, starts playback, and unmasks decoder interrupts. Stop paths issue firmware stop commands, optionally wait for EOS or decoder drain, mask interrupts, flush queues, update counters, and queue events.

## State and Persistence Behavior
The file mutates stream `video_device` fields, buffer allocations, stream flags, `capturing` and `decoding` atomics, firmware busy state, VBI encoder/decoder offsets, program index state, output mode, passthrough flags, IRQ masks, and subdevice streaming state. Registered device nodes persist until cleanup.

## Dependencies and Integration Points
It depends on V4L2 video-device registration, ivtv fileops/ioctl/queue/mailbox/IRQ/YUV/VBI/firmware/card layers, cx2341x control setup, subdevice audio/video streaming, and V4L2 EOS events.

## Risks
Start/stop ordering is firmware-sensitive. Shared counters mean one stream can keep capture hardware active while another stops. GOP-end stop waits can time out. Passthrough manipulates both encoder and decoder state and must balance atomics. Device minor calculation depends on MPEG stream registration.

## Test Signals
Open/read/write/poll all nodes, register/unregister with and without OSD, start multiple capture substreams, stop MPEG at GOP end, VBI-only capture, decode drain and immediate stop, passthrough enable/disable, firmware check failures, and cleanup after partial allocation/registration failure.
