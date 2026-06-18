# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/hgsmi_defs.h

## Purpose

`hgsmi_defs.h` defines the generic HGSMI buffer header/tail layout and sequence flag constants used by the VirtualBox guest heap command transport.

## Important APIs, Types, and Functions

- `struct hgsmi_buffer_header`: data size, sequence flags, channel id, channel-specific info, and sequence metadata.
- `struct hgsmi_buffer_tail`: reserved word and checksum field.
- `HGSMI_BUFFER_HEADER_F_SEQ_*`: single/start/continue/end sequence markers.
- `HGSMI_NUMBER_OF_CHANNELS`: fixed 256-channel namespace.

## Control Flow

`hgsmi_buffer_alloc` prepends this header and appends the tail to every guest-heap command. `hgsmi_buffer_submit` writes the header offset to the host I/O port, where the host validates and consumes the buffer.

## State and Persistence Behavior

The structures exist in shared VRAM for the duration of each command allocation. The ABI and packing are persistent contracts with the VirtualBox host.

## Dependencies and Integration Points

Used by `vbox_hgsmi.c` for checksum generation, allocation, free size calculation, and submit offset reporting. Channel values come from `hgsmi_channels.h`.

## Risks and Edge Cases

Packed layout and sizes must remain stable. The current driver only emits single-buffer commands; adding sequences would need new allocation/submission logic and checksum coverage.

## Test Signals

Check structure sizes/offsets, checksum acceptance by the host, allocation/free round trips, and command submission under hosts that validate HGSMI headers strictly.
